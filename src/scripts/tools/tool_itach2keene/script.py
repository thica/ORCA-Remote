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

from typing                                 import Dict
from typing                                 import List

from ORCA.scripts.Scripts                   import cScriptSettingPlugin
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
from ORCA.Action                            import cAction
from ORCA.definition.Definition             import cDefinition
import ORCA.Globals as Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>Tool iTach2Keene</name>
      <description language='English'>Tool to convert IR Files from iTach format to Kira Keene formats</description>
      <description language='German'>Tool um IR Dateien vom iTach Format zum Kira Keene Format zu konvertieren</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/tools/tool_itach2keene</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/tool_itach2keene.zip</sourcefile>
          <targetpath>scripts/tools</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>Widget iTach2Keene</name>
        </dependency>
      </dependencies>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


# noinspection PyUnusedLocal
class cScript(cToolsTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-tools_itach2keene
    WikiDoc:TOCTitle:Script Tools iTach2Keene
    = Tool to convert iTach ir-codes to Keene Kira ir-codes =

    This tools adds IR code coversion tool to ORCA. Will be added to the Tools section of the settings
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |}</div>

    WikiDoc:End
    """

    def __init__(self):
        cToolsTemplate.__init__(self)
        self.uSubType        = u'IR-CONVERTER'
        self.uSortOrder      = u'auto'
        self.uSettingSection = u'tools'
        self.uSettingTitle   = u"iTach2Keene"

    def RunScript(self, *args, **kwargs) -> None:
        cToolsTemplate.RunScript(self,*args, **kwargs)
        if kwargs.get("caller") == "settings" or kwargs.get("caller") == "action":
            self.ShowPageItach2Keene(self, *args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def ShowPageItach2Keene(self, *args, **kwargs) -> None:
        Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_ITach2Keene')

    def Register(self, *args, **kwargs) -> Dict:
        cToolsTemplate.Register(self,*args, **kwargs)
        Globals.oNotifications.RegisterNotification("DEFINITIONPAGESLOADED", fNotifyFunction=self.LoadScriptPages, uDescription="Script Tools iTach2Keene")
        Globals.oNotifications.RegisterNotification("STARTSCRIPTITACH2KEENE", fNotifyFunction=self.ShowPageItach2Keene, uDescription="Script Tools iTach2Keene")
        oScriptSettingPlugin = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName   = self.uObjectName
        oScriptSettingPlugin.uSettingName  = "ORCA"
        oScriptSettingPlugin.uSettingPage  = "$lvar(572)"
        oScriptSettingPlugin.uSettingTitle = "$lvar(SCRIPT_TOOLS_ITACH2KEENE_4)"
        oScriptSettingPlugin.aSettingJson  = [u'{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_ITACH2KEENE_1)","desc": "$lvar(SCRIPT_TOOLS_ITACH2KEENE_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_ITACH2KEENE_3)","id":"button_notification_STARTSCRIPTITACH2KEENE"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uObjectName,oScriptSettingPlugin=oScriptSettingPlugin)

        ''' If we press ESC on the iTach2Keene page, goto to the settings page '''

        aActions:List[cAction]= Globals.oEvents.CreateSimpleActionList([{'name':'ESC Key Handler iTach2Keene','string':'registernotification','filterpagename':'Page_iTach2Keene','notification':'on_key_ESC','notifyaction':'gotosettingspage'}])
        Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        return {}

    def LoadScriptPages(self,*args,**kwargs) -> None:
        oDefinition:cDefinition = kwargs.get("definition")

        if oDefinition.uName == Globals.uDefinitionName:
            if self.oFnXML.Exists():
                oDefinition.LoadFurtherXmlFile(self.oFnXML)
