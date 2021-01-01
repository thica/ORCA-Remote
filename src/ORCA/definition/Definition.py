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

from typing import List
from typing import Dict
from typing import Optional
from typing import Any


from xml.etree.ElementTree              import ParseError
from xml.etree.ElementTree              import Element
from xml.etree                          import ElementInclude

from collections                        import OrderedDict

from kivy.logger                        import Logger

from ORCA.definition.DefinitionPathes   import cDefinitionPathes
from ORCA.definition.DefinitionVars     import cDefinitionVars
from ORCA.Gesture                       import cGesture
from ORCA.download.RepManagerEntry      import cRepManagerEntry
from ORCA.vars.Replace                  import ReplaceDefVars
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.vars.Access                   import SetVar
from ORCA.utils.CachedFile              import CachedFile
from ORCA.utils.FileName                import cFileName
from ORCA.utils.LogError                import LogError
from ORCA.utils.wait.StartWait          import StartWait
from ORCA.utils.XML                     import GetXMLTextAttribute
from ORCA.utils.XML                     import GetXMLTextValue
from ORCA.utils.XML                     import LoadXMLFile
from ORCA.utils.XML                     import Orca_FromString
from ORCA.utils.XML                     import Orca_include
from ORCA.utils.XML                     import orca_et_loader
from ORCA.definition.DefinitionContext  import SetDefinitionContext
from ORCA.definition.DefinitionContext  import RestoreDefinitionContext
from ORCA.ui.ShowErrorPopUp             import ShowErrorPopUp

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.definition.Definitions import cDefinitions
else:
    from typing import TypeVar
    cDefinitions = TypeVar("cDefinitions")


__all__ = ['cDefinition', 'LoadFontFromXML', 'aLoadedFontFiles', 'aLoadedGestures', 'LoadGesturesFromXML']

aLoadedFontFiles:List[str] = []
aLoadedGestures:List[str]  = []

def LoadFontFromXML(*,oET_Root:Element) -> None:
    """
    Parses the font settings from a xml node

    :param Element oET_Root: An elementree object which holds the font definition
    """

    if oET_Root is not None:
        Globals.oTheScreen.oFonts.ParseFontFromXMLNode(oXMLNode=oET_Root)
        Globals.oTheScreen.oFonts.ParseIconsFromXMLNode(oXMLNode=oET_Root)


def LoadGesturesFromXML(*,oET_Root:Element,uSegmentTag:str, uListTag:str) -> None:
    """
    Parses the gesture settings from a xml node

    :param Element oET_Root: An elementree object which holds the gesture definition
    :param str uSegmentTag: The segment name in the xml tree to start search
    :param str uListTag: The list name in the xml tree to find the gesture definition
    """

    oET_Include:Element
    oET_Segment:Element

    try:
        oET_SegmentsStart:Optional[Element] = oET_Root.find(uSegmentTag)
        if oET_SegmentsStart is not None:
            oET_Includes:List[Element] = oET_SegmentsStart.findall('includes')
            if oET_Includes:
                for oET_Include in oET_Includes:
                    oET_Segments:List[Element] = oET_Include.findall(uListTag)
                    if oET_Segments:
                        for oET_Segment in oET_Segments:
                            uName:str  =GetXMLTextAttribute(oXMLNode=oET_Segment,uTag=u'name',bMandatory=True,vDefault=u'')
                            oGesture:cGesture=cGesture()
                            oGesture.ParseGestureFromXMLNode(oXMLNode=oET_Segment)
                            oGesture.oGesture = Globals.oTheScreen.oGdb.str_to_gesture(oGesture.uGestureString)
                            oGesture.oGesture.name=uName
                            Globals.oTheScreen.oGdb.add_gesture(oGesture.oGesture)
                            Globals.oTheScreen.dGestures[uName]=oGesture
    except ParseError as e:
        ShowErrorPopUp(uTitle="LoadGesturesFromXML:Fatal Error",uMessage=LogError(uMsg=u'Fatal Error:Load Gesture XmlFile:',oException=e),bAbort=True)

