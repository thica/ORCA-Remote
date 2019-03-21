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

__all__ = ['BuildSettingOptionList','BuildSettingOptionListDict']

def BuildSettingOptionList(aArray):
    """
    Little helper function to create a json option list
    """
    uValueString=u''
    for uToken in aArray:
        uValueString+=u'\"'+uToken+u'\",'
    return uValueString[:-1]

def BuildSettingOptionListDict(dArray):
    """
    Little helper function to create a json option list
    """
    uValueString=u''
    for uToken in dArray:
        uValueString+=u'\"'+dArray[uToken]+u" ["+uToken+u"]" +u'\",'
    return uValueString[:-1]
