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

import logging
import sys
import os
import math

from kivy.app                              import App
from kivy.clock                            import Clock
from kivy.config                           import Config as kivyConfig
from kivy.config                           import ConfigParser as OrcaConfigParser
# noinspection PyProtectedMember
from kivy.logger                           import FileHandler
from kivy.logger                           import Logger
from kivy.metrics                          import Metrics
from kivy.uix.settings                     import SettingsWithSpinner
# from kivy.core.window                      import Window

import ORCA.Globals as Globals

from ORCA.Actions                          import cActions
from ORCA.utils.Atlas                      import CreateAtlas
from ORCA.utils.Atlas                      import ClearAtlas
from ORCA.settings.AppSettings             import Build_Settings
from ORCA.definition.DefinitionPathes      import cDefinitionPathes
from ORCA.definition.Definitions           import cDefinitions
from ORCA.definition.Definitions           import GetDefinitionFileNameByName
from ORCA.download.DownLoadSettings        import cDownLoad_Settings
from ORCA.download.InstalledReps           import cInstalledReps
from ORCA.Events                           import cEvents
from ORCA.interfaces.Interfaces            import cInterFaces
from ORCA.International                    import cLanguage
from ORCA.Notifications                    import cNotifications
from ORCA.Screen_Init                      import cTheScreenWithInit
from ORCA.scripts.Scripts                  import cScripts
from ORCA.settings.SettingChanges          import OrcaConfigParser_On_Setting_Change
from ORCA.Sound                            import cSound
from ORCA.Parameter                        import cParameter
from ORCA.vars.Replace                     import ReplaceVars
from ORCA.vars.Links                       import DelAllVarLinks
from ORCA.vars.Access                      import SetVar
from ORCA.ui.ShowErrorPopUp                import ShowErrorPopUp
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Bool
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Float
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Str
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Int
from ORCA.utils.ConfigHelpers              import Config_GetDefault_Path
from ORCA.utils.ModuleLoader               import cModuleLoader
from ORCA.utils.FileName                   import cFileName
from ORCA.utils.Path                       import cPath
from ORCA.utils.LogError                   import LogError
from ORCA.utils.Network                    import cWaitForConnectivity
from ORCA.utils.CheckPermissions           import cCheckPermissions
from ORCA.utils.Platform                   import OS_GetDefaultNetworkCheckMode
from ORCA.utils.Platform                   import OS_GetDefaultStretchMode
from ORCA.utils.Platform                   import OS_GetLocale
from ORCA.utils.Platform                   import OS_GetWindowSize
from ORCA.utils.Platform                   import OS_GetInstallationDataPath
from ORCA.utils.Platform                   import OS_GetUserDownloadsDataPath
from ORCA.utils.Platform                   import OS_Platform
from ORCA.utils.Platform                   import OS_GetUserDataPath
from ORCA.utils.Platform                   import OS_GetIPAddressV4
from ORCA.utils.Platform                   import OS_GetIPAddressV6
from ORCA.utils.Platform                   import OS_GetGatewayV4
from ORCA.utils.Platform                   import OS_GetGatewayV6
from ORCA.utils.Platform                   import OS_GetSubnetV4
from ORCA.utils.Platform                   import OS_GetSubnetV6
from ORCA.utils.Platform                   import OS_GetMACAddress

from ORCA.utils.Rotation                   import cRotation
from ORCA.utils.Sleep                      import fSleep
from ORCA.utils.TypeConvert                import ToFloat
from ORCA.utils.TypeConvert                import ToIntVersion
from ORCA.utils.TypeConvert                import ToUnicode
from ORCA.utils.wait.StartWait             import StartWait
from ORCA.utils.wait.StopWait              import StopWait
from ORCA.definition.DefinitionContext     import SetDefinitionPathes
from ORCA.Queue                            import ClearQueue

