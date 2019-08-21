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

from os                     import remove
from os                     import rename
from shutil                 import copyfile

from copy import copy
from kivy.compat            import string_types
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


class cFileName(object):
    def __init__(self,uFile = u''):

        self.oPath      = cPath()
        if isinstance(uFile, string_types):
            self.uRaw       = uFile
        elif isinstance(uFile, cPath):
            self.oPath  = uFile
            self.uRaw   = u''
        elif isinstance(uFile, cFileName):
            self.oPath  = uFile.oPath
            self.uRaw = uFile.uRaw
        else:
            LogError("cFileName, illegal constructor:"+str(type(uFile)))
        self.uFinal     = u''
        self.bDirty     = True

        if Logger.level==logging.DEBUG:
            if self.uRaw:
                for uChar in u"/\\:":
                    if uChar in self.uRaw:
                        LogError(uMsg="do not pass full strings to a filename (use import):"+uFile, bTrackStack=True)


    def __str__(self):
        if not self.bDirty:
            return self.uFinal
        else:
            self._CreateFinal()
            return self.uFinal

    def __add__(self, uFile):
        if isinstance(uFile, string_types):
            oRet         = copy(self)
            oRet.uRaw    += uFile
            oRet.bDirty  = True

            if Logger.level ==logging.DEBUG:
                for uChar in u"/\\:":
                    if uChar in self.uRaw:
                        LogError(uMsg="do not pass full strings to a filename (use import)", bTrackStack=True)


            return oRet
        else:
            LogError("cFileName, illegal add:"+type(uFile))

        return self

    def __radd__(self, oOther):
        if isinstance(oOther, string_types):
            return oOther+self.string
        else:
            return oOther

    @property
    def basename(self):
        return self.uRaw


    @property
    def string(self):
        if not self.bDirty:
            return self.uFinal
        else:
            self._CreateFinal()
            return self.uFinal

    @property
    def unixstring(self):
        return AdjustPathToUnix(self.string)

    @property
    def urlstring(self):
        return AdjustPathToUnix(self.string).replace(":/", "://")

    def _CreateFinal(self):
        self.bDirty = False
        if self.uRaw:
            self.uFinal = CleanUp(ReplaceVars(self.oPath.uRaw)+ ReplaceVars(self.uRaw))
        else:
            self.uFinal=u''

    def Clear(self):
        self.oPath.uRaw = u''
        self.uRaw       = u''
        self.bDirty     = True
        return self

    def Exists(self):
        """
        Checks, if a file exists

        :rtype: bool
        :return: Returns True if the the given filename exists
        """
        return isfile(self.string)


    def Copy(self,oNewFile):
        """
        Copies a file

        :rtype: bool
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
            LogError (u'can\'t copy file [%s] to [%s]' % (self.string,oNewFile.string),e)
            return False

    def ImportFullPath(self,uFnFullName):
        if uFnFullName.startswith("$var("):
            if uFnFullName.endswith(")"):
                if not uSeparator in uFnFullName:
                    Logger.warning("Variable on FileName needs to replaced on import, is this what you want?:"+uFnFullName)
                    uFnFullName = ReplaceVars(uFnFullName)

        self.oPath.ImportFullPath(uFnFullName)
        self.uRaw=basename(uFnFullName)
        self.bDirty = True
        return self

    def Delete(self):
        """
        Deletes a files

        :rtype: bool
        :return: True, if successful
        """

        try:
            remove(self.string)
            return True
        except Exception as e:
            uMsg=u'can\'t delete File %s:%s' % (ToUnicode(e),self.string)
            Logger.warning (uMsg)
            return False

    def Rename(self,oNewFileName):
        """
        Renames a File

        :rtype: bool
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
            LogError (u'can\'t rename file [%s] to [%s]' % (self.string,oNewFileName.string),e)
            return False

    def IsEmpty(self):
        """
        Returns, if the FileName object is empty
        :rtype: bool
        :return: True / False
        """
        return self.uRaw==u''

    def Size(self):
        """
        Returns the size of a files
        :rtype: int
        :return: File size of -1 on error
        """

        try:
            return os.path.getsize(self.string)
        except Exception as e:
            LogError (u'can\'t get filesize [%s]' % self.string, e)
            return -1



