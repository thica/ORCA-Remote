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

sys.path.append(Globals.oScripts.dScriptPathList[u"tool_irdbitach"].string)

from ORCA.scripts.Scripts                   import cScriptSettingPlugin
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
from ORCA.Parameter                         import cParameter
from ORCA.Parameter                         import cParserAction
from ORCA.vars.Helpers                      import GetEnvVar
from IRDB                                   import ShowITachIRDB



'''
<root>
  <repositorymanager>
    <entry>
      <name>Tool IR Database iTach</name>
      <description language='English'>Tool get IR Codes from the iTach Database</description>
      <description language='German'>Tool IR Codes von der iTach Datenbank zu beziehen</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/tools/tool_irdbitach</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/tool_irdbitach.zip</sourcefile>
          <targetpath>scripts/tools</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/tools/tool_irdbitach/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''



class cScript(cToolsTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-tools_irdb_itach
    WikiDoc:TOCTitle:Script Tools IRDB iTach
    = Tool to Record Gestures =

    This tool gets codes from the iTAch IRDB Database. You need to be registered for that
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
            self.aScriptIniSettings.uHost     = u"http://irdbservice.cloudapp.net:8080/"
            self.aScriptIniSettings.uUser     = Globals.oParameter.uIRDBUser
            self.aScriptIniSettings.uPassword = Globals.oParameter.uIRDBPassword

    class cScriptParameter(cParameter):
        def AddParameter(self,oParser):
            oParser.add_argument('--irdbuser', default=GetEnvVar('IRDBUSER'), action=cParserAction, oParameter=self, dest="uIRDBUser", help='Set the initialisation username for the IRDB (can be passed as IRDBUSER environment var)')
            oParser.add_argument('--irdbpassword', default=GetEnvVar('IRDBPASSWORD'), action=cParserAction, oParameter=self, dest="uIRDBPassword", help='Set the initialisation password for the IRDB (can be passed as IRDBPASSWORD environment var)')

    def __init__(self):
        cToolsTemplate.__init__(self)
        self.uSubType        = u'IRDB'
        self.uSortOrder      = u'auto'
        self.uSettingSection = u'tools'
        self.uSettingTitle   = u"IRDB ITach"
        oParameter           = self.cScriptParameter()
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
            self.ShowIRDB(self, *args, **kwargs)

    def ShowIRDB(self, *args, **kwargs):
        oSetting                = self.GetSettingObjectForConfigName(self.uConfigName)
        ShowITachIRDB(uHost=oSetting.aScriptIniSettings.uHost,uUser=oSetting.aScriptIniSettings.uUser,uPassword=oSetting.aScriptIniSettings.uPassword)

    def Register(self, *args, **kwargs):
        cToolsTemplate.Register(self,*args, **kwargs)
        Globals.oNotifications.RegisterNotification("STARTSCRIPTIRDBITACH", fNotifyFunction=self.ShowIRDB, uDescription="Script Tools IRDB iTach")
        oScriptSettingPlugin = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName   = self.uScriptName
        oScriptSettingPlugin.uSettingName  = "ORCA"
        oScriptSettingPlugin.uSettingPage  = "$lvar(572)"
        oScriptSettingPlugin.uSettingTitle = "$lvar(SCRIPT_TOOLS_IRDBITACH_4)"
        oScriptSettingPlugin.aSettingJson  = [u'{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_IRDBITACH_1)","desc": "$lvar(SCRIPT_TOOLS_IRDBITACH_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_IRDBITACH_3)","id":"button_notification_STARTSCRIPTIRDBITACH"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uScriptName,oScriptSettingPlugin=oScriptSettingPlugin)


