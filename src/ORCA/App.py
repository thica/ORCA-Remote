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

from typing import List
from typing import Optional


import logging
import sys
import os
import math

from kivy.app                              import App
from kivy.clock                            import Clock
from kivy.config                           import Config as kivyConfig

# noinspection PyProtectedMember
from kivy.logger                           import FileHandler
from kivy.logger                           import Logger
from kivy.metrics                          import Metrics
from kivy.uix.settings                     import SettingsWithSpinner
from kivy.uix.widget                       import Widget
# from kivy.core.window                      import Window
from kivy.config                           import ConfigParser as OrcaConfigParser

from ORCA.action.Actions                   import cActions
from ORCA.Globals                          import Globals
from ORCA.Globals_Init                     import Globals_Init
from ORCA.action.Queue import ClearQueue
from ORCA.definition.DefinitionContext     import SetDefinitionPathes
from ORCA.definition.DefinitionPathes      import cDefinitionPathes
from ORCA.definition.Definitions           import GetDefinitionFileNameByName
from ORCA.download.InstalledReps           import cInstalledReps
from ORCA.screen.Screen_Init               import cTheScreenWithInit
from ORCA.settings.AppSettings             import Build_Settings
from ORCA.ui.ShowErrorPopUp                import ShowErrorPopUp
from ORCA.utils.Atlas                      import ClearAtlas
from ORCA.utils.Atlas                      import CreateAtlas
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Bool
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Float
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Int
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Path
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Str
from ORCA.utils.FileName                   import cFileName
from ORCA.utils.LogError                   import LogError
from ORCA.utils.Path                       import cPath
from ORCA.utils.Platform                   import OS_GetDefaultNetworkCheckMode
from ORCA.utils.Platform                   import OS_GetDefaultStretchMode
from ORCA.utils.Platform                   import OS_GetGatewayV4
from ORCA.utils.Platform                   import OS_GetGatewayV6
from ORCA.utils.Platform                   import OS_GetIPAddressV4
from ORCA.utils.Platform                   import OS_GetIPAddressV6
from ORCA.utils.Platform                   import OS_GetInstallationDataPath
from ORCA.utils.Platform                   import OS_GetInterfaceName
from ORCA.utils.Platform                   import OS_GetLocale
from ORCA.utils.Platform                   import OS_GetMACAddress
from ORCA.utils.Platform                   import OS_GetSubnetV4
from ORCA.utils.Platform                   import OS_GetSubnetV6
from ORCA.utils.Platform                   import OS_GetUserDataPath
from ORCA.utils.Platform                   import OS_GetUserDownloadsDataPath
from ORCA.utils.Platform                   import OS_GetWindowSize
from ORCA.utils.Sleep                      import fSleep
from ORCA.utils.TypeConvert                import ToFloat
from ORCA.utils.TypeConvert                import ToUnicode
from ORCA.utils.TypeConvert                import ToIntVersion
from ORCA.utils.wait.StartWait             import StartWait
from ORCA.utils.wait.StopWait              import StopWait
from ORCA.vars.Access                      import SetVar
from ORCA.vars.Links                       import DelAllVarLinks
from ORCA.vars.Replace                     import ReplaceVars

