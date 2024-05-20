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

from kivy.logger             import Logger
# noinspection PyUnresolvedReferences
from jnius                   import autoclass
from ORCA.utils.Path         import cPath
from ORCA.utils.Platform     import OS_GetSystemTmpPath

def GetUserDownloadsDataPath() -> cPath:
    """ returns the path to the download folder """
    uRetPath:str = '/'
    oRetPath: cPath =  cPath(uRetPath)
    try:
        Environment = autoclass('android.os.Environment')
        uRetPath = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getPath()
        Logger.debug('Android Download Folder = ' +uRetPath)
        oRetPath = cPath(uRetPath)
        # we check if we have permissions to write here, and as a fallback we use the tmp path
        if not oRetPath.IsWriteable():
            Logger.error(f'GetUserDownloadsDataPath for Android No Write Permission for Download Folder: {str(oRetPath)}')
            oRetPath=OS_GetSystemTmpPath()
            if not oRetPath.IsWriteable():
                Logger.error(f'GetUserDownloadsDataPath for Android cant find writable folder: {str(oRetPath)}')
    except Exception as e:
        Logger.error('GetUserDownloadsDataPath for Android failed:'+str(e))

    if not oRetPath.IsDir() and not oRetPath.IsWriteable():
        Logger.error(f'Downloadpath not valid: {oRetPath}')

    return oRetPath
