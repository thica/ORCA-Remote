# -*- coding: utf-8 -*-
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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

#  Copyright (c) 2024. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from typing                         import Union
from typing                         import List
from typing                         import Dict

from dataclasses                    import dataclass
from xml.etree.ElementTree          import Element
from collections                    import deque
from kivy.logger                    import  Logger
from ORCA.screen.ScreenPage import cScreenPage
from ORCA.vars.Access               import SetVar
from ORCA.vars.Access               import GetVar
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp

from ORCA.Globals import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.action.Action import cAction
else:
    from typing import TypeVar
    cAction     = TypeVar('cAction')

@dataclass
class cPageHistory:
    """
    A history object of the called page
    """
    uCalledByPageName:str
    uPageName:str


class cScreenPages(Dict[str,cScreenPage]):
    """ Class which holds all Screen Pages """
    def __init__(self):
        dict.__init__(self)
        self.aPageHistory:deque[cPageHistory] = deque(maxlen=30)

    def DeInit(self) -> None:
        """De-inits the list of pages"""
        self.clear()
        self.aPageHistory.clear()

    def AddPageFromXmlNode(self,*,oXMLPage:Element) -> None:
        """ Creates the Page Object, Parses the content and add it to the page list """
        oTmpScreenPage:cScreenPage = cScreenPage()
        oTmpScreenPage.InitPageFromXmlNode(oXMLNode=oXMLPage)
        if not oTmpScreenPage.uPageName in self:
            self[oTmpScreenPage.uPageName]=oTmpScreenPage
            oTmpScreenPage.AddPageElementsFromXmlNode(oXMLNode=oXMLPage)

    def GetLastPageReal(self) -> Union[cScreenPage,None]:
        """ returns the last (not current) page, ignoring popups and the queue stack """
        return self.get(GetVar('LASTPAGEREAL'))

    def GetLastPage(self) -> Union[cScreenPage,None]:
        """ returns the last (not current) page """
        return self.get(GetVar('LASTPAGE'))

    def GetCurrentPage(self) -> Union[cScreenPage,None]:
        """ returns the  current) page """
        return self.get(GetVar('CURRENTPAGE'))

    def AppendToPageQueue(self,*,oPage:cScreenPage) -> None:
        """  Appends a Page to the list of last shown pages"""
        if GetVar(uVarName = 'FIRSTPAGE') == '':
            if GetVar(uVarName='DEFINITIONSTARTPAGE') == '':
                SetVar(uVarName = 'FIRSTPAGE', oVarValue = oPage.uPageName)
            else:
                SetVar(uVarName='FIRSTPAGE', oVarValue=GetVar(uVarName='DEFINITIONSTARTPAGE'))
        SetVar(uVarName = 'CURRENTPAGE', oVarValue = oPage.uPageName)

        if len(self.aPageHistory)>0:
            SetVar(uVarName = 'LASTPAGEREAL', oVarValue = self.aPageHistory[-1].uPageName)

        if len(self.aPageHistory)>2:
            if oPage.uPageName == self.aPageHistory[-1].uCalledByPageName:
                SetVar(uVarName='LASTPAGE', oVarValue=self.aPageHistory[-2].uCalledByPageName)
                self.aPageHistory.pop()
                return

        self.aPageHistory.append(cPageHistory(uCalledByPageName=oPage.uCalledByPageName,uPageName=oPage.uPageName))
        if len(self.aPageHistory)>1:
            SetVar(uVarName = 'LASTPAGE', oVarValue = self.aPageHistory[-2].uPageName)

    def CreatePages(self,*,uPageName:str) -> None:
        """ Create all pages of all definitions or start the timer to create the next page """

        aActions:List[cAction]

        #either we create all of them immediatly, or scheduled, or on requests if interval = 0
        if Globals.bInitPagesAtStart or uPageName!='':
            if uPageName=='nextpage':
                if not self.CreateNextPage():
                    aActions=Globals.oEvents.CreateSimpleActionList(aActions=[{'string':'definetimer','timername':'scheduled page creation','switch':'off'}])
                    Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None,uQueueName='scheduled page creation')
                return
            if uPageName=='':
                # Scheduling Creating the pages
                aActions=Globals.oEvents.CreateSimpleActionList(aActions=[{'string':'showsplashtext','maintext':'$lvar(410)'}])

                for uPageName in self.keys():
                    SetVar(uVarName = 'PAGESTARTCOUNT_'+uPageName, oVarValue = '0')
                    if not uPageName=='Page_Settings':
                        Globals.oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'showsplashtext','subtext':uPageName},
                                                                                             {'string':'createpages','pagename':uPageName}
                                                                                            ])

                Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None,uQueueName="Create Pages")
            else:
                Logger.debug ('Creating Page:'+uPageName)
                self[uPageName].Create()
        else:
            if Globals.fDelayedPageInitInterval>0:
                aActions=Globals.oEvents.CreateSimpleActionList(aActions=[{'name':'Add timer for delayed/scheduled page creations',
                                                                           'string':'definetimer',
                                                                           'timername':'scheduled page creation',
                                                                           'interval':str(Globals.fDelayedPageInitInterval),
                                                                           'switch':'on',
                                                                           'actionname':'createnextpage'}])
                Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None,uQueueName='TimerForDelayedPageCreation')

    def CreatePage(self,*,uPageName:str) -> None:
        """ Will be used by EventDispatcher in case pages will not be created at startup """

        if uPageName=='':
            Globals.oTheScreen.oCurrentPage.Create()
            return
        oPage:cScreenPage = self.get(uPageName)
        if oPage:
            oPage.Create()
            return
        ShowErrorPopUp(uTitle='Create Page: Fatal Error',uMessage='TheScreen: Fatal Error:Page does not exist:'+uPageName,bAbort=True)

    def CreateNextPage(self) -> bool:
        """ will be used for late schedule init
            Create the next page, which has not been init by now
            return true , if a page has been initialized, false if nothing left """

        oPage:cScreenPage

        for oPage in self.values():
            if not oPage.bIsInit and not oPage.bPreventPreInit:
                oPage.Create()
                return True
        return False
