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

from __future__                         import annotations #todo: remove in Python 4.0

from typing                             import Optional
from typing                             import Dict
from typing                             import List

from copy                               import copy
from kivy.config                        import ConfigParser as KivyConfigParser
from kivy.uix.settings                  import Settings as KivySettings
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
from ORCA.ui.InputKeyboard              import cInputKeyboard

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.BaseObject   import cBaseObject
    from ORCA.BaseSettings import cBaseSettings
else:
    from typing import TypeVar
    cBaseObject     = TypeVar("cBaseObject")
    cBaseSettings   = TypeVar("cBaseSettings")

__all__ = ['cBaseConfig','SettingDictToString']


# noinspection PyProtectedMember
class cBaseConfig:
    """ Base Class to manage the initialisation/configuration and access to the settings of an Interface or scripts settings objects
    """

    def __init__(self, oObject:cBaseObject):
        self.aSections:List[str]                        = []
        self.dDefaultSettings:Dict[str,Dict]            = {}
        self.dSettingsCombined:Dict[str,Dict]           = {}
        self.oConfigParser:KivyConfigParser             = KivyConfigParser()
        self.oFnConfig:Optional[cFileName]              = None
        self.oInputKeyboard:Optional[cInputKeyboard]    = None
        self.oObject:cBaseObject                        = oObject
        self.uCurrentSection:str                        = u''
        self.uDefaultConfigName:str                     = u'DEFAULT'
        self.uType:str                                  = u''
        self.uWidgetName:str                            = u''

    def Init(self) -> None:

        """ Init function, sets the configuration file name and add the default sections """

        if self.oObject.oPathMyData is None:
            return

        self.oFnConfig = cFileName(self.oObject.oPathMyData) + u'config.ini'

        if not self.oFnConfig.Exists():
            self.oConfigParser.filename = self.oFnConfig.string
            self.CreateSection(uSectionName=self.uDefaultConfigName)

    def LoadConfig(self) -> None:
        """ Loads the config file (only once) """

        if self.oObject.oPathMyData is None:
            return

        try:
            self.oConfigParser.filename = self.oFnConfig.string
            if len(self.oConfigParser._sections) == 0:
                if self.oFnConfig.Exists():
                    self.oObject.ShowDebug(uMsg=u'Reading Config File')
                    self.oConfigParser.read(self.oFnConfig.string)
            else:
                if not self.oFnConfig.Exists():
                    self.oConfigParser.write()
        except Exception as e:
            self.oObject.ShowError(uMsg=u"can\'t load config file: %s" % self.oFnConfig.string,uParConfigName="",oException=e)

    def CreateSection(self,*,uSectionName:str) -> None:
        """
        Adds a new section to the config parser

        :param string uSectionName: The name of the section to create
        """

        if self.oObject.oPathMyData is not None:
            self.oObject.ShowDebug(uMsg='Adding new section [%s]' % uSectionName)
            self.oConfigParser.add_section(uSectionName)
            self.oConfigParser.write()

    def GetSettingParFromIni(self,*,uSectionName:str, uVarName:str) -> str:
        """
        Returns a setting for the configuration ini file
        If the entry does not exist, it tries to puls the value from the  aIniSettings dict of already predifined settings
        If not exist there as well, an error will be logged

        :param str uSectionName: The name of the section
        :param uVarName: The name of the parameter/setting in the section
        :return: The value of the setting, empty string if not found
         """

        oSetting = self.oObject.GetSettingObjectForConfigName(uConfigName=uSectionName)
        uResult = Config_GetDefault_Str(oConfig=self.oConfigParser, uSection=uSectionName, uOption=uVarName, vDefaultValue="***notfound***")
        if uResult == "***notfound***":
            uResult = str(oSetting.aIniSettings.queryget(uVarName))
        if uResult is None:
            uResult = ''
            self.oObject.ShowError(uMsg=u'can\'t find setting: %s:%s' % (uSectionName, uVarName))
        else:
            self.oObject.ShowDebug(uMsg=u'Returning setting: %s from %s:%s' % (uResult, uSectionName, uVarName))
        return uResult

    def WriteDefinitionConfigPar(self,*, uSectionName:str, uVarName:str, uVarValue:str, bNowrite:bool=False, bForce:bool= False) -> None:
        """ Writes a variable to the config file
        :param str uSectionName: The name of the section
        :param str uVarName: The name of the parameter/setting in the section
        :param str uVarValue: The value for the setting
        :param bool bNowrite: Flag, if we should not immediately write the the setting
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

        for uSettingName in self.oObject.dSettings:
            oSetting:cBaseSettings = self.oObject.dSettings[uSettingName]
            if oSetting.uConfigName == uSectionName:
                oSetting.aIniSettings[uVarName] = uVarValue
                break

    def WriteDefinitionConfig(self, *,uSectionName:str, dSettings:Dict[str,str]) -> None:
        """
        writes all vars given in a dictionary to the config file

        :param string uSectionName: The name of the section
        :param dict dSettings: A dict of all settings to write
        """

        for uKey in dSettings:
            self.WriteDefinitionConfigPar(uSectionName=uSectionName, uVarName=uKey, uVarValue=dSettings[uKey], bNowrite=True)
        self.oConfigParser.write()

    def CreateSectionsJSONString(self) -> str:
        """
        Creates a list of all sections, suitable for the configuration JSON list

        :return: a string representing the section list
        """

        self.GetSectionList()
        uSettingsJSON:str       = u''
        uValueString:str        = u''
        for uSection in self.aSections:
            uValueString+=u'\"'+uSection+u'\",'
        uValueString = uValueString[:len(uValueString)-1]
        uSettingsJSON+=uValueString
        return uSettingsJSON

    def GetSectionList(self) -> None:
        """
        Gets a list of all sections in an ini files
        Will be stored directly in the config objects (aSections)
        :return: None
        """
        self.aSections = self.oConfigParser.sections()
        if len(self.aSections)==0:
            self.CreateSection(uSectionName = self.uDefaultConfigName)
            self.aSections = self.oConfigParser.sections()
        return None


    def ConfigureKivySettings(self, *,oKivySetting:KivySettings,uConfig:str="") -> KivySettings:
        """
        Create the JSON string for all sections and applies it to a kivy settings object
        Discover settings are excluded

        :param setting oKivySetting:
        :param str uConfig: If we want a specific section, this is the name to provide
        :return: The KivySetting object
        """

        oSetting: cBaseSettings
        bFoundSetting:bool = False
        RegisterSettingTypes(oKivySetting)
        self.GetSectionList()
        SetVar(uVarName=u'SettingSectionList', oVarValue=self.CreateSectionsJSONString())

        if self.uType=="interface":
            # The Codeset List could be applied as a orca var, so set it to the list
            SetVar(uVarName=u'InterfaceCodesetList', oVarValue=self.oObject.CreateCodesetListJSONString())

        for uSection in self.aSections:
            if uConfig=="" or uConfig==uSection:
                # the Section list should be applied as an orca var
                SetVar(uVarName=u'ObjectConfigSection', oVarValue=uSection)
                # Let create a new temporary cSetting object to not harm the existing ones
                oSetting = self.oObject.GetNewSettingObject()
                # Read the ini file for this section
                oSetting.ReadConfigFromIniFile(uConfigName=uSection)
                # Create the setting string
                dSettingsJSON:Dict[str,Dict] = self.CreateSettingJsonCombined(oSetting=oSetting, bIncludeDiscoverSettings=False)
                uSettingsJSON = SettingDictToString(dSettingList=dSettingsJSON)
                uSettingsJSON = ReplaceVars(uSettingsJSON)

                if uSettingsJSON != u'[]':
                    bFoundSetting = True
                    # add the jSon to the Kivy Setting
                    oKivySetting.add_json_panel(uSection, self.oConfigParser, data=uSettingsJSON)

        # if there is nothing to configure, then return
        if not bFoundSetting:
            if self.uType == "interface":
                Globals.oNotifications.SendNotification(uNotification='closesetting_interface')
            else:
                 Globals.oNotifications.SendNotification(uNotification='closesetting_script')
            return oKivySetting

        # Adds the action handler
        oKivySetting.bind(on_config_change=self.On_ConfigChange)
        return oKivySetting

    def On_InputDel(self) -> None:
        """ User pressed the del configuration button """
        self.oConfigParser.remove_section(self.uCurrentSection)
        self.oConfigParser.write()
        self.ShowSettings()

    def On_InputRen(self, uInput:str) -> None:
        """ User pressed the rename configuration button """
        if uInput == u'':
            return
        if self.oConfigParser.has_section(uInput):
            return
        self.oConfigParser._sections[uInput] = self.oConfigParser._sections[self.uCurrentSection]
        self.oConfigParser._sections.pop(self.uCurrentSection)
        self.oConfigParser.write()
        self.ShowSettings()

    def On_InputAdd(self, uInput:str) -> None:
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

    def On_ConfigChange(self, oSettings:KivySettings, oConfig:KivyConfigParser, uSection:str, uKey:str, uValue:str):
        """ reacts, if user changes a setting """
        if uKey == u'configchangebuttons':
            self.uCurrentSection = uSection
            if uValue == u'button_add':
                SetVar(uVarName=u'SCRIPTINPUT', oVarValue=u'DEVICE_dummy')
                self.oInputKeyboard = ShowKeyBoard(uDestVar=u'SCRIPTINPUT', oFktNotify=self.On_InputAdd)
            if uValue == u'button_delete':
                ShowQuestionPopUp(uTitle=u'$lvar(5003)', uMessage=u'$lvar(5044)', fktYes=self.On_InputDel, uStringYes=u'$lvar(5001)', uStringNo=u'$lvar(5002)')
            if uValue == u'button_rename':
                SetVar(uVarName=u'SCRIPTINPUT', oVarValue=uSection)
                self.oInputKeyboard = ShowKeyBoard(uDestVar=u'SCRIPTINPUT', oFktNotify=self.On_InputRen)
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

    def ShowSettings(self) -> None:
        """ Shows the settings page """
        Globals._app_settings = None
        Globals.oApp.create_settings()

        Globals.oTheScreen.AddActionToQueue(aActions=[{'string': 'showpage Page_Settings'},
                                                      {'string': 'updatewidget Settings@Page_Settings'}])

    # noinspection PyMethodMayBeStatic
    def GetSettingParFromVar2(self,*, uObjectName:str, uConfigName:str, uSettingParName:str) -> str:
        """
        Gets a Value for a setting parameter from a setting or script
        The Orca vars for the parameter are automatically set in the c"Object"MonitoredSettings class

        :param uObjectName: The name of script or interface to use
        :param uConfigName: The name of the Config
        :param uSettingParName: The name of the parameter
        :return: The value of the parameter
        """

        return GetVar(uVarName="CONFIG_" + uSettingParName.upper(), uContext=uObjectName + u'/' + uConfigName)

    def CreateSettingJsonCombined(self, **kwargs) -> Dict[str,Dict]:
        """
        Creates a json dict which holds all the setting definitions of
        the core object

        :rtype: dict
        :keyword name: oSetting: an InterFaceSettings Object, needs to be cBaseSettings
        :return: a dict of combined settings
        """

        if len(self.dSettingsCombined)!=0:
            return self.dSettingsCombined
        dRet:Dict[str,Dict] = {}

        for uKey in self.dDefaultSettings:
            if self.dDefaultSettings[uKey]["active"] != "disabled":
                dRet[uKey] = self.dDefaultSettings[uKey]

        dScriptJSON:Dict[str,Dict] = self.oObject.GetConfigJSON()
        for uKey in dScriptJSON:
            dLine:Dict = dScriptJSON[uKey]
            iOrder:int = dLine['order']
            for uKey2 in dRet:
                if dRet[uKey2]['order'] >= iOrder:
                    dRet[uKey2]['order'] += 1
            dRet[uKey] = dLine

        self.dSettingsCombined = dRet
        return dRet

def SettingDictToString(*,dSettingList:Dict[str,Dict]) -> str:
    """
    Converts a dict into a string suitable for the kivy settings object.
    Only enries which are enabled will be shown

    :param dict dSettingList: a JSON dictionary al all settings
    :return: The kivy setting string
    """

    dLine:Dict
    aSubList:List[str]  = list(dSettingList.keys())
    aSubList2:List[str] = sorted(aSubList, key=lambda entry: dSettingList[entry]['order'])

    uResult:str = u"["
    for uKey in aSubList2:
        if dSettingList[uKey]['active'] == 'enabled':
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

