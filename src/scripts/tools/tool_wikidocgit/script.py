# -*- coding: utf-8 -*-
#
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

from __future__                             import annotations
from typing                                 import Dict
import argparse
from kivy.logger                            import Logger
from ORCA.scripts.Scripts                   import cScriptSettingPlugin
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
from ORCA.Parameter                         import cParameter
from ORCA.Parameter                         import cParserAction
from ORCA.vars.Helpers                      import GetEnvVar
import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Tool WikiDoc Git</name>
      <description language='English'>Tool to create the ORCA Wikipedia for GIT (internal Tool)</description>
      <description language='German'>Tool um das ORCA Wikipedia zu schreiben für GIT (internes Tool)</description>
      <author>Carsten Thielepape</author>
      <version>5.0.0</version>
      <minorcaversion>5.0.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/tools/tool_wikidocgit</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/tool_wikidocgit.zip</sourcefile>
          <targetpath>scripts/tools</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>Tool WikiDoc</name>
        </dependency>
      </dependencies>
    </entry>
  </repositorymanager>
</root>
'''


class cScript(cToolsTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-tools_wikidoc_git
    WikiDoc:TOCTitle:Script Tools WikiDoc for GIT
    = Tool to write ORCA Wikipedia for GIT=

    This (internal) tool writes the Wikipedia rticles to the ORCA GIT Wiki. (dont try it yourself)

    The following command line arguments / environment vars can be used to initialize the script settings

    --wikiapp: Set the WWW server address for the ORCA Wikipedia (can be passed as ORCAWIKISERVER environment var
    --wikigittargetfolder: Output Folder for the pages files

    WikiDoc:End
    """

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cScript):
            super().__init__(oScript)
            self.aIniSettings.uHost                   = oScript.oEnvParameter.uWikiGitServer
            self.aIniSettings.uWikiGitTargetFolder    = oScript.oEnvParameter.uWikiGitTargetFolder
            self.aIniSettings.uWikiGitApp             = oScript.oEnvParameter.uWikiGitApp

    class cScriptParameter(cParameter):
        def AddParameter(self,oParser:argparse.ArgumentParser) -> None:
            oParser.add_argument('--wikigitserver',       default=GetEnvVar('ORCAWIKIGITSERVER',     'https://github.com/thica/ORCA-Remote/blob/master'), action=cParserAction, oParameter=self, dest="uWikiGitServer",       help='Set the Git Path to the ORCA Images (can be passed as ORCAGITWIKISERVER environment var)')
            oParser.add_argument('--wikigittargetfolder', default=GetEnvVar('ORCAWIKIGITTARGETFOLDER',Globals.oPathTmp.string),                           action=cParserAction, oParameter=self, dest="uWikiGitTargetFolder", help='Sets local folder for the wiki files')
            oParser.add_argument('--wikigitapp',          default=GetEnvVar('ORCAWIKIGITAPP',"GITWIKI"),                                                  action=cParserAction, oParameter=self, dest="uWikiGitApp",          help='Sets the target for the wiki files (MEDIAWIKI or GITWIKI)')

    def __init__(self):
        super().__init__()
        self.uSubType        = u'WIKI'
        self.uSortOrder      = u'auto'
        self.uSettingSection = u'tools'
        self.uSettingTitle   = u"WikiDoc GIT"
        self.oEnvParameter:cParameter   = self.cScriptParameter()

    def Init(self,uObjectName:str,uScriptFile:str=u'') -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param str uScriptFile: The file of the script (to be passed to all scripts)
        """

        super().Init(uObjectName= uObjectName, oFnObject=uScriptFile)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"

    def RunScript(self, *args, **kwargs) -> None:
        super().RunScript(*args, **kwargs)
        if kwargs.get("caller") == "settings" or kwargs.get("caller") == "action":
            self.WikiDoc(self, *args, **kwargs)

    # noinspection PyUnusedLocal
    def WikiDoc(self, *args, **kwargs):
        oSetting                   = self.GetSettingObjectForConfigName(uConfigName=self.uConfigName)
        dArgs                      = {"Host":             kwargs.get("Host", oSetting.aIniSettings.uHost),
                                      "WikiTargetFolder": kwargs.get("WikiGitTargetFolder", oSetting.aIniSettings.uWikiGitTargetFolder),
                                      "WikiApp":          kwargs.get("WikiGitApp", oSetting.aIniSettings.uWikiGitApp)}
        Globals.oNotifications.SendNotification(uNotification="STARTSCRIPTWIKIDOC",**dArgs)
        Logger.debug(u'WikidocGit Finished')
        return {}

    def Register(self, *args, **kwargs) -> Dict:
        super().Register(*args, **kwargs)
        Globals.oNotifications.RegisterNotification(uNotification="STARTSCRIPTWIKIDOCGIT", fNotifyFunction=self.WikiDoc,   uDescription="Script WikiDoc Git")

        oScriptSettingPlugin = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName   = self.uObjectName
        oScriptSettingPlugin.uSettingName  = "ORCA"
        oScriptSettingPlugin.uSettingPage  = "$lvar(572)"
        oScriptSettingPlugin.uSettingTitle = "$lvar(SCRIPT_TOOLS_GITWIKIDOC_4)"
        oScriptSettingPlugin.aSettingJson  = [u'{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_GITWIKIDOC_1)","desc": "$lvar(SCRIPT_TOOLS_GITWIKIDOC_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_GITWIKIDOC_3)","id":"button_notification_STARTSCRIPTWIKIDOCGIT"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uObjectName,oScriptSettingPlugin=oScriptSettingPlugin)
        return {}

    def GetConfigJSON(self) -> Dict:
        return {"WikiTargetFolder": {"type": "string", "active": "enabled", "order": 17, "title": "$lvar(SCRIPT_TOOLS_WIKIDOC_7)", "desc": "$lvar(SCRIPT_TOOLS_WIKIDOC_8)", "key": "WikiTargetFolder", "default": Globals.oPathTmp.string,      "section": "$var(ObjectConfigSection)"}
               }
