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

from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.TypeConvert import ToFloat
from ORCA.utils.TypeConvert import ToInt
from ORCA.utils.Path        import cPath


__all__ = ['Config_GetDefault_Bool',
           'Config_GetDefault_Str',
           'Config_GetDefault_Float',
           'Config_GetDefault_Int',
           'Config_GetDefault_Path']

def Config_GetDefault_Bool(oConfig, uSection, uOption, uDefaultValue):
    return Config_GetDefault_Str(oConfig, uSection, uOption, uDefaultValue) == u'1'

def Config_GetDefault_Float(oConfig, uSection, uOption, uDefaultValue):
    return ToFloat(Config_GetDefault_Str(oConfig, uSection, uOption, uDefaultValue))

def Config_GetDefault_Int(oConfig, uSection, uOption, uDefaultValue):
    return ToInt(Config_GetDefault_Str(oConfig, uSection, uOption, uDefaultValue))

def Config_GetDefault_Path(oConfig, uSection, uOption, uDefaultValue):
    return cPath(Config_GetDefault_Str(oConfig, uSection, uOption, uDefaultValue))

def Config_GetDefault_Str(oConfig, uSection, uOption, uDefaultValue):
    """
    Replacement for the kivy function

    :rtype: string
    :param Config oConfig: The configparser object
    :param string uSection: The name of the section
    :param string uOption: The name of the option
    :param string uDefaultValue: The default value
    :return: The value of an ini setting or the default value
    """
    if not oConfig.has_section(uSection):
        oConfig.add_section(uSection)
    if not oConfig.has_option(uSection, uOption):
        if uDefaultValue is not None:
            if type(uDefaultValue)==bool:
                if uDefaultValue:
                    uDefaultValue=u'1'
                else:
                    uDefaultValue = u'0'
            oConfig.set(uSection, uOption, uDefaultValue)
        return uDefaultValue
    sRetVal = ToUnicode(oConfig.get(uSection, uOption))
    return sRetVal
