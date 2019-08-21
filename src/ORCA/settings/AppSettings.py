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
import sys

from future.utils                               import iteritems

from ORCA.RepManagerEntry                       import cRepManagerEntry
from ORCA.settings.setttingtypes.Public         import RegisterSettingTypes
from ORCA.settings.BuildSettingOptionList       import BuildSettingOptionList
from ORCA.settings.BuildSettingOptionList       import BuildSettingOptionListDict
from ORCA.utils.TypeConvert                     import ToStringVersion
from ORCA.vars.Replace                          import ReplaceVars
from ORCA.vars.Helpers                          import GetVarList
from ORCA.vars.Access                           import GetVar
from ORCA.definition.DefinitionPathes           import cDefinitionPathes

import ORCA.Globals as Globals

__all__ = ['Build_Settings','BuildSettingsStringPowerStatus']

this = sys.modules[__name__]

this.dDefinitionReps = {}

def Build_Settings(settings):
    """
    will be called, when showing the settings dialog
    We add a further panel for the orca.ini settings
    If we had a successful init, lets build the default full settings view
    otherwise just build a very minimilistic settings dialog, where the user can just change the ini path
    """
    RegisterSettingTypes(settings)
    if Globals.bInit:

        uOrcaSettingsJSON=BuildSettingsString()
        settings.add_json_panel(u'ORCA', Globals.oOrcaConfigParser, data=uOrcaSettingsJSON)

        uBuildSettingsStringDefinitionList=BuildSettingsStringDefinitionList()
        if uBuildSettingsStringDefinitionList!='':
            settings.add_json_panel(ReplaceVars('$lvar(580)'),Globals.oDefinitionConfigParser, data=uBuildSettingsStringDefinitionList)

        # Add the Info panel
        settings.add_json_panel(ReplaceVars('$lvar(585)'), Globals.oOrcaConfigParser, data=BuildSettingsStringInfo())

        # add the tools settings
        # and pass to kivy
        settings.add_json_panel(ReplaceVars('$lvar(572)'), Globals.oOrcaConfigParser, data=BuildSettingsStringTools())

        # add the Online  settings
        # and pass to kivy
        settings.add_json_panel(ReplaceVars('$lvar(699)'), Globals.oOrcaConfigParser, data=BuildSettingsStringOnlineResources())

    else:
        # just build the small settings
        settings.add_json_panel(u'ORCA', Globals.oOrcaConfigParser, data=BuildSmallSettingsString())



#this is a further helper to match a definition short name eg the directory name, against the given name
# not working by now, as required information is missing
def BuildSettingOptionList2(aArray,uRepType=u"definitions"):
    """
    Little helper function to create a json option list
    """
    uValueString=u''
    for uToken in aArray:
        uName = this.dDefinitionReps.get(uToken)
        if not uName:
            uPrettyName = uToken
        else:
            uPrettyName = uName

        uPrettyName = uToken
        uValueString+=u'\"'+uPrettyName+u'\",'
    return uValueString[:-1]

def ScanDefinitionNames():
    """
    Parses the Definition description to give definition names
    """

    aHide = ["appfavorites_template","cmdfavorites_template","tvfavorites_template","activity_template"]

    if len(this.dDefinitionReps)==0:
        for uDefinitionName in Globals.aDefinitionList:
            if not uDefinitionName in aHide:
                if Globals.dDefinitionPathes.get(uDefinitionName) is None:
                    oDefinitionPathes=cDefinitionPathes(uDefinitionName)
                    Globals.dDefinitionPathes[uDefinitionName]=oDefinitionPathes
                oRepManagerEntry=cRepManagerEntry(Globals.dDefinitionPathes[uDefinitionName].oFnDefinition)
                if oRepManagerEntry.ParseFromXML():
                    this.dDefinitionReps[uDefinitionName]=oRepManagerEntry.oRepEntry.uName


