# -*- coding: utf-8 -*-
#
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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
from __future__ import annotations
from typing                                 import Dict
from typing                                 import TYPE_CHECKING

import sys
import argparse
from ORCA.Globals import Globals

sys.path.append(str(Globals.oScripts.dScriptPathList['tool_wiki2rst']))

from kivy.logger                            import Logger
from ORCA.scripts.Scripts                   import cScriptSettingPlugin
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
from ORCA.Parameter                         import cParameter
from ORCA.Parameter                         import cParserAction
from ORCA.vars.Helpers                      import GetEnvVar


if TYPE_CHECKING:
    from scripts.tools.tool_wiki2rst.RstDoc import cRstDoc
else:
    # noinspection PyUnresolvedReferences
    from RstDoc                            import cRstDoc



class cScript(cToolsTemplate):

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cScript):
            """
            :param oScript: cScript
            """
            super().__init__(oScript)

        def WriteConfigToIniFile(self) -> None:
            # this avoids, that the Ini file will be changed from given command line / environment settings
            # nevertheless, once changes have been writen to the ini file, they will be used , regardless of any env / commandline parameter
            pass

    class cScriptParameter(cParameter):
        def AddParameter(self,oParser:argparse.ArgumentParser):
            pass
    def __init__(self):
        super().__init__()
        self.uSubType                   = 'RST'
        self.uSortOrder                 = 'auto'
        self.uSettingSection            = 'tools'
        self.uSettingTitle              = 'RstDoc'
        self.oEnvParameter:cParameter   = self.cScriptParameter()

    def Init(self,uObjectName:str,uScriptFile:str='') -> Dict:
        """
        Init function for the script

        :param string uObjectName: The name of the script (to be passed to all scripts)
        :param uScriptFile: The file of the script (to be passed to all scripts)
        """

        super().Init(uObjectName= uObjectName,oFnObject= uScriptFile)
        return {}

    def RunScript(self, *args, **kwargs) -> None:
        super().RunScript(*args, **kwargs)
        if kwargs.get('caller') == 'settings' or kwargs.get('caller') == 'action':
            self.RstDoc(self, *args, **kwargs)

    # noinspection PyUnusedLocal
    def RstDoc(self, *args, **kwargs) -> None:
        oSetting                    = self.GetSettingObjectForConfigName(uConfigName=self.uConfigName)
        dArgs                       = {'Host':              kwargs.get('Host',              oSetting.aIniSettings.uHost),
                                       'WikiPath':          kwargs.get('WikiPath',          oSetting.aIniSettings.uWikiPath),
                                       'User':              kwargs.get('WikiUser',          oSetting.aIniSettings.uUser),
                                       'Password':          kwargs.get('WikiPassword',      oSetting.aIniSettings.uPassword),
                                       'WikiTargetFolder':  kwargs.get('WikiTargetFolder',  oSetting.aIniSettings.uWikiTargetFolder),
                                       'WikiApp':           kwargs.get('WikiApp',           oSetting.aIniSettings.uWikiApp)}

        oRstDoc                    = cRstDoc(**dArgs)
        oRstDoc.Run()
        Logger.debug('Rstdoc Finished')

    def Register(self, *args, **kwargs) -> None:
        super().Register(*args, **kwargs)
        Globals.oNotifications.RegisterNotification(uNotification='STARTSCRIPTRSTDOC', fNotifyFunction=self.RstDoc,   uDescription="Script RstDoc")

        oScriptSettingPlugin:cScriptSettingPlugin   = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName            = self.uObjectName
        oScriptSettingPlugin.uSettingName           = 'ORCA'
        oScriptSettingPlugin.uSettingPage           = '$lvar(572)'
        oScriptSettingPlugin.uSettingTitle          = 'RST Convert'
        oScriptSettingPlugin.aSettingJson           = ['{"type": "buttons","title": "RST Konvert","desc": "$lvar(SCRIPT_TOOLS_WIKIDOC_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"Create RST Test",'
                                                       '"id":"button_notification_STARTSCRIPTRSTDOC"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uObjectName,oScriptSettingPlugin=oScriptSettingPlugin)

    def GetConfigJSON(self) -> Dict:
        return {'WikiPath':         {'type': 'string', 'active': 'enabled', 'order': 16, 'title': '$lvar(SCRIPT_TOOLS_WIKIDOC_5)', 'desc': '$lvar(SCRIPT_TOOLS_WIKIDOC_6)','key': 'WikiPath', 'default':self.oEnvParameter.uWikiPath, 'section': '$var(ObjectConfigSection)'},
                'WikiTargetFolder': {'type': 'string', 'active': 'enabled', 'order': 17, 'title': '$lvar(SCRIPT_TOOLS_WIKIDOC_7)', 'desc': '$lvar(SCRIPT_TOOLS_WIKIDOC_8)', 'key': 'WikiTargetFolder', 'default': str(Globals.oPathTmp), 'section': '$var(ObjectConfigSection)'}
                }
