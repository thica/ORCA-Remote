# -*- coding: utf-8 -*-
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2019  Carsten Thielepape
    Please contact me by : http://www.orca-remote.org/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import gc
import traceback
from functools              import  partial

from kivy.logger            import  Logger
from kivy.gesture           import  GestureDatabase
from kivy.clock             import  Clock
from kivy.event             import  EventDispatcher

from kivy.uix.screenmanager import  ScreenManager
from kivy.uix.screenmanager import  Screen
from kivy.uix.screenmanager import  FadeTransition
from kivy.uix.screenmanager import  FallOutTransition
from kivy.uix.screenmanager import  NoTransition
from kivy.uix.screenmanager import  RiseInTransition
from kivy.uix.screenmanager import  SlideTransition
from kivy.uix.screenmanager import  SwapTransition
from kivy.uix.screenmanager import  WipeTransition

from ORCA.Fonts                     import  cFonts
from ORCA.ui.ShowErrorPopUp         import  ShowErrorPopUp
from ORCA.utils.LogError            import  LogError
from ORCA.utils.TypeConvert         import  ToUnicode
from ORCA.Skin                      import  cSkin
from ORCA.vars.Replace              import  ReplaceVars
from ORCA.vars.Globals              import  InitSystemVars
from ORCA.vars.Actions              import  Var_Increase
from ORCA.ScreenPages               import  cScreenPages

import ORCA.Globals as Globals

