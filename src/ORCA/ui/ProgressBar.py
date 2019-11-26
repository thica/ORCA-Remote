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

from typing                         import Union
from kivy.uix.widget                import Widget
from kivy.uix.label                 import Label
from kivy.uix.progressbar           import ProgressBar
from kivy.uix.boxlayout             import BoxLayout
from kivy.uix.popup                 import Popup
from kivy.uix.button                import Button

from ORCA.ui.BasePopup              import cBasePopup
from ORCA.ui.BasePopup              import SettingSpacer
from ORCA.vars.Replace              import ReplaceVars

import ORCA.Globals as Globals

__all__ = ['cProgressBar']

class cProgressBar(cBasePopup):
    """ Progressbar popup class """

    def __init__(self):
        super(cProgressBar, self).__init__()
        self.oLabel:Union[Label:None]               = None
        self.oProgressText:Union[Label,None]        = None
        self.oProgressBar:Union[ProgressBar,None]   = None
        self.iMax:int                               = 100
        self.bCancel:bool                           = False

    def Show(self,uTitle:str,uMessage:str,iMax:int) -> Popup:
        """ Shows the Popup """
        self.iMax           = iMax
        self.bCancel        = False
        oContent:BoxLayout  = BoxLayout(orientation='vertical', spacing='5dp')
        iHeight:int         = int(Globals.iAppHeight*0.5)
        if Globals.uDeviceOrientation=="landscape":
            iHeight=int(Globals.iAppHeight*0.9)
        self.oPopup         = Popup(title=ReplaceVars(uTitle),content=oContent, size=(Globals.iAppWidth*0.9,iHeight),size_hint=(None, None),auto_dismiss=False)
        self.oLabel         = Label(text=ReplaceVars(uMessage), text_size=(Globals.iAppWidth*0.86, None), shorten=True, valign='top',halign='left')
        self.oProgressText  = Label(valign='top',halign='center',text_size=(Globals.iAppWidth*0.86, None), shorten=True)
        oContent.add_widget(Widget())
        oContent.add_widget(self.oLabel)
        oContent.add_widget(Widget())
        self.oProgressText.text=""

        self.oProgressBar = ProgressBar(size_hint_y=None, height='50dp', max=iMax)
        oContent.add_widget(self.oProgressBar)
        oContent.add_widget(self.oProgressText)
        oContent.add_widget(SettingSpacer())
        oBtn:Button = Button(size_hint_y=None, height='50dp',text=ReplaceVars('$lvar(5009)'))
        oBtn.bind(on_release=self.OnCancel)
        oContent.add_widget(oBtn)
        self.oPopup.open()
        return self.oPopup

    def Update(self,iCurrent:int,uTxt:str=None) -> None:
        """ Updates the progressbar """
        self.oProgressBar.value = iCurrent
        self.oProgressText.text = r"[%3.2f%%]" % (iCurrent * 100. / self.iMax)
        if uTxt:
            self.oLabel.text = uTxt

    def ReInit(self,uTitle:str,uMessage:str,iMax:int) -> None:
        """ Re-Starts the progressbar """
        self.oPopup.title       = ReplaceVars(uTitle)
        self.oLabel.text        = ReplaceVars(uMessage)
        self.oProgressBar.value = 0
        self.bCancel            = False
        self.SetMax(iMax)

    def SetMax(self,iMax:int) -> None:
        """ Sets the maximal Progressbar Value """
        self.oProgressBar.max   = iMax
        self.iMax               = iMax

    # noinspection PyUnusedLocal
    def OnCancel(self, *largs) -> None:
        """ Cancel event handler """
        self.bCancel=True

    def ClosePopup(self) -> None:
        """ will be called by keyhandler, if esc has been pressed """
        self.OnCancel(self)
        cBasePopup.ClosePopup(self)



