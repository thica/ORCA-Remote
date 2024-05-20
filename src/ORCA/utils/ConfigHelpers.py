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

from typing import Union

from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.TypeConvert import ToFloat
from ORCA.utils.TypeConvert import ToInt
from ORCA.utils.Path        import cPath
from kivy.config            import ConfigParser

__all__ = ['Config_GetDefault_Bool',
           'Config_GetDefault_Str',
           'Config_GetDefault_Float',
           'Config_GetDefault_Int',
           'Config_GetDefault_Path']

def Config_GetDefault_Bool(*,oConfig: ConfigParser, uSection: str, uOption: str, uDefaultValue: str) ->bool:
    return Config_GetDefault_Str(oConfig=oConfig,uSection=uSection,uOption=uOption, vDefaultValue=uDefaultValue) == '1'

def Config_GetDefault_Float(*,oConfig: ConfigParser, uSection: str, uOption: str, uDefaultValue: str) ->float:
    return ToFloat(Config_GetDefault_Str(oConfig=oConfig,uSection=uSection,uOption=uOption, vDefaultValue=uDefaultValue))

def Config_GetDefault_Int(*,oConfig: ConfigParser, uSection: str, uOption: str, uDefaultValue: str) -> int:
    return ToInt(Config_GetDefault_Str(oConfig=oConfig,uSection=uSection,uOption=uOption, vDefaultValue=uDefaultValue))

def Config_GetDefault_Path(*,oConfig: ConfigParser, uSection: str, uOption: str, uDefaultValue: str) -> cPath:
    return cPath(Config_GetDefault_Str(oConfig=oConfig,uSection=uSection,uOption=uOption, vDefaultValue=uDefaultValue))

def Config_GetDefault_Str(*,oConfig: ConfigParser , uSection: str, uOption: str, vDefaultValue:Union[None,bool,str]) -> str:
    """
    Replacement for the kivy function

    :param oConfig: The configparser object
    :param uSection: The name of the section
    :param uOption: The name of the option
    :param vDefaultValue: The default value
    :return: The value of an ini setting or the default value
    """
    uDefaultValue:str = ''

    if not oConfig.has_section(uSection):
        oConfig.add_section(uSection)
    if not oConfig.has_option(uSection, uOption):
        if vDefaultValue is not None:
            if type(vDefaultValue)==bool:
                if vDefaultValue:
                    uDefaultValue: str='1'
                else:
                    uDefaultValue: str = '0'
            else:
                uDefaultValue = vDefaultValue
            oConfig.set(uSection, uOption, uDefaultValue)
        return uDefaultValue
    uRetVal: str = ToUnicode(oConfig.get(uSection, uOption))
    return uRetVal
