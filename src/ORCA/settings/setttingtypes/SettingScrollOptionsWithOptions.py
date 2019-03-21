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

from kivy.logger                                      import Logger
from ORCA.settings.setttingtypes.SettingScrollOptions import SettingScrollOptions
from ORCA.settings.setttingtypes.SettingScrollOptions import ScrollOptionsPopUp

__all__ = ['SettingScrollOptionsWithOptions']

class SettingScrollOptionsWithOptions(SettingScrollOptions):
    """ showing a sub scroll options setting from a scroll option """
    def __init__(self, **kwargs):

        self.aSubOptions = []
        self.aSubOption  = []
        self.subpopup    = None
        self.uOption     = None
        self.oSubScrollOptionsPopup = None
        self.register_event_type('on_release')
        super(SettingScrollOptionsWithOptions, self).__init__(**kwargs)
        for aSubOptions in kwargs["suboptions"]:
            self.aSubOptions.append(aSubOptions)
        if not len(self.aSubOptions)==len(self.options):
            Logger.debug("Warning: SubScrollOptions do not match Scrolloptions")

    def _set_option(self, instance):
        """ called when the first option is selected """
        iIndex=self.GetSelectedIndex(instance)
        if iIndex<=len(self.aSubOptions):
            self.aSubOption=self.aSubOptions[iIndex]
            if len(self.aSubOption) > 0:
                self.uOption=instance.text
                self._create_subpopup(instance)
            else:
                self.value = '%s:%s'%(instance.text,'')
                self.popup.dismiss()
        else:
            self.value = '%s:%s'%(instance.text,'')
            self.popup.dismiss()

    def _set_suboption(self, instance):
        """ called, when the second option is selected """
        self.value = '%s:%s'%(self.uOption,instance.text)
        self.subpopup.dismiss()
        self.popup.dismiss()

    def GetSelectedIndex(self, instance):
        """ gets the selected option index """
        i=0
        for option in self.options:
            if option == instance.text:
                return i
            i+=1
        return 0

    def _create_subpopup(self, instance):
        kwargs={'title':self.uOption,'options':self.aSubOption}
        self.oSubScrollOptionsPopup=ScrollOptionsPopUp(**kwargs)
        self.oSubScrollOptionsPopup.CreatePopup(self.value,self._set_suboption,None)
        self.subpopup=self.oSubScrollOptionsPopup.popup

