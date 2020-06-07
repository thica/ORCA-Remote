# -*- coding: utf-8 -*-
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2020  Carsten Thielepape
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

from typing                 import Dict
from typing                 import List
from typing                 import Optional

import gc
import traceback
from functools              import  partial

from kivy.logger            import  Logger
from kivy.gesture           import  GestureDatabase
from kivy.clock             import  Clock
from kivy.event             import  EventDispatcher
from kivy.uix.widget        import  Widget
from kivy.uix.label         import  Label


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
from ORCA.vars.Access               import  SetVar
from ORCA.widgets.base.Base         import  cWidgetBase
from ORCA.actions.ReturnCode        import  eReturnCode

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage import cScreenPage
    from ORCA.Gesture    import cGesture
    from ORCA.Action     import cAction
else:
    from typing import TypeVar
    cScreenPage = TypeVar("cScreenPage")
    cGesture    = TypeVar("cGesture")
    cAction     = TypeVar("cAction")


class cTheScreen(EventDispatcher):
    """ The Main screen class """

    def __init__(self, *args, **kwargs):
        super(cTheScreen, self).__init__(*args, **kwargs)
        self.bIntransition:bool                     = False
        self.iBlockCount:int                        = 0
        self.iBlockAskCount:int                     = 0
        self.iRotateCount:int                       = 0
        self.dPopups:Dict[str,Widget]               = {}
        self.oCurrentPage:Optional[cScreenPage]     = None
        self.oFonts:cFonts                          = cFonts()
        self.oGdb:Optional[GestureDatabase]         = None
        self.dGestures:Dict[str,cGesture]           = {}
        self.iLastWidgetPage:int                    = 0
        self.oPopupPage:Optional[cScreenPage]       = None
        self.oPopup:Optional[cScreenPage]           = None
        self.oRootSM:ScreenManager                  = ScreenManager()
        self.oScreenPages:cScreenPages              = cScreenPages()
        self.oSkin:cSkin                            = cSkin()
        self.oSplashBackground:Screen               = Screen(name="SPLASH")
        self.oSplashLogger:Optional[Label]          = None
        self.oSplashLogger2:Optional[Label]         = None
        self.uCurrentEffect:str                     = u''
        self.uCurrentEffectDirection:str            = u''
        self.uCurrentPageName:str                   = u''
        self.uLastTouchType:str                     = u''
        self.uFirstPageName:str                     = u''
        self.uDefaultTransmitterPictureName:str     = u''
        self.uDefaultWaitPictureName:str            = u''
        self.uDefName:str                           = u''
        self.uInterFaceToConfig:str                 = u''
        self.uScriptToConfig:str                    = u''
        self.uConfigToConfig:str                    = u''
        self.uSplashText:str                        = u''
        self.oRootSM.add_widget(self.oSplashBackground)
        self.InitVars()

    def InitVars(self) -> None:
        """ (re) Initialisises all vars (also after a definition change) """
        InitSystemVars()
        Globals.oDefinitions.InitVars()
        SetVar(uVarName = u'REPVERSION', oVarValue = ToUnicode(Globals.iVersion))

        # Name of the Current page
        # List for settings dialog
        self.bIntransition              = False
        self.dGestures.clear()
        self.dPopups.clear()
        self.iLastWidgetPage            = 0
        Globals.oActions.InitVars()
        self.oCurrentPage               = None
        self.oFonts.DeInit()
        self.oGdb                       = GestureDatabase()
        self.oPopup                     = None
        self.oScreenPages.DeInit()
        self.uCurrentEffect             = u''
        self.uCurrentEffectDirection    = u''
        self.uCurrentPageName           = u''
        self.uDefaultTransmitterPictureName = u''
        self.uDefaultWaitPictureName    = u''
        self.uDefName                   = u''
        self.uFirstPageName             = u''
        self.uInterFaceToConfig         = u''
        self.uScriptToConfig            = u''
        self.uConfigToConfig            = u''
        self.uSplashText                = u''
        self.iBlockCount                = 0
        self.iBlockAskCount             = 0
        if Globals.oTheScreen:
            Globals.oTheScreen.oSkin.dSkinRedirects.clear()
        gc.collect()

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def DeInit(self,**kwargs) -> None:
        """ Deinitialisises the screen """
        Globals.oEvents.DeInit()

    # noinspection PyUnusedLocal
    def ShowPage(self,uPageName:str,*largs) -> eReturnCode:
        """ Shows a specific page (waiting in case a transition is still in progress) """
        if not self.bIntransition:
            self._ShowPage(uPageName=uPageName)
            return eReturnCode.Nothing
        else:
            Logger.debug ('Waiting to finish transition')
            Clock.schedule_once(partial(self.ShowPage,uPageName),0)
            return eReturnCode.Nothing

    def ShowPageGetPageStartActions(self,*,uPageName:str='Page_None') -> List[cAction]:
        """ Returns the pagestartactions for a specific page """
        aActions:List[cAction] = Globals.oActions.GetPageStartActionList(uActionName=uPageName, bNoCopy=False)
        oPage:cScreenPage      = self.oScreenPages.get(uPageName)
        if oPage:
            oPage.Create()
        return aActions

    def ShowPageGetPageStopActions(self, *,uPageName:str = u'')  -> List[cAction]:
        """ Returns the pagestopactions for a specific page """
        if uPageName==u'':
            if self.oCurrentPage:
                uPageName=self.oCurrentPage.uPageName
        return Globals.oActions.GetPageStopActionList(uActionName = uPageName, bNoCopy = False)

    def _ShowPage(self,*,uPageName:str = 'Page_None') -> bool:
        oPage:cScreenPage
        uPageName:str
        try:
            if self.uCurrentPageName==uPageName:
                return True
            oPage = self.oScreenPages.get(uPageName)
            if oPage is None:
                Logger.error(u'ShowPage: Wrong Pagename given:'+uPageName)
                self.DumpPages()
                uPageName         = 'Page_None'
                oPage             = self.oScreenPages.get(uPageName)
                self.oCurrentPage = oPage
            else:
                self.oCurrentPage = oPage

            self.oScreenPages.CreatePage(uPageName=u'')
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

            oPage.uCalledByPageName            = self.uCurrentPageName
            self.oCurrentPage.uCallingPageName = "" # uPageName
            self.uCurrentPageName              = uPageName

            if self.uFirstPageName==u'':
                self.uFirstPageName=uPageName

            self.oScreenPages.AppendToPageQueue(oPage=oPage)

            oPage.SetTransmitterPicture(uTransmitterPictureName=self.uDefaultTransmitterPictureName)
            oPage.SetWaitPicture(uWaitPictureName=self.uDefaultWaitPictureName)
            return True

        except Exception as e:
            uMsg:str
            uMsg = traceback.format_exc()
            Logger.debug (uMsg)
            Logger.debug("Rootsm:"+str(self.oRootSM))
            if self.oRootSM is not None:
                Logger.debug("current_screen:"+str(self.oRootSM.current_screen))

            uMsg=LogError(uMsg=u'TheScreen: ShowPage: Page could not be activated:'+uPageName,oException=e)
            ShowErrorPopUp(uMessage=uMsg)
            return False

    def IsPopup(self,*,uPageName:Optional[str]=None) -> bool:
        """ Detects/returns, if a page is a popup page """
        oPage:cScreenPage
        uPageNameOrg:str=uPageName
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

    # noinspection PyUnusedLocal
    def On_Transition_Complete(self, oTransition) -> None:
        """ Called by the framework, when the transition has been finished, sets the flag, to stop waiting """
        self.bIntransition      = False

    # noinspection PyUnusedLocal
    def On_Transition_Started(self, oTransition,Percentage)  -> None:
        """ Called by the framework, when the transition has been started """
        #print 'in Transition',oTransition.is_active,Percentage
        if Percentage==0:
            self.bIntransition      = True

    def SetPageEffectDirection(self,*,uDirection:str='fade') -> bool:
        """ Sets the Page effect direction (in case , the effect has an direction) """
        self.uCurrentEffectDirection = uDirection

        try:
            if ToUnicode(type(self.oRootSM.transition)).endswith(u'SlideTransition\'>') or True:
                if uDirection!=u'':
                    self.oRootSM.transition.direction=uDirection
            return True
        except Exception as e:
            uMsg:str=LogError(uMsg=u'TheScreen: Can not set page effect direction:' + uDirection ,oException=e)
            ShowErrorPopUp(uMessage=uMsg)
            return False

    def SetPageEffect(self,*,uEffect:str) -> bool:
        """ Sets the page effect for showing a page """
        self.uCurrentEffect = uEffect
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

            # noinspection PyArgumentList
            self.oRootSM.transition.bind(on_complete=self.On_Transition_Complete)
            # noinspection PyArgumentList
            self.oRootSM.transition.bind(on_progress=self.On_Transition_Started)
            return True

        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'TheScreen: Can not set page effect:' + uEffect,oException=e))
            return False

    def AddActionShowPageToQueue(self,*,uPageName:str) -> None:
        """ Convinient function to show a page by the scheduler """
        self.AddActionToQueue(aActions= [{'string':'showpage','pagename':uPageName}])

    # noinspection PyMethodMayBeStatic
    def AddActionToQueue(self,*,aActions:List[cAction], bNewQueue:bool=False) -> None:
        """ Adds Actions to the scheduler """
        aTmpActions=Globals.oEvents.CreateSimpleActionList(aActions=aActions)
        if bNewQueue:
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aTmpActions,oParentWidget=None)
        else:
            Globals.oEvents.ExecuteActions(aActions=aTmpActions,oParentWidget=None)

    def UpdateSetupWidgets(self) -> None:
        """ Updates all setup / settings widgets """
        for uPageName in self.oScreenPages:
            self.oScreenPages[uPageName].UpdateSetupWidgets()

    def FindWidgets(self,*,uPageName:str,uWidgetName:str,bIgnoreError:bool=False) -> List[cWidgetBase]:
        """ Find a set widgets with a given name """
        uWidgetNameRep:str
        uPageNameRep:str
        aPages:List[str]
        aWidgets:List[cWidgetBase]
        oWidget:cWidgetBase
        oPage:cScreenPage

        aRet:List[cWidgetBase] = []
        if "@" in uWidgetName:
            uWidgetName,uPageName=uWidgetName.split(u"@")

        uWidgetNameRep = ReplaceVars(uWidgetName)
        uPageNameRep   = ReplaceVars(uPageName)
        if uPageNameRep=="":
            if self.oCurrentPage is not None:
                uPageNameRep=self.oCurrentPage.uPageName

        aPages=[]
        if uPageNameRep!="*":
            aPages.append(uPageNameRep)
        else:
            for uPageNameRep in self.oScreenPages:
                aPages.append(uPageNameRep)

        for uPageName in aPages:
            oPage=self.oScreenPages.get(uPageName)
            if oPage is None:
                if not bIgnoreError:
                    uMsg:str=u'The Screen: Page [%s] for Widget [%s] not found:' % (uPageName,uWidgetNameRep)
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
                uMsg:str=u'The Screen: Widget not found:'+uWidgetNameRep
                Logger.error (uMsg)
                self.DumpWidgets(uPageNameRep)

        return aRet

    def DumpWidgets(self,uPageName:str):

        uPageNameRep:str
        aPages:List[str]
        oWidget:cWidgetBase
        oPage:cScreenPage
        uPageNameRep   = ReplaceVars(uPageName)

        if uPageNameRep=="":
            if self.oCurrentPage is not None:
                uPageNameRep=self.oCurrentPage.uPageName

        aPages=[]
        if uPageNameRep!="*":
            aPages.append(uPageNameRep)
        else:
            for uPageNameRep in self.oScreenPages:
                aPages.append(uPageNameRep)

        for uPageName in aPages:
            oPage=self.oScreenPages.get(uPageName)
            if oPage is None:
                uMsg:str=u'The Screen: Dump: Page [%s]not found: ' % uPageName
                Logger.error (uMsg)
            else:
                for oWidget in oPage.aWidgets:
                    Logger.debug("Widget:[%s] Page:[%s]" % (oWidget.uName,oWidget.oParentScreenPage.uPageName))
                Logger.debug("")
                for uWidgetName in oPage.dWidgets:
                    Logger.debug("Widget:[%s]" % uWidgetName)



    def GuiIsBlocked(self) -> bool:
        """ returns, if the Gui is Blocked"""
        if self.iBlockCount>0:
            Logger.debug("GUI action ignored, GUI is locked")
            self.iBlockAskCount += 1
        else:
            self.iBlockAskCount = 0

        if self.iBlockAskCount>5:
            Logger.warning("Overiding locked GUI, (prevent unlocked GUI)")
            self.iBlockCount = 0
            self.iBlockAskCount = 0
        return self.iBlockCount>0

    def BlockGui(self,*,bStatus:bool) -> None:
        """ Blocks or unblocks the Gui"""
        if bStatus:
            self.iBlockCount += 1
        else:
            self.iBlockCount -= 1
        if self.iBlockCount<0:
            Logger.warning("Unlocking mismatch, unlocking unlocked GUI")
            self.iBlockCount = 0

    # noinspection PyUnusedLocal
    def on_motion(self, window,etype, motionevent) -> None:
        """ To detect, if we still have a down touch if we missed the touch_up message so we do not want endless repeat """
        self.uLastTouchType  = etype

    def DumpPages(self,*, uFilter:str='') -> None:
        """ Dumps the names of all pages to the log file"""
        Logger.error(u'Available Pages:')
        for uKey in sorted(self.oScreenPages):
            if uFilter=="":
                Logger.error(uKey)
            else:
                if uFilter in uKey:
                    Logger.error(uKey)
