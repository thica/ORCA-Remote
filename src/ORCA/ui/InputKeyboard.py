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

from kivy.uix.widget                    import Widget
from kivy.uix.boxlayout                 import BoxLayout
from kivy.uix.popup                     import Popup
from kivy.uix.textinput                 import TextInput
from kivy.logger                        import Logger
from kivy.clock                         import Clock

from ORCA.ui.BasePopup                  import cBasePopup,SettingSpacer
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.vars.Access                   import SetVar
from ORCA.vars.Access                   import GetVar
from ORCA.widgets.core.MultiLineButton  import cMultiLineButton

import ORCA.Globals as Globals

__all__ = ['ShowKeyBoard']

class cInputKeyboard(cBasePopup):
    """  Shows an Input keyboard """
    def __init__(self):
        super(cInputKeyboard, self).__init__()
        self.oTextInput = None
        self.uDestVar   = u''
        self.oFktNotify = None

    def ScheduledSetFocus(self, *largs):
        """ sets the focus to the input field, called by the clock, to avoid timing problems """
        self.oTextInput.focus=True

    def ShowKeyBoard(self,uDestVar,oFktNotify, uTitle):
        """ create popup layout """
        self.oFktNotify=oFktNotify
        self.uDestVar  =uDestVar
        oContent = BoxLayout(orientation='vertical', spacing='5dp')
        self.oPopup =  Popup(uTitle='Input',content=oContent, size_hint=(None, None), size=(Globals.iAppWidth*0.9,Globals.iAppHeight*0.35),auto_dismiss=False, pos_hint={'x': .05, 'top': 1})
        uText=GetVar(uVarName = self.uDestVar)
        if uText is None:
            uText=u''
        Logger.debug("InputKeyboard: Preassigning Value [%s]" % uText)
        #self.oTextInput = textinput = TextInput(text=uText, focus=False,multiline=False, size_hint_y=None, height='30dp')
        self.oTextInput = textinput = TextInput(text=uText,multiline=False, size_hint_y=None, height='30dp')
        self.oTextInput.bind(on_text_validate=self.On_Enter)

        # construct the content, widget are used as a spacer
        oContent.add_widget(Widget())
        oContent.add_widget(textinput)
        oContent.add_widget(Widget())
        oContent.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        oBtnlayout      = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        oBtn            = cMultiLineButton(text=ReplaceVars('$lvar(5008)'), halign='center', valign='middle')
        oBtn.bind (on_release=self.On_Enter)
        oBtnlayout.add_widget(oBtn)
        oBtn             = cMultiLineButton(text=ReplaceVars('$lvar(5009)'), halign='center', valign='middle')
        oBtn.bind(on_release=self.On_Cancel)
        oBtnlayout.add_widget(oBtn)
        oContent.add_widget(oBtnlayout)

        #if we do setup the focus before the popup is shown, no vkeyboard is shown
        self.oPopup.bind(on_open=self.ScheduledSetFocus)
        self.oPopup.open()

    def On_Cancel(self,instance):
        """ Reacts to pressing the cancel button """
        if self.oTextInput:
            self.oTextInput.focus = False
        cBasePopup.ClosePopup(self)

    def ClosePopup(self):
        """will be called by keyhandler, if esc has been pressed"""
        self.On_Cancel(self)
    def On_Enter(self,instance):
        """
        Will be Called by Input Popup, if the users press Enter
        Closes the Popoup
        Hides Keyboard
        Passes Input string to destination variable
        Call Notifier Function
        """

        SetVar(uVarName = self.uDestVar, oVarValue = self.oTextInput.text)
        self.ClosePopup()
        # schedule action, after PopUp disappears
        if self.oFktNotify:
            Clock.schedule_once(self.fDoNotify, 0)
            #self.fDoNotify(self.oTextInput.text)

    def fDoNotify(self, *largs):
        """ helper """
        self.oFktNotify(self.oTextInput.text)


def ShowKeyBoard(sDestVar,oFktNotify,  uTitle = 'Input'):
    """ convinience abstraction to show the keyboard class """
    oInputKeyboard      = cInputKeyboard()
    oInputKeyboard.ShowKeyBoard(sDestVar,oFktNotify, uTitle)
    return oInputKeyboard
