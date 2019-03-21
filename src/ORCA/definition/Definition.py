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

from xml.etree.ElementTree              import ParseError
from xml.etree                          import ElementInclude

from collections                        import OrderedDict

from kivy.logger                        import Logger

from ORCA.definition.DefinitionPathes   import cDefinitionPathes
from ORCA.definition.DefinitionVars     import cDefinitionVars
from ORCA.Gesture                       import cGesture
from ORCA.RepManagerEntry               import cRepManagerEntry
from ORCA.vars.Replace                  import ReplaceDefVars
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.vars.Access                   import SetVar
from ORCA.utils.CachedFile              import CachedFile
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

__all__ = ['cDefinition', 'LoadFontFromXML', 'aLoadedFontFiles', 'aLoadedGestures', 'LoadGesturesFromXML']

aLoadedFontFiles=[]
aLoadedGestures=[]


def LoadFontFromXML(oET_Root):
    """
    Parses the font settings from a xml node

    :param Element oET_Root: An elementree object which holds the font definition
    """

    if oET_Root is not None:
        Globals.oTheScreen.oFonts.ParseFontFromXMLNode(oET_Root)
        Globals.oTheScreen.oFonts.ParseIconsFromXMLNode(oET_Root)


def LoadGesturesFromXML(oET_Root,uSegmentTag, uListTag):
    """
    Parses the gesture settings from a xml node

    :param Element oET_Root: An elementree object which holds the gesture definition
    :param string uSegmentTag: The segment name in the xml tree to start search
    :param string uListTag: The list name in the xml tree to find the gesture definition
    """

    try:
        oET_SegmentsStart  = oET_Root.find(uSegmentTag)
        if oET_SegmentsStart is not None:
            oET_Includes=oET_SegmentsStart.findall('includes')
            if oET_Includes:
                for oET_Include in oET_Includes:
                    oET_Segments=oET_Include.findall(uListTag)
                    if oET_Segments:
                        for oET_Segment in oET_Segments:
                            uName=GetXMLTextAttribute(oET_Segment,u'name',True,u'')
                            oGesture=cGesture()
                            oGesture.ParseGestureFromXMLNode(oET_Segment)
                            oGesture.oGesture = Globals.oTheScreen.oGdb.str_to_gesture(oGesture.uGestureString)
                            oGesture.oGesture.Name=uName
                            Globals.oTheScreen.oGdb.add_gesture(oGesture.oGesture)
                            Globals.oTheScreen.dGestures[uName]=oGesture
    except ParseError as e:
        uMsg=LogError(u'Fatal Error:Load Gesture XmlFile:',e)
        ShowErrorPopUp(uTitle="Fatal Error",uMessage=uMsg,bAbort=True)

