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

import ORCA.Globals as Globals
from ORCA.utils.Path        import cPath
from ORCA.vars.Helpers      import GetEnvVar

def GetSystemTmpPath() -> cPath:
    """ Gets the path to the tmp folder """
    oPath:cPath

    oPath = cPath(GetEnvVar(u"TMPDIR"))
    if oPath.Exists():
        return oPath

    oPath = cPath(GetEnvVar(u"TMP"))
    if oPath.Exists():
        return oPath

    oPath = cPath(u"/var/tmp")
    if oPath.Exists():
        return oPath

    oPath = cPath(u"/var/tmp")
    if oPath.Exists():
        return oPath

    oPath = cPath(u"/tmp")
    if oPath.Exists():
        return oPath

    oPath = Globals.oPathUserDownload+"orcatmp"

    oPath.Create()
    return oPath

