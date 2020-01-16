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

import                              logging
from typing                         import List
from typing                         import Dict
from typing                         import Union
from collections                    import OrderedDict
from xml.etree.ElementTree          import fromstring
from xml.etree.ElementTree          import Element
from copy                           import copy

from kivy.logger                    import Logger
from kivy.config                    import Config

from ORCA.Cookies                   import Var_Load
from ORCA.definition.Definition     import aLoadedFontFiles
from ORCA.definition.Definition     import cDefinition
from ORCA.definition.DefinitionContext import SetDefinitionContext
from ORCA.definition.DefinitionPathes import cDefinitionPathes
from ORCA.definition.Definition     import LoadFontFromXML
from ORCA.download.RepManagerEntry import cRepManagerEntry
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
from ORCA.interfaces.BaseInterface import cBaseInterFace

import ORCA.Globals as Globals

__all__ = ['cDefinitions','GetDefinitionFileNameByName']

class cDefinitions(OrderedDict): #type: OrderedDict[str,cDefinition]
    """ Class which holds all definitions, as related functions, iterable """
    def __init__(self):
        super().__init__()
        self.aDefinitionSettingVars:List[str]                   = []
        self.dInitInterfaceSettings:Dict[str,Dict[str,Dict]]    = {}
        self.aSettingsVars:List[str]                            = []
        self.dSettingsDefaults:Dict[str,str]                    = {}
        self.uInstallationHint:str                              = u''
        self.uDefinitionAuthor:str                              = u''
        self.uDefinitionSupport:str                             = u''
        self.uDefinitionVersion:str                             = u''
        self.dSettingFormatStrings:Dict[str,str]                = {}
        self.dInstallationsHints:Dict[str,str]                  = {}

    def __getitem__(self,key:Union[str,int]) -> Union[cDefinition,None]:
        try:
            if isinstance(key,int):
                return list(self.values())[key]
            else:
                return self[key]
        except Exception as e:
            LogError(uMsg="Wrong Definition Name or Index given:"+str(key),oException=e)
            return None

    def InitVars(self) -> None:
        """ (Re) Initialize all vars of the definitions """
        self.clear()
        del self.aDefinitionSettingVars[:]
        self.dInitInterfaceSettings.clear()
        self.dSettingsDefaults.clear()
        self.dInstallationsHints.clear()
        del self.aSettingsVars[:]
        self.uInstallationHint  = u''
        self.uDefinitionAuthor  = u''
        self.uDefinitionSupport = u''
        self.uDefinitionVersion = u''
        self.dSettingFormatStrings={'options'       :',{{"type":"{type}","title":"{title}","desc":"{description}","section":"{section}","key":"{var}","allowtextinput":"{allowtextinput}","options":[{options}]}}',
                                    'numericslider' :',{{"type":"{type}","title":"{title}","desc":"{description}","section":"{section}","key":"{var}","min":"{min}", "max":"{max}","roundpos":"{roundpos}"}}',
                                    'title'         :',{{"type":"{type}","title":"{title}"}}',
                                    'buttons'       :',{{"type":"{type}","title":"{title}","desc":"{description}","section":"{section}","key":"{var}","buttons":{buttons}}}',
                                    'default'       :',{{"type":"{type}","title":"{title}","desc":"{description}","section":"{section}","key":"{var}"}}'}
        self.dSettingFormatStrings['scrolloptions']=self.dSettingFormatStrings['options']

    def DumpDefinitionList(self) -> None:
        """ Dumps a list af all available definition (alias) names """
        LogError(uMsg=u'Available Definition Names:')
        for uKey in self:
            LogError(uMsg=u'Available Name:'+uKey)

    def AddDefinition(self,oDefinition:cDefinition) -> None:
        """ adds a definition member to the list of definitions """
        self[oDefinition.uAlias] = oDefinition

    def LoadLanguages(self,fSplashScreenPercentageStartValue:float) -> None:
        """ Loads the language files for the definitions """
        # Scheduling Loading Definition Languages

        oDefinition:cDefinition
        aCommands:List[Dict]
        fSplashScreenPercentageRange:float  = 10.0
        fPercentage:float                   = fSplashScreenPercentageStartValue
        fPercentageStep:float               = fSplashScreenPercentageRange/len(self)

        aActions:List[Dict] = Globals.oEvents.CreateSimpleActionList([{'name':'Show Message to Load the Language','string':'showsplashtext','maintext':'$lvar(413)'}])
        for uDefinitionKey in reversed(self):
            oDefinition=self[uDefinitionKey]
            fPercentage=fPercentage+fPercentageStep
            if oDefinition.bImportLanguages:
                if Logger.getEffectiveLevel() != logging.DEBUG:
                    aCommands = []
                else:
                    aCommands=[{'name':'Update Percentage and DefinitionName','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)}]
                if oDefinition.oDefinitionPathes.oFnDefinitionLanguageFallBack.Exists():
                    aCommands.append({'name':'Load Default Language File','string':'loadlanguages','languagefilename':oDefinition.oDefinitionPathes.oFnDefinitionLanguageFallBack.string,'definition':oDefinition.uName,'definitionalias':oDefinition.uAlias})
                if not Globals.uLanguage==u'English':
                    oDefinition.oDefinitionPathes.LanguageChange()
                    if oDefinition.oDefinitionPathes.oFnDefinitionLanguage.Exists():
                        aCommands.append({'name':'Load Requested Language File','string':'loadlanguages','languagefilename':oDefinition.oDefinitionPathes.oFnDefinitionLanguage.string,'definition':oDefinition.uName,'definitionalias':oDefinition.uAlias})
                if len(aCommands)>0:
                    Globals.oEvents.AddToSimpleActionList(aActions,aCommands)

        Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

    def LoadActions(self,fSplashScreenPercentageStartValue:float) -> None:
        """ Loads the action files for the definitions """

        oDefinition:cDefinition
        aCommands:List[Dict]

        fSplashScreenPercentageRange:float          = 10.0
        fPercentage:float                           = fSplashScreenPercentageStartValue
        fPercentageStep:float                       = fSplashScreenPercentageRange/len(self)

        aActions:List[Dict] = Globals.oEvents.CreateSimpleActionList([{'name':'Show Message we load Actions','string':'showsplashtext','maintext':'$lvar(403)'}])
        for uDefinitionKey in reversed(self):
            oDefinition = self[uDefinitionKey]
            fPercentage=fPercentage+fPercentageStep
            if oDefinition.bImportActions:
                if Logger.getEffectiveLevel() != logging.DEBUG:
                    aCommands = []
                else:
                    aCommands = [{'name': 'Update Percentage and Definition Name', 'string': 'showsplashtext', 'subtext': oDefinition.uDefPublicTitle, 'percentage': str(fPercentage)}]

                aCommands.append({'name': 'Load the Definition Actions', "string": "loaddefinitionactions", "definitionname": oDefinition.uAlias})
                Globals.oEvents.AddToSimpleActionList(aActions,aCommands)

        Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

    def LoadFonts(self,uDefinitionName:str,fSplashScreenPercentageStartValue:float) -> None:
        """ Load the fonts for a single definition """

        aCommands:List[Dict]

        if uDefinitionName=="":
            fSplashScreenPercentageRange:float      = 10.0
            fPercentage:float                       = fSplashScreenPercentageStartValue
            fPercentageStep:float                   = fSplashScreenPercentageRange/(len(self)+1)

            # Scheduling Loading Definition Fonts
            aActions:List[Dict] = Globals.oEvents.CreateSimpleActionList([{'name':'Show Message we load Fonts','string':'showsplashtext','maintext':'Loading Definition Fonts'}])

            #for definition
            for uDefinitionKey in reversed(self):
                oDefinition = self[uDefinitionKey]
                fPercentage = fPercentage+fPercentageStep
                if Logger.getEffectiveLevel() != logging.DEBUG:
                    aCommands = []
                else:
                    aCommands = [{'name':'Update Percentage and Definition Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)}]
                aCommands.append({'name':'Load Fonts for Definition','string':'loaddefinitionfonts','definitionname':oDefinition.uAlias})

                Globals.oEvents.AddToSimpleActionList(aActions,aCommands)

            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        elif uDefinitionName=="ORCA":
            aFontsFolders:List[str] = Globals.oPathFonts.GetFolderList(bFullPath=True)
            for uFontFolder in aFontsFolders:
                oFnFontDefinition:cFileName = cFileName('').ImportFullPath(uFontFolder+u"/fonts.xml")
                if not oFnFontDefinition.string in aLoadedFontFiles:
                    Logger.info(u'Loading Global Fonts: '+uFontFolder)
                    aLoadedFontFiles.append(oFnFontDefinition.string)
                    LoadFontFromXML(LoadXMLFile(oFnFontDefinition))
        else:
            self[uDefinitionName].LoadFonts()

    def LoadGestures(self,uDefinitionName:str,fSplashScreenPercentageStartValue:float) -> None:
        """ Loads the gestures for a single definition, or creates the queue entries """

        aCommands: List[Dict]

        if uDefinitionName=="":
            fSplashScreenPercentageRange:float  = 10.0
            fPercentage:float                   = fSplashScreenPercentageStartValue
            fPercentageStep:float               = fSplashScreenPercentageRange/len(self)

            # Scheduling Loading Definition Gestures
            aActions:List[Dict] = Globals.oEvents.CreateSimpleActionList([{'name':'Show Message we load Gestures','string':'showsplashtext','maintext':'$lvar(404)'}])
            for uDefinitionKey in reversed(self):
                oDefinition = self[uDefinitionKey]
                fPercentage=fPercentage+fPercentageStep
                if Logger.getEffectiveLevel() != logging.DEBUG:
                    aCommands = []
                else:
                    aCommands = [{'name':'Update Percentage and Definition Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)}]
                aCommands.append({'name':'Load Gestures for Definition','string':'loaddefinitiongestures','definitionname':oDefinition.uAlias})

                if oDefinition.bImportActions:
                    Globals.oEvents.AddToSimpleActionList(aActions,aCommands)
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        else:
            self[uDefinitionName].LoadGestures()

    def GetUsedDefinitions(self) -> None:
        """ Gets a list of all used definitions """
        Logger.debug (u'Collecting used definitions...')
        fSplashScreenPercentageRange:float = 10.0
        Globals.oTheScreen.LogToSplashScreen("Collecting used definitions",str(fSplashScreenPercentageRange))
        self.__GetUsedDefinitions_Sub(uDefinitionName=Globals.uDefinitionName,
                                      bImportActions=True,
                                      bImportLanguages=True,
                                      bImportPages=True,
                                      bImportSettings=True,
                                      uParentDefinitionName=Globals.oTheScreen.uDefName,
                                      uParentDefinitionAlias=Globals.uDefinitionName,
                                      oDefinitionVarsFromParent=cDefinitionVars(),
                                      uAlias=u'' )
        Globals.uDefinitionContext="" # to ensure, root definitioncontext is loaded
        RestoreDefinitionContext()

    # noinspection PyUnusedLocal
    def __GetUsedDefinitions_Sub(self,uDefinitionName:str,bImportActions:bool,bImportLanguages:bool,bImportPages:bool,bImportSettings:bool, uParentDefinitionName:str, uParentDefinitionAlias:str,oDefinitionVarsFromParent:cDefinitionVars, uAlias:str):

        dAdditionalDefVars:Dict[str,cDefinitionVars] ={}

        if not uAlias in self:
            oDefinitionPathes:cDefinitionPathes = cDefinitionPathes(uDefinitionName)
            SetVar(uVarName   = "DEFINITIONPATH[%s]" % uDefinitionName, oVarValue = oDefinitionPathes.oPathDefinition.string)
            SetVar(uVarName   = "DEFINITIONPATHSKINELEMENTS[%s]" % uDefinitionName, oVarValue=oDefinitionPathes.oPathDefinitionSkinElements.string)
            Globals.dDefinitionPathes[uDefinitionName]=oDefinitionPathes
            SetDefinitionPathes(uDefinitionName)

            oFnDefinition:cFileName = Globals.oDefinitionPathes.oFnDefinition
            Logger.debug (u'TheScreen: Load Definition XmlFile:'+oFnDefinition)
            oDefinition:cDefinition                = cDefinition(uDefinitionName,self)
            oDefinition.uParentDefinitionName      = uParentDefinitionName
            oDefinition.bImportActions             = bImportActions
            oDefinition.bImportLanguages           = bImportLanguages
            oDefinition.bImportPages               = bImportPages
            oDefinition.bImportSettings            = bImportSettings
            oDefinition.oDefinitionVarsFromParent  = oDefinitionVarsFromParent

            #we read the definitionvars first with raw funtions
            uET_Data = CachedFile(oFileName=Globals.oDefinitionPathes.oFnDefinition)
            oET_Root = fromstring(uET_Data)
            oRef = oET_Root.find('def_parameter')
            # And merge / Replace the existing Vars
            oDefinition.oDefinitionVars.clear()
            oDefinition.oDefinitionVars.update(ToOrderedDic(GetXMLTextValue(oRef,u'definitionvars',False,u'{}')))

            if len(oDefinitionVarsFromParent)>0:
                for uVarName in oDefinition.oDefinitionVars:
                    if uVarName in oDefinition.oDefinitionVarsFromParent:
                        oDefinition.oDefinitionVars[uVarName]=oDefinition.oDefinitionVarsFromParent[uVarName]
                    else:
                        Logger.warning("Importing definition %s from %s: Definition varname not passed: '%s', using default %s" % (oDefinition.uName, uParentDefinitionName, uVarName, oDefinition.oDefinitionVars[uVarName]))
                for uVarName in oDefinitionVarsFromParent:
                    if not uVarName in oDefinition.oDefinitionVars:
                        oDefinition.oDefinitionVars[uVarName]=oDefinition.oDefinitionVarsFromParent[uVarName]
                        dAdditionalDefVars[uVarName]=oDefinition.oDefinitionVarsFromParent[uVarName]

            for uKey in oDefinition.oDefinitionVars:
                uVar:str=oDefinition.oDefinitionVars[uKey]
                if "$cookie(" in uVar:
                    uValue:str=GetCookieValue(uVar)
                    oDefinition.oDefinitionVars[uKey]=uValue

            if uAlias==u'':
                # this works on all python versions
                for uKey in oDefinition.oDefinitionVars:
                    uAlias:str = oDefinition.oDefinitionVars[uKey]
                    break

            if uAlias=='':
                uAlias:str=uDefinitionName
                oDefinition.uDefPublicTitle=uDefinitionName
                #create a default alias def var
                uAliasDefVar:str="definition_alias_"+uAlias
                if oDefinition.oDefinitionVars.get(uAliasDefVar) is None:
                    SetDefVar(uVarName = uAliasDefVar,uVarValue = uAlias,dArray = oDefinition.oDefinitionVars)
            else:
                oDefinition.uDefPublicTitle="%s [%s]" % (uAlias,uDefinitionName)

            oDefinition.uAlias                     = uAlias

            if not uAlias in self:
                # create defvars for import pages
                oTmpDefinitionVars:cDefinitionVars=copy(oDefinition.oDefinitionVars)
                for uVar in oTmpDefinitionVars:
                    if not uVar.endswith("_IMPORTPAGES"):
                        if bImportPages:
                            SetDefVar(uVarName = uVar + "_IMPORTPAGES",uVarValue = "1",dArray = oDefinition.oDefinitionVars)
                        else:
                            SetDefVar(uVarName = uVar+"_IMPORTPAGES",uVarValue = "0",dArray = oDefinition.oDefinitionVars)


                #and now again with adjusted definitionvars
                oET_Root:Element = Orca_FromString(uET_Data,oDefinition,"root")
                oDefinition.oET_Root            = oET_Root
                oDefinition.sET_Data            = uET_Data

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
                        for uVarName in dAdditionalDefVars:
                            if not uVarName in aDefinitionVarsImp:
                                aDefinitionVarsImp[uVarName]=dAdditionalDefVars[uVarName]

                        self.__GetUsedDefinitions_Sub(uDefinitionNameImp,bImportActionsImp,bImportLanguagesImp,bImportPagesImp,bImportSettingsImp,oDefinition.uName, oDefinition.uAlias,aDefinitionVarsImp, uAliasImp)
            else:
                Logger.debug (u'GetUsedDefinitions: Skipping duplicate xml %s [%s]' %(uAlias,uDefinitionName))
        else:
            Logger.debug (u'GetUsedDefinitions: Skipping duplicate xml %s [%s]' %(uAlias,uDefinitionName))


    def ParseXmlFiles(self,uDefinitionName:str,fSplashScreenPercentageStartValue:float) -> None:
        """ Parses the definition file for a single definition """
        aCommands: List[Dict]
        fSplashScreenPercentageRange:float = 10.0

        if not uDefinitionName:
            fPercentage:float       = fSplashScreenPercentageStartValue
            fPercentageStep:float   = fSplashScreenPercentageRange/len(self)

            aActions:List[Dict] = Globals.oEvents.CreateSimpleActionList([{'name':'Show Message that we parse the XML Files','string':'showsplashtext','maintext':'$lvar(412)'}])
            # Scheduling Parsing of Definition XML Files
            for uDefinitionKey in self:
                oDefinition = self[uDefinitionKey]
                fPercentage = fPercentage+fPercentageStep
                if Logger.getEffectiveLevel() != logging.DEBUG:
                    aCommands = []
                else:
                    aCommands = [{'name':'Update Percentage and Definitioon Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)}]
                aCommands.append({'name':'And parse the definition','string':'parsedefinitionxml','definitionname':oDefinition.uAlias})
                Globals.oEvents.AddToSimpleActionList(aActions,aCommands)

            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        else:
            self[uDefinitionName].LoadXMLFile()

    def InitInterFaceSettings(self,uDefinitionName:str,fSplashScreenPercentageStartValue:float) -> None:
        """ Init The Interface settings of a definition  """

        aCommands: List[Dict]
        oInterface: cBaseInterFace
        fSplashScreenPercentageRange = 10.0

        if not uDefinitionName:
            # Scheduling Initialize Interface settings
            fPercentage     = fSplashScreenPercentageStartValue
            fPercentageStep = fSplashScreenPercentageRange/len(self)

            aActions:List[Dict] = Globals.oEvents.CreateSimpleActionList([{'name':'Show Message the we initialize the interfaces','string':'showsplashtext','maintext':'$lvar(418)'}])

            for uDefinitionKey in reversed(self):
                oDefinition = self[uDefinitionKey]
                fPercentage=fPercentage+fPercentageStep
                if Logger.getEffectiveLevel() != logging.DEBUG:
                    aCommands = []
                else:
                    aCommands = [{'name':'Update Percentage and Interface Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)}]
                aCommands.append({'name':'Initialize the Interface','string':'initinterfacesettings','definitionname':oDefinition.uAlias})
                Globals.oEvents.AddToSimpleActionList(aActions,aCommands)
            Globals.oEvents.AddToSimpleActionList(aActions,    [{'name':'Show Message the we write all interface settings','string':'showsplashtext','subtext':"$lvar(456)",'percentage':str(fPercentage)},
                                                                {'name':'Write all interface settings','string':'initinterfacesettings','definitionname':'WRITEALLSETTINGS'}
                                                               ])

            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

        elif uDefinitionName=="WRITEALLSETTINGS":
            for uInterfaceName in self.dInitInterfaceSettings:
                if uInterfaceName in Globals.oInterFaces.aInterfaceList:
                    oInterface = Globals.oInterFaces.dInterfaces.get(uInterfaceName)
                    if oInterface is None:
                        Logger.info('Need to load unrecognized Interface [%s] for configuration' % uInterfaceName)
                        Globals.oInterFaces.LoadInterface(uInterfaceName)
                        oInterface=Globals.oInterFaces.dInterfaces.get(uInterfaceName)
                    if oInterface is not None:
                        for uConfigurationName in self.dInitInterfaceSettings[uInterfaceName]:
                            oInterface.oObjectConfig.WriteDefinitionConfig(uSectionName = uConfigurationName ,dSettings = self.dInitInterfaceSettings[uInterfaceName][uConfigurationName])
                else:
                    Logger.warning('Interface [%s] not on device, so it will not be configured!' % uInterfaceName)

        else:
            oDef:cDefinition = self[uDefinitionName]
            SetDefinitionContext(oDef.uName)
            oDef.InitInterFaceSettings(oDef.oET_Root)
            RestoreDefinitionContext()

    def LoadParameter(self) -> None:
        """ Loads the parameter for all definitions  """
        oDef:cDefinition
        for uDefinitionKey in self:
            oDefinition = self[uDefinitionKey]
            oDefinition.LoadParameter()

    def LoadSettings(self,uDefinitionName:str,fSplashScreenPercentageStartValue:float):
        """ Loads the settings for a specific definition """

        oDefinition:cDefinition
        aCommands: List[Dict]
        uHintKey:str
        fSplashScreenPercentageRange:float = 10.0

        if not uDefinitionName:
            # Scheduling Loading Definition Settings
            fPercentage:float     = fSplashScreenPercentageStartValue
            fPercentageStep:float = fSplashScreenPercentageRange/len(self)

            aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message that we load the settings','string':'showsplashtext','maintext':'$lvar(414)'}])
            for uDefinitionKey in reversed(self):
                oDefinition = self[uDefinitionKey]
                fPercentage=fPercentage+fPercentageStep
                if Logger.getEffectiveLevel() != logging.DEBUG:
                    aCommands = []
                else:
                    aCommands = [{'name':'Update Percentage and Definition Name','string':'showsplashtext','subtext':oDefinition.uDefPublicTitle,'percentage':str(fPercentage)}]
                aCommands.append({'name':'Load the settings for the Definition','string':'loaddefinitionsettings','definitionname':oDefinition.uAlias})
                Globals.oEvents.AddToSimpleActionList(aActions,aCommands)

            # Lets parse them (to init all default vars
            Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Parse all Settings and set defaults','string':'loaddefinitionsettings','definitionname':'PARSESETTINGS'}])
            #Execute the Queue
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
            #just to put it somewhere
            for uHintKey in self.dInstallationsHints:
                self.uInstallationHint+=self.dInstallationsHints[uHintKey]
            SetVar(uVarName = "INSTALLATIONHINT", oVarValue = self.uInstallationHint)

        else:
            oDefinition=self[uDefinitionName]
            SetDefinitionContext(oDefinition.uName)
            oDefinition.ParseSettings()
            RestoreDefinitionContext()

    def CreateSettingsJSONString(self) -> None:

        """ Creates the json string for the settings dialog AND reads/writes the defaults to the config file """

        uSection:str = Globals.uDefinitionName
        uSection = uSection.replace(u' ', u'_')
        uVisSection:str
        oConfig:Config = Globals.oDefinitionConfigParser

        for uDefinitionKey in self:
            oDef = self[uDefinitionKey]
            uVisSection=oDef.uName
            if len(oDef.aDefinitionsSettings)>0:
                uTitle:str = oDef.uDefPublicTitle
                for aSetting in oDef.aDefinitionsSettings:
                    uType:str = aSetting['type']

                    if uType=="section":
                        uVisSection=aSetting['title']
                        continue
                    if oDef.dDefinitionSettingsJSON.get(uVisSection) is None:
                        oDef.dDefinitionSettingsJSON[uVisSection]=u'[{ "type": "title","title": "'+uTitle+'" }\n'
                        #oDef.dDefinitionSettingsJSON[uVisSection]=u'['

                    aSetting['section']=uSection
                    uFormatString:str=self.dSettingFormatStrings.get(uType)
                    if uFormatString is None:
                        uFormatString=self.dSettingFormatStrings['default']
                    oDef.dDefinitionSettingsJSON[uVisSection]+=uFormatString.format(**aSetting)
                    uVar:str     = aSetting['var']
                    uDefault:str =self.dSettingsDefaults[uVar]
                    #uDefault=ReplaceVars(uDefault)
                    #todo temporary hack to bypass configparser unicode bug
                    uDefault = EscapeUnicode(uDefault)
                    #check for cookies
                    uCookie:str=aSetting["cookie"]
                    if uCookie!=u"" and uDefault=="":
                        uDefault=Var_Load(uCookie,"","")

                    # parse definition settings into vars
                    uValue:str   = ReplaceVars(Config_GetDefault_Str(oConfig,uSection, uVar,uDefault))
                    #todo temporärer hack to bypass configparser unicode bug
                    uValue = UnEscapeUnicode(uValue)
                    # Logger.debug("Loading Definition Config Setting into var: [%s]=[%s]" %(uVar,uValue))
                    SetVar(uVarName = uVar, oVarValue = uValue)
                    self.aDefinitionSettingVars.append(uVar)
            for uVisSection in oDef.dDefinitionSettingsJSON:
                if len(oDef.dDefinitionSettingsJSON[uVisSection])>0:
                    oDef.dDefinitionSettingsJSON[uVisSection]+=u']'
        oConfig.write()

    def FindDefinitionAliasForInterfaceConfiguration(self,uInterFaceName:str,uConfigName:str) -> str:
        for uDefinitionKey in self:
            oDefinition = self[uDefinitionKey]
            uAddVar:str = oDefinition.uAlias
            uDefinitionInterFace:str=GetVar(uAddVar+"_INTERFACE_MAIN")
            if uDefinitionInterFace == uInterFaceName:
                uDefinitionConfig:str = GetVar(uAddVar + "_CONFIGNAME_MAIN")
                if uDefinitionConfig == uConfigName:
                    return oDefinition.uAlias
        return ""

def GetDefinitionFileNameByName(uDefinitionName:str) -> str:
    """
        gets the definition file name if the definition description is available
    """
    try:
        aDefinitionList:List[str] = Globals.oPathDefinitionRoot.GetFolderList()
        for uDir in aDefinitionList:
            if not uDir == 'shared_documents':
                oFn:cFileName = cFileName(Globals.oPathDefinitionRoot + uDir) + u"definition.xml"
                oRepManEntry:cRepManagerEntry = cRepManagerEntry(oFn)
                oRepManEntry.ParseFromXML()
                uDefName:str = oRepManEntry.oRepEntry.uName
                if uDefName == uDefinitionName:
                    return uDir
        return ''

    except Exception as e:
        LogError(uMsg=u'GetDefinitionFileNameByName: Error:Load Definition XmlFile:', oException=e)
        return ''
