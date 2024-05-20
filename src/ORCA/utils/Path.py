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

from __future__             import annotations
from typing                 import List
from typing                 import Union
from typing                 import Callable
import os
import logging

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

def CleanUp(*,uFinal:str) -> str:
    while '//' in uFinal:
        uFinal = uFinal.replace('//', '/')
    while '\\\\' in uFinal:
        uFinal = uFinal.replace('\\\\', '\\')

    return AdjustPathToOs(uPath=ReplaceVars(uFinal))

def AdjustPathToUnix(*,uPath:str) ->str:
    """
    Adjust a path to Unix specific syntax

    :param string uPath: Path to convert to Unix syntax
    :return: Adjusted Path
    """

    if uPath:
        return uPath.replace('\\','/')
    return uPath


class cPath:
    def __init__(self, vPath:Union[str,cPath]=''):
        """
        :param unicode|cPath vPath:
        """
        self.uRaw:str
        if isinstance(vPath, str):
            self.uRaw        = vPath
        elif isinstance(vPath, cPath):
            self.uRaw = vPath.uRaw
        self.uFinal:str      = ''
        self.bDirty:bool     = True

        if Logger.level==logging.DEBUG:
            if '.' in self.uRaw[-4:]:
                LogError(uMsg='do not pass full filenames to a path | '+self.uRaw, bTrackStack=True)

        self.Normalize()

    def __add__(self, uPath:str) -> cPath:
        oRet:cPath = copy(self)
        if isinstance(uPath, str):
            oRet.uRaw       += uPath
        elif isinstance(uPath, cPath):
            oRet.uRaw += uPath.uRaw
        oRet.Normalize()
        return oRet

    def __radd__(self, uOther:str) -> str:
        if isinstance(uOther, str):
            return uOther+str(self)
        else:
            LogError(uMsg=f'You can only add strings to a path: {str(uOther)}' ,bTrackStack=True)
            return uOther

    def Normalize(self):
        if self.uRaw:
            # self.uRaw+=uSeparator
            self.uRaw += '/'

    def ImportFullPath(self,*,uFnFullName:str) -> cPath:
        self.uRaw=os.path.dirname(uFnFullName)
        self.Normalize()
        return self

    @property
    def string(self) -> str:
        return CleanUp(uFinal=self.uRaw)

    @property
    def unixstring(self) -> str:
        return AdjustPathToUnix(uPath=CleanUp(uFinal=self.uRaw))


    def __str__(self) -> str:
        return CleanUp(uFinal=self.uRaw)

    def Create(self) -> bool:
        """
        Creates a folder

        :return: True, if successful
        """

        uPath:str = str(self)

        try:
            makedirs(uPath)
            Logger.debug('Created folder:' + uPath)
            if not self.Exists():
                Logger.error(f'Could not create folder: {uPath} unknown reason')
                return False
            return True
        except Exception as e:
            # noinspection PyUnresolvedReferences
            if not e.errno == 17:
                Logger.warning(f'Could not create folder: {uPath}  reason: {str(e)}')
            return False

    def GetFolderList(self,*,bFullPath:bool=False) -> List:
        """
        Returns a list of all folders in a path

        :param bool bFullPath: If True, the folder entries include the full folder struture, otherwise on the foldername is returned
        :return: A list of all folder in a folder
        """

        oDirList:List = []
        uRootDir:str = ''
        uItem:str
        try:

            # stdout_encoding = sys.getfilesystemencoding()
            # print 'stdout_encoding:', stdout_encoding
            uRootDir = CleanUp(uFinal=str(self))
            for uItem in listdir(uRootDir):
                if isdir(join(uRootDir, uItem)):
                    if not bFullPath:
                        oDirList.append(uItem)
                    else:
                        oDirList.append(AdjustPathToOs(uPath=uRootDir + '/' + uItem))
        except Exception as e:
            Logger.warning('can\'t get Dirlist ' + ToUnicode(e) + ' ' + uRootDir)
        return oDirList

    def GetFileList(self,*,bSubDirs:bool=False, bFullPath:bool=False) -> List:
        """
        Returns a dict of all files in a folder

        :param bool bSubDirs: If true, includes files in folders
        :param bool bFullPath: If True, the file entries include the full folder struture, otherwise on the filename is returned
        :return: A list of all files
        """

        oDirList:List = []
        uRootDir:str  = str(self)
        uItem:str
        try:
            for uItem in listdir(uRootDir):
                if not isdir(join(uRootDir, uItem)):
                    if not bFullPath:
                        oDirList.append(uItem)
                    else:
                        oDirList.append(AdjustPathToOs(uPath=uRootDir + '/' + uItem))
                else:
                    if bSubDirs:
                        oDirList.extend((cPath(uRootDir) + uItem).GetFileList(bSubDirs= bSubDirs,bFullPath=bFullPath))
        except Exception as e:
            Logger.debug('can\'t get File list:' + ToUnicode(str(e)) + ' :' + uRootDir)

        return oDirList

    def Exists(self) -> bool:
        """
        Checks if a Path / Directory exists
        Not complete clean, but sufficient for purpose

        :return: Returns True if the the given path name exists
        """
        return exists(str(self))

    def Delete(self, bSilent:bool=False) -> bool:
        """
        Deletes a folder (Needs to be inside the Orca folder structure)
        :param bool bSilent: If set, no warning is displayed
        :return: True, if successful
        """

        uPath:str = str(self)

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
            if not bSilent:
                Logger.warning (msg=f'can\'t remove folder [{uPath}]: {ToUnicode(e)}  ')
            return False

    def Copy(self,*,oDest:cPath, fIgnoreFiles:Union[Callable,None]=None) -> bool:
        """
        Copys a folder

        :param oDest: target folder name
        :param fIgnoreFiles: Function to check, if files should be copied
        :return: True, if successful
        """

        from ORCA.utils.FileName import cFileName
        aFiles:List
        aIgnored:set
        aFolders:List
        oFolder:cPath

        try:

            aFiles = self.GetFileList(bSubDirs=False,bFullPath=False)
            if fIgnoreFiles is not None:
                aIgnored = fIgnoreFiles(str(self), aFiles)
            else:
                aIgnored = set()

            if str(self) in aIgnored:
                return True

            aFolders = self.GetFolderList(bFullPath=False)

            oDest.Create()
            for uFolder in aFolders:
                oFolder=cPath(oDest)+uFolder
                (self+uFolder).Copy(oDest=oFolder)

            for uFile in aFiles:
                if not uFile in aIgnored:
                    (cFileName(self)+uFile).Copy(oNewFile=cFileName(oDest)+uFile)

            return True
        except Exception as e:
            LogError (uMsg=f'can\'t copy folder [{self}] to [{oDest}]', oException=e)
            return False

    def GetBaseFolder(self) -> str:
        """
        Returns the name of the last/base folder

        :return: the base folder name (eg: GetBaseFolder('c:/foo/bar') returns bar)
        """

        uTmp:str = str(self)
        uRet:str
        if "/" in uTmp:
            uRet = uTmp[uTmp.rfind('/',0,-1)+1:]
        else:
            uRet = uTmp[uTmp.rfind('\\',0,-1)+1:]
        return uRet


    def GetParentFolder(self,*, bFullPath:bool=True) -> str:
        """
        Returns the parent folder name,

        :param bool bFullPath: True/False to return the full path or just the folder name
        :return: the base folder name (eg: GetParentFolder('c:/foo/bar',True) returns c:/foo)
        """

        uTmp:str            = str(self)
        uBaseFolder:str     = self.GetBaseFolder()
        uParentFolder:str   = uTmp[0:-len(uBaseFolder)-1]

        if bFullPath:
            return uParentFolder
        else:
            return cPath(uParentFolder).GetBaseFolder()

    @classmethod
    def CheckIsDir(cls,*,uCheckName:str) -> bool:
        """
        Checks, if a reference is a folder

        :param uCheckName: reference to check, if Folder
        :return: Returns True if the the given path name exists
        """

        try:
            return isdir(uCheckName)
        except Exception:
            return False


    def IsDir(self) -> bool:
        """
        Checks, if a reference is a folder

        :rtype: bool
        :return: Returns True if the the given path name exists
        """

        try:
            return isdir(str(self))
        except Exception:
            return False

    def Clear(self) -> bool:
        """
        Clear() just removes the files within a folder
        It is not deleting the folder itself, and is not handling sub folders

        :return: True, if successful
        """
        aFiles:List[str]
        uFile:str
        try:
            aFiles=self.GetFileList(bSubDirs=False, bFullPath=True)
            for uFile in aFiles:
                remove(uFile)
            return True
        except Exception:
            return False

    def IsWriteable(self) -> bool:
        """
        Checks, if we have write access to a folder

        :return: True, if the directory has write access
        """
        uTestFile:str = 'orcatestfile'
        oTestDir:cPath = cPath(str(self)) +'orcatestdir'

        try:
            oTestDir.Delete(bSilent=True)
            if oTestDir.Create():
                if oTestDir.Exists():
                    uTestFile = str(oTestDir)+uSeparator+uTestFile
                    oFile=open(uTestFile,'w+')
                    oFile.write("ORCA")
                    oFile.close()
                    oFile=open(uTestFile,'r+')
                    oFile.read(1)
                    oFile.close()
                    if oTestDir.Delete():
                        return True
            return False
        except Exception as e:
            return False

    def Rename(self,*,oNewPath:cPath) -> bool:
        """
        Renames a folder

        :param cPath oNewPath: New Folder name
        :return: True, if successful
        """

        try:
            if self.Exists():
                if oNewPath.Exists():
                    rename(str(self),str(oNewPath))
                    return True
            return False
        except Exception as e:
            LogError (uMsg=f'can\'t rename folder [{self}] to [{oNewPath}]', oException=e)
            return False

    def IsEmpty(self) -> bool:
        """
        Returns, if the Path object is empty
        """
        return self.uRaw==''