def BuildSettingOptionList_sub(uIn,uRepType):
    """
    Helper Function for Buildsettings
    """

    for (key,val) in iteritems(Globals.dInstalledReps):
        if val.uType==uRepType and val.uName==uIn:
            return val.uName

def BuildSettingsString():
    """ Create a Interface list with the used interfaces at the top """
    aInterfaceList = []
    for uInterFacename in Globals.oInterFaces.dUsedInterfaces:
        uInterFacename=ReplaceVars(uInterFacename)
        if not uInterFacename in aInterfaceList and uInterFacename!=u'':
            aInterfaceList.append(uInterFacename)

    for uInterFacename  in Globals.oInterFaces.oInterfaceList:
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

    ScanDefinitionNames()
    Globals.oScripts.LoadScripts()

    # here we build to large settings panel string
    uOrcaSettingsJSON = u'[{{ "type": "title","title": "$lvar(501)" }},\n' \
                        u'{{"type": "scrolloptions","title": "$lvar(502)","desc": "$lvar(503)","section": "ORCA","key": "language","options":[{languagelist}]}},\n' \
                        u'{{"type": "scrolloptions","title": "$lvar(504)","desc": "$lvar(505)","section": "ORCA","key": "locales","options":[{localeslist}]}},\n' \
                        u'{{"type": "scrolloptions","title": "$lvar(506)","desc": "$lvar(507)","section": "ORCA","key": "definition","options":[{definitionlist}]}},\n' \
                        u'{{"type": "path",    "title":    "$lvar(531)","desc": "$lvar(532)","section": "ORCA","key": "rootpath"}},\n' \
                        u'{{"type": "scrolloptions","title": "$lvar(508)","desc": "$lvar(509)","section": "ORCA","key": "skin","options":[{skinlist}]}},\n' \
                        u'{{"type": "scrolloptions","title": "$lvar(634)","desc": "$lvar(635)","section": "ORCA","key": "sounds","options":[{soundlist}]}},\n' \
                        u'{{"type": "scrolloptions","title": "$lvar(561)","desc": "$lvar(562)","section": "ORCA","key": "interface","options":[{interfacelist}] }},\n' \
                        u'{{"type": "scrolloptionsoptions","title": "$lvar(577)","desc": "$lvar(578)","section": "ORCA","key": "script","options":[{scriptmanagestrings}] , "suboptions":[[{scriptlistconfig}],[{scriptlist}]],"alwaysonchange":"1","novaluechange":"1" }},\n' \
                        u'{{"type": "bool","title": "$lvar(510)","desc": "$lvar(511)","section": "ORCA","key": "initpagesatstartup"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(512)","desc": "$lvar(513)","section": "ORCA","key": "delayedpageinitinterval","min":"0", "max":"60" ,"roundpos":"0"}},\n' \
                        u'{{"type": "bool","title": "$lvar(514)","desc": "$lvar(515)","section": "ORCA","key": "ignoreatlas"}},\n' \
                        u'{{"type": "scrolloptions","title": "$lvar(518)","desc": "$lvar(519)", "section": "ORCA","key": "stretchmode","options":["CENTER","TOPLEFT","STRETCH","RESIZE"]}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(535)","desc": "$lvar(536)", "section": "ORCA","key": "screensize","min":"0", "max":"20" ,"roundpos":"1"}},\n' \
                        u'{{ "type": "title","title":  "$lvar(520)" }},\n' \
                        u'{{"type": "bool","title": "$lvar(567)","desc": "$lvar(568)","section": "ORCA","key": "vibrate"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(525)","desc": "$lvar(526)","section": "ORCA","key": "startrepeatdelay","min":"0.2", "max":"3" ,"roundpos":"2"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(527)","desc": "$lvar(528)","section": "ORCA","key": "contrepeatdelay","min":"0.2", "max":"3" ,"roundpos":"2"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(537)","desc": "$lvar(538)","section": "ORCA","key": "longpresstime","min":"0", "max":"3" ,"roundpos":"2"}},\n' \
                        u'{{ "type": "title","title":  "$lvar(540)" }},\n' \
                        u'{{"type": "bool","title": "$lvar(541)","desc": "$lvar(542)","section": "ORCA","key": "checkfornetwork"}},\n' \
                        u'{{"type": "scrolloptions","title": "$lvar(545)","desc": "$lvar(546)","section": "ORCA","key": "checknetworktype","options":["ping","system"]}},\n' \
                        u'{{"type": "string","title": "$lvar(543)","desc": "$lvar(544)","section": "ORCA","key": "checknetworkaddress"}},\n' \
                        u'{{ "type": "title","title": "$lvar(550)" }},\n' \
                        u'{{"type": "bool","title": "$lvar(551)","desc": "$lvar(552)","section": "ORCA","key": "clockwithseconds"}},\n' \
                        u'{{"type": "bool","title": "$lvar(553)","desc": "$lvar(554)","section": "ORCA","key": "longdate"}},\n' \
                        u'{{"type": "bool","title": "$lvar(555)","desc": "$lvar(556)","section": "ORCA","key": "longday"}},\n' \
                        u'{{"type": "bool","title": "$lvar(557)","desc": "$lvar(558)","section": "ORCA","key": "longmonth"}},\n' \
                        u'{{ "type": "title","title":  "$lvar(590)" }},\n' \
                        u'{{"type": "numericslider","title": "$lvar(591)","desc": "$lvar(592)","section": "ORCA","key": "soundvolume_startup",        "min":"0", "max":"100" ,"roundpos":"0"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(593)","desc": "$lvar(594)","section": "ORCA","key": "soundvolume_shutdown",       "min":"0", "max":"100" ,"roundpos":"0"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(595)","desc": "$lvar(596)","section": "ORCA","key": "soundvolume_error",          "min":"0", "max":"100" ,"roundpos":"0"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(597)","desc": "$lvar(598)","section": "ORCA","key": "soundvolume_message",        "min":"0", "max":"100" ,"roundpos":"0"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(599)","desc": "$lvar(600)","section": "ORCA","key": "soundvolume_question",       "min":"0", "max":"100" ,"roundpos":"0"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(601)","desc": "$lvar(602)","section": "ORCA","key": "soundvolume_notification",   "min":"0", "max":"100" ,"roundpos":"0"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(603)","desc": "$lvar(604)","section": "ORCA","key": "soundvolume_ring",           "min":"0", "max":"100" ,"roundpos":"0"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(605)","desc": "$lvar(606)","section": "ORCA","key": "soundvolume_success",        "min":"0", "max":"100" ,"roundpos":"0"}},\n' \
                        u'{{"type": "numericslider","title": "$lvar(607)","desc": "$lvar(608)","section": "ORCA","key": "soundvolume_click",          "min":"0", "max":"100" ,"roundpos":"0"}}\n' \
                        u']'.format( \
                        languagelist            = BuildSettingOptionList(Globals.aLanguageList), \
                        localeslist             = BuildSettingOptionList(Globals.oLanguage.oLocales.oLocalesEntries), \
                        definitionlist          = BuildSettingOptionListDict(this.dDefinitionReps), \
                        definitionmanagestrings = BuildSettingOptionList(['$lvar(675)','$lvar(676)','$lvar(677)','$lvar(678)']), \
                        scriptmanagestrings     = BuildSettingOptionList(['$lvar(516)','$lvar(517)']), \
                        skinlist                = BuildSettingOptionList(Globals.aSkinList), \
                        soundlist               = BuildSettingOptionList(Globals.oSound.aSoundsList), \
                        scriptlistconfig        = BuildSettingOptionList(Globals.oScripts.aScriptNameListWithConfig), \
                        scriptlist              = BuildSettingOptionList(Globals.oScripts.aScriptNameList), \
                        interfacelist           = BuildSettingOptionList(aInterfaceList))

    # definitionlist          = BuildSettingOptionList(Globals.aDefinitionList), \

    uOrcaSettingsJSON=ReplaceVars(uOrcaSettingsJSON)

    #Logger.debug(uOrcaSettingsJSON)
    return uOrcaSettingsJSON

