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

from xml.etree.ElementTree          import fromstring

from copy                           import copy

from kivy.logger                    import Logger

from ORCA.Cookies                   import Var_Load
from ORCA.definition.Definition     import aLoadedFontFiles
from ORCA.definition.Definition     import cDefinition
from ORCA.definition.DefinitionContext import SetDefinitionContext
from ORCA.definition.DefinitionPathes import cDefinitionPathes
from ORCA.definition.Definition     import LoadFontFromXML
from ORCA.RepManagerEntry           import cRepManagerEntry
from ORCA.utils.ConfigHelpers       import Config_GetDefault_Str
from ORCA.utils.FileName            import cFileName
from ORCA.utils.CachedFile          import CachedFile
from ORCA.utils.LogError            import LogError
from ORCA.utils.XML                 import GetXMLBoolAttribute
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import GetXMLTextValue
from ORCA.utils.XML                 import Orca_FromString
from ORCA.utils.XML                 import LoadXMLFile
from ORCA.vars.Replace              import ReplaceVars
from ORCA.vars.Access               import SetDefVar
from ORCA.vars.Access               import SetVar
from ORCA.utils.TypeConvert         import ToDic
from ORCA.utils.TypeConvert         import UnEscapeUnicode
from ORCA.utils.TypeConvert         import EscapeUnicode
from ORCA.utils.TypeConvert         import ToOrderedDic
from ORCA.Cookies                   import GetCookieValue
from ORCA.definition.DefinitionVars import cDefinitionVars
from ORCA.definition.DefinitionContext import SetDefinitionPathes
from ORCA.definition.DefinitionContext import RestoreDefinitionContext
from ORCA.vars.Access               import GetVar

import ORCA.Globals as Globals

__all__ = ['cDefinitions','GetDefinitionFileNameByName']

