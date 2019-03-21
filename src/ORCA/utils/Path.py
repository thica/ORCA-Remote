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
import logging

from kivy.compat            import string_types
from kivy.logger            import Logger

from os                     import listdir
from os                     import remove
from os                     import makedirs
from os                     import rename
from os.path                import isdir
from os.path                import join
from os.path                import exists
from shutil                 import rmtree
from copy import copy
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.Filesystem  import AdjustPathToOs
from ORCA.utils.LogError    import LogError
from ORCA.vars.Replace      import ReplaceVars

uSeparator = os.sep

__all__ = ["CleanUp", "cPath","AdjustPathToUnix"]

def CleanUp(uFinal):
    while "//" in uFinal:
        uFinal = uFinal.replace("//", "/")
    while "\\\\" in uFinal:
        uFinal = uFinal.replace("\\\\", "\\")
    return AdjustPathToOs(ReplaceVars(uFinal))

def AdjustPathToUnix(uPath):
    """
    Adjust a path to Unix specific syntax

    :rtype: string
    :param string uPath: Path to convert to Unix syntax
    :return: Adjusted Path
    """

    if uPath:
        return uPath.replace(u'\\',u'/')
    return uPath


class cPath(object):
    def __init__(self, uPath=u''):

        '''
        if Logger.level == logging.DEBUG:
            import inspect
            frame = inspect.currentframe()
            try:
                aStack = inspect.stack()
                for aLine in aStack:
                    if not aLine[1].endswith("Path.py"):
                        aCodeLine = aLine[-2]
                        uCodeLine = aCodeLine[0]
                        uVarName=uCodeLine.split("=")[0].strip()
                        tVarName=uVarName.split(".")
                        if len(tVarName)==2:
                            uVarName=tVarName[-1]
                            if not uVarName.startswith("oPath"):
                                if not "[" in uVarName:
                                    print (uVarName)
                        break
            finally:
                del frame
        '''

        if isinstance(uPath, string_types):
            self.uRaw       = uPath
        elif isinstance(uPath, cPath):
            self.uRaw = uPath.uRaw
        self.uFinal     = u''
        self.bDirty     = True

        if Logger.level==logging.DEBUG:
            if "." in self.uRaw[-4:]:
                LogError(uMsg="do not pass full filenames to a path:"+self.uRaw, bTrackStack=True)

        self.Normalize()

    def __add__(self, uPath):
        oRet = copy(self)
        if isinstance(uPath, string_types):
            oRet.uRaw       += uPath
        elif isinstance(uPath, cPath):
            oRet.uRaw += uPath.uRaw
        oRet.Normalize()
        return oRet

    def __radd__(self, oOther):
        if isinstance(oOther, string_types):
            return oOther+self.string
        else:
            LogError(uMsg="You can only add strings to a path:" + oOther.string,bTrackStack=True)
            return oOther

    def Normalize(self):
        if self.uRaw:
            self.uRaw+=uSeparator

    def ImportFullPath(self,uFnFullName):
        self.uRaw=os.path.dirname(uFnFullName)
        self.Normalize()
        return self

    @property
    def string(self):
        return CleanUp(self.uRaw)

    @property
    def unixstring(self):
        return AdjustPathToUnix(CleanUp(self.uRaw))


    def __str__(self):
        return CleanUp(self.uRaw)

    def Create(self):
        """
        Creates a folder

        :rtype: bool
        :return: True, if successful
        """

        uPath = self.string

        try:
            makedirs(uPath)
            Logger.debug('Created folder:' + uPath)
            if not self.Exists():
                Logger.error('Could not create folder: %s unknown reason' % uPath)
                return False
            return True
        except Exception as e:
            if not e.errno == 17:
                Logger.warning('Could not create folder: %s  reason: %s' % (uPath, e.strerror))
            return False

    def GetFolderList(self,bFullPath=False):
        """
        Returns a list of all folders in a path

        :rtype: list
        :param bool bFullPath: If True, the folder entries include the full folder struture, otherwise on the foldername is returned
        :return: A list of all folder in a folder
        """

        oDirList = []
        try:

            # stdout_encoding = sys.getfilesystemencoding()
            # print 'stdout_encoding:', stdout_encoding
            uRootDir = CleanUp(self.string)
            for oItem in listdir(uRootDir):
                if isdir(join(uRootDir, oItem)):
                    if not bFullPath:
                        oDirList.append(oItem)
                    else:
                        oDirList.append(AdjustPathToOs(uRootDir + '/' + oItem))
        except Exception as e:
            uMsg = u'can\'t get Dirlist ' + ToUnicode(e) + " " + uRootDir
            Logger.warning(uMsg)
        return oDirList

    def GetFileList(self,bSubDirs=False, bFullPath=False):
        """
        Returns a dict of all files in a folder

        :rtype: list
        :param bool bSubDirs: If true, includes files in folders
        :param bool bFullPath: If True, the file entries include the full folder struture, otherwise on the filename is returned
        :return: A list of all files
        """

        oDirList = []
        try:
            uRootDir = self.string
            for oItem in listdir(uRootDir):
                if not isdir(join(uRootDir, oItem)):
                    if not bFullPath:
                        oDirList.append(oItem)
                    else:
                        oDirList.append(AdjustPathToOs(uRootDir + '/' + oItem))
                else:
                    if bSubDirs:
                        oDirList.extend((cPath(uRootDir) + oItem).GetFileList( bSubDirs, bFullPath))
        except Exception as e:
            uMsg = u'can\'t get File list:' + ToUnicode(e) + " :" + uRootDir
            Logger.warning(uMsg)

        return oDirList

    def Exists(self):
        """
        Checks if a Path / Directory exists
        Not complete clean, but sufficient for purpose

        :rtype: bool
        :return: Returns True if the the given path name exists
        """
        return exists(self.string)

    def Delete(self):
        """
        Deletes a folder (Needs to be inside the Orca folder structure)

        :rtype: bool
        :return: True, if successful
        """

        uPath=self.string

        if uPath=='':
            return False
        if uPath=='/':
            return False
        if uPath=='\\':
            return False
        if uPath.startswith('.'):
            return False

        try:
            rmtree(uPath,False)
            return True
        except Exception as e:
            uMsg=u'can\'t remove folder [%s]: %s  ' % (uPath,ToUnicode(e))
            Logger.warning (uMsg)
            return False

    def Copy(self, oDest, fIgnoreFiles=None):
        """
        Copys a folder

        :rtype: bool
        :param cPath oDest: target folder name
        :param function fIgnoreFiles: Function to check, if files should be copied
        :return: True, if successful
        """

        from ORCA.utils.FileName import cFileName

        try:

            aFiles   = self.GetFileList(bSubDirs=False,bFullPath=False)
            if fIgnoreFiles is not None:
                aIgnored = fIgnoreFiles(self.string, aFiles)
            else:
                aIgnored = set()

            if self.string in aIgnored:
                return True

            aFolders = self.GetFolderList(bFullPath=False)

            oDest.Create()
            for uFolder in aFolders:
                oFolder=cPath(oDest)+uFolder
                (self+uFolder).Copy(oFolder)

            for uFile in aFiles:
                if not uFile in aIgnored:
                    (cFileName(self)+uFile).Copy(cFileName(oDest)+uFile)

            return True
        except Exception as e:
            LogError (u'can\'t copy folder [%s] to [%s]' % (self.string,oDest.string),e)
            return False

    @classmethod
    def CheckIsDir(cls,uCheckName):
        """
        Checks, if a reference is a folder

        :param str uCheckName: reference to check, if Folder
        :rtype: bool
        :return: Returns True if the the given path name exists
        """

        try:
            return isdir(uCheckName)
        except Exception:
            return False


    def IsDir(self):
        """
        Checks, if a reference is a folder

        :rtype: bool
        :return: Returns True if the the given path name exists
        """

        try:
            return isdir(self.string)
        except Exception:
            return False

    def Clear(self):
        """
        Clear just removes the files within a folder
        It is not deleting the folder itself, and is not handling subfolders

        :rtype: bool
        :return: True, if successful
        """
        try:
            aFiles=self.GetFileList(bSubDirs=False, bFullPath=True)
            for uFile in aFiles:
                remove(uFile)
            return True
        except Exception:
            return False

    def IsWritable(self):
        """
        Checks, if we have write access to a folder

        :rtype: bool
        :return: True, if the a directory has write access
        """
        oTestDir = cPath(self.string) +'orcatestdir'
        if oTestDir.Create():
            if oTestDir.Delete():
                return True
            return False
        else:
            return False

    def Rename(self,oNewPath):
        """
        Renames a folder

        :rtype: bool
        :param cPath oNewPath: New Folder name
        :return: True, if successful
        """

        try:
            if self.Exists():
                if oNewPath.Exists():
                    rename(self.string,oNewPath.string)
                    return True
            return False
        except Exception as e:
            uMsg=u'can\'t rename folder [%s] to [%s]: %s  ' % (self.string,oNewPath.string,ToUnicode(e))
            LogError (u'can\'t rename folder [%s] to [%s]' % (self.string,oNewPath.string),e)
            return False

    def IsEmpty(self):
        """
        Returns, if the Path object is empty
        :return:
        """
        return self.uRaw==u''
