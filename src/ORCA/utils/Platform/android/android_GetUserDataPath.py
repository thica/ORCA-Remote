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
from typing import List

from kivy.logger             import Logger
# noinspection PyUnresolvedReferences
# from jnius                   import autoclass
from ORCA.utils.Platform     import OS_GetUserDownloadsDataPath
from ORCA.utils.Platform     import OS_GetInstallationDataPath

from ORCA.utils.Path         import cPath
from ORCA.utils.FileName     import cFileName

import ORCA.Globals as Globals


# noinspection PyUnreachableCode
def Android_GetDataDir() -> cPath:
    """
    tries to find an already installed Kivy User Data Installation
    and sets a default, if none has been found
    """

    oPathInst:cPath = OS_GetInstallationDataPath()
    uSubDir:str = u'OrcaRemote'

    # on android 6 and higher kivy runs on and error we fetch the kivy user_data_dir (kivy 1.10.1)
    # replace with a working value

    uUserDataDir:str = OS_GetUserDownloadsDataPath()
    try:
        uUserDataDir = Globals.oApp.user_data_dir
    except:
        pass

    oPreferredUserDataPath:cPath = cPath(uUserDataDir)+uSubDir
    oPreferredUserDataPath.Create()

    # First try to Find existing Orca Data Dir
    aTestDirs:List[cPath]=[oPreferredUserDataPath,cPath(OS_GetUserDownloadsDataPath())+uSubDir,oPathInst]
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
                # lets copy the files outside of the Android App folder to make them accessible to users
                '''
                TODO: Currently it just copies it to the sub folder OrcaRemote inm the user app folder, which is not outside of the app, 
                as in Android 11 we will have further restrictions on placing Application data, this needs to be reworked
                Also needs to be reworked, that the appstartearly is always taken from the installation folder
                '''
                Logger.debug(u"Copy Orca installations file (Fallback) from %s to %s" %(oTestDir.string,oPreferredUserDataPath.string))
                oTmpSrcDir:cPath = oTestDir +"actions"
                oTmpDstDir:cPath = oPreferredUserDataPath+"actions"
                oTmpSrcDir.Copy(oDest=oTmpDstDir)
                oTmpSrcDir = oTestDir +"languages"
                oTmpDstDir = oPreferredUserDataPath+"languages"
                oTmpSrcDir.Copy(oDest=oTmpDstDir)
                return oPreferredUserDataPath
            return oTestDir

    Logger.error(u"Haven't found Orca installations file")

    Logger.error("Folder content so far")
    aContent:List[str]
    uName:str
    for oTestDir in aTestDirs:
        Logger.error("Folder:"+oTestDir.string)
        aContent=oTestDir.GetFolderList()
        for uName in aContent:
            Logger.error("Folder:"+uName)
        aContent=oTestDir.GetFileList()
        for uName in aContent:
            Logger.error("File:"+uName)


    return cPath()



def GetUserDataPath() -> cPath:
    """ Gets the path to the user folder """
    # we always keep the Orca Ini File on Android in SD-Card Folder
    return Android_GetDataDir()
