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


from typing import Dict
from typing import List
from typing import Tuple
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kivy.config import Config
    from ORCA.App                              import ORCA_App
    from ORCA.action.Actions import cActions
    from ORCA.definition.DefinitionPathes      import cDefinitionPathes
    from ORCA.definition.Definitions           import cDefinitions
    from ORCA.download.DownLoadSettings        import cDownLoad_Settings
    from ORCA.action.Events import cEvents
    from ORCA.International                    import cLanguage
    from ORCA.screen.Screen_Init import cTheScreenWithInit
    from ORCA.scripts.Scripts                  import cScripts
    from ORCA.Sound                            import cSound
    from ORCA.utils.Network                    import cWaitForConnectivity
    from ORCA.utils.CheckPermissions           import cCheckPermissions
    from ORCA.utils.Rotation                   import cRotationLayer
    from ORCA.utils.FTP                        import cFTP
    from ORCA.utils.FileName                   import cFileName
    from ORCA.utils.Path                       import cPath
    from ORCA.interfaces.Interfaces            import cInterFaces
    from ORCA.utils.Persistence import cPersistence
    from ORCA.utils.Notifications import cNotifications
    from ORCA.utils.ModuleLoader               import cModuleLoader
    from ORCA.download.InstalledReps           import cInstalledReps
else:
    from typing import TypeVar
    Config                  = TypeVar('Config')
    ORCA_App                = TypeVar('ORCA_App')
    cActions                = TypeVar('cActions')
    cCheckPermissions       = TypeVar('cCheckPermissions')
    cDefinitionPathes       = TypeVar('cDefinitionPathes')
    cDefinitions            = TypeVar('cDefinitions')
    cDownLoad_Settings      = TypeVar('cDownLoad_Settings')
    cEvents                 = TypeVar('cEvents')
    cFTP                    = TypeVar('cFTP')
    cFileName               = TypeVar('cFileName')
    cInstalledReps          = TypeVar('cInstalledReps')
    cInterFaces             = TypeVar('cInterFaces')
    cLanguage               = TypeVar('cLanguage')
    cModuleLoader           = TypeVar('cModuleLoader')
    cNotifications          = TypeVar('cNotifications')
    cParameter              = TypeVar('cParameter')
    cPath                   = TypeVar('cPath')
    cPersistence            = TypeVar('cPersistence')
    cRotationLayer          = TypeVar('cRotationLayer')
    cScripts                = TypeVar('cScripts')
    cSound                  = TypeVar('cSound')
    cTheScreenWithInit      = TypeVar('cTheScreenWithInit')
    cWaitForConnectivity    = TypeVar('cWaitForConnectivity')