def BuildSettingsStringDefinitionList():
    """ Build the settings for the ORCA DefinitionList """

    uMainSetting       = u''
    uSubSetting        = u''
    uOrcaSettingsJSON  = u''

    aDefinitionListSorted=sorted(Globals.oDefinitions, key=lambda entry: entry.uDefPublicTitle)

    for oDef in aDefinitionListSorted:
        if len(oDef.dDefinitionSettingsJSON)>0:
            uPublicTitle=oDef.uDefPublicTitle
            iStart =uPublicTitle.find( '[' )
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

def BuildSettingsStringInfo():
    """ Build the settings for the ORCA Info panel """
    uOrcaSettingsJSON  =u'[{"type": "title","title": "$lvar(586)" },\n' \
                        u'{"type": "info","title": "$lvar(587)","section": "ORCA","info":"$var(VERSION)"}\n,' \
                        u'{"type": "info","title": "$lvar(588)","section": "ORCA","info":"$var(AUTHOR)"}\n,' \
                        u'{"type": "info","title": "$lvar(589)","section": "ORCA","info":"$var(SUPPORT)"}\n,' \
                        u'{"type": "buttons","title": "$lvar(653)","desc": "$lvar(654)","section": "ORCA","key": "button_show_logfile","buttons":[{"title":"$lvar(655)","id":"button_show_logfile"}]},\n' \
                        u'{"type": "buttons","title": "$lvar(660)","desc": "$lvar(661)","section": "ORCA","key": "button_show_licensefile","buttons":[{"title":"$lvar(662)","id":"button_show_licensefile"}]},\n' \
                        u'{"type": "buttons","title": "$lvar(609)","desc": "$lvar(610)","section": "ORCA","key": "button_show_credits","buttons":[{"title":"$lvar(611)","id":"button_show_credits"}]},\n' \
                        u'{"type": "buttons","title": "$lvar(547)","desc": "$lvar(548)","section": "ORCA","key": "button_show_powerstati","buttons":[{"title":"$lvar(549)","id":"button_show_powerstati"}]},\n' \
                        u'{"type": "title","title":"$lvar(652)"}\n,' \
                        u'{"type": "info","title": "$lvar(587)","section": "ORCA","info":"$var(DEFINITIONVERSION)"}\n,' \
                        u'{"type": "info","title": "$lvar(588)","section": "ORCA","info":"$var(DEFINITIONAUTOR)"}\n,' \
                        u'{"type": "info","title": "$lvar(589)","section": "ORCA","info":"$var(DEFINITIONSUPPORT)"}\n,' \
                        u'{"type": "buttons","title": "$lvar(657)","desc": "$lvar(658)","section": "ORCA","key": "button_show_installationhint","buttons":[{"title":"$lvar(659)","id":"button_show_installationhint"}]}\n' \
                        u']'
    uOrcaSettingsJSON=ReplaceVars(uOrcaSettingsJSON)

    #Logger.debug(uOrcaSettingsJSON)
    return uOrcaSettingsJSON

