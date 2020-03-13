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
from typing import Dict
from typing import List
from typing import Union

from kivy.uix.label         import Label
from kivy.uix.button        import Button
from kivy.uix.gridlayout    import GridLayout
from kivy.metrics           import dp

from ORCA.utils.LogError    import LogError
from ORCA.scripts.BaseScript import cBaseScript
from ORCA.vars.Replace      import ReplaceVars
from ORCA.vars.QueryDict    import TypedQueryDict

import ORCA.Globals as Globals

class cDiscoverScriptTemplate(cBaseScript):
    """ template class for discover scripts """
    def __init__(self):
        cBaseScript.__init__(self)
        self.dDevices:Dict[str,TypedQueryDict]  = {}
        self.uType:str                          = u'DEVICE_DISCOVER'
        self.iLineHeight:int                    = dp(35)
        self.oGrid:Union[GridLayout,None]       = None
        self.iDivide:int                        = 1
        self.bFirstLine:bool                    = True

    def RunScript(self, *args, **kwargs) -> Dict:
        """ main entry point to run the script """
        if 'createlist' in kwargs:
            self.oGrid = kwargs['oGrid']
            return self.CreateDiscoverList()
        else:
            return self.Discover(**kwargs)

    def AddHeaders(self) -> None:
        aHeaders:List[str] = self.GetHeaderLabels()
        self.iDivide = len(aHeaders) * 1

        self.oGrid.cols              = len(aHeaders)
        self.oGrid.row_default_height = self.iLineHeight
        self.oGrid.row_force_default = True
        self.oGrid.col_default_width = (Globals.iAppWidth * 0.9) / self.iDivide

        for uLabel in aHeaders:
            self.oGrid.add_widget(Label(text=ReplaceVars(uLabel)))

    def CreateDiscoverList(self) -> Dict:
        """ creates a list of discover results """
        try:
            self.bFirstLine = True
            self.dDevices.clear()
            self.ListDiscover()
        except Exception as e:
            LogError (uMsg="Template_Discover: Critical Error",oException=e)

        return self.dDevices

    def Discover(self,**kwargs) -> Dict:
        """ empty placeholder """
        return {}

    def GetHeaderLabels(self) -> List[str]:
        """ empty placeholder """
        return []

    def AddLine(self,aLine:List[str],dDevice:TypedQueryDict):
        """ adds a line to the discover results """
        aButtons:List[Button] = []

        if self.bFirstLine:
            self.AddHeaders()

        for uText in aLine:
            oButton=Button(text=uText, text_size=(Globals.iAppWidth*0.9/(self.iDivide*1.2),self.iLineHeight*0.9), shorten=True)
            oButton.dDevice=dDevice
            aButtons.append(oButton)
            oButton.bind(on_release=self.CreateDiscoverList_ShowDetails)
            self.oGrid.add_widget(oButton)

        self.bFirstLine = False

    def ListDiscover(self) -> None:
        """ empty placeholder """
        pass

    def CreateDiscoverList_ShowDetails(self,instance) -> None:
        """ empty placeholder """
        pass
