# -*- coding: utf-8 -*-

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

from typing                         import Dict
from typing                         import Union
from kivy.uix.widget                import Widget
from kivy.config                    import ConfigParser
from xml.etree.ElementTree          import Element
from random                         import random
from functools                      import partial
from kivy.uix.settings              import Settings
from kivy.uix.settings              import SettingsWithSidebar
from kivy.uix.settings              import SettingsWithSpinner
from kivy.uix.spinner               import Spinner
from kivy.clock                     import Clock
from kivy.logger                    import Logger
from ORCA.settings.SettingChanges   import OrcaConfigParser_On_Setting_Change
from ORCA.settings.AppSettings      import BuildSettingsStringPowerStatus
from ORCA.settings.setttingtypes.Public import RegisterSettingTypes
from ORCA.utils.LogError            import LogError
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.vars.Replace              import ReplaceVars
from ORCA.vars.Access               import SetVar
from ORCA.vars.Actions              import Var_Invert
from ORCA.widgets.FileViewer        import cWidgetFileViewer
from ORCA.interfaces.BaseInterface  import cBaseInterFace
from ORCA.scripts.BaseScript        import cBaseScript


import ORCA.Globals as Globals
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")

__all__ = ['cWidgetSettings']


class cWidgetSettings(cWidgetFileViewer):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-SETTINGS
    WikiDoc:TOCTitle:Settings
    = SETTINGS =

    The Settings widget shows various settings dialogs. This is a more like internal widget

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "SETTINGS". Capital letters!
    |-
    |settingstype
    |Type of the setting, could be
    * interface
    * script
    * download
    * orca
    * definition
    |}</div>

    Below you see an example for a settings widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='definitionsettings' type='SETTINGS' settingstype='definition' />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.uSettingsType:str                  = u''
        self.oXMLNode:Union[Element,None]       = None
        self.aSettingObjects:Dict[str,Settings] = {}
        self.oReAssignObject                    = None

    def InitWidgetFromXml(self,*,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        self.uSettingsType  = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=u'settingstype', bMandatory=False,vDefault=u'interface')
        self.oXMLNode       = oXMLNode
        bRet=super(cWidgetSettings, self).InitWidgetFromXml(oXMLNode=oXMLNode,oParentScreenPage=oParentScreenPage, uAnchor=uAnchor)
        if bRet:
            bRet = self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)
        return bRet

    def Create(self, oParent: Widget) -> bool:

        self.oParent = oParent
        if self.uSettingsType == u'orca':
            return self.CreateReal(oParent)
        else:
            Clock.schedule_once(partial(self.CreateReal,oParent),0)
            return True

    # noinspection PyUnusedLocal
    def CreateReal(self,oParent:Widget,*largs) -> bool:
        uSettingsJSON:str = ""
        uConfigName:str
        oInterFace:cBaseInterFace
        oScript:cBaseScript
        uNewMenuName:str = ReplaceVars("$lvar(579)")
        uOldMenuName:str = "Kivy"

        try:
            if self.uSettingsType==u'powerstati':
                if self.CreateBase(Parent=oParent, Class=SettingsWithSidebar):
                    self.oParent.add_widget(self.oObject)
                    uSettingsJSON = BuildSettingsStringPowerStatus()
                    self.oObject.add_json_panel(ReplaceVars('$lvar(547)'),Globals.oDefinitionConfigParser, data=uSettingsJSON)
                    self.oObject.bind(on_close=self.On_SettingsClose,on_config_change=self.On_PowerStatus_ConfigChange)
                    return True
                return False

            if self.uSettingsType==u'interface':
                if self.CreateBase(Parent=oParent, Class=SettingsWithSidebar):
                    self.oParent.add_widget(self.oObject)
                    oInterFace=Globals.oInterFaces.dInterfaces.get(Globals.oTheScreen.uInterFaceToConfig)
                    if oInterFace:
                        oInterFace.oObjectConfig.ConfigureKivySettings(oKivySetting=self.oObject)
                        self.oObject.bind(on_close=self.On_SettingsClose)
                    return True
                return False

            if self.uSettingsType==u'script':
                if self.CreateBase(Parent=oParent, Class=SettingsWithSpinner):
                    self.oParent.add_widget(self.oObject)
                    Globals.oScripts.LoadScript(Globals.oTheScreen.uScriptToConfig)
                    oScript=Globals.oScripts.dScripts.get(Globals.oTheScreen.uScriptToConfig)
                    if oScript:
                        oScript.oObjectConfig.ConfigureKivySettings(oKivySetting=self.oObject)
                        self.oObject.bind(on_close=self.On_SettingsClose)
                    return True
                return False

            if self.uSettingsType==u'interface_discover':
                if self.CreateBase(Parent=oParent, Class=SettingsWithSidebar):
                    self.oParent.add_widget(self.oObject)
                    oInterFace=Globals.oInterFaces.dInterfaces.get(Globals.oTheScreen.uInterFaceToConfig)
                    uConfigName=Globals.oTheScreen.uConfigToConfig
                    if oInterFace:
                        oInterFace.oObjectConfigDiscover.ConfigureKivySettingsForDiscoverParameter(oKivySetting=self.oObject, uConfigName=uConfigName)
                        self.oObject.bind(on_close=self.On_SettingsDiscoverClose)
                    return True
                return False

            if self.uSettingsType==u'download':
                if self.CreateBase(Parent=oParent, Class=SettingsWithSidebar):
                    self.oParent.add_widget(self.oObject)
                    Globals.oDownLoadSettings.ConfigDownLoadSettings(oSetting=self.oObject)
                    return True
                return False

            if self.uSettingsType==u'orca':
                if self.CreateBase(Parent=oParent, Class=''):
                    self.oObject = Globals.oApp.create_settings()

                    # Replace the old "Kivy" Menu text by "System"
                    oMenu = self.oObject.interface.menu
                    for oChildren in oMenu.children:
                        if isinstance(oChildren,Spinner):
                            for n, uValue in enumerate(oChildren.values):
                                if uValue == uOldMenuName:
                                    oChildren.values[n] = uNewMenuName
                                    oMenu.panel_names[uNewMenuName] = oMenu.panel_names.pop(uOldMenuName)

                    Globals.oApp._app_settings = self.oObject
                    self.oObject.oOrcaWidget=   self
                    self.oObject.size=oParent.size
                    self.oParent.add_widget(self.oObject)
                    Globals.oWinOrcaSettings=oParent
                    self.oObject.bind(on_close=self.On_SettingsClose)
                    self.oObject.bind(on_config_change=self.On_Orca_ConfigChange)
                    return True
                return False

            if self.uSettingsType=='definition':

                if Globals.uDefinitionToConfigure=='':
                    return False

                if self.CreateBase(Parent=oParent, Class=SettingsWithSidebar):
                    settings=self.oObject
                    RegisterSettingTypes(settings)
                    self.oParent.add_widget(self.oObject)
                    uDefinitionName=Globals.uDefinitionToConfigure
                    oDef=Globals.oDefinitions[uDefinitionName]
                    uSettingsJSON =u'[{ "type": "title","title": "%s" },{"type": "info","title": "$lvar(587)","section": "ORCA","info":"$var(VERSION)"}]' % oDef.uDefPublicTitle
                    for uVisSection in oDef.dDefinitionSettingsJSON:
                        uSettingsJSON=oDef.dDefinitionSettingsJSON[uVisSection]
                        uSettingsJSON=ReplaceVars(uSettingsJSON)
                        settings.add_json_panel(ReplaceVars(uVisSection),Globals.oDefinitionConfigParser, data=uSettingsJSON)
                    settings.bind(on_config_change=self.On_Definition_ConfigChange,on_close=self.On_SettingsClose)
                    self.aSettingObjects[uDefinitionName]=self.oObject
                    return True
                return False
        except Exception as e:
            LogError(uMsg="Fatal Error creating settings Panel",oException=e)
            Logger.error(uSettingsJSON)
        return False

    def UpdateWidget(self) -> None:

        if self.oObject is None:
            # pass
            return

        if self.oParent is not None:
            if self.uSettingsType== 'definition':
                uDefinitionName = Globals.uDefinitionToConfigure
                oObject = self.aSettingObjects.get(uDefinitionName)
                if oObject is not None:
                    self.oParent.remove_widget(self.oObject)
                    self.oReAssignObject=oObject
                    Clock.schedule_once(self.Scheduled_AssignExistingObject,0)
                    return

            if (self.uSettingsType=='interface') or (self.uSettingsType=='script') or (self.uSettingsType=='download') or (self.uSettingsType=='definition') or (self.uSettingsType=='powerstati'):
                self.oParent.remove_widget(self.oObject)
                Clock.schedule_once(self.Schedule_AssignNewObject,0)
                return

            if self.uSettingsType=='orca':
                self.oParent.remove_widget(self.oObject)
                Globals.oApp.settings = None
                Globals.oApp._app_settings  = None

        self.Create(self.oParent)

    # noinspection PyUnusedLocal
    def On_SettingsClose(self,instance:Settings) -> bool:
        """ Called, when the setting will be closed """
        Globals.oNotifications.SendNotification(uNotification='closesetting_'+self.uSettingsType)
        return True

    # noinspection PyUnusedLocal
    def On_SettingsDiscoverClose(self,instance:Settings) -> bool:
        """ Called, when the discover settings will be closed """
        Globals.oNotifications.SendNotification(uNotification='closesetting_'+self.uSettingsType)
        return True

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def On_Definition_ConfigChange(self, settings:Settings,config:ConfigParser, section:str, key:str, value:str) -> None:
        """ Called, when a setting has been changed, will set the associated var as well """
        if key in Globals.oDefinitions.aDefinitionSettingVars:
            if value.startswith("button_"):
                SetVar(uVarName = key, oVarValue = str(random()))
            else:
                SetVar(uVarName=key, oVarValue=value)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def On_Orca_ConfigChange(self, settings:Settings,config:ConfigParser, section:str, key:str, value:str) -> None:
        """ Called, when a setting has been changed, will set the associated var as well """
        if value.startswith("button_"):
            SetVar(uVarName = key, oVarValue = str(random()))
        else:
            SetVar(uVarName=key, oVarValue=value)
        OrcaConfigParser_On_Setting_Change(config=config,section=section,key=key,value=value)


    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def On_PowerStatus_ConfigChange(self, settings:Settings,config:ConfigParser, section:str, key:str, value:str) -> None:
        """ Called, when a powerstatus var has been changed, will invert the associated var as well """
        if key.startswith('powerstatus_'):
            Var_Invert(key[12:].upper())

    # noinspection PyUnusedLocal
    def Scheduled_AssignExistingObject(self,*largs) -> None:
        self.oParent.add_widget(self.oReAssignObject)

    # noinspection PyUnusedLocal
    def Schedule_AssignNewObject(self,*largs) -> None:
        self.CreateReal(self.oParent)
