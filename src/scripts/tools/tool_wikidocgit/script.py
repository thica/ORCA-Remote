# -*- coding: utf-8 -*-
#
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


import ORCA.Globals as Globals

from kivy.logger                            import Logger
from ORCA.scripts.Scripts                   import cScriptSettingPlugin
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
from ORCA.Parameter                         import cParameter
from ORCA.Parameter                         import cParserAction
from ORCA.vars.Helpers                      import GetEnvVar

'''
<root>
  <repositorymanager>
    <entry>
      <name>Tool WikiDoc Git</name>
      <description language='English'>Tool to create the ORCA Wikipedia for GIT (internal Tool)</description>
      <description language='German'>Tool um das ORCA Wikipedia zu schreiben für GIT (internes Tool)</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/tools/tool_wikidocgit</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/tool_wikidocgit.zip</sourcefile>
          <targetpath>scripts/tools</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/tools/tool_wikidocgit/script.pyc</file>
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
    --wikipath: Set the WWW server path for the ORCA Wikipedia (can be passed as ORCAWIKIPATH environment var
    --wikiuser: Set the initialisation username for the ORCA Wikipedia (can be passed as ORCAWIKIUSER environment var
    --wikipassword: Set the initialisation password for the ORCA Wikipedia (can be passed as ORCAWIKIPW environment var

    WikiDoc:End
    """

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aScriptIniSettings.uHost                   = Globals.oParameter.uWikiGitServer
            self.aScriptIniSettings.uWikiGitTargetFolder    = Globals.oParameter.uWikiGitTargetFolder
            self.aScriptIniSettings.uWikiGitApp             = Globals.oParameter.uWikiGitApp

    class cScriptParameter(cParameter):
        def AddParameter(self,oParser):
            oParser.add_argument('--wikigitserver',       default=GetEnvVar('ORCAWIKIGITSERVER', 'https://github.com/thica/ORCA-Remote/blob/master'), action=cParserAction, oParameter=self, dest="uWikiGitServer",help='Set the Git Path to the ORCA Images (can be passed as ORCAGITWIKISERVER environment var)')
            oParser.add_argument('--wikigittargetfolder', default=GetEnvVar('ORCAWIKIGITTARGETFOLDER',Globals.oPathTmp.string), action=cParserAction, oParameter=self, dest="uWikiGitTargetFolder", help='Sets local folder for the wiki files')
            oParser.add_argument('--wikigitapp',          default=GetEnvVar('ORCAWIKIGITAPP',"GITWIKI"), action=cParserAction, oParameter=self, dest="uWikiGitApp", help='Sets the target for the wiki files (MEDIAWIKI or GITWIKI)')

    def __init__(self):
        cToolsTemplate.__init__(self)
        self.uSubType        = u'WIKI'
        self.uSortOrder      = u'auto'
        self.uSettingSection = u'tools'
        self.uSettingTitle   = u"WikiDoc GIT"
        oParameter      = self.cScriptParameter()
        for uKey in oParameter:
            Globals.oParameter[uKey]= oParameter[uKey]

    def Init(self,uScriptName,uScriptFile=u''):
        """
        Init function for the script

        :param string uScriptName: The name of the script (to be passed to all scripts)
        :param uScriptFile: The file of the script (to be passed to all scripts)
        """

        cToolsTemplate.Init(self, uScriptName, uScriptFile)
        self.oScriptConfig.dDefaultSettings['Host']['active']                        = "enabled"

    def RunScript(self, *args, **kwargs):
        cToolsTemplate.RunScript(self,*args, **kwargs)
        if kwargs.get("caller") == "settings" or kwargs.get("caller") == "action":
            self.WikiDoc(self, *args, **kwargs)

    def WikiDoc(self, *args, **kwargs):
        oSetting                    = self.GetSettingObjectForConfigName(self.uConfigName)
        dArgs                       = {}

        dArgs["Host"]              = kwargs.get("Host",oSetting.aScriptIniSettings.uHost)
        dArgs["WikiTargetFolder"]  = kwargs.get("WikiGitTargetFolder",oSetting.aScriptIniSettings.uWikiGitTargetFolder)
        dArgs["WikiApp"]           = kwargs.get("WikiGitApp",oSetting.aScriptIniSettings.uWikiGitApp)
        Globals.oNotifications.SendNotification("STARTSCRIPTWIKIDOC",**dArgs)

        Logger.debug(u'WikidocGit Finished')

    def Register(self, *args, **kwargs):
        cToolsTemplate.Register(self,*args, **kwargs)
        Globals.oNotifications.RegisterNotification("STARTSCRIPTWIKIDOCGIT", fNotifyFunction=self.WikiDoc,   uDescription="Script WikiDoc Git")

        oScriptSettingPlugin = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName   = self.uScriptName
        oScriptSettingPlugin.uSettingName  = "ORCA"
        oScriptSettingPlugin.uSettingPage  = "$lvar(572)"
        oScriptSettingPlugin.uSettingTitle = "$lvar(SCRIPT_TOOLS_GITWIKIDOC_4)"
        oScriptSettingPlugin.aSettingJson  = [u'{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_GITWIKIDOC_1)","desc": "$lvar(SCRIPT_TOOLS_GITWIKIDOC_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_GITWIKIDOC_3)","id":"button_notification_STARTSCRIPTWIKIDOCGIT"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uScriptName,oScriptSettingPlugin=oScriptSettingPlugin)

    def GetConfigJSON(self):
        return {"WikiPath":         {"type": "string", "active": "enabled", "order": 16, "title": "$lvar(SCRIPT_TOOLS_WIKIDOC_5)", "desc": "$lvar(SCRIPT_TOOLS_WIKIDOC_6)","key": "WikiPath", "default":Globals.oParameter.uWikiPath, "section": "$var(ScriptConfigSection)"},
                "WikiTargetFolder": {"type": "string", "active": "enabled", "order": 17, "title": "$lvar(SCRIPT_TOOLS_WIKIDOC_7)", "desc": "$lvar(SCRIPT_TOOLS_WIKIDOC_8)", "key": "WikiTargetFolder", "default": Globals.oPathTmp.string, "section": "$var(ScriptConfigSection)"}
                }
