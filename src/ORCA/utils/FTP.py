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

import ftplib

from kivy.logger            import Logger

from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.LogError    import LogError
from ORCA.utils.FileName    import cFileName
from ORCA.utils.Path        import cPath


__all__ = ['cFTP']

class cFTP(object):
    """ This for uploading files per FTP to an FTP server, NOT for downloading """

    PATH_CACHE = []

    def __init__(self, bEncrypt = False):
        super(cFTP, self).__init__()
        self.oFTP           = None
        self.bEncrypt       = bEncrypt

    def DirExists(self, oPath):
        """
        checks, if a remote ftp path exists

        :param cPath oPath: The remote path, to check
        :return: True/False
        """
        bExists = False
        uPath = oPath.unixstring
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

    def CreateDir(self, oPath, uSep=u'/'):
        """
        creates a remote ftp path
        :param cPath oPath: The Remote Path to create
        :param string uSep: The Separator to slit the pathes into it's sub pathes
        :return: True/False
        """

        uPath = oPath.unixstring
        uSplitPath = uPath.split(uSep)
        uNewDir = u''
        for uServerDir in uSplitPath:
            if uServerDir:
                uNewDir += uSep + uServerDir
                if not self.DirExists(cPath(uNewDir)):
                    try:
                        Logger.debug('Attempting to create directory (%s) ...' % (uNewDir))
                        self.oFTP.mkd(uNewDir)
                    except Exception as e:
                        LogError('can\'t create directory (%s) ...' % (uNewDir),e)
                        return False
        return True

    def ChangeDir(self,oPath):
        """
        Changes to a remote ftp directory

        :param cPath oPath: the remote path to create
        :return: True/False
        """
        try:
            self.oFTP.cwd(oPath.unixstring)
            return True
        except Exception as e:
            LogError('can\'t change directory (%s) ...' % (oPath.unixstring),e)
        return False

    def Connect(self, uServer):
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
            uMsg=LogError('FTP: Could not connect to (%s)' % (uServer), e)
            ShowErrorPopUp(uMessage=uMsg)
        return False
    def DisConnect(self):
        try:
            self.oFTP.quit()
        except Exception as e:
            LogError('FTP: Could not disconnect', e)
        return True
    def Login(self,uUsername,uPassword):
        """ logs to an ftp server """
        uMsg=''
        try:
            self.oFTP.login(uUsername,uPassword)
            Logger.debug('Logged in as (%s)' % (uUsername))
            return True
        except ftplib.error_perm as e:
            uMsg=LogError('FTP: can\'t login, check Username/Password',e)
        except Exception as e:
            uMsg=LogError('FTP: can\'t login, general failure',e)
        ShowErrorPopUp(uMessage=uMsg)
        return False

    def _UploadFile(self,oFile,oRemoteSubPath):
        """
        uploads a file to an ftp server

        :param cFileName oFile:
        :param cPath oRemoteSubPath:
        :return:
        """
        oFileHandle = open(oFile.string,'rb')
        uFileName = oFile.basename

        uDisplayFilename = uFileName

        Logger.debug('Sending (%s) via FTP to %s' % (uDisplayFilename,oRemoteSubPath.unixstring))
        uSendCmd = 'STOR %s' % (uFileName)
        try:
            self.oFTP.storbinary(uSendCmd, oFileHandle)
            Logger.debug('FTP: Upload done!')
            oFileHandle.close()
            return True
        except Exception as e:
            LogError('FTP: can\'t upload file (%s), general failure' % (uFileName),e)
            oFileHandle.close()
        return False


    def UploadLocalFile(self,oFile, oBaseLocalDir, oBaseRemoteDir):
        """
        Subfunction to upload a local file including sub pathes to to remote folder

        :param cFileName oFile: FileName to Upload
        :param cPath oBaseLocalDir: Local Path
        :param cPath oBaseRemoteDir: Remote FTP Path
        :return:
        """
        try:
            bRet             = False
            uPath            = oFile.oPath.string
            oRemoteSubPath   = cPath(uPath.replace(oBaseLocalDir.string, ''))
            oRemotePath      = cPath(uPath.replace(oBaseLocalDir.string, oBaseRemoteDir.string))

            if not self.DirExists(oRemotePath):
                self.CreateDir(oRemotePath)

            if self.ChangeDir(oRemotePath):
                if oFile.Exists():
                    bRet = self._UploadFile(oFile,oRemoteSubPath)
                else:
                    Logger.warning ("File no longer exists, (%s)!" % oFile.string)

            return bRet

        except Exception as e:
            bOnError=True
            LogError('Fatal FTP error' ,e)
        return bOnError
