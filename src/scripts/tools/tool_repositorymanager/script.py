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

sys.path.append(Globals.oScripts.dScriptPathList[u"tool_repositorymanager"].string)

from ORCA.scripts.Scripts                   import cScriptSettingPlugin
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.vars.Access                       import SetVar
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.utils.Path                        import cPath
from ORCA.Parameter                         import cParameter
from ORCA.Parameter                         import cParserAction
from ORCA.vars.Helpers                      import GetEnvVar
from RepManager                             import RepositoryManager
from RepManager                             import CreateRepVarArray

'''
<root>
  <repositorymanager>
    <entry>
      <name>Tool Repositorymanager</name>
      <description language='English'>Tool to write the repository (internal tool)</description>
      <description language='German'>Tool um ein repository zu schreiben (internes Tool)</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/tools/tool_repositorymanager</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/tool_repositorymanager.zip</sourcefile>
          <targetpath>scripts/tools</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/tools/tool_repositorymanager/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''



class cScript(cToolsTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-tools_repositorymanager
    WikiDoc:TOCTitle:Script Tools Repository Manager
    = Tool to write the repository =

    This (internal) tool writes the repository to the ORCA server. (dont try it yourself)
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |}</div>

    WikiDoc:End
    """

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aScriptIniSettings.uHost           = Globals.oParameter.uFTPServer
            self.aScriptIniSettings.uUser           = Globals.oParameter.uFTPUser
            self.aScriptIniSettings.uPassword       = Globals.oParameter.uFTPPassword
            self.aScriptIniSettings.uFTPPath        = Globals.oParameter.uFTPServerPath
            self.aScriptIniSettings.uPathRepSource  = Globals.oParameter.oPathRepSource
            self.aScriptIniSettings.uWWWServerPath  = Globals.oParameter.uWWWServerPath
            self.aScriptIniSettings.bFTPSSL         = ToBool(Globals.oParameter.uFTPSSL)

            uVersion = str(Globals.iVersion)
            self.aScriptIniSettings.uWWWServerPath  = self.aScriptIniSettings.uWWWServerPath.replace(uVersion,"$var(REPVERSION)")
            self.aScriptIniSettings.uFTPPath        = self.aScriptIniSettings.uFTPPath.replace(uVersion,"$var(REPVERSION)")

    class cScriptParameter(cParameter):
        def AddParameter(self,oParser):
            oParser.add_argument('--ftpserver', default=GetEnvVar('ORCAFTPSERVER'), action=cParserAction, oParameter=self, dest="uFTPServer", help='Set the FTP Server address for the repository manager (can be passed as ORCAFTPSERVER environment var)')
            oParser.add_argument('--ftpserverpath', default=GetEnvVar('ORCAFTPSERVERPATH'), action=cParserAction, oParameter=self, dest="uFTPServerPath", help='Set the FTP Server path for the repository manager (can be passed as ORCAFTPSERVERPATH environment var)')
            oParser.add_argument('--ftpuser', default=GetEnvVar('ORCAFTPUSER'), action=cParserAction, oParameter=self, dest="uFTPUser", help='Set the username for the FTP Server for the repository manager (can be passed as ORCAFTPUSER environment var)')
            oParser.add_argument('--ftppassword', default=GetEnvVar('ORCAFTPPW'), action=cParserAction, oParameter=self, dest="uFTPPassword", help='Set the password for the FTP Server for the repository manager (can be passed as ORCAFTPPW environment var)')
            oParser.add_argument('--ftpssl', default=GetEnvVar('ORCAFTPSSL'), action=cParserAction, oParameter=self, dest="uFTPSSL", help='Flag 0/1 to use SSL to connect to the FTP server (can be passed as ORCAFTPSSL environment var)')
            oParser.add_argument('--ftprepsourcepath', default=GetEnvVar('ORCAREPSOURCEPATH',Globals.oPathRoot.string), action=cParserAction, oParameter=self, dest="oPathRepSource", help='Changes the path for repository manager where to find the repositry files to upload (can be passed as ORCAREPSOURCEPATH environment var)')
            oParser.add_argument('--wwwserverpath', default=GetEnvVar('ORCAWWWSERVERPATH'), action=cParserAction, oParameter=self, dest="uWWWServerPath", help='Set the WWW Server path for the repository manager  (can be passed as ORCAWWWSERVERPATH environment var)')

    def __init__(self):
        cToolsTemplate.__init__(self)
        self.uSubType        = u'REPOSITORY'
        self.uSortOrder      = u'auto'
        self.uSettingSection = u'tools'
        self.uSettingTitle   = u"Repository Manager"
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
            self.StartRepositoryManager(self, *args, **kwargs)

    def StartRepositoryManager(self, *args, **kwargs):
        oSetting                = self.GetSettingObjectForConfigName(self.uConfigName)
        SetVar(uVarName=u'REPOSITORYWWWPATH',  oVarValue=oSetting.aScriptIniSettings.uWWWServerPath)
        SetVar(uVarName=u"REPMAN_FTPSERVER",   oVarValue=oSetting.aScriptIniSettings.uHost)
        SetVar(uVarName=u"REPMAN_FTPPATH",     oVarValue=oSetting.aScriptIniSettings.uFTPPath)
        SetVar(uVarName=u"REPMAN_FTPUSER",     oVarValue=oSetting.aScriptIniSettings.uUser)
        SetVar(uVarName=u"REPMAN_FTPPASSWORD", oVarValue=oSetting.aScriptIniSettings.uPassword)

        if oSetting.aScriptIniSettings.bFTPSSL:
            SetVar(uVarName=u"REPMAN_FTPSSL",oVarValue=u"1")
        else:
            SetVar(uVarName=u"REPMAN_FTPSSL", oVarValue=u"0")

        RepositoryManager(oPathRepSource = cPath(oSetting.aScriptIniSettings.uPathRepSource))

    def CreateRepositoryVarArray(self,  *args, **kwargs):
        uBaseLocalDir  = ReplaceVars(kwargs.get("baselocaldir",(Globals.oPathTmp + "RepManager").string))
        CreateRepVarArray(uBaseLocalDir)

    def Register(self, *args, **kwargs):
        cToolsTemplate.Register(self,*args, **kwargs)
        Globals.oNotifications.RegisterNotification("STARTSCRIPTREPOSITORYMANAGER", fNotifyFunction=self.StartRepositoryManager,   uDescription="Script Repository Manager")
        Globals.oNotifications.RegisterNotification("CREATEREPOSITORYVARARRAY",     fNotifyFunction=self.CreateRepositoryVarArray, uDescription="Script Repository Manager")

        oScriptSettingPlugin = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName   = self.uScriptName
        oScriptSettingPlugin.uSettingName  = "TOOLS"
        oScriptSettingPlugin.uSettingPage  = "$lvar(699)"
        oScriptSettingPlugin.uSettingTitle = "$lvar(SCRIPT_TOOLS_REPMANAGER_4)"
        oScriptSettingPlugin.aSettingJson  = [u'{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_REPMANAGER_1)","desc": "$lvar(SCRIPT_TOOLS_REPMANAGER_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_REPMANAGER_3)","id":"button_notification_STARTSCRIPTREPOSITORYMANAGER"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uScriptName,oScriptSettingPlugin=oScriptSettingPlugin)
        self.LoadActions()

    def GetConfigJSON(self):
        return {"FTPPath": {"type": "varstring", "active":"enabled", "order":16,  "title": "$lvar(SCRIPT_TOOLS_REPMANAGER_5)", "desc": "$lvar(SCRIPT_TOOLS_REPMANAGER_6)","key": "FTPPath", "default":Globals.oParameter.uFTPServerPath, "section": "$var(ScriptConfigSection)"},
                "FTPSSL":  {"type": "bool",   "active":"enabled", "order":17,  "title": "$lvar(SCRIPT_TOOLS_REPMANAGER_7)", "desc": "$lvar(SCRIPT_TOOLS_REPMANAGER_8)","key": "FTPSSL", "default":ToBool(Globals.oParameter.uFTPSSL),"section": "$var(ScriptConfigSection)"},
                "PathRepSource": {"type": "path", "active": "enabled", "order": 18, "title": "$lvar(SCRIPT_TOOLS_REPMANAGER_9)", "desc": "$lvar(SCRIPT_TOOLS_REPMANAGER_10)", "key": "PathRepSource", "default": Globals.oParameter.oPathRepSource.unixstring, "section": "$var(ScriptConfigSection)"},
                "WWWServerPath": {"type": "varstring", "active": "enabled", "order": 19, "title": "$lvar(SCRIPT_TOOLS_REPMANAGER_11)", "desc": "$lvar(SCRIPT_TOOLS_REPMANAGER_12)", "key": "WWWServerPath", "default": Globals.oParameter.uWWWServerPath,"section": "$var(ScriptConfigSection)"}
                }
