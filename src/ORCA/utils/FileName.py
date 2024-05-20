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
from __future__ import annotations
from typing import Union

import os
import logging
import codecs

from os                     import remove
from os                     import rename
from shutil                 import copyfile

from copy import copy
from kivy.logger            import Logger
from ORCA.utils.LogError    import LogError
from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.Path        import cPath
from ORCA.utils.Path        import CleanUp
from ORCA.utils.TypeConvert import ToUnicode
from os.path                import basename
from os.path                import isfile
from ORCA.utils.Path        import AdjustPathToUnix

uSeparator = os.sep

__all__ = ['cFileName']


class cFileName:
    def __init__(self,uFile: Union[str,cPath,cFileName] = ''):

        self.oPath: cPath  = cPath()
        self.uRaw: str = ''
        if isinstance(uFile, str):
            self.uRaw = uFile
            if uFile:
                for uChar in '/\\:':
                    if uChar in self.uRaw:
                        self.ImportFullPath(uFnFullName=uFile)
                        break

        elif isinstance(uFile, cPath):
            self.oPath  = uFile
            self.uRaw   = ''
        elif isinstance(uFile, cFileName):
            self.oPath  = uFile.oPath
            self.uRaw = uFile.uRaw
        else:
            LogError(uMsg=f'cFileName, illegal constructor: {type(uFile)}')
        self.uFinal: str      = ''
        self.bDirty: bool     = True

    def __str__(self) ->str:
        if not self.bDirty:
            return self.uFinal
        else:
            self._CreateFinal()
            return self.uFinal

    def __add__(self, uFile: str) ->cFileName:
        if isinstance(uFile, str):
            oRet: cFileName = copy(self)
            oRet.uRaw    += uFile
            oRet.bDirty  = True

            if Logger.level ==logging.DEBUG:
                for uChar in '/\\:':
                    if uChar in self.uRaw:
                        LogError(uMsg='do not pass full strings to a filename (use import)', bTrackStack=True)

            return oRet
        else:
            LogError(uMsg=f'cFileName, illegal add: {str(type(uFile))}')

        return self

    def __radd__(self, uOther: str) ->str:
        if isinstance(uOther, str):
            return uOther+str(self)
        else:
            return uOther

    @property
    def basename(self) ->str:
        return self.uRaw

    @property
    def string(self) ->str:
        if not self.bDirty:
            return self.uFinal
        else:
            self._CreateFinal()
            return self.uFinal

    @property
    def unixstring(self) ->str:
        return AdjustPathToUnix(uPath=str(self))

    @property
    def urlstring(self) ->str:
        return AdjustPathToUnix(uPath=str(self)).replace(':/', '://')

    def _CreateFinal(self) ->None:
        self.bDirty = False
        if self.uRaw:
            self.uFinal = CleanUp(uFinal=ReplaceVars(self.oPath.uRaw)+ ReplaceVars(self.uRaw))
        else:
            self.uFinal=''

    def Clear(self) ->cFileName:
        self.oPath.uRaw = ''
        self.uRaw       = ''
        self.bDirty     = True
        return self

    def Exists(self) ->bool:
        """
        Checks, if a file exists
        :return: Returns True if the the given filename exists
        """
        return isfile(str(self))


    def Copy(self,*,oNewFile: Union[cFileName,cPath]) ->bool:
        """
        Copies a file

        :param cFileName/cPath oNewFile: Destination file name or destination path
        :return: True, if successful
        """

        try:
            if isinstance(oNewFile,cFileName):
                copyfile(str(self),str(oNewFile))
            else:
                oNewFileTmp=cFileName(oNewFile)+self.basename
                copyfile(str(self), str(oNewFileTmp))
            return True
        except Exception as e:
            LogError (uMsg=f'can\'t copy file [{self}] to [{oNewFile}]', oException=e)
            return False

    def ImportFullPath(self,*,uFnFullName: str) ->cFileName:
        if uFnFullName.startswith('$var('):
            if uFnFullName.endswith(')'):
                if not uSeparator in uFnFullName:
                    Logger.warning(f'Variable on FileName needs to replaced on import, is this what you want?: {uFnFullName}')
                    uFnFullName = ReplaceVars(uFnFullName)

        self.oPath.ImportFullPath(uFnFullName=uFnFullName)
        self.uRaw=basename(uFnFullName)
        self.bDirty = True
        return self

    def Delete(self) ->bool:
        """
        Deletes a files
        :return: True, if successful
        """

        try:
            remove(str(self))
            return True
        except Exception as e:
            if self.Exists():
                uMsg= f'can\'t delete file {ToUnicode(e)}:{self}'
                Logger.warning (uMsg)
            return False

    def Rename(self,*,oNewFileName: cFileName) ->bool:
        """
        Renames a File

        :param cFileName oNewFileName: New file name
        :return: True, if successful
        """

        try:
            if self.Exists():
                if not oNewFileName.Exists():
                    rename(str(self),str(oNewFileName))
                    return True
            return False
        except Exception as e:
            LogError (uMsg=f'can\'t rename file [{self}] to [{oNewFileName}]', oException=e)
            return False

    def IsEmpty(self) ->bool:
        """
        Returns, if the FileName object is empty
        :return: True / False
        """
        return self.uRaw==''

    def Size(self) ->int:
        """
        Returns the size of a file
        :return: File size of -1 on error
        """

        try:
            return os.path.getsize(str(self))
        except Exception as e:
            LogError (uMsg=f'can\'t get filesize [{self}]', oException=e)
            return -1


    def Extension(self) -> str:
        """
        Returns the extension of a file (with dot)
        :return: extension as str
        """

        try:
            return os.path.splitext(str(self))[1]
        except Exception as e:
            LogError (uMsg=f'can\'t get file extension [{self}]', oException=e)
            return ""

    def Load(self):
        """ returns a content of file as string (unicode on Py3)
        :rtype: string
        :return: The File Content as string
        """

        try:
            f = None
            try:
                #should work for all xml files
                f= codecs.open(str(self), 'r', encoding='utf-8')
                read_data = f.read()
            except Exception:
                if f is not None:
                    f.close()
                # should work for common other files
                try:
                    f = codecs.open(str(self), 'r', encoding='latin1')
                    read_data = f.read()
                except Exception:
                    #fallback
                    if f is not None:
                        f.close()
                    f = codecs.open(str(self), 'r', encoding='utf-8', errors='ignore')
                    read_data = f.read()
            f.close()
            return read_data
        except Exception as e:
            uMsg= f'can\'t load file [{self}] : {e}  '
            Logger.error (uMsg)
            return ''
