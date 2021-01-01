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
from typing import Union
from typing import BinaryIO
import ftplib

from kivy.logger            import Logger

from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.LogError    import LogError
from ORCA.utils.FileName    import cFileName
from ORCA.utils.Path        import cPath


__all__ = ['cFTP']

class cFTP:
    """ This for uploading files per FTP to an FTP server, NOT for downloading """

    PATH_CACHE: List = []

    def __init__(self, bEncrypt:bool = False):
        super().__init__()
        self.oFTP:Union[ftplib.FTP,None] = None
        self.bEncrypt:bool               = bEncrypt

    def DirExists(self,*, oPath: cPath) ->bool:
        """
        checks, if a remote ftp path exists

        :param cPath oPath: The remote path, to check
        :return: True/False
        """
        bExists:bool = False
        uPath:str    = oPath.unixstring

        if uPath not in self.PATH_CACHE:
            try:
                self.oFTP.cwd(uPath)
                bExists = True
                self.PATH_CACHE.append(uPath)
            except ftplib.error_perm as e:
                if str(e.args).count('550'):
                    bExists = False
        else:
            bExists = True
        return bExists

    def CreateDir(self,*, oPath:cPath, uSep:str=u'/') ->bool:
        """
        creates a remote ftp path
        :param cPath oPath: The Remote Path to create
        :param string uSep: The Separator to slit the pathes into it's sub pathes
        :return: True/False
        """

        uPath:str             = oPath.unixstring
        aSplitPath:List[str]  = uPath.split(uSep)
        uNewDir:str           = u''

        for uServerDir in aSplitPath:
            if uServerDir:
                uNewDir += uSep + uServerDir
                if not self.DirExists(oPath=cPath(uNewDir)):
                    try:
                        Logger.debug('Attempting to create directory (%s) ...' % uNewDir)
                        self.oFTP.mkd(uNewDir)
                    except Exception as e:
                        LogError(uMsg='can\'t create directory (%s) ...' % uNewDir,oException=e)
                        return False
        return True

    def ChangeDir(self,*,oPath:cPath)->bool:
        """
        Changes to a remote ftp directory

        :param cPath oPath: the remote path to create
        :return: True/False
        """
        try:
            self.oFTP.cwd(oPath.unixstring)
            return True
        except Exception as e:
            LogError(uMsg='can\'t change directory (%s) ...' % oPath.unixstring,oException=e)
        return False

    def Connect(self, *,uServer:str) ->bool:
        """ connects to an ftp server """
        if not self.bEncrypt: # Use standard FTP
            self.oFTP = ftplib.FTP()
        else: # Use sftp
            self.oFTP = ftplib.FTP_TLS()
        try:
            self.oFTP.connect(uServer)
            if self.bEncrypt:
                self.oFTP.prot_p()
            return True
        except Exception as e:
             ShowErrorPopUp(uMessage=LogError(uMsg='FTP: Could not connect to (%s)' % uServer, oException=e))
        return False
    def DisConnect(self) ->bool:
        try:
            self.oFTP.quit()
        except Exception as e:
            LogError(uMsg='FTP: Could not disconnect', oException=e)
            return False
        return True
    def Login(self,*,uUsername:str, uPassword:str) ->bool:
        """ logs to an ftp server """
        try:
            self.oFTP.login(uUsername,uPassword)
            Logger.debug('Logged in as (%s)' % uUsername)
            return True
        except ftplib.error_perm as e:
            uMsg=LogError(uMsg='FTP: can\'t login, check Username/Password',oException=e)
        except Exception as e:
            uMsg=LogError(uMsg='FTP: can\'t login, general failure',oException=e)
        ShowErrorPopUp(uMessage=uMsg)
        return False

    def _UploadFile(self,*,oFile:cFileName,oRemoteSubPath:cPath) ->bool:
        """
        uploads a file to an ftp server

        :param cFileName oFile:
        :param cPath oRemoteSubPath:
        :return:
        """
        oFileHandle:BinaryIO = open(oFile.string,'rb')
        uFileName:str        = oFile.basename

        uDisplayFilename:str = uFileName

        Logger.debug('Sending (%s) via FTP to %s' % (uDisplayFilename,oRemoteSubPath.unixstring))
        uSendCmd:str = 'STOR %s' % uFileName
        try:
            self.oFTP.storbinary(uSendCmd, oFileHandle)
            Logger.debug('FTP: Upload done!')
            oFileHandle.close()
            return True
        except Exception as e:
            LogError(uMsg='FTP: can\'t upload file (%s), general failure' % uFileName,oException=e)
            oFileHandle.close()
        return False


    def UploadLocalFile(self,*,oFile:cFileName, oBaseLocalDir:cPath, oBaseRemoteDir:cPath) ->bool:
        """
        Subfunction to upload a local file including sub pathes to a remote folder

        :param cFileName oFile: FileName to Upload
        :param cPath oBaseLocalDir: Local Path
        :param cPath oBaseRemoteDir: Remote FTP Path
        :return:
        """
        try:
            bRet:bool             = False
            uPath:str             = oFile.oPath.string
            oRemoteSubPath:cPath  = cPath(uPath.replace(oBaseLocalDir.string, ''))
            oRemotePath:cPath     = cPath(uPath.replace(oBaseLocalDir.string, oBaseRemoteDir.string))

            if not self.DirExists(oPath=oRemotePath):
                self.CreateDir(oPath=oRemotePath)

            if self.ChangeDir(oPath=oRemotePath):
                if oFile.Exists():
                    bRet = self._UploadFile(oFile=oFile,oRemoteSubPath=oRemoteSubPath)
                else:
                    Logger.warning ("File no longer exists, (%s)!" % oFile.string)

            return bRet

        except Exception as e:
            LogError(uMsg='Fatal FTP error',oException=e)
            return False

    def _DownloadFile(self,*,oFnLocalFile:cFileName,oPathRemote:cPath) ->bool:
        """
        downloads a file from a ftp server

        :param cFileName oFnLocalFile: Local filename to download to, basename will be taken as the ftp filename
        :param cPath oPathRemote: The remote FTP Path
        :return:
        """
        uFileName:str        = oFnLocalFile.basename
        uDisplayFilename:str = uFileName

        Logger.debug('Download (%s) via FTP from %s' % (uDisplayFilename,oPathRemote.unixstring))
        uGetCmd:str = 'RETR %s' % uFileName
        try:
            if self.ChangeDir(oPath=oPathRemote):
                oStream:BinaryIO = open(str(oFnLocalFile), 'wb')
                self.oFTP.retrbinary(uGetCmd, oStream.write)
                oStream.close()
                Logger.debug('FTP: Download done!')
            return True
        except Exception as e:
            LogError(uMsg='FTP: can\'t Download file (%s), general failure' % uFileName,oException=e)
        return False


    def DownloadRemoteFile(self,*,oFnFile:cFileName, oPathLocal:cPath, oPathRemote:cPath) ->bool:
        """
        Subfunction to download a remote file to a local folder

        :param cFileName oFnFile: FileName to Download
        :param cPath oPathLocal: Local Path
        :param cPath oPathRemote: Remote FTP Path
        :return:
        """
        try:
            bRet:bool
            uFnFile:str           = oFnFile.basename
            oFnLocal:cFileName    = cFileName(oPathLocal) + uFnFile

            if not oPathLocal.Exists():
                oPathLocal.Create()

            bRet = self._DownloadFile(oFnLocalFile=oFnLocal,oPathRemote=oPathRemote)

            return bRet

        except Exception as e:
            LogError(uMsg='Fatal FTP error',oException=e)
            return False
