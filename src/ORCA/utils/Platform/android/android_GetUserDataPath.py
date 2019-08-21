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

from kivy.logger             import Logger
# noinspection PyUnresolvedReferences
from jnius                   import autoclass
from ORCA.utils.Platform     import OS_GetUserDownloadsDataPath
from ORCA.utils.Path         import cPath
from ORCA.utils.FileName     import cFileName


import ORCA.Globals as Globals

def Android_GetDataDir():
    """
    tries to find an already installed Kivy User Data Installation
    and sets a default, if none has been found
    """

    Environment = autoclass('android.os.Environment')
    uRootPath = Environment.getRootDirectory().getPath()
    Logger.debug("Android Root Folder = "+uRootPath)

    uSubDir = u'OrcaRemote'

    # on android 6 and higher kivy runs on and error we we fetch the kivy user_data_dir (kivy 1.10.1)
    # replace with a working value

    uUserDataDir = OS_GetUserDownloadsDataPath()
    try:
        uUserDataDir = Globals.oApp.user_data_dir
    except:
        pass

    oPreferredUserDataPath = cPath(uUserDataDir)+uSubDir
    oPreferredUserDataPath.Create()

    # First try to Find existing Orca Data Dir
    aTestDirs=[oPreferredUserDataPath,cPath(OS_GetUserDownloadsDataPath())+uSubDir,cPath(uRootPath)+uSubDir,cPath("/data/data/org.orca.orca/files/app")]
    for oTestDir in aTestDirs:
        Logger.debug(u"Try to find Orca installations file at: " + oTestDir.string)
        if (cFileName(cPath(oTestDir)+'actions') + 'actions.xml').Exists():
            Logger.debug(u"Found Orca installations file at " + oTestDir.string)
            return oTestDir

    # First try to Find existing Orca Data Dir (fresh install)
    for oTestDir in aTestDirs:
        Logger.debug(u"Try to find Orca installations file (Fallback) at: " + oTestDir.string)
        if (cFileName(cPath(oTestDir)+'actions') + 'actionsfallback.xml').Exists():
            Logger.debug(u"Found Orca installations file (Fallback) at " + oTestDir.string)
            if oTestDir != oPreferredUserDataPath and oPreferredUserDataPath.IsWriteable():
                # lets copy the files outside of the Android App folder to make them accessable to users
                oTmpSrcDir = oTestDir +"actions"
                oTmpDstDir = oPreferredUserDataPath+"actions"
                oTmpSrcDir.Copy(oTmpDstDir)
                oTmpSrcDir = oTestDir +"languages"
                oTmpDstDir = oPreferredUserDataPath+"languages"
                oTmpSrcDir.Copy(oTmpDstDir)
                return oPreferredUserDataPath
            return oTestDir

    Logger.error(u"Haven't found Orca installations file")
    return cPath()

    # if we haven't found anything try to find the best writable location
    Logger.error(u"Haven't found Orca installations file")

    for oTestDir in aTestDirs:
        if oTestDir.IsWriteable():
            Logger.debug(u"Fallback: Trying Orca installations file at: " + oTestDir.string)
            return oTestDir

    #if we are here, we failed
    return cPath(OS_GetUserDownloadsDataPath()+uSubDir)

def GetUserDataPath():
    """ Gets the path to the user folder """
    # we alway keep the Orca Ini File on Android in SDcard Folder

    oPathRoot = Android_GetDataDir()
    return oPathRoot
