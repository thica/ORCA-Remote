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

from typing                                     import List
from typing                                     import Dict

from kivy.uix.settings                          import Settings as KivySettings
from kivy.config                                import Config

from ORCA.definition.Definition                 import cDefinition
from ORCA.definition.DefinitionPathes           import cDefinitionPathes
from ORCA.download.InstalledReps                import cInstalledReps
from ORCA.download.RepManagerEntry              import cRepManagerEntry
from ORCA.settings.BuildSettingOptionList       import BuildSettingOptionListDictVar
from ORCA.settings.BuildSettingOptionList       import BuildSettingOptionListVar
from ORCA.settings.setttingtypes.Public         import RegisterSettingTypes
from ORCA.utils.FileName                        import cFileName
from ORCA.utils.LoadFile                        import LoadFile
from ORCA.utils.TypeConvert                     import ToStringVersion
from ORCA.vars.Access                           import GetVar
from ORCA.vars.Helpers                          import GetVarList
from ORCA.vars.Replace                          import ReplaceVars

import ORCA.Globals as Globals


__all__ = ['Build_Settings','BuildSettingsStringPowerStatus']

def Build_Settings(oSettings:KivySettings) -> None:
    """
    will be called, when showing the settings dialog
    We add a further panel for the orca.ini settings
    If we had a successful init, lets build the default full settings view
    otherwise just build a very minimilistic settings dialog, where the user can just change the ini path
    """
    RegisterSettingTypes(oSettings)
    if Globals.bInit:

        uOrcaSettingsJSON:str = BuildSettingsString()
        oSettings.add_json_panel(u'ORCA', Globals.oOrcaConfigParser, data=uOrcaSettingsJSON)

        uBuildSettingsStringDefinitionList:str = BuildSettingsStringDefinitionList()
        if uBuildSettingsStringDefinitionList != '':
            oSettings.add_json_panel(ReplaceVars('$lvar(580)'),Globals.oDefinitionConfigParser, data=uBuildSettingsStringDefinitionList)

        # Add the Info panel
        oSettings.add_json_panel(ReplaceVars('$lvar(585)'), Globals.oOrcaConfigParser, data=BuildSettingsStringInfo())

        # add the tools settings
        # and pass to kivy
        oSettings.add_json_panel(ReplaceVars('$lvar(572)'), Globals.oOrcaConfigParser, data=BuildSettingsStringTools())

        # add the Online  settings
        # and pass to kivy
        oSettings.add_json_panel(ReplaceVars('$lvar(699)'), Globals.oOrcaConfigParser, data=BuildSettingsStringOnlineResources())

    else:
        # just build the small settings
        oSettings.add_json_panel(u'ORCA', Globals.oOrcaConfigParser, data=BuildSmallSettingsString())

def GetJsonFromSettingFileName(uSettingFileName:str) -> str:
    oFnSetting:cFileName = cFileName(Globals.oPathAppReal + "ORCA/settings/settingstrings") + uSettingFileName
    if not oFnSetting.Exists():
        oFnSetting: cFileName = cFileName(Globals.oPathApp + "ORCA/settings/settingstrings") + uSettingFileName

    return ReplaceVars(LoadFile(oFnSetting))

def ScanDefinitionNames() -> Dict:
    """
    Parses the Definition description to give definition names
    """

    uDefinitionName:str
    oDefinitionPathes:cDefinitionPathes
    oRepManagerEntry:cRepManagerEntry
    dDefinitionReps:Dict={}

    aHide:List[str] = ["appfavorites_template","cmdfavorites_template","tvfavorites_template","activity_template"]

    for uDefinitionName in Globals.aDefinitionList:
        if not uDefinitionName in aHide:
            if Globals.dDefinitionPathes.get(uDefinitionName) is None:
                oDefinitionPathes=cDefinitionPathes(uDefinitionName)
                Globals.dDefinitionPathes[uDefinitionName]=oDefinitionPathes
            oRepManagerEntry=cRepManagerEntry(Globals.dDefinitionPathes[uDefinitionName].oFnDefinition)
            if oRepManagerEntry.ParseFromXML():
                dDefinitionReps[uDefinitionName]=oRepManagerEntry.oRepEntry.uName

    return dDefinitionReps