class cTheScreen(EventDispatcher):
    """ The Main screen class """

    def __init__(self, *args, **kwargs):
        super(cTheScreen, self).__init__(*args, **kwargs)
        self.bIntransition          = False
        self.iRotateCount           = 0
        self.oScreenPages           = {}
        self.dPopups                = {}
        self.oCurrentPage           = None
        self.oFonts                 = cFonts()
        self.dGestures              = {}
        self.oPopupPage             = None
        self.oRootSM                = ScreenManager()
        self.oScreenPages           = cScreenPages()
        self.oSkin                  = cSkin()
        self.oSplashBackground      = Screen(name="SPLASH")
        self.oSplashLogger          = None
        self.oSplashLogger2         = None
        self.uCurrentEffect         = u''
        self.uCurrentEffectDirection =u''
        self.uCurrentPageName       = None
        self.uLastTouchType         = u''
        self.uFirstPageName         = u''
        self.oRootSM.add_widget(self.oSplashBackground)
        self.InitVars()

    def InitVars(self):
        """ (re) Initialisises all vars (also after a definition change) """
        InitSystemVars()
        Globals.oDefinitions.InitVars()

        # Name of the Current page
        # List for settings dialog
        self.bIntransition      = False
        self.dGestures.clear()
        self.dPopups.clear()
        self.iLastWidgetPage    = 0
        Globals.oActions.InitVars()
        self.oCurrentPage       = None
        self.oFonts.DeInit()
        self.oGdb               = GestureDatabase()
        self.oPopup             = None
        self.oScreenPages.DeInit()
        self.uCurrentEffect     = u''
        self.uCurrentEffectDirection =u''
        self.uCurrentPageName   = u''
        self.uDefaultTransmitterPictureName = u''
        self.uDefaultWaitPictureName = u''
        self.uDefName           = u''
        self.uFirstPageName     = u''
        self.uInterFaceToConfig = u''
        self.uScriptToConfig    = u''
        self.uConfigToConfig    = u''
        self.uSplashText        = u''
        if Globals.oTheScreen:
            Globals.oTheScreen.oSkin.dSkinRedirects.clear()
        gc.collect()

    def DeInit(self,**kwargs):
        """ Deinitialisises the screen """
        Globals.oEvents.DeInit()

    def ShowPage(self,uPageName,*largs):
        """ Shows a specific page (waiting in case a transition is still in progress) """
        if not self.bIntransition:
            self._ShowPage(uPageName=uPageName)
            return -2
        else:
            Logger.debug ('Waiting to finish transition')
            Clock.schedule_once(partial(self.ShowPage,uPageName),0)
            return -2

    def ShowPageGetPageStartActions(self,uPageName='Page_None'):
        """ Returns the pagestartactions for a specific page """
        aActions=Globals.oActions.GetPageStartActionList(uActionName=uPageName, bNoCopy=False)
        oPage=self.oScreenPages.get(uPageName)
        if oPage:
            oPage.Create()
        return aActions

    def ShowPageGetPageStopActions(self, uPageName=u''):
        """ Returns the pagestopactions for a specific page """
        if uPageName==u'':
            if self.oCurrentPage:
                uPageName=self.oCurrentPage.uPageName
        return Globals.oActions.GetPageStopActionList(uActionName = uPageName, bNoCopy = False)

    def _ShowPage(self,uPageName='Page_None'):

        try:
            if self.uCurrentPageName==uPageName:
                return True
            oPage=self.oScreenPages.get(uPageName)
            if oPage is None:
                Logger.error(u'ShowPage: Wrong Pagename given:'+uPageName)
                self.DumpPages()
                uPageName = 'Page_None'
                oPage=self.oScreenPages.get(uPageName)
                self.oCurrentPage=oPage
            else:
                self.oCurrentPage=oPage

            self.oScreenPages.CreatePage(u'')
            Var_Increase(uVarName = "PAGESTARTCOUNT_"+oPage.uPageName)
            if self.oPopupPage:
                if self.oPopupPage.oScreen in self.oRootSM.current_screen.children:
                    self.oRootSM.current_screen.remove_widget(self.oPopupPage.oScreen)

            Logger.debug("TheScreen: Showing page: %s, called from %s" % (uPageName,self.uCurrentPageName))

            oPage.iESCPressCount = 0

            if not oPage.bIsPopUp:
                self.oRootSM.current        = uPageName
            else:
                self.oPopupPage=oPage
                #self.oRoot.add_widget(oPage.oScreen)
                self.oRootSM.current_screen.add_widget(oPage.oScreen)

            oPage.uCallingPageName          = self.uCurrentPageName
            self.uCurrentPageName           = uPageName

            if self.uFirstPageName==u'':
                self.uFirstPageName=uPageName

            self.oScreenPages.AppendToPageQueue(oPage)

            oPage.SetTransmitterPicture(self.uDefaultTransmitterPictureName)
            oPage.SetWaitPicture(uWaitPictureName=self.uDefaultWaitPictureName)
            return True

        except Exception as e:
            uMsg = traceback.format_exc()
            Logger.debug (uMsg)
            Logger.debug("Rootsm:"+str(self.oRootSM))
            if self.oRootSM is not None:
                Logger.debug("current_screen:"+str(self.oRootSM.current_screen))

            uMsg=LogError(u'TheScreen: ShowPage: Page could not be activated:'+uPageName,e)
            ShowErrorPopUp(uMessage=uMsg)
            return False

    def IsPopup(self,uPageName=None):
        """ Detects/returns, if a page is a popup page """
        uPageNameOrg=uPageName
        if uPageName is None or uPageName=='':
            oPage=self.oCurrentPage
            if oPage is None:
                return False
        else:
            uPageName=ReplaceVars(uPageName)
            oPage=self.oScreenPages.get(uPageName)

        if oPage is None:
            Logger.debug(u'IsPopup: Wrong Pagename given: [%s/%s]' % (uPageName,uPageNameOrg))
            return False
        else:
            return oPage.bIsPopUp

    def On_Transition_Complete(self,oTransition):
        """ Called by the framework, when the transition has been finished, sets the flag, to stop waiting """
        self.bIntransition      = False
    def On_Transition_Started(self,oTransition,Percentage):
        """ Called by the framework, when the transition has been started """
        #print 'in Transition',oTransition.is_active,Percentage
        if Percentage==0:
            self.bIntransition      = True

    def SetPageEffectDirection(self,uDirection='fade'):
        """ Sets the Page effect direction (in case , the effect has an direction) """
        self.uCurrentEffectDirection=uDirection

        try:
            if ToUnicode(type(self.oRootSM.transition)).endswith(u'SlideTransition\'>'):
                if uDirection!=u'':
                    self.oRootSM.transition.direction=uDirection
            return True
        except Exception as e:
            uMsg=LogError(u'TheScreen: Can not set page effect direction:' + uDirection ,e)
            ShowErrorPopUp(uMessage=uMsg)
            return False

    def SetPageEffect(self,uEffect):
        """ Sets the page effect for showing a page """
        self.uCurrentEffect=uEffect
        try:
            if uEffect==u'':
                return True
            uType=ToUnicode(type(self.oRootSM.transition))
            if uEffect==u'no':
                self.oRootSM.transition = NoTransition()
            if uEffect==u'fade':
                if uType.endswith(u'FadeTransition\'>'):
                    return True
                self.oRootSM.transition = FadeTransition()
            elif uEffect==u'slide':
                if uType.endswith(u'SlideTransition\'>'):
                    return True
                self.oRootSM.transition = SlideTransition()
            elif uEffect==u'wipe':
                if uType.endswith(u'WipeTransition\'>'):
                    return True
                self.oRootSM.transition = WipeTransition()
            elif uEffect==u'swap':
                if uType.endswith(u'SwapTransition\'>'):
                    return True
                self.oRootSM.transition = SwapTransition()
            elif uEffect==u'fallout':
                if uType.endswith(u'FallOutTransition\'>'):
                    return True
                self.oRootSM.transition = FallOutTransition()
            elif uEffect==u'risein':
                if uType.endswith(u'RiseInTransition\'>'):
                    return True
                self.oRootSM.transition = RiseInTransition()

            self.oRootSM.transition.bind(on_complete=self.On_Transition_Complete)
            self.oRootSM.transition.bind(on_progress=self.On_Transition_Started)
            return True

        except Exception as e:
            uMsg=LogError(u'TheScreen: Can not set page effect:' + uEffect,e)
            ShowErrorPopUp(uMessage=uMsg)
            return False

    def AddActionShowPageToQueue(self,uPageName):
        """ Convinient function to show a page by the scheduler """
        self.AddActionToQueue([{'string':'showpage','pagename':uPageName}])

    def AddActionToQueue(self,aActions, bNewQueue=False):
        """ Adds Actions to the scheduler """
        aTmpActions=Globals.oEvents.CreateSimpleActionList(aActions)
        if bNewQueue:
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aTmpActions,oParentWidget=None)
        else:
            Globals.oEvents.ExecuteActions(aActions=aTmpActions,oParentWidget=None)

    def UpdateSetupWidgets(self):
        """ Updates all setup / settings widgets """
        for uPageName in self.oScreenPages:
            self.oScreenPages[uPageName].UpdateSetupWidgets()

    def FindWidgets(self,uPageName,uWidgetName,bIgnoreError=False):
        """ Find a set widgets with a given name """
        aRet=[]
        if "@" in uWidgetName:
            uWidgetName,uPageName=uWidgetName.split(u"@")

        uWidgetNameRep = ReplaceVars(uWidgetName)
        uPageNameRep   = ReplaceVars(uPageName)
        if uPageNameRep=="":
            if self.oCurrentPage is not None:
                uPageNameRep=self.oCurrentPage.uPageName

        oPages=[]
        if uPageNameRep!="*":
            oPages.append(uPageNameRep)
        else:
            for uPageNameRep in self.oScreenPages:
                oPages.append(uPageNameRep)

        for uPageName in oPages:
            oPage=self.oScreenPages.get(uPageName)
            if oPage is None:
                if not bIgnoreError:
                    uMsg=u'The Screen: Page [%s] for Widget [%s] not found:' % (uPageName,uWidgetNameRep)
                    Logger.error (uMsg)
            else:
                if uWidgetNameRep != "*":
                    aWidgets = oPage.dWidgets[uWidgetNameRep]
                    if aWidgets:
                        for oWidget in aWidgets:
                            aRet.append(oWidget)
                    else:
                        if uPageNameRep!="*":
                            if not bIgnoreError:
                                Logger.warning ("Can't find widget [%s] on  page [%s]" % (uWidgetNameRep,uPageName))
                else:
                    for oWidget in oPage.aWidgets:
                        aRet.append(oWidget)

        if len(aRet)==0:
            if not bIgnoreError:
                uMsg=u'The Screen: Widget not found:'+uWidgetNameRep
                Logger.error (uMsg)

        return aRet


    def on_motion(self, window,etype, motionevent):
        """ To detect, if we still have a down touch if we missed the touch_up message so we do not want endless repeat """
        self.uLastTouchType  = etype

    def DumpPages(self, uFilter=''):
        """ Dumps the names of all pages to the log file"""
        Logger.error(u'Available Pages:')
        for uKey in sorted(self.oScreenPages):
            if uFilter=="":
                Logger.error(uKey)
            else:
                if uFilter in uKey:
                    Logger.error(uKey)

