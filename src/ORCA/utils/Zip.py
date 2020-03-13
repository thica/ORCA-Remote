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

from typing import Union
from typing import List

from fnmatch                import fnmatch
from os                     import walk
from os.path                import basename
from os.path                import join
from os.path                import split
from zipfile                import ZIP_DEFLATED
from zipfile                import ZipFile
from zipfile                import is_zipfile

from kivy.logger            import Logger

from ORCA.utils.FileName    import cFileName
from ORCA.utils.LogError    import LogError
from ORCA.utils.Path        import cPath
from ORCA.utils.TypeConvert import ToUnicode

__all__ = ['cZipFile','cZipPath']

class cZipFile(cFileName):
    def IsZipFile(self)-> bool:
        """
        Checks if a file is a zipfile
        :return: True  is file is a zipfile
        """

        try:
            return is_zipfile(self.string)
        except Exception as e:
            LogError(uMsg=u'IsZipFile: Error for:'+self.string, oException=e)
            return False

    def ZipFile(self, oZipDest:cFileName, uRemovePath:str='') -> bool:
        """
        Zips a single file to a zip file

        :param cFileName oZipDest: Destination zip file
        :param string uRemovePath: Removes a specific folder part from the the zip file
        :return: True is succesfull
        """

        try:
            oZipFile:ZipFile = ZipFile(oZipDest.string, 'w', ZIP_DEFLATED)
            if uRemovePath == '':
                oZipFile.write(self.string)
            else:
                uArc:str = self.string[len(uRemovePath):]
                oZipFile.write(self.string, uArc)
            oZipFile.close()
            return True
        except Exception as e:
            Logger.critical(u'Zip: Fatal Error Zipping File:' + ToUnicode(e))
            return False

    def Unzip(self, oPath:cPath) -> bool:
        """
        Unzips a zip file  to a path
        If the output location does not yet exist, it creates it

        :param cPath oPath:
        :return: True if successful
        """

        oZip:Union[ZipFile,None]=None
        uEach:str
        uRoot:str
        uName:str
        oFn:cFileName
        # oFn:cPath

        try:

            Logger.debug(u'Extracting file [%s] to path [%s]' % (self.string, oPath.string))

            oZip = ZipFile(self.string, 'r')
            if not oPath.IsDir():
                oPath.Create()
            for uEach in oZip.namelist():
                # each=ToUnicode(each)

                Logger.debug(u'Extracting ' + ToUnicode(basename(uEach)) + ' ...')
                # Check to see if the item was written to the zip file with an
                # archive name that includes a parent directory. If it does, create
                # the parent folder in the output workspace and then write the file,
                # otherwise, just write the file to the workspace.
                #
                if not uEach.endswith('/'):
                    uRoot, uName = split(uEach)
                    oFolder = cPath(oPath) + uRoot
                    if not oFolder.IsDir():
                        oFolder.Create()
                    oFn = cFileName(oFolder) + uName
                    uFn = oFn.string
                    Logger.debug(u'... Writing to ' + uFn)
                    oFile = open(uFn, 'wb')
                    oFile.write(oZip.read(uEach))
                    oFile.close()
            oZip.close()
            return True
        except Exception as e:
            LogError(uMsg=u'Unzip: Fatal Error unzipping file',oException=e)
            try:
                oZip.close()
            except Exception:
                pass
            return False


class cZipPath(cPath):
    # noinspection PyDefaultArgument
    def ZipFolder(self, oFnZipDest:cFileName, uRemovePath:str=u'', aSkipFiles:List[str]=[])-> bool:
        """
        Zips a folder to a zip file

        :param cFileName oFnZipDest: Destination zip file
        :param string uRemovePath: Removes a specific folder part from the the zip files
        :param list aSkipFiles: List of files to exclude from the zip files
        :return: True is succesfull
        """

        uRoot:str
        aDirs:List[str]
        aFiles:List[str]

        try:
            Logger.debug(u'Zipping path [%s] to file [%s] , removing path [%s]' % (self.string, oFnZipDest.string, uRemovePath))
            oZipFile:ZipFile = ZipFile(oFnZipDest.string, 'w')
            for uRoot, uDirs, uFiles in walk(self.string):
                for uFile in uFiles:
                    uFile      = join(uRoot, uFile)
                    uFile2:str = ''
                    if uRemovePath != '':
                        uFile2 = uFile[len(uRemovePath) + 1:]

                    bSkip:bool = False
                    if (uFile in aSkipFiles) or (uFile2 in aSkipFiles):
                        bSkip = True
                    for uSkipFile in aSkipFiles:
                        if uSkipFile.endswith("*"):
                            uSkipFile = uSkipFile[:-1]
                            if uFile.startswith(uSkipFile):
                                bSkip = True
                                break
                        if uSkipFile.startswith("*"):
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
                                oZipFile.write(uFile)
                        else:
                            uArc:str = uFile[len(uRemovePath):]
                            oZipFile.write(uFile, uArc)
                    else:
                        Logger.debug(u'Skip Zipping File [%s]' % uFile)

            oZipFile.close()
            return True
        except Exception as e:
            uMsg = u'Zip: Fatal Error Zipping Directory:' + ToUnicode(e)
            Logger.critical(uMsg)
            return False
