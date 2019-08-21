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
import os
from kivy.logger             import Logger
from ORCA.utils.Platform     import OS_GetUserDownloadsDataPath
from ORCA.utils.Path         import cPath
from ORCA.utils.FileName     import cFileName


import ORCA.Globals as Globals

def Linux_GetDataDir():
    """
    tries to find an already installed data folder
    and sets a default, if none has been found
    """

    uRootPath = u"/"
    Logger.debug("Linux Root Folder = "+uRootPath)

    uSubDir = u'OrcaRemote'

    uUserDataDir = OS_GetUserDownloadsDataPath()
    try:
        uUserDataDir = Globals.oApp.user_data_dir
    except:
        pass

    # First try to Find existing Orca Data Dir
    aTestDirs=[cPath(uUserDataDir)+uSubDir,cPath(OS_GetUserDownloadsDataPath())+uSubDir,cPath(uRootPath)+uSubDir,cPath(os.getcwd())]
    for oTestDir in aTestDirs:
        Logger.debug(u"Try to find Orca installations file at: " + oTestDir.string)
        if (cFileName(cPath(oTestDir)+'actions') + 'actions.xml').Exists():
            Logger.debug(u"Found Orca installations file at " + oTestDir.string)
            return oTestDir


    # First try to Find existing Orca Data Dir
    for oTestDir in aTestDirs:
        Logger.debug(u"Try to find Orca installations file (Fallback) at: " + oTestDir.string)
        if (cFileName(cPath(oTestDir)+'actions') + 'actionsfallback.xml').Exists():
            Logger.debug(u"Found Orca installations file (Fallback) at " + oTestDir.string)
            return oTestDir

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

    oPathRoot = Linux_GetDataDir()
    return oPathRoot
