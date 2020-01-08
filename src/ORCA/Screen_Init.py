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

from typing import Union

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

from ORCA.Screen                    import cTheScreen
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

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.definition.Definition import cDefinition
else:
    from typing import TypeVar
    cDefinition = TypeVar("cDefinition")


# noinspection PyMethodMayBeStatic
class cTheScreenWithInit(cTheScreen):
    """ Just for better code readability
        All Funtions to initialize the screen are here """
    def __init__(self):
        super(cTheScreenWithInit,self).__init__()
        self.oSplashBox:Union[BoxLayout,None]     = None
        self.oProgessBar:Union[ProgressBar,None]  = None
        self.ShowSplash()
        EventLoop.window.bind(size          = Globals.oApp.On_Size)
        EventLoop.window.bind(on_keyboard   = Globals.oApp.hook_keyboard)
        EventLoop.window.bind(on_motion     = self.on_motion)

    def Init(self) -> None:
        """ Adds the vars and the Settings options """
        self.AddGlobalVars()
        Globals.oNotifications.RegisterNotification("on_stopapp",self.DeInit,"The Screen")


    def __CreateSplashBackGround(self) -> None:
        """ Creates the Background for the splash screen """
        if len(self.oSplashBackground.children) == 0:
            self.oSplashBox                         = BoxLayout(orientation="vertical")
            self.oSplashLogger                      = Label(font_size = '24sp',text = u'Starting....', halign='center')
            self.oSplashLogger2                     = Label(font_size = '20sp',halign='center')
            self.oProgessBar                        = ProgressBar(size_hint=(0.5,None),pos_hint={'center_x': .5})
            self.oSplashBox.add_widget(Label())
            self.oSplashBox.add_widget(self.oSplashLogger)
            self.oSplashBox.add_widget(self.oProgessBar)
            self.oSplashBox.add_widget(self.oSplashLogger2)
            self.oSplashBackground.add_widget(self.oSplashBox)

    def LogToSplashScreen(self,uText:str,uPercentage:str='') -> None:
        """ Logs a main text message to the splash screen """
        self.uSplashText                        = uText
        self.oSplashLogger.size=(Globals.iAppWidth*0.95,Globals.iAppHeight/3)
        self.oSplashLogger.text_size=(Globals.iAppWidth*0.95,None)
        self.oSplashLogger.text                 = ReplaceVars(uText)
        if uPercentage!='':
            fPercentage:float
            if uPercentage.startswith('+'):
                fPercentage=self.oProgessBar.value+ToFloat(uPercentage[1:])
            else:
                fPercentage=ToFloat(uPercentage)
            self.oProgessBar.value=fPercentage

        self.LogToSplashScreen2('')

    def LogToSplashScreen2(self,uText:str,uPercentage:str='') -> None:
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

    def ShowSplash(self) -> None:
        """ Shows the splash screen """
        self.__CreateSplashBackGround()
        self.oRootSM.current = "SPLASH"
        self.LogToSplashScreen(u'Starting')

        # Remove all screens from screenmanager
        # There is no clear function for screen manager, so lets do it manually
        # this is required, as on restart there might be some screenmanager pages in the root (which we do no want anymore)
        while len(self.oRootSM.screens)>1:
            for oScreen in self.oRootSM.screens:
                if oScreen.name != "SPLASH":
                    self.oRootSM.remove_widget(oScreen)

    def LoadLanguage(self, uLanguageFileName:str=u'') -> None:
        """ Loads the languages files """
        try:
            if uLanguageFileName:
                Logger.info(u'TheScreen: Loading Language File [%s]' % uLanguageFileName)
                Globals.oLanguage.LoadXmlFile(uLanguageFileName)
            else:
                Logger.info(u'TheScreen: Loading Language [%s]' % Globals.uLanguage)
                Globals.oLanguage.LoadXmlFile("APP")
                self.LoadLocales()
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'TheScreen: LoadLanguage: can\'t load Language:',oException=e))

    def LoadLocales(self) -> None:
        """ Loads the locales """
        Logger.info (u'TheScreen: Loading Locales [%s]' % Globals.uLocalesName)
        try:
            if not Globals.uLocalesName in Globals.oLanguage.oLocales.oLocalesEntries:
                for  Globals.uLocalesName in Globals.oLanguage.oLocales.oLocalesEntries:
                    Logger.debug (u'TheScreen: Cant\'t find locales, defaulting to [%s]' % Globals.uLocalesName)
                    oConfig=Globals.oOrcaConfigParser
                    oConfig.set(u'ORCA', u'locales', Globals.uLocalesName)
                    break
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'TheScreen: LoadLocales: can\'t load Locales',oException=e))

    def LoadSkinDescription(self) -> None:
        """ Loads the skin description """
        self.oSkin.LoadSkinDescription()

    def LoadAtlas(self) -> None:
        """ Loads the atlas picture file(s) """
        oAtlas:Atlas
        try:
            Logger.debug (u'TheScreen: Loading Skin Atlas')
            if not Globals.bIgnoreAtlas:
                if Globals.oFnAtlasSkin.Exists():
                    oAtlas = Atlas(Globals.oFnAtlasSkin.string)
                    Cache.append('kv.atlas', Globals.oFnAtlasSkin.string, oAtlas)
                Logger.debug (u'TheScreen: Loading Definition Atlas')
                if Globals.oDefinitionPathes.oFnDefinitionAtlas.Exists():
                    oAtlas = Atlas(Globals.oDefinitionPathes.oFnDefinitionAtlas.string)
                    Cache.append('kv.atlas', Globals.oDefinitionPathes.oFnDefinitionAtlas.string, oAtlas)
        except ParseError as e:
            ShowErrorPopUp(uTitle="Fatal Error",uMessage=LogError(uMsg=u'TheScreen: Fatal Error:Load Atlas',oException=e),bAbort=True)

    def RegisterInterFaces(self,uInterFaceName:str) -> None:
        """ Registers all interfaces """
        Globals.oInterFaces.RegisterInterFaces(uInterFaceName,self.oProgessBar.value)

    def RegisterFonts(self,uFontName:str) -> None:
        """ Registers all fonts """
        self.oFonts.RegisterFonts(uFontName,self.oProgessBar.value)

    def LoadActions_ForDefinition(self,uDefinitionName:str) -> None:
        """ Loads all definition actions """

        if not uDefinitionName:
            Globals.oDefinitions.LoadActions(self.oProgessBar.value)
        else:
            Globals.oDefinitions[uDefinitionName].LoadActions()

    def InitInterFaceSettings_ForDefinition(self,uDefinitionName:str) -> None:
        """ Initializes the inerface settings for the definitions """
        Globals.oDefinitions.InitInterFaceSettings(uDefinitionName,self.oProgessBar.value)

    def LoadFonts_ForDefinition(self,uDefinitionName:str) -> None:
        """ Loads the fonts files for the definitions """
        Globals.oDefinitions.LoadFonts(uDefinitionName,self.oProgessBar.value)

    def LoadLanguages_ForDefinition(self) -> None:
        """ Loads the language files for the definitions """
        Globals.oDefinitions.LoadLanguages(self.oProgessBar.value)

    def LoadGestures_ForDefinition(self,uDefinitionName:str) -> None:
        """ Loads the gestures files for the definitions """
        Globals.oDefinitions.LoadGestures(uDefinitionName,self.oProgessBar.value)

    def ParseDefinitionXmlFile(self,uDefinitionName:str) -> None:
        """ Loads the main definition xml file for the definitions"""
        Globals.oDefinitions.ParseXmlFiles(uDefinitionName,self.oProgessBar.value)

    def LoadSettings_ForDefinition(self,uDefinitionName:str) -> None:
        """ Loads all definition settings """

        if uDefinitionName=='PARSESETTINGS':
            Globals.oDefinitions.CreateSettingsJSONString()
        else:
            Globals.oDefinitions.LoadSettings(uDefinitionName,self.oProgessBar.value)

    def CheckToRotate(self) -> None:
        """ Check if we need to rotate the screen """

        oListDef:cDefinition
        uDefinitionDefaultOrientation:str
        fRatio:float

        oDef:cDefinition = Globals.oDefinitions[0]
        oET_Root:Element = oDef.oET_Root
        #Get Definition Wide Setting
        oRef             = oET_Root.find('def_parameter')

        for oListDef in Globals.oDefinitions:
            oListDef.iDefMaxX           = GetXMLIntValue(oRef,u'maxx',True,1)
            oListDef.iDefMaxY           = GetXMLIntValue(oRef,u'maxy',True,1)
            oListDef.uOrientations      = GetXMLTextValue(oRef,u'orientations',False,'landscape')

        uDefinitionDefaultOrientation = 'landscape'
        if oDef.iDefMaxX<oDef.iDefMaxY:
            uDefinitionDefaultOrientation='portrait'

        if not uDefinitionDefaultOrientation in oDef.uOrientations:
            ShowErrorPopUp(uMessage='Invalid Definition: Orientation does not match supportet orientations')

        #check if we need to swap x/y
        if Globals.uDeviceOrientation in oDef.uOrientations:
            for oListDef in Globals.oDefinitions:
                uDefinitionDefaultOrientation = 'landscape'
                if oListDef.iDefMaxX<oListDef.iDefMaxY:
                    uDefinitionDefaultOrientation='portrait'
                if Globals.uDeviceOrientation != uDefinitionDefaultOrientation:
                    Logger.debug("Rotating the definition to supported orientation: "+oListDef.uName)
                    #oDef.iDefMaxX,oDef.iDefMaxY = oDef.iDefMaxY,oDef.iDefMaxX
                    oListDef.iDefMaxX,oListDef.iDefMaxY = oListDef.iDefMaxY,oListDef.iDefMaxX
            self.AdjustRatiosAfterResize()
        else:
            Logger.debug("Orientation not supported, rotating screen")
            Globals.bWaitForRotation=True
            SetVar(uVarName = u'WAITFORROTATION', oVarValue = '1')
            if Globals.uDeviceOrientation=='landscape':
                Globals.oRotation.SetOrientation_Portrait()
            else:
                Globals.oRotation.SetOrientation_Landscape()
            self.iRotateCount +=1
            Logger.debug("Rotation adjusted")

        if Globals.uStretchMode=="RESIZE":
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


    def AdjustRatiosAfterResize(self) -> None:
        """ we need to re-adjust the screen dimensions if we did change rotation of size  """

        oDef:cDefinition
        fRatio:float
        for oDef in Globals.oDefinitions:
            fRatio=float(float(Globals.iAppWidth)/float(Globals.iAppHeight))/float(float(oDef.iDefMaxX)/float(oDef.iDefMaxY))
            if fRatio<1:
                oDef.fRationX           = float(oDef.iDefMaxX)/float(Globals.iAppWidth)
                oDef.fRationY           = float(oDef.iDefMaxY)/float(Globals.iAppHeight)
            else:
                oDef.fRationX           = float(oDef.iDefMaxX)/float(Globals.iAppWidth)
                oDef.fRationY           = float(oDef.iDefMaxY)/float(Globals.iAppHeight)

            Logger.debug("Ratios: Def [%s]: X=%d y=%d | Screen: X=%d y=%d" %(oDef.uName,oDef.iDefMaxX,oDef.iDefMaxY,Globals.iAppWidth,Globals.iAppHeight))

    def AddGlobalVars(self) -> None:
        """ Adds system vars """

        SetVar(uVarName=u'DEFINITIONROOTPATH',    oVarValue=Globals.oPathDefinitionRoot.string)
        SetVar(uVarName=u'CODESETPATH',           oVarValue=Globals.oPathCodesets.string)
        SetVar(uVarName=u'SKINPATH',              oVarValue=Globals.oPathSkin.string)
        SetVar(uVarName=u'SOUNDSPATH',            oVarValue=Globals.oPathSounds.string)
        SetVar(uVarName=u'RESOURCEPATH',          oVarValue=Globals.oPathResources.string)
        SetVar(uVarName=u'SHAREDDOCUMENTSPATH',   oVarValue=Globals.oPathSharedDocuments.string)
        SetVar(uVarName=u'INTERFACEPATH',         oVarValue=Globals.oPathInterface.string)
        SetVar(uVarName=u'INTERFACESETTINGSPATH', oVarValue=Globals.oDefinitionPathes.oPathDefinitionInterfaceSettings.string)
        SetVar(uVarName=u'SCRIPTSETTINGSPATH',    oVarValue=Globals.oDefinitionPathes.oPathDefinitionScriptSettings.string)
        SetVar(uVarName=u'APPLICATIONPATH',       oVarValue=Globals.oPathRoot.string)
        SetVar(uVarName=u'STANDARDPAGESPATH',     oVarValue=Globals.oPathStandardPages.string)
        SetVar(uVarName=u'STANDARDELEMENTSPATH',  oVarValue=Globals.oPathStandardElements.string)
        SetVar(uVarName=u'TMPPATH',               oVarValue=Globals.oPathTmp.string)
        SetVar(uVarName=u'ACTIONPATH',            oVarValue=Globals.oPathAction.string)
        SetVar(uVarName=u'GESTURESPATH',          oVarValue=Globals.oPathGestures.string)
        SetVar(uVarName=u'SKINNAME',              oVarValue=Globals.uSkinName)
        SetVar(uVarName=u'LANGUAGE',              oVarValue=Globals.uLanguage)
        SetVar(uVarName=u'CURRENTPAGE',           oVarValue=u'')
        SetVar(uVarName=u'LASTPAGE',              oVarValue=u'')
        SetVar(uVarName=u'LASTPAGEREAL',          oVarValue=u'')
        SetVar(uVarName=u'LOGFILE',               oVarValue=Globals.oFnLog.string)
        SetVar(uVarName=u'LICENSEFILE',           oVarValue=Globals.oFnLicense.string)
        SetVar(uVarName=u'CREDITSFILE',           oVarValue=Globals.oFnCredits.string)
        SetVar(uVarName=u'VERSION',               oVarValue=Globals.uVersion)
        SetVar(uVarName=u'LASTVERSION',           oVarValue=ToUnicode(ToStringVersion(Globals.iLastInstalledVersion)))
        SetVar(uVarName=u'AUTHOR',                oVarValue=Globals.uAuthor)
        SetVar(uVarName=u'SUPPORT',               oVarValue=Globals.uSupport)
        SetVar(uVarName=u'LOCALTIME',             oVarValue=Globals.oLanguage.GetLocalizedTime(Globals.bClockWithSeconds))
        SetVar(uVarName=u'LOCALDATE',             oVarValue=Globals.oLanguage.GetLocalizedDate(Globals.bLongDate, Globals.bLongMonth, Globals.bLongDay))
        SetVar(uVarName=u'IP_ADDRESSV4',          oVarValue=Globals.uIPAddressV4)
        SetVar(uVarName=u'IP_GATEWAYV4',          oVarValue=Globals.uIPGateWayV4)
        SetVar(uVarName=u'IP_SUBNETV4',           oVarValue=Globals.uIPSubNetV4)
        SetVar(uVarName=u'IP_ADDRESSV6',          oVarValue=Globals.uIPAddressV6)
        SetVar(uVarName=u'IP_GATEWAYV6',          oVarValue=Globals.uIPGateWayV6)
        SetVar(uVarName=u'IP_SUBNETV6',           oVarValue=Globals.uIPSubNetV6)
        SetVar(uVarName=u'MAC_ADDRESS_COLON',     oVarValue=Globals.uMACAddressColon)
        SetVar(uVarName=u'MAC_ADDRESS_DASH',      oVarValue=Globals.uMACAddressDash)
        SetVar(uVarName=u'DEFINITIONSTARTPAGE',   oVarValue=u'Page_Settings')
        SetVar(uVarName=u'INTERFACENAMES',        oVarValue=Globals.oInterFaces.uInterFaceListSettingString)
        SetVar(uVarName=u'WAITFORROTATION',       oVarValue=u'0')
        SetVar(uVarName=u'FIRSTPAGE',             oVarValue=u'')
        SetVar(uVarName=u'RETCODE_ERROR',         oVarValue=str(eReturnCode.Error))
        SetVar(uVarName=u'RETCODE_SUCCESS',       oVarValue=str(eReturnCode.Success))

        # do NOT change this if we change the definitioncontext
        SetVar(uVarName = u'DEFINITIONNAME',                        oVarValue = Globals.uDefinitionName)
        SetVar(uVarName = u'ORCASTANDARDPAGESTARTACTIONSINCLUDED',  oVarValue = u"0")
        SetVar(uVarName = u'ORCASTANDARDPAGESINCLUDED',             oVarValue = u"0")
        SetVar(uVarName = u"ORCASTANDARDGESTURESINCLUDED",          oVarValue = u"0")
        SetVar(uVarName = u'ORCASTANDARDACTIONSINCLUDED',           oVarValue = u"0")

        if Globals.aLogoPackFolderNames:
            SetVar("LOGOPACKFOLDERNAME", Globals.aLogoPackFolderNames[0])
            BuildSettingOptionListVar(Globals.aLogoPackFolderNames, "SETTINGS_LOGOPACKFOLDERNAMES")
            uLogoPackFolderNames = GetVar("SETTINGS_LOGOPACKFOLDERNAMES")
            SetVar("SETTINGS_LOGOPACKFOLDERNAMES",uLogoPackFolderNames[1:-1])
