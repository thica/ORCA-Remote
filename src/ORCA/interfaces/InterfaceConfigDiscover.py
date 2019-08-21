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

from ORCA.vars.Access                   import SetVar
from ORCA.vars.Access                   import GetVar
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.utils.TypeConvert             import DictToUnicode
from ORCA.settings.setttingtypes.Public import RegisterSettingTypes
from ORCA.ui.ShowErrorPopUp             import ShowMessagePopUp

import ORCA.Globals as Globals

class cInterFaceConfigDiscover(object):
    def __init__(self,oInterFace):
        self.oInterFace         = oInterFace
        self.oConfigParser      = oInterFace.oObjectConfig.oConfigParser
        self.uConfigName        = ""
    def Init(self):
        """ Init function, sets the configuration file name and add the default sections """
        pass


    def ConfigureKivySettingsForDiscoverParameter(self, oKivySetting,uConfigName):
        """
        Create the JSON string for all discover scripts and applies it to a kivy settings object

        :param setting oKivySetting:
        :param string uConfigName:
        :return: The KivySetting object
        """

        SetVar(uVarName=u'ObjectConfigSection', oVarValue=uConfigName)
        self.uConfigName = uConfigName
        RegisterSettingTypes(oKivySetting)
        oSetting = self.oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
        dSettingsJSON = self.CreateSettingJsonCombined(oSetting=oSetting)
        if len(dSettingsJSON)==0:
            return None
            # return self.On_SettingsClose(None)

        # add the jSon to the Kivy Setting

        dTarget= {}
        for uKey in dSettingsJSON:
            uDictKey=dSettingsJSON[uKey]['scriptsection']
            if dTarget.get(uDictKey) is None:
                dTarget[uDictKey]={}
            dTarget[uDictKey][uKey] = dSettingsJSON[uKey]

        for uKey in dTarget:
            if not uKey.startswith('discover'):
                uSettingsJSON = SettingDictToString(dTarget[uKey])
                uSettingsJSON = ReplaceVars(uSettingsJSON)
                oKivySetting.add_json_panel(ReplaceVars(uKey), self.oConfigParser, data=uSettingsJSON)

        for uKey in dTarget:
            if uKey.startswith('discover'):
                if uKey in GetVar("DISCOVERSCRIPTLIST"):
                    uSettingsJSON = SettingDictToString(dTarget[uKey])
                    uSettingsJSON = ReplaceVars(uSettingsJSON)
                    oKivySetting.add_json_panel(uKey[9:].upper(), self.oConfigParser, data=uSettingsJSON)

        # Adds the action handler
        oKivySetting.bind(on_config_change=self.On_ConfigChange)
        return oKivySetting

    def On_ConfigChange(self, oSettings, oConfig, uSection, uKey, uValue):
        """ reacts, if user changes a setting """
        if uKey != "CheckDiscover":
            oSetting = self.oInterFace.GetSettingObjectForConfigName(uConfigName=uSection)
            oSetting.aIniSettings[uKey]=uValue
        else:
            self.CheckDiscover(uSection = uSection)

    def CheckDiscover(self,uSection):

        self.oInterFace.ShowDebug(u'Testing to discover settings')
        oSetting = self.oInterFace.GetSettingObjectForConfigName(uConfigName=uSection)
        uDiscoverScriptName = oSetting.aIniSettings.uDiscoverScriptName
        dParams={}

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


    def ShowSettingsDiscover(self):
        """ Shows the settings page """
        Globals.oTheScreen.AddActionToQueue([{'string': 'updatewidget', 'widgetname': 'Interfacesettings_discover'}])

    def CreateSettingJsonCombined(self, **kwargs):
        """
        Creates a json dict which holds all the setting definitions of
        the core interface plus the settings from the discover script (if requested)

        :rtype: dict
        :return: a dict of combined settings
        """

        dRet = {}

        for uKey in self.oInterFace.oObjectConfig.dSettingsCombined:
            uSection = self.oInterFace.oObjectConfig.dSettingsCombined[uKey].get('scriptsection')
            if uSection:
                dRet[uKey]=self.oInterFace.oObjectConfig.dSettingsCombined[uKey]
                dRet[uKey]['section'] = "$var(ObjectConfigSection)"

        self.CreateDiscoverScriptListVar()
        return dRet

    def CreateDiscoverScriptListVar(self):
        """
        Creates a list of valid discover strings. Set the DISCOVERSCRIPTLIST var

        """

        uScripts = ""
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

def SettingDictToString(dSettingList):
    """
    Converts a dict into a string suitable for the kivy settings object.
    Only entries which are enabled will be shown

    :rtype: string
    :param dict dSettingList: a JSON dictionary al all settings
    :return: The kivy setting string
    """

    aSubList = list(dSettingList.keys())
    aSubList2 = sorted(aSubList, key=lambda entry: dSettingList[entry]['order'])

    uResult = u"["
    for uKey in aSubList2:
        uResult += DictToUnicode(dSettingList[uKey]) + ",\n"
    uResult = uResult[:-2] + u"]"
    return uResult
