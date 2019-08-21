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

from ORCA.actions.Base                  import cEventActionBase
from ORCA.definition.DefinitionContext  import SetDefinitionContext
from ORCA.Downloads                     import cLoadOnlineResource
from ORCA.utils.FTP                     import cFTP
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.utils.TypeConvert             import ToBool
from ORCA.utils.Path                    import cPath
from ORCA.utils.FileName                import cFileName

import ORCA.Globals as Globals


__all__ = ['cEventActionsInternal']



class cEventActionsInternal(cEventActionBase):
    """ Internal Actions for Appstart, etc. Not for User use  """
    def __init__(self, oEventDispatcher):
        super(cEventActionsInternal, self).__init__(oEventDispatcher)
        self.oLoadOnlineResource = None

    def ExecuteActionShowSplashText(self,oAction):
        """
        showsplashtext:
        Displays a text on the splash screen
        Parameter:
        maintext:    Maintext to show
        subtext:     Subtext to show
        percentage: percentage value of the scrollbar (0-100)
        """

        self.oEventDispatcher.LogAction(u'ShowSplashText',oAction)
        self.oEventDispatcher.bDoNext = False
        uMainText    = oAction.dActionPars.get("maintext","")
        uSubText     = oAction.dActionPars.get("subtext","")
        uPercentage  = oAction.dActionPars.get("percentage","")

        if uMainText:
            Globals.oTheScreen.LogToSplashScreen(uMainText,uPercentage)
        if uSubText:
            Globals.oTheScreen.LogToSplashScreen2(uSubText,uPercentage)
        return -2

    def ExecuteActionLoadDefinitionParameter(self,oAction):
        """
            loaddefinitionparameter:
            Loads all definition parameter of all definitions into vars
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'LoadDefinitionParameter',oAction)
        Globals.oDefinitions.LoadParameter()
        return -2

    def ExecuteActionCheckToRotate(self,oAction):
        """
            checktorotate:
            Checks, if rotation is required. Needs to be excecuted before any pages are loaded
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'CheckToRotate',oAction)
        Globals.oTheScreen.CheckToRotate()
        return -2

    def ExecuteActionLoadSkin(self,oAction):
        """
        loadskin:
            Loads the configured skin
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'LoadSkin',oAction)
        Globals.oTheScreen.LoadSkinDescription()
        return -2

    def ExecuteActionLoadSounds(self,oAction):
        """
        loadsounds:
            Loads the configured sounds
            Parameter:
            None
        """
        self.oEventDispatcher.LogAction(u'LoadSounds',oAction)
        Globals.oSound.Init()
        Globals.oSound.LoadSoundsDescription()
        return -2

    def ExecuteActionCreatePages(self,oAction):
        """
        createpages:
            create the pages, as configured in the settings
            Parameter:
            pagename: can be empty to create all pages, a specific page name or "nextpage"
        """
        self.oEventDispatcher.LogAction(u'CreatePages',oAction)
        Globals.oTheScreen.oScreenPages.CreatePages(oAction.dActionPars.get("pagename",""))
        return -2

    def ExecuteActionLoadDefinition(self,oAction):
        """
        loaddefinition:
            Loads the definition itself
            Parameter:
            None
        """
        self.oEventDispatcher.LogAction(u'LoadDefinition',oAction)
        Globals.oActions.LoadActionsAppStart()
        return -2

    def ExecuteActionGetUsedDefinitions(self,oAction):
        """
        getuseddefinitions:
            Collects all used definition in the main definition
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'GetUsedDefinitions',oAction)
        Globals.oDefinitions.GetUsedDefinitions()
        return -2

    def ExecuteActionLoadLanguages(self,oAction):

        """
        loadlanguages:
            Loads the core languages, which are there even without the online resources or a specific language file
            Parameter:
            languagefilename: if give a specific language file will be loaded, otherwise the core languares are loaded
            context: a context for the language
            definition: the definition name for the definition vars
        """
        self.oEventDispatcher.LogAction(u'LoadLanguages',oAction)
        uLanguageFileName  = oAction.dActionPars.get("languagefilename","")
        uContext           = oAction.dActionPars.get("context","")
        uDefinitionAlias   = oAction.dActionPars.get("definitionalias","")
        uDefinition        = oAction.dActionPars.get("definition","")

        if uDefinitionAlias:
            uOrgDefinitionContext=Globals.uDefinitionContext
            SetDefinitionContext(uDefinitionAlias,uDefinition)
            Globals.oTheScreen.LoadLanguage(uLanguageFileName=uLanguageFileName,uContext=uContext)
            SetDefinitionContext(uOrgDefinitionContext)
        else:
            Globals.oTheScreen.LoadLanguage(uLanguageFileName=uLanguageFileName,uContext=uContext)

        return -2

    def ExecuteActionDownLoadDefinition(self,oAction):

        """
        downloaddefinition:
            Loads a definition from a online repository
            Parameter:
            definitionname: Name of the definition
        """

        self.oEventDispatcher.LogAction(u'DownLoadDefinition',oAction)
        Globals.oApp.DownloadDefinition(uDefinitionName=oAction.dActionPars.get("definitionname",""))
        return -2

    def ExecuteActionRepositoryUpdate(self,oAction):

        """
        repositoryupdate:
            Updates all local repositories with online versions
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'RepositoryUpdate',oAction)
        Globals.oApp.RepositoryUpdate()
        return -2

    def ExecuteActionRestartAfterRepositoryUpdate(self,oAction):
        """
        restartafterdreposityupdate:
            Restarts Orca, after a the repository have been updated
            Parameter:
            None
        """
        self.oEventDispatcher.LogAction(u'RestartAfterRepositoryUpdate',oAction)
        Globals.oApp.RestartAfterRepositoryUpdate()
        return -2

    def ExecuteActionRestartAfterDefinitionDownload(self,oAction):
        """
        restartafterdefinitiondownload:
            Restarts Orca, after a new definition have been downloaded
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'RestartAfterDefinitionDownload',oAction)
        Globals.oApp.RestartAfterDefinitionLoad()
        return -2

    def ExecuteActionResumeInterfaces(self,oAction):

        """
        resumeinterfaces:
            Resumes interfaces after sleep
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'ResumeInterfaces',oAction)
        Globals.oInterFaces.OnResume()
        return -2


    def ExecuteActionSleepInterfaces(self,oAction):
        """
        sleepinterfaces:
            Sleeps the Interfaces
            Parameter:
            None
        """
        self.oEventDispatcher.LogAction(u'SleepInterfaces',oAction)
        Globals.oInterFaces.OnPause()
        return -2

    def ExecuteActionSleepScripts(self,oAction):

        """
        sleepscripts:
            Sleeps the Scripts
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'SleepScripts',oAction)
        Globals.oScripts.OnPause()
        return -2

    def ExecuteActionResumeScripts(self,oAction):

        """
        resumescripts:
            Resumes scripts after sleep
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'ResumeScripts',oAction)
        Globals.oScripts.OnResume()
        return -2
    def ExecuteActionLoadDefinitionLanguages(self,oAction):

        """
        loaddefinitionlanguages:
            Loads the language of all definitions or from a single definition
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'LoadDefinitionLanguages',oAction)
        Globals.oTheScreen.LoadLanguages_ForDefinition()
        return -2

    def ExecuteActionLoadDefinitionSettings(self,oAction):

        """
        loaddefinitionSettings:
            Loads the settings of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's settings should be loaded. If not given, then all definition settings will be loaded
        """
        self.oEventDispatcher.LogAction(u'LoadDefinitionSettings',oAction)
        uDefinitionName  = oAction.dActionPars.get("definitionname","")

        Globals.oTheScreen.LoadSettings_ForDefinition(uDefinitionName)
        return -2

    def ExecuteActionLoadDefinitionFonts(self,oAction):

        """
        loaddefinitionfonts:
            Loads the fonts of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's fonts should be loaded. If not given, then all definition fonts will be loaded, if 'ORCA', then the Orca application fonts will be loaded
        """
        self.oEventDispatcher.LogAction(u'LoadDefinitionFonts',oAction)
        uDefinitionName  = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.LoadFonts_ForDefinition(uDefinitionName)
        return -2

    def ExecuteActionLoadDefinitionActions(self,oAction):
        """
        loaddefinitionactions:
            Loads the actions of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's actions should be loaded. If not given, then all definition actions will be loaded
        """

        self.oEventDispatcher.LogAction(u'LoadDefinitionActions',oAction)
        uDefinitionName  = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.LoadActions_ForDefinition(uDefinitionName)
        return -2

    def ExecuteActionLoadDefinitionGestures(self,oAction):
        """
        loaddefinitiongestures:
            Loads the gestures of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's gestures should be loaded. If not given, then all definition gestures will be loaded
        """
        self.oEventDispatcher.LogAction(u'LoadDefinitionGestures',oAction)
        uDefinitionName  = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.LoadGestures_ForDefinition(uDefinitionName)
        return -2

    def ExecuteActionInitInterfaceSettings(self,oAction):
        """
        initinterfacesettings:
            Init the interface settings of all definitions or from a single definition
            Parameter:
            definitionname: name of definition, who's interface settings should be initialized. If not given, then all definition interface settings will be initialized
        """
        self.oEventDispatcher.LogAction(u'InitInterfaceSettings',oAction)
        uDefinitionName  = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.InitInterFaceSettings_ForDefinition(uDefinitionName)
        return -2

    def ExecuteActionRegisterFonts(self,oAction):
        """
        registerfonts:
            Register all used fonts
            Parameter:
            fontname: name of font to register. If not given, then all fonts will be registered
        """

        self.oEventDispatcher.LogAction(u'RegisterFonts',oAction)
        uFontName  = oAction.dActionPars.get("fontname","")
        Globals.oTheScreen.RegisterFonts(uFontName)
        return -2

    def ExecuteActionRegisterInterfaces(self,oAction):
        """
        registerinterfaces:
            Register all used interfaces
            Parameter:
            interfacename: name of interface to register. If not given, then all interfaces will be registered
        """

        self.oEventDispatcher.LogAction(u'RegisterInterfaces',oAction)
        uInterfaceName  = oAction.dActionPars.get("interfacename","")
        self.oEventDispatcher.LogAction(u'RegisterInterfaces',oAction)
        Globals.oTheScreen.RegisterInterFaces(uInterfaceName)
        return -2

    def ExecuteActionParseDefinitionXML(self,oAction):
        """
        parsedefinitionxml:
            Parses a definition xml file
            Parameter:
            definitionname: name of definition, who's xml file should be loaded. If not given, then all definition xml files will be loaded
        """

        self.oEventDispatcher.LogAction(u'ParseDefinitionXML',oAction)
        uDefinitionName  = oAction.dActionPars.get("definitionname","")
        Globals.oTheScreen.ParseDefinitionXmlFile(uDefinitionName)
        return -2

    def ExecuteActionLoadRepositoryContent(self,oAction):
        """
        loadrepositorycontent:
            Loads the content of a repository
            Parameter:
            None
        """

        self.oEventDispatcher.LogAction(u'LoadRepositoryContent',oAction)
        Globals.oDownLoadSettings.LoadRepositoryDirectory(bDoNotExecute=False)
        return -2

    def ExecuteActionLoadResource(self,oAction):
        """
        loadresource:
            Loads a resource from an online repository
            Parameter:
            resourcereference: Reference to load
        """

        self.oEventDispatcher.LogAction(u'LoadResource',oAction)
        uResourceReference  = oAction.dActionPars.get("resourcereference","")
        self.oLoadOnlineResource=cLoadOnlineResource()
        self.oLoadOnlineResource.LoadSingleFile(uResourceReference,self.oEventDispatcher.aProgressBars[-1])
        return -2


    def ExecuteActionExecuteFTPCommand(self,oAction):
        """
        executeftpcommand:
            Executes various FTP commands (connect, disconnect, uploadfile)
            Parameter:
            None
        """

        bRet = None
        self.oEventDispatcher.LogAction(u'ExecuteFTPCommand',oAction)

        uCommand           = ReplaceVars(oAction.dActionPars.get("command",         ""))
        uHost              = ReplaceVars(oAction.dActionPars.get("host",            ""))
        uUsername          = ReplaceVars(oAction.dActionPars.get("user",            ""))
        uPassword          = ReplaceVars(oAction.dActionPars.get("password",        ""))
        uSSL               = ReplaceVars(oAction.dActionPars.get("ssl",             ""))

        oLocalFile         = cFileName('').ImportFullPath(ReplaceVars(oAction.dActionPars.get("localfile",       "")))
        oLocalBaseFolder   = cPath(ReplaceVars(oAction.dActionPars.get("localbasefolder", "")))
        oRemoteBaseFolder  = cPath(ReplaceVars(oAction.dActionPars.get("remotebasefolder","")))

        if Globals.oFTP is None:
            Globals.oFTP = cFTP(ToBool(uSSL))

        if uCommand==u'connect':
            bRet = Globals.oFTP.Connect(uServer = uHost)
            if bRet:
                bRet=Globals.oFTP.Login(uUsername = uUsername, uPassword=uPassword )
        elif uCommand==u'disconnect':
            bRet=Globals.oFTP.DisConnect()
        elif uCommand==u'uploadfile':
            bRet = Globals.oFTP.UploadLocalFile(oFile=oLocalFile, oBaseLocalDir=oLocalBaseFolder, oBaseRemoteDir=oRemoteBaseFolder)
        if bRet:
            return 0
        else:
            return 1

    def ExecuteActionCheckPermissions(self,oAction):
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
        self.oEventDispatcher.LogAction(u'CheckForPermissions',oAction)
        Globals.oCheckPermissions.Wait()
        return -2

    def ExecuteActionCheckOnSleep(self,oAction):
        """
        CheckOnSleep
            Verifies, if we are still on sleep (so Android/Kivy missed to send the resume command
            Parameter:
            oAction: Unused
        """

        if Globals.bOnSleep:
            self.oEventDispatcher.LogAction(u'CheckOnSleep, resume now', oAction)
            Globals.oApp.on_resume()
        return -2

    def ExecuteActionResumeOnSleep(self,oAction):
        """
        ResumeFromSleep
            Resumes from sleep, if manual triggered
            Parameter:
            oAction: Unused
        """

        if Globals.bOnSleep:
            self.oEventDispatcher.LogAction(u'Resume from Sleep, resume now', oAction)
            Globals.oApp.on_resume()
        return -2
