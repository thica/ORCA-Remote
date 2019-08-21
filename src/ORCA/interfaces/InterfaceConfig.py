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

from ORCA.BaseConfig                    import cBaseConfig
import ORCA.Globals as Globals


class cInterFaceConfig(cBaseConfig):
    """ Class to manage the initialisation/configuration and access toe the settings of an Interface settings objects

    """

    def __init__(self, oInterFace):

        super(cInterFaceConfig,self).__init__(oInterFace)

        self.uType                          = "interface"
        self.uWidgetName                    = "Interfacesettings"
        self.uDefaultConfigName             = u'DEVICE_DEFAULT'
        self.dDefaultSettings               = {"SettingTitle":               {"active": "enabled",  "order": 0,   "type": "title" ,         "title": "$lvar(560)"},
                                               "Host":                       {"active": "disabled", "order": 1,   "type": "string",         "title": "$lvar(6004)", "desc": "$lvar(6005)", "section": "$var(ObjectConfigSection)", "key": "Host",                        "default": "192.168.1.2"},
                                               "Port":                       {"active": "disabled", "order": 2,   "type": "string",         "title": "$lvar(6002)", "desc": "$lvar(6003)", "section": "$var(ObjectConfigSection)", "key": "Port",                        "default": "80"},
                                               "User":                       {"active": "disabled", "order": 3,   "type": "string",         "title": "$lvar(6006)", "desc": "$lvar(6007)", "section": "$var(ObjectConfigSection)", "key": "User",                        "default": "root"},
                                               "Password":                   {"active": "disabled", "order": 4,   "type": "string",         "title": "$lvar(6008)", "desc": "$lvar(6009)", "section": "$var(ObjectConfigSection)", "key": "Password",                    "default": ""},
                                               "FNCodeset":                  {"active": "disabled", "order": 5,   "type": "scrolloptions",  "title": "$lvar(6000)", "desc": "$lvar(6001)", "section": "$var(ObjectConfigSection)", "key": "FNCodeset",                   "default": "Select",  "options": ["$var(InterfaceCodesetList)"]},
                                               "ParseResult":                {"active": "disabled", "order": 6,   "type": "scrolloptions",  "title": "$lvar(6027)", "desc": "$lvar(6028)", "section": "$var(ObjectConfigSection)", "key": "ParseResult",                 "default": "store",    "options": ["no","tokenize","store","json","dict","xml"]},
                                               "TokenizeString":             {"active": "disabled", "order": 7,   "type": "string",         "title": "$lvar(6029)", "desc": "$lvar(6030)", "section": "$var(ObjectConfigSection)", "key": "TokenizeString",              "default": ":"},
                                               "TimeOut":                    {"active": "disabled", "order": 8,   "type": "numericfloat",   "title": "$lvar(6019)", "desc": "$lvar(6020)", "section": "$var(ObjectConfigSection)", "key": "TimeOut",                     "default": "1.0"},
                                               "TimeToClose":                {"active": "disabled", "order": 9,   "type": "numeric",        "title": "$lvar(6010)", "desc": "$lvar(6011)", "section": "$var(ObjectConfigSection)", "key": "TimeToClose",                 "default": "10"},
                                               "DisableInterFaceOnError":    {"active": "disabled", "order": 10,  "type": "bool",           "title": "$lvar(529)",  "desc": "$lvar(530)",  "section": "$var(ObjectConfigSection)", "key": "DisableInterFaceOnError",     "default": "0"},
                                               "DisconnectInterFaceOnSleep": {"active": "disabled", "order": 11,  "type": "bool",           "title": "$lvar(533)",  "desc": "$lvar(534)",  "section": "$var(ObjectConfigSection)", "key": "DisconnectInterFaceOnSleep",  "default": "1"},
                                               "DiscoverSettingButton":      {"active": "disabled", "order": 12,  "type": "buttons",        "title": "$lvar(6033)", "desc": "$lvar(6034)", "section": "$var(ObjectConfigSection)", "key": "DiscoverSettings",            "buttons": [{"title": "Discover Settings", "id": "button_discover"}]},
                                               "ConfigChangeButtons":        {"active": "enabled",  "order": 999, "type": "buttons",        "title": "$lvar(565)",  "desc": "$lvar(566)",  "section": "$var(ObjectConfigSection)", "key": "configchangebuttons",         "buttons": [{"title": "$lvar(569)", "id": "button_add"}, {"title": "$lvar(570)", "id": "button_delete"}, {"title": "$lvar(571)", "id": "button_rename"}]}
                                              }


        self.aDiscoverScriptList            = None
        self.dGenericDiscoverSettings     = { "DiscoverScriptName":          {"active": "hidden",   "order": 100,  "scriptsection": "$lvar(539)", "type": "scrolloptions",  "title": "$lvar(6035)", "desc": "$lvar(6036)", "section": "$var(ObjectConfigSection)", "key": "DiscoverScriptName",          "default": "", "options":["$var(DISCOVERSCRIPTLIST)"]},
                                              "SaveDiscoveredIP":            {"active": "hidden",   "order": 101,  "scriptsection": "$lvar(539)", "type": "bool",           "title": "$lvar(6031)", "desc": "$lvar(6032)", "section": "$var(ObjectConfigSection)", "key": "SaveDiscoveredIP",            "default": "1"},
                                              "OldDiscoveredIP":             {"active": "hidden",   "order": 102,  "scriptsection": "$lvar(539)", "type": "string",         "title": "$lvar(6021)", "desc": "$lvar(6022)", "section": "$var(ObjectConfigSection)", "key": "OldDiscoveredIP",             "default": ""},
                                              "CheckDiscoverButton":         {"active": "disabled", "order": 103,  "scriptsection": "$lvar(539)", "type": "buttons",        "title": "Check Discover", "desc": "$lvar(6034)", "section": "$var(ObjectConfigSection)", "key": "CheckDiscover", "buttons": [{"title": "Check Discover", "id": "button_checkdiscover"}]},
                                              }


    def On_ConfigChange(self, oSettings, oConfig, uSection, uKey, uValue):
        """
        reacts, if user changes a setting

        :param setting oSettings: The kivy settings object
        :param ConfigParser oConfig: The Kivy config parser
        :param string uSection: The section of the change
        :param string uKey: The key name
        :param string uValue: The value
        """

        super(cInterFaceConfig,self).On_ConfigChange(oSettings, oConfig, uSection, uKey, uValue)

        if uKey == u'DiscoverSettings':
            Globals.oTheScreen.uConfigToConfig = uSection
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_InterfaceSettingsDiscover')
        elif uKey == u'FNCodeset':
            oSetting = self.oObject.GetSettingObjectForConfigName(uConfigName=uSection)
            oSetting.aIniSettings[uKey] = uValue
            oSetting.ReadCodeset()

    def GetSettingParFromVar(self, uLink):
        """
        Returns a setting var of a an other interface or config
        The Interfca must allready be initalized
        syntax should be: linked:interfacename:configname:varname

        :rtype: string
        :param string uLink: The link: syntax should be: linked:interfacename:configname:varname
        :return: The Value of the linked setting, empty string, if not found
        """

        aLinks = uLink.split(':')
        if len(aLinks) == 4:
            uInterFaceName  = aLinks[1]
            uConfigName     = aLinks[2]
            uSettingParName = aLinks[3]
            Globals.oInterFaces.LoadInterface(uInterFaceName)
            oInterface = Globals.oInterFaces.GetInterface(uInterFaceName)
            oSetting = oInterface.GetSettingObjectForConfigName(uConfigName=uConfigName)
            oSetting.Discover()
            return self.GetSettingParFromVar2(uObjectName=uInterFaceName, uConfigName=uConfigName, uSettingParName=uSettingParName)
        return ""

    def CreateSettingJsonCombined(self, **kwargs):
        """
        Creates a json dict which holds all the setting definitions of
        the core interface plus the settings from the discover script (if requested)

        :rtype: dict
        :keyword name: oSetting: an IterFaceSettins Object, needs to be cBaseInterFaceSettings
        :keyword name: bIncludeDiscoverSettings: If we want to include the discover settings, needs to be bools
        :return: a dict of combined settings
        """

        oSetting                  = kwargs.get("oSetting")
        bIncludeDiscoverSettings  = kwargs.get("bIncludeDiscoverSettings",True)
        dRet = super(cInterFaceConfig,self).CreateSettingJsonCombined(**kwargs)

        if 'DiscoverSettingButton' in dRet and bIncludeDiscoverSettings:
            dRet.update(self.dGenericDiscoverSettings)
            if self.aDiscoverScriptList is None:
                self.aDiscoverScriptList = Globals.oScripts.GetScriptListForScriptType("DEVICE_DISCOVER")
            iLastOrder = 200
            for uDiscoverScriptName in self.aDiscoverScriptList:
                oScript = Globals.oScripts.LoadScript(uDiscoverScriptName)
                dScriptJSONSettings = oScript.cScript.GetConfigJSONforParameters(oSetting.aIniSettings)
                iMax = 0
                for uKey in dScriptJSONSettings:
                    uTempKey                         = uDiscoverScriptName + "_" + uKey
                    dRet[uTempKey]                   = dScriptJSONSettings[uKey]
                    dRet[uTempKey]['key']            = uDiscoverScriptName.upper() + "_" + dScriptJSONSettings[uKey]['key']
                    dRet[uTempKey]['scriptsection']  = uDiscoverScriptName
                    dRet[uTempKey]['active']         = 'hidden'
                    iOrder                           = dRet[uTempKey]['order']
                    iMax                             = max(iMax,iOrder)
                    dRet[uTempKey]['order']          = iOrder+iLastOrder

                iLastOrder+=iMax
        self.dSettingsCombined = dRet
        return dRet

