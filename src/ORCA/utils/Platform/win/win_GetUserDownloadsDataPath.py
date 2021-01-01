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

from kivy.logger                            import Logger
from ORCA.utils.Path                        import cPath
from ORCA.utils.Platform.win.win_GetPlaces  import GetDownloadFolder

def GetUserDownloadsDataPath() -> cPath:
    """ returns the path to the download folder """

    oPath:cPath=GetDownloadFolder()
    Logger.debug("Windows Download Folder  = "+oPath.string)

    if not oPath.IsDir():
        Logger.error("Downloadpath not valid:" + oPath.string)
    return oPath