def BuildSettingsString() -> str:
    """ Create a Interface list with the used interfaces at the top """
    uInterFacename:str
    iLast:int
    i:int
    aInterfaceList:List[str] = []


    for uInterFacename in Globals.oInterFaces.dUsedInterfaces:
        uInterFacename=ReplaceVars(uInterFacename)
        if not uInterFacename in aInterfaceList and uInterFacename!=u'':
            aInterfaceList.append(uInterFacename)

    for uInterFacename  in Globals.oInterFaces.aInterfaceList:
        if not uInterFacename in aInterfaceList:
            aInterfaceList.append(uInterFacename)

    # put the templates to the end
    iLast=len(Globals.aDefinitionList)-1
    for i in range(0,len(Globals.aDefinitionList)):
        if i>=iLast:
            break
        if Globals.aDefinitionList[i].endswith(u"_template"):
            Globals.aDefinitionList[i],Globals.aDefinitionList[iLast]=Globals.aDefinitionList[iLast],Globals.aDefinitionList[i]
            iLast=iLast-1

    dDefinitionReps:Dict=ScanDefinitionNames()
    Globals.oScripts.LoadScripts()

    BuildSettingOptionListVar(Globals.aLanguageList,                        "SETTINGS_LANGUAGELIST")
    BuildSettingOptionListVar(Globals.oLanguage.oLocales.oLocalesEntries,   "SETTINGS_LANGUAGELOCALES")
    BuildSettingOptionListVar(Globals.oScripts.aScriptNameList,             "SETTINGS_SCRIPTNAMELIST")
    BuildSettingOptionListVar(Globals.oScripts.aScriptNameListWithConfig,   "SETTINGS_SCRIPTNAMELISTWITHCONFIG")
    BuildSettingOptionListVar(aInterfaceList,                               "SETTINGS_INTERFACENAMELIST")
    BuildSettingOptionListVar(Globals.oSound.aSoundsList,                   "SETTINGS_SOUNDLIST")
    BuildSettingOptionListVar(Globals.aSkinList,                            "SETTINGS_SKINLIST")
    BuildSettingOptionListDictVar(dDefinitionReps,                          "SETTINGS_DEFINITIONLIST")
    return GetJsonFromSettingFileName("setting_orca.txt")

def BuildSettingsStringDefinitionList() -> str:
    """ Build the settings for the ORCA DefinitionList """

    uMainSetting:str       = u''
    uSubSetting:str        = u''
    uOrcaSettingsJSON:str  = u''

    uPublicTitle:str
    oDef:cDefinition
    iStart:int

    aDefinitionListSorted:List[cDefinition] = sorted(Globals.oDefinitions, key=lambda entry: entry.uDefPublicTitle)

    for oDef in aDefinitionListSorted:
        if len(oDef.dDefinitionSettingsJSON)>0:
            uPublicTitle = oDef.uDefPublicTitle
            iStart       = uPublicTitle.find( '[' )
            if iStart != -1 :
                uPublicTitle = uPublicTitle[:iStart]
            if oDef==Globals.oDefinitions[0]:
                uMainSetting= u'{"type": "buttons","title": "%s","desc": "%s","section": "ORCA","key": "button_changedefinitionsetting","buttons":[{"title":"$lvar(716)","id":"button_%s"}]}'  %(uPublicTitle,oDef.uDefDescription,oDef.uAlias)
            else:
                uSubSetting+= u'{"type": "buttons","title": "%s","desc": "%s","section": "ORCA","key": "button_changedefinitionsetting","buttons":[{"title":"$lvar(716)","id":"button_%s"}]},' %(uPublicTitle,oDef.uDefDescription,oDef.uAlias )

    if uMainSetting != u'':
        uOrcaSettingsJSON  =u'[{ "type": "title","title":  "$lvar(717)" },\n %s]' % uMainSetting
        if uSubSetting!=u'':
            uOrcaSettingsJSON = u'%s,{ "type": "title","title":  "$lvar(718)" },\n %s]' % (uOrcaSettingsJSON[:-1],uSubSetting[:-1])
    else:
        if uSubSetting!=u'':
            uOrcaSettingsJSON = u'[{ "type": "title","title":  "$lvar(718)" },\n %s]' % (uSubSetting[:-1])

    uOrcaSettingsJSON=uOrcaSettingsJSON.replace("'","\'")
    uOrcaSettingsJSON=ReplaceVars(uOrcaSettingsJSON)
    return uOrcaSettingsJSON

def BuildSettingsStringInfo() -> str:
    """ Build the settings for the ORCA Info panel """
    return GetJsonFromSettingFileName("setting_info.txt")


