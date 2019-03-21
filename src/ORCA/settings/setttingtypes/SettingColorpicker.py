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
        super(SettingColorPicker, self).__init__(**RemoveNoClassArgs(kwargs,SettingNumeric))
        self.newvalue = u''
        self.colorpicker = None

    def _create_popup(self, instance):
        """ create popup layout  """
        content = BoxLayout(orientation='vertical', spacing='5dp')
        self.popup = popup = Popup(title=self.title,content=content, size_hint=(0.9, 0.9))

        # Create the slider used for numeric input
        self.colorpicker = colorpicker = ColorPicker()

        content.add_widget(colorpicker)
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        btn = cMultiLineButton(text=ReplaceVars('$lvar(5008)'), halign='center', valign='middle')
        btn.bind(on_release=self._validate)
        btnlayout.add_widget(btn)
        btn = cMultiLineButton(text=ReplaceVars('$lvar(5009)'), halign='center', valign='middle')
        btn.bind(on_release=self._dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)
        colorpicker.bind(color= self.On_Color)
        # all done, open the popup !

        colorpicker.hex_color = self.value

        popup.open()

    def On_Color(self,instance, value):
        """ called, when a color is selected """
        self.newvalue = instance.hex_color

    def _validate(self, instance):
        """ User input ended """
        self._dismiss()
        if self.newvalue:
            self.value = self.newvalue


