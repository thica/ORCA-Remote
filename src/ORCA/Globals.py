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


from typing import Dict
from typing import List
from typing import Tuple
from typing import Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kivy.config import Config
    from ORCA.App                              import ORCA_App
    from ORCA.Actions                          import cActions
    from ORCA.definition.DefinitionPathes      import cDefinitionPathes
    from ORCA.definition.Definitions           import cDefinitions
    from ORCA.download.DownLoadSettings        import cDownLoad_Settings
    from ORCA.Events                           import cEvents
    from ORCA.International                    import cLanguage
    from ORCA.Screen_Init                      import cTheScreenWithInit
    from ORCA.scripts.Scripts                  import cScripts
    from ORCA.Sound                            import cSound
    from ORCA.utils.Network                    import cWaitForConnectivity
    from ORCA.utils.CheckPermissions           import cCheckPermissions
    from ORCA.utils.Rotation                   import cRotation
    from ORCA.utils.FTP                        import cFTP
    from ORCA.utils.FileName                   import cFileName
    from ORCA.utils.Path                       import cPath
    from ORCA.interfaces.Interfaces            import cInterFaces
    from ORCA.Parameter                        import cParameter
    from ORCA.Notifications                    import cNotifications
    from ORCA.utils.ModuleLoader               import cModuleLoader
    from ORCA.download.InstalledReps           import cInstalledReps
else:
    from typing import TypeVar
    Config                  = TypeVar("Config")
    ORCA_App                = TypeVar("ORCA_App")
    cActions                = TypeVar("cActions")
    cCheckPermissions       = TypeVar("cCheckPermissions")
    cDefinitionPathes       = TypeVar("cDefinitionPathes")
    cDefinitions            = TypeVar("cDefinitions")
    cDownLoad_Settings      = TypeVar("cDownLoad_Settings")
    cEvents                 = TypeVar("cEvents")
    cFTP                    = TypeVar("cFTP")
    cFileName               = TypeVar("cFileName")
    cInstalledReps          = TypeVar("cInstalledReps")
    cInterFaces             = TypeVar("cInterFaces")
    cLanguage               = TypeVar("cLanguage")
    cModuleLoader           = TypeVar("cModuleLoader")
    cNotifications          = TypeVar("cNotifications")
    cParameter              = TypeVar("cParameter")
    cPath                   = TypeVar("cPath")
    cRotation               = TypeVar("cRotation")
    cScripts                = TypeVar("cScripts")
    cSound                  = TypeVar("cSound")
    cTheScreenWithInit      = TypeVar("cTheScreenWithInit")
    cWaitForConnectivity    = TypeVar("cWaitForConnectivity")


aDefinitionList:List[str]                           = []
aLanguageList:List[str]                             = []
aLogoPackFolderNames:List[str]                      = []
aRepNames:List[Tuple[str,str]]                      = []
aRepositories:List[str]                             = []     # Online Repositories
aSkinList:List[str]                                 = []     # List of all available skins (Just their names)
aTransitionDirections:List[str]                     = [u'left',u'right',u'up',u'down']
aTransitionTypes:List[str]                          = [u'no',u'fade',u'slide',u'wipe',u'swap',u'fallout',u'risein']
aTVLogoList:List[str]                               = []
bClockWithSeconds:bool                              = False  # Flag, if we want to have the clock with seconds
bConfigCheckForNetwork:bool                         = True   # Flag, if we should check for network connectivity on application start / resume
bHasPermissions:bool                                = False  # Flag, if ORCA has sufficient permissions
bIgnoreAtlas:bool                                   = False  # Flag, if we would ignore the Kivy Atlas function to cache Images
bInit:bool                                          = False  # Flag, if app has been initialized to prevent double initialisations
bInitPagesAtStart:bool                              = False  # Flag, if we would initialize all pages at startup
bLongDate:bool                                      = False  # Flag, if we would use long date format
bLongDay:bool                                       = False  # Flag, if we would use long day format
bLongMonth:bool                                     = False  # Flag, if we would use long month format
bOnSleep:bool                                       = False  # Flag to be used, if the system is on  (system) sleep, Changes the scheduler behaviour
bProtected:bool                                     = False  # Flag, if we do want prevent repository updates and initial setup download
bShowBorders:bool                                   = False  # Flag, if we should show borders
bVibrate:bool                                       = True   # Flag, if we would should vibrate in button press
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
oRotation:Optional[cRotation]                                 = None
oScripts:Optional[cScripts]                                   = None   # Object which holds all scripts
oSound:Optional[cSound]                                       = None   # Object to play standard sound
oTheScreen:Optional[cTheScreenWithInit]                       = None   # The Screen Object which holds all pages an widgets
oWaitForConnectivity:Optional[cWaitForConnectivity]           = None   # Object for checking, if we have network access
oWinOrcaSettings:Optional[Config]                             = None   # Object for the settings page
uAuthor:str                                         = u'Carsten Thielepape'
uBranch:str                                         = u''
uConfigCheckNetWorkAddress:str                      = u'auto'
uDefaultTransitionDirection                         = u'left'
uDefaultTransitionType                              = u'fade'
uDefinitionContext:str                              = u''   # CurrentDefinitionContext
uDefinitionName:str                                 = u''
uDefinitionToConfigure:str                          = u''
uDeviceOrientation:str                              = u'landscape'  # Default Orientation
uIPAddressV4:str                                    = u''  # Own IP address
uIPAddressV6:str                                    = u''  # Own IP address
uIPGateWayV4:str                                    = u''  # App Gateway
uIPGateWayV6:str                                    = u''  # App Gateway.
uIPSubNetV4:str                                     = u''  # App Subnet
uIPSubNetV6:str                                     = u''  # App Subnet
uLanguage:str                                       = u'English'    # Language for the UI, This is not the default value
uLocalesName:str                                    = u''
uMACAddressColon:str                                = u''
uMACAddressDash:str                                 = u''
uNetworkCheckType:str                               = u'ping'       # The way, how we detect network connectivity (ping/system)
uPlatform:str                                       = u''           # The used Platform
uScriptLanguageFallBackTail:str                     = u''
uScriptLanguageFileTail:str                         = u''
uSkinName:str                                       = u''
uStretchMode:str                                    = u"STRETCH"    # Stretchmode: could be "STRETCH" or "CENTER" or "TOPLEFT" or "RESIZE"
uSupport:str                                        = u'http://www.orca-remote.org/'
uVersion:str                                        = u''











