def BuildSettingsStringTools() -> str:
    """ Build the settings for the ORCA tools """
    uOrcaSettingsJSON  =u'[{ "type": "title","title": "$lvar(573)" },\n' \
                        u'{"type": "buttons","title": "$lvar(574)","desc": "$lvar(575)","section": "ORCA","key": "button_clear_atlas","buttons":[{"title":"$lvar(576)","id":"button_clear_atlas"}]},\n' \
                        u'{ "type": "title","title": "$lvar(633)" },\n' \
                        u'{"type": "buttons","title": "$lvar(720)","desc": "$lvar(721)","section": "ORCA","key": "button_discover_results","buttons":[{"title":"$lvar(722)","id":"button_discover_results"}]},\n' \
                        u'{"type": "buttons","title": "$lvar(760)","desc": "$lvar(761)","section": "ORCA","key": "button_discover_rediscover","buttons":[{"title":"$lvar(722)","id":"button_discover_rediscover"},{"title":"$lvar(729)","id":"button_discover_rediscover_force"}]}]'

    uOrcaSettingsJSON=AddScriptSetting(uSettingName="ORCA",uSettingPage=ReplaceVars("$lvar(572)"),uOrcaSettingsJSON=uOrcaSettingsJSON)
    uOrcaSettingsJSON=ReplaceVars(uOrcaSettingsJSON)

    return uOrcaSettingsJSON

def BuildSettingsStringOnlineResources() -> str:
    """ Build the settings for the ORCA Online Resource """

    iCountBlanks:int = 0
    i:int
    uReps:str        = ''
    uKey:str
    oInstalledRep: cInstalledReps
    aSubList: List[cInstalledReps]

    for i in range(Globals.iCntRepositories):
        if Globals.aRepositories[i]=='':
            iCountBlanks+=1
            if iCountBlanks>1:
                continue
        uReps+=u'{"type": "string","title":    "$lvar(671)","desc": "$lvar(672)","section": "ORCA","key": "repository%d"},\n' % i


    uOrcaSettingsJSON  =u'[{ "type": "title","title":  "$lvar(670)" },\n' \
                        '%s' \
                        u'{ "type": "title","title": "$lvar(680)" },\n' \
                        u'{"type": "buttons","title": "$lvar(681)","desc": "$lvar(682)","section": "ORCA","key": "button_getonline","buttons":[{"title":"$lvar(678)","id":"button_getonline"}]}' \
                        u']' % uReps


    if len(Globals.dInstalledReps)>0:
        uOrcaSettingsJSON=uOrcaSettingsJSON[:-1]

        aSubList = []

        for (uKey,oInstalledRep) in Globals.dInstalledReps.items():
            aSubList.append(oInstalledRep)
        aSubList.sort(key = lambda x: x.uType)

        uOldType:str = u''
        uOrcaSettingsJSON+=u',{ "type": "title","title": "$lvar(679)" },\n'
        for oInstalledRep in aSubList:
            if uOldType!=oInstalledRep.uType:
                uOldType=oInstalledRep.uType
                uName="???"
                for tTup in Globals.aRepNames:
                    if tTup[1]==oInstalledRep.uType:
                        uName=tTup[0]
                uOrcaSettingsJSON+=u'{ "type": "title","title": "-> %s" },\n' % uName

            uOrcaSettingsJSON+=u'{"type": "buttons","title": "%s","desc": "$lvar(751): %s","section": "ORCA","key": "button_installed_reps","buttons":[{"title":"$lvar(752)","id":"button_updaterep:%s:%s"}]},\n' % (oInstalledRep.uName,ToStringVersion(oInstalledRep.iVersion),oInstalledRep.uType,oInstalledRep.uName)
        uOrcaSettingsJSON=uOrcaSettingsJSON[:-2]
        uOrcaSettingsJSON+=u']'

    uOrcaSettingsJSON=uOrcaSettingsJSON.replace("'","\'")

    uOrcaSettingsJSON=AddScriptSetting(uSettingName="TOOLS",uSettingPage=ReplaceVars("$lvar(699)"),uOrcaSettingsJSON=uOrcaSettingsJSON)
    uOrcaSettingsJSON=ReplaceVars(uOrcaSettingsJSON)
    return uOrcaSettingsJSON

def BuildSmallSettingsString() -> str:
    """ just build the small settings """
    uOrcaSettingsJSON=u'[{ "type": "title","title": "Initialisation" },\n' \
                      u'{"type": "path","title":    "Path to Orca Files","desc": "Sets the file root path for Orca files (Definitions, etc)","section": "ORCA","key": "rootpath"}\n' \
                      u']'
    return uOrcaSettingsJSON

