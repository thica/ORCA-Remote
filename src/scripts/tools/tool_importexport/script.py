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

from typing                                 import Dict
from shutil                                 import ignore_patterns
from ORCA.scripts.Scripts                   import cScriptSettingPlugin
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.Path                        import cPath
from ORCA.vars.Access                       import GetVar
from ORCA.vars.Access                       import SetVar
from ORCA.definition.Definition             import cDefinition

from ORCA.Globals import Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Tool Import Export</name>
      <description language='English'>Tool to Im/Export Orca files</description>
      <description language='German'>Tool um die Orca Files zu Im/Exportieren</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/tools/tool_importexport</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/tool_importexport.zip</sourcefile>
          <targetpath>scripts/tools</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class cScript(cToolsTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-tools_importexport
    WikiDoc:TOCTitle:Script Tools Import Export
    = Tool to import or export the orca files =

    This tool imports or exports the orca files
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |}</div>

    WikiDoc:End
    """

    def __init__(self):
        super().__init__()
        self.uSubType           = 'EXPORT'
        self.uSortOrder         = 'auto'
        self.uSettingSection    = 'tools'
        self.uSettingTitle      = 'Import Export'
        self.uIniFileLocation   = 'none'

    def RunScript(self, *args, **kwargs) -> None:
        super().RunScript(*args, **kwargs)
        if kwargs.get('caller') == 'settings' or kwargs.get('caller') == 'action':
            self.ShowPageExport(self, *args, **kwargs)

    def ShowPageExport(self, *args, **kwargs) -> None:
        SetVar(uVarName='ORCA_IE_DIRECTION', oVarValue='EXPORT')
        oEvents = Globals.oEvents
        aActions=oEvents.CreateSimpleActionList(aActions=[{'name':'init var','string':'setvar CHECKBOX_EXPORT_CHANGE_LOCATION=0'},
                                                          {'name':'show page','string':'showpage','pagename':'Page_Export'}])
        oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None,uQueueName='ShowPageExport')

    def ShowPageImport(self, *args, **kwargs) -> None:
        SetVar(uVarName='ORCA_IE_DIRECTION', oVarValue='IMPORT')
        oEvents = Globals.oEvents
        aActions=oEvents.CreateSimpleActionList(aActions=[{'name':'init var','string':'setvar CHECKBOX_IMPORT_CHANGE_LOCATION=0'},
                                                          {'name':'show page','string':'showpage','pagename':'Page_Import'}])
        oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None,uQueueName='ShowPageImport')

    def Register(self, *args, **kwargs) -> Dict:
        super().Register(*args, **kwargs)
        Globals.oNotifications.RegisterNotification(uNotification='DEFINITIONPAGESLOADED',            fNotifyFunction=self.LoadScriptPages, uDescription='Script Tools Import Export')
        Globals.oNotifications.RegisterNotification(uNotification='STARTSCRIPTIMPORTEXPORT-IMPORT',   fNotifyFunction=self.ShowPageImport,  uDescription='Script Tools Import / Export')
        Globals.oNotifications.RegisterNotification(uNotification='STARTSCRIPTIMPORTEXPORT-EXPORT',   fNotifyFunction=self.ShowPageExport,  uDescription='Script Tools Import / Export')
        Globals.oNotifications.RegisterNotification(uNotification='STARTSCRIPTIMPORTEXPORT-DOIMPORT', fNotifyFunction=self.ImportOrcaFiles, uDescription='Script Tools Import / Export')
        Globals.oNotifications.RegisterNotification(uNotification='STARTSCRIPTIMPORTEXPORT-DOEXPORT', fNotifyFunction=self.ExportOrcaFiles, uDescription='Script Tools Import / Export')

        oScriptSettingPlugin = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName   = self.uObjectName
        oScriptSettingPlugin.uSettingName  = 'ORCA'
        oScriptSettingPlugin.uSettingPage  = '$lvar(572)'
        oScriptSettingPlugin.uSettingTitle = '$lvar(SCRIPT_TOOLS_IMPORTEXPORT_4)'
        oScriptSettingPlugin.aSettingJson  = ['{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_IMPORTEXPORT_1)","desc": "$lvar(SCRIPT_TOOLS_IMPORTEXPORT_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_IMPORTEXPORT_3)","id":"button_notification_STARTSCRIPTIMPORTEXPORT-EXPORT"}]}',
                                              '{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_IMPORTEXPORT_5)","desc": "$lvar(SCRIPT_TOOLS_IMPORTEXPORT_5)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_IMPORTEXPORT_7)","id":"button_notification_STARTSCRIPTIMPORTEXPORT-IMPORT"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uObjectName,oScriptSettingPlugin=oScriptSettingPlugin)

        self.LoadActions()
        return {}

    def LoadScriptPages(self,*args,**kwargs) -> None:
        oDefinition:cDefinition = kwargs.get('definition')

        if oDefinition.uName == Globals.uDefinitionName:
            if self.oFnXML.Exists():
                oDefinition.LoadFurtherXmlFile(oFnXml=self.oFnXML)

    def ExportOrcaFiles(self,*args,**kwargs) -> None:
        """
        Export all Orca Files a given location
        """
        oPath:cPath = cPath(GetVar(uVarName='filebrowserfile')) + '/OrcaExport'
        oPath.Delete()
        if not str(Globals.oPathRoot) in str(oPath):
            fIgnore = ignore_patterns('*.ini', 'ORCA', '*.py*')
            Globals.oPathRoot.Copy(oDest=oPath, fIgnoreFiles=fIgnore)
            if GetVar(uVarName='CHECKBOX_EXPORT_CHANGE_LOCATION')=='1':
                Globals.oOrcaConfigParser.set('ORCA', 'rootpath', str(oPath))
                Globals.oOrcaConfigParser.write()

    def ImportOrcaFiles(self,*args,**kwargs) -> None:
            """
            Import all ORCA files from a given location
            """
            oPath:cPath = cPath(GetVar(uVarName='filebrowserfile'))
            oFnCheckFile:cFileName = cFileName(oPath + 'actions') + 'actions.xml'
            if oFnCheckFile.Exists():
                if not Globals.bProtected:
                    oPath.Copy(oDest=Globals.oPathRoot)
                    if GetVar(uVarName='CHECKBOX_IMPORT_CHANGE_LOCATION')=='1':
                        Globals.oOrcaConfigParser.set('ORCA', 'rootpath', '')
                        Globals.oOrcaConfigParser.write()