class ORCA_App(App):
    """ The Main Orca Class, here starts all """

    def __init__(self) -> None:

        """
        We initialize all App vars. Even as this is formally not required in python,
        I prefer to have it this way
        """

        App.__init__(self)

        # Don't Move or change
        self.sVersion="6.0.0"
        self.sBranch="Florence"

        Globals_Init(oApp=self)

        #todo: Remove in release
        #Logger.setLevel(logging.DEBUG)

        SetVar(uVarName = 'REPVERSION', oVarValue = ToUnicode(Globals.iVersion))

        self.bClearCaches                                    = False                    # If we install a new app version, all Caches (Atlas/Definition) are cleared
        self.bDeInitDone                                     = False                    # Flag, if de-initialisation already done
        self.bOnError                                        = False                    # Flag, if we got an error on app initialisation, Mainly used, if we can't find the ORCA definition files to give the user a chance to adjust the path
        self.bOnWait                                         = False                    # Flag, which shows, that a user has opened a questions No further actions behind this by now
        self.oDiscoverList                                   = None                     # Objects which represents the result of all discover scripts
        self.oInput                                          = None
        self.oWaitMessage                                    = None
        self.settings_cls                                    = SettingsWithSpinner
        self.title                                           = 'ORCA - Open Remote Control Application'
        self.oFnConfig                                       = None
        self.uDefinitionToDelete                             = ''
        self.oPathSkinRoot                                   = None
        self.uSoundsName                                     = ''
        self.tOldSize                                        = (0,0)

        SetVar(uVarName = 'WAITFORROTATION', oVarValue = '0')
        OS_GetWindowSize()
        Logger.info(f'Init: ORCA Remote Application started: Version {Globals.uVersion} ({Globals.uPlatform}):')

    def build(self) -> Optional[Widget]:
        """
        Framework function, which gets called on application start
        All Initialisation functions start here
        We use it to show the splash
        and after that the schedule all init functions
        Init is scheduled to update the splash screen for progress
        """

        try:
            # Window.borderless = True
            Globals.oCheckPermissions.Wait()
            kivyConfig.set('graphics', 'kivy_clock', 'interrupt')
            kivyConfig.set('kivy','log_maxfiles','3')
            Globals.oTheScreen = cTheScreenWithInit()               # Create the Screen Object
            Clock.schedule_once(self.Init_ReadConfig, 0)    # Trigger the scheduled init functions
            return Globals.oTheScreen.oRootSM                       # And return the root object (black background at first instance)
        except Exception as e:
            ShowErrorPopUp(uTitle='build: Fatal Error', uMessage='build: Fatal Error running Orca', bAbort=True, uTextContinue='', uTextQuit='Quit', oException=e)
        return None
    # noinspection PyUnusedLocal
    def On_Size(self, win, size) ->None:
        """ Function called by the Framework, when the size or rotation has changed """

        if self.tOldSize==size:
            return None

        Logger.debug(f'Resize/rotation detected {size[0]:d} {size[1]:d}')
        # todo: remove after Kivy Bug has been removed
        size = (Globals.iAppWidth, Globals.iAppHeight)

        self.tOldSize = size
        Globals.iAppWidth, Globals.iAppHeight = size

        if Globals.iAppWidth < Globals.iAppHeight:
            Globals.uDeviceOrientation = 'portrait'
        else:
            Globals.uDeviceOrientation = 'landscape'

        SetVar(uVarName = 'DEVICEORIENTATION', oVarValue = Globals.uDeviceOrientation)
        if Globals.oParameter.bSmallScreen:
            Globals.fScreenSize=4.5
        SetVar(uVarName = 'SCREENSIZE', oVarValue = str(Globals.fScreenSize))
        SetVar(uVarName = 'WAITFORROTATION', oVarValue= '0')
        Globals.bWaitForRotation = False
        Globals.oTheScreen.AdjustRatiosAfterResize()
        return None

    # noinspection PyUnusedLocal
    def Init_ReadConfig(self, *largs) ->bool:
        """
        Called by the timer to continue initialisation after appstart
        More or less all actions after here will be executed by the scheduler/queue
        """

        #from ORCA.utils.ParseResult_Test import ResultParser_Test
        # ResultParser_Test()

        aActions:List[cActions]

        if not self.Init():
            return False

        Logger.debug(f'Late_Init: Screen Resolution: {Globals.iAppWidth:d} x {Globals.iAppHeight:d}')
        Logger.debug('Late_Init_StartInitActions')

        Globals.oTheScreen.Init()           # Add Global Vars first
        Globals.oInterFaces.Init()          # Create the Interfaces:

        if Globals.bIsPersistenceMode:
            Globals.oPersistence.Read()  # we read the persistence data
            SetVar(uVarName="PERSISTENCESTART", oVarValue="TRUE")
            Globals.oPersistence.Kill(dummy=True)

        # and execute the startup scripts
        aActions = Globals.oEvents.CreateSimpleActionList(aActions = [  {'name':'Show Message we begin','string': 'showsplashtext', 'maintext': 'Executing Startup Script'},
                                                                        {'name':'And kick off the start up actions','string': 'loaddefinition'} ])

        Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions, oParentWidget=None, uQueueName="Initual Queue")
        return False

    # noinspection PyMethodMayBeStatic
    def DownloadDefinition(self, uDefinitionName) -> bool:
        """
                Downloads a specific definition and restarts after
        """
        StartWait()
        Globals.oDownLoadSettings.LoadDirect(uDirect=f' :definitions:{uDefinitionName}', bForce=True)
        return False          # we do not proceed here as Downloader will restart

    def RestartAfterDefinitionLoad(self)->bool:
        """
        This function will get either called when we detect a new ORCA version we downloaded the updated ORCA repository files
        Or it will get called at the first time installation after we downloaded the setup definition
        in Both cases we restart ORCA to make changes effective
        """
        Globals.iLastInstalledVersion = Globals.iVersion
        Globals.oOrcaConfigParser.set('ORCA', 'lastinstalledversion', str(Globals.iLastInstalledVersion))
        Globals.oOrcaConfigParser.write()

        # if we get called after a repository update caused by  new version install (but not on the first install)
        # we restart to make the changes effective
        # todo: check if we just need to skip restart as we might have updated several definitions
        if Globals.iVersion != Globals.iLastInstalledVersion and Globals.iLastInstalledVersion!=0:
            # self.ReStart()
            return True

        uTmp, uRepType, uRepName = Globals.oDownLoadSettings.uLast.split(':')

        if uRepType == 'definitions':
            if self.CheckForOrcaFiles():
                uDefName = GetDefinitionFileNameByName(uDefinitionName=uRepName)
                Globals.uDefinitionName = uDefName
                Globals.oOrcaConfigParser.set('ORCA', 'definition', uDefName)
                Globals.oOrcaConfigParser.write()
                self.ReStart()
                return True
        StopWait()
        return True

    # noinspection PyUnusedLocal
    def RestartAfterRepositoryUpdate(self, *largs)->bool:
        """
        Restarts ORCA, after a definition has been updated
        """
        Globals.oOrcaConfigParser.set('ORCA', 'lastinstalledversion', str(Globals.iVersion))
        Globals.oOrcaConfigParser.write()
        # Globals.iLastInstalledVersion = Globals.iVersion
        StopWait()
        self.ReStart()
        return True

    def CheckForOrcaFiles(self)->bool:
        """
        Checks, if ORCA files are available somewhere
        """
        oFnCheck = cFileName(Globals.oPathRoot + 'actions')+ 'actions.xml'
        Logger.debug('Looking for Orca files at ' + str(oFnCheck))
        # if we can't find orca files (tested on the actions xml file), we stop here
        if not oFnCheck.Exists():
            Globals.bInit = False
            self.ShowSettings()
            uMsg = ReplaceVars('$lvar(415)') % str(Globals.oPathRoot)
            Logger.critical(uMsg)
            ShowErrorPopUp(uTitle='CheckForOrcaFiles: Fatal Error', uMessage=uMsg, bAbort=True, uTextContinue='Continue',uTextQuit='Quit')
            return False
        return True

    def Init(self) -> bool:
        """
        first real init step
        Sets some basic vars
        and find/sets the path to the orca files
        """

        try:

            '''
            oPathAppReal: The path where the OS Installer places the installation files, eg the the fallback action files
                          Could be every where and could be a read only location
                          Not necessary the place where the binaries are
            oPathRoot:    This is the path, where to find the (downloaded) ORCA files. Can be changed in the settings
            '''

            Globals.oPathAppReal    = OS_GetInstallationDataPath()
            Globals.oPathRoot       = OS_GetUserDataPath()
            Globals.uIPAddressV4    = OS_GetIPAddressV4()
            Globals.uIPSubNetV4     = OS_GetSubnetV4()
            Globals.uIPGateWayV4    = OS_GetGatewayV4()

            dInterfaceNames                 = OS_GetInterfaceName()
            Globals.uIPInterfaceName_OS     = dInterfaceNames.uOSAdapterName
            Globals.uIPInterfaceName_Phys   = dInterfaceNames.uPysicalAdapterName
            Globals.uIPInterfaceName_Nice   = dInterfaceNames.uOSAdapterNiceName
            Globals.uMACAddressColon, Globals.uMACAddressDash = OS_GetMACAddress()

            # Has a dependency to the interfacename
            Globals.uIPAddressV6Full= OS_GetIPAddressV6()
            Globals.uIPAddressV6    = Globals.uIPAddressV6Full.split('%')[0]
            Globals.uIPSubNetV6     = OS_GetSubnetV6()
            Globals.uIPGateWayV6    = OS_GetGatewayV6()
            Globals.oPathApp        = cPath(os.getcwd())

            if str(Globals.oParameter.oPathDebug):
                Globals.oPathRoot     = Globals.oParameter.oPathDebug
                Globals.oPathAppReal  = Globals.oParameter.oPathDebug

            Logger.info(f'OrcaAppInit (Root/Real): Path: {Globals.oPathAppReal}')
            Logger.info(f'OrcaAppInit (Root)     : Path: {Globals.oPathRoot}' )

            SetVar(uVarName = 'APPLICATIONPATH', oVarValue =  str(Globals.oPathRoot))
            SetVar(uVarName = 'WIZARDTEMPLATESPATH', oVarValue = (Globals.oPathRoot + 'wizard templates').unixstring)

            if not Globals.oPathRoot.IsDir():
                    Globals.oPathRoot.Create()

            # Read all custom settings
            if not self.InitAndReadSettingsPanel():
                return False

            Globals.oLanguage.Init()                    # Init the Languages (doesn't load them)
            Globals.oInterFaces.LoadInterfaceList()     # load the list of all available interfaces
            Globals.oScripts.LoadScriptList()           # load the list of all available scripts

            # Create the atlas files for the skin and the definition
            if Globals.oDefinitionPathes.oPathDefinition.Exists():
                if Globals.uDefinitionName != 'setup':
                    CreateAtlas(oPicPath=Globals.oDefinitionPathes.oPathDefinition,oAtlasFile=Globals.oDefinitionPathes.oFnDefinitionAtlas,uDebugMsg='Create Definition Atlas Files')

            Globals.bIsPersistenceMode = Globals.oPersistence.HasOldSession()
            if Globals.bIsPersistenceMode:
                SetVar(uVarName="PERSISTENCESTART",oVarValue="TRUE")
            else:
                SetVar(uVarName="PERSISTENCESTART", oVarValue="FALSE")
            Globals.bInit = True
            return True

        except Exception as e:
            uMsg = LogError(uMsg='App Init:Unexpected error:', oException=e)
            Logger.critical(uMsg)
            ShowErrorPopUp(uTitle='App Init:Fatal Error', uMessage=uMsg, bAbort=True, uTextContinue='', uTextQuit='Quit')
            self.bOnError = True
            return False

    def InitAndReadSettingsPanel(self)->bool:
        """
        Reads the complete settings from the orca.ini file
        it will set setting defaults, if we do not have an ini file by now
        """
        #todo: Temporary
        if not str(Globals.oParameter.oPathLog):
            Globals.oParameter.oPathLog=OS_GetUserDownloadsDataPath()

        try:
            if str(Globals.oParameter.oPathLog):
                oPathLogfile = Globals.oParameter.oPathLog
                oPathLogfile.Create()
                kivyConfig.set('kivy', 'log_dir', str(oPathLogfile))
                kivyConfig.write()
                # uOrgLogFn=Logger.manager.loggerDict['kivy'].handlers[1].filename
                Logger.debug('Init: Replacing Logfile Location to :'+str(Globals.oParameter.oPathLog))

            Globals.fDoubleTapTime  = ToFloat(kivyConfig.getint('postproc', 'double_tap_time')) / 1000.0
            self.oFnConfig          = cFileName(Globals.oPathRoot) + 'orca.ini'

            oConfig                 = Globals.oOrcaConfigParser
            oConfig.filename        = str(self.oFnConfig)
            if self.oFnConfig.Exists():
                oConfig.read(str(self.oFnConfig))

            if not oConfig.has_section('ORCA'):
                oConfig.add_section('ORCA')

            Globals.uDefinitionName = Config_GetDefault_Str(oConfig=oConfig,uSection= 'ORCA',uOption= 'definition',vDefaultValue= 'setup')
            if '[' in Globals.uDefinitionName:
                Globals.uDefinitionName = Globals.uDefinitionName[Globals.uDefinitionName.find('[')+1 : Globals.uDefinitionName.find(']')]

            if Globals.uDefinitionName == 'setup':
                Logger.setLevel(logging.DEBUG)

            oRootPath = Config_GetDefault_Path(oConfig=oConfig, uSection='ORCA', uOption='rootpath', uDefaultValue=str(Globals.oPathRoot))
            if str(oRootPath):
                Globals.oPathRoot = oRootPath
            oFnCheck = cFileName(Globals.oPathRoot + 'actions') +'actionsfallback.xml'
            if not oFnCheck.Exists():
                Globals.oPathRoot = OS_GetUserDataPath()

            Logger.debug(f'Init: Override Path:{Globals.oPathRoot}')

            self.InitRootDirs()
            Globals.iLastInstalledVersion = Config_GetDefault_Int(oConfig=oConfig, uSection=u'ORCA', uOption='lastinstalledversion', uDefaultValue=Globals.uVersion)

            # The protected file /flag indicates, that we are in the development environment, so we will not download anything from the repository
            Globals.bProtected = (Globals.oPathRoot + 'protected').Exists()
            if Globals.bProtected:
                SetVar(uVarName = 'PROTECTED', oVarValue = '1')
            else:
                SetVar(uVarName = 'PROTECTED', oVarValue = '0')

            # get the installed interfaces , etc
            i = 0
            while True:
                oInstalledRep = cInstalledReps()
                uKey = f'installedrep{i:d}_type'
                oInstalledRep.uType = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption=uKey, vDefaultValue='')
                uKey = f'installedrep{i:d}_name'
                oInstalledRep.uName = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption=uKey, vDefaultValue='')
                uKey = f'installedrep{i:d}_version'
                oInstalledRep.iVersion = Config_GetDefault_Int(oConfig=oConfig, uSection='ORCA', uOption=uKey, uDefaultValue='0')

                if not oInstalledRep.uName == '':
                    uKey = f'{oInstalledRep.uType}:{oInstalledRep.uName}'
                    Globals.dInstalledReps[uKey] = oInstalledRep
                    i += 1
                else:
                    break

            del Globals.aRepositories[:]

            # get the configured repos
            for i in range(Globals.iCntRepositories):
                if i == 0:
                    uDefault = 'https://www.orca-remote.org/repositories/ORCA_$var(REPVERSION)/repositories'
                else:
                    uDefault = ''
                uKey = 'repository' + str(i)
                uRep = ReplaceVars(Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption=uKey, vDefaultValue=uDefault))
                Globals.aRepositories.append(uRep)

                # we add some values for state, which helps for the Download Settings
                uKey = 'repository_state' + str(i)
                Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption=uKey, vDefaultValue='1')

            # Getting the lists for skins, definitions and languages
            Globals.aSkinList                   = self.oPathSkinRoot.GetFolderList()
            Globals.aLanguageList               = Globals.oPathLanguageRoot.GetFolderList()
            Globals.aDefinitionList             = Globals.oPathDefinitionRoot.GetFolderList()
            Globals.uSkinName                   = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption='skin', vDefaultValue='ORCA_silver_hires')
            self.uSoundsName                    = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption='sounds', vDefaultValue='ORCA_default')
            Globals.uLanguage                   = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption='language', vDefaultValue=OS_GetLocale())
            Globals.bShowBorders                = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='showborders', uDefaultValue='0')
            Globals.uDefinitionContext          = Globals.uDefinitionName

            # this is temporary as some screen animation do not work in the final WINDOwS package (pyinstaller package)
            uDefaultType:str = 'fade'
            if Globals.uPlatform == 'win':
                uDefaultType = 'no'

            Globals.uDefaultTransitionType      = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption='defaulttransitiontype', vDefaultValue=uDefaultType)
            Globals.uDefaultTransitionDirection = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption='defaulttransitiondirection', vDefaultValue='left')

            if Globals.uDefinitionName == 'setup':
                Logger.setLevel(logging.DEBUG)

            if not Globals.uLanguage in Globals.aLanguageList:
                if len(Globals.aLanguageList) > 0:
                    Globals.uLanguage = Globals.aLanguageList[0]
            oConfig.set('ORCA', 'language', Globals.uLanguage)

            Globals.uLocalesName = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption='locales', vDefaultValue='UK (12h)')

            if 'shared_documents' in Globals.aDefinitionList:
                Globals.aDefinitionList.remove('shared_documents')

            if not Globals.uDefinitionName in Globals.aDefinitionList:
                if len(Globals.aDefinitionList) > 0:
                    Globals.uDefinitionName = Globals.aDefinitionList[0]
                    oConfig.set('ORCA', 'definition', Globals.uDefinitionName)

            if not Globals.uSkinName in Globals.aSkinList:
                if len(Globals.aSkinList) > 0:
                    Globals.uSkinName = Globals.aSkinList[0]

            oConfig.set('ORCA', 'skin',               Globals.uSkinName)
            oConfig.set('ORCA', 'interface',          ReplaceVars('select'))
            oConfig.set('ORCA', 'script',             ReplaceVars('select'))
            oConfig.set('ORCA', 'definitionmanage',   ReplaceVars('select'))

            Globals.bInitPagesAtStart          = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='initpagesatstartup', uDefaultValue='0')
            Globals.fDelayedPageInitInterval   = Config_GetDefault_Float(oConfig=oConfig, uSection='ORCA', uOption='delayedpageinitinterval',uDefaultValue= '60')
            Globals.fStartRepeatDelay          = Config_GetDefault_Float(oConfig=oConfig, uSection='ORCA', uOption='startrepeatdelay',uDefaultValue= '0.8')
            Globals.fContRepeatDelay           = Config_GetDefault_Float(oConfig=oConfig, uSection='ORCA', uOption='contrepeatdelay', uDefaultValue='0.2')
            Globals.fLongPressTime             = Config_GetDefault_Float(oConfig=oConfig, uSection='ORCA', uOption='longpresstime', uDefaultValue='1')
            Globals.bConfigCheckForNetwork     = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='checkfornetwork', uDefaultValue='1')
            Globals.uNetworkCheckType          = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption='checknetworktype',vDefaultValue=OS_GetDefaultNetworkCheckMode())
            Globals.uConfigCheckNetWorkAddress = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption='checknetworkaddress', vDefaultValue='auto')
            Globals.bClockWithSeconds          = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='clockwithseconds', uDefaultValue='1')
            Globals.bLongDate                  = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='longdate', uDefaultValue='0')
            Globals.bLongDay                   = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='longday', uDefaultValue='0')
            Globals.bLongMonth                 = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='longmonth', uDefaultValue='0')
            Globals.bVibrate                   = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='vibrate', uDefaultValue='0')
            Globals.bIgnoreAtlas               = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='ignoreatlas', uDefaultValue='0')
            Globals.fScreenSize                = Config_GetDefault_Float(oConfig=oConfig, uSection='ORCA', uOption='screensize', uDefaultValue='0')
            Globals.bPersistence_OnPageStart   = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='persistence_pagestart', uDefaultValue='0')
            Globals.bPersistence_OnSleep       = Config_GetDefault_Bool(oConfig=oConfig, uSection='ORCA', uOption='persistence_sleep', uDefaultValue='1')

            if Globals.fScreenSize == 0:
                Globals.fScreenSize = math.sqrt(Globals.iAppWidth ** 2 + Globals.iAppHeight ** 2) / Metrics.dpi

            self.InitOrientationVars()
            Globals.uStretchMode = Config_GetDefault_Str(oConfig=oConfig, uSection='ORCA', uOption='stretchmode', vDefaultValue=OS_GetDefaultStretchMode())
            Globals.oSound.ReadSoundVolumesFromConfig(oConfig=oConfig)
            oConfig.write()

            self.InitPathes()   # init all used pathes

            # clear cache in case of an update
            if self.bClearCaches:
                ClearAtlas()

            # Create and read the definition ini file
            Globals.oDefinitionConfigParser = OrcaConfigParser()

            Globals.oDefinitionConfigParser.filename = str(Globals.oDefinitionPathes.oFnDefinitionIni)
            if Globals.oDefinitionPathes.oFnDefinitionIni.Exists():
                Globals.oDefinitionConfigParser.read(str(Globals.oDefinitionPathes.oFnDefinitionIni))
            uSection = Globals.uDefinitionName
            uSection = uSection.replace(' ', '_')
            if not Globals.oDefinitionConfigParser.has_section(uSection):
                Globals.oDefinitionConfigParser.add_section(uSection)
            Globals.oPersistence.Register()
            return True

        except Exception as e:
            uMsg = 'Global Init:Unexpected error reading settings:' + ToUnicode(e)
            Logger.critical(uMsg)
            ShowErrorPopUp(uTitle='InitAndReadSettingsPanel: Fatal Error', uMessage=uMsg, bAbort=True, uTextContinue='', uTextQuit='Quit')
            return False

    # noinspection PyProtectedMember
    def InitOrientationVars(self)->None:
        """
        Getting the orientation of the App and sets to system vars for it
        """
        Logger.debug(f'Setting Orientation Variables #1: Screen Size: [{Globals.fScreenSize:f}], Width: [{self._app_window._size[0]:d}], Height: [{self._app_window._size[1]:d}], Orientation: [{Globals.uDeviceOrientation}]')

        OS_GetWindowSize()

        if Globals.iAppWidth < Globals.iAppHeight:
            Globals.uDeviceOrientation = 'portrait'
        else:
            Globals.uDeviceOrientation = 'landscape'

        Globals.oRotation.Lock()

        SetVar(uVarName = 'DEVICEORIENTATION', oVarValue = Globals.uDeviceOrientation)
        SetVar(uVarName = 'SCREENSIZE', oVarValue = str(Globals.fScreenSize))

        Logger.debug(f'Setting Orientation Variables #2: Screen Size: [{Globals.fScreenSize:f}], Width: [{Globals.iAppWidth:d}], Height: [{Globals.iAppHeight:d}], Orientation: [{Globals.uDeviceOrientation}]')

    def RepositoryUpdate(self)->bool:
        """
        Updates all loaded repository files when a new ORCA version has been detected
        """

        if not Globals.bProtected:
            Logger.info('New ORCA version detected, updating all repositories')
            self.InitPathes()
            Globals.oTheScreen.LoadLanguage()
            StartWait()
            Globals.oDownLoadSettings.UpdateAllInstalledRepositories(bForce = False)
            self.bClearCaches = True
            # self.RestartAfterRepositoryUpdate()
            return True
        return False

    def InitRootDirs(self)->None:
        """
        inits and creates the core pathes
        """

        Globals.oPathResources              = Globals.oPathRoot + 'resources'
        Globals.oPathInterface              = Globals.oPathRoot + 'interfaces'
        Globals.oPathAction                 = Globals.oPathRoot + 'actions'
        Globals.oPathCodesets               = Globals.oPathRoot + 'codesets'
        Globals.oPathSoundsRoot             = Globals.oPathRoot + 'sounds'
        if str(Globals.oParameter.oPathTmp):
            Globals.oPathTmp = Globals.oParameter.oPathTmp
        else:
            Globals.oPathTmp = Globals.oPathRoot + 'tmp'

        Globals.oPathDefinitionRoot        = Globals.oPathRoot + 'definitions'
        Globals.oPathSharedDocuments       = Globals.oPathDefinitionRoot  + 'shared_documents'
        self.oPathSkinRoot                 = Globals.oPathRoot + 'skins'
        Globals.oPathScripts               = Globals.oPathRoot + 'scripts'
        Globals.oPathLanguageRoot          = Globals.oPathRoot + 'languages'
        oPathGlobalSettings                = Globals.oPathRoot + 'globalsettings'
        Globals.oPathGlobalSettingsScripts = oPathGlobalSettings + 'scripts'
        Globals.oPathGlobalSettingsInterfaces = oPathGlobalSettings + 'interfaces'
        Globals.oPathTVLogos               = Globals.oPathResources + 'tvlogos'
        Globals.oPathWizardTemplates       = Globals.oPathRoot + 'wizard templates'
        Globals.oPathTmp.Create()
        Globals.oPathInterface.Create()
        Globals.oPathResources.Create()
        Globals.oPathCodesets.Create()
        Globals.oPathSoundsRoot.Create()
        Globals.oPathAction.Create()
        self.oPathSkinRoot.Create()
        Globals.oPathScripts.Create()
        Globals.oPathDefinitionRoot.Create()
        Globals.oPathSharedDocuments.Create()
        Globals.oPathLanguageRoot.Create()
        Globals.oPathWizardTemplates.Create()
        oPathGlobalSettings.Create()
        Globals.oPathGlobalSettingsScripts.Create()
        Globals.oPathGlobalSettingsInterfaces.Create()

        (Globals.oPathSharedDocuments + 'actions').Create()

    def InitPathes(self)->None:
        """
        init all used pathes by the app (root pathes needs to be initialized)
        """

        Globals.oPathSkin                       = self.oPathSkinRoot                            + Globals.uSkinName

        oPathCheck = Globals.oPathSharedDocuments + 'elements'+('skin_' + Globals.uSkinName)
        if oPathCheck.Exists():
            Globals.oPathStandardPages          =  oPathCheck
        else:
            Globals.oPathStandardPages          = (Globals.oPathSharedDocuments + 'elements') +'skin_default'
        Globals.oPathUserDownload               = OS_GetUserDownloadsDataPath()
        Globals.oPathStandardElements           = Globals.oPathStandardPages
        Globals.oPathStandardPages              = Globals.oPathStandardPages + 'pages'
        Globals.oFnElementIncludeWrapper        = cFileName(Globals.oPathStandardElements) + 'block_elementincludewrapper.xml'

        Globals.oFnSkinXml                      = cFileName(Globals.oPathSkin)                  + 'skin.xml'
        Globals.oPathSounds                     = cPath(Globals.oPathSoundsRoot)                + self.uSoundsName
        Globals.oFnSoundsXml                    = cFileName(Globals.oPathSounds)                + 'sounds.xml'
        Globals.oPathFonts                      = Globals.oPathResources                        + 'fonts'
        Globals.oFnGestureLog                   = cFileName(Globals.oPathUserDownload)          + 'gestures.log'
        Globals.oFnLangInfo                     = cFileName(Globals.oPathLanguageRoot + Globals.uLanguage) + 'langinfo.xml'
        Globals.oFnAction                       = cFileName(Globals.oPathAction)                + 'actions.xml'
        Globals.oFnActionEarlyAppStart          = cFileName(Globals.oPathAction)                + 'actionsearly.xml'
        Globals.oFnActionFreshInstall           = cFileName(Globals.oPathAppReal+'actions')     + 'actionsfallback.xml'
        Globals.oFnCredits                      = cFileName(Globals.oPathAppReal)               + 'credits.txt'

        Globals.oPathGestures                   = cPath(Globals.oPathAction)
        Globals.oFnGestures                     = cFileName(Globals.oPathGestures)              + 'gestures.xml'
        Globals.oFnLog                          = cFileName(FileHandler.filename)
        Globals.oFnLicense                      = cFileName(Globals.oPathAppReal)               + 'license.txt'
        Globals.oPathCookie                     = Globals.oPathTmp
        Globals.uScriptLanguageFileTail         = f'/languages/{Globals.uLanguage}/strings.xml'
        Globals.uScriptLanguageFallBackTail     = '/languages/English/strings.xml'
        Globals.oFnInterfaceLanguage            = cFileName(Globals.oPathInterface         + '/%s/languages/' + Globals.uLanguage)  + 'strings.xml'
        Globals.oFnInterfaceLanguageFallBack    = cFileName(Globals.oPathInterface         + '/%s/languages/English')               + 'strings.xml'
        oDefinitionPathes                       = cDefinitionPathes(uDefinitionName=Globals.uDefinitionName)
        Globals.dDefinitionPathes[Globals.uDefinitionName] = oDefinitionPathes
        SetDefinitionPathes(uDefinitionName=Globals.uDefinitionName)

        Globals.aLogoPackFolderNames            = Globals.oPathTVLogos.GetFolderList(bFullPath=False)
        Globals.oFnPersistence                  = cFileName(Globals.oPathTmp) + 'persistence.xml'

        if Globals.oDefinitionPathes.oPathDefinition.Exists():
            Globals.oDefinitionPathes.oPathDefinitionAtlas.Create()

    def build_settings(self, settings):
        """
        Called by the framework to build the settings json strings
        """
        Build_Settings(settings)

    def ShowSettings(self):
        """
        we use not the native function, maybe we add some more functions later
        """
        return self.open_settings()

    def On_CloseSetting(self, **kwArgs):
        """ Override the defaults, does nothing """
        pass

    # noinspection PyUnusedLocal
    def fdo_config_change_load_definition(self, *largs):
        """ loads a definition triggered by a configuration change """
        self._on_config_change_on_definitionlistchange()
        if not self.oWaitMessage is None:
            self.oWaitMessage.ClosePopup()

    # noinspection PyMethodMayBeStatic
    def _on_config_change_on_definitionlistchange(self):
        # reloads the definition list and restarts the settings dialog
        Globals.aDefinitionList = (Globals.oPathRoot + 'definitions').GetFolderList()
        Globals.aDefinitionList.remove('shared_documents')
        Globals.oTheScreen.UpdateSetupWidgets()

    def ReStart(self)->None :
        """
        Restarts the whole ORCA App
        """
        Logger.debug('Restarting ORCA....')
        Globals.oTheScreen.ShowSplash()
        # Whole restart
        # Stop the timer
        Globals.oTheScreen.DeInit()
        # Close the settings
        Globals.bInit = True
        self.close_settings()
        Globals.bInit = False
        # # Ensure, settings are recreated
        self._app_settings = None
        # Write current changes
        kivyConfig.write()
        # Delete the timers
        Globals.oEvents.oAllTimer.DeleteAllTimer()
        # Cancel Queue Events
        ClearQueue()
        # stop interfaces
        Globals.oInterFaces.DeInit()

        # Reset all the screen vars
        Globals.oTheScreen.InitVars()
        # delete all varlinks
        DelAllVarLinks()
        # And here we go again
        StopWait()
        Clock.schedule_once(self.Init_ReadConfig, 0)

    # noinspection PyMethodMayBeStatic
    def DeInit(self) ->None:
        """
        Call to stop Interfaces, Queues, Timer, Scripts
        """
        Globals.oNotifications.SendNotification(uNotification='on_stopapp')

    def StopApp(self):
        """
        Stops the ORCA App
        """
        Logger.debug('Quit App on request')
        # self.DeInit()
        Globals.oSound.PlaySound(SoundName=Globals.oSound.eSounds.shutdown)
        fSleep(fSeconds=0.5)

        if Globals.oPathUserDownload:
            Globals.oFnLog.Copy(oNewFile=cFileName(Globals.oPathUserDownload) + 'orca.log')
            # Globals.oFnLog.Delete()
        self.stop()
        sys.exit(0)

    def on_pause(self):
        """
        Called by the system, if the app goes on sleep
        Pauses Interfaces, Scripts, Timers
        """
        if not Globals.bOnSleep:
            Logger.debug('System is going to pause')
            # We prevent any on_pause activities as long we didn't finish starting actions
            if Globals.oTheScreen.uCurrentPageName=='':
                return True
            Globals.oNotifications.SendNotification(uNotification='on_pause')
            # Globals.bOnSleep = True #todo: check is this helps sometimes having black screen on resume
        else:
            Logger.warning('Duplicate on_pause, this should not happen')
            # Globals.bOnSleep = False
        return True

    def on_resume(self):
        """ this is the normal entry point, if android would work """
        Globals.oNotifications.SendNotification(uNotification='on_resume')
        Globals.bOnSleep = False
        return True

    def open_settings(self, *largs):
        """
        Creates the settings panel (framework function)
        :param largs:
        :return:
        """
        if Globals.oWinOrcaSettings is None:
            return App.open_settings(self, *largs)
        return False

    def close_settings(self, *largs):
        """
        close the settings pages and shows the first page
        (if we did not start the definition, just continue with ini)
        """

        # If initialisation failed, maybe the user entered a different location for ORCA Files, so lets restart
        if not Globals.bInit:
            self.ReStart()

        if Globals.oWinOrcaSettings is None:
            return App.close_settings(self, *largs)

        Globals.oNotifications.SendNotification(uNotification='closesetting_orca')
        return True

    def _install_settings_keys(self, window):
        pass

    # noinspection PyUnusedLocal
    def hook_keyboard(self, window, key, *largs):
        """
        handles the esc key to stop the app, and other keys
        """

        key = str(key)
        Logger.debug(f'hook_keyboard: key: {key}')
        dRet = Globals.oNotifications.SendNotification(uNotification='on_key',**{'key':key,'window':window})

        if dRet:
            key = dRet.get('key',key)

        # print ('Key:'+key)

        Globals.oNotifications.SendNotification(uNotification='on_key_'+key)

        if not Globals.oTheScreen.oCurrentPage is None:
            return Globals.oTheScreen.oCurrentPage.OnKey(window, 'key_' +key)
        else:
            if key == '27':
                self.StopApp()
        return False

    # noinspection PyUnusedLocal
    def on_config_change_change_definition(self, *largs):
        """
        Called from the dialog, when the user confirms to change the definition
        """
        Logger.debug('Definition has changed, restarting ORCA')
        self.ReStart()

    def fktYesClose(self):
        """
        Function to called, if the user chosen to stop the app on a critical initialisation error
        """
        self.StopApp()

    def on_stop(self) ->bool:
        """
        System Callback, which will be called when the app terminates
        """

        # Logger.debug('OnStop')
        if not self.bDeInitDone:
            self.bDeInitDone = True
            self.DeInit()
        return True