class ORCA_App(App):
    """ The Main Orca Class, here starts all """

    def __init__(self):

        """
        We initialize all App vars. Even as this is formally not required in python,
        I prefer to have it this way
        """

        App.__init__(self)

        # Don't Move or change
        self.sVersion="4.6.4"
        self.sBranch="Dublin"

        #todo: Remove in release
        #Logger.setLevel(logging.DEBUG)

        Globals.uVersion                                    = ToUnicode(self.sVersion)
        Globals.iVersion                                    = ToIntVersion(Globals.uVersion)      # string of App Version
        SetVar(uVarName = u'REPVERSION', oVarValue = ToUnicode(Globals.iVersion))

        Globals.uBranch                                     = ToUnicode(self.sBranch)
        Globals.oApp                                        = self
        Globals.uPlatform                                   = OS_Platform()  # The used Platform
        Globals.oParameter                                  = cParameter()             # Object for Commandline and Environment Parameter

        Globals.aRepNames                                   = [('$lvar(683)', 'definitions'),
                                                               ('$lvar(690)', 'wizard templates'),
                                                               ('$lvar(684)', 'codesets'),
                                                               ('$lvar(685)', 'skins'),
                                                               ('$lvar(686)', 'interfaces'),
                                                               ('$lvar(730)', 'scripts'),
                                                               ('$lvar(687)', 'languages'),
                                                               ('$lvar(689)', 'sounds'),
                                                               ('$lvar(691)', 'fonts'),
                                                               ('$lvar(688)', 'others')]

        Globals.oModuleLoader                                = cModuleLoader()
        Globals.oOrcaConfigParser                            = OrcaConfigParser()
        Globals.oActions                                     = cActions()
        Globals.oCheckPermissions                            = cCheckPermissions()     # Object for checking, if we have permissions
        Globals.oDefinitions                                 = cDefinitions()           # Object which holds all loaded definitions
        Globals.oDownLoadSettings                            = cDownLoad_Settings()     # Object, for managing the settings dialog for download repositories
        Globals.oNotifications                               = cNotifications()
        Globals.oRotation                                    = cRotation()
        Globals.oLanguage                                    = cLanguage()
        Globals.oScripts                                     = cScripts()               # Object which holds all scripts
        Globals.oSound                                       = cSound()
        Globals.oInterFaces                                  = cInterFaces()            # Object which holds all Interfaces
        Globals.oWaitForConnectivity                         = cWaitForConnectivity()   # Object for checking, if we have network access
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
        self.uDefinitionToDelete                             = u''
        self.oPathSkinRoot                                   = None
        self.uSoundsName                                     = u''
        self.tOldSize                                        = (0,0)

        SetVar(uVarName = u'WAITFORROTATION', oVarValue = '0')
        OS_GetWindowSize()
        Logger.info(u'Init: ORCA Remote Application started: Version %s (%s):' % (Globals.uVersion, Globals.uPlatform))

        # Globals.oCheckPermissions.Wait()

    def build(self):
        """
        Frame work function, which gets called on application start
        All Initialisation functions start here
        We use it to show the splash
        and after that the schedule all init functions
        Init is scheduled to updated the splash screen for progress
        """

        try:
            # Window.borderless = True
            Globals.oCheckPermissions.Wait()
            kivyConfig.set('graphics', 'kivy_clock', 'interrupt')
            kivyConfig.set('kivy','log_maxfiles','3')
            Globals.oTheScreen = cTheScreenWithInit()       # Create the Screen Object
            Globals.oEvents = cEvents()                     # Create the Scheduler
            Clock.schedule_once(self.Init_ReadConfig, 0)    # Trigger the scheduled init functions
            return Globals.oTheScreen.oRootSM               # And return the root object (black background at first instance)
        except Exception as e:
            ShowErrorPopUp(uTitle='build: Fatal Error', uMessage=u'build: Fatal Error running Orca', bAbort=True, uTextContinue='', uTextQuit=u'Quit', oException=e)

    # noinspection PyUnusedLocal
    def On_Size(self, win, size):
        """ Function called by the Framework, when the size or rotation has changed """

        if self.tOldSize==size:
            return

        Logger.debug("Resize/rotation detected %d %d" % (size[0], size[1]))
        self.tOldSize = size
        Globals.iAppWidth, Globals.iAppHeight = size

        if Globals.iAppWidth < Globals.iAppHeight:
            Globals.uDeviceOrientation = 'portrait'
        else:
            Globals.uDeviceOrientation = 'landscape'

        SetVar(uVarName = u'DEVICEORIENTATION', oVarValue = Globals.uDeviceOrientation)
        SetVar(uVarName = u'SCREENSIZE', oVarValue = str(Globals.fScreenSize))
        SetVar(uVarName = u'WAITFORROTATION', oVarValue= '0')
        Globals.bWaitForRotation = False
        Globals.oTheScreen.AdjustRatiosAfterResize()

    # noinspection PyUnusedLocal
    def Init_ReadConfig(self, *largs):
        """
        Called by the timer to continue initalisation after appstart
        More or less all actions after here will be executed by the scheduler/queue
        """

        if not self.Init():
            return False

        Logger.debug(u'Late_Init: Screen Resolution: %d x %d' % (Globals.iAppWidth, Globals.iAppHeight))
        Logger.debug(u'Late_Init_StartInitActions')

        Globals.oTheScreen.Init()           # Add Global Vars first
        Globals.oInterFaces.Init()          # Create the Interfaces:

        # and execute the startup scripts
        aActions = Globals.oEvents.CreateSimpleActionList([{u'name':u'Show Message we begin',u'string': u'showsplashtext', u'maintext': u'Executing Startup Script'},
                                                           {u'name':u'And kick off the start up actions',u'string': u'loaddefinition'}
                                                          ])
        Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions, oParentWidget=None)
        return False

    # noinspection PyMethodMayBeStatic
    def DownloadDefinition(self, uDefinitionName):
        """
                Downloads a specific definition and restarts after
        """
        StartWait()
        Globals.oDownLoadSettings.LoadDirect(' :definitions:' + uDefinitionName, True)
        return False          # we do not proceed here as Downloader will restart


    def RestartAfterDefinitionLoad(self):
        """
        This function will get either called when we detect a new ORCA version we downloaded the updated ORCA repository files
        Or it will get called at the first time installation after we downloaded the setup definition
        in Both cases we restart ORCA to make changes effective
        """
        Globals.oOrcaConfigParser.set(u'ORCA', u'lastinstalledversion', str(Globals.iVersion))
        Globals.oOrcaConfigParser.write()

        # if we get called after a repository update caused by  new version install (but not on the first install)
        # we restart to make the changes effective
        # todo: check if we just need to skip restart as we might have updated several definitions
        if Globals.iVersion != Globals.iLastInstalledVersion and Globals.iLastInstalledVersion!=0:
            # self.ReStart()
            return True

        uTmp, uRepType, uRepName = Globals.oDownLoadSettings.uLast.split(':')

        if uRepType == u'definitions':
            if self.CheckForOrcaFiles():
                uDefName = GetDefinitionFileNameByName(uRepName)
                Globals.uDefinitionName = uDefName
                Globals.oOrcaConfigParser.set(u'ORCA', u'definition', uDefName)
                Globals.oOrcaConfigParser.write()
                self.ReStart()
                return True
        StopWait()
        return True

    # noinspection PyUnusedLocal
    def RestartAfterRepositoryUpdate(self, *largs):
        """
        Restarts ORCA, after a definition has been updated
        """
        Globals.oOrcaConfigParser.set(u'ORCA', u'lastinstalledversion', str(Globals.iVersion))
        Globals.oOrcaConfigParser.write()
        Globals.iLastInstalledVersion = Globals.iVersion
        StopWait()
        self.ReStart()
        return True

    def CheckForOrcaFiles(self):
        """
        Checks, if ORCA files are available somewhere
        """
        oFnCheck = cFileName(Globals.oPathRoot + 'actions')+ 'actions.xml'
        Logger.debug(u'Looking for Orca files at ' + oFnCheck.string)
        # if we can't find orca files (tested on the actions xml file), we stop here
        if not oFnCheck.Exists():
            Globals.bInit = False
            self.ShowSettings()
            uMsg = ReplaceVars("$lvar(415)") % Globals.oPathRoot.string
            Logger.critical(uMsg)
            ShowErrorPopUp(uTitle='CheckForOrcaFiles: Fatal Error', uMessage=uMsg, bAbort=True, uTextContinue='Continue',uTextQuit=u'Quit')
            return False
        return True

    def Init(self):
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
            # Globals.uIPAddressV4, Globals.uIPGateWayAssumedV4, Globals.uIPSubNetAssumedV4 = GetLocalIPV4()
            Globals.uIPAddressV4    = OS_GetIPAddressV4()
            Globals.uIPSubNetV4     = OS_GetSubnetV4()
            Globals.uIPGateWayV4    = OS_GetGatewayV4()

            # Globals.uIPAddressV6, Globals.uIPGateWayAssumedV6 = GetLocalIPV6()
            Globals.uIPAddressV6    = OS_GetIPAddressV6()
            Globals.uIPSubNetV6     = OS_GetSubnetV6()
            Globals.uIPGateWayV6    = OS_GetGatewayV6()

            Globals.uMACAddressColon, Globals.uMACAddressDash = OS_GetMACAddress()

            # Globals.uMACAddressColon, Globals.uMACAddressDash = GetMACAddress()
            Globals.oPathApp = cPath(os.getcwd())

            if Globals.oParameter.oPathDebug.string:
                Globals.oPathRoot     = Globals.oParameter.oPathDebug
                Globals.oPathAppReal  = Globals.oParameter.oPathDebug

            Logger.info('OrcaAppInit (Root/Real): Path: ' + Globals.oPathAppReal)
            Logger.info('OrcaAppInit (Root)     : Path: ' + Globals.oPathRoot)

            SetVar(uVarName = u'APPLICATIONPATH', oVarValue =  Globals.oPathRoot.string)
            SetVar(uVarName = u'WIZARDTEMPLATESPATH', oVarValue = (Globals.oPathRoot + "wizard templates").unixstring)

            if not Globals.oPathRoot.IsDir():
                    Globals.oPathRoot.Create()

            # Read all custom settings
            if not self.InitAndReadSettingsPanel():
                return False

            Globals.oLanguage.Init()                    # Init the Languages (dont load them)
            Globals.oInterFaces.LoadInterfaceList()     # load the list of all available interfaces
            Globals.oScripts.LoadScriptList()           # load the list of all available scripts

            # Create the atlas files for the skin and the definition
            if Globals.oDefinitionPathes.oPathDefinition.Exists():
                if Globals.uDefinitionName != "setup":
                    CreateAtlas(Globals.oDefinitionPathes.oPathDefinition, Globals.oDefinitionPathes.oFnDefinitionAtlas,u'Create Definition Atlas Files')

            Globals.bInit = True
            return True

        except Exception as e:
            uMsg = LogError(uMsg=u'App Init:Unexpected error:', oException=e)
            Logger.critical(uMsg)
            ShowErrorPopUp(uTitle='App Init:Fatal Error', uMessage=uMsg, bAbort=True, uTextContinue='', uTextQuit=u'Quit')
            self.bOnError = True
            return 0

    def InitAndReadSettingsPanel(self):
        """
        Reads the complete settings from the orca.ini file
        it will set setting defaults, if we do not have an ini file by now
        """
        try:
            if Globals.oParameter.oPathLog.string:
                oPathLogfile = Globals.oParameter.oPathLog
                oPathLogfile.Create()
                kivyConfig.set('kivy', 'log_dir', oPathLogfile.string)
                kivyConfig.write()
                # uOrgLogFn=Logger.manager.loggerDict["kivy"].handlers[1].filename
                Logger.debug(u"Init: Replacing Logfile Location to :"+Globals.oParameter.oPathLog.string)

            Logger.level=Logger.level

            Globals.fDoubleTapTime  = ToFloat(kivyConfig.getint('postproc', 'double_tap_time')) / 1000.0
            self.oFnConfig          = cFileName(Globals.oPathRoot) + u'orca.ini'

            oConfig                 = Globals.oOrcaConfigParser
            oConfig.filename        = self.oFnConfig.string
            if self.oFnConfig.Exists():
                oConfig.read(self.oFnConfig.string)

            if not oConfig.has_section(u'ORCA'):
                oConfig.add_section(u'ORCA')

            Globals.uDefinitionName = Config_GetDefault_Str(oConfig, u'ORCA', u'definition', u'setup')
            if "[" in Globals.uDefinitionName:
                Globals.uDefinitionName = Globals.uDefinitionName[Globals.uDefinitionName.find("[")+1 : Globals.uDefinitionName.find("]")]

            if Globals.uDefinitionName == u'setup':
                Logger.setLevel(logging.DEBUG)

            oRootPath = Config_GetDefault_Path(oConfig, u'ORCA', u'rootpath', Globals.oPathRoot.string)
            if oRootPath.string:
                Globals.oPathRoot = oRootPath
            oFnCheck = cFileName(Globals.oPathRoot + 'actions') +'actionsfallback.xml'
            if not oFnCheck.Exists():
                Globals.oPathRoot = OS_GetUserDataPath()

            Logger.debug(u'Init: Override Path:' + Globals.oPathRoot)

            self.InitRootDirs()
            Globals.iLastInstalledVersion = Config_GetDefault_Int(oConfig, u'ORCA', 'lastinstalledversion', Globals.uVersion)

            Globals.bProtected = (Globals.oPathRoot + u'protected').Exists()
            if Globals.bProtected:
                SetVar(uVarName = "PROTECTED", oVarValue = "1")
            else:
                SetVar(uVarName = "PROTECTED", oVarValue = "0")

            # get the installed interfaces , etc
            i = 0
            while True:
                oInstalledRep = cInstalledReps()
                uKey = u'installedrep%i_type' % i
                oInstalledRep.uType = Config_GetDefault_Str(oConfig, u'ORCA', uKey, '')
                uKey = u'installedrep%i_name' % i
                oInstalledRep.uName = Config_GetDefault_Str(oConfig, u'ORCA', uKey, '')
                uKey = u'installedrep%i_version' % i
                oInstalledRep.iVersion = Config_GetDefault_Int(oConfig, u'ORCA', uKey, "0")

                if not oInstalledRep.uName == '':
                    uKey = '%s:%s' % (oInstalledRep.uType, oInstalledRep.uName)
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
                uKey = u'repository' + str(i)
                uRep = ReplaceVars(Config_GetDefault_Str(oConfig, u'ORCA', uKey, uDefault))
                Globals.aRepositories.append(uRep)

                # we add some values for state, which helps for the Download Settings
                uKey = u'repository_state' + str(i)
                Config_GetDefault_Str(oConfig, u'ORCA', uKey, '1')

            # Getting the lists for skins, definitions and languages
            Globals.aSkinList          = self.oPathSkinRoot.GetFolderList()
            Globals.aLanguageList      = Globals.oPathLanguageRoot.GetFolderList()
            Globals.aDefinitionList    = Globals.oPathDefinitionRoot.GetFolderList()
            Globals.uSkinName          = Config_GetDefault_Str(oConfig, u'ORCA', u'skin', u'ORCA_silver_hires')
            self.uSoundsName           = Config_GetDefault_Str(oConfig, u'ORCA', u'sounds', u'ORCA_default')
            Globals.uLanguage          = Config_GetDefault_Str(oConfig, u'ORCA', u'language', OS_GetLocale())
            Globals.bShowBorders       = Config_GetDefault_Bool(oConfig, u'ORCA', u'showborders', u'0')
            Globals.uDefinitionContext = Globals.uDefinitionName

            if Globals.uDefinitionName == 'setup':
                Logger.setLevel(logging.DEBUG)

            if not Globals.uLanguage in Globals.aLanguageList:
                if len(Globals.aLanguageList) > 0:
                    Globals.uLanguage = Globals.aLanguageList[0]
            oConfig.set(u'ORCA', u'language', Globals.uLanguage)

            Globals.uLocalesName = Config_GetDefault_Str(oConfig, u'ORCA', u'locales', u'UK (12h)')

            if 'shared_documents' in Globals.aDefinitionList:
                Globals.aDefinitionList.remove('shared_documents')

            if not Globals.uDefinitionName in Globals.aDefinitionList:
                if len(Globals.aDefinitionList) > 0:
                    Globals.uDefinitionName = Globals.aDefinitionList[0]
                    oConfig.set(u'ORCA', u'definition', Globals.uDefinitionName)

            if not Globals.uSkinName in Globals.aSkinList:
                if len(Globals.aSkinList) > 0:
                    Globals.uSkinName = Globals.aSkinList[0]

            oConfig.set(u'ORCA', u'skin',               Globals.uSkinName)
            oConfig.set(u'ORCA', u'interface',          ReplaceVars("select"))
            oConfig.set(u'ORCA', u'script',             ReplaceVars("select"))
            oConfig.set(u'ORCA', u'definitionmanage',   ReplaceVars("select"))

            Globals.bInitPagesAtStart          = Config_GetDefault_Bool(oConfig, u'ORCA', u'initpagesatstartup', u'0')
            Globals.fDelayedPageInitInterval   = Config_GetDefault_Float(oConfig, u'ORCA', u'delayedpageinitinterval', u'60')
            Globals.fStartRepeatDelay          = Config_GetDefault_Float(oConfig, u'ORCA', u'startrepeatdelay', u'0.8')
            Globals.fContRepeatDelay           = Config_GetDefault_Float(oConfig, u'ORCA', u'contrepeatdelay', u'0.2')
            Globals.fLongPressTime             = Config_GetDefault_Float(oConfig, u'ORCA', u'longpresstime', u'1')
            Globals.bConfigCheckForNetwork     = Config_GetDefault_Bool(oConfig, u'ORCA', u'checkfornetwork', u'1')
            Globals.uNetworkCheckType          = Config_GetDefault_Str(oConfig, u'ORCA', u'checknetworktype',OS_GetDefaultNetworkCheckMode())
            Globals.uConfigCheckNetWorkAddress = Config_GetDefault_Str(oConfig, u'ORCA', u'checknetworkaddress', 'auto')
            Globals.bClockWithSeconds          = Config_GetDefault_Bool(oConfig, u'ORCA', u'clockwithseconds', u'1')
            Globals.bLongDate                  = Config_GetDefault_Bool(oConfig, u'ORCA', u'longdate', u'0')
            Globals.bLongDay                   = Config_GetDefault_Bool(oConfig, u'ORCA', u'longday', u'0')
            Globals.bLongMonth                 = Config_GetDefault_Bool(oConfig, u'ORCA', u'longmonth', u'0')
            Globals.bVibrate                   = Config_GetDefault_Bool(oConfig, u'ORCA', u'vibrate', u'0')
            Globals.bIgnoreAtlas               = Config_GetDefault_Bool(oConfig, u'ORCA', u'ignoreatlas', u'0')
            Globals.fScreenSize                = Config_GetDefault_Float(oConfig, u'ORCA', u'screensize', u'0')

            if Globals.fScreenSize == 0:
                Globals.fScreenSize = math.sqrt(Globals.iAppWidth ** 2 + Globals.iAppHeight ** 2) / Metrics.dpi

            self.InitOrientationVars()
            Globals.uStretchMode = Config_GetDefault_Str(oConfig, u'ORCA', u'stretchmode', OS_GetDefaultStretchMode())
            Globals.oSound.ReadSoundVolumesFromConfig(oConfig)
            oConfig.write()

            self.InitPathes()   # init all used pathes

            # clear cache in case of an update
            if self.bClearCaches:
                ClearAtlas()

            # Create and read the definition ini file
            Globals.oDefinitionConfigParser = oConfig = OrcaConfigParser()

            oConfig.filename = Globals.oDefinitionPathes.oFnDefinitionIni.string
            if Globals.oDefinitionPathes.oFnDefinitionIni.Exists():
                oConfig.read(Globals.oDefinitionPathes.oFnDefinitionIni.string)
            uSection = Globals.uDefinitionName
            uSection = uSection.replace(u' ', u'_')
            if not oConfig.has_section(uSection):
                oConfig.add_section(uSection)
            return True

        except Exception as e:
            uMsg = u'Global Init:Unexpected error reading settings:' + ToUnicode(e)
            Logger.critical(uMsg)
            ShowErrorPopUp(uTitle='InitAndReadSettingsPanel: Fatal Error', uMessage=uMsg, bAbort=True, uTextContinue='', uTextQuit=u'Quit')
            return 0

    # noinspection PyProtectedMember
    def InitOrientationVars(self):
        """
        Getting the orientation of the App and sets to system vars for it
        """
        Logger.debug(
            u'Setting Orientation Variables #1: Screen Size: [%s], Width: [%s], Heigth: [%s], Orientation: [%s]' % (
            str(Globals.fScreenSize), str(self._app_window._size[0]), str(self._app_window._size[1]),
            str(Globals.uDeviceOrientation)))

        OS_GetWindowSize()

        if Globals.iAppWidth < Globals.iAppHeight:
            Globals.uDeviceOrientation = 'portrait'
        else:
            Globals.uDeviceOrientation = 'landscape'

        Globals.oRotation.Lock()

        SetVar(uVarName = u'DEVICEORIENTATION', oVarValue = Globals.uDeviceOrientation)
        SetVar(uVarName = u'SCREENSIZE', oVarValue = str(Globals.fScreenSize))

        Logger.debug(u'Setting Orientation Variables: Screen Size: [%s], Width: [%s], Heigth: [%s], Orientation: [%s]' % (str(Globals.fScreenSize), str(Globals.iAppWidth), str(Globals.iAppHeight), str(Globals.uDeviceOrientation)))

    def RepositoryUpdate(self):
        """
        Updates all loaded repository files when a new ORCA version has been detected
        """

        if not Globals.bProtected:
            Logger.info("New ORCA version detected, updating all repositories")
            self.InitPathes()
            Globals.oTheScreen.LoadLanguage()
            StartWait()
            Globals.oDownLoadSettings.UpdateAllInstalledRepositories(bForce = False)
            self.bClearCaches = True
            # self.RestartAfterRepositoryUpdate()
            return True
        return False

    def InitRootDirs(self):
        """
        inits and creates the core pathes
        """

        Globals.oPathResources              = Globals.oPathRoot + u'resources'
        Globals.oPathInterface              = Globals.oPathRoot + u'interfaces'
        Globals.oPathAction                 = Globals.oPathRoot + u'actions'
        Globals.oPathCodesets               = Globals.oPathRoot + u'codesets'
        Globals.oPathSoundsRoot             = Globals.oPathRoot + u'sounds'
        if Globals.oParameter.oPathTmp.string:
            Globals.oPathTmp = Globals.oParameter.oPathTmp
        else:
            Globals.oPathTmp = Globals.oPathRoot + u'tmp'

        Globals.oPathDefinitionRoot        = Globals.oPathRoot + u'definitions'
        Globals.oPathSharedDocuments       = Globals.oPathDefinitionRoot  + u'shared_documents'
        self.oPathSkinRoot                 = Globals.oPathRoot + u'skins'
        Globals.oPathScripts               = Globals.oPathRoot + u'scripts'
        Globals.oPathLanguageRoot          = Globals.oPathRoot + u'languages'
        oPathGlobalSettings                = Globals.oPathRoot + u'globalsettings'
        Globals.oPathGlobalSettingsScripts = oPathGlobalSettings + u'scripts'
        Globals.oPathGlobalSettingsInterfaces = oPathGlobalSettings + u'interfaces'
        Globals.oPathTVLogos               = Globals.oPathResources + "tvlogos"
        Globals.oPathWizardTemplates       = Globals.oPathRoot + u"wizard templates"
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

    def InitPathes(self):
        """
        init all used pathes by the app (root pathes needs to be initialized)
        """

        Globals.oPathSkin                       = self.oPathSkinRoot                            + Globals.uSkinName

        oPathCheck = Globals.oPathSharedDocuments + "elements"+("skin_" + Globals.uSkinName)
        if oPathCheck.Exists():
            Globals.oPathStandardPages          =  oPathCheck
        else:
            Globals.oPathStandardPages          = (Globals.oPathSharedDocuments + "elements") +"skin_default"
        Globals.oPathUserDownload               = OS_GetUserDownloadsDataPath()
        Globals.oPathStandardElements           = Globals.oPathStandardPages
        Globals.oPathStandardPages              = Globals.oPathStandardPages + "pages"
        Globals.oFnElementIncludeWrapper        = cFileName(Globals.oPathStandardElements) + u'block_elementincludewrapper.xml'

        Globals.oFnSkinXml                      = cFileName(Globals.oPathSkin)                  + u'skin.xml'
        Globals.oPathSounds                     = cPath(Globals.oPathSoundsRoot)                + self.uSoundsName
        Globals.oFnSoundsXml                    = cFileName(Globals.oPathSounds)                + u'sounds.xml'
        Globals.oPathFonts                      = Globals.oPathResources                        + u'fonts'
        Globals.oFnGestureLog                   = cFileName(Globals.oPathRoot)                  + u'gestures.log'
        Globals.oFnLangInfo                     = cFileName(Globals.oPathLanguageRoot + Globals.uLanguage) + u'langinfo.xml'
        Globals.oFnAction                       = cFileName(Globals.oPathAction)                + u'actions.xml'
        Globals.oFnActionEarlyAppStart          = cFileName(Globals.oPathAction)                + u'actionsearly.xml'
        Globals.oFnActionFreshInstall           = cFileName(Globals.oPathAppReal+u'actions')    + u'actionsfallback.xml'
        Globals.oFnCredits                      = cFileName(Globals.oPathAppReal)               + u'credits.txt'

        Globals.oPathGestures                   = cPath(Globals.oPathAction)
        Globals.oFnGestures                     = cFileName(Globals.oPathGestures)              + u'gestures.xml'
        Globals.oFnLog                          = cFileName('').ImportFullPath(FileHandler.filename)
        Globals.oFnLicense                      = cFileName(Globals.oPathAppReal)               + u'license.txt'
        Globals.oPathCookie                     = Globals.oPathTmp
        Globals.uScriptLanguageFileTail         = u'/languages/'+Globals.uLanguage+'/strings.xml'
        Globals.uScriptLanguageFallBackTail     = u'/languages/English/strings.xml'
        Globals.oFnInterfaceLanguage            = cFileName(Globals.oPathInterface         + u'/%s/languages/' + Globals.uLanguage)  + u'strings.xml'
        Globals.oFnInterfaceLanguageFallBack    = cFileName(Globals.oPathInterface         + u'/%s/languages/English')               + u'strings.xml'
        oDefinitionPathes                       = cDefinitionPathes(Globals.uDefinitionName)
        Globals.dDefinitionPathes[Globals.uDefinitionName] = oDefinitionPathes
        SetDefinitionPathes(Globals.uDefinitionName)

        Globals.aLogoPackFolderNames            = Globals.oPathTVLogos.GetFolderList(bFullPath=False)

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
        pass

    def on_config_change(self, config, section, key, value):
        """
        call back, if the user changes a setting
        trigger the tools as well
        """
        OrcaConfigParser_On_Setting_Change(config=config,section=section,key=key,value=value)

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

    def ReStart(self):
        """
        Restarts the whole ORCA App
        """
        Logger.debug("Restarting ORCA....")
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
    def DeInit(self):
        """
        Call to stop Interfaces, Queues, Timer, Scripts
        """
        Globals.oNotifications.SendNotification("on_stopapp")

    def StopApp(self):
        """
        Stops the ORAC App
        """
        Logger.debug("Quit App on request")
        # self.DeInit()
        Globals.oSound.PlaySound('shutdown')
        fSleep(0.5)

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
            Logger.debug("System is going to pause")
            # We prevent any on_pause activities as long we didn't finish starting actions
            if Globals.oTheScreen.uCurrentPageName=="":
                return True
            Globals.oNotifications.SendNotification("on_pause")
            Globals.bOnSleep = True
        else:
            Logger.warning("Duplicate on_pause, this should not happen")
            # Globals.bOnSleep = False
        return True

    def on_resume(self):
        # this is the normal entry point, if android would work
        Globals.oNotifications.SendNotification("on_resume")
        Globals.bOnSleep = False
        return True

    def open_settings(self, *largs):
        # creates the settings panel (framework function)
        if Globals.oWinOrcaSettings is None:
            return App.open_settings(self, *largs)
        return False

    def close_settings(self, *largs):
        # close the settings pages and shows the first page
        # (if we did not start the definition, just continue with ini..)

        # If initialisiation failed, maybe the user entered a different location for ORCA Files, so lets restart
        if not Globals.bInit:
            self.ReStart()

        if Globals.oWinOrcaSettings is None:
            return App.close_settings(self, *largs)

        Globals.oNotifications.SendNotification("closesetting_orca")
        return True

    def _install_settings_keys(self, window):
        pass

    # noinspection PyUnusedLocal
    def hook_keyboard(self, window, key, *largs):
        """
        handles the esc key to stop the app, and other keys
        """

        key = str(key)
        Logger.debug('hook_keyboard: key:' + key)
        dRet = Globals.oNotifications.SendNotification("on_key",**{"key":key,"window":window})

        if dRet:
            key = dRet.get("key",key)

        # print ("Key:"+key)

        Globals.oNotifications.SendNotification("on_key_"+key)

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
        Logger.debug(u'Definition has changed, restarting ORCA')
        self.ReStart()

    def fktYesClose(self):
        """
        Function to called, if the user chosen to stop the app on a critical initialisation error
        """
        self.StopApp()

    def on_stop(self):
        """
        System Callback, which will be called when the app terminates
        """

        # Logger.debug('OnStop')
        if not self.bDeInitDone:
            self.bDeInitDone = True
            self.DeInit()
        return True