def BuildSettingsStringInfoSmall():
    """ Build the settings for the ORCA tools """
    uOrcaSettingsJSON  =u'[{"type": "title","title": "Info" },\n' \
                        u'{"type": "buttons","title": "Show Logfile","desc": "Show Orca Logfile","section": "ORCA","key": "button_show_logfile","buttons":[{"title":"Show Logfile","id":"button_show_logfile"}]}\n' \
                        u']'

    #Logger.debug(uOrcaSettingsJSON)
    return uOrcaSettingsJSON


def BuildSettingsStringTools():
    """ Build the settings for the ORCA tools """
    uOrcaSettingsJSON  =u'[{ "type": "title","title": "$lvar(573)" },\n' \
                        u'{"type": "buttons","title": "$lvar(574)","desc": "$lvar(575)","section": "ORCA","key": "button_clear_atlas","buttons":[{"title":"$lvar(576)","id":"button_clear_atlas"}]},\n' \
                        u'{ "type": "title","title": "$lvar(633)" },\n' \
                        u'{"type": "buttons","title": "$lvar(720)","desc": "$lvar(721)","section": "ORCA","key": "button_discover_results","buttons":[{"title":"$lvar(722)","id":"button_discover_results"}]},\n' \
                        u'{"type": "buttons","title": "$lvar(760)","desc": "$lvar(761)","section": "ORCA","key": "button_discover_rediscover","buttons":[{"title":"$lvar(722)","id":"button_discover_rediscover"},{"title":"$lvar(729)","id":"button_discover_rediscover_force"}]}]'

    uOrcaSettingsJSON=AddScriptSetting(uSettingName="ORCA",uSettingPage=ReplaceVars("$lvar(572)"),uOrcaSettingsJSON=uOrcaSettingsJSON)
    uOrcaSettingsJSON=ReplaceVars(uOrcaSettingsJSON)

    return uOrcaSettingsJSON

