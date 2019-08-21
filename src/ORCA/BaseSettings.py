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

from ORCA.vars.QueryDict    import cMonitoredSettings
from kivy.logger import Logger
from kivy.compat import string_types

from ORCA.utils.ConfigHelpers               import Config_GetDefault_Str
from ORCA.utils.LogError                    import LogErrorSmall
from ORCA.utils.TypeConvert                 import ToInt, ToFloat, ToBool, ToUnicode
from ORCA.vars.Access                       import SetVar
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.utils.Path                        import cPath

class cObjectMonitoredSettings(cMonitoredSettings):
    def WriteVar(self,sName,oValue):
        self.oBaseSettings.SetContextVar("CONFIG_" + sName.upper()[1:], oValue)

class cBaseSettings(object):
    """ A base class for the script settings """
    def __init__(self, oObject):
        # some default settings, which should be there even if not configured by the Object
        # use the exact spelling as in the settings json

        self.oObject                                            = oObject
        self.uConfigName                                        = "DEFAULT"
        self.uContext                                           = u''
        self.uSection                                           = None
        self.aIniSettings                                       = cObjectMonitoredSettings(self)
        self.aIniSettings.bInitCompleted                        = False
        self.bOnError                                           = False

    def SetContextVar(self,uVarName,uVarValue):
        """ Sets a var within the interface context

        :param string uVarName: The name of the var
        :param string uVarValue: The value if the var
        """
        SetVar(uVarName = uVarName, oVarValue = ToUnicode(uVarValue), uContext = self.oObject.uObjectName+u'/'+self.uConfigName)

    def ReadConfigFromIniFile(self,uConfigName):
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
            dIniDef = self.oObject.oObjectConfig.CreateSettingJsonCombined(oSetting=self)

            for uKey2 in dIniDef:
                oLine       = dIniDef[uKey2]
                uType       = oLine.get("type")
                uKey        = oLine.get("key")
                uDefault    = oLine.get("default")

                if uKey is None or uDefault is None:
                    continue

                # we replace JSON defaults by interface-settings defaults, if exists
                if self.aIniSettings.queryget(uKey) is not None:
                    uDefault = self.aIniSettings.queryget(uKey)

                uResult     = Config_GetDefault_Str(self.oObject.oObjectConfig.oConfigParser,self.uSection, uKey,uDefault)

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
                    if isinstance(uResult,string_types):
                        self.aIniSettings[uKey]=cPath(uResult)
                    else:
                        self.aIniSettings[uKey] = uResult
                elif uType == "title" or uType=="buttons":
                    pass
                else:
                    self.ShowError(u'Cannot read config name (base), wrong attribute:'+self.oObject.oObjectConfig.oFnConfig.string + u' Section:'+self.uSection+" " +oLine["type"])

                if uKey == 'FNCodeset':
                    self.ReadCodeset()

            self.oObject.oObjectConfig.oConfigParser.write()
        except Exception as e:
            self.ShowError(u'Cannot read config name (base):'+self.oObject.oObjectConfig.oFnConfig.string + u' Section:'+self.uSection,e)
            return

    def WriteConfigToIniFile(self):
        """ Writes changes to the object config file """
        self.oObject.oObjectConfig.oConfigParser.write()

    def ReadCodeset(self):
        # Dummy
        pass

    def ShowWarning(self,uMsg):
        """ Shows a warning """
        uRet=u'Script '+self.oObject.uObjectName+u'/'+self.uConfigName+u': '+ uMsg
        Logger.warning (uRet)
        return uRet
    def ShowInfo(self,uMsg):
        """ Shows a warning """
        uRet=u'Script '+self.oObject.uObjectName+u'/'+self.uConfigName+u': '+ uMsg
        Logger.info (uRet)
        return uRet
    def ShowDebug(self,uMsg):
        """ Shows a debug message """
        uRet=u'Script '+self.oObject.uObjectName+u'/'+self.uConfigName+u': '+ uMsg
        Logger.debug (uRet)
        return uRet
    def ShowError(self,uMsg, oException=None):
        """ Shows an error"""
        iErrNo = 0
        if oException is not None:
            if hasattr(oException,'errno'):
                iErrNo=oException.errno
        if iErrNo is None:
            iErrNo=-1

        uRet = LogErrorSmall (u'Script %s/%s %s (%d):' %( self.oObject.uObjectName,self.uConfigName, uMsg,iErrNo),oException)

        return uRet
