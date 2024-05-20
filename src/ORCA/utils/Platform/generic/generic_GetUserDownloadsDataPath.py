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

from os.path                 import sep, expanduser
from kivy.logger             import Logger
from ORCA.utils.Platform     import OS_ToPath
from ORCA.utils.Path         import cPath


def GetUserDownloadsDataPath() -> cPath:
    """ returns the path to the download folder """
    oRetPath = cPath(OS_ToPath(expanduser('~') + sep + 'Downloads'))
    Logger.debug(f'Download Folder  = {oRetPath}')

    if oRetPath.Exists():
        return oRetPath

    Logger.error(f'Downloadpath not valid: {oRetPath}')
    return cPath('')


#todo: enable as soon we can use the new toolchain
'''
from plyer                   import storagepath
from kivy.logger             import Logger
from ORCA.utils.Path         import cPath

def GetUserDownloadsDataPath():
    """ returns the path to the download folder """
    uRetPath=u"/"
    try:
        uRetPath = storagepath.get_downloads_dir
        Logger.debug('Android Download Folder = '+uRetPath)
    except Exception as e:
        Logger.error('GetUserDownloadsDataPath for Android failed:'+str(e))
    oRetPath = cPath(uRetPath)

    if not oRetPath.IsDir():
        Logger.error(f'Android Download path not valid: {oRetPath}')

    return oRetPath
'''
