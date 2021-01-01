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

"""
Base Module for Scripts and Interfaces
"""

from typing import Dict
from typing import List
from typing import Union
from typing import Any
from typing import Optional

from kivy.logger                             import Logger
from ORCA.utils.LogError                     import LogError
from ORCA.utils.TypeConvert                  import ToIntVersion
from ORCA.utils.TypeConvert                  import ToUnicode
from ORCA.utils.TypeConvert                  import ToInt
from ORCA.utils.FileName                     import cFileName
from ORCA.utils.Path                         import cPath
from ORCA.vars.Access                        import SetVar

from ORCA.download.RepManagerEntry import cRepManagerEntry
from ORCA.vars.Replace                       import ReplaceVars

import ORCA.Globals as Globals

__all__ = ['cBaseObject','cBaseObjects']

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.BaseSettings import cBaseSettings
    from ORCA.BaseConfig   import cBaseConfig
else:
    from typing import TypeVar
    cBaseSettings = TypeVar("cBaseSettings")
    cBaseConfig   = TypeVar("cBaseConfig")

class cBaseObject:
    """
    Base Class for Interfaces AND Scripts
    Mainly to provide common functionality for settings, logging , pause / resume
    """

    def __init__(self):
        self.dSettings:Dict[str,cBaseSettings]  = {}
        self.bIsInit:bool                       = False
        self.iMyVersion:int                     = ToIntVersion('1.0.0')
        self.iOrcaVersion:int                   = ToIntVersion('1.0.0')     #OrcaVersion defines for what Orca Version the Interface has been developed
        self.oFnObject:Optional[cFileName]      = None
        self.oObjectConfig:cBaseConfig          = None
        self.oPathMyData:Optional[cPath]        = None
        self.oPathMyCode:Optional[cPath]        = None
        self.uConfigName:str                    = u'DEFAULT'
        self.uIniFileLocation:str               = u'local'
        self.uObjectName:str                    = u''
        self.uObjectType:str                    = u''

    def Init(self,uObjectName:str,oFnObject:Optional[cFileName]=None) -> None:
        """ Initializes the object """

        self.bIsInit            = True
        self.uObjectName        = uObjectName

        if self.uObjectType == "script":
            self.oPathMyCode = Globals.oScripts.dScriptPathList[self.uObjectName]
            if self.uIniFileLocation == "global":
                self.oPathMyData = Globals.oPathGlobalSettingsScripts + self.uObjectName
            elif self.uIniFileLocation == "local":
                self.oPathMyData = Globals.oDefinitionPathes.oPathDefinitionScriptSettings +self.uObjectName
        else:
            self.oPathMyCode = Globals.oPathInterface + self.uObjectName
            if self.uIniFileLocation == "global":
                self.oPathMyData = Globals.oPathGlobalSettingsInterfaces + self.uObjectName
            elif self.uIniFileLocation == "local":
                self.oPathMyData = Globals.oDefinitionPathes.oPathDefinitionInterfaceSettings +self.uObjectName

        if self.oPathMyData is not None:
            if not self.oPathMyData.Exists():
                self.oPathMyData.Create()

        self.oFnObject            = cFileName(oFnObject)

        Globals.oLanguage.LoadXmlFile(self.uObjectType.upper(), self.uObjectName)
        oRepManagerEntry:cRepManagerEntry = cRepManagerEntry(oFileName=oFnObject)
        if oRepManagerEntry.ParseFromSourceFile():
            self.iMyVersion     = oRepManagerEntry.oRepEntry.iVersion
            self.iOrcaVersion   = oRepManagerEntry.oRepEntry.iMinOrcaVersion
        Globals.oNotifications.RegisterNotification(uNotification="on_stopapp",fNotifyFunction=self.DeInit,  uDescription=self.uObjectType.capitalize()+":"+self.uObjectName)
        Globals.oNotifications.RegisterNotification(uNotification="on_pause",  fNotifyFunction=self.OnPause, uDescription=self.uObjectType.capitalize()+":"+self.uObjectName)
        Globals.oNotifications.RegisterNotification(uNotification="on_resume", fNotifyFunction=self.OnResume,uDescription=self.uObjectType.capitalize()+":"+self.uObjectName)
        self.ShowDebug(uMsg=u'Init')

    def DeInit(self, **kwargs) -> None:
        """ De-Initializes the object """
        self.ShowDebug(uMsg=u'DeInit')

    def OnPause(self,**kwargs) -> None:
        """ called by system, if the device goes on pause """
        self.ShowInfo(uMsg=u'OnPause')
    def OnResume(self,**kwargs) -> None:
        """ called by system, if the device resumes """
        self.ShowInfo(uMsg=u'OnResume')

    def _FormatShowMessage(self,*,uMsg:str,uParConfigName:str=u"",uParAdd:str=u"") -> str:
        """
        Creates a debug line for the object

        :param str uMsg: The message to show
        :param str uParConfigName:  The name of the configuration
        :return: The formatted debug string
        """
        uConfigName:str = u''
        if uParConfigName:
            uConfigName = u'/' + uParConfigName
        if uParAdd!="":
            uConfigName = uConfigName+u'/' + uConfigName

        return "%s %s %s: %s" % (self.uObjectType.capitalize(),self.uObjectName , uConfigName , uMsg)

    def ShowWarning(self,*,uMsg:str,uParConfigName:str=u"") -> str:
        """
        Writes a warning message

        :param str uMsg: The warning message
        :param str uParConfigName: The configuration name
        :return: The written logfile entry
        """
        uRet:str = self._FormatShowMessage(uMsg=uMsg,uParConfigName=uParConfigName)
        Logger.warning (uRet)
        return uRet

    def ShowDebug(self,*,uMsg:str,uParConfigName:str=u"") -> str:
        """
        writes a debug message

        :rtype: str
        :param str uMsg: The debug message
        :param str uParConfigName: The configuration name
        :return: The written logfile entry
        """
        uRet:str = self._FormatShowMessage(uMsg=uMsg,uParConfigName=uParConfigName)
        Logger.debug (uRet)
        return uRet

    def ShowInfo(self,*,uMsg:str,uParConfigName:str=U"") -> str:
        """
        writes a info message

        :param str uMsg: The info message
        :param str uParConfigName: The configuration name
        :return: The written logfile entry
        """

        uRet:str = self._FormatShowMessage(uMsg=uMsg,uParConfigName=uParConfigName)
        Logger.info (uRet)
        return uRet

    def ShowError(self,*,uMsg:str, uParConfigName:str=u"",uParAdd:str=u"",oException:Exception=None) -> str:
        """
        writes an error message

        :param str uMsg: The error message
        :param str uParConfigName: The configuration name
        :param str uParAdd: The additional text
        :param exception oException: Optional, an exception to show
        :return: The written logfile entry
        """

        uRet:str = self._FormatShowMessage(uMsg=uMsg,uParConfigName=uParConfigName,uParAdd=uParAdd)
        iErrNo:int = 0
        if oException is not None:
            if hasattr(oException,'errno'):
                iErrNo = ToInt(oException.errno)
        if iErrNo is  None:
            iErrNo = 12345
        if iErrNo!=0:
            uRet = uRet + u" "+ToUnicode(iErrNo)
        uRet=LogError(uMsg=uRet,oException=oException)
        return uRet

    def GetConfigJSON(self) -> Dict:
        """
        Abstract function, needs to be overridden by object class

        :rtype: dict
        :return: Dummy function, returns empty dict
        """
        return {}

    def GetNewSettingObject(self) -> Union[cBaseSettings,None]:
        """ Dummy """
        return None


    def GetSettingObjectForConfigName(self,*,uConfigName:str) -> cBaseSettings:
        """
        Creates/returns a config object

        :param string uConfigName: The Name of the configuration
        :return: a Setting object
        """

        oSetting: cBaseSettings
        oSetting = self.dSettings.get(uConfigName)

        if oSetting is None:
            uConfigName = ReplaceVars(uConfigName)
            oSetting = self.dSettings.get(uConfigName)

        if oSetting is None:
            oSetting = self.GetNewSettingObject()
            self.dSettings[uConfigName]=oSetting
            oSetting.ReadConfigFromIniFile(uConfigName=uConfigName)
        return oSetting

    def CreateCodesetListJSONString(self) -> str:
        """ Dummy """
        pass

