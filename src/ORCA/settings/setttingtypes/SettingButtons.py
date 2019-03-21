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

__all__ = ['SettingButtons']

from kivy.uix.settings                  import SettingItem
from ORCA.widgets.core.MultiLineButton  import cMultiLineButton
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs

class SettingButtons(SettingItem):
    """ a setting item with several buttons """

    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        # by purpose: we super to the settingitem directly, as SettingItem tries to read a non existing section
        super(SettingItem, self).__init__(**RemoveNoClassArgs(kwargs,SettingItem))

        for aButton in kwargs["buttons"]:
            oButton=cMultiLineButton(text=aButton['title'], font_size= '15sp', halign='center', valign='middle')
            oButton.ID=aButton['id']
            self.add_widget(oButton)
            oButton.bind (on_release=self.On_ButtonPressed)
    def set_value(self, section, key, value):
        """ set_value normally reads the configparser values and runs on an error to do nothing here """
        return
    def On_ButtonPressed(self,instance):
        """ dispatch a message, when the button is pressed """
        self.panel.settings.dispatch('on_config_change',self.panel.config, self.section, self.key, instance.ID)
        # self.panel.config._do_callbacks(self.section, self.key, instance.ID)

