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

from ORCA.scripts.Scripts import cScriptSettingPlugin
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
import ORCA.Globals as Globals



'''
<root>
  <repositorymanager>
    <entry>
      <name>Tool Gesturerecorder</name>
      <description language='English'>Tool to record gestures</description>
      <description language='German'>Tool um Gesten aufzuzeichnen</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/tools/tool_gesturerecorder</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/tool_gesturerecorder.zip</sourcefile>
          <targetpath>scripts/tools</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>Widget Gesturerecorder</name>
        </dependency>
      </dependencies>
      <skipfiles>
        <file>scripts/tools/tool_gesturerecorder/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''



class cScript(cToolsTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-tools_gesturerecorder
    WikiDoc:TOCTitle:Script Tools Gesturerecorder
    = Tool to Record Gestures =

    This tools add a gesture recorder to ORCA. Will be added to the Tools section of the settings
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |}</div>

    WikiDoc:End
    """

    def __init__(self):
        cToolsTemplate.__init__(self)
        self.uSubType           = u'GESTURERECORCER'
        self.uSortOrder         = u'auto'
        self.uSettingSection    = u'tools'
        self.uSettingTitle      = u'Gestures'
        self.uIniFileLocation   = u'none'

    def ShowPageGestureRecorder(self, *args, **kwargs):
        Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_GestureRecorder')

    def RunScript(self, *args, **kwargs):
        cToolsTemplate.RunScript(self, *args, **kwargs)
        if kwargs.get("caller") == "settings" or kwargs.get("caller") == "action":
            self.ShowPageGestureRecorder(self, *args, **kwargs)

    def Register(self, *args, **kwargs):
        cToolsTemplate.Register(self,*args, **kwargs)
        Globals.oNotifications.RegisterNotification("DEFINITIONPAGESLOADED", fNotifyFunction=self.LoadScriptPages, uDescription="Script Tools GestureRecorder")
        Globals.oNotifications.RegisterNotification("STARTSCRIPTGESTURERECORDER", fNotifyFunction=self.ShowPageGestureRecorder, uDescription="Script Tools GestureRecorder")
        oScriptSettingPlugin = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName   = self.uObjectName
        oScriptSettingPlugin.uSettingName  = "ORCA"
        oScriptSettingPlugin.uSettingPage  = "$lvar(572)"
        oScriptSettingPlugin.uSettingTitle = "$lvar(SCRIPT_TOOLS_GESTURERECORDER_4)"
        oScriptSettingPlugin.aSettingJson  = [u'{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_GESTURERECORDER_1)","desc": "$lvar(SCRIPT_TOOLS_GESTURERECORDER_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_GESTURERECORDER_3)","id":"button_notification_STARTSCRIPTGESTURERECORDER"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uObjectName,oScriptSettingPlugin=oScriptSettingPlugin)

        ''' If we press ESC on the Gestureboard page, goto to the settings page
            If we press the close button on the interface-settings page, goto to the settings page '''

        oEvents = Globals.oEvents
        aActions=oEvents.CreateSimpleActionList([{'name':'ESC Key Handler Gestureboard','string':'registernotification','filterpagename':'Page_GestureRecorder','notification':'on_key_ESC','notifyaction':'gotosettingspage'},
                                                 {'name':'Button Close Gestureboard Key Handler Settings','string':'registernotification','filterpagename':'Page_GestureRecorder','notification':'closesetting_gesturerecorder','notifyaction':'gotosettingspage'}])
        oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)


    def LoadScriptPages(self,*args,**kwargs):
        oDefinition = kwargs.get("definition")

        if oDefinition.uName == Globals.uDefinitionName:
            if self.oFnXML.Exists():
                oDefinition.LoadFurtherXmlFile(self.oFnXML)
