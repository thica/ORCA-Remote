# -*- coding: utf-8 -*-
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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

from copy                                       import copy
from xml.etree.ElementTree                      import Element

from kivy.logger                                import Logger
from kivy.clock                                 import Clock

from ORCA.Globals                               import Globals
from ORCA.action.Action import GetActionID
from ORCA.action.Action import cAction
from ORCA.interfaces.BaseTrigger                import cBaseTrigger
from ORCA.interfaces.BaseTrigger                import dTriggers

from ORCA.settings.BaseSettings import cBaseSettings
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
    cBaseInterFace = TypeVar('cBaseInterFace')
    cInterFaceResultParser = TypeVar('cInterFaceResultParser')

dRefTriggers:Dict = {} # just a reference, to avoid duplicate triggers


__all__ = ['cBaseInterFaceSettings']

class cBaseInterFaceSettings(cBaseSettings):
    """ A base class for the interfacesettings """
    def __init__(self, oInterFace):
        # some default settings, which should be there even if not configered by the interface
        # use the exact spelling as in the settings json

        super().__init__(oInterFace)

        self.oInterFace:cBaseInterFace                          = oInterFace
        self.uConfigName:str                                    = 'DEVICE_DEFAULT'
        self.uType:str                                          = 'interface'

        self.aIniSettings.bDisableInterFaceOnError              = False
        self.aIniSettings.bDisconnectInterFaceOnSleep           = True
        self.aIniSettings.fTimeOut                              = 1.0
        self.aIniSettings.iTimeToClose                          = -1
        self.aIniSettings.uFNCodeset                            = ''
        self.aIniSettings.uHost                                 = '192.168.1.2'
        self.aIniSettings.uParseResultOption                    = ''
        self.aIniSettings.uParseResultTokenizeString            = ''
        self.aIniSettings.uParseResultFlags                     = ''
        self.aIniSettings.uPort                                 = '80'
        self.aIniSettings.uResultEndString                      = '\\n'
        self.aIniSettings.uDiscoverScriptName                   = ''
        self.bInConnect:bool                                    = False
        self.bIsConnected:bool                                  = False
        self.bResumeConnection:bool                             = False
        self.iDiscoverCount:int                                 = 0
        self.iMaxDiscoverCount:int                              = 1
        self.oAction:Union[cAction,None]                        = None
        self.oLastAction:Union[cAction,None]                    = None
        self.dStandardActions:Dict[str,Union[cAction,None]]     = {'ping':None,'defaultresponse':None}
        self.bStandardActionsLoaded:bool                        = False
        self.oResultParser:Union[cInterFaceResultParser,None]   = None

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

        :param cAction|None oTargetAction: The Action for a standard action, should be None as input
        :param str uActionName: The Actionname
        """

        if oTargetAction is None or oTargetAction=='':
            aActions:List[cAction] = Globals.oActions.GetActionList(uActionName = self.MakeLocalActionName(uActionName), bNoCopy=False)
            if aActions is not None:
                if len(aActions)==1:
                    return aActions[0]
                else:
                    Logger.error('StandardCodesetCodes can\'t be multiline:'+uActionName)
        return None

    def ExecuteStandardAction(self,uActionName:str) -> int:
        """
        Executes as standard action

        :param string uActionName:
        :return: The return code of the action
        """

        aActions:List[cAction]=Globals.oActions.GetActionList(uActionName = self.MakeLocalActionName(uActionName), bNoCopy = False)
        if aActions is not None:
            return Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions, oParentWidget=None, bForce=True,uQueueName="readstandardactions")
        else:
            return 0

    # noinspection PyUnusedLocal
    def Discover(self,**kwargs) -> bool:
        """ helper for the discover scripts"""

        if self.aIniSettings.uHost!='discover':
            return True

        self.iDiscoverCount += 1
        if self.iDiscoverCount > self.iMaxDiscoverCount:
            return False

        self.ShowDebug(uMsg='Try to discover device')
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
                if uKey == 'Host' and dResult.get('Hostname','')=='':
                    if self.aIniSettings.bSaveDiscoveredIP:
                        self.oInterFace.oObjectConfig.oConfigParser.set(self.uSection, 'olddiscoveredip', self.aIniSettings.uHost)
                        self.oInterFace.oObjectConfig.oConfigParser.write()
                if uKey == 'Hostname' and dResult.get('Hostname','')!='':
                    self.aIniSettings['Host']=dResult[uKey]
                    if self.aIniSettings.bSaveDiscoveredIP:
                        self.oInterFace.oObjectConfig.oConfigParser.set(self.uSection, 'olddiscoveredip', self.aIniSettings.uHostname)
                        self.oInterFace.oObjectConfig.oConfigParser.write()

            return True
        else:
            self.ShowError(uMsg=f'Can\'t discover device: {self.oInterFace.oObjectConfig.oFnConfig} Section: {self.uSection}', oException=oException)
            return False

    def ReadCodeset(self) -> None:
        """  reads the codeset file """

        oTmpCodeSetAction:cAction
        aTmpCodeSetAction:List[cAction]

        oCodesetFileName:cFileName = self.oInterFace.FindCodesetFile(self.aIniSettings.uFNCodeset)

        if oCodesetFileName is None:
            self.ShowDebug(uMsg='Cannot Read Codeset (Not Found):' + self.aIniSettings.uFNCodeset)
            return

        self.ShowDebug(uMsg=f'Read Codeset: {oCodesetFileName.string}')

        if oCodesetFileName.Exists():
            uET_Data:str     = CachedFile(oFileName=oCodesetFileName)
            oET_Root:Element = Orca_FromString(uET_Data=uET_Data,oDef=None,uFileName=str(oCodesetFileName))
            Orca_include(oET_Root,orca_et_loader)
            dTmpCodeSetActions:Dict[str,List[cAction]] = {}
            Globals.oActions.LoadActionsSub(oET_Root=oET_Root ,uSegmentTag='',uListTag='action', dTargetDic=dTmpCodeSetActions,uFileName=str(oCodesetFileName))
            # replacing alias
            bDoItAgain:bool = True
            uKey:str        = ''
            uAlias:str      = ''

            try:
                # replace all alias
                while bDoItAgain:
                    bDoItAgain=False
                    try:
                        for uKey in dTmpCodeSetActions:
                            iPos:int = -1
                            for oTmpCodeSetAction in dTmpCodeSetActions[uKey]:
                                iPos += 1
                                if oTmpCodeSetAction.dActionPars.get('type','')=='alias':
                                    uAlias:str = oTmpCodeSetAction.dActionPars['cmd']
                                    aAliasCodeSet:List[cAction] = dTmpCodeSetActions[uAlias]
                                    if len(aAliasCodeSet)==1:
                                        oTmpCodeSetAction = copy(aAliasCodeSet[0])
                                        oTmpCodeSetAction.uActionName= uAlias
                                    else:
                                        oTmpCodeSetAction.uActionString='call'
                                        oTmpCodeSetAction.dActionPars['actionname']=uAlias
                                        oTmpCodeSetAction.iActionId=GetActionID(oTmpCodeSetAction.uActionString)
                                        oTmpCodeSetAction.dActionPars['type']=''

                                    dTmpCodeSetActions[uKey][iPos]=oTmpCodeSetAction
                                    bDoItAgain=True

                    except Exception as e:
                        uMsg:str = self.ShowError(uMsg=f'Can\'t read codeset (wrong alias [{uKey}={uAlias}] CodesetFileName: {oCodesetFileName}):', oException=e)
                        ShowErrorPopUp(uTitle='Error reading codeset',uMessage=uMsg)

                # Make calls local & Read the common attributes
                for  uKey in dTmpCodeSetActions:
                    for oTmpCodeSetAction in dTmpCodeSetActions[uKey]:
                        if oTmpCodeSetAction.iActionId==Globals.oActions.oActionType.Call:
                            uActionName:str = oTmpCodeSetAction.dActionPars.get('actionname','')
                            if uActionName in dTmpCodeSetActions:
                                oTmpCodeSetAction.dActionPars['actionname'] = self.MakeLocalActionName(uActionName)
                        self.ReadAction(oTmpCodeSetAction)

                # add them to the global action list
                for  uKey in dTmpCodeSetActions:
                    Globals.oActions.SetActionList(self.MakeLocalActionName(uKey),dTmpCodeSetActions[uKey])

            except Exception as e:
                uMsg:str = self.ShowError(uMsg='Can\'t read codeset :',oException=e)
                ShowErrorPopUp(uTitle='Error reading codeset',uMessage=uMsg)

            self.SetContextVar(uVarName='firstcall',uVarValue='1')

    def ReadAction(self,oAction:cAction) -> None:
        """
        Adds and defaults some common attributes to the action

        :param cAction oAction: Reads an action from the action pars
        """

        oAction.uType                       = oAction.dActionPars.get('type',              'send')
        oAction.uCmd                        = oAction.dActionPars.get('cmd',               'No cmd action defined')
        oAction.uLocalDestVar               = oAction.dActionPars.get('ldestvar',          'RESULT_' + oAction.uActionName)
        oAction.uGlobalDestVar              = oAction.dActionPars.get('gdestvar',          'RESULT_' + oAction.uActionName)
        oAction.uGetVar                     = oAction.dActionPars.get('getvar',            '')
        oAction.bWaitForResponse            = ToBool(oAction.dActionPars.get('waitforresponse',   '0'))
        oAction.uParseResultOption          = oAction.dActionPars.get('parseoption',       self.aIniSettings.uParseResultOption)
        oAction.uParseResultTokenizeString  = oAction.dActionPars.get('parsetoken',        self.aIniSettings.uParseResultTokenizeString)
        oAction.uParseResultFlags           = oAction.dActionPars.get('parseflags',        self.aIniSettings.uParseResultFlags)
        oAction.uResultEndString            = oAction.dActionPars.get('parseendstring',    self.aIniSettings.uResultEndString)

        oAction.dActionPars['interface']  = self.oInterFace.uObjectName
        oAction.dActionPars['configname'] = self.uConfigName

        if oAction.dActionPars.get('varcontext','')=='codeset':
            oAction.dActionPars['varcontext']=self.uContext

    def MakeLocalActionName(self,uActionName:str) -> str:
        """
        Creates a (codeset) local version of an action

        :param uActionName:
        :return:
        """
        return uActionName+' :'+self.uContext

    def Connect(self) -> bool:
        """ basic helper for managing connect """
        if self.bOnError:
            self.ShowDebug(uMsg='Interface Connect: Interface is on Error, setting interface to disconnected')
            self.bIsConnected=False
        if not self.aIniSettings.bDisableInterFaceOnError:
            self.bOnError=False
        if self.bIsConnected:
            self.ShowDebug(uMsg='Interface Connect: Interface is connected, no connect required.')
            return False
        self.ReadStandardActions()
        if self.bOnError:
            return False

        uOldHost:str = self.aIniSettings.uHost
        if self.aIniSettings.get('bSaveDiscoveredIP') is not None and self.aIniSettings.get('uOldDiscoveredIP') is not None:
            if self.aIniSettings.bSaveDiscoveredIP and self.aIniSettings.uOldDiscoveredIP != '' and self.aIniSettings.uHost== 'discover':
                self.aIniSettings.uHost=self.aIniSettings.uOldDiscoveredIP
                self.ShowDebug(uMsg='Reusing previous discovered IP:'+self.aIniSettings.uOldDiscoveredIP)
            elif self.aIniSettings.uHost=='discover':
                bRet:bool = self.Discover()
                if not bRet:
                    if self.aIniSettings.uOldDiscoveredIP!='':
                        self.aIniSettings.uHost=self.aIniSettings.uOldDiscoveredIP
        if self.aIniSettings.uHost.startswith('linked:'):
            self.aIniSettings.uHost=self.oInterFace.oObjectConfig.GetSettingParFromVar(self.aIniSettings.uHost)
            self.ShowDebug(uMsg=f'Pulled crosslinked var: {uOldHost}={self.aIniSettings.uHost}')

        if self.aIniSettings.uHost=='discover':
            return False

        return True

    @classmethod
    def CreateTriggerReference(cls,*,uTrigger:str,uActionName:str) -> str:
        return f"TriggerName:{uTrigger}_ActionName:{uActionName}"


    def AddTrigger(self,uTrigger:str,uActionName:str,uRetVar:str,uGetVar:str) -> cBaseTrigger:
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
        oTrigger.uInterfaceName             = self.oInterFace.uObjectName
        oTrigger.uConfigName                = self.uConfigName
        uRefTrigger:str                     = self.CreateTriggerReference(uTrigger=uTrigger,uActionName=uActionName)

        if uRefTrigger in dRefTriggers:
            self.DelTrigger(uTrigger=uTrigger,uActionName=uActionName)

        aCurrentTriggers:List[cBaseTrigger] = dTriggers.get(uTrigger,[])
        aCurrentTriggers.append(oTrigger)

        #todo: this is debug only, need to be removed in release
        if len(aCurrentTriggers)>1:
            self.ShowError(uMsg=f"Multiple Trigger detected {uTrigger}",oException=None)
        #     del aCurrentTriggers[1:]

        dTriggers[uTrigger]=aCurrentTriggers
        dRefTriggers[uRefTrigger]=oTrigger
        return oTrigger

    def DelTrigger(self,uTrigger:str,uActionName:str) -> None:
        """
        deletes a trigger

        :param string uTrigger: The Name of the trigger to delete
        :param string uActionName: The Action which has been registered
        """

        oTrigger:cBaseTrigger
        uRefTrigger:str

        if uTrigger in dTriggers:
            aCurrentTriggers:List[cBaseTrigger] = dTriggers.get(uTrigger,[])
            for oTrigger in aCurrentTriggers:
                if oTrigger.uTriggerAction == uActionName:
                    aCurrentTriggers.remove(oTrigger)
                    uRefTrigger = self.CreateTriggerReference(uTrigger=oTrigger.uTriggerName,uActionName=oTrigger.uTriggerAction)
                    dRefTriggers.pop(uRefTrigger)
            dTriggers[uTrigger] = aCurrentTriggers

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

        for uTriggerIdx in dTriggers:
            aTriggers = dTriggers[uTriggerIdx]
            for oTrigger in aTriggers:
                if oTrigger.uTriggerName == uTrigger[:len(oTrigger.uTriggerName)]:
                    if oTrigger.uInterfaceName == self.oInterFace.uObjectName:
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
        #    self.ShowWarning('No Trigger Action defined for Trigger:' + oTrigger.uTriggerName)
        #    # return

        self.ShowDebug(uMsg=oTrigger.uTriggerName+':Trigger Action:'+oTrigger.uTriggerAction)

        uCmd:str
        vRetVal:Union[str,Tuple]
        uRetVal:str
        oAction:Union[None,cAction] = None

        if oTrigger.uGetVar.startswith('codesetcode:'):
            uActionName:str = self.MakeLocalActionName(oTrigger.uGetVar[12:])
            aActions:List[cAction] = Globals.oActions.GetActionList(uActionName = uActionName, bNoCopy=False)
            if aActions is not None:
                oAction=aActions[0]
                if oAction.uGetVar != '':
                    oTrigger.uGetVar=oAction.uGetVar
                if oAction.uGlobalDestVar != '':
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

        if oTrigger.uRetVar != '' and uRetVal != '':
            SetVar(uVarName = oTrigger.uRetVar, oVarValue = uRetVal)
        if oAction.uActionName != '':
            aActions=Globals.oEvents.CreateSimpleActionList(aActions=[{'string':'call','actionname':oTrigger.uTriggerAction,'name':oAction.uActionName}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=Globals.oTheScreen.oCurrentPage.oWidgetBackGround,uQueueName="calltrigger")

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
        self.ShowDebug(uMsg='Base Disconnect #1:Closing Connection')
        if not self.bIsConnected:
            return False
        self.ShowDebug(uMsg='Base Disconnect #2:Closing Connection')
        self.bIsConnected = False
        if self.bOnError:
            return False
        self.ShowDebug(uMsg='Closing Connection')
        Clock.unschedule(self.FktDisconnect)
        return True

