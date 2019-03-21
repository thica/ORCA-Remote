# -*- coding: utf-8 -*-
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

from kivy.logger                import Logger

from ORCA.actions.Base          import cEventActionBase
from ORCA.utils.LogError        import LogError
from ORCA.vars.Replace          import ReplaceVars
from ORCA.vars.Access           import SetVar
from ORCA.vars.Access           import GetVar
from ORCA.utils.TypeConvert     import ToUnicode
from ORCA.utils.TypeConvert     import UnEscapeUnicode
from ORCA.utils.TypeConvert     import EscapeUnicode
from ORCA.utils.TypeConvert     import ToBool
import ORCA.Globals as Globals

__all__ = ['cEventActionsSettings']

class cEventActionsSettings(cEventActionBase):
    """ Actions for getting/writings settings """

    def ExecuteActionRemoveDefinitionSetting(self,oAction):
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-RemoveDefinitionSetting
        WikiDoc:TOCTitle:removedefinitionsetting
        = removedefinitionsetting =
        Removes a definitionsetting from a definition.
        Must be called in appstartactions or in definitionstartactions.

        This function removes either
        * a single setting within a settings of a definition
        * a set of settings which are identified by the title of the section
        * all settings of a definition

        This function is usefull, when you import a definition with it's settings, but not all settings apply to the parent setting. Remarks: Using this function will replace all variable names in the settings at this time.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |removedefinitionsetting
        |-
        |definitionname
        |If empty, the whole definitionsetting will be removed
         If given, this is variable name of the single setting within the definitionsetting to remove: Variablenames will be replaced
         If you want to remove a complete section you need to pass the title name as the variable name
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="Remove the Numberpad settings from the imported setting" string="removedefinitionsetting" definitionname="kodi_mediaplayer_template" settingname="$lvar(mediaplayertemplate_10070) ($dvar(definition_alias_mediaplayer_template))"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEvenDispatcher.LogAction(u'RemoveDefinitionSetting',oAction)
        uDefinitionName = ReplaceVars(oAction.dActionPars.get("definitionname",""))
        uSettingVar     = ReplaceVars(oAction.dActionPars.get("settingname",""))
        uSettingVarOrg  = oAction.dActionPars.get("settingname","")
        bFound=False

        oDef=Globals.oDefinitions[uDefinitionName]
        if oDef:
            if uSettingVar==u'':
                oDef.dDefinitionSettingsJSON.clear()
                bFound=True
            elif self.RemoveSettingSection(uSettingVarOrg,oDef):
                bFound=True
            else:
                import json
                for uVisSection in oDef.dDefinitionSettingsJSON:
                    aDefinitionSettingsJSON = json.loads(ReplaceVars(oDef.dDefinitionSettingsJSON[uVisSection]))
                    aDefinitionSettingsJSON2 = json.loads(ReplaceVars(oDef.dDefinitionSettingsJSON[uVisSection]))
                    iStart=-1
                    for aLine in aDefinitionSettingsJSON2:
                        iStart+=1
                        if aLine.get('key') is not None:
                            if aLine.get('key')==uSettingVar or aLine.get('key')==uSettingVarOrg:
                                aDefinitionSettingsJSON.remove(aLine)
                                bFound=True
                                break
                        else:
                            if aLine.get('type')=='title':
                                if aLine.get('title')==uSettingVar:
                                    bFound=True
                                    iEnd=iStart
                                    for aLine2 in aDefinitionSettingsJSON2[iStart+1:]:
                                        if aLine2.get('key') is not None:
                                            iEnd+=1
                                        else:
                                            break
                                    del aDefinitionSettingsJSON[iStart:iEnd+1]
                                    break
                    oDef.dDefinitionSettingsJSON[uVisSection]=ToUnicode(json.dumps(aDefinitionSettingsJSON))

        else:
            LogError(u'Action: RemoveDefinitionSetting: Wrong definition name:'+uDefinitionName )
            Globals.oDefinitions.DumpDefinitionList()
            return 1
        if not bFound:
            LogError (u'Action: RemoveDefinitionSetting: Cannot remove setting (not found) : %s [%s] [%s]' % (uSettingVar,uSettingVarOrg,uDefinitionName))
        return 0

    def RemoveSettingSection(self,uSettingVar,oDef):
        uSettingVar2=ReplaceVars(uSettingVar)
        for uSection in oDef.dDefinitionSettingsJSON:
            if uSection==uSettingVar:
                del oDef.dDefinitionSettingsJSON[uSection]
                return True
            if uSection==uSettingVar2:
                del oDef.dDefinitionSettingsJSON[uSection]
                return True
            if ReplaceVars(uSection)==uSettingVar2:
                del oDef.dDefinitionSettingsJSON[uSection]
                return True
        return False

    def ExecuteActionSaveInterfaceSetting(self,oAction):

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-SaveInterfaceSetting
        WikiDoc:TOCTitle:saveinterfacesetting
        = saveinterfacesetting =
        Write a parameter into the interface.ini. Important: You can't use this command in the appstart actions and you should set them before the interface is used. The definition start actions is a good place for this action
        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |saveinterfacesetting
        |-
        |interfacename
        |Name of the interface
        |-
        |configname
        |Name of the configuration
        |-
        |varname
        |Name of the variable to set
        |-
        |varvalue
        |Value of the variable
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="save var" string="saveinterfacesetting" interfacename="Keene_Kira" configname="mycomfigname" varname="host" varvalue="192.168.1.31"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEvenDispatcher.bDoNext = True
        self.oEvenDispatcher.aHiddenKeyWords.remove('configname')
        self.oEvenDispatcher.LogAction(u'SaveInterfaceSetting',oAction)
        self.oEvenDispatcher.aHiddenKeyWords.append('configname')

        uInterfaceName       = ReplaceVars(oAction.dActionPars.get("interfacename",""))
        uConfigName          = ReplaceVars(oAction.dActionPars.get("configname",""))
        uVarName             = ReplaceVars(oAction.dActionPars.get("varname",""))
        uVarValue            = ReplaceVars(oAction.dActionPars.get("varvalue",""))

        oInterFace=Globals.oInterFaces.dInterfaces.get(uInterfaceName)
        if oInterFace is None:
            Globals.oInterFaces.LoadInterface(uInterfaceName)
            oInterFace=Globals.oInterFaces.dInterfaces.get(uInterfaceName)

        if oInterFace is None:
            LogError(u'Action: Save Interface Setting failed: Interface: %s  Interface not found!' % (uInterfaceName))
            return 1
        oInterFace.oInterFaceConfig.WriteDefinitionConfigPar(uSectionName=uConfigName, uVarName=uVarName, uVarValue=uVarValue, bForce=True)
        return 0

    def ExecuteActionGetInterfaceSetting(self,oAction):
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-GetInterfaceSetting
        WikiDoc:TOCTitle:getinterfacesetting
        = getinterfacesetting =
        Reads a parameter from the interface.ini file. Important: You can't use this command in the appstart actions.
        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |getinterfacesetting
        |-
        |interfacename
        |Name of the interface
        |-
        |configname
        |Name of the configuration
        |-
        |varname
        |Name of the variable to get
        |-
        |retvar
        |Destination var
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="getinterfacesetting" interfacename="eiscp" configname="myconfig" varname="uHost" retvar="DISCOVERHOST"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEvenDispatcher.bDoNext = True
        self.oEvenDispatcher.LogAction(u'GetInterfaceSetting',oAction)

        uInterfaceName       = ReplaceVars(oAction.dActionPars.get("interfacename",""))
        uConfigName          = ReplaceVars(oAction.dActionPars.get("configname",""))
        uVarName             = ReplaceVars(oAction.dActionPars.get("varname",""))
        uRetVar              = ReplaceVars(oAction.dActionPars.get("retvar",""))

        oInterFace=Globals.oInterFaces.dInterfaces.get(uInterfaceName)
        if oInterFace is None:
            Globals.oInterFaces.LoadInterface(uInterfaceName)
            oInterFace=Globals.oInterFaces.dInterfaces.get(uInterfaceName)

        if oInterFace is None:
            LogError(u'Action: Get Interface Setting failed: Interface: %s  Interface not found!' % (uInterfaceName))
            return 1

        SetVar(uVarName = uRetVar, oVarValue = oInterFace.oInterFaceConfig.GetSettingParFromIni(uConfigName,uVarName))

        return 0

    def ExecuteActionGetSaveOrcaSetting(self,oAction):
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-GetSaveOrcaSetting
        WikiDoc:TOCTitle:getsaveorcasetting
        = getsaveorcasetting =
        Reads or write a parameter from or into the definition.ini file or the ORCA ini file

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |getsaveorcasetting
        |-
        |configtype
        |type of the config: "ORCA" to read/write the ORCA ini file, otherwise the definition ini file will be used
        |-
        |varname
        |The value to write, if we do not read
        |-
        |retvar
        |The varname, where the ini file value should be read into. If retvar is empty, we just write a value without reading it.
        |-
        |nowrite
        |Doesn't write the setting immediatly. Helpful for bulk operations
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="getsaveorcasetting" configtype="$var(DEFINITIONNAME)" varname="$dvar(definition_alias_enigma2)_GETCURRENTVOL" varvalue="1" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEvenDispatcher.LogAction(u'GetSaveOrcaSetting',oAction)
        self.oEvenDispatcher.bDoNext = True

        uConfigType          = ReplaceVars(oAction.dActionPars.get("configtype",""))
        uVarName             = ReplaceVars(oAction.dActionPars.get("varname",""))
        uVarValue            = oAction.dActionPars.get("varvalue","")
        uRetVar              = ReplaceVars(oAction.dActionPars.get("retvar",""))
        bNoWrite             = ToBool(ReplaceVars(oAction.dActionPars.get("nowrite","")))

        if uVarValue!= u'':
            if not "$lvar(" in uVarValue:
                uVarValue=ReplaceVars(uVarValue)
            else:
                uVarValue=uVarValue
        else:
            uVarValue=GetVar(uVarName = uVarName)

        # if uRetVar = "", we want to write
        if uRetVar=="":
            if uConfigType=="ORCA":
                Globals.oOrcaConfigParser.set(uConfigType, uVarName, uVarValue)
                if not bNoWrite:
                    Globals.oOrcaConfigParser.write()
            else:
                uSection = uConfigType
                uSection = uSection.replace(u' ', u'_')

                #todo: temporary hack to bypass configparser unicode error
                uVarValue=EscapeUnicode(uVarValue)

                Globals.oDefinitionConfigParser.set(uSection, uVarName, uVarValue)
                Logger.debug("Writing Config Var [%s]:[%s] into [%s] " % (uVarName,uVarValue,uConfigType))
                if not bNoWrite:
                    Globals.oDefinitionConfigParser.write()
            SetVar(uVarName = uVarName, oVarValue = uVarValue)
            return -2

        # otherwise we want to read
        try:
            if uConfigType=="ORCA":
                uVarValue = Globals.oOrcaConfigParser.get(u'ORCA', uVarName)
            else:
                uSection = uConfigType
                uSection = uSection.replace(u' ', u'_')
                try:
                    uVarValue = Globals.oDefinitionConfigParser.get(uSection, uVarName)
                except Exception as e:
                    Logger.warning("getsaveorcasetting: not var to read: [%s] from [%s] into Var [%s], returning empty value" % (uVarName,uConfigType,uRetVar))

            #todo: temporary hack to bypass configparser unicode error
            uVarValue=UnEscapeUnicode(uVarValue)
            SetVar(uVarName = uRetVar, oVarValue = uVarValue)
            SetVar(uVarName = uRetVar, oVarValue = uVarValue, uContext = uConfigType)
            Logger.debug("Pulled Config Var [%s]:[%s] from [%s] into Var [%s]" % (uVarName,uVarValue,uConfigType,uRetVar))
        except Exception as e:
            LogError(u'Action: GetSaveOrcaSetting',e )
            SetVar(uVarName = uRetVar, oVarValue = u'')
        return -2


