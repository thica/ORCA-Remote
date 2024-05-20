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

from typing                             import Union
from kivy.uix.boxlayout                 import BoxLayout
from kivy.uix.popup                     import Popup
from kivy.uix.colorpicker               import ColorPicker
from kivy.uix.settings                  import SettingNumeric

from ORCA.vars.Replace                  import ReplaceVars
from ORCA.widgets.core.MultiLineButton  import cMultiLineButton
from ORCA.settings.setttingtypes.Base   import SettingSpacer
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs

__all__ = ['SettingColorPicker']

class SettingColorPicker(SettingNumeric):
    """ A colorpicker settings """
    def __init__(self, **kwargs):
        super(SettingColorPicker, self).__init__(**RemoveNoClassArgs(dInArgs=kwargs,oObject=SettingNumeric))
        self.newvalue = ''
        self.oColorpicker:Union[ColorPicker,None] = None

    def _create_popup(self, instance) -> None:
        """ create popup layout  """
        oContent:BoxLayout = BoxLayout(orientation='vertical', spacing='5dp')
        self.popup = popup = Popup(title=self.title,content=oContent, size_hint=(0.9, 0.9))

        # Create the slider used for numeric input
        oColorpicker:ColorPicker = ColorPicker()
        self.oColorpicker = oColorpicker

        oContent.add_widget(oColorpicker)
        oContent.add_widget(SettingSpacer())

        oBtn:cMultiLineButton

        # 2 buttons are created for accept or cancel the current value
        oBtnlayout:BoxLayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        oBtn = cMultiLineButton(text=ReplaceVars('$lvar(5008)'), halign='center', valign='middle')
        oBtn.bind(on_release=self._validate)
        oBtnlayout.add_widget(oBtn)
        oBtn = cMultiLineButton(text=ReplaceVars('$lvar(5009)'), halign='center', valign='middle')
        oBtn.bind(on_release=self._dismiss)
        oBtnlayout.add_widget(oBtn)
        oContent.add_widget(oBtnlayout)
        oColorpicker.bind(color= self.On_Color)
        # all done, open the popup !

        oColorpicker.hex_color = self.value

        popup.open()

    # noinspection PyUnusedLocal
    def On_Color(self,instance:ColorPicker, value) -> None:
        """ called, when a color is selected """
        self.newvalue = instance.hex_color

    def _validate(self, instance:ColorPicker) -> None:
        """ User input ended """
        self._dismiss()
        if self.newvalue:
            self.value = self.newvalue


