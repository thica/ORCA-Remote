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

__all__ = ['SettingButtons']

from typing                             import Dict
from typing                             import List
from typing                             import Optional
from kivy.uix.settings                  import SettingItem
from ORCA.widgets.core.MultiLineButton  import cMultiLineButton
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs
from ORCA.settings.setttingtypes.SettingScrollOptions import ScrollOptionsPopUp

class SettingButtons(SettingItem):
    """ a setting item with several buttons """

    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        # by purpose: we super to the settingitem directly, as SettingItem tries to read a non existing section
        super(SettingItem, self).__init__(**RemoveNoClassArgs(dInArgs=kwargs,oObject=SettingItem))
        self.dKwArgs:Dict                                           = kwargs
        # Level 1 = Buttons, Level 2 = Options per Button
        self.aOptions:Optional[List[List[str]]]                     = kwargs.get('buttonoptions',None)
        # Level 1 = Buttons, Level 2 = Options per Button, Level 3 = Suboptions per options
        self.aSubOptions:Optional[List[List[List[str]]]]            = kwargs.get('buttonsuboptions',None)
        self.iButton:int                                            = 0
        self.uOption                                                = u''
        self.oScrollOptionsPopup:Optional[ScrollOptionsPopUp]       = None
        self.oScrollSubOptionsPopup:Optional[ScrollOptionsPopUp]    = None
        aButton:Dict[str,str]
        i:int                                                       = 0

        if self.aOptions is not None:
            u=1

        for aButton in kwargs["buttons"]:
            oButton:cMultiLineButton = cMultiLineButton(text=aButton['title'], font_size= '15sp', halign='center', valign='middle')
            oButton.ID=aButton['id']
            oButton.iOrder = i
            self.add_widget(oButton)
            oButton.bind (on_release=self.On_ButtonPressed)
            i += 1
    def set_value(self, section, key, value) -> None:
        """ set_value normally reads the configparser values and runs on an error to do nothing here """
        return
    def On_ButtonPressed(self,oButton:cMultiLineButton) -> None:
        """ dispatch a message, when the button is pressed """
        if self.aOptions is None:
            self.panel.settings.dispatch('on_config_change',self.panel.config, self.section, self.key, oButton.ID)
        else:
            self.iButton = oButton.iOrder
            self.dKwArgs['options'] = self.aOptions[oButton.iOrder]
            self.oScrollOptionsPopup = ScrollOptionsPopUp(**self.dKwArgs)
            self.oScrollOptionsPopup.CreatePopup(self.value, self._set_option, None)

    def _set_option(self, oButton:cMultiLineButton):
        """ called when the first option is selected """
        self.oScrollOptionsPopup.popup.dismiss()
        if self.aSubOptions is None:
            uValue:str = '%s:%s'% (self.dKwArgs["buttons"][self.iButton]['id'], oButton.text)
            self.panel.settings.dispatch('on_config_change', self.panel.config, self.section, self.key, uValue)
        else:
            self.dKwArgs['options'] = self.aSubOptions[self.iButton][oButton.iIndex]
            self.uOption = oButton.text
            self.oScrollSubOptionsPopup = ScrollOptionsPopUp(**self.dKwArgs)
            self.oScrollSubOptionsPopup.CreatePopup(self.value, self._set_suboption, None)

    def _set_suboption(self, oButton:cMultiLineButton):
        """ called when the first option is selected """
        self.oScrollSubOptionsPopup.popup.dismiss()
        uValue: str = '%s:%s:%s' % (self.dKwArgs["buttons"][self.iButton]['id'],self.uOption,oButton.text)
        self.panel.settings.dispatch('on_config_change', self.panel.config, self.section, self.key, uValue)

