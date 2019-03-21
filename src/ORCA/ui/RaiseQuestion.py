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

from kivy.uix.widget                import Widget
from kivy.uix.boxlayout             import BoxLayout
from kivy.uix.popup                 import Popup
from kivy.uix.button                import Button

from ORCA.ui.BasePopup              import cBasePopup,SettingSpacer
from ORCA.vars.Replace              import ReplaceVars
from ORCA.widgets.core.ScrollableLabelLarge   import cScrollableLabelLarge

import ORCA.Globals as Globals

__all__ = ['cRaiseQuestion','ShowQuestionPopUp']

class cRaiseQuestion(cBasePopup):
    """ Shows a question popup """
    def __init__(self):
        super(cRaiseQuestion, self).__init__()
        self.oPopup         = None
        self.oBtnlayout     = None
        self.oLabel         = None
        self.oBtn1          = None
        self.oBtn2          = None
        self.oBtnDetails    = None
        self.uMessage       = u''
        self.fktYes         = None
        self.fktNo          = None
        self.uStringDetails = ''

    def RaiseQuestion(self,uTitle='',uMessage='',fktYes=None,fktNo=None,uStringYes='',uStringNo='',uStringDetails=''):
        """ Shows the question """
        oContent = BoxLayout(orientation='vertical', spacing='5dp')

        self.uMessage=uMessage
        self.oPopup =  Popup(title=ReplaceVars(uTitle),content=oContent, size=(Globals.iAppWidth*0.9,Globals.iAppHeight*0.9),size_hint=(None, None),auto_dismiss=False)
        self.oLabel  = cScrollableLabelLarge(text=ReplaceVars(uMessage),size_hint=(1, None),size=(Globals.iAppWidth*0.86, Globals.iAppHeight*0.4),markup = True, noxscroll=True,)

        oContent.add_widget(Widget())
        oContent.add_widget(self.oLabel)
        oContent.add_widget(Widget())
        oContent.add_widget(SettingSpacer())
        self.fktYes=fktYes
        self.fktNo=fktNo

        # 2 buttons are created for accept or cancel the current value
        self.oBtnlayout      = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        if uStringYes!='':
            self.oBtn1            = Button(text=ReplaceVars(uStringYes))
            self.oBtn1.bind(on_release=self.fktYES)
            self.oBtnlayout.add_widget(self.oBtn1)

        if uStringDetails!='':
            self.uStringDetails=uStringDetails
            self.oBtnDetails            = Button(text=ReplaceVars('$lvar(452)'))
            self.oBtnDetails.bind(on_release=self.fktDetails)
            self.oBtnlayout.add_widget(self.oBtnDetails)

        if uStringNo!='':
            self.oBtn2             = Button(text=ReplaceVars(uStringNo))
            self.oBtn2.bind(on_release=self.fktNO)
            self.oBtnlayout.add_widget(self.oBtn2)

        oContent.add_widget(self.oBtnlayout)

        self.oPopup.open()
        return self.oPopup

    def fktDetails(self, *largs):
        """ switch between details and core message """
        if self.oLabel.text==self.uMessage:
            self.oLabel.text=self.uStringDetails
        else:
            self.oLabel.text=self.uMessage

    def fktYES(self, *largs):
        """ handles pressing the yes button """
        cBasePopup.ClosePopup(self)
        if self.fktYes:
            return self.fktYes()
        return None

    def fktNO(self, *largs):
        """ handles pressing the no button """
        cBasePopup.ClosePopup(self)
        if self.fktNo:
            return self.fktNo()
        return None

def ShowQuestionPopUp(uTitle='',uMessage='',fktYes=None,fktNo=None,uStringYes='',uStringNo='', uSound=u'question'):
    """ all in a function """
    Globals.oSound.PlaySound(uSound)
    oRaiseQuestion      = cRaiseQuestion()
    oRaiseQuestion.RaiseQuestion(uTitle=uTitle, uMessage=uMessage, fktYes=fktYes, fktNo=fktNo, uStringYes=uStringYes, uStringNo=uStringNo)
    return oRaiseQuestion

