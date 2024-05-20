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

from typing             import Dict
from typing             import Iterable
from ORCA.vars.Access   import SetVar

__all__ = ['BuildSettingOptionList','BuildSettingOptionListDict','BuildSettingOptionListVar','BuildSettingOptionListDictVar']

def BuildSettingOptionList(aArray:Iterable[str]) -> str:
    """
    Little helper function to create a json option list
    """
    uToken:str
    uValueString:str=''
    for uToken in aArray:
        uValueString+=f'"{uToken}",'
    return uValueString[:-1]

def BuildSettingOptionListVar(aArray:Iterable[str],uDestVar:str) -> str:
    """
    Little helper function to create a json option list
    """
    uValueString = f'[{BuildSettingOptionList(aArray)}]'
    SetVar(uDestVar,uValueString)
    return uValueString


def BuildSettingOptionListDict(dArray:Dict[str,str]) -> str:
    """
    Little helper function to create a json option list
    """
    uToken:str
    uValueString:str=''
    for uToken in dArray:
        uValueString+='\"'+dArray[uToken]+" ["+uToken+"]" +'\",'
    return uValueString[:-1]

def BuildSettingOptionListDictVar(dArray:Dict[str,str],uDestVar:str) -> str:
    """
    Little helper function to create a json option list
    """
    uValueString = f'[{BuildSettingOptionListDict(dArray)}]'
    SetVar(uDestVar, uValueString)
    return uValueString
