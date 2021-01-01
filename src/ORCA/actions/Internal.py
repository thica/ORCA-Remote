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
from xml.etree.ElementTree              import Element

from ORCA.actions.Base                  import cEventActionBase
from ORCA.definition.DefinitionContext  import SetDefinitionContext
from ORCA.download.LoadOnlineResource   import cLoadOnlineResource
from ORCA.utils.FTP                     import cFTP
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.utils.TypeConvert             import ToBool
from ORCA.utils.Path                    import cPath
from ORCA.utils.FileName                import cFileName
from ORCA.Action                        import cAction
from ORCA.download.Repository           import oRepository
from ORCA.actions.ReturnCode            import eReturnCode
from ORCA.utils.CachedFile              import CachedFile
from ORCA.utils.XML                     import Orca_FromString
import ORCA.Globals as Globals

__all__ = ['cEventActionsInternal']



class cEventActionsInternal(cEventActionBase):
    """ Internal Actions for Appstart, etc. Not for User use  """
    def __init__(self, oEventDispatcher):
        super(cEventActionsInternal, self).__init__(oEventDispatcher)
        self.oLoadOnlineResource = None

    def ExecuteActionShowSplashText(self,oAction:cAction) -> eReturnCode:
        """
        showsplashtext:
        Displays a text on the splash screen
        Parameter:
        maintext:    Maintext to show
        subtext:     Subtext to show
        percentage: percentage value of the scrollbar (0-100)
        """

        self.oEventDispatcher.LogAction(uTxt=u'ShowSplashText',oAction=oAction)
        self.oEventDispatcher.bDoNext = False
        uMainText:str    = oAction.dActionPars.get("maintext","")
        uSubText:str     = oAction.dActionPars.get("subtext","")
        uPercentage:str  = oAction.dActionPars.get("percentage","")

        if uMainText:
            Globals.oTheScreen.LogToSplashScreen(uText=uMainText,uPercentage=uPercentage)
        if uSubText:
            Globals.oTheScreen.LogToSplashScreen2(uText=uSubText,uPercentage=uPercentage)
        return eReturnCode.Nothing

    def ExecuteActionLoadDefinitionParameter(self,oAction:cAction) -> eReturnCode:
        """
            loaddefinitionparameter:
            Loads all definition parameter of all definitions into vars
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'LoadDefinitionParameter',oAction=oAction)
        Globals.oDefinitions.LoadParameter()
        return eReturnCode.Nothing

    def ExecuteActionCheckToRotate(self,oAction:cAction) -> eReturnCode:
        """
            checktorotate:
            Checks, if rotation is required. Needs to be executed before any pages are loaded
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'CheckToRotate',oAction=oAction)
        Globals.oTheScreen.CheckToRotate()
        return eReturnCode.Nothing

    def ExecuteActionLoadSkin(self,oAction:cAction) -> eReturnCode:
        """
        loadskin:
            Loads the configured skin
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'LoadSkin',oAction=oAction)
        Globals.oTheScreen.LoadSkinDescription()
        return eReturnCode.Nothing

    def ExecuteActionLoadSounds(self,oAction:cAction) -> eReturnCode:
        """
        loadsounds:
            Loads the configured sounds
            Parameter:
            None
        """
        self.oEventDispatcher.LogAction(uTxt=u'LoadSounds',oAction=oAction)
        Globals.oSound.Init()
        Globals.oSound.LoadSoundsDescription()
        return eReturnCode.Nothing

    def ExecuteActionCreatePages(self,oAction:cAction) -> eReturnCode:
        """
        createpages:
            create the pages, as configured in the settings
            Parameter:
            pagename: can be empty to create all pages, a specific page name or "nextpage"
        """
        self.oEventDispatcher.LogAction(uTxt=u'CreatePages',oAction=oAction)
        Globals.oTheScreen.oScreenPages.CreatePages(uPageName=oAction.dActionPars.get("pagename",""))
        return eReturnCode.Nothing

    def ExecuteActionLoadDefinition(self,oAction:cAction) -> eReturnCode:
        """
        loaddefinition:
            Loads the definition itself
            Parameter:
            None
        """
        self.oEventDispatcher.LogAction(uTxt=u'LoadDefinition',oAction=oAction)
        Globals.oActions.LoadActionsAppStart()
        return eReturnCode.Nothing

    def ExecuteActionGetUsedDefinitions(self,oAction:cAction) -> eReturnCode:
        """
        getuseddefinitions:
            Collects all used definition in the main definition
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'GetUsedDefinitions',oAction=oAction)
        Globals.oDefinitions.GetUsedDefinitions()
        return eReturnCode.Nothing

    def ExecuteActionLoadLanguages(self,oAction:cAction) -> eReturnCode:

        """
        loadlanguages:
            Loads the core languages, which are there even without the online resources or a specific language file
            Parameter:
            languagefilename: if give a specific language file will be loaded, otherwise the core languages are loaded
            definition: the definition name for the definition vars
        """
        self.oEventDispatcher.LogAction(uTxt=u'LoadLanguages',oAction=oAction)
        uLanguageFileName:str  = oAction.dActionPars.get("languagefilename","")
        uDefinitionAlias:str   = oAction.dActionPars.get("definitionalias","")
        uDefinition:str        = oAction.dActionPars.get("definition","")

        if uDefinitionAlias:
            uOrgDefinitionContext:str = Globals.uDefinitionContext
            SetDefinitionContext(uDefinitionName = uDefinitionAlias,uDefinitionPathName=uDefinition)
            Globals.oTheScreen.LoadLanguage(uLanguageFileName = uLanguageFileName)
            SetDefinitionContext(uDefinitionName = uOrgDefinitionContext)
        else:
            Globals.oTheScreen.LoadLanguage(uLanguageFileName=uLanguageFileName)
        return eReturnCode.Nothing

    def ExecuteActionDownLoadDefinition(self,oAction:cAction) -> eReturnCode:

        """
        downloaddefinition:
            Loads a definition from a online repository
            Parameter:
            definitionname: Name of the definition
        """

        self.oEventDispatcher.LogAction(uTxt=u'DownLoadDefinition',oAction=oAction)
        Globals.oApp.DownloadDefinition(uDefinitionName=oAction.dActionPars.get("definitionname",""))
        return eReturnCode.Nothing

    def ExecuteActionRepositoryUpdate(self,oAction:cAction) -> eReturnCode:

        """
        repositoryupdate:
            Updates all local repositories with online versions
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'RepositoryUpdate',oAction=oAction)
        Globals.oApp.RepositoryUpdate()
        return eReturnCode.Nothing

    def ExecuteActionRestartAfterRepositoryUpdate(self,oAction:cAction) -> eReturnCode:
        """
        restartafterdreposityupdate:
            Restarts Orca, after a the repository have been updated
            Parameter:
            None
        """
        self.oEventDispatcher.LogAction(uTxt=u'RestartAfterRepositoryUpdate',oAction=oAction)
        Globals.oApp.RestartAfterRepositoryUpdate()
        return eReturnCode.Nothing

    def ExecuteActionRestartAfterDefinitionDownload(self,oAction:cAction) -> eReturnCode:
        """
        restartafterdefinitiondownload:
            Restarts Orca, after a new definition have been downloaded
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'RestartAfterDefinitionDownload',oAction=oAction)
        Globals.oApp.RestartAfterDefinitionLoad()
        return eReturnCode.Nothing

    def ExecuteActionResumeInterfaces(self,oAction:cAction) -> eReturnCode:

        """
        resumeinterfaces:
            Resumes interfaces after sleep
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'ResumeInterfaces',oAction=oAction)
        Globals.oInterFaces.OnResume()
        return eReturnCode.Nothing

    def ExecuteActionSleepInterfaces(self,oAction:cAction) -> eReturnCode:
        """
        sleepinterfaces:
            Sleeps the Interfaces
            Parameter:
            None
        """
        self.oEventDispatcher.LogAction(uTxt=u'SleepInterfaces',oAction=oAction)
        Globals.oInterFaces.OnPause()
        return eReturnCode.Nothing

    def ExecuteActionSleepScripts(self,oAction:cAction) -> eReturnCode:

        """
        sleepscripts:
            Sleeps the Scripts
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'SleepScripts',oAction=oAction)
        Globals.oScripts.OnPause()
        return eReturnCode.Nothing

    def ExecuteActionResumeScripts(self,oAction:cAction) -> eReturnCode:

        """
        resumescripts:
            Resumes scripts after sleep
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'ResumeScripts',oAction=oAction)
        Globals.oScripts.OnResume()
        return eReturnCode.Nothing

    def ExecuteActionLoadDefinitionLanguages(self,oAction:cAction) -> eReturnCode:

        """
        loaddefinitionlanguages:
            Loads the language of all definitions or from a single definition
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'LoadDefinitionLanguages',oAction=oAction)
        Globals.oTheScreen.LoadLanguages_ForDefinition()
        return eReturnCode.Nothing

    def ExecuteActionLoadDefinitionSettings(self,oAction:cAction) -> eReturnCode:

        """
        loaddefinitionSettings:
            Loads the settings of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's settings should be loaded. If not given, then all definition settings will be loaded
        """
        self.oEventDispatcher.LogAction(uTxt=u'LoadDefinitionSettings',oAction=oAction)
        uDefinitionName:str = oAction.dActionPars.get("definitionname","")

        Globals.oTheScreen.LoadSettings_ForDefinition(uDefinitionName=uDefinitionName)
        return eReturnCode.Nothing

    def ExecuteActionLoadDefinitionFonts(self,oAction:cAction) -> eReturnCode:

        """
        loaddefinitionfonts:
            Loads the fonts of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's fonts should be loaded. If not given, then all definition fonts will be loaded, if 'ORCA', then the Orca application fonts will be loaded
        """
        self.oEventDispatcher.LogAction(uTxt=u'LoadDefinitionFonts',oAction=oAction)
        uDefinitionName:str  = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.LoadFonts_ForDefinition(uDefinitionName=uDefinitionName)
        return eReturnCode.Nothing

    def ExecuteActionLoadActionFile(self,oAction:cAction) -> eReturnCode:
        """
        loadactionfile:
            Load as specific action file
            Parameter:
            actionfilename: Full path to the action file
        """

        self.oEventDispatcher.LogAction(uTxt=u'LoadActionFile',oAction=oAction)
        oFnAction:cFileName=cFileName().ImportFullPath(uFnFullName=oAction.dActionPars.get("actionfilename",""))
        if oFnAction.Exists():
            uET_Data = CachedFile(oFileName=oFnAction)
            oET_Root:Element = Orca_FromString(uET_Data=uET_Data, oDef=None, uFileName=str(oFnAction))
            Globals.oActions.LoadActionsSub(oET_Root=oET_Root,uSegmentTag=u'actions',uListTag=u'action',dTargetDic=Globals.oActions.dActionsCommands,uFileName=oFnAction.string)


        return eReturnCode.Nothing

    def ExecuteActionLoadDefinitionActions(self,oAction:cAction) -> eReturnCode:
        """
        loaddefinitionactions:
            Loads the actions of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's actions should be loaded. If not given, then all definition actions will be loaded
        """

        self.oEventDispatcher.LogAction(uTxt=u'LoadDefinitionActions',oAction=oAction)
        uDefinitionName:str = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.LoadActions_ForDefinition(uDefinitionName=uDefinitionName)
        return eReturnCode.Nothing

    def ExecuteActionLoadDefinitionGestures(self,oAction:cAction) -> eReturnCode:
        """
        loaddefinitiongestures:
            Loads the gestures of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's gestures should be loaded. If not given, then all definition gestures will be loaded
        """
        self.oEventDispatcher.LogAction(uTxt=u'LoadDefinitionGestures',oAction=oAction)
        uDefinitionName:str = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.LoadGestures_ForDefinition(uDefinitionName=uDefinitionName)
        return eReturnCode.Nothing

    def ExecuteActionInitInterfaceSettings(self,oAction:cAction) -> eReturnCode:
        """
        initinterfacesettings:
            Init the interface settings of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's interface settings should be initialized. If not given, then all definition interface settings will be initialized
        """
        self.oEventDispatcher.LogAction(uTxt=u'InitInterfaceSettings',oAction=oAction)
        uDefinitionName:str = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.InitInterFaceSettings_ForDefinition(uDefinitionName=uDefinitionName)
        return eReturnCode.Nothing

    def ExecuteActionRegisterFonts(self,oAction:cAction) -> eReturnCode:
        """
        registerfonts:
            Register all used fonts
            Parameter:
            fontname: name of font to register. If not given, then all fonts will be registered
        """

        self.oEventDispatcher.LogAction(uTxt=u'RegisterFonts',oAction=oAction)
        uFontName:str = oAction.dActionPars.get("fontname","")
        Globals.oTheScreen.RegisterFonts(uFontName=uFontName)
        return eReturnCode.Nothing

    def ExecuteActionRegisterInterfaces(self,oAction:cAction) -> eReturnCode:
        """
        registerinterfaces:
            Register all used interfaces
            Parameter:
            interfacename: name of interface to register. If not given, then all interfaces will be registered
        """

        self.oEventDispatcher.LogAction(uTxt=u'RegisterInterfaces',oAction=oAction)
        uInterfaceName:str = oAction.dActionPars.get("interfacename","")
        self.oEventDispatcher.LogAction(uTxt=u'RegisterInterfaces',oAction=oAction)
        Globals.oTheScreen.RegisterInterFaces(uInterFaceName=uInterfaceName)
        return eReturnCode.Nothing

    def ExecuteActionParseDefinitionXML(self,oAction:cAction) -> eReturnCode:
        """
        parsedefinitionxml:
            Parses a definition xml file
            Parameter:
            definitionname: name of definition, who's xml file should be loaded. If not given, then all definition xml files will be loaded
        """

        self.oEventDispatcher.LogAction(uTxt=u'ParseDefinitionXML',oAction=oAction)
        uDefinitionName:str = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.ParseDefinitionXmlFile(uDefinitionName=uDefinitionName)
        return eReturnCode.Nothing

    def ExecuteActionLoadRepositoryContent(self,oAction:cAction) -> eReturnCode:
        """
        loadrepositorycontent:
            Loads the content of a repository
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'LoadRepositoryContent',oAction=oAction)
        Globals.oDownLoadSettings.LoadRepositoryDirectory(bDoNotExecute=False)
        return eReturnCode.Nothing

    def ExecuteActionLoadResource(self,oAction:cAction) -> eReturnCode:
        """
        loadresource:
            Loads a resource from an online repository
            Parameter:
            resourcereference: Reference to load
        """

        self.oEventDispatcher.LogAction(uTxt=u'LoadResource',oAction=oAction)
        uResourceReference:str = oAction.dActionPars.get("resourcereference","")
        self.oLoadOnlineResource=cLoadOnlineResource(oRepository=oRepository)
        self.oLoadOnlineResource.LoadSingleFile(uRef=uResourceReference,oProgressBar=self.oEventDispatcher.aProgressBars[-1])
        return eReturnCode.Nothing

    def ExecuteActionExecuteFTPCommand(self,oAction:cAction) -> eReturnCode:
        """
        executeftpcommand:
            Executes various FTP commands (connect, disconnect, uploadfile)
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(uTxt=u'ExecuteFTPCommand',oAction=oAction)

        bRet:bool               = False
        uCommand:str            = ReplaceVars(oAction.dActionPars.get("command",  ""))
        uHost:str               = ReplaceVars(oAction.dActionPars.get("host",     ""))
        uUsername:str           = ReplaceVars(oAction.dActionPars.get("user",     ""))
        uPassword:str           = ReplaceVars(oAction.dActionPars.get("password", ""))
        uSSL:str                = ReplaceVars(oAction.dActionPars.get("ssl",      ""))

        oLocalFile:cFileName    = cFileName('').ImportFullPath(uFnFullName=ReplaceVars(oAction.dActionPars.get("localfile",       "")))
        oLocalBaseFolder:cPath  = cPath(ReplaceVars(oAction.dActionPars.get("localbasefolder", "")))
        oRemoteBaseFolder:cPath = cPath(ReplaceVars(oAction.dActionPars.get("remotebasefolder","")))

        if Globals.oFTP is None:
            Globals.oFTP = cFTP(ToBool(uSSL))

        if uCommand==u'connect':
            bRet = Globals.oFTP.Connect(uServer=uHost)
            if bRet:
                bRet=Globals.oFTP.Login(uUsername=uUsername, uPassword=uPassword )
        elif uCommand==u'disconnect':
            bRet=Globals.oFTP.DisConnect()
        elif uCommand==u'uploadfile':
            bRet = Globals.oFTP.UploadLocalFile(oFile=oLocalFile, oBaseLocalDir=oLocalBaseFolder, oBaseRemoteDir=oRemoteBaseFolder)
        elif uCommand==u'downloadfile':
            bRet = Globals.oFTP.DownloadRemoteFile(oFnFile=oLocalFile, oPathLocal=oLocalBaseFolder, oPathRemote=oRemoteBaseFolder)
        if bRet:
            return eReturnCode.Success
        else:
            return eReturnCode.Error

    def ExecuteActionCheckPermissions(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-CheckPermissions
        WikiDoc:TOCTitle:checkpermissions
        = checkpermissions =
        Checks, if ORCA has sufficient write access. This will be called on android
        This action will not modify the error code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        |-
        |checkpermissions
        |}</div>
        WikiDoc:End
        """
        self.oEventDispatcher.LogAction(uTxt=u'CheckForPermissions',oAction=oAction)
        Globals.oCheckPermissions.Wait()
        return eReturnCode.Nothing

    def ExecuteActionCheckOnSleep(self,oAction:cAction) -> eReturnCode:
        """
        CheckOnSleep
            Verifies, if we are still on sleep (so Android/Kivy missed to send the resume command)
            Parameter:
            oAction: Unused
        """

        if Globals.bOnSleep:
            self.oEventDispatcher.LogAction(uTxt=u'CheckOnSleep, resume now', oAction=oAction)
            Globals.oApp.on_resume()
        return eReturnCode.Nothing

    def ExecuteActionResumeOnSleep(self,oAction:cAction) -> eReturnCode:
        """
        ResumeFromSleep
            Resumes from sleep, if manual triggered
            Parameter:
            oAction: Unused
        """

        if Globals.bOnSleep:
            self.oEventDispatcher.LogAction(uTxt=u'Resume from Sleep, resume now', oAction=oAction)
            Globals.oApp.on_resume()
        return eReturnCode.Nothing
