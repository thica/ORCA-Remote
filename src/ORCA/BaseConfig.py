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

from copy                               import copy
from kivy.config                        import ConfigParser as KivyConfigParser
from ORCA.settings.setttingtypes.Public import RegisterSettingTypes
from ORCA.ui.InputKeyboard              import ShowKeyBoard
from ORCA.ui.RaiseQuestion              import ShowQuestionPopUp
from ORCA.utils.ConfigHelpers           import Config_GetDefault_Str
from ORCA.utils.FileName                import cFileName
from ORCA.utils.TypeConvert             import DictToUnicode
from ORCA.utils.TypeConvert             import ToBool
from ORCA.utils.TypeConvert             import ToFloat
from ORCA.utils.TypeConvert             import ToInt
from ORCA.vars.Access                   import GetVar
from ORCA.vars.Access                   import SetVar
from ORCA.vars.Replace                  import ReplaceVars

import ORCA.Globals as Globals

__all__ = ['cBaseConfig','SettingDictToString']

class cBaseConfig(object):
    """ Base Class to manage the initialisation/configuration and access to the settings of an Interface or scripts settings objects
    """

    def __init__(self, oObject):
        self.oObject                        = oObject
        self.oConfigParser                  = KivyConfigParser()
        self.oFnConfig                      = None
        self.uCurrentSection                = None
        self.uDefaultConfigName             = u'DEFAULT'
        self.oInputKeyboard                 = None
        self.dDefaultSettings               = {}
        self.dSettingsCombined              = {}
        self.uType                          = ""
        self.uWidgetName                    = ""

    def Init(self):

        """ Init function, sets the configuration file name and add the default sections """

        if self.oObject.oPathMyData is None:
            return

        self.oFnConfig = cFileName(self.oObject.oPathMyData) + u'config.ini'

        if not self.oFnConfig.Exists():
            self.oConfigParser.filename = self.oFnConfig.string
            self.CreateSection(uSectionName=self.uDefaultConfigName)

    def LoadConfig(self):
        """ Loads the config file (only once) """

        if self.oObject.oPathMyData is None:
            return

        try:
            self.oConfigParser.filename = self.oFnConfig.string
            if len(self.oConfigParser._sections) == 0:
                if self.oFnConfig.Exists():
                    self.oObject.ShowDebug(u'Reading Config File')
                    self.oConfigParser.read(self.oFnConfig.string)
            else:
                if not self.oFnConfig.Exists():
                    self.oConfigParser.write()
        except Exception as e:
            self.oObject.ShowError(u"can\'t load config file: %s" % self.oFnConfig.string, None, e)


    def CreateSection(self, uSectionName):
        """
        Adds a new section to the config parser

        :param string uSectionName: The name of the section to create
        """

        if self.oObject.oPathMyData is not None:
            self.oObject.ShowDebug('Adding new section [%s]' % uSectionName)
            self.oConfigParser.add_section(uSectionName)
            self.oConfigParser.write()

    def GetSettingParFromIni(self, uSectionName, uVarName):
        """
        Returns a setting for the configuration ini file
        If the entry does not exist, it tries to puls the value from the  aIniSettings dict of already predifined settings
        If not exist there as well, an error will be logged

        :rtype: string|None
        :param string uSectionName: The name of the section
        :param uVarName: The name of the parameter/setting in the section
        :return: The value of the setting, empty string if not found
         """

        oSetting = self.oObject.GetSettingObjectForConfigName(uSectionName)
        uResult = Config_GetDefault_Str(self.oConfigParser, uSectionName, uVarName, "***notfound***")
        if uResult == "***notfound***":
            uResult = str(oSetting.aIniSettings.queryget(uVarName))
        if uResult is None:
            uResult = ''
            self.oObject.ShowError(u'can\'t find setting: %s:%s' % (uSectionName, uVarName))
        else:
            self.oObject.ShowDebug(u'Returning setting: %s from %s:%s' % (uResult, uSectionName, uVarName))
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

        for uSettingName in self.oObject.aSettings:
            oSetting = self.oObject.aSettings[uSettingName]
            if oSetting.uConfigName == uSectionName:
                oSetting.aIniSettings[uVarName] = uVarValue
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
            aSections = self.oConfigParser.sections()

        if self.uType=="interface":
            # The Codeset List could be applied as a orca var, so set it to the list
            SetVar(uVarName=u'InterfaceCodesetList', oVarValue=self.oObject.CreateCodsetListJSONString())

        for uSection in aSections:
            # the Section list should be applied as a orca var
            SetVar(uVarName=u'ObjectConfigSection', oVarValue=uSection)
            # Let create a new temporary cSetting object to not harm the existing ones
            oSetting = self.oObject.GetNewSettingObject()
            # Read the ini file for this section
            oSetting.ReadConfigFromIniFile(uSection)
            # Create the setting string
            dSettingsJSON = self.CreateSettingJsonCombined(oSetting=oSetting, bIncludeDiscoverSettings=False)

            uSettingsJSON = SettingDictToString(dSettingsJSON)
            uSettingsJSON = ReplaceVars(uSettingsJSON)
            oSetting = None

            # if there is nothing to configure, then return
            if uSettingsJSON == u'{}':
                if self.uType == "interface":
                    Globals.oNotifications.SendNotification('closesetting_interface')
                else:
                    Globals.oNotifications.SendNotification('closesetting_script')
                return False

            # add the jSon to the Kivy Setting
            oKivySetting.add_json_panel(uSection, self.oConfigParser, data=uSettingsJSON)

        # Adds the action handler
        oKivySetting.bind(on_config_change=self.On_ConfigChange)
        return oKivySetting

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

    def On_InputAdd(self, uInput):
        """
        User pressed the add configuration button

        :param string uInput: The Name of the section
        :return:
        """
        if uInput == u'':
            return
        if self.oConfigParser.has_section(uInput):
            return
        self.oConfigParser.add_section(uInput)
        self.oConfigParser.write()
        self.ShowSettings()

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
            oSetting = self.oObject.GetSettingObjectForConfigName(uConfigName=uSection)
            if uKey in self.dSettingsCombined:
                uType = self.dSettingsCombined[uKey].get("type")
                if uType == "numeric" or uType == "numericslider":
                    oSetting.aIniSettings[uKey] = ToInt(uValue)
                elif uType == "numericfloat":
                    oSetting.aIniSettings[uKey] = ToFloat(uValue)
                elif uType == "bool":
                    oSetting.aIniSettings[uKey] = ToBool(uValue)
                else:
                    oSetting.aIniSettings[uKey] = uValue

    def ShowSettings(self):
        """ Shows the settings page """
        Globals.oTheScreen.AddActionToQueue([{'string': 'updatewidget', 'widgetname': self.uWidgetName}])

    def GetSettingParFromVar2(self, uObjectName, uConfigName, uSettingParName):
        """
        Gets a Value for a setting parameter from a setting or script
        The Orca vars for the parameter are automatically set in the c"Object"MonitoredSettings class

        :rtype: string
        :param uObjectName: The name of script or interface to use
        :param uConfigName: The name of the Config
        :param uSettingParName: The name of the parameter
        :return: The value of the parameter
        """

        return GetVar(uVarName="CONFIG_" + uSettingParName.upper(), uContext=uObjectName + u'/' + uConfigName)

    def CreateSettingJsonCombined(self, **kwargs):
        """
        Creates a json dict which holds all the setting definitions of
        the core object

        :rtype: dict
        :keyword name: oSetting: an IterFaceSettins Object, needs to be cBaseSettings
        :return: a dict of combined settings
        """

        oSetting                  = kwargs.get("oSetting")

        if len(self.dSettingsCombined)!=0:
            return self.dSettingsCombined
        dRet = {}

        for uKey in self.dDefaultSettings:
            if self.dDefaultSettings[uKey]["active"] != "disabled":
                dRet[uKey] = self.dDefaultSettings[uKey]

        dScriptJSON = self.oObject.GetConfigJSON()
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
            dLine = copy(dSettingList[uKey])
            dLine.pop("order", None)
            dLine.pop("active", None)
            dLine.pop("default", None)
            uResult += DictToUnicode(dLine) + ",\n"
    uResult = uResult[:-2] + u"]"
    return uResult
