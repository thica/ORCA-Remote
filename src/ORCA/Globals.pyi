from kivy.config import Config

from ORCA.App                              import ORCA_App
from ORCA.Actions                          import cActions
from ORCA.definition.DefinitionPathes      import cDefinitionPathes
from ORCA.definition.Definitions           import cDefinitions
from ORCA.Downloads                        import cDownLoad_Settings
from ORCA.Events                           import cEvents
from ORCA.International                    import cLanguage
from ORCA.Screen_Init                      import cTheScreenWithInit
from ORCA.scripts.Scripts                  import cScripts
from ORCA.Sound                            import cSound
from ORCA.utils.Network                    import cWaitForConnectivity
from ORCA.utils.Rotation                   import cRotation
from ORCA.utils.FTP                        import cFTP
from ORCA.utils.FileName                   import cFileName
from ORCA.utils.Path                       import cPath
from ORCA.interfaces.Interfaces            import cInterFaces
from ORCA.Parameter                        import cParameter
from ORCA.Notifications                    import cNotifications

aDefinitionList:            list
aLanguageList:              list
aRepNames:                  list
aRepositories:              list
aScriptList:                list
aSkinList:                  list
bClockWithSeconds:          bool
bConfigCheckForNetwork:     bool
bIgnoreAtlas:               bool
bInit:                      bool
bInitPagesAtStart:          bool
bLongDate:                  bool
bLongDay:                   bool
bLongMonth:                 bool
bOnSleep:                   bool
bProtected:                 bool
bVibrate:                   bool
bWaitForRotation:           bool
dDefinitionPathes:          dict
dIcons:                     dict
dInstalledReps:             dict
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
oActions:                    cActions
oApp:                        ORCA_App
oDefinitionConfigParser:     Config
oDefinitionPathes:           cDefinitionPathes
oDefinitions:                cDefinitions
oDownLoadSettings:           cDownLoad_Settings
oFnElementIncludeWrapper:    cFileName
oEvents:                     cEvents
oFTP:                        cFTP
oFnAction:                   cFileName
oFnActionEarlyAppStart:      cFileName
oFnActionFreshInstall:       cFileName
oFnAtlasSkin:                cFileName
oFnCredits:                  cFileName
oFnGestureLog:               cFileName
oFnGestures:                 cFileName
oFnGlobalFontDefinition:     cFileName
oFnInterfaceLanguage:        cFileName
oFnInterfaceLanguageFallBack:cFileName
oFnLangInfo:                 cFileName
oFnLicense:                  cFileName
oFnLog:                      cFileName
oFnScriptLanguageFallBack:   cFileName
oFnScriptLanguageFile:       cFileName
oFnSkinXml:                  cFileName
oFnSoundsXml:                cFileName
oInterFaces:                 cInterFaces
oLanguage:                   cLanguage
oNotifications:              cNotifications
oOrcaConfigParser:           Config
oParameter:                  cParameter
oPathAction:                 cPath
oPathApp:                    cPath
oPathAppReal:                cPath
oPathCodesets:               cPath
oPathCookie:                 cPath
oPathDefinitionRoot:         cPath
oPathFonts:                  cPath
oPathGestures:               cPath
oPathInterface:              cPath
oPathLanguageRoot:           cPath
oPathResources:              cPath
oPathRoot:                   cPath
oPathScripts:                cPath
oPathSharedDocuments:        cPath
oPathSkin:                   cPath
oPathSounds:                 cPath
oPathSoundsRoot:             cPath
oPathStandardElements:       cPath
oPathStandardPages:          cPath
oPathTmp:                    cPath
oPathUserDownload:           cPath
oRotation:                   cRotation
oScripts:                    cScripts
oSound:                      cSound
oTheScreen:                  cTheScreenWithInit
oWaitForConnectivity:        cWaitForConnectivity
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
