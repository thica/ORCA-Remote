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
from kivy.uix.settings import Settings
from ORCA.settings.setttingtypes.SettingActions                 import SettingActions
from ORCA.settings.setttingtypes.SettingButtons                 import SettingButtons
from ORCA.settings.setttingtypes.SettingColorpicker             import SettingColorPicker
from ORCA.settings.setttingtypes.SettingFile                    import SettingFile
from ORCA.settings.setttingtypes.SettingInfo                    import SettingInfo
from ORCA.settings.setttingtypes.SettingNumericFloat            import SettingNumericFloat
from ORCA.settings.setttingtypes.SettingNumericSlider           import SettingNumericSlider
from ORCA.settings.setttingtypes.SettingPicture                 import SettingPicture
from ORCA.settings.setttingtypes.SettingScrollOptions           import SettingScrollOptions
from ORCA.settings.setttingtypes.SettingScrollOptionsWithOptions import SettingScrollOptionsWithOptions
from ORCA.settings.setttingtypes.SettingVarString               import SettingVarString

__all__ = ['RegisterSettingTypes']

def RegisterSettingTypes(oSetting:Settings):
    """ Register ORCA "homemade" settings widgets """
    # Button to have buttons on the settings
    oSetting.register_type('buttons', SettingButtons)
    # For more convinient input of numbers
    oSetting.register_type('numericslider', SettingNumericSlider)
    # Bypass a "bug" in kivy, that you can't scroll the original options popup
    oSetting.register_type('scrolloptions',  SettingScrollOptions)
    # An extension to have options on options
    oSetting.register_type('scrolloptionsoptions', SettingScrollOptionsWithOptions)
    # Having a colorpicker (for later use)
    oSetting.register_type('colorpicker', SettingColorPicker)
    # Info widget
    oSetting.register_type('info', SettingInfo)
    # File Picker
    oSetting.register_type('file', SettingFile)
    #Pictures
    oSetting.register_type('picture', SettingPicture)
    # Action List
    oSetting.register_type('actions', SettingActions)
    # For more convinient input of numbers
    oSetting.register_type('numericfloat', SettingNumericFloat)
    # To replace vars in strings
    oSetting.register_type('varstring', SettingVarString)