def BuildSettingsStringPowerStatus() -> str:
    """ Build the settings for the Power Stati """

    uSection:str
    uVarNameKey:str
    uIndexGroup:str
    uActivityGroupName:str
    uActivityName:str
    oConfig:Config
    aPowerListDevices:List[str]    = []
    aPowerListActivities:List[str] = []
    iLeftBracketPos:int
    iRightBracketPos:int

    uPowerStatusJSON:str =u'['

    aPowerList=sorted(GetVarList(uFilter = "POWERSTATUS"))
    for uKey in aPowerList:
        if uKey.startswith("POWERSTATUS_"):
            aPowerListDevices.append(uKey)
    for uKey in aPowerList:
        if u"ACTIVITY_POWERSTATUS[" in uKey:
            aPowerListActivities.append(uKey)

    uSection = Globals.uDefinitionName
    uSection = uSection.replace(u' ', u'_')
    oConfig=Globals.oDefinitionConfigParser

    if len(aPowerListDevices):
        uPowerStatusJSON+=ReplaceVars(u'{ "type": "title","title": "$lvar(2001)" },\n')
        for uVarNameKey in aPowerListDevices:
            uPowerStatusJSON+= u'{"type": "bool","title": "%s","desc": "","section": "%s","key": "powerstatus_%s"},\n' %(uVarNameKey,uSection,uVarNameKey.lower())
            if GetVar(uVarName = uVarNameKey)=="ON":
                oConfig.set(uSection, "powerstatus_"+uVarNameKey.lower(), "1")
            else:
                oConfig.set(uSection, "powerstatus_"+uVarNameKey.lower(), "0")


    if len(aPowerListActivities):
        uPowerStatusJSON+=ReplaceVars(u'{ "type": "title","title": "$lvar(2000)" },\n')
        for uVarNameKey in aPowerListActivities:
            iLeftBracketPos=uVarNameKey.find('[')
            if iLeftBracketPos != -1:
                iRightBracketPos = uVarNameKey.find(']',iLeftBracketPos)
                if iRightBracketPos != -1:
                    uIndexGroup=uVarNameKey[iLeftBracketPos+1:iRightBracketPos]
                    uActivityGroupName=GetVar(uVarName = "ACTIVITYGROUPNAME["+uIndexGroup+"]")
                    uActivityName=GetVar(uVarName = "ACTIVITY_NAME"+uVarNameKey[iLeftBracketPos:])
                    if uActivityName:
                        uPowerStatusJSON+= u'{"type": "bool","title": "%s %s","desc": "%s","section": "%s","key": "powerstatus_%s"},\n' %(uActivityGroupName,uActivityName,uVarNameKey,uSection,uVarNameKey.lower())
                        if GetVar(uVarName = uVarNameKey)=="ON":
                            oConfig.set(uSection, "powerstatus_"+uVarNameKey.lower(), "1")
                        else:
                            oConfig.set(uSection, "powerstatus_"+uVarNameKey.lower(), "0")

    if len(uPowerStatusJSON)>1:
        uPowerStatusJSON=uPowerStatusJSON[:-2]
        uPowerStatusJSON+=u']'
    else:
        uPowerStatusJSON=u'[]'

    oConfig.write()
    return uPowerStatusJSON

def AddScriptSetting(uSettingName,uSettingPage,uOrcaSettingsJSON):
    dTitleSettings = {}
    uTmp = u","
    for uScripKey in Globals.oScripts.dScriptSettingPlugins:
        oScriptSettingPlugins = Globals.oScripts.dScriptSettingPlugins[uScripKey]
        if oScriptSettingPlugins.uSettingName==uSettingName and ReplaceVars(oScriptSettingPlugins.uSettingPage)==uSettingPage:
            uSettingTitle = ReplaceVars(oScriptSettingPlugins.uSettingTitle)
            if dTitleSettings.get(uSettingTitle) is None:
                dTitleSettings[uSettingTitle]=[u'{ "type": "title","title": "%s" }' % oScriptSettingPlugins.uSettingTitle]
            for uSettingJson in oScriptSettingPlugins.aSettingJson:
                dTitleSettings[uSettingTitle].append(uSettingJson)
    if len(dTitleSettings)>0:
        for uKey in dTitleSettings:
            for uLine in dTitleSettings[uKey]:
                uTmp=uTmp+uLine+",\n"
        uOrcaSettingsJSON=uOrcaSettingsJSON[:-1]+uTmp[:-2]+u"]"
    return uOrcaSettingsJSON



