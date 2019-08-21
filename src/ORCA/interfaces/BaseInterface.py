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

from ORCA.BaseObject                         import cBaseObject
from ORCA.interfaces.BaseInterfaceSettings   import cBaseInterFaceSettings
from ORCA.interfaces.InterfaceResultParser   import cInterFaceResultParser
from ORCA.interfaces.InterfaceConfig         import cInterFaceConfig
from ORCA.interfaces.InterfaceConfigDiscover import cInterFaceConfigDiscover
from ORCA.utils.FileName                     import cFileName
from ORCA.utils.TypeConvert                  import ToDic
from ORCA.vars.Replace                       import ReplaceVars
from ORCA.vars.Access                        import SetVar

import ORCA.Globals as Globals

__all__ = ['cBaseInterFace']


class cBaseInterFace(cBaseObject):
    """ Basic Interface class """

    # Some Type hints
    oObjectConfigDiscover = None  # type: cInterFaceConfigDiscover
    oObjectConfig         = None  # type: cInterFaceConfig

    class cInterFaceSettings(cBaseInterFaceSettings):
        """ Needs to be implemented by main interface class """
        pass

    def __init__(self):

        super(cBaseInterFace,self).__init__()

        self.oObjectConfig              = None
        self.oObjectConfigDiscover      = None
        self.uObjectType                = "interface"

        self.aDiscoverScriptsBlackList  = []
        self.aDiscoverScriptsWhiteList  = []
        self.oAction                    = None
        self.iLastRet                   = 0

    def Init(self,uObjectName,oFnObject=None):
        """ Initialisizes the Interface

        :param string uObjectName: unicode : Name of the interface
        :param cFileName oFnObject: The Filename of the interface
        """

        super(cBaseInterFace, self).Init(uObjectName,oFnObject)

        self.oObjectConfig           = cInterFaceConfig(self)
        self.oObjectConfig.Init()
        self.oObjectConfigDiscover   = cInterFaceConfigDiscover(self)
        self.oObjectConfigDiscover.Init()

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
                    uRepeatVar     = ReplaceVars(uRepeatVarName,self.uObjectName+u'/'+oSetting.uConfigName)
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
                            Logger.error(u'Error Parsing/Sending Repeats, RepeatCommand not found %s' % uKey2)

                    for oTmpAction1 in reversed(aExecActions):
                        if oTmpAction1.iActionId  == Globals.oActions.oActionType.Codeset:
                            oTmpAction1.dActionPars['nologout']='0'
                            break

                else:
                    if oAction.uRetVar:
                        oTmpAction.uRetVar=oAction.uRetVar
                    aExecActions.append(oTmpAction)

        except Exception as e:
            self.ShowError(u'Error Parsing/Sending Repeats %s' % uCmd,"",e)
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
            if oSetting.aIniSettings.bDisconnectInterFaceOnSleep:
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
                    if oSetting.aIniSettings.get('iTimeToClose') is not None:
                        if oSetting.aIniSettings.iTimeToClose>0:
                            Clock.unschedule(oSetting.FktDisconnect)
                            Clock.schedule_once(oSetting.FktDisconnect, oSetting.aIniSettings.iTimeToClose)

    def FindCodesetFile(self,uFNCodeset):
        """
        looks for a codeset file on two locations

        :rtype: cFileName
        :param string uFNCodeset: The file name of the codeset file
        :return: The founded filename
        """
        oFnName= cFileName(self.oPathMyData)+uFNCodeset
        if oFnName.Exists():
            return oFnName

        oFnName=cFileName(Globals.oPathCodesets) + uFNCodeset
        if oFnName.Exists():
            return oFnName
        oFnName = cFileName(Globals.oPathCodesets +  self.uObjectName) + uFNCodeset
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
            oSetting.oResultParser.uGlobalParseResultOption = oSetting.aIniSettings.uParseResultOption
            oSetting.oResultParser.uGlobalTokenizeString    = oSetting.aIniSettings.uParseResultTokenizeString
            if oAction is None:
                return "",""
        return oSetting.oResultParser.ParseResult(oAction,uResponse,oSetting)

    def GetConfigCodesetList(self):
        """
        Gets the list of codeset file names for an interface

        :rtype: list
        :return: A list of all codeset files for an interface
        """
        aCodesetFiles = []
        uPattern=u"CODESET_"+self.uObjectName
        oPathFolder = Globals.oPathCodesets + self.uObjectName
        if oPathFolder.Exists():
            aCodesetFilesSub=oPathFolder.GetFolderList()
            aCodesetFilesSub = oPathFolder.GetFileList(bSubDirs=False,bFullPath=False)
            for uFile in aCodesetFilesSub:
                if uFile.startswith(uPattern):
                    aCodesetFiles.append(uFile)
        aCodesetFilesSub=self.oPathMyData.GetFileList(bSubDirs=True,bFullPath=False)
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

    def GetNewSettingObject(self):
        return self.cInterFaceSettings(self)

