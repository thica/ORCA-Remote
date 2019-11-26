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
from __future__ import annotations
from typing import Union

import os
import logging

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

__all__ = ["cFileName"]


class cFileName:
    def __init__(self,uFile: Union[str,cPath,cFileName] = u''):

        self.oPath: cPath  = cPath()
        self.uRaw: str
        if isinstance(uFile, str):
            self.uRaw       = uFile
        elif isinstance(uFile, cPath):
            self.oPath  = uFile
            self.uRaw   = u''
        elif isinstance(uFile, cFileName):
            self.oPath  = uFile.oPath
            self.uRaw = uFile.uRaw
        else:
            LogError(uMsg="cFileName, illegal constructor:"+str(type(uFile)))
        self.uFinal: str      = u''
        self.bDirty: bool     = True

        if Logger.level==logging.DEBUG:
            if self.uRaw:
                for uChar in u"/\\:":
                    if uChar in self.uRaw:
                        LogError(uMsg="do not pass full strings to a filename (use import):"+str(uFile), bTrackStack=True)

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
                for uChar in u"/\\:":
                    if uChar in self.uRaw:
                        LogError(uMsg="do not pass full strings to a filename (use import)", bTrackStack=True)

            return oRet
        else:
            LogError(uMsg="cFileName, illegal add:"+str(type(uFile)))

        return self

    def __radd__(self, oOther: str) ->str:
        if isinstance(oOther, str):
            return oOther+self.string
        else:
            return oOther

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
        return AdjustPathToUnix(self.string)

    @property
    def urlstring(self) ->str:
        return AdjustPathToUnix(self.string).replace(":/", "://")

    def _CreateFinal(self) ->None:
        self.bDirty = False
        if self.uRaw:
            self.uFinal = CleanUp(ReplaceVars(self.oPath.uRaw)+ ReplaceVars(self.uRaw))
        else:
            self.uFinal=u''

    def Clear(self) ->cFileName:
        self.oPath.uRaw = u''
        self.uRaw       = u''
        self.bDirty     = True
        return self

    def Exists(self) ->bool:
        """
        Checks, if a file exists
        :return: Returns True if the the given filename exists
        """
        return isfile(self.string)


    def Copy(self,oNewFile: Union[cFileName,cPath]) ->bool:
        """
        Copies a file

        :param cFileName/cPath oNewFile: Destination file name or destination path
        :return: True, if successful
        """

        try:
            if isinstance(oNewFile,cFileName):
                copyfile(self.string,oNewFile.string)
            else:
                oNewFileTmp=cFileName(oNewFile)+self.basename
                copyfile(self.string, oNewFileTmp.string)
            return True
        except Exception as e:
            LogError (uMsg=u'can\'t copy file [%s] to [%s]' % (self.string,oNewFile.string),oException=e)
            return False

    def ImportFullPath(self,uFnFullName: str) ->cFileName:
        if uFnFullName.startswith("$var("):
            if uFnFullName.endswith(")"):
                if not uSeparator in uFnFullName:
                    Logger.warning("Variable on FileName needs to replaced on import, is this what you want?:"+uFnFullName)
                    uFnFullName = ReplaceVars(uFnFullName)

        self.oPath.ImportFullPath(uFnFullName)
        self.uRaw=basename(uFnFullName)
        self.bDirty = True
        return self

    def Delete(self) ->bool:
        """
        Deletes a files
        :return: True, if successful
        """

        try:
            remove(self.string)
            return True
        except Exception as e:
            uMsg=u'can\'t delete File %s:%s' % (ToUnicode(e),self.string)
            Logger.warning (uMsg)
            return False

    def Rename(self,oNewFileName: cFileName) ->bool:
        """
        Renames a File

        :param cFileName oNewFileName: New file name
        :return: True, if successful
        """

        try:
            if self.Exists():
                if not oNewFileName.Exists():
                    rename(self.string,oNewFileName.string)
                    return True
            return False
        except Exception as e:
            LogError (uMsg=u'can\'t rename file [%s] to [%s]' % (self.string,oNewFileName.string),oException=e)
            return False

    def IsEmpty(self) ->bool:
        """
        Returns, if the FileName object is empty
        :return: True / False
        """
        return self.uRaw==u''

    def Size(self) ->int:
        """
        Returns the size of a files
        :return: File size of -1 on error
        """

        try:
            return os.path.getsize(self.string)
        except Exception as e:
            LogError (uMsg=u'can\'t get filesize [%s]' % self.string, oException=e)
            return -1



