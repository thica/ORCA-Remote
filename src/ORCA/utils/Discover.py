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

from typing import List

from kivy.uix.popup         import Popup
from kivy.uix.gridlayout    import GridLayout
from kivy.uix.stacklayout   import StackLayout
from kivy.uix.button        import Button
from kivy.uix.widget        import Widget
from kivy.uix.scrollview    import ScrollView
from kivy.metrics           import dp
from kivy.clock             import Clock
from ORCA.vars.Replace      import ReplaceVars

from ORCA.widgets.core.Label import cLabel
from ORCA.ui.BasePopup      import cBasePopup,SettingSpacer

import ORCA.Globals as Globals

__all__ = ['cDiscover_List']

class cDiscover_List(cBasePopup):
    """ creates a list of all discover results from all scripts """

    def __init__(self):
        self.oScrollContent: StackLayout = StackLayout(size_hint=(None, None))
        super().__init__()
    def ShowList(self):
        """ Shows the discover results """
        # create the popup
        oContent: GridLayout         = GridLayout(cols=1, spacing='5dp')
        oScrollview: ScrollView      = ScrollView( do_scroll_x=False)
        self.oPopup   = oPopup = Popup(content=oContent, title=ReplaceVars('$lvar(5028)'), size_hint=(0.9, 0.9),  auto_dismiss=False)

        #we need to open the popup first to get the metrics
        oPopup.open()
        #Add some space on top
        oContent.add_widget(Widget(size_hint_y=None, height=dp(2)))
        aDiscoverScripts: List = Globals.oScripts.GetScriptListForScriptType("DEVICE_DISCOVER")
        aScrollContent: List = []
        for uDiscoverScriptName in aDiscoverScripts:
            oScrollContentSingle: GridLayout = GridLayout(size_hint=(None, None),size=(oPopup.width, dp(10)))
            aScrollContent.append(oScrollContentSingle)
            oScrollContentSingle.bind(minimum_height=oScrollContentSingle.setter('height'))
            Globals.oScripts.RunScript(uDiscoverScriptName,**{'createlist':1,'oGrid':oScrollContentSingle})
            self.oScrollContent.add_widget(cLabel(text=Globals.oScripts.dScripts[uDiscoverScriptName].uSubType, background_color=[0.2, 0.2, 0.2, 1.0], color=[0.2, 0.9, 0.9, 1.0], size=(oPopup.width, dp(30)),size_hint=(None, None), halign='center'))
            self.oScrollContent.add_widget(oScrollContentSingle)
            self.oScrollContent.add_widget(SettingSpacer())

        # finally, add a cancel button to return on the previous panel
        oScrollview.add_widget(self.oScrollContent)
        oContent.add_widget(oScrollview)
        oContent.add_widget(SettingSpacer())

        oBtn: Button = Button(text=ReplaceVars('$lvar(5000)'), size=(oPopup.width, dp(50)),size_hint=(1, None))
        oBtn.bind(on_release=self.On_Cancel)
        oContent.add_widget(oBtn)

        #resize the Scrollcontent to fit to all Childs. Needs to be done, after the popup has been shown
        Clock.schedule_once(self.SetScrollSize, 0)

    # noinspection PyUnusedLocal
    def SetScrollSize(self, *args):
        """  Sets the size of the scoll window of the results """
        iHeight: int = 0
        for oChild in self.oScrollContent.children:
            if hasattr(oChild,"minimum_height"):
                iHeight = iHeight+oChild.minimum_height
            else:
                iHeight = iHeight+oChild.height
        self.oScrollContent.size=(self.oPopup.width,iHeight)

    # noinspection PyUnusedLocal
    def On_Cancel(self,instance):
        """ call handler for abort """
        cBasePopup.ClosePopup(self)

    def ClosePopup(self):
        """ will be called by keyhandler, if esc has been pressed """
        self.On_Cancel(self)

