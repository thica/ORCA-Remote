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

from typing                 import List
from typing                 import Optional

from fnmatch                import fnmatch
from os                     import walk
from os.path                import join

import  tarfile
from kivy.logger            import Logger

from ORCA.utils.FileName    import cFileName
from ORCA.utils.LogError    import LogError
from ORCA.utils.Path        import cPath
from ORCA.utils.TypeConvert import ToUnicode

__all__ = ['cTarFile','cTarPath']

def GetWriteMode(*,oFnTarDest:cFileName, uDefaultMode:str='') -> str:
    uMode:str
    if oFnTarDest.Exists():
        uMode = 'w'
    else:
        uMode = 'x'

    if uDefaultMode:
        uMode+=':'+uDefaultMode
    else:
        uMode+=':'+oFnTarDest.Extension()[1:]

    return uMode

class cTarFile(cFileName):
    def IsTarFile(self)-> bool:
        """
        Checks if a file is a tarfile
        :return: True  is file is a tarfile
        """

        try:
            return tarfile.is_tarfile(str(self))
        except Exception as e:
            LogError(uMsg=f'IstarFile: Error for: {self}', oException=e)
            return False

    def TarFile(self,*, oTarDest:cFileName, uRemovePath:str='', uCompressionMode:str = '') -> bool:
        """
        tars a single file to a tar file

        :param oTarDest: Destination tar file
        :param uRemovePath: Removes a specific folder part from the the tar file
        :param uCompressionMode: Sets Compression Mode: If not given, it will be taken from the file extension
        :return: True is successful
        """

        uMode:str
        try:
            uMode = GetWriteMode(oFnTarDest=oTarDest,uDefaultMode=uCompressionMode)
            oTarFile:tarfile.TarFile = tarfile.open(name=str(oTarDest), mode=uMode)
            if uRemovePath == '':
                oTarFile.add(name=str(self))
            else:
                uArc:str = str(self)[len(uRemovePath):]
                oTarFile.add(name=str(self), arcname=uArc)
            oTarFile.close()
            return True
        except Exception as e:
            Logger.critical('Tar: Fatal Error Taring File:' + ToUnicode(e))
            return False

    def UnTar(self, oPath:cPath) -> bool:
        """
        Untar a tar file  to a path
        If the output location does not yet exist, it creates it

        :param cPath oPath:
        :return: True if successful
        """

        oTarFile:tarfile.TarFile

        try:

            Logger.debug(f'Extracting file [{self}] to path [{oPath}]')
            oTarFile = tarfile.open(str(self), 'r')
            oTarFile.extractall(path=str(oPath))
            oTarFile.close()
            return True
        except Exception as e:
            LogError(uMsg='Untar: Fatal Error untaring file',oException=e)
            try:
                # noinspection PyUnboundLocalVariable
                oTarFile.close()
            except Exception:
                pass
            return False


class cTarPath(cPath):
    def TarFolder(self, oFnTarDest:cFileName, uRemovePath:str='', aSkipFiles:Optional[List[str]]=None, uCompressionMode:str = '')-> bool:
        """
        Tars a folder to a tar file

        :param oFnTarDest: Destination tar file
        :param uRemovePath: Removes a specific folder part from the tar files
        :param aSkipFiles: List of files to exclude from the tar files
        :param uCompressionMode: Sets Compression Mode: If not given, it will be taken from the file extension
        :return: True is successful
        """

        uRoot:str
        aDirs:List[str]
        aFiles:List[str]
        uMode:str

        if aSkipFiles is None:
            aSkipFiles = []

        try:
            Logger.debug(f'Taring path [{self}] to file [{oFnTarDest}] , removing path [{uRemovePath}]')
            uMode = GetWriteMode(oFnTarDest=oFnTarDest,uDefaultMode=uCompressionMode)
            oTarFile:tarfile.TarFile = tarfile.open(name=str(oFnTarDest), mode=uMode)
            for uRoot, uDirs, uFiles in walk(str(self)):
                for uFile in uFiles:
                    uFile      = join(uRoot, uFile)
                    uFile2:str = ''
                    if uRemovePath != '':
                        uFile2 = uFile[len(uRemovePath) + 1:]

                    bSkip:bool = False
                    if (uFile in aSkipFiles) or (uFile2 in aSkipFiles):
                        bSkip = True
                    for uSkipFile in aSkipFiles:
                        if uSkipFile.endswith('*'):
                            uSkipFile = uSkipFile[:-1]
                            if uFile.startswith(uSkipFile):
                                bSkip = True
                                break
                        if uSkipFile.startswith('*'):
                            if uFile.endswith(uSkipFile[1:]):
                                bSkip = True
                                break
                        if not bSkip:
                            if fnmatch(uFile, uSkipFile):
                                bSkip = True
                                break

                    if not bSkip:
                        if uRemovePath == '':
                            if not uFile in aSkipFiles:
                                oTarFile.add(name=uFile)
                        else:
                            uArc:str = uFile[len(uRemovePath):]
                            oTarFile.add(name=uFile, arcname=uArc)
                    else:
                        Logger.debug(f'Skip Taring File [{uFile}]')

            oTarFile.close()
            return True
        except Exception as e:
            uMsg = 'Tar: Fatal Error taring Directory:' + ToUnicode(e)
            Logger.critical(uMsg)
            return False

'''
def Extract_LZMA2Tar(*,oFnSource:cFileName,oPathDst:cPath) -> cFileName:
    """Extract an lzma file to the given path"""

    byData:bytes
    oFnDestTar:cFileName
    # open lzma file
    with open(str(oFnSource),"rb") as oArSource:
        byData = lzma.decompress(oArSource.read())
    # write tar file
    oFnDestTar = cFileName().ImportFullPath(uFnFullName=str(oPathDst)+"/"+oFnSource.basename[:-3])

    with open(str(oFnDestTar), "wb") as oArDest:
        oArDest.write(byData)
    return oFnDestTar

'''