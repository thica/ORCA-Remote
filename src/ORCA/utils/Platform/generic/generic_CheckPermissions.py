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

# from ORCA.utils.Platform import OS_GetUserDataPath
from ORCA.utils.Platform import OS_GetUserDownloadsDataPath
import ORCA.Globals as Globals


def CheckPermissions() -> bool:
    """ We assume to have all permissions, as long we do not have OS specific code"""

    if Globals.oPathUserDownload is not None:
        return Globals.oPathUserDownload.IsWriteable()
    else:
        return OS_GetUserDownloadsDataPath().IsWriteable()
