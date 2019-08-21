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

"""
Base Module for Scripts and Interfaces
"""

from kivy.logger                             import Logger
from ORCA.utils.LogError                     import LogError
from ORCA.utils.TypeConvert                  import ToIntVersion
from ORCA.utils.TypeConvert                  import ToUnicode
from ORCA.utils.FileName                     import cFileName
from ORCA.RepManagerEntry                    import cRepManagerEntry
from ORCA.vars.Replace                       import ReplaceVars

import ORCA.Globals as Globals

__all__ = ['cBaseObject']

class cBaseObject(object):
    def __init__(self):
        self.aSettings                  = {}
        self.bIsInit                    = False
        self.iLastRet                   = 0
        self.iMyVersion                 = ToIntVersion('1.0.0')
        self.iOrcaVersion               = ToIntVersion('1.0.0')     #OrcaVersion defines for what Orca Version the Interface has been developed
        self.oFnObject                  = None
        self.oObjectConfig              = None
        self.oPathMyData                = None
        self.oPathMyCode                = None
        self.uConfigName                = "DEFAULT"
        self.uIniFileLocation           = "local"
        self.uObjectName                = u''
        self.uObjectType                = ""

    def Init(self,uObjectName,oFnObject=None):
        """ Initializes the script """

        self.bIsInit            = True
        self.uObjectName        = uObjectName

        if self.uObjectType == "script":
            self.oPathMyCode = Globals.oScripts.dScriptPathList[self.uObjectName]
            # oFnObjectPy = cFileName(self.oPathMyCode) + u'script.py'
            if self.uIniFileLocation == "global":
                self.oPathMyData = Globals.oPathGlobalSettingsScripts + self.uObjectName
            elif self.uIniFileLocation == "local":
                self.oPathMyData = Globals.oDefinitionPathes.oPathDefinitionScriptSettings +self.uObjectName
        else:
            self.oPathMyCode = Globals.oPathInterface + self.uObjectName
            # oFnObjectPy = cFileName(self.oPathMyCode) + u'interface.py'
            if self.uIniFileLocation == "global":
                self.oPathMyData = Globals.oPathGlobalSettingsInterfaces + self.uObjectName
            elif self.uIniFileLocation == "local":
                self.oPathMyData = Globals.oDefinitionPathes.oPathDefinitionInterfaceSettings +self.uObjectName

        if self.oPathMyData is not None:
            if not self.oPathMyData.Exists():
                self.oPathMyData.Create()

        self.oFnObject            = cFileName(oFnObject)

        Globals.oLanguage.LoadXmlFile(self.uObjectType.upper(), self.uObjectName)
        oRepManagerEntry=cRepManagerEntry(oFnObject)
        if oRepManagerEntry.ParseFromSourceFile():
            self.iMyVersion     = oRepManagerEntry.oRepEntry.iVersion
            self.iOrcaVersion   = oRepManagerEntry.oRepEntry.iMinOrcaVersion
        Globals.oNotifications.RegisterNotification("on_stopapp",self.DeInit,self.uObjectType.capitalize()+":"+self.uObjectName)
        Globals.oNotifications.RegisterNotification("on_pause",self.OnPause,self.uObjectType.capitalize()+":"+self.uObjectName)
        Globals.oNotifications.RegisterNotification("on_resume",self.OnResume,self.uObjectType.capitalize()+":"+self.uObjectName)

        self.ShowDebug(u'Init')

    def DeInit(self, **kwargs):
        """ Deinitialisizes the object """
        self.ShowDebug(u'DeInit')

    def OnPause(self,**kwargs):
        """ called by system, if the device goes on pause """
        self.ShowInfo(u'OnPause')
    def OnResume(self,**kwargs):
        """ called by system, if the device resumes """
        self.ShowInfo(u'OnResume')

    def _FormatShowMessage(self,uMsg,uParConfigName=""):
        """
        Creates a debug line for the object

        :rtype: string
        :param string uMsg: The message to show
        :param string uParConfigName:  The name of the configuration
        :return: The formatted debug string
        """
        uConfigName = u''
        if uParConfigName:
            uConfigName = u'/' + uParConfigName

        return "%s %s %s: %s" % (self.uObjectType.capitalize(),self.uObjectName , uConfigName , uMsg)

    def ShowWarning(self,uMsg,uParConfigName=""):
        """
        writes a warning message

        :rtype: string
        :param string uMsg: The warning message
        :param string uParConfigName: The configuration name
        :return: The written logfile entry
        """
        uRet = self._FormatShowMessage(uMsg,uParConfigName)
        Logger.warning (uRet)
        return uRet

    def ShowDebug(self,uMsg,uParConfigName=""):
        """
        writes a debug message

        :rtype: string
        :param string uMsg: The debug message
        :param string uParConfigName: The configuration name
        :return: The written logfile entry
        """
        uRet = self._FormatShowMessage(uMsg,uParConfigName)
        Logger.debug (uRet)
        return uRet

    def ShowInfo(self,uMsg,uParConfigName=""):
        """
        writes a info message

        :rtype: string
        :param string uMsg: The info message
        :param string uParConfigName: The configuration name
        :return: The written logfile entry
        """

        uRet = self._FormatShowMessage(uMsg,uParConfigName)
        Logger.info (uRet)
        return uRet

    def ShowError(self,uMsg, uParConfigName="",oException=None):
        """
        writes an error message

        :rtype: string
        :param string uMsg: The error message
        :param string uParConfigName: The configuration name
        :param exception oException: Optional, an exception to show
        :return: The written logfile entry
        """

        # uRet = self._FormatShowMessage(uMsg,uParConfigName)
        # Logger.debug (uRet)
        # return uRet
        uRet = self._FormatShowMessage(uMsg,uParConfigName)
        iErrNo = 0
        if oException is not None:
            if hasattr(oException,'errno'):
                iErrNo = oException.errno
        if iErrNo is  None:
            iErrNo = 12345
        if iErrNo!=0:
            uRet = uRet + u" "+ToUnicode(iErrNo)
        uRet=LogError (uRet,oException)
        return uRet

    def GetConfigJSON(self):
        """
        Abstract function, needs to be overriden by object class

        :rtype: dict
        :return: Dummy funtion, returns empty dict
        """
        return {}

    def GetNewSettingObject(self):
        """ Dummy """
        pass


    def GetSettingObjectForConfigName(self,uConfigName):
        """
        Creates/returns a config object

        :rtype: cSetting
        :param string uConfigName: The Name of the configuration
        :return: a Setting object
        """

        oSetting=self.aSettings.get(uConfigName)

        if oSetting is None:
            uConfigName=ReplaceVars(uConfigName)
            oSetting = self.aSettings.get(uConfigName)

        if oSetting is None:
            oSetting=self.GetNewSettingObject()
            self.aSettings[uConfigName]=oSetting
            oSetting.ReadConfigFromIniFile(uConfigName)
        return oSetting
