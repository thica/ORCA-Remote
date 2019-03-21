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

from collections                    import deque
from kivy.logger                    import  Logger
from ORCA.ScreenPage                import cScreenPage
from ORCA.vars.Access               import SetVar
from ORCA.vars.Access               import GetVar
from ORCA.utils.LogError            import LogError
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp

import ORCA.Globals as Globals

class cScreenPages(dict):
    """ Class which holds all Screen Pages """
    def __init__(self):
        dict.__init__(self)
        self.aPageQueue=deque(maxlen=10)

    def DeInit(self):
        self.clear()
        self.aPageQueue.clear()

    def AddPageFromXmlNode(self,oXMLPage):
        """ Creates the Page Object, Parses the content and add it to the page list """
        oTmpScreenPage     = cScreenPage()
        oTmpScreenPage.InitPageFromXmlNode(oXMLNode=oXMLPage)
        if not oTmpScreenPage.uPageName in self:
            self[oTmpScreenPage.uPageName]=oTmpScreenPage
            oTmpScreenPage.AddPageElementsFromXmlNode(oXMLNode=oXMLPage)

    def GetLastPage(self):
        """ returns the last (not current) page """
        if len(self.aPageQueue)>1:
            return self.aPageQueue[-2]
        return None

    def GetCurrentPage(self):
        """ returns the  current) page """
        if len(self.aPageQueue):
            return self.aPageQueue[-1]
        return None

    def AppendToPageQueue(self,oPage):
        """  Appends a Page to the list of last shown pages"""
        if GetVar(uVarName = u'FIRSTPAGE') == u'':
            SetVar(uVarName = u'FIRSTPAGE', oVarValue = oPage.uPageName)
        SetVar(uVarName = u'CURRENTPAGE', oVarValue = oPage.uPageName)

        self.aPageQueue.append(oPage)
        if len(self.aPageQueue)>1:
            SetVar(uVarName = u'LASTPAGE', oVarValue = self.aPageQueue[-2].uPageName)

    def CreatePages(self,uPageName):
        """ Create all pages of all defitions or start the timer to create the next page """

        #either we create all of them immediatly, or scheduled, or on requests if interval = 0
        if Globals.bInitPagesAtStart or uPageName!="":
            if uPageName=="nextpage":
                if not self.CreateNextPage():
                    aActions=Globals.oEvents.CreateSimpleActionList([{'string':'definetimer','timername':'scheduled page creation','switch':'off'}])
                    Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
                return
            if uPageName=="":
                # Scheduling Creating the pages
                aActions=Globals.oEvents.CreateSimpleActionList([{'string':'showsplashtext','maintext':'$lvar(410)'}])

                for uPageName in self:
                    SetVar(uVarName = "PAGESTARTCOUNT_"+uPageName, oVarValue = "0")
                    if not uPageName=="Page_Settings":
                        Globals.oEvents.AddToSimpleActionList(aActions,[{'string':'showsplashtext','subtext':uPageName},
                                                                                 {'string':'createpages','pagename':uPageName}
                                                                                ])

                Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
            else:
                Logger.debug (u'Creating Page:'+uPageName)
                self[uPageName].Create()
        else:
            if Globals.fDelayedPageInitInterval>0:
                aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Add timer for delayed/scheduled page creations','string':'definetimer','timername':'scheduled page creation','interval':str(Globals.fDelayedPageInitInterval),'switch':'on','actionname':'createnextpage'}])
                Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

    def CreatePage(self,uPageName):
        """ Will be used by EventDispatcher in case pages will not be created at startup """

        if uPageName==u'':
            Globals.oTheScreen.oCurrentPage.Create()
            return
        oPage=self.get(uPageName)
        if oPage:
            oPage.Create()
            return
        uMsg=LogError(u'TheScreen: Fatal Error:Page does not exist:'+uPageName)
        ShowErrorPopUp(uTitle="Fatal Error",uMessage=uMsg,bAbort=True)

    def CreateNextPage(self):
        """ will be used for late schedule init
            Create the next page, which has not been init by now
            return true , if a page has been initialized, false if nothing left """

        for uPageName in self:
            oPage=self[uPageName]
            if not oPage.bIsInit and not oPage.bPreventPreInit:
                oPage.Create()
                return True
        return False