class cDefinitions(object):
    """ Class which holds all definitions, as related functions, iterable """
    def __init__(self):
        self.dDefinitionList_Dict   = {}
        self.aDefinitionList_List   = []
        self.aDefinitionSettingVars = []
        self.dInitInterfaceSettings = {}
        self.aSettingsVars          = []
        self.dSettingsDefaults      = {}
        self.uInstallationHint      = u''
        self.uDefinitionAutor       = u''
        self.uDefinitionSupport     = u''
        self.uDefinitionVersion     = u''
        self.dSettingFormatStrings  = {}
        self.dInstallationsHints    = {}

    def __iter__(self):
        return iter(self.aDefinitionList_List)

    def __len__(self):
        return len(self.aDefinitionList_List)

    def __getitem__(self,key):
        try:
            if isinstance(key,int):
                return self.aDefinitionList_List[key]
            else:
                return self.dDefinitionList_Dict[key]
        except Exception as e:
            LogError("Wrong Definition Name or Index given:"+str(key),e)
            return None

    def get(self,key):
        """ returns a dinition object idetified by alias name """
        return self.dDefinitionList_Dict.get(key)

    def __contains__(self,key):
        return key in self.dDefinitionList_Dict

    def InitVars(self):
        """ (Re) Initialize all vars of the definitions """
        self.dDefinitionList_Dict.clear()
        del self.aDefinitionList_List[:]
        del self.aDefinitionSettingVars[:]
        self.dInitInterfaceSettings.clear()
        self.dSettingsDefaults.clear()
        self.dInstallationsHints.clear()
        del self.aSettingsVars[:]
        self.uInstallationHint      = u''
        self.uDefinitionAutor   = u''
        self.uDefinitionSupport = u''
        self.uDefinitionVersion = u''
        self.dSettingFormatStrings={'options'       :',{{"type":"{type}","title":"{title}","desc":"{description}","section":"{section}","key":"{var}","allowtextinput":"{allowtextinput}","options":[{options}]}}',
                                    'numericslider' :',{{"type":"{type}","title":"{title}","desc":"{description}","section":"{section}","key":"{var}","min":"{min}", "max":"{max}","roundpos":"{roundpos}"}}',
                                    'title'         :',{{"type":"{type}","title":"{title}"}}',
                                    'buttons'       :',{{"type":"{type}","title":"{title}","desc":"{description}","section":"{section}","key":"{var}","buttons":{buttons}}}',
                                    'default'       :',{{"type":"{type}","title":"{title}","desc":"{description}","section":"{section}","key":"{var}"}}'}
        self.dSettingFormatStrings['scrolloptions']=self.dSettingFormatStrings['options']

    def DumpDefinitionList(self):
        """ Dumps a list af all available definition (alias) names """
        LogError(u'Available Definition Names:')
        for uKey in self.dDefinitionList_Dict:
            LogError(u'Available Name:'+uKey)

    def AddDefinition(self,oDefinition):
        """ adds a definition member to the list of definitions """
        self.aDefinitionList_List.append(oDefinition)
        self.dDefinitionList_Dict[oDefinition.uAlias] = oDefinition

    def LoadLanguages(self,fSplashScreenPercentageStartValue):
        """ Loads the language files for the definitions """
        # Scheduling Loading Definition Languages

        fSplashScreenPercentageRange=10.0
        fPercentage=fSplashScreenPercentageStartValue
        fPercentageStep=fSplashScreenPercentageRange/len(self.dDefinitionList_Dict)

        aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message to Load the Language','string':'showsplashtext','maintext':'$lvar(413)'}])
        for oDefinition in reversed(self.aDefinitionList_List):
            fPercentage=fPercentage+fPercentageStep
            if oDefinition.bImportLanguages:
                aCommands=[{'name':'Update Percentage and DefinitionName','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)}]
                if oDefinition.oDefinitionPathes.oFnDefinitionLanguageFallBack.Exists():
                    aCommands.append({'name':'Load Default Language File','string':'loadlanguages','languagefilename':oDefinition.oDefinitionPathes.oFnDefinitionLanguageFallBack.string,'definition':oDefinition.uName,'definitionalias':oDefinition.uAlias})
                if not Globals.uLanguage==u'English':
                    oDefinition.oDefinitionPathes.LanguageChange()
                    if oDefinition.oDefinitionPathes.oFnDefinitionLanguage.Exists():
                        aCommands.append({'name':'Load Requested Language File','string':'loadlanguages','languagefilename':oDefinition.oDefinitionPathes.oFnDefinitionLanguage.string,'definition':oDefinition.uName,'definitionalias':oDefinition.uAlias})
                if len(aCommands)>1:
                    Globals.oEvents.AddToSimpleActionList(aActions,aCommands)

        Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

    def LoadActions(self,fSplashScreenPercentageStartValue):
        """ Loads the action files for the definitions """

        fSplashScreenPercentageRange=10.0
        fPercentage=fSplashScreenPercentageStartValue
        fPercentageStep=fSplashScreenPercentageRange/len(self.dDefinitionList_Dict)

        aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message we load Actions','string':'showsplashtext','maintext':'$lvar(403)'}])
        for oDefinition in reversed(self.aDefinitionList_List):
            fPercentage=fPercentage+fPercentageStep
            if oDefinition.bImportActions:
                aCommands= [{'name': 'Update Percentage and Definition Name', 'string': 'showsplashtext', 'subtext': oDefinition.uDefPublicTitle, 'percentage': str(fPercentage)},
                            {'name': 'Load the Definition Actions', "string": "loaddefinitionactions", "definitionname": oDefinition.uAlias}]
                if len(aCommands)>1:
                    Globals.oEvents.AddToSimpleActionList(aActions,aCommands)

        Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

    def LoadFonts(self,uDefinitionName,fSplashScreenPercentageStartValue):
        """ Load the fonts for a single definition """

        if uDefinitionName=="":
            fSplashScreenPercentageRange=10.0
            fPercentage=fSplashScreenPercentageStartValue
            fPercentageStep=fSplashScreenPercentageRange/(len(self.dDefinitionList_Dict)+1)

            # Scheduling Loading Definition Fonts
            aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message we load Fonts','string':'showsplashtext','maintext':'Loading Definition Fonts'}])

            #for definition
            for oDefinition in reversed(self.aDefinitionList_List):
                fPercentage=fPercentage+fPercentageStep
                Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Update Percentage and Definition Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)},
                                                                         {'name':'Load Fonts for Definition','string':'loaddefinitionfonts','definitionname':oDefinition.uAlias}])
            '''
            #Global
            fPercentage=fPercentage+fPercentageStep
            Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Update Percentage for ORCA','string':'showsplashtext','subtext':'ORCA','percentage':str(fPercentage)},
                                                           {'name':'Load Fonts for Orca','string':'loaddefinitionfonts','definitionname':'ORCA'}])
            '''

            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        elif uDefinitionName=="ORCA":
            aFontsFolders = Globals.oPathFonts.GetFolderList(bFullPath=True)
            for uFontFolder in aFontsFolders:
                oFnFontDefinition = cFileName('').ImportFullPath(uFontFolder+u"/fonts.xml")
                if not oFnFontDefinition.string in aLoadedFontFiles:
                    Logger.info(u'Loading Global Fonts: '+uFontFolder)
                    aLoadedFontFiles.append(oFnFontDefinition.string)
                    oET_Root = LoadXMLFile(oFnFontDefinition)
                    LoadFontFromXML(oET_Root)
        else:
            self.dDefinitionList_Dict[uDefinitionName].LoadFonts()

    def LoadGestures(self,uDefinitionName,fSplashScreenPercentageStartValue):
        """ Loads the gestures for a single definition, or creates the queue entries """
        if uDefinitionName=="":
            fSplashScreenPercentageRange=10.0
            fPercentage=fSplashScreenPercentageStartValue
            fPercentageStep=fSplashScreenPercentageRange/len(self.aDefinitionList_List)

            # Scheduling Loading Definition Gestures
            aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message we load Gestures','string':'showsplashtext','maintext':'$lvar(404)'}])
            for oDefinition in reversed(self.aDefinitionList_List):
                fPercentage=fPercentage+fPercentageStep
                if oDefinition.bImportActions:
                    Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Update Percentage and Definition Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)},
                                                                             {'name':'Load Gestures for Definition','string':'loaddefinitiongestures','definitionname':oDefinition.uAlias}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        else:
            self.dDefinitionList_Dict[uDefinitionName].LoadGestures()

    def GetUsedDefinitions(self):
        """ Gets a list of all used definitions """
        Logger.debug (u'Collecting used definitions...')
        fSplashScreenPercentageRange=10.0
        Globals.oTheScreen.LogToSplashScreen("Collecting used definitions",fSplashScreenPercentageRange)
        self.__GetUsedDefinitions_Sub(Globals.uDefinitionName,True,True,True,True, Globals.oTheScreen.uDefName, Globals.uDefinitionName,cDefinitionVars(),u'' )
        Globals.uDefinitionContext="" # to ensure, root definitioncontext is loaded
        RestoreDefinitionContext()

    def __GetUsedDefinitions_Sub(self,uDefinitionName,bImportActions,bImportLanguages,bImportPages,bImportSettings, uParentDefinitionName, uParentDefinitionAlias,aDefinitionVarsFromParent, uAlias):

        aAdditionalDefVars={}

        if not uAlias in self.dDefinitionList_Dict:
            oDefinitionPathes=cDefinitionPathes(uDefinitionName)
            SetVar(uVarName = "DEFINITIONPATH[%s]" %  (uDefinitionName), oVarValue = oDefinitionPathes.oPathDefinition.string)
            SetVar(uVarName = "DEFINITIONPATHSKINELEMENTS[%s]" % (uDefinitionName), oVarValue=oDefinitionPathes.oPathDefinitionSkinElements.string)
            Globals.dDefinitionPathes[uDefinitionName]=oDefinitionPathes
            SetDefinitionPathes(uDefinitionName)

            oFnDefinition=Globals.oDefinitionPathes.oFnDefinition
            Logger.debug (u'TheScreen: Load Definition XmlFile:'+oFnDefinition)
            oDefinition                            = cDefinition(uDefinitionName,self)
            oDefinition.uParentDefinitionName      = uParentDefinitionName
            oDefinition.bImportActions             = bImportActions
            oDefinition.bImportLanguages           = bImportLanguages
            oDefinition.bImportPages               = bImportPages
            oDefinition.bImportSettings            = bImportSettings
            oDefinition.oDefinitionVarsFromParent  = aDefinitionVarsFromParent

            #we read the definitionvars first with raw funtions
            sET_Data = CachedFile(Globals.oDefinitionPathes.oFnDefinition)
            oET_Root = fromstring(sET_Data)
            oRef = oET_Root.find('def_parameter')
            # And merge / Replace the existing Vars
            oDefinition.oDefinitionVars.clear()
            oDefinition.oDefinitionVars.update(ToOrderedDic(GetXMLTextValue(oRef,u'definitionvars',False,u'{}')))

            if len(aDefinitionVarsFromParent)>0:
                for uVarName in oDefinition.oDefinitionVars:
                    if uVarName in oDefinition.oDefinitionVarsFromParent:
                        oDefinition.oDefinitionVars[uVarName]=oDefinition.oDefinitionVarsFromParent[uVarName]
                    else:
                        Logger.warning("Importing definition %s from %s: Definition varname not passed: '%s', using default %s" % (oDefinition.uName, uParentDefinitionName, uVarName, oDefinition.oDefinitionVars[uVarName]))
                for uVarName in aDefinitionVarsFromParent:
                    if not uVarName in oDefinition.oDefinitionVars:
                        oDefinition.oDefinitionVars[uVarName]=oDefinition.oDefinitionVarsFromParent[uVarName]
                        aAdditionalDefVars[uVarName]=oDefinition.oDefinitionVarsFromParent[uVarName]

            for uKey in oDefinition.oDefinitionVars:
                uVar=oDefinition.oDefinitionVars[uKey]
                if "$cookie(" in uVar:
                    uValue=GetCookieValue(uVar)
                    oDefinition.oDefinitionVars[uKey]=uValue

            if uAlias==u'':
                # this works on all python versions
                for uKey in oDefinition.oDefinitionVars:
                    uAlias=oDefinition.oDefinitionVars[uKey]
                    break

            if uAlias=='':
                uAlias=uDefinitionName
                oDefinition.uDefPublicTitle=uDefinitionName
                #create a default alias def var
                uAliasDefVar="definition_alias_"+uAlias
                if oDefinition.oDefinitionVars.get(uAliasDefVar) is None:
                    SetDefVar(uVarName = uAliasDefVar,uVarValue = uAlias,dArray = oDefinition.oDefinitionVars)
            else:
                oDefinition.uDefPublicTitle="%s [%s]" % (uAlias,uDefinitionName)

            oDefinition.uAlias                     = uAlias

            if not uAlias in self.dDefinitionList_Dict:
                # create defvars for import pages
                aTmpDefinitionVars=copy(oDefinition.oDefinitionVars)
                for uVar in aTmpDefinitionVars:
                    if not uVar.endswith("_IMPORTPAGES"):
                        if bImportPages:
                            SetDefVar(uVarName = uVar + "_IMPORTPAGES",uVarValue = "1",dArray = oDefinition.oDefinitionVars)
                        else:
                            SetDefVar(uVarName = uVar+"_IMPORTPAGES",uVarValue = "0",dArray = oDefinition.oDefinitionVars)


                #and now again with adjusted definitionvars
                oET_Root = Orca_FromString(sET_Data,oDefinition,"root")
                oDefinition.oET_Root            = oET_Root
                oDefinition.sET_Data            = sET_Data

                self.AddDefinition(oDefinition)

                oXMLIncludes       = oET_Root.find('definitionimports')
                if oXMLIncludes is not None:
                    for oXMLInclude in oXMLIncludes.findall('definition'):
                        uDefinitionNameImp  = GetXMLTextValue(oXMLInclude,u'',True,'')
                        bImportActionsImp   = GetXMLBoolAttribute(oXMLInclude,u'importactions',False,False)
                        bImportLanguagesImp = GetXMLBoolAttribute(oXMLInclude,u'importlanguages',False,False)
                        bImportPagesImp     = GetXMLBoolAttribute(oXMLInclude,u'importpages',False,False)
                        bImportSettingsImp  = GetXMLBoolAttribute(oXMLInclude,u'importsettings',False,False)
                        uAliasImp           = GetXMLTextAttribute(oXMLInclude,u'alias',False,'')
                        aDefinitionVarsImp  = cDefinitionVars()
                        aDefinitionVarsImp.update(ToDic(GetXMLTextAttribute(oXMLInclude,u'definitionvars',False,{})))

                        # Pass Through of additional Definitionvars
                        for uVarName in aAdditionalDefVars:
                            if not uVarName in aDefinitionVarsImp:
                                aDefinitionVarsImp[uVarName]=aAdditionalDefVars[uVarName]

                        self.__GetUsedDefinitions_Sub(uDefinitionNameImp,bImportActionsImp,bImportLanguagesImp,bImportPagesImp,bImportSettingsImp,oDefinition.uName, oDefinition.uAlias,aDefinitionVarsImp, uAliasImp)
            else:
                Logger.debug (u'GetUsedDefinitions: Skipping duplicate xml %s [%s]' %(uAlias,uDefinitionName))
        else:
            Logger.debug (u'GetUsedDefinitions: Skipping duplicate xml %s [%s]' %(uAlias,uDefinitionName))


    def ParseXmlFiles(self,uDefinitionName,fSplashScreenPercentageStartValue):
        """ Parses the definition file for a single definition """
        fSplashScreenPercentageRange=10.0

        if not uDefinitionName:
            fPercentage=fSplashScreenPercentageStartValue
            fPercentageStep=fSplashScreenPercentageRange/len(self.aDefinitionList_List)

            aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message that we parse the XML Files','string':'showsplashtext','maintext':'$lvar(412)'}])
            # Scheduling Parsing of Definition XML Files
            for oDefinition in self.aDefinitionList_List:
                fPercentage=fPercentage+fPercentageStep
                Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Update Percentage and Definitioon Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)},
                                                                         {'name':'And parse the definition','string':'parsedefinitionxml','definitionname':oDefinition.uAlias}])

            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        else:
            self.dDefinitionList_Dict[uDefinitionName].LoadXMLFile()

    def InitInterFaceSettings(self,uDefinitionName,fSplashScreenPercentageStartValue):
        """ Init The Interface settings of a definition  """

        fSplashScreenPercentageRange=10.0

        if not uDefinitionName:
            # Scheduling Initialize Interface settings
            fPercentage=fSplashScreenPercentageStartValue
            fPercentageStep=fSplashScreenPercentageRange/len(self.aDefinitionList_List)

            aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message the we initialize the interfaces','string':'showsplashtext','maintext':'$lvar(418)'}])

            for oDefinition in reversed(self.aDefinitionList_List):
                fPercentage=fPercentage+fPercentageStep
                Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Update Percentage and Interface Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)},
                                                                         {'name':'Initialize the Interface','string':'initinterfacesettings','definitionname':oDefinition.uAlias}
                                                                        ])
            Globals.oEvents.AddToSimpleActionList(aActions,    [{'name':'Show Message the we write all interface settings','string':'showsplashtext','subtext':"$lvar(456)",'percentage':str(fPercentage)},
                                                                         {'name':'Write all interface settings','string':'initinterfacesettings','definitionname':'WRITEALLSETTINGS'}
                                                                        ])

            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

        elif uDefinitionName=="WRITEALLSETTINGS":
            for uInterfaceName in self.dInitInterfaceSettings:
                if uInterfaceName in Globals.oInterFaces.oInterfaceList:
                    oInterface=Globals.oInterFaces.dInterfaces.get(uInterfaceName)
                    if oInterface is None:
                        Logger.info('Need to load unrecognized Interface [%s] for configuration' % (uInterfaceName))
                        Globals.oInterFaces.LoadInterface(uInterfaceName)
                        oInterface=Globals.oInterFaces.dInterfaces.get(uInterfaceName)
                    if oInterface is not None:
                        for uConfigurationName in self.dInitInterfaceSettings[uInterfaceName]:
                            oInterface.oInterFaceConfig.WriteDefinitionConfig(uSectionName = uConfigurationName ,dSettings = self.dInitInterfaceSettings[uInterfaceName][uConfigurationName])
                else:
                    Logger.warning('Interface [%s] not on device, so it will not be configured!' %(uInterfaceName))

        else:
            oDef=self.dDefinitionList_Dict[uDefinitionName]
            SetDefinitionContext(oDef.uName)
            oXMLRoot=oDef.oET_Root
            oDef.InitInterFaceSettings(oXMLRoot)
            RestoreDefinitionContext()

    def LoadParameter(self):
        """ Loads the parameter for all definitiona  """
        for oDef in self.aDefinitionList_List:
            oDef.LoadParameter()

    def LoadSettings(self,uDefinitionName,fSplashScreenPercentageStartValue):
        """ Loads the settimgs for a specific definition """

        fSplashScreenPercentageRange=10.0

        if not uDefinitionName:
            # Scheduling Loading Definition Settings
            fPercentage=fSplashScreenPercentageStartValue
            fPercentageStep=fSplashScreenPercentageRange/len(self.aDefinitionList_List)

            aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message that we load the settings','string':'showsplashtext','maintext':'$lvar(414)'}])
            for oDefinition in reversed(self.aDefinitionList_List):
                fPercentage=fPercentage+fPercentageStep
                Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Update Percentage and Definition Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)},
                                                                         {'name':'Load the settings for the Definition','string':'loaddefinitionsettings','definitionname':oDefinition.uAlias}
                                                                        ])

            # Lets parse them (to init all default vars
            Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Parse all Settings and set defaults','string':'loaddefinitionsettings','definitionname':'PARSESETTINGS'}])
            #Execute the Queue
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
            #just to put it somewhere
            for uHintKey in self.dInstallationsHints:
                self.uInstallationHint+=self.dInstallationsHints[uHintKey]
            SetVar(uVarName = "INSTALLATIONHINT", oVarValue = self.uInstallationHint)

        else:
            oDef=self.dDefinitionList_Dict[uDefinitionName]
            SetDefinitionContext(oDef.uName)
            oDef.ParseSettings()
            RestoreDefinitionContext()

    def CreateSettingsJSONString(self):

        """ Creates the json string for the settings dialog AND reads/writes the defaults to the config file """

        uSection = Globals.uDefinitionName
        uSection = uSection.replace(u' ', u'_')
        uVisSection=uSection
        oConfig=Globals.oDefinitionConfigParser

        for oDef in self.aDefinitionList_List:


            uVisSection=oDef.uName
            if len(oDef.aDefinitionsSettings)>0:
                uTitle = oDef.uDefPublicTitle
                for aSetting in oDef.aDefinitionsSettings:
                    uType = aSetting['type']

                    if uType=="section":
                        uVisSection=aSetting['title']
                        continue
                    if oDef.dDefinitionSettingsJSON.get(uVisSection) is None:
                        oDef.dDefinitionSettingsJSON[uVisSection]=u'[{ "type": "title","title": "'+uTitle+'" }\n'
                        #oDef.dDefinitionSettingsJSON[uVisSection]=u'['

                    aSetting['section']=uSection
                    uFormatString=self.dSettingFormatStrings.get(uType)
                    if uFormatString is None:
                        uFormatString=self.dSettingFormatStrings['default']
                    oDef.dDefinitionSettingsJSON[uVisSection]+=uFormatString.format(**aSetting)
                    uVar    = aSetting['var']
                    uDefault=self.dSettingsDefaults[uVar]
                    #uDefault=ReplaceVars(uDefault)
                    #todo temporary hack to bypass configparser unicode bug
                    uDefault = EscapeUnicode(uDefault)
                    #check for cookies
                    uCookie=aSetting["cookie"]
                    if uCookie!=u"" and uDefault=="":
                        uDefault=Var_Load(uCookie,"","")

                    # parse definition settings into vars
                    uValue   = ReplaceVars(Config_GetDefault_Str(oConfig,uSection, uVar,uDefault))

                    #todo temporärer hack to bypass configparser unicode bug
                    uValue = UnEscapeUnicode(uValue)
                    # Logger.debug("Loading Definition Config Setting into var: [%s]=[%s]" %(uVar,uValue))
                    SetVar(uVarName = uVar, oVarValue = uValue)
                    self.aDefinitionSettingVars.append(uVar)
            for uVisSection in oDef.dDefinitionSettingsJSON:
                if len(oDef.dDefinitionSettingsJSON[uVisSection])>0:
                    oDef.dDefinitionSettingsJSON[uVisSection]+=u']'
        oConfig.write()

    def FindDefinitionAliasForInterfaceConfiguration(self,uInterFaceName,uConfigName):
        for oDefinition in self.aDefinitionList_List:
            uAddVar = oDefinition.uAlias
            uDefinitionInterFace=GetVar(uAddVar+"_INTERFACE_MAIN")
            if uDefinitionInterFace == uInterFaceName:
                uDefinitionConfig = GetVar(uAddVar + "_CONFIGNAME_MAIN")
                if uDefinitionConfig == uConfigName:
                    return oDefinition.uAlias
        return ""

def GetDefinitionFileNameByName(uDefinitionName):
    """
        gets the definition file name if the definition description is available
    """
    try:
        aDefinitionList = Globals.oPathDefinitionRoot.GetFolderList()
        for uDir in aDefinitionList:
            if not uDir == 'shared_documents':
                oFn = cFileName(Globals.oPathDefinitionRoot + uDir) + u"definition.xml"
                oRepManEntry = cRepManagerEntry(oFn)
                oRepManEntry.ParseFromXML()
                uDefName = oRepManEntry.oRepEntry.uName
                if uDefName == uDefinitionName:
                    return uDir
        return ''

    except Exception as e:
        LogError(u'GetDefinitionFileNameByName: Error:Load Definition XmlFile:', e)
