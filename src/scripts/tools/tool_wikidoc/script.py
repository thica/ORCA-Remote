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

import sys
import ORCA.Globals as Globals

sys.path.append(Globals.oScripts.dScriptPathList[u"tool_wikidoc"].string)

from kivy.logger                            import Logger
from ORCA.scripts.Scripts                   import cScriptSettingPlugin
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
from ORCA.Parameter                         import cParameter
from ORCA.Parameter                         import cParserAction
from ORCA.vars.Helpers                      import GetEnvVar
from WikiDoc                                import cWikiDoc

'''
<root>
  <repositorymanager>
    <entry>
      <name>Tool WikiDoc</name>
      <description language='English'>Tool to create the ORCA Wikipedia (internal tool)</description>
      <description language='German'>Tool um das ORCA Wikipedia zu schreiben (internes Tool)</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/tools/tool_wikidoc</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/tool_wikidoc.zip</sourcefile>
          <targetpath>scripts/tools</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/tools/tool_wikidoc/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''



class cScript(cToolsTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-tools_wikidoc
    WikiDoc:TOCTitle:Script Tools WikiDoc
    = Tool to write ORCA Wikipedia =

    This (internal) tool writes the Wikipedia rticles to the ORCA server. (dont try it yourself)

    The following command line arguments / environment vars can be used to initialize the script settings

    --wikiserver: Set the WWW server address for the ORCA Wikipedia (can be passed as ORCAWIKISERVER environment var
    --wikipath: Set the WWW server path for the ORCA Wikipedia (can be passed as ORCAWIKIPATH environment var
    --wikiuser: Set the initialisation username for the ORCA Wikipedia (can be passed as ORCAWIKIUSER environment var
    --wikipassword: Set the initialisation password for the ORCA Wikipedia (can be passed as ORCAWIKIPW environment var

    WikiDoc:End
    """

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript):
            cBaseScriptSettings.__init__(self,oScript)
            # Globals.oParameter values will be added in this script
            self.aScriptIniSettings.uHost               = Globals.oParameter.uWikiServer
            self.aScriptIniSettings.uFTPPath            = Globals.oParameter.uWikiPath
            self.aScriptIniSettings.uUser               = Globals.oParameter.uWikiUser
            self.aScriptIniSettings.uPassword           = Globals.oParameter.uWikiPassword
            self.aScriptIniSettings.uWikiTargetFolder   = Globals.oParameter.uWikiTargetFolder
            self.aScriptIniSettings.uWikiApp            = Globals.oParameter.uWikiApp

    class cScriptParameter(cParameter):
        def AddParameter(self,oParser):
            oParser.add_argument('--wikiserver', default=GetEnvVar('ORCAWIKISERVER', 'www.orca-remote.org'), action=cParserAction, oParameter=self, dest="uWikiServer",help='Set the WWW server address for the ORCA Wikipedia (can be passed as ORCAWIKISERVER environment var)')
            oParser.add_argument('--wikipath', default=GetEnvVar('ORCAWIKIPATH', '/mediawiki/'), action=cParserAction, oParameter=self, dest="uWikiPath", help='Set the WWW server path for the ORCA Wikipedia (can be passed as ORCAWIKIPATH environment var)')
            oParser.add_argument('--wikiuser', default=GetEnvVar('ORCAWIKIUSER'), action=cParserAction, oParameter=self, dest="uWikiUser", help='Set the initialisation username for the ORCA Wikipedia (can be passed as ORCAWIKIUSER environment var)')
            oParser.add_argument('--wikipassword', default=GetEnvVar('ORCAWIKIPW'), action=cParserAction, oParameter=self, dest="uWikiPassword", help='Set the initialisation password for the ORCA Wikipedia (can be passed as ORCAWIKIPW environment var)')
            oParser.add_argument('--wikitargetfolder', default=GetEnvVar('ORCAWIKITARGETFOLDER',Globals.oPathTmp.string), action=cParserAction, oParameter=self, dest="uWikiTargetFolder", help='Sets local folder for the wiki files')
            oParser.add_argument('--wikiapp', default=GetEnvVar('ORCAWIKIAPP',"MEDIAWIKI"), action=cParserAction, oParameter=self, dest="uWikiApp", help='Sets the target for the wiki files (MEDIAWIKI or GITWIKI)')


    def __init__(self):
        cToolsTemplate.__init__(self)
        self.uSubType        = u'WIKI'
        self.uSortOrder      = u'auto'
        self.uSettingSection = u'tools'
        self.uSettingTitle   = u"WikiDoc"
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
        self.oScriptConfig.dDefaultSettings['User']['active']                        = "enabled"
        self.oScriptConfig.dDefaultSettings['Password']['active']                    = "enabled"
        self.oScriptConfig.dDefaultSettings['Host']['active']                        = "enabled"

    def RunScript(self, *args, **kwargs):
        cToolsTemplate.RunScript(self,*args, **kwargs)
        if kwargs.get("caller") == "settings" or kwargs.get("caller") == "action":
            self.WikiDoc(self, *args, **kwargs)

    def WikiDoc(self, *args, **kwargs):
        oSetting                    = self.GetSettingObjectForConfigName(self.uConfigName)
        dArgs                       = {}
        dArgs["Host"]              = kwargs.get("Host",oSetting.aScriptIniSettings.uHost)
        dArgs["WikiPath"]          = kwargs.get("WikiPath",oSetting.aScriptIniSettings.uWikiPath)
        dArgs["User"]              = kwargs.get("WikiUser",oSetting.aScriptIniSettings.uUser)
        dArgs["Password"]          = kwargs.get("WikiPassword",oSetting.aScriptIniSettings.uPassword)
        dArgs["WikiTargetFolder"]  = kwargs.get("WikiTargetFolder",oSetting.aScriptIniSettings.uWikiTargetFolder)
        dArgs["WikiApp"]           = kwargs.get("WikiApp",oSetting.aScriptIniSettings.uWikiApp)

        oWikiDoc                    = cWikiDoc(**dArgs)
        oWikiDoc.Run()
        Logger.debug(u'Wikidoc Finished')

    def Register(self, *args, **kwargs):
        cToolsTemplate.Register(self,*args, **kwargs)
        Globals.oNotifications.RegisterNotification("STARTSCRIPTWIKIDOC", fNotifyFunction=self.WikiDoc,   uDescription="Script WikiDoc")

        oScriptSettingPlugin = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName   = self.uScriptName
        oScriptSettingPlugin.uSettingName  = "ORCA"
        oScriptSettingPlugin.uSettingPage  = "$lvar(572)"
        oScriptSettingPlugin.uSettingTitle = "$lvar(SCRIPT_TOOLS_WIKIDOC_4)"
        oScriptSettingPlugin.aSettingJson  = [u'{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_WIKIDOC_1)","desc": "$lvar(SCRIPT_TOOLS_WIKIDOC_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_WIKIDOC_3)","id":"button_notification_STARTSCRIPTWIKIDOC"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uScriptName,oScriptSettingPlugin=oScriptSettingPlugin)

    def GetConfigJSON(self):
        return {"WikiPath":         {"type": "string", "active": "enabled", "order": 16, "title": "$lvar(SCRIPT_TOOLS_WIKIDOC_5)", "desc": "$lvar(SCRIPT_TOOLS_WIKIDOC_6)","key": "WikiPath", "default":Globals.oParameter.uWikiPath, "section": "$var(ScriptConfigSection)"},
                "WikiTargetFolder": {"type": "string", "active": "enabled", "order": 17, "title": "$lvar(SCRIPT_TOOLS_WIKIDOC_7)", "desc": "$lvar(SCRIPT_TOOLS_WIKIDOC_8)", "key": "WikiTargetFolder", "default": Globals.oPathTmp.string, "section": "$var(ScriptConfigSection)"}
                }
