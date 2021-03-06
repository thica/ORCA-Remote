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

from typing                                     import Dict
from typing                                     import List
from typing                                     import Union
from typing                                     import Any
from typing                                     import Tuple
from typing                                     import Optional

from copy                                       import copy
from xml.etree.ElementTree                      import Element

from kivy.logger                                import Logger
from kivy.clock                                 import Clock

from ORCA                                       import Globals as Globals
from ORCA.Action                                import GetActionID
from ORCA.Action                                import cAction
from ORCA.interfaces.BaseTrigger                import cBaseTrigger
from ORCA.BaseSettings                          import cBaseSettings
from ORCA.ui.ShowErrorPopUp                     import ShowErrorPopUp
from ORCA.utils.CachedFile                      import CachedFile
from ORCA.utils.TypeConvert                     import ToBool
from ORCA.utils.XML                             import Orca_FromString, Orca_include, orca_et_loader
from ORCA.vars.Access                           import SetVar
from ORCA.utils.FileName                        import cFileName

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.interfaces.BaseInterface import cBaseInterFace
    from ORCA.interfaces.InterfaceResultParser import cInterFaceResultParser
else:
    from typing import TypeVar
    cBaseInterFace = TypeVar("cBaseInterFace")
    cInterFaceResultParser = TypeVar("cInterFaceResultParser")


__all__ = ['cBaseInterFaceSettings']

