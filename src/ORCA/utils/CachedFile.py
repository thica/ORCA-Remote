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

from kivy.cache          import Cache

from ORCA.utils.FileName import cFileName
from ORCA.utils.LoadFile import LoadFile

__all__ = ['CachedFile','ClearCache']

uCacheName:str = 'CachedFiles'
Cache.register(category = uCacheName,  timeout=120)


def CachedFile(*,oFileName: cFileName) -> str:
    """
    Returns the content of a file as string, using a cache if already loaded
    """

    uFileContent: str = Cache.get(category = uCacheName, key = oFileName.string)
    if uFileContent is None:
        uFileContent = LoadFile(oFileName)
        Cache.append(category = uCacheName, key = oFileName.string, obj = uFileContent, timeout = 120)

    return uFileContent

def ClearCache() -> None:
    """ Clears the cache and frees memory """
    Cache.remove(category = uCacheName)
