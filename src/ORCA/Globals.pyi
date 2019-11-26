from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

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

aDefinitionList:            List[str]
aLanguageList:              List[str]
aRepNames:                  List[Tuple]
aRepositories:              List[str]
aLogoPackFolderNames:       List[str]
# aScriptList:                list
aSkinList:                  List[str]
aTVLogoList:                List[str]
bClockWithSeconds:          bool
bConfigCheckForNetwork:     bool
bHasPermissions:            bool
bIgnoreAtlas:               bool
bInit:                      bool
bInitPagesAtStart:          bool
bLongDate:                  bool
bLongDay:                   bool
bLongMonth:                 bool
bOnSleep:                   bool
bProtected:                 bool
bShowBorders:               bool
bVibrate:                   bool
bWaitForRotation:           bool
dDefinitionPathes:          Dict[str,cDefinitionPathes]
dIcons:                     Dict[str,Dict]
dInstalledReps:             Dict[str,cInstalledReps]
fContRepeatDelay:           float
fDelayedPageInitInterval:   float
fDoubleTapTime:             float
fLongPressTime:             float
fScreenSize:                float
fStartRepeatDelay:          float
iAppHeight:                 int
iAppWidth:                  int
iCntRepositories:           int
iLastInstalledVersion:      int
iVersion:                   int
oActions:                    Union[cActions,None]
oApp:                        Union[ORCA_App,None]
oDefinitionConfigParser:     Config
oDefinitionPathes:           Union[cDefinitionPathes,None]
oDefinitions:                Union[cDefinitions,None]
oDownLoadSettings:           Union[cDownLoad_Settings,None]
oFnElementIncludeWrapper:    Union[cFileName,None]
oEvents:                     Union[cEvents,None]
oFTP:                        Union[cFTP,None]
oFnAction:                   Union[cFileName,None]
oFnActionEarlyAppStart:      Union[cFileName,None]
oFnActionFreshInstall:       Union[cFileName,None]
oFnAtlasSkin:                Union[cFileName,None]
oFnCredits:                  Union[cFileName,None]
oFnGestureLog:               Union[cFileName,None]
oFnGestures:                 Union[cFileName,None]
oFnGlobalFontDefinition:     Union[cFileName,None]
oFnInterfaceLanguage:        Union[cFileName,None]
oFnInterfaceLanguageFallBack:Union[cFileName,None]
oFnLangInfo:                 Union[cFileName,None]
oFnLicense:                  Union[cFileName,None]
oFnLog:                      Union[cFileName,None]
oFnScriptLanguageFallBack:   Union[cFileName,None]
oFnScriptLanguageFile:       Union[cFileName,None]
oFnSkinXml:                  Union[cFileName,None]
oFnSoundsXml:                Union[cFileName,None]
oInterFaces:                 Union[cInterFaces,None]
oLanguage:                   Union[cLanguage,None]
oModuleLoader:               Union[cModuleLoader,None]
oNotifications:              Union[cNotifications,None]
oOrcaConfigParser:           Config
oParameter:                  Union[cParameter,None]
oPathAction:                 Union[cPath,None]
oPathApp:                    Union[cPath,None]
oPathAppReal:                Union[cPath,None]
oPathCodesets:               Union[cPath,None]
oPathCookie:                 Union[cPath,None]
oPathDefinitionRoot:         Union[cPath,None]
oPathFonts:                  Union[cPath,None]
oPathGestures:               Union[cPath,None]
oPathGlobalSettingsScripts:  Union[cPath,None]
oPathGlobalSettingsInterfaces: Union[cPath,None]
oPathInterface:              Union[cPath,None]
oPathLanguageRoot:           Union[cPath,None]
oPathResources:              Union[cPath,None]
oPathRoot:                   Union[cPath,None]
oPathScripts:                Union[cPath,None]
oPathSharedDocuments:        Union[cPath,None]
oPathSkin:                   Union[cPath,None]
oPathSounds:                 Union[cPath,None]
oPathSoundsRoot:             Union[cPath,None]
oPathStandardElements:       Union[cPath,None]
oPathStandardPages:          Union[cPath,None]
oPathTmp:                    Union[cPath,None]
oPathTVLogos:                Union[cPath,None]
oPathUserDownload:           Union[cPath,None]
oPathWizardTemplates:        Union[cPath,None]
oRotation:                   Union[cRotation,None]
oScripts:                    Union[cScripts,None]
oSound:                      Union[cSound,None]
oTheScreen:                  Union[cTheScreenWithInit,None]
oWaitForConnectivity:        Union[cWaitForConnectivity,None]
oCheckPermissions:           Union[cCheckPermissions,None]
oWinOrcaSettings:            Config
uAuthor:                     str
uBranch:                     str
uConfigCheckNetWorkAddress:  str
uDefinitionContext:          str
uDefinitionName:             str
uDefinitionToConfigure:      str
uDeviceOrientation:          str
uIPAddressV4:                str
uIPGateWayAssumedV4:         str
uIPSubNetAssumedV4:          str
uIPAddressV6:                str
uIPGateWayV6:                str

uLanguage:                   str
uLocalesName:                str
uMACAddressColon:            str
uMACAddressDash:             str
uNetworkCheckType:           str
uPlatform:                   str
uSkinName:                   str
uStretchMode:                str
uSupport:                    str
uVersion:                    str
uScriptLanguageFallBackTail: str
uScriptLanguageFileTail:     str