class cBaseInterFaceSettings(cBaseSettings):
    """ A base class for the interfacesettings """
    def __init__(self, oInterFace):
        # some default settings, which should be there even if not configered by the interface
        # use the exact spelling as in the settings json

        super().__init__(oInterFace)

        self.oInterFace:cBaseInterFace                          = oInterFace
        self.uConfigName:str                                    = "DEVICE_DEFAULT"
        self.uType:str                                          = "interface"

        self.aIniSettings.bDisableInterFaceOnError              = False
        self.aIniSettings.bDisconnectInterFaceOnSleep           = True
        self.aIniSettings.fTimeOut                              = 1.0
        self.aIniSettings.iTimeToClose                          = -1
        self.aIniSettings.uFNCodeset                            = u''
        self.aIniSettings.uHost                                 = u'192.168.1.2'
        self.aIniSettings.uParseResultOption                    = u''
        self.aIniSettings.uParseResultTokenizeString            = u''
        self.aIniSettings.uParseResultFlags                     = u''
        self.aIniSettings.uPort                                 = u'80'
        self.aIniSettings.uResultEndString                      = u'\\n'
        self.aIniSettings.uDiscoverScriptName                   = u''
        self.bInConnect:bool                                    = False
        self.bIsConnected:bool                                  = False
        self.bResumeConnection:bool                             = False
        self.dTriggers:Dict[str,cBaseTrigger]                   = {}
        self.iDiscoverCount:int                                 = 0
        self.iMaxDiscoverCount:int                              = 1
        self.oAction:Union[cAction,None]                        = None
        self.oLastAction:Union[cAction,None]                    = None
        self.dStandardActions:Dict[str,Union[cAction,None]]     = {"ping":None,"defaultresponse":None}
        self.bStandardActionsLoaded:bool                        = False
        self.oResultParser:Union[cInterFaceResultParser,None]   = None
        self.dNewTriggers:Dict[str,List[cBaseTrigger]]          = {}

    def ReadStandardActions(self) -> None:
        """ Reads the standard codeset codes eg ping """
        if not self.bStandardActionsLoaded:
            for uKey in self.dStandardActions:
                oAction:cAction = self.ReadStandardActions_sub(self.dStandardActions[uKey],uKey)
                if oAction:
                    self.dStandardActions[uKey]=oAction
                self.bStandardActionsLoaded=True

    def ReadStandardActions_sub(self,oTargetAction:cAction,uActionName:str) -> Union[cAction,None]:
        """
        Sub Routine to read the standard actions

        :param cAction|None oTargetAction: The Action for a standradextion, should be None as input
        :param str uActionName: The Actionname
        """

        if oTargetAction is None or oTargetAction==u'':
            aActions:List[cAction] = Globals.oActions.GetActionList(uActionName = self.MakeLocalActionName(uActionName), bNoCopy=False)
            if aActions is not None:
                if len(aActions)==1:
                    return aActions[0]
                else:
                    Logger.error("StandardCodesetCodes can''t be multiline:"+uActionName)
        return None

    def ExecuteStandardAction(self,uActionName:str) -> int:
        """
        Executes as standard action

        :param string uActionName:
        :return: The return code of the action
        """

        aActions:List[cAction]=Globals.oActions.GetActionList(uActionName = self.MakeLocalActionName(uActionName), bNoCopy = False)
        if aActions is not None:
            return Globals.oEvents.ExecuteActionsNewQueue(aActions, None, True)
        else:
            return 0

    # noinspection PyUnusedLocal
    def Discover(self,**kwargs) -> bool:
        """ helper for the discover scripts"""

        if self.aIniSettings.uHost!="discover":
            return True

        self.iDiscoverCount += 1
        if self.iDiscoverCount > self.iMaxDiscoverCount:
            return False

        self.ShowDebug(uMsg=u'Try to discover device')
        uDiscoverScriptName:str = self.aIniSettings.uDiscoverScriptName
        dParams:Dict[str,Any] = {}

        for uKey in self.aIniSettings:
            if uKey[1:].startswith(uDiscoverScriptName.upper()):
                uParamKey=uKey[len(uDiscoverScriptName)+2:]
                dParams[uParamKey]=self.aIniSettings[uKey]

        dResult:Dict = Globals.oScripts.RunScript(uDiscoverScriptName, **dParams)
        oException:Exception = dResult.get('Exception','')
        if oException is None or oException=='':
            for uKey in dResult:
                if uKey != Exception:
                    self.aIniSettings[uKey]=dResult[uKey]
                if uKey == 'Host' and dResult.get("Hostname","")=="":
                    if self.aIniSettings.bSaveDiscoveredIP:
                        self.oInterFace.oObjectConfig.oConfigParser.set(self.uSection, u'olddiscoveredip', self.aIniSettings.uHost)
                        self.oInterFace.oObjectConfig.oConfigParser.write()
                if uKey == 'Hostname' and dResult.get("Hostname","")!="":
                    self.aIniSettings["Host"]=dResult[uKey]
                    if self.aIniSettings.bSaveDiscoveredIP:
                        self.oInterFace.oObjectConfig.oConfigParser.set(self.uSection, u'olddiscoveredip', self.aIniSettings.uHostname)
                        self.oInterFace.oObjectConfig.oConfigParser.write()

            return True
        else:
            self.ShowError(uMsg=u'Can''t discover device:' + self.oInterFace.oObjectConfig.oFnConfig.string + u' Section:' + self.uSection, oException=oException)
            return False

    def ReadCodeset(self) -> None:
        """  reads the codeset file """

        oTmpCodeSetAction:cAction
        aTmpCodeSetAction:List[cAction]

        oCodesetFileName:cFileName = self.oInterFace.FindCodesetFile(self.aIniSettings.uFNCodeset)

        if oCodesetFileName is None:
            self.ShowDebug(uMsg=u'Cannot Read Codeset (Not Found):' + self.aIniSettings.uFNCodeset)
            return

        self.ShowDebug(uMsg=u'Read Codeset:'+oCodesetFileName)

        if oCodesetFileName.Exists():
            uET_Data:str     = CachedFile(oFileName=oCodesetFileName)
            oET_Root:Element = Orca_FromString(uET_Data=uET_Data,oDef=None,uFileName=oCodesetFileName.string)
            Orca_include(oET_Root,orca_et_loader)
            dTmpCodeSetActions:Dict[str,List[cAction]] = {}
            Globals.oActions.LoadActionsSub(oET_Root=oET_Root ,uSegmentTag=u'',uListTag=u'action', dTargetDic=dTmpCodeSetActions,uFileName=oCodesetFileName.string)
            # replacing alias
            bDoItAgain:bool = True
            uKey:str        = u''
            uAlias:str      = u''

            try:
                # replace all alias
                while bDoItAgain:
                    bDoItAgain=False
                    try:
                        for uKey in dTmpCodeSetActions:
                            iPos:int = -1
                            for oTmpCodeSetAction in dTmpCodeSetActions[uKey]:
                                iPos += 1
                                if oTmpCodeSetAction.dActionPars.get('type','')=="alias":
                                    uAlias:str = oTmpCodeSetAction.dActionPars['cmd']
                                    aAliasCodeSet:List[cAction] = dTmpCodeSetActions[uAlias]
                                    if len(aAliasCodeSet)==1:
                                        oTmpCodeSetAction = copy(aAliasCodeSet[0])
                                        oTmpCodeSetAction.uActionName= uAlias
                                    else:
                                        oTmpCodeSetAction.uActionString="call"
                                        oTmpCodeSetAction.dActionPars["actionname"]=uAlias
                                        oTmpCodeSetAction.iActionId=GetActionID(oTmpCodeSetAction.uActionString)
                                        oTmpCodeSetAction.dActionPars["type"]=""

                                    dTmpCodeSetActions[uKey][iPos]=oTmpCodeSetAction
                                    bDoItAgain=True

                    except Exception as e:
                        uMsg:str = self.ShowError(uMsg=u'Cannot read Codeset (wrong alias [%s=%s] CodesetFileName: %s):'% (uKey,uAlias,oCodesetFileName.string),oException=e)
                        ShowErrorPopUp(uTitle='Error Reading Codeset',uMessage=uMsg)

                # Make calls local & Read the common attributes
                for  uKey in dTmpCodeSetActions:
                    for oTmpCodeSetAction in dTmpCodeSetActions[uKey]:
                        if oTmpCodeSetAction.iActionId==Globals.oActions.oActionType.Call:
                            uActionName:str = oTmpCodeSetAction.dActionPars.get("actionname","")
                            if uActionName in dTmpCodeSetActions:
                                oTmpCodeSetAction.dActionPars["actionname"] = self.MakeLocalActionName(uActionName)
                        self.ReadAction(oTmpCodeSetAction)

                # add them to the global action list
                for  uKey in dTmpCodeSetActions:
                    Globals.oActions.SetActionList(self.MakeLocalActionName(uKey),dTmpCodeSetActions[uKey])

            except Exception as e:
                uMsg:str = self.ShowError(uMsg=u'Cannot read Codeset :',oException=e)
                ShowErrorPopUp(uTitle='Error Reading Codeset',uMessage=uMsg)

            self.SetContextVar(uVarName="firstcall",uVarValue="1")

    def ReadAction(self,oAction:cAction) -> None:
        """
        Adds and defaults some common attributes to the action

        :param cAction oAction: Reads an action from the action pars
        """

        oAction.uType                       = oAction.dActionPars.get(u'type',              u'send')
        oAction.uCmd                        = oAction.dActionPars.get(u'cmd',               u'No cmd action defined')
        oAction.uLocalDestVar               = oAction.dActionPars.get(u'ldestvar',          u'RESULT_' + oAction.uActionName)
        oAction.uGlobalDestVar              = oAction.dActionPars.get(u'gdestvar',          u'RESULT_' + oAction.uActionName)
        oAction.uGetVar                     = oAction.dActionPars.get(u'getvar',            u'')
        oAction.bWaitForResponse            = ToBool(oAction.dActionPars.get(u'waitforresponse',   u'0'))
        oAction.uParseResultOption          = oAction.dActionPars.get(u'parseoption',       self.aIniSettings.uParseResultOption)
        oAction.uParseResultTokenizeString  = oAction.dActionPars.get(u'parsetoken',        self.aIniSettings.uParseResultTokenizeString)
        oAction.uParseResultFlags           = oAction.dActionPars.get(u'parseflags',        self.aIniSettings.uParseResultFlags)
        oAction.uResultEndString            = oAction.dActionPars.get(u'parseendstring',    self.aIniSettings.uResultEndString)

        oAction.dActionPars['interface']  = self.oInterFace.uObjectName
        oAction.dActionPars['configname'] = self.uConfigName

        if oAction.dActionPars.get('varcontext','')=="codeset":
            oAction.dActionPars["varcontext"]=self.uContext

    def MakeLocalActionName(self,uActionName:str) -> str:
        """
        Creates a (codeset) local version of an action

        :param uActionName:
        :return:
        """
        return uActionName+" :"+self.uContext

    def Connect(self) -> bool:
        """ basic helper for managing connect """
        if self.bOnError:
            self.ShowDebug(uMsg=u'Interface Connect: Interface is on Error, setting interface to disconnected')
            self.bIsConnected=False
        if not self.aIniSettings.bDisableInterFaceOnError:
            self.bOnError=False
        if self.bIsConnected:
            self.ShowDebug(uMsg=u'Interface Connect: Interface is connected, no connect required.')
            return False
        self.ReadStandardActions()
        if self.bOnError:
            return False

        uOldHost:str = self.aIniSettings.uHost
        if self.aIniSettings.get("bSaveDiscoveredIP") is not None and self.aIniSettings.get("uOldDiscoveredIP") is not None:
            if self.aIniSettings.bSaveDiscoveredIP and self.aIniSettings.uOldDiscoveredIP != '' and self.aIniSettings.uHost== u'discover':
                self.aIniSettings.uHost=self.aIniSettings.uOldDiscoveredIP
                self.ShowDebug(uMsg="Reusing previous discovered IP:"+self.aIniSettings.uOldDiscoveredIP)
            elif self.aIniSettings.uHost==u'discover':
                bRet:bool = self.Discover()
                if not bRet:
                    if self.aIniSettings.uOldDiscoveredIP!="":
                        self.aIniSettings.uHost=self.aIniSettings.uOldDiscoveredIP
        if self.aIniSettings.uHost.startswith('linked:'):
            self.aIniSettings.uHost=self.oInterFace.oObjectConfig.GetSettingParFromVar(self.aIniSettings.uHost)
            self.ShowDebug(uMsg=u'Pulled crosslinked var: %s=%s' %(uOldHost,self.aIniSettings.uHost))

        if self.aIniSettings.uHost=="discover":
            return False

        return True

    def AddTrigger(self,uTrigger:str,uActionName:str,uRetVar:str,uGetVar:str) -> cBaseTrigger:
        """
        Adds a trigger

        :rtype: cBaseTrigger
        :param string uTrigger: The name of the trigger
        :param string uActionName: The Action the get triggered
        :param string uRetVar: The return var
        :param string uGetVar: The var to parse
        :return: The trigger
        """

        oTrigger:cBaseTrigger               = cBaseTrigger()
        oTrigger.uTriggerAction             = uActionName
        oTrigger.uRetVar                    = uRetVar
        oTrigger.uGetVar                    = uGetVar
        oTrigger.uTriggerName               = uTrigger
        oTrigger.uGlobalDestVar             = uRetVar
        oTrigger.uLocalDestVar              = uRetVar

        # If we link to a codesetcode setting
        '''
        if uGetVar.startswith(u'codesetcode:'):
            uActionName = self.MakeLocalActionName(uGetVar[12:])
            aActions = Globals.oActions.dActionsCommands.get(uActionName)
            if aActions is not None:
                oAction=aActions[0]
                if oAction.uGetVar != u'':
                    oTrigger.uGetVar=oAction.uGetVar
                if oAction.uGlobalDestVar != u'':
                    oTrigger.uRetVar = oAction.uGlobalDestVar
                oTrigger.uTriggerName = oAction.uCmd
        '''
        self.dTriggers[uTrigger] = oTrigger
        return self.AddTriggerNew(uTrigger,uActionName,uRetVar,uGetVar)
        return oTrigger

    def AddTriggerNew(self,uTrigger:str,uActionName:str,uRetVar:str,uGetVar:str) -> cBaseTrigger:
        """
        Adds a trigger

        :rtype: cBaseTrigger
        :param string uTrigger: The name of the trigger
        :param string uActionName: The Action to call
        :param string uRetVar: The return var
        :param string uGetVar: The var to parse
        :return: The trigger
        """

        oTrigger:cBaseTrigger               = cBaseTrigger()
        oTrigger.uTriggerAction             = uActionName
        oTrigger.uRetVar                    = uRetVar
        oTrigger.uGetVar                    = uGetVar
        oTrigger.uTriggerName               = uTrigger
        oTrigger.uGlobalDestVar             = uRetVar
        oTrigger.uLocalDestVar              = uRetVar

        aCurrentTriggers:List[cBaseTrigger]=self.dNewTriggers.get(uTrigger,[])
        aCurrentTriggers.append(oTrigger)
        self.dNewTriggers[uTrigger]=aCurrentTriggers
        return oTrigger

    def DelTrigger(self,uTrigger:str,uActionName:str) -> None:
        """
        deletes a trigger

        :param string uTrigger: The Name of the trigger to delete
        :param string uActionName: The Action which has been registered
        """

        oTrigger:cBaseTrigger               = cBaseTrigger()

        if uTrigger in self.dNewTriggers:
            aCurrentTriggers:List[cBaseTrigger]=self.dNewTriggers.get(uTrigger,[])
            aCurrentTriggers[:] = [oTrigger for oTrigger in aCurrentTriggers if oTrigger.uTriggerAction!=uActionName]

    def GetTrigger(self,uTrigger:str) -> List[cBaseTrigger]:
        """
        We do not use the index, as the uTrigger might not reflect the Trigger Name,
        it could be an Trigger parsed by the result eg defined by an codesetcode

        :param string uTrigger:
        :return:
        """

        aTriggers:List[cBaseTrigger]
        aResult:List[cBaseTrigger] = []
        oTrigger:cBaseTrigger

        for uTriggerIdx in self.dNewTriggers:
            aTriggers = self.dNewTriggers[uTriggerIdx]
            for oTrigger in aTriggers:
                if oTrigger.uTriggerName == uTrigger[:len(oTrigger.uTriggerName)]:
                    aResult.append(oTrigger)
        return aResult

    def CallTrigger(self,oTrigger:cBaseTrigger,uResponse:str) -> None:
        """
        calls a trigger

        :param cBaseTrigger oTrigger: The trigger object
        :param str uResponse: The response of the trigger action
        :return: None
        """
        # if oTrigger.uTriggerAction=='':
        #    self.ShowWarning(u'No Trigger Action defined for Trigger:' + oTrigger.uTriggerName)
        #    # return

        self.ShowDebug(uMsg=oTrigger.uTriggerName+":"u'Trigger Action:'+oTrigger.uTriggerAction)

        uCmd:str
        vRetVal:Union[str,Tuple]
        uRetVal:str
        oAction:Union[None,cAction] = None

        if oTrigger.uGetVar.startswith(u'codesetcode:'):
            uActionName:str = self.MakeLocalActionName(oTrigger.uGetVar[12:])
            aActions:List[cAction] = Globals.oActions.GetActionList(uActionName = uActionName, bNoCopy=False)
            if aActions is not None:
                oAction=aActions[0]
                if oAction.uGetVar != u'':
                    oTrigger.uGetVar=oAction.uGetVar
                if oAction.uGlobalDestVar != u'':
                    oTrigger.uRetVar = oAction.uGlobalDestVar
                oTrigger.uTriggerName = oAction.uCmd

        if oAction is None:
            if self.oAction:
                oAction = copy(self.oAction)
            else:
                oAction = copy(self.oLastAction)

        oAction.uActionName        = oTrigger.uTriggerAction
        oAction.uGetVar            = oTrigger.uGetVar
        oAction.uGlobalDestVar     = oTrigger.uRetVar

        #We call ParseResult to set the Values to proper Global Vars
        uCmd,vRetVal                = self.oInterFace.ParseResult(oAction,uResponse,self)
        if isinstance(vRetVal,tuple):
            uRetVal = vRetVal[0]
        else:
            uRetVal = vRetVal

        if oTrigger.uRetVar != u'' and uRetVal != u'':
            SetVar(uVarName = oTrigger.uRetVar, oVarValue = uRetVal)
        if oAction.uActionName != u'':
            aActions=Globals.oEvents.CreateSimpleActionList(aActions=[{'string':'call','actionname':oTrigger.uTriggerAction,'name':oAction.uActionName}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions,Globals.oTheScreen.oCurrentPage.oWidgetBackGround)


    def DeInit(self) -> None:
        """ Deinits the interfaces """
        Clock.unschedule(self.FktDisconnect)
        self.Disconnect()

    # noinspection PyUnusedLocal
    def FktDisconnect(self,*largs) -> None:
        """ Helper for scheduled (timed) disconnect """
        self.Disconnect()
    def Disconnect(self) -> bool:
        """ Basic disconnect function """
        self.ShowDebug(uMsg=u'Base Disconnect #1:Closing Connection')
        if not self.bIsConnected:
            return False
        self.ShowDebug(uMsg=u'Base Disconnect #2:Closing Connection')
        self.bIsConnected = False
        if self.bOnError:
            return False
        self.ShowDebug(uMsg=u'Closing Connection')
        Clock.unschedule(self.FktDisconnect)
        return True


    def GetTriggerOld(self,uTrigger:str) -> Union[cBaseTrigger,None]:
        """
        We do not use the index, as the uTrigger might not reflect the Trigger Name,
        it could be an Trigger parsed by the result eg defined by an codesetcode

        :param string uTrigger:
        :return:
        """

        for uTriggerIdx in self.dTriggers:
            oTrigger = self.dTriggers[uTriggerIdx]
            if oTrigger.uTriggerName == uTrigger[:len(oTrigger.uTriggerName)]:
                return oTrigger
        return None

    def DelTriggerOld(self,uTrigger:str) -> None:
        """
        deletes a trigger

        :param string uTrigger: The Name of the trigger to delete
        """

        if uTrigger in self.dTriggers:
            del self.dTriggers[uTrigger]
