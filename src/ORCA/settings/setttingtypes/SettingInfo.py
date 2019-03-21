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

from kivy.uix.settings                  import SettingString
from kivy.uix.settings                  import SettingItem
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs

__all__ = ['SettingInfo']

class SettingInfo(SettingString):
    """ A setting item, which just shows an information """
    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        super(SettingItem, self).__init__(**RemoveNoClassArgs(kwargs,SettingString))
        value=kwargs["info"]
        self.value=value
    def _create_popup(self, instance):
        """ shows the popup """
        SettingString._create_popup(self,instance)
        self.textinput.readonly=True
        #self.textinput._copy(self.value)

    def set_value(self, section, key, value):
        """ set_value normally reads the configparser values and runs on an error
        to do nothing here """
        return

