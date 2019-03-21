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

from kivy.logger import Logger

from ORCA.scripts.ScriptMonitoredSettings   import cScriptMonitoredSettings
from ORCA.utils.ConfigHelpers               import Config_GetDefault_Str
from ORCA.utils.LogError                    import LogErrorSmall
from ORCA.utils.TypeConvert                 import ToInt, ToFloat, ToBool, ToUnicode
from ORCA.vars.Access                       import SetVar
from ORCA.vars.Replace                      import ReplaceVars


class cBaseScriptSettings(object):
    """ A base class for the script settings """
    def __init__(self, oScript):
        # some default settings, which should be there even if not configured by the script
        # use the exact spelling as in the settings json

        self.oScript                                            = oScript
        self.uConfigName                                        = "SCRIPTDEFAULT"

        self.aScriptIniSettings                                  = cScriptMonitoredSettings(self)
        self.aScriptIniSettings.bInitCompleted                   = False
        self.bOnError                                           = False
        self.oResultParser                                      = None
        self.uContext                                           = u''
        self.uSection                                           = None

    def ReadConfigFromIniFile(self,uConfigName):
        """ Reads the script config file """
        if self.aScriptIniSettings.bInitCompleted:
            return
        self.aScriptIniSettings.bInitCompleted = True

        if uConfigName != u'':
            self.uConfigName = uConfigName
            self.uContext=self.oScript.uScriptName+u'/'+self.uConfigName
        self.uSection = self.uConfigName

        try:
            self.oScript.oScriptConfig.LoadConfig()
            SetVar(uVarName = u'ScriptConfigSection', oVarValue = uConfigName)
            dIniDef = self.oScript.oScriptConfig.CreateSettingJsonCombined(self)

            for uKey2 in dIniDef:
                oLine = dIniDef[uKey2]
                uType       = oLine.get("type")
                uKey        = oLine.get("key")
                uDefault    = oLine.get("default")

                if uKey is None or uDefault is None:
                    continue

                # we replace JSON defaults by script-settings defaults, if exists
                if self.aScriptIniSettings.queryget(uKey) is not None:
                    uDefault = self.aScriptIniSettings.queryget(uKey)

                uResult     = Config_GetDefault_Str(self.oScript.oScriptConfig.oConfigParser,self.uSection, uKey,uDefault)

                if uType == "scrolloptions" or uType == "string":
                    self.aScriptIniSettings[uKey]=ReplaceVars(uResult)
                elif uType == "numeric" or uType == "numericslider":
                    self.aScriptIniSettings[uKey]=ToInt(uResult)
                elif uType == "numericfloat" :
                    self.aScriptIniSettings[uKey]=ToFloat(uResult)
                elif uType == "bool":
                    self.aScriptIniSettings[uKey]=ToBool(uResult)
                elif uType == "title" or uType=="buttons" or uType=="path" or uType=="varstring":
                    pass
                else:
                    self.ShowError(u'Cannot read config name (base), wrong attribute:'+self.oScript.oScriptConfig.oFnConfig.string + u' Section:'+self.uSection+" " +oLine["type"])

            self.oScript.oScriptConfig.oConfigParser.write()
        except Exception as e:
            self.ShowError(uMsg = u'Cannot read config name (base):'+self.oScript.oScriptConfig.oFnConfig.string + u' Section:'+self.uSection, oException = e)
            return

    def SetContextVar(self,uVarName,uVarPar):
        """ Sets a var within the script context """
        SetVar(uVarName = uVarName, oVarValue = ToUnicode(uVarPar), uContext = self.oScript.uScriptName+u'/'+self.uConfigName)

    def ShowWarning(self,uMsg):
        """ Shows a warning """
        uRet=u'Script '+self.oScript.uScriptName+u'/'+self.uConfigName+u': '+ uMsg
        Logger.warning (uRet)
        return uRet
    def ShowInfo(self,uMsg):
        """ Shows a warning """
        uRet=u'Script '+self.oScript.uScriptName+u'/'+self.uConfigName+u': '+ uMsg
        Logger.info (uRet)
        return uRet
    def ShowDebug(self,uMsg):
        """ Shows a debug message """
        uRet=u'Script '+self.oScript.uScriptName+u'/'+self.uConfigName+u': '+ uMsg
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

        uRet = LogErrorSmall (u'Script %s/%s %s (%d):' %( self.oScript.uScriptName,self.uConfigName, uMsg,iErrNo),oException)

        return uRet
