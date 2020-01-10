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

aDefinitionList             = []
aLanguageList               = []
aLogoPackFolderNames        = []
aRepNames                   = []
aRepositories               = []     # Online Repositories
aSkinList                   = []     # List of all available skins (Just their names)
aTVLogoList                 = []
bClockWithSeconds           = False  # Flag, if we want to have the clock with seconds
bConfigCheckForNetwork      = True   # Flag, if we should check for network connectivity on application start / resume
bHasPermissions             = False  # Flag, if ORCA has sufficient permissions
bIgnoreAtlas                = False  # Flag, if we would ignore the Kivy Atlas function to cache Images
bInit                       = False  # Flag, if app has been initialized to prevent double initialisations
bInitPagesAtStart           = False  # Flag, if we woulkd initialize all pages at startup
bLongDate                   = False  # Flag, if we would use long date format
bLongDay                    = False  # Flag, if we would use long day format
bLongMonth                  = False  # Flag, if we would use long month format
bOnSleep                    = False  # Flag to be used, if the system is on  (system) sleep, Changes the scheduler behaviour
bProtected                  = False  # Flag, if we do want prevent repository updates and initial setup download
bShowBorders                = False  # Flag, if we should show borders
bVibrate                    = True   # Flag, if we would should vibrate in buttton press
bWaitForRotation            = False  # Flag, if Rotation has been detected by kivy
dDefinitionPathes           = {}     # Dict of Array of definition pathes
dIcons                      = {}     # Dict of all Icons
dInstalledReps              = {}     # Installed packages
fContRepeatDelay            = 0.2    # Gap time between repeating the button action on long continous button press
fDelayedPageInitInterval    = 10.0   # Gap time betweeen creation of pages if we have a deleyed page creation
fDoubleTapTime              = 0.250  # DoubleTabTime from Config
fLongPressTime              = 1.0    # Time to get a button press as a long press
fScreenSize                 = 0.0    # Display Size in inch eg 5 or 7, or 10
fStartRepeatDelay           = 0.5    # Time on button press before we start repeating the action
iAppHeight                  = 0      # Application Height in Pixel
iAppWidth                   = 0
iCntRepositories            = 5      # Number of Repositories, which can be configured
iLastInstalledVersion       = 0
iVersion                    = 0

oActions                    = None
oApp                        = None
oDefinitionConfigParser     = None   # The configparser object
oDefinitionPathes           = None   # The current DefinitionPathes
oDefinitions                = None   # Object which holds all loaded definitions
oDownLoadSettings           = None   # Object, for managing the settings dialog for download repositories
oEvents                     = None   # Object for Events / Queues
oFTP                        = None   # FTP Object for the repository manager
oInterFaces                 = None   # Object which holds all Interfaces
oLanguage                   = None
oModuleLoader               = None   # Object to hold dynamic loaded python modules (scripts, interfaces,...)
oOrcaConfigParser           = None
oParameter                  = None
oRotation                   = None
oScripts                    = None   # Object which holds all scripts
oSound                      = None   # Object to play standard sound
oTheScreen                  = None   # The Screen Object which holds all pages an widgets
oWaitForConnectivity        = None   # Object for checking, if we have network access
oCheckPermissions           = None   # Object for checking, if we have permissions
oWinOrcaSettings            = None   # Object for the settings page
uAuthor                     = u'Carsten Thielepape'
uBranch                     = u''
uConfigCheckNetWorkAddress  = u'auto'
uDefinitionContext          = u''   # CurrentDefinitionContext
uDefinitionName             = u''
oPathDefinitionRoot         = None
uDefinitionToConfigure      = u''
uDeviceOrientation          = u'landscape'  # Default Orientation
oFnElementIncludeWrapper    = None
oFnAction                   = None
oFnActionEarlyAppStart      = None
oFnActionFreshInstall       = None
oFnAtlasSkin                = None
oFnCredits                  = None
oFnGestureLog               = None
oFnGestures                 = None
oFnInterfaceLanguage        = None
oFnInterfaceLanguageFallBack= None
oFnLangInfo                 = None
oFnLicense                  = None
oFnLog                      = None
oFnSkinXml                  = None
oFnSoundsXml                = None
uIPAddressV4                = u''  # Own IP address
uIPGateWayV4                = u''  # App Gateway
uIPSubNetV4                 = u''  # App Subnet
uIPAddressV6                = u''  # Own IP address
uIPGateWayV6                = u''  # App Gateway.
uIPSubNetV6                 = u''  # App Subnet
uLanguage                   = u'English'    # Language for the UI, This is not the default value
uLocalesName                = u''
uMACAddressColon            = u''
uMACAddressDash             = u''
uNetworkCheckType           = u'ping' # The way, how we detect network connectivity (ping/system)
oNotifications              = None # Notification Handler
oPathAction                 = None
oPathAppReal                = None
oPathCodesets               = None
oPathCookie                 = None
oPathUserDownload           = None
oPathGestures               = None
oPathGlobalSettingsScripts  = None
oPathGlobalSettingsInterfaces  = None
oPathInterface              = None
oPathLanguageRoot           = None
oPathResources              = None
oPathRoot                   = None    # The "root path" where to store / find the Orca data files. This can be replaced by custom settings, so uRootPath is the one, which is then really used
oPathScripts                = None
oPathSharedDocuments        = None
oPathSkin                   = None
oPathSounds                 = None
oPathSoundsRoot             = None
oPathStandardElements       = None
oPathStandardPages          = None
oPathTmp                    = None
oPathTVLogos                = None
oPathWizardTemplates        = None
uPlatform                   = u''           # The used Platform
uScriptLanguageFallBackTail = u''
uScriptLanguageFileTail     = u''
uSkinName                   = u''
uStretchMode                = u"STRETCH"  # Stretchmode: could be "STRETCH" or "CENTER" or "TOPLEFT" or "RESIZE"
uSupport                    = u'http://www.orca-remote.org/'
uVersion                    = u''











