"""


    def FindWidget(self,oScreenPage,uWidgetName,bDoNotCreatePage=False):
        '''
        Finds widgets with a given name
        :param oScreenPage: The page to look for, if empty, the current page will be searched
        :param str: uWidgetName: The name of the Widget
        :param bool: bDoNotCreatePage: If True, pages will not be cretaed, otherwise the page will be created to ensure, the widget is valid
        :return: list of Widgets
        :rtype list
        '''



        uWidgetNameRep=ReplaceVars(uWidgetName)
        if oScreenPage is None:
            oScreenPage=self.oCurrentPage

        if oScreenPage is None:
            uMsg=u'The Screen: Page for Widget not found:'+uWidgetNameRep
            Logger.error (uMsg)
            return []

        aWidgets = oScreenPage.dWidgets[uWidgetNameRep]
        if aWidgets:
            for oWidget in aWidgets:
                if not oScreenPage.bIsInit and not bDoNotCreatePage:
                    oScreenPage.Create()
            return aWidgets
        Logger.warning ("Can't find widget [%s] on current page [%s], looking on all pages" % (uWidgetName,oScreenPage.uPageName))

        # this returns widgets just on the first page we find them, not of all pages
        for oPageName in self.oScreenPages:
            oPage=self.oScreenPages[oPageName]
            aWidgets = oPage.dWidgets[uWidgetNameRep]
            if aWidgets:
                for oWidget in aWidgets:
                    if not oPage.bIsInit and not bDoNotCreatePage:
                        oPage.Create()
                return aWidgets

        uMsg=u'The Screen: Widget not found:'+uWidgetNameRep
        Logger.error (uMsg)

        return []


"""
