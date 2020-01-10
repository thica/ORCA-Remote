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

from kivy.uix.settings                  import SettingString

__all__ = ['SettingInputHelper']

class SettingInputHelper(SettingString):
    """ Shows in input field for settings """

    # noinspection PyMissingConstructor,PyUnusedLocal
    def __init__(self, **kwargs):
        self.settings = None
        self.action   = ""
        self.title    = ""
        self.config   = None

    def GetInput(self, settings,config,section,key,title,action,value) -> None:
        """ gets the input """
        # title = title to show
        self.title      = title
        # value = text to change
        self.value      = value
        # key = the key returned on on_config_change
        self.key        = key
        # section = the section returned on on_config_change
        self.section    = section
        # action =      customer vlaue combined to the value
        self.action     = action

        self.settings = settings
        self.config   = config
        self._create_popup(None)

    def _validate(self, instance) -> None:
        """ input is done """
        self._dismiss()
        value = self.textinput.text.strip()
        value='%s:%s:%s'%(self.action, self.value,value)

        self.settings.dispatch('on_config_change', self.config, self.section, self.key, value)