class cBaseObjects:
    """ A base class for interface and script container classes """
    def __init__(self,*,uType:str,uPrefix:str):
        self.aObjectNameList:List[str]                              = []        # list of all names of all scripts
        self.dObjects:Dict[str,cBaseObject]                         = {}
        self.aObjectNameList:List[str]                              = []        # list of all names of all objects (scripts/interfaces)
        self.uType:str                                              = uType     # For future extension, so that the base class knows it parent type
        self.uPrefix:str                                            = uPrefix   # Prefix for the var name of the list of all configs / sections
        self.dModules:Dict[str,Any]                                 = {}        # dict of all python modules for all objects (scripts/interfaces)

    def RegisterObjects(self,*,dObjects:Dict[str,cBaseObject]) -> None:
        """
        Registers the objects
        :param dObjects: The objects list as dict
        :return: None
        """
        self.dObjects=dObjects

    def CreateJsonSectionList(self,*,aObjectList:List[str]) -> str:
        """
        Creates a list of all sections of all given objects in a json format. Sets the var as well
        :param aObjectList: The list of objects, (list of names)
        :return:
        """

        oObject:cBaseObject
        uRetJson:str = u'['
        uObjectName:str
        for uObjectName in aObjectList:
            oObject=self.dObjects[uObjectName]
            if len(oObject.oObjectConfig.aSections)==0:
                oObject.oObjectConfig.GetSectionList()
            uRetJson+="["+oObject.oObjectConfig.CreateSectionsJSONString()+"],"
        if uRetJson.endswith(","):
            uRetJson=uRetJson[:-1]+"]"
        else:
            uRetJson=uRetJson+"]"
        SetVar(uVarName=self.uPrefix+"_"+u'SETTINGSECTIONLIST', oVarValue=uRetJson)
        return uRetJson

    def OnPause(self) -> None:
        """ Entry for on Pause """
        for oObject in self.dObjects.values():
            oObject.OnPause()

    def OnResume(self) -> None:
        """ Entry for on resume """
        for oObject in self.dObjects.values():
            oObject.OnResume()

    def DeInit(self) -> None:
        """ deinits the  object """
        for oObject in self.dObjects.values():
            oObject.DeInit()

    def Init(self) -> None:
        """ dummy """
        pass

    def Clear(self) -> None:
        """ clears the list of Objects """
        self.DeInit()
        del self.aObjectNameList[:]
        self.dObjects.clear()