class cDefinition:

    """ A definition object for the list of definitions """
    def __init__(self,*,uDefinitionName:str, oDefinitions:cDefinitions):
        self.dDefinitionSettingsJSON:OrderedDict        = OrderedDict()
        self.aDefinitionsSettings:List[Dict]            = []
        self.oDefinitionVars:cDefinitionVars            = cDefinitionVars()
        self.oDefinitionVarsFromParent:cDefinitionVars  = cDefinitionVars()
        self.bImportActions:bool                        = False
        self.bImportLanguages:bool                      = False
        self.bImportPages:bool                          = False
        self.bImportSettings:bool                       = False
        self.bLoadedCached:bool                         = False
        self.fRatio:float                               = 1.0
        self.fRationX:float                             = 1.0
        self.fRationY:float                             = 1.0
        self.iDefMaxX:int                               = 1
        self.iDefMaxY:int                               = 1
        self.uFontSize_Button:str                       = u'200'
        self.uFontSize_File:str                         = u'200'
        self.uFontSize_Text:str                         = u'200'
        self.iGapX:int                                  = 0
        self.iGapY:int                                  = 0
        self.oDefinitionPathes:cDefinitionPathes        = Globals.dDefinitionPathes.get(uDefinitionName, cDefinitionPathes(uDefinitionName=uDefinitionName))
        self.oDefinitions                               = oDefinitions
        self.oET_Root:Optional[Element]                 = None
        self.oRepManEntry:Optional[cRepManagerEntry]    = None
        self.sET_Data:str                               = ''
        self.uAlias:str                                 = u''
        self.uDefaultFont:str                           = u''
        self.uDefDescription:str                        = u''
        self.uDefPublicTitle:str                        = u''
        self.uName:str                                  = uDefinitionName
        self.uParentDefinitionName:str                  = u''

    # next two functions required to have a definition object included as an element tree attribute
    def __contains__(self,key:Any) -> bool:
        return False

    # noinspection PyUnusedLocal
    def encode(self,encoding:str, decode:str) -> str:
        """ Dummy to return the name """
        return str(self.uAlias)

    def LoadActions(self) -> None:
        """ parses the definition specific actions """
        Logger.info (u'Loading Actions for definition:'+self.uDefPublicTitle)
        uET_Data: str
        SetDefinitionContext(uDefinitionName=self.uName)
        if Globals.oFnAction.Exists():
            uET_Data = CachedFile(oFileName=Globals.oFnAction)
            uET_Data = ReplaceDefVars(uET_Data,self.oDefinitionVars)
            oET_Root:Element = Orca_FromString(uET_Data=uET_Data, oDef=self, uFileName=Globals.oFnAction.string)
            Orca_include(oET_Root,orca_et_loader)
            SetDefinitionContext(uDefinitionName=self.uName)
            Globals.oActions.LoadActionsSub(oET_Root=oET_Root,uSegmentTag=u'pagestartactions',uListTag=u'pagestartaction', dTargetDic=Globals.oActions.dActionsPageStart, uFileName=Globals.oFnAction)
            Globals.oActions.LoadActionsSub(oET_Root=oET_Root,uSegmentTag=u'pagestartactions',uListTag=u'pagestopaction',  dTargetDic=Globals.oActions.dActionsPageStop,  uFileName=Globals.oFnAction)
            Globals.oActions.LoadActionsSub(oET_Root=oET_Root,uSegmentTag=u'actions',         uListTag=u'action',          dTargetDic=Globals.oActions.dActionsCommands,  uFileName=Globals.oFnAction)

            SetVar(uVarName = u'ORCASTANDARDPAGESTARTACTIONSINCLUDED',oVarValue = u"1")
            SetVar(uVarName = u'ORCASTANDARDACTIONSINCLUDED', oVarValue = u"1")
        RestoreDefinitionContext()
        return None

    def LoadFonts(self) -> None:
        """ Loads all fonts descriptions for a definition """
        Logger.info (u'Loading Local Font list for definition:'+self.uDefPublicTitle)
        if self.oDefinitionPathes.oFnDefinitionLocalFont.Exists():
            if not self.oDefinitionPathes.oFnDefinitionLocalFont.string in aLoadedFontFiles:
                aLoadedFontFiles.append(self.oDefinitionPathes.oFnDefinitionLocalFont.string)
                LoadFontFromXML(oET_Root=LoadXMLFile(oFile=self.oDefinitionPathes.oFnDefinitionLocalFont))

    def LoadGestures(self) -> None:
        """ Loads all Gestures descriptions for a definition """
        Logger.info ('Loading Gestures for definition:'+self.uDefPublicTitle)
        if not self.uName in aLoadedGestures:
            aLoadedGestures.append(self.uName)
            if Globals.oFnGestures.Exists():
                SetDefinitionContext(uDefinitionName=self.uName)
                oET_Root:Element = LoadXMLFile(oFile=Globals.oFnGestures)
                Orca_include(oET_Root,orca_et_loader)
                LoadGesturesFromXML(oET_Root=oET_Root ,uSegmentTag=u'gestures',uListTag=u'gesture')
            RestoreDefinitionContext()
        SetVar(uVarName = "ORCASTANDARDGESTURESINCLUDED", oVarValue = "1")

    def LoadXMLFile(self) -> bool:
        """ The main function to load the xml """

        SetDefinitionContext(uDefinitionName=self.uName)
        Globals.oTheScreen.LogToSplashScreen2(uText=self.uDefDescription)
        Logger.info (u'Loading definition XmlFile:'+Globals.oDefinitionPathes.oFnDefinition)

        oET_Root:Element = self.oET_Root
        try:
            Logger.debug (u'Definition %s (%s): Loading xml includes' % (self.uName,self.uAlias))
            Orca_include(oElem=oET_Root,pLoader=orca_et_loader,uFileName=Globals.oDefinitionPathes.oFnDefinition.string)
            SetDefinitionContext(uDefinitionName=self.uName)
        except Exception as e:
            StartWait()
            ShowErrorPopUp(uTitle="LoadXMLFile:Fatal Error",uMessage=LogError(uMsg=u'Fatal Error: definition xml file faulty:'+self.uName,oException=e),bAbort=True)

        SetVar(uVarName = 'ORCASTANDARDPAGESINCLUDED', oVarValue = "1")

        Globals.oTheScreen.uDefName            = self.oRepManEntry.oRepEntry.uName
        self.oDefinitions.uDefinitionAuthor    = self.oRepManEntry.oRepEntry.uAuthor
        self.oDefinitions.uDefinitionVersion   = self.oRepManEntry.oRepEntry.uVersion
        SetVar(uVarName = u'DEFINITIONAUTHOR',  oVarValue = self.oDefinitions.uDefinitionAuthor)
        SetVar(uVarName = u'DEFINITIONVERSION', oVarValue = self.oDefinitions.uDefinitionVersion)
        SetVar(uVarName = u'DEFINITIONSUPPORT', oVarValue = self.oDefinitions.uDefinitionSupport)

        Logger.debug (u'Definition [%s] : Ratios %fx%f:' % (self.uName,self.fRationX,self.fRationY))
        if self.bImportPages:
            # get a list of all pages and add Them
            oXMLPages:Element       = oET_Root.find('pages')
            for oXMLPage in oXMLPages.findall('page'):
                Globals.oTheScreen.oScreenPages.AddPageFromXmlNode(oXMLPage=oXMLPage)
            oXMLPageImport:Element       = oXMLPages.find('pageimport')
            if oXMLPageImport is not None:
                for oXMLPage in oXMLPageImport.findall('page'):
                    Globals.oTheScreen.oScreenPages.AddPageFromXmlNode(oXMLPage=oXMLPage)


            Globals.oNotifications.SendNotification(uNotification="DEFINITIONPAGESLOADED",**{"definition":self})
        RestoreDefinitionContext()

        return True

    def LoadFurtherXmlFile(self,*,oFnXml:cFileName) -> None:
        """
        Loads pages from a further XML File
        :param cFileName oFnXml: The filename of the xml to load
        :return: None
        """

        uET_Data = CachedFile(oFileName=oFnXml)
        uET_Data = ReplaceDefVars(uET_Data, self.oDefinitionVars)
        oET_Root:Element = Orca_FromString(uET_Data=uET_Data, oDef=self, uFileName=oFnXml.string)
        Orca_include(oET_Root, orca_et_loader)

        if self.bImportPages:
            # get a list of all pages and add Them
            oXMLPages:Element       = oET_Root.find('pages')
            for oXMLPage in oXMLPages.findall('page'):
                Globals.oTheScreen.oScreenPages.AddPageFromXmlNode(oXMLPage=oXMLPage)

    def InitInterFaceSettings(self,*,oXMLRoot:Element) -> None:
        """ sub routine to recursive load setups """
        oXMLInterfaceSetup:Element
        oConfiguration:Element
        oSetting:Element
        oXMLInterfaceSetupTag:Element       = oXMLRoot.find('interface_setup')
        if oXMLInterfaceSetupTag is not None:
            aXMLInterfaceSetups:List[Element]=oXMLInterfaceSetupTag.findall('interface')
            for oXMLInterfaceSetup in aXMLInterfaceSetups:
                uInterFaceName:str=GetXMLTextAttribute(oXMLNode=oXMLInterfaceSetup,uTag='name',bMandatory=True,vDefault=u'')
                if self.oDefinitions.dInitInterfaceSettings.get(uInterFaceName) is None:
                    self.oDefinitions.dInitInterfaceSettings[uInterFaceName]={}
                aConfigurations:List[Element] = oXMLInterfaceSetup.findall('configuration')
                for oConfiguration in aConfigurations:
                    uConfigurationName:str = GetXMLTextAttribute(oXMLNode=oConfiguration,uTag='name',bMandatory=True,vDefault=u'')
                    if self.oDefinitions.dInitInterfaceSettings[uInterFaceName].get(uConfigurationName) is None:
                        self.oDefinitions.dInitInterfaceSettings[uInterFaceName][uConfigurationName]={}
                    oSettings:List[Element] = oConfiguration.findall('setting')
                    for oSetting in oSettings:
                        uSettingName:str=GetXMLTextAttribute(oXMLNode=oSetting,uTag='name',bMandatory=True,vDefault=u'')
                        uSettingParameter:str=GetXMLTextAttribute(oXMLNode=oSetting,uTag='parameter',bMandatory=True,vDefault=u'')
                        self.oDefinitions.dInitInterfaceSettings[uInterFaceName][uConfigurationName][uSettingName.upper()]=uSettingParameter
            self.InitInterFaceSettings(oXMLRoot=oXMLInterfaceSetupTag)

    def LoadParameter(self) -> bool:
        """ Loads the Parameter from the definition XML File """
        Logger.info (u'Load Definition Parameter [%s] %s:' %(self.uAlias, self.oDefinitionPathes.oPathDefinition.string))

        oET_Root:Element = self.oET_Root
        #Get Definition Wide Setting
        oRef:Element                    = oET_Root.find('def_parameter')

        self.uFontSize_Button   = GetXMLTextValue(oXMLNode=oRef,uTag=u'fontsize_button',bMandatory=False,vDefault='%h100')
        self.uFontSize_Text     = GetXMLTextValue(oXMLNode=oRef,uTag=u'fontsize_text',  bMandatory=False,vDefault='%h100')
        self.uFontSize_File     = GetXMLTextValue(oXMLNode=oRef,uTag=u'fontsize_file',  bMandatory=False,vDefault='d11')

        # we replace the custom definition vars and reparse the xml again
        self.sET_Data=ReplaceDefVars(self.sET_Data,self.oDefinitionVars)
        self.oET_Root=Orca_FromString(uET_Data=self.sET_Data,oDef=self,uFileName="root2")

        self.uDefaultFont       = GetXMLTextValue(oXMLNode=oRef,uTag=u'defaultfont',bMandatory=True,vDefault=Globals.oTheScreen.oSkin.dSkinAttributes['defaultfont'])

        if not self.uDefaultFont:
            self.uDefaultFont=Globals.oTheScreen.oSkin.dSkinAttributes['defaultfont']

        if self.uName==Globals.uDefinitionName:
            self.oDefinitions.uDefinitionSupport = GetXMLTextValue(oXMLNode=oRef,uTag=u'support',bMandatory=False,vDefault=u'')
        uInstallationHint:str = GetXMLTextValue(oXMLNode=oRef,uTag=u'installationhint',bMandatory=False,vDefault=u'')
        if uInstallationHint!='':
            self.oDefinitions.dInstallationsHints[self.uName]=("[b][color=#FFFF00]"+self.uDefPublicTitle +u"[/color][/b]\n\n"+uInstallationHint+u"\n\n")

        if Globals.uStretchMode=="CENTER" or Globals.uStretchMode=="TOPLEFT":
            fRatio:float=float(float(Globals.iAppWidth)/float(Globals.iAppHeight))/float(float(self.iDefMaxX)/float(self.iDefMaxY))
            if fRatio<1.0:
                fShouldHeight=float(Globals.iAppWidth)/ (float(self.iDefMaxX)/float(self.iDefMaxY))
                self.fRationY=float(self.iDefMaxY)/fShouldHeight
                if Globals.uStretchMode=="CENTER" :
                    self.iGapY=int((((Globals.iAppHeight*self.fRationX)-self.iDefMaxY)/self.fRationX)/2)
            else:
                fShouldWidth:float=float(Globals.iAppHeight)/ (float(self.iDefMaxY)/float(self.iDefMaxX))
                self.fRationX=float(self.iDefMaxX)/fShouldWidth
                if Globals.uStretchMode=="CENTER" :
                    self.iGapX=int((((Globals.iAppWidth*self.fRationY)-self.iDefMaxX)/self.fRationY)/2)
        return True

    def ParseSettings(self) -> None:

        """ Parses the settings for a definition """
        self.oRepManEntry = cRepManagerEntry(oFileName="")
        self.oRepManEntry.ParseFromXML(vContent=self.oET_Root)
        self.uDefDescription = self.oRepManEntry.oRepEntry.uName
        self.uDefPublicTitle = self.uDefDescription
        if self.uAlias!="" and self.uAlias!=self.uName:
            self.uDefPublicTitle="%s [%s]" % (self.uAlias,self.uDefPublicTitle)

        if self.bImportSettings:
            self.ParseXMLSettings()
        return

    def ParseXMLSettings(self) -> None:
        """ get list of all definition settings """
        self.ParseXMLSettings_sub(oXMLRoot=self.oET_Root,bFirst=True)

    def ParseXMLSettings_sub(self,*,oXMLRoot:Element, bFirst:bool=True) -> None:
        """ sub function to do it recursive """
        if bFirst:
            oXMLSettings:Element       = oXMLRoot.find('settings')
            if oXMLSettings is not None:
                if oXMLSettings.find(ElementInclude.XINCLUDE_INCLUDE) is not None:
                    Orca_include(oXMLSettings,orca_et_loader)
            else:
                return None
        else:
            oXMLSettings=oXMLRoot

        for oEntry in oXMLSettings:
            if oEntry.tag=='setting':
                self.AddDefinitionSetting(oXMLSetting=oEntry)
            elif oEntry.tag=='default':
                self.__AddSettingDefaults(oXMLSetting=oEntry)
            elif oEntry.tag=='settings':
                self.ParseXMLSettings_sub(oXMLRoot=oEntry,bFirst=False)
        return None

    def AddDefinitionSetting(self,*,oXMLSetting:Element) -> None:
        """ Adds a single definition to the list of settings """

        dSetting:Dict= {'title':             GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'title',           bMandatory=True,  vDefault=u'NoName'),
                        'type':              GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'type',            bMandatory=True,  vDefault=u'string'),
                        'var':               GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'var',             bMandatory=False, vDefault=u'NoVar'),
                        'description':       GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'desc',            bMandatory=False, vDefault=u''),
                        'default':           GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'default',         bMandatory=False, vDefault=u''),
                        'options':           GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'options',         bMandatory=False, vDefault=u''),
                        'buttons':           GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'buttons',         bMandatory=False, vDefault=u''),
                        'min':               GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'min',             bMandatory=False, vDefault=u'0'),
                        'max':               GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'max',             bMandatory=False, vDefault=u'100'),
                        'roundpos':          GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'roundpos',        bMandatory=False, vDefault=u'0'),
                        'allowtextinput':    GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'allowtextinput',  bMandatory=False, vDefault=u'0'),
                        'cookie':            GetXMLTextAttribute(oXMLNode=oXMLSetting, uTag=u'cookie',          bMandatory=False, vDefault=u'')}

        self.oDefinitions.dSettingsDefaults[dSetting['var']]  = dSetting['default']

        uKey:str = ReplaceVars(dSetting['title']+dSetting['var'])
        if uKey not in self.oDefinitions.aSettingsVars or dSetting['type']=="title" or dSetting['type']=="section":
            self.aDefinitionsSettings.append(dSetting)
            self.oDefinitions.aSettingsVars.append(uKey)
        else:
            pass
            #Logger.warning("Skipping duplicate setting:"+uKey+":"+dSetting['title'])

    def __AddSettingDefaults(self,*,oXMLSetting:Element) -> None:
        uVar:str                 = GetXMLTextAttribute(oXMLNode=oXMLSetting,uTag=u'var',              bMandatory=True,  vDefault=u'NoVar')
        uDefault:str             = GetXMLTextAttribute(oXMLNode=oXMLSetting,uTag=u'default',          bMandatory=True,  vDefault=u'')
        #Logger.debug( "setdefault: Definition:%s Var:%s  Default:%s" % (self.uAlias,uVar,uDefault))
        self.oDefinitions.dSettingsDefaults[uVar]  = uDefault


