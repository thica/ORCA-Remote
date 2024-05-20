# -*- coding: utf-8 -*-
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

#  Copyright (c) 2024. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from typing import Optional

from xml.etree.ElementTree  import ParseError
from xml.etree.ElementTree  import Element

from kivy.uix.label         import  Label
from kivy.uix.boxlayout     import  BoxLayout
from kivy.uix.progressbar   import  ProgressBar

from kivy.logger            import  Logger
from kivy.atlas             import  Atlas
from kivy.cache             import  Cache

from kivy.base              import  EventLoop

import kivy.core.window

from ORCA.screen.Screen import cTheScreen
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp
from ORCA.utils.LogError            import LogError
from ORCA.utils.TypeConvert         import ToFloat
from ORCA.utils.TypeConvert         import ToStringVersion
from ORCA.utils.TypeConvert         import ToUnicode
from ORCA.utils.XML                 import GetXMLIntValue
from ORCA.utils.XML                 import GetXMLTextValue
from ORCA.vars.Replace              import ReplaceVars
from ORCA.vars.Access               import SetVar
from ORCA.vars.Access               import GetVar
from ORCA.actions.ReturnCode        import eReturnCode

from ORCA.settings.BuildSettingOptionList  import BuildSettingOptionListVar

from ORCA.Globals import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.definition.Definition import cDefinition
else:
    from typing import TypeVar
    cDefinition = TypeVar('cDefinition')


