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
from typing                                  import Union
from typing                                  import Optional

from typing                                  import List
from typing                                  import Dict
from typing                                  import Tuple

from kivy.logger                             import Logger
from kivy.clock                              import Clock

from ORCA.BaseObject                         import cBaseObject
from ORCA.interfaces.BaseInterfaceSettings   import cBaseInterFaceSettings
from ORCA.interfaces.InterfaceResultParser   import cInterFaceResultParser
from ORCA.interfaces.InterfaceConfig         import cInterFaceConfig
from ORCA.interfaces.InterfaceConfigDiscover import cInterFaceConfigDiscover
from ORCA.utils.FileName                     import cFileName
from ORCA.utils.Path                         import cPath
from ORCA.utils.TypeConvert                  import ToDic
from ORCA.vars.Replace                       import ReplaceVars
from ORCA.vars.Access                        import SetVar
from ORCA.Action                             import cAction
from ORCA.actions.ReturnCode                 import eReturnCode

import ORCA.Globals as Globals

__all__ = ['cBaseInterFace']


class cBaseInterFace(cBaseObject):
    """ Basic Interface class """

    class cInterFaceSettings(cBaseInterFaceSettings):
        """ Needs to be implemented by main interface class """
        pass

    def __init__(self):

        super().__init__()

        self.oObjectConfig:Optional[cInterFaceConfig]                    = None
        self.oObjectConfigDiscover:Optional[cInterFaceConfigDiscover]    = None
        self.uObjectType:str                                             = "interface"

        self.aDiscoverScriptsBlackList:List[str]                         = []
        self.aDiscoverScriptsWhiteList:List[str]                         = []
        self.oAction:Optional[cAction]                                   = None
        self.iMaxTryCount:int                                            = 2

    def Init(self,uObjectName:str,oFnObject:Optional[cFileName]=None) -> None:
        """ Initializes the Interface

        :param str uObjectName: unicode : Name of the interface
        :param cFileName oFnObject: The Filename of the interface
        """

        super().Init(uObjectName=uObjectName,oFnObject=oFnObject)

        self.oObjectConfig           = cInterFaceConfig(self)
        self.oObjectConfig.Init()
        self.oObjectConfigDiscover   = cInterFaceConfigDiscover(self)
        self.oObjectConfigDiscover.Init()

    def DoAction(self,oAction:cAction) -> eReturnCode:
        """
        Main entry function for performing an action. Handles repeating actions

        :param cAction oAction:
        :return: 0 if successful, 1 one exception error, -10 if codeset not found
        """
        uConfigName:str                     = oAction.dActionPars.get(u'configname',u'')
        oSetting:cBaseInterFaceSettings     = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        uCmdName:str                        = ReplaceVars(oAction.dActionPars.get('commandname',""))
        uCmdNameLocal:str                   = oSetting.MakeLocalActionName(uActionName=uCmdName)
        aActions:List[cAction]              = Globals.oActions.GetActionList(uActionName = uCmdNameLocal, bNoCopy = False)

        if aActions is None:
            self.ShowError(uMsg="Action not found:"+uCmdName,uParConfigName=uConfigName,uParAdd=oSetting.aIniSettings.uFNCodeset)
            return eReturnCode.NotFound

        for uKey in oAction.dCommandParameter:
            oSetting.SetContextVar(uVarName=uKey,uVarValue=oAction.dCommandParameter[uKey])
            SetVar(uVarName = uKey, oVarValue = oAction.dCommandParameter[uKey])

        aExecActions:List[cAction] = []

        uCmd:str = u''

        try:
            for oTmpAction in aActions:
                uCmd=oTmpAction.uCmd
                if uCmd.startswith('{"REPEAT":'):
                    dRepeatCmds:Dict[str,Dict]    = ToDic(uCmd)
                    uRepeatCmd:str     = dRepeatCmds["REPEAT"]["REPEATCMD"]
                    uRepeatVarName:str = dRepeatCmds["REPEAT"]["REPEATVAR"]
                    uRepeatVar:str     = ReplaceVars(uRepeatVarName,self.uObjectName+u'/'+oSetting.uConfigName)
                    if uRepeatVar == "":
                        uRepeatVar = ReplaceVars(uRepeatVarName)
                    iLen:int = len(uRepeatVar)
                    for i in range(iLen):
                        uRepeatChar:str=uRepeatVar[i]
                        uKey2:str=uRepeatCmd+uRepeatChar
                        aActionRepeatActions:List[cAction]=Globals.oActions.GetActionList(uActionName = oSetting.MakeLocalActionName(ReplaceVars(uKey2)),bNoCopy = False)
                        if aActionRepeatActions is not None:
                            for oRepeatAction in aActionRepeatActions:
                                if oRepeatAction.iActionId  == Globals.oActions.oActionType.Codeset:
                                    oRepeatAction.dActionPars['nologout']='1'
                                aExecActions.append(oRepeatAction)
                        else:
                            Logger.error(u'Error Parsing/Sending Repeats, RepeatCommand not found %s' % uKey2)

                    oTmpAction1:cAction
                    for oTmpAction1 in reversed(aExecActions):
                        if oTmpAction1.iActionId  == Globals.oActions.oActionType.Codeset:
                            oTmpAction1.dActionPars['nologout']='0'
                            break
                else:
                    if oAction.uRetVar:
                        oTmpAction.uRetVar=oAction.uRetVar
                    aExecActions.append(oTmpAction)

        except Exception as e:
            self.ShowError(uMsg= u'Error Parsing/Sending Repeats %s' % uCmd,uParConfigName= "",oException=e)
            return eReturnCode.Error

        Globals.oEvents.ExecuteActionsNewQueue(aExecActions, oAction.oParentWidget)
        return eReturnCode.Success

    def SendCommand(self,*,oAction:cAction,oSetting:cBaseInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
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
        return eReturnCode.Success

    def AddTrigger(self,oAction:cAction) -> None:
        """
        Adds a trigger

        :param cAction oAction: The Action object to set a trigger
        """

        uTrigger:str    = ReplaceVars(oAction.dActionPars.get("triggername",""))
        uAction:str     = ReplaceVars(oAction.dActionPars.get("actionname",""))
        uRetVar:str     = oAction.dActionPars.get("retvar","")
        uGetVar:str     = oAction.dActionPars.get("getvar","")
        uConfigName:str = ReplaceVars(oAction.dActionPars.get("configname",""))

        self.ShowDebug(uMsg=u'Adding Trigger:'+uTrigger,uParConfigName=uConfigName)
        oSetting=self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        oSetting.AddTrigger(uTrigger,uAction,uRetVar,uGetVar)

    def DelTrigger(self,oAction:cAction) -> None:
        """
        Deletes a trigger

        :param cAction oAction: The Action object to set a trigger
        """

        uTrigger:str    = ReplaceVars(oAction.dActionPars.get("triggername",""))
        uActionName:str = ReplaceVars(oAction.dActionPars.get("actionname",""))
        uConfigName:str = ReplaceVars(oAction.dActionPars.get("configname",""))

        self.ShowDebug(uMsg=u'Delete Trigger:'+uTrigger,uParConfigName=uConfigName)
        oSetting=self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        oSetting.DelTrigger(uTrigger=uTrigger,uActionName=uActionName)

    def OnPause(self,**kwargs) -> None:
        """
        entry for the onpause event

        """
        self.ShowInfo(uMsg=u'OnPause')

        uSettingName:str

        for uSettingName in self.dSettings:
            oSetting:cBaseInterFaceSettings = self.dSettings[uSettingName]
            if oSetting.aIniSettings.bDisconnectInterFaceOnSleep:
                if oSetting.bIsConnected:
                    oSetting.bResumeConnection=True
                    self.dSettings[uSettingName].Disconnect()

    def OnResume(self,**kwargs) -> None:
        """
        entry for the onresume event

        """
        self.ShowInfo(uMsg=u'OnResume')

        uSettingName:str

        for uSettingName in self.dSettings:
            oSetting:cBaseInterFaceSettings=self.dSettings[uSettingName]
            if oSetting.bResumeConnection:
                oSetting.bResumeConnection=False
                oSetting.Connect()
                if oSetting.bIsConnected:
                    if oSetting.aIniSettings.get('iTimeToClose') is not None:
                        if oSetting.aIniSettings.iTimeToClose>0:
                            Clock.unschedule(oSetting.FktDisconnect)
                            Clock.schedule_once(oSetting.FktDisconnect, oSetting.aIniSettings.iTimeToClose)

    def FindCodesetFile(self,uFNCodeset:str) -> Union[cFileName,None]:
        """
        looks for a codeset file on two locations

        :param str uFNCodeset: The file name of the codeset file
        :return: The founded filename
        """

        oFnName: cFileName

        oFnName = cFileName(self.oPathMyData)+uFNCodeset
        if oFnName.Exists():
            return oFnName

        oFnName=cFileName(Globals.oPathCodesets) + uFNCodeset
        if oFnName.Exists():
            return oFnName
        oFnName = cFileName(Globals.oPathCodesets +  self.uObjectName) + uFNCodeset
        if oFnName.Exists():
            return oFnName

        return None

    def ParseResult(self,oAction:cAction,uResponse:str,oSetting:cBaseInterFaceSettings) -> Tuple[str,str]:
        """
        Parses the result of an interface action

        :param cAction oAction: The Action object
        :param string uResponse: The Response to parse
        :param cSetting oSetting: The setting object
        :return: The parsed response
        """

        if oSetting.oResultParser is None:
            oSetting.oResultParser                          = cInterFaceResultParser(self, oSetting.uConfigName)
            oSetting.oResultParser.uGlobalParseResultOption = oSetting.aIniSettings.uParseResultOption
            oSetting.oResultParser.uGlobalTokenizeString    = oSetting.aIniSettings.uParseResultTokenizeString
            if oAction is None:
                return "",""
        return oSetting.oResultParser.ParseResult(oAction,uResponse,oSetting)

    def GetConfigCodesetList(self) -> List[str]:
        """
        Gets the list of codeset file names for an interface

        :return: A list of all codeset files for an interface
        """
        aCodesetFiles:List[str] = []
        uPattern:str            = u"CODESET_"+self.uObjectName
        oPathFolder:cPath       = Globals.oPathCodesets + self.uObjectName
        uFile:str

        if oPathFolder.Exists():
            aCodesetFilesSub:List[str] = oPathFolder.GetFileList(bSubDirs=False,bFullPath=False)
            for uFile in aCodesetFilesSub:
                if uFile.startswith(uPattern):
                    aCodesetFiles.append(uFile)
        aCodesetFilesSub=self.oPathMyData.GetFileList(bSubDirs=True,bFullPath=False)
        for uFile in  aCodesetFilesSub:
            if uFile.startswith(uPattern):
                aCodesetFiles.append(uFile)
        return aCodesetFiles

    def CreateCodesetListJSONString(self) -> str:
        """
        Creates a list of all codeset, suitable for the configuration JSON list

        :return: a string representing the codeset list
        """

        aCodesetFiles:List[str] = self.GetConfigCodesetList()
        uSettingsJSON:str       = u''
        uValueString:str        = u''
        for uCodesetFile in aCodesetFiles:
            uValueString+=u'\"'+uCodesetFile+u'\",'
        uValueString = uValueString[1:len(uValueString)-2]
        uSettingsJSON+=uValueString
        return uSettingsJSON

    def GetNewSettingObject(self) -> cBaseInterFaceSettings:
        return self.cInterFaceSettings(self)

    # noinspection PyMethodMayBeStatic
    def CloseSettingConnection(self,oSetting:cBaseInterFaceSettings,bNoLogOut:bool):
        if not bNoLogOut:
            if oSetting.bIsConnected:
                if oSetting.aIniSettings.iTimeToClose==0:
                    oSetting.Disconnect()
                elif oSetting.aIniSettings.iTimeToClose!=-1:
                    Clock.unschedule(oSetting.FktDisconnect)
                    Clock.schedule_once(oSetting.FktDisconnect, oSetting.aIniSettings.iTimeToClose)