def BuildSettingsStringOnlineResources():
    """ Build the settings for the ORCA Online Resource """

    iCountBlanks=0
    uReps=''
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
                        u']' %(uReps)


    if len(Globals.dInstalledReps)>0:
        uOrcaSettingsJSON=uOrcaSettingsJSON[:-1]

        aSubList=[]
        for (key,val) in iteritems(Globals.dInstalledReps):
            aSubList.append(val)
        aSubList.sort(key = lambda x: x.uType)

        uOldType=''
        uOrcaSettingsJSON+=u',{ "type": "title","title": "$lvar(679)" },\n'
        for oRep in aSubList:
            if uOldType!=oRep.uType:
                uOldType=oRep.uType
                uName="???"
                for tTup in Globals.aRepNames:
                    if tTup[1]==oRep.uType:
                        uName=tTup[0]
                uOrcaSettingsJSON+=u'{ "type": "title","title": "-> %s" },\n' %(uName)

            uOrcaSettingsJSON+=u'{"type": "buttons","title": "%s","desc": "$lvar(751): %s","section": "ORCA","key": "button_installed_reps","buttons":[{"title":"$lvar(752)","id":"button_updaterep:%s:%s"}]},\n' % (oRep.uName,ToStringVersion(oRep.iVersion),oRep.uType,oRep.uName)
        uOrcaSettingsJSON=uOrcaSettingsJSON[:-2]
        uOrcaSettingsJSON+=u']'



    uOrcaSettingsJSON=uOrcaSettingsJSON.replace("'","\'")

    uOrcaSettingsJSON=AddScriptSetting(uSettingName="TOOLS",uSettingPage=ReplaceVars("$lvar(699)"),uOrcaSettingsJSON=uOrcaSettingsJSON)
    uOrcaSettingsJSON=ReplaceVars(uOrcaSettingsJSON)


    #Logger.debug(uOrcaSettingsJSON)
    return uOrcaSettingsJSON


def BuildSmallSettingsString():
    """ just build the small settings """
    uOrcaSettingsJSON=u'[{ "type": "title","title": "Initialisation" },\n' \
                      u'{"type": "path","title":    "Path to Orca Files","desc": "Sets the file root path for Orca files (Definitions, etc)","section": "ORCA","key": "rootpath"}\n' \
                      u']'
    return uOrcaSettingsJSON

def BuildSettingsStringPowerStatus():
    """ Build the settings for the Power Stati """

    aPowerListDevices    = []
    aPowerListActivities = []

    uPowerStatusJSON=u'['

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



