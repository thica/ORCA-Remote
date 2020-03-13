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

from typing import Dict
from typing import Union

from copy                               import copy

from kivy.uix.settings                  import Settings as KivySettings
from kivy.config                        import ConfigParser as KivyConfigParser

from ORCA.vars.Access                   import SetVar
from ORCA.vars.Access                   import GetVar
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.settings.setttingtypes.Public import RegisterSettingTypes
from ORCA.ui.ShowErrorPopUp             import ShowMessagePopUp
from ORCA.utils.TypeConvert             import DictToUnicode

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.interfaces.BaseInterface import cBaseInterFace
    from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
else:
    from typing import TypeVar
    cBaseInterFace         = TypeVar("cBaseInterFace")
    cBaseInterFaceSettings = TypeVar("cBaseInterFaceSettings")

class cInterFaceConfigDiscover:
    def __init__(self,oInterFace:cBaseInterFace):
        self.oInterFace:cBaseInterFace         = oInterFace
        self.oConfigParser:KivyConfigParser    = oInterFace.oObjectConfig.oConfigParser
        self.uConfigName:str                   = u''

    def Init(self):
        """ Init function, sets the configuration file name and add the default sections """
        pass


    def ConfigureKivySettingsForDiscoverParameter(self, oKivySetting:KivySettings,uConfigName:str) -> Union[KivyConfigParser,None]:
        """
        Create the JSON string for all discover scripts and applies it to a kivy settings object

        :param setting oKivySetting:
        :param string uConfigName:
        :return: The KivySetting object
        """

        uSettingsJSON: str
        uKey:str
        uDictKey:str

        SetVar(uVarName=u'ObjectConfigSection', oVarValue=uConfigName)
        self.uConfigName = uConfigName
        RegisterSettingTypes(oKivySetting)
        oSetting:cBaseInterFaceSettings = self.oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
        dSettingsJSON:Dict[str,Dict] = self.CreateSettingJsonCombined(oSetting=oSetting)
        if len(dSettingsJSON)==0:
            return None
            # return self.On_SettingsClose(None)

        # add the jSon to the Kivy Setting

        dTarget:Dict[str,Dict] = {}
        for uKey in dSettingsJSON:
            uDictKey=dSettingsJSON[uKey]['scriptsection']
            if dTarget.get(uDictKey) is None:
                dTarget[uDictKey]={}
            dTarget[uDictKey][uKey] = dSettingsJSON[uKey]

        for uKey in dTarget:
            if not uKey.startswith('discover'):
                uSettingsJSON = SettingDictToString2(dTarget[uKey])
                uSettingsJSON = ReplaceVars(uSettingsJSON)
                if uSettingsJSON!=u'[]':
                    oKivySetting.add_json_panel(ReplaceVars(uKey), self.oConfigParser, data=uSettingsJSON)

        for uKey in dTarget:
            if uKey.startswith('discover'):
                if uKey in GetVar("DISCOVERSCRIPTLIST"):
                    uSettingsJSON = SettingDictToString2(dTarget[uKey])
                    uSettingsJSON = ReplaceVars(uSettingsJSON)
                    if uSettingsJSON!=u'[]':
                        oKivySetting.add_json_panel(uKey[9:].upper(), self.oConfigParser, data=uSettingsJSON)

        # Adds the action handler
        oKivySetting.bind(on_config_change=self.On_ConfigChange)
        return oKivySetting

    # noinspection PyUnusedLocal
    def On_ConfigChange(self, oSettings:KivySettings, oConfig:KivyConfigParser, uSection:str, uKey:str, uValue:str) -> None:
        """ reacts, if user changes a setting """
        if uKey != "CheckDiscover":
            oSetting:cBaseInterFaceSettings = self.oInterFace.GetSettingObjectForConfigName(uConfigName=uSection)
            oSetting.aIniSettings[uKey]=uValue
        else:
            self.CheckDiscover(uSection = uSection)

    def CheckDiscover(self,uSection:str)  -> None:

        self.oInterFace.ShowDebug(uMsg=u'Testing to discover settings')
        oSetting:cBaseInterFaceSettings = self.oInterFace.GetSettingObjectForConfigName(uConfigName=uSection)
        uDiscoverScriptName:str = oSetting.aIniSettings.uDiscoverScriptName
        dParams:Dict[str,str] = {}
        uKey:str
        uParamKey:str
        dResult:Dict
        uResult:str
        oException:Exception

        for uKey in oSetting.aIniSettings:
            if uKey[1:].startswith(uDiscoverScriptName.upper()):
                uParamKey=uKey[len(uDiscoverScriptName)+2:]
                dParams[uParamKey]=oSetting.aIniSettings[uKey]

        dResult = Globals.oScripts.RunScript(uDiscoverScriptName, **dParams)
        oException = dResult.get('Exception',None)
        uResult = ""
        if oException is None:
            for uKey in dResult:
                uResult = uResult + uKey+":"+str(dResult[uKey]) + "\n"
            ShowMessagePopUp(uMessage=uResult)

    # noinspection PyMethodMayBeStatic
    def ShowSettingsDiscover(self) -> None:
        """ Shows the settings page """
        Globals.oTheScreen.AddActionToQueue(aActions=[{'string': 'updatewidget', 'widgetname': 'Interfacesettings_discover'}])

    # noinspection PyUnusedLocal
    def CreateSettingJsonCombined(self, **kwargs) -> Dict[str,Dict]:
        """
        Creates a json dict which holds all the setting definitions of
        the core interface plus the settings from the discover script (if requested)

        :return: a dict of combined settings
        """

        dRet:Dict[str,Dict] = {}
        uKey:str
        uSection:str

        for uKey in self.oInterFace.oObjectConfig.dSettingsCombined:
            uSection = self.oInterFace.oObjectConfig.dSettingsCombined[uKey].get('scriptsection')
            if uSection:
                dRet[uKey]=self.oInterFace.oObjectConfig.dSettingsCombined[uKey]
                dRet[uKey]['section'] = "$var(ObjectConfigSection)"

        self.CreateDiscoverScriptListVar()
        return dRet

    def CreateDiscoverScriptListVar(self) -> None:
        """
        Creates a list of valid discover strings. Set the DISCOVERSCRIPTLIST var
        """

        uScripts:str = ""
        uScriptName:str
        uScriptSubTypeName:str

        for uScriptName in self.oInterFace.oObjectConfig.aDiscoverScriptList:
            uScriptSubTypeName = Globals.oScripts.dScripts[uScriptName].uSubType
            if uScriptSubTypeName in self.oInterFace.aDiscoverScriptsBlackList:
               continue
            if len(self.oInterFace.aDiscoverScriptsWhiteList)>0:
                if uScriptSubTypeName in self.oInterFace.aDiscoverScriptsWhiteList:
                    uScripts = uScripts + '"' + uScriptName + '",'
                    continue
                else:
                    continue
            uScripts=uScripts+'"'+uScriptName+'",'
        uScripts = uScripts[1:-2]
        SetVar("DISCOVERSCRIPTLIST",uScripts)

def SettingDictToString2(dSettingList:Dict[str,Dict]) -> str:
    """
    Converts a dict into a string suitable for the kivy settings object.
    Only enries which are enabled will be shown

    :param dict dSettingList: a JSON dictionary al all settings
    :return: The kivy setting string
    """

    dLine: Dict

    uResult:str = u"["
    for uKey in dSettingList:
       dLine = copy(dSettingList[uKey])
       dLine.pop("order", None)
       dLine.pop("active", None)
       dLine.pop("default", None)
       if "scriptsection" in dLine:
           dLine.pop("scriptsection", None)
       uResult += DictToUnicode(dLine) + ",\n"

    if len(uResult)>2:
        uResult = uResult[:-2] + u"]"
    else:
        uResult="[]"
    return uResult