# noinspection PyMethodMayBeStatic
class cTheScreenWithInit(cTheScreen):
    """ Just for better code readability
        All Functions to initialize the screen are here """
    def __init__(self):
        super(cTheScreenWithInit,self).__init__()
        self.oSplashBox:Optional[BoxLayout]     = None
        self.oProgessBar:Optional[ProgressBar]  = None
        self.ShowSplash()
        EventLoop.window.bind(size          = Globals.oApp.On_Size)
        EventLoop.window.bind(on_keyboard   = Globals.oApp.hook_keyboard)
        EventLoop.window.bind(on_motion     = self.on_motion)

    def Init(self) -> None:
        """ Adds the vars and the Settings options """
        self.AddGlobalVars()
        Globals.oNotifications.RegisterNotification(uNotification='on_stopapp',fNotifyFunction=self.DeInit,uDescription='The Screen')
        return None


    def __CreateSplashBackGround(self) -> None:
        """ Creates the Background for the splash screen """
        if len(self.oSplashBackground.children) == 0:
            self.oSplashBox                         = BoxLayout(orientation='vertical')
            self.oSplashLogger                      = Label(font_size = '24sp',text = 'Starting....', halign='center')
            self.oSplashLogger2                     = Label(font_size = '20sp',halign='center')
            self.oProgessBar                        = ProgressBar(size_hint=(0.5,None),pos_hint={'center_x': .5})
            self.oSplashBox.add_widget(Label())
            self.oSplashBox.add_widget(self.oSplashLogger)
            self.oSplashBox.add_widget(self.oProgessBar)
            self.oSplashBox.add_widget(self.oSplashLogger2)
            self.oSplashBackground.add_widget(self.oSplashBox)
        return None

    def LogToSplashScreen(self,*,uText:str,uPercentage:str='') -> None:
        """ Logs a main text message to the splash screen """
        fPercentage: float
        self.uSplashText                        = uText
        self.oSplashLogger.size                 = (Globals.iAppWidth*0.95,Globals.iAppHeight/3)
        self.oSplashLogger.text_size            = (Globals.iAppWidth*0.95,None)
        self.oSplashLogger.text                 = ReplaceVars(uText)
        if uPercentage!='':
            if uPercentage.startswith('+'):
                fPercentage=self.oProgessBar.value+ToFloat(uPercentage[1:])
            else:
                fPercentage=ToFloat(uPercentage)
            self.oProgessBar.value=fPercentage

        self.LogToSplashScreen2(uText='')
        return None

    def LogToSplashScreen2(self,*,uText:str,uPercentage:str='') -> None:
        """ Logs a sub text message to the splash screen """
        self.oSplashLogger2.size                 =(Globals.iAppWidth*0.95,Globals.iAppHeight/3)
        self.oSplashLogger2.text_size            =(Globals.iAppWidth*0.95,None)
        self.oSplashLogger2.text                 = ReplaceVars(uText)
        if uPercentage!='':
            fPercentage:float
            if uPercentage.startswith('+'):
                fPercentage=self.oProgessBar.value+ToFloat(uPercentage[1:])
            else:
                fPercentage=ToFloat(uPercentage)
            self.oProgessBar.value=fPercentage
        return None

    def ShowSplash(self) -> None:
        """ Shows the splash screen """
        self.__CreateSplashBackGround()
        self.oRootSM.current = 'SPLASH'
        self.LogToSplashScreen(uText='Starting')

        # Remove all screens from screen manager
        # There is no clear function for screen manager, so lets do it manually
        # this is required, as on restart there might be some screen manager pages in the root (which we do no want anymore)
        while len(self.oRootSM.screens)>1:
            for oScreen in self.oRootSM.screens:
                if oScreen.name != 'SPLASH':
                    self.oRootSM.remove_widget(oScreen)
        return None

    def LoadLanguage(self, *,uLanguageFileName:str='') -> None:
        """ Loads the languages files """
        try:
            if uLanguageFileName:
                Logger.info('TheScreen: Loading Language File [%s]' % uLanguageFileName)
                Globals.oLanguage.LoadXmlFile(uLanguageFileName)
            else:
                Logger.info('TheScreen: Loading Language [%s]' % Globals.uLanguage)
                Globals.oLanguage.LoadXmlFile('APP')
                self.LoadLocales()
            SetVar(uVarName='LOCALTIME',             oVarValue=Globals.oLanguage.GetLocalizedTime(Globals.bClockWithSeconds))
            SetVar(uVarName='LOCALDATE',             oVarValue=Globals.oLanguage.GetLocalizedDate(Globals.bLongDate, Globals.bLongMonth, Globals.bLongDay))
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg='TheScreen: LoadLanguage: can\'t load Language:',oException=e))
        return None

    def LoadLocales(self) -> None:
        """ Loads the locales """
        Logger.info ('TheScreen: Loading Locales [%s]' % Globals.uLocalesName)
        try:
            if not Globals.uLocalesName in Globals.oLanguage.oLocales.oLocalesEntries:
                for  Globals.uLocalesName in Globals.oLanguage.oLocales.oLocalesEntries:
                    Logger.debug ('TheScreen: Cant\'t find locales, defaulting to [%s]' % Globals.uLocalesName)
                    oConfig=Globals.oOrcaConfigParser
                    oConfig.set('ORCA', 'locales', Globals.uLocalesName)
                    break
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg='TheScreen: LoadLocales: can\'t load Locales',oException=e))
        return None

    def LoadSkinDescription(self) -> None:
        """ Loads the skin description """
        self.oSkin.LoadSkinDescription()
        return None

    def LoadAtlas(self) -> None:
        """ Loads the atlas picture file(s) """
        oAtlas:Atlas
        try:
            Logger.debug ('TheScreen: Loading Skin Atlas')
            if not Globals.bIgnoreAtlas:
                if Globals.oFnAtlasSkin.Exists():
                    oAtlas = Atlas(str(Globals.oFnAtlasSkin))
                    Cache.append('kv.atlas', str(Globals.oFnAtlasSkin), oAtlas)
                Logger.debug ('TheScreen: Loading Definition Atlas')
                if Globals.oDefinitionPathes.oFnDefinitionAtlas.Exists():
                    oAtlas = Atlas(str(Globals.oDefinitionPathes.oFnDefinitionAtlas))
                    Cache.append('kv.atlas', str(Globals.oDefinitionPathes.oFnDefinitionAtlas), oAtlas)
        except ParseError as e:
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=LogError(uMsg='TheScreen: Fatal Error:Load Atlas',oException=e),bAbort=True)
        return None

    def RegisterInterFaces(self,*,uInterFaceName:str) -> None:
        """ Registers all interfaces """
        Globals.oInterFaces.RegisterInterFaces(uInterFaceName,self.oProgessBar.value)
        return None

    def RegisterFonts(self,*,uFontName:str) -> None:
        """ Registers all fonts """
        self.oFonts.RegisterFonts(uFontName=uFontName,fSplashScreenPercentageStartValue=self.oProgessBar.value)
        return None

    def LoadActions_ForDefinition(self,*,uDefinitionName:str) -> None:
        """ Loads all definition actions """

        if not uDefinitionName:
            Globals.oDefinitions.LoadActions(fSplashScreenPercentageStartValue=self.oProgessBar.value)
        else:
            Globals.oDefinitions[uDefinitionName].LoadActions()
        return None

    def InitInterFaceSettings_ForDefinition(self,*,uDefinitionName:str) -> None:
        """ Initializes the inerface settings for the definitions """
        Globals.oDefinitions.InitInterFaceSettings(uDefinitionName=uDefinitionName,fSplashScreenPercentageStartValue=self.oProgessBar.value)
        return None

    def LoadFonts_ForDefinition(self,*,uDefinitionName:str) -> None:
        """ Loads the fonts files for the definitions """
        Globals.oDefinitions.LoadFonts(uDefinitionName=uDefinitionName,fSplashScreenPercentageStartValue=self.oProgessBar.value)
        return None

    def LoadLanguages_ForDefinition(self) -> None:
        """ Loads the language files for the definitions """
        Globals.oDefinitions.LoadLanguages(fSplashScreenPercentageStartValue=self.oProgessBar.value)
        return None

    def LoadGestures_ForDefinition(self,*,uDefinitionName:str) -> None:
        """ Loads the gestures files for the definitions """
        Globals.oDefinitions.LoadGestures(uDefinitionName=uDefinitionName,fSplashScreenPercentageStartValue=self.oProgessBar.value)
        return None

    def ParseDefinitionXmlFile(self,*,uDefinitionName:str) -> None:
        """ Loads the main definition xml file for the definitions"""
        Globals.oDefinitions.ParseXmlFiles(uDefinitionName=uDefinitionName,fSplashScreenPercentageStartValue=self.oProgessBar.value)
        return None

    def LoadSettings_ForDefinition(self,*,uDefinitionName:str) -> None:
        """ Loads all definition settings """

        if uDefinitionName=='PARSESETTINGS':
            Globals.oDefinitions.CreateSettingsJSONString()
        else:
            Globals.oDefinitions.LoadSettings(uDefinitionName=uDefinitionName,fSplashScreenPercentageStartValue=self.oProgessBar.value)
        return None

    def CheckToRotate(self) -> None:
        """ Check if we need to rotate the screen """

        oListDef:cDefinition
        uDefinitionDefaultOrientation:str
        fRatio:float

        oDef:cDefinition = Globals.oDefinitions[0]
        oET_Root:Element = oDef.oET_Root
        #Get Definition Wide Setting
        oRef             = oET_Root.find('def_parameter')

        for uListDefName in Globals.oDefinitions:
            oListDef                    = Globals.oDefinitions[uListDefName]
            oListDef.iDefMaxX           = GetXMLIntValue(oXMLNode=oRef, uTag='maxx',        bMandatory=True, iDefault=1)
            oListDef.iDefMaxY           = GetXMLIntValue(oXMLNode=oRef, uTag='maxy',        bMandatory=True, iDefault=1)
            oListDef.uOrientations      = GetXMLTextValue(oXMLNode=oRef,uTag='orientations',bMandatory=False,vDefault='landscape')

        uDefinitionDefaultOrientation = 'landscape'
        if oDef.iDefMaxX<oDef.iDefMaxY:
            uDefinitionDefaultOrientation='portrait'

        if not uDefinitionDefaultOrientation in oDef.uOrientations:
            ShowErrorPopUp(uMessage='Invalid Definition: Orientation does not match supportet orientations')

        #check if we need to swap x/y
        if Globals.uDeviceOrientation in oDef.uOrientations:
            for uListDefName in Globals.oDefinitions:
                oListDef = Globals.oDefinitions[uListDefName]
                uDefinitionDefaultOrientation = 'landscape'
                if oListDef.iDefMaxX<oListDef.iDefMaxY:
                    uDefinitionDefaultOrientation='portrait'
                if Globals.uDeviceOrientation != uDefinitionDefaultOrientation:
                    Logger.debug('Rotating the definition to supported orientation: '+oListDef.uName)
                    #oDef.iDefMaxX,oDef.iDefMaxY = oDef.iDefMaxY,oDef.iDefMaxX
                    oListDef.iDefMaxX,oListDef.iDefMaxY = oListDef.iDefMaxY,oListDef.iDefMaxX
            self.AdjustRatiosAfterResize()
        else:
            Logger.debug('Orientation not supported, rotating screen')
            Globals.bWaitForRotation=True
            SetVar(uVarName = 'WAITFORROTATION', oVarValue = '1')
            if Globals.uDeviceOrientation=='landscape':
                Globals.oRotation.SetOrientation_Portrait()
            else:
                Globals.oRotation.SetOrientation_Landscape()
            self.iRotateCount +=1
            Logger.debug('Rotation adjusted')

        if Globals.uStretchMode=='RESIZE':
            # noinspection PySimplifyBooleanCheck
            if kivy.core.window.Window.fullscreen!=True:
                fRatio=float(float(Globals.iAppWidth)/float(Globals.iAppHeight))/float(float(oDef.iDefMaxX)/float(oDef.iDefMaxY))
                if fRatio<1:
                    fRatio = float(oDef.iDefMaxX) / float(oDef.iDefMaxY)
                    Globals.iAppHeight=int(float(Globals.iAppWidth)/fRatio)
                elif fRatio>1:
                    fRatio = float(oDef.iDefMaxY) / float(oDef.iDefMaxX)
                    Globals.iAppWidth=int(float(Globals.iAppHeight)/fRatio)
                kivy.core.window.Window.size=(Globals.iAppWidth,Globals.iAppHeight)
        return None

    def AdjustRatiosAfterResize(self) -> None:
        """ we need to re-adjust the screen dimensions if we did change rotation of size  """

        oDef:cDefinition
        fRatio:float
        for uDefName in Globals.oDefinitions:
            oDef = Globals.oDefinitions[uDefName]
            fRatio=float(float(Globals.iAppWidth)/float(Globals.iAppHeight))/float(float(oDef.iDefMaxX)/float(oDef.iDefMaxY))
            # todo: Check, if we need to swap X/Y in the if clause
            if fRatio<1:
                oDef.fRationX           = float(oDef.iDefMaxX)/float(Globals.iAppWidth)
                oDef.fRationY           = float(oDef.iDefMaxY)/float(Globals.iAppHeight)
            else:
                oDef.fRationX           = float(oDef.iDefMaxX)/float(Globals.iAppWidth)
                oDef.fRationY           = float(oDef.iDefMaxY)/float(Globals.iAppHeight)

            Logger.debug('Ratios: Def [%s]: X=%d y=%d | Screen: X=%d y=%d' %(oDef.uName,oDef.iDefMaxX,oDef.iDefMaxY,Globals.iAppWidth,Globals.iAppHeight))
        return None

    def AddGlobalVars(self) -> None:
        """ Adds system vars """

        SetVar(uVarName='DEFINITIONROOTPATH',    oVarValue=str(Globals.oPathDefinitionRoot))
        SetVar(uVarName='CODESETPATH',           oVarValue=str(Globals.oPathCodesets))
        SetVar(uVarName='SKINPATH',              oVarValue=str(Globals.oPathSkin))
        SetVar(uVarName='SOUNDSPATH',            oVarValue=str(Globals.oPathSounds))
        SetVar(uVarName='RESOURCEPATH',          oVarValue=str(Globals.oPathResources))
        SetVar(uVarName='SHAREDDOCUMENTSPATH',   oVarValue=str(Globals.oPathSharedDocuments))
        SetVar(uVarName='INTERFACEPATH',         oVarValue=str(Globals.oPathInterface))
        SetVar(uVarName='INTERFACESETTINGSPATH', oVarValue=str(Globals.oDefinitionPathes.oPathDefinitionInterfaceSettings))
        SetVar(uVarName='SCRIPTSETTINGSPATH',    oVarValue=str(Globals.oDefinitionPathes.oPathDefinitionScriptSettings))
        SetVar(uVarName='APPLICATIONPATH',       oVarValue=str(Globals.oPathRoot))
        SetVar(uVarName='STANDARDPAGESPATH',     oVarValue=str(Globals.oPathStandardPages))
        SetVar(uVarName='STANDARDELEMENTSPATH',  oVarValue=str(Globals.oPathStandardElements))
        SetVar(uVarName='TMPPATH',               oVarValue=str(Globals.oPathTmp))
        SetVar(uVarName='ACTIONPATH',            oVarValue=str(Globals.oPathAction))
        SetVar(uVarName='GESTURESPATH',          oVarValue=str(Globals.oPathGestures))
        SetVar(uVarName='DOWNLOADSPATH',         oVarValue=str(Globals.oPathUserDownload))
        SetVar(uVarName='SKINNAME',              oVarValue=Globals.uSkinName)
        SetVar(uVarName='LANGUAGE',              oVarValue=Globals.uLanguage)
        SetVar(uVarName='CURRENTPAGE',           oVarValue='')
        SetVar(uVarName='LASTPAGE',              oVarValue='')
        SetVar(uVarName='LASTPAGEREAL',          oVarValue='')
        SetVar(uVarName='LOGFILE',               oVarValue=str(Globals.oFnLog))
        SetVar(uVarName='LICENSEFILE',           oVarValue=str(Globals.oFnLicense))
        SetVar(uVarName='CREDITSFILE',           oVarValue=str(Globals.oFnCredits))
        SetVar(uVarName='VERSION',               oVarValue=Globals.uVersion)
        SetVar(uVarName='LASTVERSION',           oVarValue=ToStringVersion(Globals.iLastInstalledVersion))
        SetVar(uVarName='AUTHOR',                oVarValue=Globals.uAuthor)
        SetVar(uVarName='SUPPORT',               oVarValue=Globals.uSupport)
        SetVar(uVarName='LOCALTIME',             oVarValue=Globals.oLanguage.GetLocalizedTime(Globals.bClockWithSeconds))
        SetVar(uVarName='LOCALDATE',             oVarValue=Globals.oLanguage.GetLocalizedDate(Globals.bLongDate, Globals.bLongMonth, Globals.bLongDay))
        SetVar(uVarName='IP_ADDRESSV4',          oVarValue=Globals.uIPAddressV4)
        SetVar(uVarName='IP_GATEWAYV4',          oVarValue=Globals.uIPGateWayV4)
        SetVar(uVarName='IP_SUBNETV4',           oVarValue=Globals.uIPSubNetV4)
        SetVar(uVarName='IP_ADDRESSV6',          oVarValue=Globals.uIPAddressV6)
        SetVar(uVarName='IP_ADDRESSV6FULL',      oVarValue=Globals.uIPAddressV6Full)
        SetVar(uVarName='IP_GATEWAYV6',          oVarValue=Globals.uIPGateWayV6)
        SetVar(uVarName='IP_SUBNETV6',           oVarValue=Globals.uIPSubNetV6)
        SetVar(uVarName='IP_INTERFACENAME_OS',   oVarValue=Globals.uIPInterfaceName_OS)
        SetVar(uVarName='IP_INTERFACENAME_PHYS', oVarValue=Globals.uIPInterfaceName_Phys)
        SetVar(uVarName='IP_INTERFACENAME_NICE', oVarValue=Globals.uIPInterfaceName_Nice)
        SetVar(uVarName='MAC_ADDRESS_COLON',     oVarValue=Globals.uMACAddressColon)
        SetVar(uVarName='MAC_ADDRESS_DASH',      oVarValue=Globals.uMACAddressDash)
        SetVar(uVarName='DEFAULTTRANSITIONTYPE', oVarValue=Globals.uDefaultTransitionType)
        SetVar(uVarName='DEFAULTTRANSITIONDIRECTION', oVarValue=Globals.uDefaultTransitionDirection)

        SetVar(uVarName='DEFINITIONSTARTPAGE',   oVarValue='Page_Settings')
        SetVar(uVarName='INTERFACENAMES',        oVarValue=Globals.oInterFaces.uInterFaceListSettingString)
        SetVar(uVarName='WAITFORROTATION',       oVarValue='0')
        SetVar(uVarName='FIRSTPAGE',             oVarValue='')
        SetVar(uVarName='RETCODE_ERROR',         oVarValue=str(eReturnCode.Error))
        SetVar(uVarName='RETCODE_SUCCESS',       oVarValue=str(eReturnCode.Success))

        # do NOT change this if we change the definition context
        SetVar(uVarName = 'DEFINITIONNAME',                        oVarValue = Globals.uDefinitionName)
        SetVar(uVarName = 'ORCASTANDARDPAGESTARTACTIONSINCLUDED',  oVarValue = '0')
        SetVar(uVarName = 'ORCASTANDARDPAGESINCLUDED',             oVarValue = '0')
        SetVar(uVarName = 'ORCASTANDARDGESTURESINCLUDED',          oVarValue = '0')
        SetVar(uVarName = 'ORCASTANDARDACTIONSINCLUDED',           oVarValue = '0')

        if Globals.aLogoPackFolderNames:
            SetVar('LOGOPACKFOLDERNAME', Globals.aLogoPackFolderNames[0])
            BuildSettingOptionListVar(Globals.aLogoPackFolderNames, 'SETTINGS_LOGOPACKFOLDERNAMES')
            uLogoPackFolderNames = GetVar('SETTINGS_LOGOPACKFOLDERNAMES')
            SetVar('SETTINGS_LOGOPACKFOLDERNAMES',uLogoPackFolderNames[1:-1])
        return None