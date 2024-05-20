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

from os.path import sep,  isdir
from typing import List
from typing import Tuple
from typing import Callable
from ctypes import windll, create_unicode_buffer, Array, c_wchar
import string

def GetDrives() -> List[Tuple[str,str]]:
    """
    Returns the list of available drives for the operating system
    """
    aDrives:List[Tuple[str,str]] = []
    iBitmask:int = windll.kernel32.GetLogicalDrives()
    uLetter:str
    oName:Array[c_wchar]
    uDrive:str
    GetVolumeInformationW:Callable = windll.kernel32.GetVolumeInformationW
    for uLetter in string.ascii_uppercase:
        if iBitmask & 1:
            oName = create_unicode_buffer(64)
            # get name of the drive
            uDrive = uLetter + ':'
            GetVolumeInformationW(uDrive + sep, oName, 64, None,None, None, None, 0)
            if isdir(uDrive):
                aDrives.append((uDrive, oName.value))
        iBitmask >>= 1
    return aDrives