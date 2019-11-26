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
from typing import Any
from typing import Dict

from ORCA.vars.QueryDict    import cMonitoredSettings
from kivy.logger import Logger
from ORCA.utils.ConfigHelpers               import Config_GetDefault_Str
from ORCA.utils.LogError                    import LogErrorSmall
from ORCA.utils.TypeConvert                 import ToInt, ToFloat, ToBool, ToUnicode
from ORCA.vars.Access                       import SetVar
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.utils.Path                        import cPath

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.BaseObject import cBaseObject
else:
    from typing import TypeVar
    cBaseObject = TypeVar("cBaseObject")


class cObjectMonitoredSettings(cMonitoredSettings):
    def WriteVar(self,uName:str,vValue:Any) -> None:
        self.oBaseSettings.SetContextVar("CONFIG_" + uName.upper()[1:], vValue)

class cBaseSettings:
    """ A base class for the script settings """
    def __init__(self, oObject:cBaseObject ):
        # some default settings, which should be there even if not configured by the Object
        # use the exact spelling as in the settings json

        self.oObject:cBaseObject                                = oObject
        self.uConfigName:str                                    = "DEFAULT"
        self.uContext:str                                       = u''
        self.uSection:str                                       = u''
        self.aIniSettings:cObjectMonitoredSettings              = cObjectMonitoredSettings(self)
        self.aIniSettings.bInitCompleted                        = False
        self.bOnError:bool                                      = False
        self.uType:str                                          = u''


    def SetContextVar(self,uVarName:str,uVarValue:str) -> None:
        """ Sets a var within the interface context

        :param str uVarName: The name of the var
        :param str uVarValue: The value if the var
        """
        SetVar(uVarName = uVarName, oVarValue = ToUnicode(uVarValue), uContext = self.oObject.uObjectName+u'/'+self.uConfigName)

    def ReadConfigFromIniFile(self,uConfigName:str) -> None:
        """
        Reads the object config file

        :param string uConfigName: The configuration name to read
        :return: None
        """

        if self.aIniSettings.bInitCompleted:
            return
        self.aIniSettings.bInitCompleted = True

        if uConfigName != u'':
            self.uConfigName = uConfigName
            self.uContext=self.oObject.uObjectName+u'/'+self.uConfigName
            self.SetContextVar(uVarName="context",uVarValue=self.uContext)

        self.uSection = self.uConfigName

        try:
            self.oObject.oObjectConfig.LoadConfig()

            if self.oObject.uObjectType == "interface":
                SetVar(uVarName = u'InterfaceCodesetList',   oVarValue = self.oObject.CreateCodsetListJSONString())
            SetVar(uVarName = u'ObjectConfigSection', oVarValue = uConfigName)
            dIniDef:Dict[str,Dict] = self.oObject.oObjectConfig.CreateSettingJsonCombined(oSetting=self)

            for uKey2 in dIniDef:
                dLine:Dict   = dIniDef[uKey2]
                uType:str    = dLine.get("type")
                uKey:str     = dLine.get("key")
                uDefault:str = dLine.get("default")

                if uKey is None or uDefault is None:
                    continue

                # we replace JSON defaults by interface-settings defaults, if exists
                if self.aIniSettings.queryget(uKey) is not None:
                    uDefault = self.aIniSettings.queryget(uKey)

                uResult:str     = Config_GetDefault_Str(self.oObject.oObjectConfig.oConfigParser,self.uSection, uKey,uDefault)

                if uType == "scrolloptions" or uType == "string":
                    self.aIniSettings[uKey]=ReplaceVars(uResult)
                elif uType == "numeric" or uType == "numericslider":
                    self.aIniSettings[uKey]=ToInt(uResult)
                elif uType == "numericfloat" :
                    self.aIniSettings[uKey]=ToFloat(uResult)
                elif uType == "bool":
                    self.aIniSettings[uKey]=ToBool(uResult)
                elif uType == "varstring":
                    self.aIniSettings[uKey] = ReplaceVars(uResult)
                elif uType=="path":
                    if isinstance(uResult,str):
                        self.aIniSettings[uKey]=cPath(uResult)
                    else:
                        self.aIniSettings[uKey] = uResult
                elif uType == "title" or uType=="buttons":
                    pass
                else:
                    self.ShowError(u'Cannot read config name (base), wrong attribute:'+self.oObject.oObjectConfig.oFnConfig.string + u' Section:'+self.uSection+" " +dLine["type"])

                if uKey == 'FNCodeset':
                    self.ReadCodeset()

            self.oObject.oObjectConfig.oConfigParser.write()
        except Exception as e:
            self.ShowError(u'Cannot read config name (base):'+self.oObject.oObjectConfig.oFnConfig.string + u' Section:'+self.uSection,e)
            return

    def WriteConfigToIniFile(self) -> None:
        """ Writes changes to the object config file """
        self.oObject.oObjectConfig.oConfigParser.write()

    def ReadCodeset(self) -> None:
        # Dummy
        pass

    def ShowWarning(self,uMsg:str) -> str:
        """ Shows a warning """
        uRet:str=u'Script '+self.oObject.uObjectName+u'/'+self.uConfigName+u': '+ uMsg
        Logger.warning (uRet)
        return uRet

    def ShowInfo(self,uMsg:str) -> str:
        """ Shows a warning """
        uRet:str=u'Script '+self.oObject.uObjectName+u'/'+self.uConfigName+u': '+ uMsg
        Logger.info (uRet)
        return uRet

    def ShowDebug(self,uMsg:str)-> str:
        """ Shows a debug message """
        uRet:str = u'Script '+self.oObject.uObjectName+u'/'+self.uConfigName+u': '+ uMsg
        Logger.debug (uRet)
        return uRet

    def ShowError(self,uMsg:str, oException:Exception=None) -> str:
        """ Shows an error"""
        iErrNo:int = 0
        if oException is not None:
            if hasattr(oException,'errno'):
                iErrNo=oException.errno
        if iErrNo is None:
            iErrNo=-1

        uRet:str = LogErrorSmall (uMsg=u'Script %s/%s %s (%d):' %( self.oObject.uObjectName,self.uConfigName, uMsg,iErrNo),oException=oException)

        return uRet