class cGlobals:

    aDefinitionList:List[str]                           = []
    aLanguageList:List[str]                             = []
    aLogoPackFolderNames:List[str]                      = []
    aRepNames:List[Tuple[str,str]]                      = []
    aRepositories:List[str]                             = []     # Online Repositories
    aSkinList:List[str]                                 = []     # List of all available skins (Just their names)
    aTransitionDirections:List[str]                     = ['left','right','up','down']
    aTransitionTypes:List[str]                          = ['no','fade','slide','wipe','swap','fallout','risein']
    aTVLogoList:List[str]                               = []
    bClockWithSeconds:bool                              = False  # Flag, if we want to have the clock with seconds
    bConfigCheckForNetwork:bool                         = True   # Flag, if we should check for network connectivity on application start / resume
    bHasPermissions:bool                                = False  # Flag, if ORCA has sufficient permissions
    bIgnoreAtlas:bool                                   = False  # Flag, if we would ignore the Kivy Atlas function to cache Images
    bInit:bool                                          = False  # Flag, if app has been initialized to prevent double initialisations
    bInitPagesAtStart:bool                              = False  # Flag, if we would initialize all pages at startup
    bIsPersistenceMode:bool                             = False  # Flag, if we have an abnormal app end
    bLongDate:bool                                      = False  # Flag, if we would use long date format
    bLongDay:bool                                       = False  # Flag, if we would use long day format
    bLongMonth:bool                                     = False  # Flag, if we would use long month format
    bOnSleep:bool                                       = False  # Flag to be used, if the system is on  (system) sleep, Changes the scheduler behaviour
    bPersistence_OnSleep                                = False  # Flag to be used, if persistence should be created on_sleep
    bPersistence_OnPageStart                            = True   # Flag to be used, if persistence should be created on page start
    bProtected:bool                                     = False  # Flag, if we do want to prevent repository updates and initial setup download
    bShowBorders:bool                                   = False  # Flag, if we should show borders
    bVibrate:bool                                       = True   # Flag, if we should vibrate in button press
    bWaitForRotation:bool                               = False  # Flag, if Rotation has been detected by kivy
    dDefinitionPathes:Dict[str,cDefinitionPathes]       = {}     # Dict of Array of definition pathes
    dIcons:Dict[str,Dict[str,str]]                      = {}     # Dict of all Icons
    dInstalledReps:Dict[str,cInstalledReps]             = {}     # Installed packages
    fContRepeatDelay:float                              = 0.2    # Gap time between repeating the button action on long continous button press
    fDelayedPageInitInterval:float                      = 10.0   # Gap time betweeen creation of pages if we have a deleyed page creation
    fDoubleTapTime:float                                = 0.250  # DoubleTabTime from Config
    fLongPressTime:float                                = 1.0    # Time to get a button press as a long press
    fScreenSize:float                                   = 0.0    # Display Size in inch eg 5 or 7, or 10
    fStartRepeatDelay:float                             = 0.5    # Time on button press before we start repeating the action
    iAppHeight:int                                      = 0      # Application Height in Pixel
    iAppWidth:int                                       = 0
    iCntRepositories:int                                = 5      # Number of Repositories, which can be configured
    iLastInstalledVersion:int                           = 0
    iVersion:int                                        = 0
    oActions:Optional[cActions]                                   = None
    oApp:Optional[ORCA_App]                                       = None
    oCheckPermissions:Optional[cCheckPermissions]                 = None   # Object for checking, if we have permissions
    oDefinitionConfigParser:Optional[Config]                      = None   # The configparser object
    oDefinitionPathes:Optional[cDefinitionPathes]                 = None   # The current DefinitionPathes
    oDefinitions:Optional[cDefinitions]                           = None   # Object which holds all loaded definitions
    oDownLoadSettings:Optional[cDownLoad_Settings]                = None   # Object, for managing the settings dialog for download repositories
    oEvents:Optional[cEvents]                                     = None   # Object for Events / Queues
    oFTP:Optional[cFTP]                                           = None   # FTP Object for the repository manager
    oFnAction:Optional[cFileName]                                 = None
    oFnActionEarlyAppStart:Optional[cFileName]                    = None
    oFnActionFreshInstall:Optional[cFileName]                     = None
    oFnAtlasSkin:Optional[cFileName]                              = None
    oFnCredits:Optional[cFileName]                                = None
    oFnElementIncludeWrapper:Optional[cFileName]                  = None
    oFnGestureLog:Optional[cFileName]                             = None
    oFnGestures:Optional[cFileName]                               = None
    oFnInterfaceLanguage:Optional[cFileName]                      = None
    oFnInterfaceLanguageFallBack:Optional[cFileName]              = None
    oFnLangInfo:Optional[cFileName]                               = None
    oFnLicense:Optional[cFileName]                                = None
    oFnLog:Optional[cFileName]                                    = None
    oFnPersistence:Optional[cFileName]                            = None
    oFnSkinXml:Optional[cFileName]                                = None
    oFnSoundsXml:Optional[cFileName]                              = None
    oInterFaces:Optional[cInterFaces]                             = None   # Object which holds all Interfaces
    oLanguage:Optional[cLanguage]                                 = None
    oModuleLoader:Optional[cModuleLoader]                         = None   # Object to hold dynamic loaded python modules (scripts, interfaces,...)
    oNotifications:Optional[cNotifications]                       = None # Notification Handler
    oOrcaConfigParser:Optional[Config]                            = None
    oParameter:Optional[cParameter]                               = None
    oPathAction:Optional[cPath]                                   = None
    oPathApp:Optional[cPath]                                      = None
    oPathAppReal:Optional[cPath]                                  = None
    oPathCodesets:Optional[cPath]                                 = None
    oPathCookie:Optional[cPath]                                   = None
    oPathDefinitionRoot:Optional[cPath]                           = None
    oPathFonts:Optional[cPath]                                    = None
    oPathGestures:Optional[cPath]                                 = None
    oPathGlobalSettingsInterfaces:Optional[cPath]                 = None
    oPathGlobalSettingsScripts:Optional[cPath]                    = None
    oPathInterface:Optional[cPath]                                = None
    oPathLanguageRoot:Optional[cPath]                             = None
    oPathResources:Optional[cPath]                                = None
    oPathRoot:Optional[cPath]                                     = None    # The "root path" where to store / find the Orca data files. This can be replaced by custom settings, so uRootPath is the one, which is then really used
    oPathScripts:Optional[cPath]                                  = None
    oPathSharedDocuments:Optional[cPath]                          = None
    oPathSkin:Optional[cPath]                                     = None
    oPathSounds:Optional[cPath]                                   = None
    oPathSoundsRoot:Optional[cPath]                               = None
    oPathStandardElements:Optional[cPath]                         = None
    oPathStandardPages:Optional[cPath]                            = None
    oPathTVLogos:Optional[cPath]                                  = None
    oPathTmp:Optional[cPath]                                      = None
    oPathUserDownload:Optional[cPath]                             = None
    oPathWizardTemplates:Optional[cPath]                          = None
    oPersistence:Optional[cPersistence]                           = None
    oRotation:Optional[cRotationLayer]                            = None
    oScripts:Optional[cScripts]                                   = None   # Object which holds all scripts
    oSound:Optional[cSound]                                       = None   # Object to play standard sound
    oTheScreen:Optional[cTheScreenWithInit]                       = None   # The Screen Object which holds all pages and widgets
    oWaitForConnectivity:Optional[cWaitForConnectivity]           = None   # Object for checking, if we have network access
    oWinOrcaSettings:Optional[Config]                             = None   # Object for the settings page
    uAuthor:str                                         = 'Carsten Thielepape'
    uBranch:str                                         = ''
    uConfigCheckNetWorkAddress:str                      = 'auto'
    uDefaultTransitionDirection                         = 'left'
    uDefaultTransitionType                              = 'fade'
    uDefinitionContext:str                              = ''   # CurrentDefinitionContext
    uDefinitionName:str                                 = ''
    uDefinitionToConfigure:str                          = ''
    uDeviceOrientation:str                              = 'landscape'  # Default Orientation
    uIPAddressV4:str                                    = ''  # Own IP address V4
    uIPAddressV6:str                                    = ''  # Own IP address V6
    uIPAddressV6Full:str                                = ''  # Own IP address V6 incl %
    uIPGateWayV4:str                                    = ''  # App Gateway V4
    uIPGateWayV6:str                                    = ''  # App Gateway V6
    uIPInterfaceName_OS:str                             = ''  # Name of main interface, empty if it can't be detected
    uIPInterfaceName_Phys:str                           = ''  # Name of main interface, empty if it can't be detected
    uIPInterfaceName_Nice:str                           = ''  # Name of main interface, empty if it can't be detected
    uIPSubNetV4:str                                     = ''  # App Subnet V4
    uIPSubNetV6:str                                     = ''  # App Subnet, maybe no sense on V6
    uLanguage:str                                       = 'English'    # Language for the UI, This is not the default value
    uLocalesName:str                                    = ''
    uMACAddressColon:str                                = ''
    uMACAddressDash:str                                 = ''
    uNetworkCheckType:str                               = 'ping'       # The way, how we detect network connectivity (ping/system)
    uPlatform:str                                       = ''           # The used Platform
    uScriptLanguageFallBackTail:str                     = ''
    uScriptLanguageFileTail:str                         = ''
    uSkinName:str                                       = ''
    uStretchMode:str                                    = 'STRETCH'    # Stretchmode: could be "STRETCH" or "CENTER" or "TOPLEFT" or "RESIZE"
    uSupport:str                                        = 'http://www.orca-remote.org/'
    uVersion:str                                        = ''



Globals=cGlobals()







































