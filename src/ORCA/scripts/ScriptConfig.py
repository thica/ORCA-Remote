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

from ORCA.settings.setttingtypes.Public import RegisterSettingTypes
from ORCA.ui.InputKeyboard              import ShowKeyBoard
from ORCA.ui.RaiseQuestion              import ShowQuestionPopUp
from ORCA.utils.ConfigHelpers           import Config_GetDefault_Str
from ORCA.utils.TypeConvert             import DictToUnicode
from ORCA.vars.Access                   import GetVar
from ORCA.vars.Access                   import SetVar
from ORCA.vars.Replace                  import ReplaceVars
from kivy.config                        import ConfigParser as KivyConfigParser
from ORCA.utils.FileName                import cFileName

import ORCA.Globals as Globals


class cScriptConfig(object):
    """ Class to manage the initialisation/configuration and access the the settings of an Script settings objects

    """

    def __init__(self, oScript):
        self.oScript                        = oScript
        self.oConfigParser                  = KivyConfigParser()
        self.oFnConfig                      = None
        self.uCurrentSection                = None
        self.uDefaultConfigName             = u'SCRIPTDEFAULT'
        self.aDiscoverScriptList            = None
        self.oInputKeyboard                 = None
        self.dDefaultSettings               = {"SettingTitle":               {"active": "enabled",  "order": 0,    "type": "title" ,       "title": "$lvar(560)"},
                                               "TimeOut":                    {"active": "disabled", "order": 1,    "type": "numericfloat", "title": "$lvar(6019)", "desc": "$lvar(6020)", "section": "$var(ScriptConfigSection)", "key": "TimeOut", "default": "1.0"},
                                               "Host":                       {"active": "disabled", "order": 5,    "type": "string",       "title": "$lvar(6004)", "desc": "$lvar(6005)", "section": "$var(ScriptConfigSection)", "key": "Host", "default": "192.168.1.2"},
                                               "Port":                       {"active": "disabled", "order": 6,    "type": "string",       "title": "$lvar(6002)", "desc": "$lvar(6003)", "section": "$var(ScriptConfigSection)", "key": "Port", "default": "80"},
                                               "User":                       {"active": "disabled", "order": 7,    "type": "string",       "title": "$lvar(6006)", "desc": "$lvar(6007)", "section": "$var(ScriptConfigSection)", "key": "User", "default": ""},
                                               "Password":                   {"active": "disabled", "order": 8,    "type": "string",       "title": "$lvar(6008)", "desc": "$lvar(6009)", "section": "$var(ScriptConfigSection)", "key": "Password", "default": ""},
                                               "ConfigChangeButtons":        {"active": "disabled", "order": 999,  "type": "buttons",      "title": "$lvar(565)",  "desc": "$lvar(566)",  "section": "$var(ScriptConfigSection)", "key": "configchangebuttons",         "buttons": [{"title": "$lvar(569)", "id": "button_add"}, {"title": "$lvar(570)", "id": "button_delete"}, {"title": "$lvar(571)", "id": "button_rename"}]},
                                               }

        self.dSettingsCombined            = {}

    def Init(self):

        """ Init function, sets the configuration file name and add the default sections """

        self.oFnConfig = cFileName(self.oScript.oPathMy) + u'config.ini'
        if not self.oFnConfig.Exists():
            self.oConfigParser.filename = self.oFnConfig.string
            self.CreateSection(uSectionName=self.uDefaultConfigName)

    def LoadConfig(self):
        """ Loads the config file (only once) """

        try:
            self.oConfigParser.filename = self.oFnConfig.string
            if len(self.oConfigParser._sections) == 0:
                if self.oFnConfig.Exists():
                    self.oScript.ShowDebug(u'Reading Config File')
                    self.oConfigParser.read(self.oFnConfig.string)
        except Exception as e:
            self.oScript.ShowError(u"can\'t load config file: %s" % self.oFnConfig.string, None, e)

    def CreateSection(self, uSectionName):
        """
        Adds a new section to the config parser

        :param string uSectionName: The name of the section to create
        """
        self.oScript.ShowDebug('Adding new section [%s]' % (uSectionName))
        self.oConfigParser.add_section(uSectionName)
        self.oConfigParser.write()

    def GetSettingParFromIni(self, uSectionName, uVarName):
        """
        Returns a setting for the configuration ini file
        If the entry does not exist, it tries to puls the value from the  aInterFaceIniSettings dict of already predifined settings
        If not exist there as well, an error will be logged

        :rtype: string|None
        :param string uSectionName: The name of the section
        :param uVarName: The name of the parameter/setting in the section
        :return: The value of the setting, empty string if not found
         """

        oSetting = self.oScript.GetSettingObjectForConfigName(uSectionName)
        uResult = Config_GetDefault_Str(self.oConfigParser, uSectionName, uVarName, None)
        if uResult is None:
            uResult = str(oSetting.aScriptIniSettings.queryget(uVarName))
        if uResult is None:
            uResult = ''
            self.oScript.ShowError(u'can\'t find script setting: %s:%s' % (uSectionName, uVarName))
        else:
            self.oScript.ShowDebug(u'Returning script setting: %s from %s:%s' % (uResult, uSectionName, uVarName))
        return uResult

    def WriteDefinitionConfigPar(self, uSectionName, uVarName, uVarValue, bNowrite=False, bForce= False):
        """ Writes a variable to the config file
        :param string uSectionName: The name of the section
        :param string uVarName: The name of the parameter/setting in the section
        :param string uVarValue: The value for the setting
        :param bool bNowrite: Flag, if we should not immidiatly write the the setting
        :param bool bForce: Flag to force write, even if parameter exists in config
        """
        self.LoadConfig()
        if not self.oConfigParser.has_section(uSectionName):
            self.CreateSection(uSectionName=uSectionName)

        if self.oConfigParser.has_option(uSectionName,uVarName):
            if not bForce:
                return

        self.oConfigParser.set(uSectionName, uVarName, uVarValue)
        if not bNowrite:
            self.oConfigParser.write()

        for uSettingName in self.oScript.aSettings:
            oSetting = self.oScript.aSettings[uSettingName]
            if oSetting.uConfigName == uSectionName:
                oSetting.aScriptIniSettings[uVarName] = uVarValue
                break

    def WriteDefinitionConfig(self, uSectionName, dSettings):
        """
        writes all vars given in a dictionary to the config file

        :param string uSectionName: The name of the section
        :param dict dSettings: A dict of all settings to write
        """

        for uKey in dSettings:
            self.WriteDefinitionConfigPar(uSectionName=uSectionName, uVarName=uKey, uVarValue=dSettings[uKey], bNowrite=True)
        self.oConfigParser.write()

    def ConfigureKivySettings(self, oKivySetting):
        """
        Create the JSON string for all sections and applies it to a kivy settings object
        Discover settings are excluded

        :param setting oKivySetting:
        :return: The KivySetting object
        """
        RegisterSettingTypes(oKivySetting)
        aSections = self.oConfigParser.sections()
        if len(aSections)==0:
            self.CreateSection(uSectionName = self.uDefaultConfigName)

        for uSection in aSections:
            # the Section list should be applied as a orca var
            SetVar(uVarName=u'ScriptConfigSection', oVarValue=uSection)
            # Let create a new temporary cSetting object to not harm the existing ones
            oSetting = self.oScript.cScriptSettings(self.oScript)
            # Read the ini file for this section
            oSetting.ReadConfigFromIniFile(uSection)
            # Create the setting string
            dSettingsJSON = self.CreateSettingJsonCombined(oSetting=oSetting)
            uSettingsJSON = SettingDictToString(dSettingsJSON)
            uSettingsJSON = ReplaceVars(uSettingsJSON)
            oSetting = None

            # if there is nothing to configure, then return
            if uSettingsJSON == u'{}':
                Globals.oNotifications.SendNotification('closesetting_script')
                return False

            # add the jSon to the Kivy Setting
            oKivySetting.add_json_panel(uSection, self.oConfigParser, data=uSettingsJSON)

        # Adds the action handler
        oKivySetting.bind(on_config_change=self.On_ConfigChange)
        return oKivySetting

    def On_ConfigChange(self, oSettings, oConfig, uSection, uKey, uValue):
        """ reacts, if user changes a setting """
        if uKey == u'configchangebuttons':
            self.uCurrentSection = uSection
            if uValue == u'button_add':
                SetVar(uVarName=u'SCRIPTINPUT', oVarValue=u'DEVICE_dummy')
                self.oInputKeyboard = ShowKeyBoard(u'SCRIPTINPUT', self.On_InputAdd)
            if uValue == u'button_delete':
                ShowQuestionPopUp(uTitle=u'$lvar(5003)', uMessage=u'Do you really want to delete this setting?', fktYes=self.On_InputDel, uStringYes=u'$lvar(5001)', uStringNo=u'$lvar(5002)')
            if uValue == u'button_rename':
                SetVar(uVarName=u'SCRIPTINPUT', oVarValue=uSection)
                self.oInputKeyboard = ShowKeyBoard(u'SCRIPTINPUT', self.On_InputRen)
        else:
            oSetting = self.oScript.GetSettingObjectForConfigName(uConfigName=uSection)
            oSetting.aScriptIniSettings[uKey] = uValue

    def On_InputAdd(self, uInput):
        """ User pressed the add configuration button """
        if uInput == u'':
            return
        if self.oConfigParser.has_section(uInput):
            return
        self.oConfigParser.add_section(uInput)
        # self.InitializeSection(uInput)
        self.oConfigParser.write()
        Globals.oTheScreen.AddActionToQueue([{'string': 'updatewidget', 'widgetname': 'Scriptsettings'}])
        self.ShowSettings()

    def On_InputDel(self):
        """ User pressed the del configuration button """
        self.oConfigParser.remove_section(self.uCurrentSection)
        self.oConfigParser.write()
        self.ShowSettings()

    def On_InputRen(self, uInput):
        """ User pressed the rename configuration button """
        if uInput == u'':
            return
        if self.oConfigParser.has_section(uInput):
            return
        self.oConfigParser._sections[uInput] = self.oConfigParser._sections[self.uCurrentSection]
        self.oConfigParser._sections.pop(self.uCurrentSection)
        self.oConfigParser.write()
        self.ShowSettings()

    def ShowSettings(self):
        """ Shows the settings page """
        Globals.oTheScreen.AddActionToQueue([{'string': 'updatewidget', 'widgetname': 'Scriptsettings'}])

    def GetSettingParFromVar2(self, uScriptName, uConfigName, uSettingParName):
        """
        Gets a Value for a setting parameter from the orca vars
        The Orca vars fpr the parameter are automatically set in the cInterfaceMonitoredSettings class

        :rtype: string
        :param uScriptName: The name of script to use
        :param uConfigName: The nemae of the Config
        :param uSettingParName: The name of the parameter
        :return: The value of the parameter
        """


        return GetVar(uVarName="CONFIG_" + uSettingParName.upper(), uContext=uScriptName + u'/' + uConfigName)


    def CreateSettingJsonCombined(self, oSetting):
        """
        Creates a json dict which holds all the setting definitions of
        the core interface plus the settinmgs from the discover script (if requested)

        :rtype: dict
        :param cBaseInterFaceSettings oSetting: an IterFaceSettins Object
        :return: a dict of combined settings
        """

        if len(self.dSettingsCombined)!=0:
            return self.dSettingsCombined
        dRet = {}

        for uKey in self.dDefaultSettings:
            if self.dDefaultSettings[uKey]["active"] != "disabled":
                dRet[uKey] = self.dDefaultSettings[uKey]

        dScriptJSON = self.oScript.GetConfigJSON()
        for uKey in dScriptJSON:
            dLine = dScriptJSON[uKey]
            iOrder = dLine['order']
            for uKey2 in dRet:
                if dRet[uKey2]['order'] >= iOrder:
                    dRet[uKey2]['order'] += 1
            dRet[uKey] = dLine

        self.dSettingsCombined = dRet
        return dRet


def SettingDictToString(dSettingList):
    """
    Converts a dict into a string suitable for the kivy settings object.
    Only enries which are enabled will be shown

    :rtype: string
    :param dict dSettingList: a JSON dictionary al all settings
    :return: The kivy setting string
    """

    aSubList = list(dSettingList.keys())
    aSubList2 = sorted(aSubList, key=lambda entry: dSettingList[entry]['order'])

    uResult = u"["
    for uKey in aSubList2:
        if dSettingList[uKey]['active'] == 'enabled':
            uResult += DictToUnicode(dSettingList[uKey]) + ",\n"
    uResult = uResult[:-2] + u"]"
    return uResult
