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


class cScriptConfig(cBaseConfig):
    """
    Class to manage the initialisation/configuration and access the the settings of an Script settings objects
    """

    def __init__(self, oScript):

        super(cScriptConfig,self).__init__(oScript)

        self.uType                          = "script"
        self.uWidgetName                    = "Scriptsettings"

        self.uDefaultConfigName             = u'SCRIPTDEFAULT'
        self.aDiscoverScriptList            = None
        self.dDefaultSettings               = {"SettingTitle":               {"active": "enabled",  "order": 0,    "type": "title" ,       "title": "$lvar(560)"},
                                               "TimeOut":                    {"active": "disabled", "order": 1,    "type": "numericfloat", "title": "$lvar(6019)", "desc": "$lvar(6020)", "section": "$var(ObjectConfigSection)", "key": "TimeOut", "default": "1.0"},
                                               "Host":                       {"active": "disabled", "order": 5,    "type": "string",       "title": "$lvar(6004)", "desc": "$lvar(6005)", "section": "$var(ObjectConfigSection)", "key": "Host", "default": "192.168.1.2"},
                                               "Port":                       {"active": "disabled", "order": 6,    "type": "string",       "title": "$lvar(6002)", "desc": "$lvar(6003)", "section": "$var(ObjectConfigSection)", "key": "Port", "default": "80"},
                                               "User":                       {"active": "disabled", "order": 7,    "type": "string",       "title": "$lvar(6006)", "desc": "$lvar(6007)", "section": "$var(ObjectConfigSection)", "key": "User", "default": ""},
                                               "Password":                   {"active": "disabled", "order": 8,    "type": "string",       "title": "$lvar(6008)", "desc": "$lvar(6009)", "section": "$var(ObjectConfigSection)", "key": "Password", "default": ""},
                                               "ConfigChangeButtons":        {"active": "disabled", "order": 999,  "type": "buttons",      "title": "$lvar(565)",  "desc": "$lvar(566)",  "section": "$var(ObjectConfigSection)", "key": "configchangebuttons",         "buttons": [{"title": "$lvar(569)", "id": "button_add"}, {"title": "$lvar(570)", "id": "button_delete"}, {"title": "$lvar(571)", "id": "button_rename"}]},
                                               }