class cDefinition(object):

    """ A definition object for the list of definitions """
    def __init__(self,uDefinitionName, oDefinitions):
        self.dDefinitionSettingsJSON   = OrderedDict()
        self.aDefinitionsSettings      = []
        self.oDefinitionVars           = cDefinitionVars()
        self.oDefinitionVarsFromParent = cDefinitionVars()
        self.bImportActions            = False
        self.bImportLanguages          = False
        self.bImportPages              = False
        self.bImportSettings           = False
        self.bLoadedCached             = False
        self.fRatio                    = 1.0
        self.fRationX                  = 1.0
        self.fRationY                  = 1.0
        self.iDefMaxX                  = 1
        self.iDefMaxY                  = 1
        self.iFontSize_Button          = 200
        self.iFontSize_File            = 200
        self.iFontSize_Text            = 200
        self.iGapX                     = 0
        self.iGapY                     = 0
        self.oDefinitionPathes         = Globals.dDefinitionPathes.get(uDefinitionName, cDefinitionPathes(uDefinitionName))
        self.oDefinitions              = oDefinitions
        self.oET_Root                  = None
        self.oRepManEntry              = None
        self.oTree                     = None
        self.sET_Data                  = ''
        self.uAlias                    = u''
        self.uDefaultFont              = u''
        self.uDefDescription           = u''
        self.uDefPublicTitle           = u''
        self.uName                     = uDefinitionName
        self.uParentDefinitionName     = u''

    # next two functions required to have a definition object included as an element tree attribute
    def __contains__(self,key):
        return False
    def encode(self,encoding, decode):
        """ Dummy to return the name """
        return str(self.uAlias)

    def LoadActions(self):
        """ parses the definition specific actions """
        Logger.info (u'Loading Actions for definition:'+self.uDefPublicTitle)
        SetDefinitionContext(self.uName)
        if Globals.oFnAction.Exists():
            sET_Data = CachedFile(Globals.oFnAction)
            sET_Data = ReplaceDefVars(sET_Data,self.oDefinitionVars)
            oET_Root = Orca_FromString(sET_Data, self, Globals.oFnAction.string)
            Orca_include(oET_Root,orca_et_loader)
            SetDefinitionContext(self.uName)
            Globals.oActions.LoadActionsSub(oET_Root,u'pagestartactions',u'pagestartaction', Globals.oActions.dActionsPageStart, Globals.oFnAction)
            Globals.oActions.LoadActionsSub(oET_Root,u'pagestartactions',u'pagestopaction',  Globals.oActions.dActionsPageStop,  Globals.oFnAction)
            Globals.oActions.LoadActionsSub(oET_Root,u'actions',         u'action',          Globals.oActions.dActionsCommands,  Globals.oFnAction)

            SetVar(uVarName = u'ORCASTANDARDPAGESTARTACTIONSINCLUDED',oVarValue = u"1")
            SetVar(uVarName = u'ORCASTANDARDACTIONSINCLUDED', oVarValue = u"1")
        RestoreDefinitionContext()
        return

    def LoadFonts(self):
        """ Loads all fonts descriptions for a definition """
        Logger.info (u'Loading Local Font list for definition:'+self.uDefPublicTitle)
        if self.oDefinitionPathes.oFnDefinitionLocalFont.Exists():
            if not self.oDefinitionPathes.oFnDefinitionLocalFont.string in aLoadedFontFiles:
                aLoadedFontFiles.append(self.oDefinitionPathes.oFnDefinitionLocalFont.string)
                oET_Root = LoadXMLFile(self.oDefinitionPathes.oFnDefinitionLocalFont)
                LoadFontFromXML(oET_Root)

    def LoadGestures(self):
        """ Loads all Gestures descriptions for a definition """
        Logger.info ('Loading Gestures for definition:'+self.uDefPublicTitle)
        if not self.uName in aLoadedGestures:
            aLoadedGestures.append(self.uName)
            if Globals.oFnGestures.Exists():
                SetDefinitionContext(self.uName)
                oET_Root = LoadXMLFile(Globals.oFnGestures)
                Orca_include(oET_Root,orca_et_loader)
                LoadGesturesFromXML(oET_Root ,u'gestures',u'gesture')
            RestoreDefinitionContext()
        SetVar(uVarName = "ORCASTANDARDGESTURESINCLUDED", oVarValue = "1")

    def LoadXMLFile(self):
        """ The main function to load the xml """

        SetDefinitionContext(self.uName)
        Globals.oTheScreen.LogToSplashScreen2(self.uDefDescription)
        Logger.info (u'Load Definition XmlFile:'+Globals.oDefinitionPathes.oFnDefinition)

        oET_Root=self.oET_Root

        try:
            Logger.debug (u'Definition %s (%s): Loading xml includes' % (self.uName,self.uAlias))
            Orca_include(oET_Root,orca_et_loader)
            SetDefinitionContext(self.uName)
        except Exception as e:
            StartWait()
            uMsg=LogError(u'Fatal Error: definition xml file faulty',e)
            ShowErrorPopUp(uTitle="Fatal Error",uMessage=uMsg,bAbort=True)

        SetVar(uVarName = 'ORCASTANDARDPAGESINCLUDED', oVarValue = "1")

        Globals.oTheScreen.uDefName            = self.oRepManEntry.oRepEntry.uName
        self.oDefinitions.uDefinitionAutor   = self.oRepManEntry.oRepEntry.uAuthor
        self.oDefinitions.uDefinitionVersion = self.oRepManEntry.oRepEntry.uVersion
        SetVar(uVarName = u'DEFINITIONAUTOR',   oVarValue = self.oDefinitions.uDefinitionAutor)
        SetVar(uVarName = u'DEFINITIONVERSION', oVarValue = self.oDefinitions.uDefinitionVersion)
        SetVar(uVarName = u'DEFINITIONSUPPORT', oVarValue = self.oDefinitions.uDefinitionSupport)

        Logger.debug (u'Definition [%s] : Ratios %fx%f:' % (self.uName,self.fRationX,self.fRationY))
        if self.bImportPages:
            # get a list of all pages and add Them
            oXMLPages       = oET_Root.find('pages')
            for oXMLPage in oXMLPages.findall('page'):
                Globals.oTheScreen.oScreenPages.AddPageFromXmlNode(oXMLPage)
            Globals.oNotifications.SendNotification("DEFINITIONPAGESLOADED",**{"definition":self})
        RestoreDefinitionContext()

        return True

    def LoadFurtherXmlFile(self,oFnXml):
        # Loads pages from a further XML File
        sET_Data = CachedFile(oFnXml)
        sET_Data = ReplaceDefVars(sET_Data, self.oDefinitionVars)
        oET_Root = Orca_FromString(sET_Data, self, oFnXml.string)
        Orca_include(oET_Root, orca_et_loader)

        if self.bImportPages:
            # get a list of all pages and add Them
            oXMLPages       = oET_Root.find('pages')
            for oXMLPage in oXMLPages.findall('page'):
                Globals.oTheScreen.oScreenPages.AddPageFromXmlNode(oXMLPage)

    def InitInterFaceSettings(self,oXMLRoot):
        """ sub routine to recursive load setups """
        oXMLInterfaceSetupTag       = oXMLRoot.find('interface_setup')
        if oXMLInterfaceSetupTag is not None:
            oXMLInterfaceSetups=oXMLInterfaceSetupTag.findall('interface')
            for oXMLInterfaceSetup in oXMLInterfaceSetups:
                uInterFaceName=GetXMLTextAttribute(oXMLInterfaceSetup,'name',True,u'')
                if self.oDefinitions.dInitInterfaceSettings.get(uInterFaceName) is None:
                    self.oDefinitions.dInitInterfaceSettings[uInterFaceName]={}
                oConfigurations = oXMLInterfaceSetup.findall('configuration')
                for oConfiguration in oConfigurations:
                    uConfigurationName = GetXMLTextAttribute(oConfiguration,'name',True,u'')
                    if self.oDefinitions.dInitInterfaceSettings[uInterFaceName].get(uConfigurationName) is None:
                        self.oDefinitions.dInitInterfaceSettings[uInterFaceName][uConfigurationName]={}
                    oSettings = oConfiguration.findall('setting')
                    for oSetting in oSettings:
                        uSettingName=GetXMLTextAttribute( oSetting,'name',True,u'')
                        uSettingParameter=GetXMLTextAttribute( oSetting,'parameter',True,u'')
                        self.oDefinitions.dInitInterfaceSettings[uInterFaceName][uConfigurationName][uSettingName.upper()]=uSettingParameter
            self.InitInterFaceSettings(oXMLInterfaceSetupTag)

    def LoadParameter(self):
        """ Loads the Parameter from the definition XML File """
        Logger.info (u'Load Definition Parameter [%s] %s:' %(self.uAlias, self.oDefinitionPathes.oPathDefinition.string))

        oET_Root=self.oET_Root
        #Get Definition Wide Setting
        oRef                    = oET_Root.find('def_parameter')

        self.iFontSize_Button   = GetXMLTextValue(oRef,u'fontsize_button',False,'%h100')
        self.iFontSize_Text     = GetXMLTextValue(oRef,u'fontsize_text',False,'%h100')
        self.iFontSize_File     = GetXMLTextValue(oRef,u'fontsize_file',False,'d11')

        # we replace the custom definition vars and reparse the xml again
        self.sET_Data=ReplaceDefVars(self.sET_Data,self.oDefinitionVars)
        self.oET_Root=Orca_FromString(self.sET_Data,self, "root2")

        self.uDefaultFont       = GetXMLTextValue(oRef,u'defaultfont',True,Globals.oTheScreen.oSkin.dSkinAttributes['defaultfont'])

        if not self.uDefaultFont:
            self.uDefaultFont=Globals.oTheScreen.oSkin.dSkinAttributes['defaultfont']

        if self.uName==Globals.uDefinitionName:
            self.oDefinitions.uDefinitionSupport = GetXMLTextValue(oRef,u'support',False,u'')
        uInstallationHint       = GetXMLTextValue(oRef,u'installationhint',False,u'')
        if uInstallationHint!='':
            self.oDefinitions.dInstallationsHints[self.uName]=("[b][color=#FFFF00]"+self.uDefPublicTitle +u"[/color][/b]\n\n"+uInstallationHint+u"\n\n")

        if Globals.uStretchMode=="CENTER" or Globals.uStretchMode=="TOPLEFT":
            fRatio=float(float(Globals.iAppWidth)/float(Globals.iAppHeight))/float(float(self.iDefMaxX)/float(self.iDefMaxY))
            if fRatio<1:
                fShouldHeight=float(Globals.iAppWidth)/ (float(self.iDefMaxX)/float(self.iDefMaxY))
                self.fRationY=float(self.iDefMaxY)/fShouldHeight
                if Globals.uStretchMode=="CENTER" :
                    self.iGapY=int((((Globals.iAppHeight*self.fRationX)-self.iDefMaxY)/self.fRationX)/2)
            else:
                fShouldWidth=float(Globals.iAppHeight)/ (float(self.iDefMaxY)/float(self.iDefMaxX))
                self.fRationX=float(self.iDefMaxX)/fShouldWidth
                if Globals.uStretchMode=="CENTER" :
                    self.iGapX=int((((Globals.iAppWidth*self.fRationY)-self.iDefMaxX)/self.fRationY)/2)
        return True

    def ParseSettings(self):

        """ Parses the settings for a definition """
        self.oRepManEntry = cRepManagerEntry("")
        self.oRepManEntry.ParseFromXML(self.oET_Root)
        self.uDefDescription = self.oRepManEntry.oRepEntry.uName
        self.uDefPublicTitle = self.uDefDescription
        if self.uAlias!="" and self.uAlias!=self.uName:
            self.uDefPublicTitle="%s [%s]" % (self.uAlias,self.uDefPublicTitle)

        if self.bImportSettings:
            self.ParseXMLSettings()
        return

    def ParseXMLSettings(self):
        """ get list of all definition settings """
        self.ParseXMLSettings_sub(self.oET_Root)

    def ParseXMLSettings_sub(self,oXMLRoot, bFirst=True):
        """ sub function to do it recursive """
        if bFirst:
            oXMLSettings       = oXMLRoot.find('settings')
            if oXMLSettings is not None:
                if oXMLSettings.find(ElementInclude.XINCLUDE_INCLUDE) is not None:
                    Orca_include(oXMLSettings,orca_et_loader)
            else:
                return
        else:
            oXMLSettings=oXMLRoot

        for oEntry in oXMLSettings:
            if oEntry.tag=='setting':
                self.AddDefinitionSetting(oEntry)
            elif oEntry.tag=='default':
                self.__AddSettingDefaults(oEntry)
            elif oEntry.tag=='settings':
                self.ParseXMLSettings_sub(oEntry,False)
        return

    def AddDefinitionSetting(self,oXMLSetting):
        """ Adds a single definition to the list of settings """

        dSetting= {'title':             GetXMLTextAttribute(oXMLSetting, u'title',           True, u'NoName'),
                   'type':              GetXMLTextAttribute(oXMLSetting, u'type',            True, u'string'),
                   'var':               GetXMLTextAttribute(oXMLSetting, u'var',             False, u'NoVar'),
                   'description':       GetXMLTextAttribute(oXMLSetting, u'desc',            False, u''),
                   'default':           GetXMLTextAttribute(oXMLSetting, u'default',         False, u''),
                   'options':           GetXMLTextAttribute(oXMLSetting, u'options',         False, u''),
                   'buttons':           GetXMLTextAttribute(oXMLSetting, u'buttons',         False, u''),
                   'min':               GetXMLTextAttribute(oXMLSetting, u'min',             False, u'0'),
                   'max':               GetXMLTextAttribute(oXMLSetting, u'max',             False, u'100'),
                   'roundpos':          GetXMLTextAttribute(oXMLSetting, u'roundpos',        False, u'0'),
                   'allowtextinput':    GetXMLTextAttribute(oXMLSetting, u'allowtextinput',  False, u'0'),
                   'cookie':            GetXMLTextAttribute(oXMLSetting, u'cookie',          False, u'')}

        self.oDefinitions.dSettingsDefaults[dSetting['var']]  = dSetting['default']

        uKey=ReplaceVars(dSetting['title']+dSetting['var'])
        if uKey not in self.oDefinitions.aSettingsVars or dSetting['type']=="title" or dSetting['type']=="section":
            self.aDefinitionsSettings.append(dSetting)
            self.oDefinitions.aSettingsVars.append(uKey)
        else:
            pass
            #Logger.warning("Skipping duplicate setting:"+uKey+":"+dSetting['title'])

    def __AddSettingDefaults(self,oXMLSetting):
        uVar                 = GetXMLTextAttribute(oXMLSetting,u'var',              True,  u'NoVar')
        uDefault             = GetXMLTextAttribute(oXMLSetting,u'default',          True,  u'')
        #Logger.debug( "setdefault: Definition:%s Var:%s  Default:%s" % (self.uAlias,uVar,uDefault))
        self.oDefinitions.dSettingsDefaults[uVar]  = uDefault


