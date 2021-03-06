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

from os.path import sep,  isdir, expanduser
from os import walk
from typing import List


# noinspection PyListCreation
def GetDrives() -> List:
    """
    Returns the list of available drives for the operating system
    """
    aDrives = []
    aDrives.append((sep, sep))
    aDrives.append((expanduser(u'~'), '~/'))
    uPlaces = (sep + u'mnt', sep + u'media')
    for uPlace in uPlaces:
        if isdir(uPlace):
            for uDirectory in next(walk(uPlace))[1]:
                aDrives.append((uPlace + sep + uDirectory, uDirectory))
    return aDrives