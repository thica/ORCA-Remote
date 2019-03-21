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

from kivy.logger                             import Logger
from kivy.clock                              import Clock

from ORCA.RepManagerEntry                    import cRepManagerEntry
from ORCA.interfaces.BaseInterfaceSettings   import cBaseInterFaceSettings
from ORCA.interfaces.InterfaceResultParser   import cInterFaceResultParser
from ORCA.interfaces.InterfaceConfig         import cInterFaceConfig
from ORCA.interfaces.InterfaceConfigDiscover import cInterFaceConfigDiscover

from ORCA.utils.FileName                     import cFileName

from ORCA.utils.LogError                     import LogError
from ORCA.utils.TypeConvert                  import ToDic
from ORCA.utils.TypeConvert                  import ToIntVersion
from ORCA.utils.TypeConvert                  import ToUnicode
from ORCA.vars.Replace                       import ReplaceVars
from ORCA.vars.Access                        import SetVar

import ORCA.Globals as Globals

__all__ = ['cBaseInterFace']


class cBaseInterFace(object):
    """ Basic Interface class """

    # Some Type hints
    oInterFaceConfigDiscover = None  # type: cInterFaceConfigDiscover
    oInterFaceConfig         = None  # type: cInterFaceConfig

    class cInterFaceSettings(cBaseInterFaceSettings):
        """ Needs to be implemented by main interface class """
        pass

    def __init__(self):

        self.aDiscoverScriptsBlackList  = []
        self.aDiscoverScriptsWhiteList  = []
        self.aSettings                  = {}
        self.bIsInit                    = False
        self.iLastRet                   = 0
        self.iMyVersion                 = ToIntVersion('1.0.0')
        self.iOrcaVersion               = ToIntVersion('1.0.0')     #OrcaVersion defines for what Orca Version the Interface has been developed
        self.oAction                    = None
        self.oInterFaceConfig           = None
        self.oInterFaceConfigDiscover   = None
        self.oFnInterFace               = None
        self.uInterFaceName             = u''
        self.oPathMyCode                = None
        self.oPathMy                    = None

    def Init(self,uInterFaceName,oFnInterFace=None):
        """ Initialisizes the Interface

        :param string uInterFaceName: unicode : Name of the interface
        :param cFileName oFnInterFace: The Filename of the interface
        """

        self.bIsInit            = True
        self.uInterFaceName     = uInterFaceName

        if oFnInterFace is None:
            oFnInterFacePy    = cFileName(Globals.oPathInterface +  uInterFaceName) + u'interface.py'
            oFnInterFace      = cFileName(oFnInterFacePy)

        self.oFnInterFace     = cFileName(oFnInterFace)

        self.oPathMyCode        = Globals.oPathInterface + self.uInterFaceName
        self.oPathMy            = Globals.oDefinitionPathes.oPathDefinitionInterfaceSettings +self.uInterFaceName
        if not self.oPathMy.Exists():
            self.oPathMy.Create()

        self.oInterFaceConfig           = cInterFaceConfig(self)
        self.oInterFaceConfig.Init()
        self.oInterFaceConfigDiscover   = cInterFaceConfigDiscover(self)
        self.oInterFaceConfigDiscover.Init()

        Globals.oLanguage.LoadXmlFile("INTERFACE", uInterFaceName)

        oRepManagerEntry=cRepManagerEntry(oFnInterFace)
        if oRepManagerEntry.ParseFromSourceFile():
            self.iMyVersion     = oRepManagerEntry.oRepEntry.iVersion
            self.iOrcaVersion   = oRepManagerEntry.oRepEntry.iMinOrcaVersion
            #OrcaVersion defines for what Orca Version the Interface has been developed
        Globals.oNotifications.RegisterNotification("on_stopapp",self.DeInit,"Interface:"+self.uInterFaceName)
        Globals.oNotifications.RegisterNotification("on_pause",self.OnPause,"Interface:"+self.uInterFaceName)
        Globals.oNotifications.RegisterNotification("on_resume",self.OnResume,"Interface:"+self.uInterFaceName)
        self.ShowDebug(u'Init')

    def DeInit(self, **kwargs):
        """ Deinitialisizes the interface """
        self.ShowDebug(u'DeInit')

    def DoAction(self,oAction):
        """
        Main entry function for performing an action. Handles repeating actions

        :rtype: int
        :param cAction oAction:
        :return: 0 if successfull, 1 onnexception error, -10 if codeset not found
        """
        uConfigName   = oAction.dActionPars.get(u'configname',u'')
        oSetting      = self.GetSettingObjectForConfigName(uConfigName)
        uCmdName      = ReplaceVars(oAction.dActionPars.get('commandname',""))
        uCmdNameLocal = oSetting.MakeLocalActionName(uCmdName)
        aActions      = Globals.oActions.GetActionList(uActionName = uCmdNameLocal, bNoCopy = False)
        if aActions is None:
            self.ShowError("Action not found:"+uCmdName,uConfigName)
            return -10

        for uKey in oAction.dCommandParameter:
            oSetting.SetContextVar(uKey,oAction.dCommandParameter[uKey])
            SetVar(uVarName = uKey, oVarValue = oAction.dCommandParameter[uKey])

        aExecActions=[]

        uCmd= u''

        try:
            for oTmpAction in aActions:
                uCmd=oTmpAction.uCmd
                if uCmd.startswith('{"REPEAT":'):
                    dRepeatCmds    = ToDic(uCmd)
                    uRepeatCmd     = dRepeatCmds["REPEAT"]["REPEATCMD"]
                    uRepeatVarName = dRepeatCmds["REPEAT"]["REPEATVAR"]
                    uRepeatVar     = ReplaceVars(uRepeatVarName,self.uInterFaceName+u'/'+oSetting.uConfigName)
                    if uRepeatVar == "":
                        uRepeatVar = ReplaceVars(uRepeatVarName)
                    iLen = len(uRepeatVar)
                    for i in range(iLen):
                        uRepeatChar=uRepeatVar[i]
                        uKey2=uRepeatCmd+uRepeatChar
                        aActionRepeatActions=Globals.oActions.GetActionList(uActionName = oSetting.MakeLocalActionName(ReplaceVars(uKey2)),bNoCopy = False)
                        if aActionRepeatActions is not None:
                            for oRepeatAction in aActionRepeatActions:
                                if oRepeatAction.iActionId  == Globals.oActions.oActionType.Codeset:
                                    oRepeatAction.dActionPars['nologout']='1'
                                aExecActions.append(oRepeatAction)
                        else:
                            Logger.error(u'Error Parsing/Sending Repeats, RepeatCommand not found %s' % (uKey2))

                    for oTmpAction1 in reversed(aExecActions):
                        if oTmpAction1.iActionId  == Globals.oActions.oActionType.Codeset:
                            oTmpAction1.dActionPars['nologout']='0'
                            break

                else:
                    if oAction.uRetVar:
                        oTmpAction.uRetVar=oAction.uRetVar
                    aExecActions.append(oTmpAction)

        except Exception as e:
            self.ShowError(u'Error Parsing/Sending Repeats %s' % (uCmd),"",e)
            return 1

        Globals.oEvents.ExecuteActionsNewQueue(aExecActions, oAction.oParentWidget)
        return 0

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        """
        Template function

        :param cAction oAction: The Action object
        :param cSetting oSetting: The Setting object
        :param string uRetVar: The return value
        :param bool bNoLogOut: Switch, that the setting object should not logout
        :return: The return code. always 0 for this template
        """
        oSetting.oAction     = oAction
        oSetting.oLastAction = oAction
        return 0

    def AddTrigger(self,oAction):
        """
        Adds a trigger

        :param cAction oAction: The Action object to set a trigger
        """

        uTrigger = ReplaceVars(oAction.dActionPars.get("triggername",""))
        uAction  = ReplaceVars(oAction.dActionPars.get("actionname",""))
        uRetVar  = oAction.dActionPars.get("retvar","")
        uGetVar  = oAction.dActionPars.get("getvar","")

        if uAction!=u'' or uRetVar!=u'':
            self.ShowDebug(u'Adding Trigger:'+uTrigger,oAction.dActionPars.get(u'configname',u''))
        else:
            self.ShowDebug(u'Delete Trigger:'+uTrigger,oAction.dActionPars.get(u'configname',u''))
        oSetting=self.GetSettingObjectForConfigName(oAction.dActionPars.get(u'configname',u''))

        if uAction==u'' and uRetVar==u'':
            oSetting.DelTrigger(uTrigger)
        else:
            oSetting.AddTrigger(uTrigger,uAction,uRetVar,uGetVar)

    def OnPause(self,**kwargs):
        """
        entry for the onpause event

        """
        self.ShowInfo(u'OnPause')
        for aSetting in self.aSettings:
            oSetting=self.aSettings[aSetting]
            if oSetting.aInterFaceIniSettings.bDisconnectInterFaceOnSleep:
                if oSetting.bIsConnected:
                    oSetting.bResumeConnection=True
                    self.aSettings[aSetting].Disconnect()

    def OnResume(self,**kwargs):
        """
        entry for the onresume event

        """
        self.ShowInfo(u'OnResume')
        for aSetting in self.aSettings:
            oSetting=self.aSettings[aSetting]
            if oSetting.bResumeConnection:
                oSetting.bResumeConnection=False
                oSetting.Connect()
                if oSetting.bIsConnected:
                    if oSetting.aInterFaceIniSettings.get('iTimeToClose') is not None:
                        if oSetting.aInterFaceIniSettings.iTimeToClose>0:
                            Clock.unschedule(oSetting.FktDisconnect)
                            Clock.schedule_once(oSetting.FktDisconnect, oSetting.aInterFaceIniSettings.iTimeToClose)

    def FindCodesetFile(self,uFNCodeset):
        """
        looks for a codeset file on two locations

        :rtype: cFileName
        :param string uFNCodeset: The file name of the codeset file
        :return: The founded filename
        """
        oFnName= cFileName(self.oPathMy)+uFNCodeset
        if oFnName.Exists():
            return oFnName

        oFnName=cFileName(Globals.oPathCodesets) + uFNCodeset
        if oFnName.Exists():
            return oFnName
        oFnName = cFileName(Globals.oPathCodesets +  self.uInterFaceName) + uFNCodeset
        if oFnName.Exists():
            return oFnName

        return None

    def ParseResult(self,oAction,uResponse,oSetting):
        """
        Parses the result of an interface action

        :rtype: string
        :param cAction oAction: The Action object
        :param string uResponse: The Response to parse
        :param cSetting oSetting: The setting object
        :return: The parsed response
        """

        if oSetting.oResultParser is None:
            oSetting.oResultParser                          = cInterFaceResultParser(self, oSetting.uConfigName)
            oSetting.oResultParser.uGlobalParseResultOption = oSetting.aInterFaceIniSettings.uParseResultOption
            oSetting.oResultParser.uGlobalTokenizeString    = oSetting.aInterFaceIniSettings.uParseResultTokenizeString
            if oAction is None:
                return "",""
        return oSetting.oResultParser.ParseResult(oAction,uResponse,oSetting)


    def GetSettingObjectForConfigName(self,uConfigName):
        """
        Creates/returns a config object

        :rtype: cSetting
        :param string uConfigName: The Name of the configuration
        :return: a Setting object
        """

        oSetting=self.aSettings.get(uConfigName)

        if oSetting is None:
            uConfigName = ReplaceVars(uConfigName)
            oSetting    = self.aSettings.get(uConfigName)

        if uConfigName=='' or '$var' in  uConfigName:
            uConfigName = ReplaceVars(uConfigName)

        if oSetting is None:
            oSetting=self.cInterFaceSettings(self)
            self.aSettings[uConfigName]=oSetting
            oSetting.ReadConfigFromIniFile(uConfigName)
        return oSetting

    def GetConfigCodesetList(self):
        """
        Gets the list of codeset file names for an interface

        :rtype: list
        :return: A list of all codeset files for an interface
        """
        aCodesetFiles = []
        uPattern=u"CODESET_"+self.uInterFaceName
        oPathFolder = Globals.oPathCodesets + self.uInterFaceName
        if oPathFolder.Exists():
            aCodesetFilesSub=oPathFolder.GetFolderList()
            for uFile in aCodesetFilesSub:
                if uFile.startswith(uPattern):
                    aCodesetFiles.append(uFile)
        aCodesetFilesSub=self.oPathMy.GetFolderList()
        for uFile in  aCodesetFilesSub:
            if uFile.startswith(uPattern):
                aCodesetFiles.append(uFile)
        return aCodesetFiles

    def CreateCodsetListJSONString(self):
        """
        Creates a list of all codeset, suitable for the configuration JSON list

        :rtype: string
        :return: a string representing the codeset list
        """

        aCodesetFiles=self.GetConfigCodesetList()
        uSettingsJSON=u''
        uValueString=u''
        for uCodesetFile in aCodesetFiles:
            uValueString+=u'\"'+uCodesetFile+u'\",'
        uValueString= uValueString[1:len(uValueString)-2]
        uSettingsJSON+=uValueString
        return uSettingsJSON

    def GetConfigJSON(self):
        """
        Abstract function, needs to be overriden by interface class

        :rtype: dict
        :return: Dummy funtion, returns empty dict
        """
        return {}

    def _FormatShowMessage(self,uMsg,uParConfigName=""):
        """
        Creates a debug line for the interface

        :rtype: string
        :param string uMsg: The message to show
        :param string uParConfigName:  The name of the configuration
        :return: The formatted debug string
        """
        uConfigName = u''
        if uParConfigName:
            uConfigName = u'/' + uParConfigName

        return u'Interface ' + self.uInterFaceName + uConfigName + u': ' + uMsg

    def ShowWarning(self,uMsg,uParConfigName=""):
        """
        writes a warning message

        :rtype: string
        :param string uMsg: The warning message
        :param string uParConfigName: The configuration name
        :return: The written logfile entry
        """
        uRet = self._FormatShowMessage(uMsg,uParConfigName)
        Logger.warning (uRet)
        return uRet

    def ShowDebug(self,uMsg,uParConfigName=""):
        """
        writes a debug message

        :rtype: string
        :param string uMsg: The debug message
        :param string uParConfigName: The configuration name
        :return: The written logfile entry
        """
        uRet = self._FormatShowMessage(uMsg,uParConfigName)
        Logger.debug (uRet)
        return uRet

    def ShowInfo(self,uMsg,uParConfigName=""):
        """
        writes a info message

        :rtype: string
        :param string uMsg: The info message
        :param string uParConfigName: The configuration name
        :return: The written logfile entry
        """

        uRet = self._FormatShowMessage(uMsg,uParConfigName)
        Logger.info (uRet)
        return uRet

    def ShowError(self,uMsg, uParConfigName="",oException=None):
        """
        writes an error message

        :rtype: string
        :param string uMsg: The error message
        :param string uParConfigName: The configuration name
        :param exception oException: Optional, an exception to show
        :return: The written logfile entry
        """

        # uRet = self._FormatShowMessage(uMsg,uParConfigName)
        # Logger.debug (uRet)
        # return uRet
        uRet = self._FormatShowMessage(uMsg,uParConfigName)
        iErrNo = 0
        if oException is not None:
            if hasattr(oException,'errno'):
                iErrNo = oException.errno
        if iErrNo is  None:
            iErrNo = 12345
        if iErrNo!=0:
            uRet = uRet + u" "+ToUnicode(iErrNo)
        uRet=LogError (uRet,oException)
        return uRet

