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
from copy                                       import copy

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


__all__ = ['cBaseInterFaceSettings']

class cBaseInterFaceSettings(cBaseSettings):
    """ A base class for the interfacesettings """
    def __init__(self, oInterFace):
        # some default settings, which should be there even if not configered by the interface
        # use the exact spelling as in the settings json

        super(cBaseInterFaceSettings,self).__init__(oInterFace)

        self.oInterFace                                         = oInterFace
        self.uConfigName                                        = "DEVICE_DEFAULT"
        self.uType                                              = "interface"

        self.aIniSettings.bDisableInterFaceOnError              = False
        self.aIniSettings.bDisconnectInterFaceOnSleep           = True
        self.aIniSettings.fTimeOut                              = 1.0
        self.aIniSettings.iTimeToClose                          = -1
        self.aIniSettings.uFNCodeset                            = u''
        self.aIniSettings.uHost                                 = u'192.168.1.2'
        self.aIniSettings.uParseResultOption                    = u''
        self.aIniSettings.uParseResultTokenizeString            = u''
        self.aIniSettings.uPort                                 = u'80'
        self.aIniSettings.uResultEndString                      = u'\\n'
        self.aIniSettings.uDiscoverScriptName                   = u''
        self.bInConnect                                         = False
        self.bIsConnected                                       = False
        self.bResumeConnection                                  = False
        self.dTriggers                                          = {}
        self.iDiscoverCount                                     = 0
        self.iMaxDiscoverCount                                  = 1
        self.oAction                                            = None
        self.oLastAction                                        = None
        self.dStandardActions                                   = {"ping":None,"defaultresponse":None}
        self.bStandardActionsLoaded                             = False
        self.oResultParser                                      = None

    def ReadStandardActions(self):
        """ Reads the standard codeset codes eg ping """
        if not self.bStandardActionsLoaded:
            for uKey in self.dStandardActions:
                oAction = self.ReadStandardActions_sub(self.dStandardActions[uKey],uKey)
                if oAction:
                    self.dStandardActions[uKey]=oAction
                self.bStandardActionsLoaded=True

    def ReadStandardActions_sub(self,oTargetAction,uActionName):
        """
        Sub Routine to read the standard actions

        :param cAction|None oTargetAction: The Action for a standradextion, should be None as input
        :param string uActionName: The Actionname
        """

        if oTargetAction is None or oTargetAction==u'':
            aActions=Globals.oActions.GetActionList(uActionName = self.MakeLocalActionName(uActionName), bNoCopy=False)
            if aActions is not None:
                if len(aActions)==1:
                    return aActions[0]
                else:
                    Logger.error("StandardCodesetCodes can''t be multiline:"+uActionName)
        return None

    def ExecuteStandardAction(self,uActionName):
        """
        Executes as standard action

        :rtype: int
        :param string uActionName:
        :return: The return code of the action
        """

        aActions=Globals.oActions.GetActionList(uActionName = self.MakeLocalActionName(uActionName), bNoCopy = False)
        if aActions is not None:
            return Globals.oEvents.ExecuteActionsNewQueue(aActions, None, True)
        else:
            return 0

    def Discover(self,**kwargs):
        """ helper for the discover scripts"""

        if self.aIniSettings.uHost!="discover":
            return True

        self.iDiscoverCount += 1
        if self.iDiscoverCount > self.iMaxDiscoverCount:
            return False

        self.ShowDebug(u'Try to discover device')
        uDiscoverScriptName = self.aIniSettings.uDiscoverScriptName
        dParams={}

        for uKey in self.aIniSettings:
            if uKey[1:].startswith(uDiscoverScriptName.upper()):
                uParamKey=uKey[len(uDiscoverScriptName)+2:]
                dParams[uParamKey]=self.aIniSettings[uKey]

        dResult = Globals.oScripts.RunScript(uDiscoverScriptName, **dParams)
        oException = dResult.get('Exception','')
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
            self.ShowError(u'Can''t discover device:' + self.oInterFace.oObjectConfig.oFnConfig.string + u' Section:' + self.uSection, oException)
            return False

    def ReadCodeset(self):
        """  reads the codeset file """
        oCodesetFileName = self.oInterFace.FindCodesetFile(self.aIniSettings.uFNCodeset)

        if oCodesetFileName is None:
            self.ShowDebug(u'Cannot Read Codeset (Not Found):' + self.aIniSettings.uFNCodeset)
            return


        self.ShowDebug(u'Read Codeset:'+oCodesetFileName)

        if oCodesetFileName.Exists():
            sET_Data = CachedFile(oCodesetFileName)
            oET_Root = Orca_FromString(sET_Data,None,oCodesetFileName.string)
            Orca_include(oET_Root,orca_et_loader)
            aTmpCodeSetActions={}
            Globals.oActions.LoadActionsSub(oET_Root ,u'',u'action', aTmpCodeSetActions,oCodesetFileName.string)
            # replacing alias
            bDoItAgain=True
            uKey=u''
            uAlias=u''
            try:
                # replace all alias
                while bDoItAgain:
                    bDoItAgain=False
                    try:
                        for uKey in aTmpCodeSetActions:
                            iPos = -1
                            for oTmpCodeSetAction in aTmpCodeSetActions[uKey]:
                                iPos += 1
                                if oTmpCodeSetAction.dActionPars.get('type','')=="alias":
                                    uAlias=oTmpCodeSetAction.dActionPars['cmd']
                                    aAliasCodeSet=aTmpCodeSetActions[uAlias]
                                    if len(aAliasCodeSet)==1:
                                        oTmpCodeSetAction=copy(aAliasCodeSet[0])
                                        oTmpCodeSetAction.uActionName=uAlias
                                    else:
                                        oTmpCodeSetAction.uActionString="call"
                                        oTmpCodeSetAction.dActionPars["actionname"]=uAlias
                                        oTmpCodeSetAction.iActionId=GetActionID(oTmpCodeSetAction.uActionString)
                                        oTmpCodeSetAction.dActionPars["type"]=""

                                    aTmpCodeSetActions[uKey][iPos]=oTmpCodeSetAction
                                    bDoItAgain=True

                    except Exception as e:
                        uMsg = self.ShowError(u'Cannot read Codeset (wrong alias [%s=%s] CodesetFileName: %s):'% (uKey,uAlias,oCodesetFileName.string),e)
                        ShowErrorPopUp(uTitle='Error Reading Codeset',uMessage=uMsg)

                # Make calls local & Read the common attributes
                for  uKey in aTmpCodeSetActions:
                    for aTmpCodeSetAction in aTmpCodeSetActions[uKey]:
                        if aTmpCodeSetAction.iActionId==Globals.oActions.oActionType.Call:
                            uActionName=aTmpCodeSetAction.dActionPars.get("actionname","")
                            if uActionName in aTmpCodeSetActions:
                                aTmpCodeSetAction.dActionPars["actionname"] = self.MakeLocalActionName(uActionName)
                        self.ReadAction(aTmpCodeSetAction)

                # add them to the global action list
                for  uKey in aTmpCodeSetActions:
                    Globals.oActions.SetActionList(self.MakeLocalActionName(uKey),aTmpCodeSetActions[uKey])

            except Exception as e:
                uMsg = self.ShowError(u'Cannot read Codeset :',e)
                ShowErrorPopUp(uTitle='Error Reading Codeset',uMessage=uMsg)

            self.SetContextVar("firstcall","1")

    def ReadAction(self,oAction):
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
        oAction.uResultEndString            = oAction.dActionPars.get(u'parseendstring',    self.aIniSettings.uResultEndString)

        oAction.dActionPars['interface']  = self.oInterFace.uObjectName
        oAction.dActionPars['configname'] = self.uConfigName

        if oAction.dActionPars.get('varcontext','')=="codeset":
            oAction.dActionPars["varcontext"]=self.uContext

    def MakeLocalActionName(self,uActionName):
        """
        Creates a (codeset) local version of an action

        :param uActionName:
        :return:
        """
        return uActionName+" :"+self.uContext

    def Connect(self):
        """ basic helper for managing connect """
        if self.bOnError:
            self.ShowDebug(u'Interface Connect: Interface is on Error, setting interface to disconnected')
            self.bIsConnected=False
        if not self.aIniSettings.bDisableInterFaceOnError:
            self.bOnError=False
        if self.bIsConnected:
            self.ShowDebug(u'Interface Connect: Interface is connected, no connect required.')
            return False
        self.ReadStandardActions()
        if self.bOnError:
            return False

        uOldHost=self.aIniSettings.uHost
        if self.aIniSettings.get("bSaveDiscoveredIP") is not None and self.aIniSettings.get("uOldDiscoveredIP") is not None:
            if self.aIniSettings.bSaveDiscoveredIP and self.aIniSettings.uOldDiscoveredIP != '' and self.aIniSettings.uHost== u'discover':
                self.aIniSettings.uHost=self.aIniSettings.uOldDiscoveredIP
                self.ShowDebug("Reusing previous discovered IP:"+self.aIniSettings.uOldDiscoveredIP)
            elif self.aIniSettings.uHost==u'discover':
                bRet=self.Discover()
                if not bRet:
                    if self.aIniSettings.uOldDiscoveredIP!="":
                        self.aIniSettings.uHost=self.aIniSettings.uOldDiscoveredIP
        if self.aIniSettings.uHost.startswith('linked:'):
            self.aIniSettings.uHost=self.oInterFace.oObjectConfig.GetSettingParFromVar(self.aIniSettings.uHost)
            self.ShowDebug(u'Pulled crosslinked var: %s=%s' %(uOldHost,self.aIniSettings.uHost))

        if self.aIniSettings.uHost=="discover":
            return False

        return True

    def AddTrigger(self,uTrigger,uActionName,uRetVar,uGetVar):
        """
        Adds a trigger

        :rtype: cBaseTrigger
        :param string uTrigger: The name of the trigger
        :param string uActionName: The Action the get triggered
        :param string uRetVar: The return var
        :param string uGetVar: The var to parse
        :return: The trigger
        """

        oTrigger                = cBaseTrigger()
        oTrigger.uTriggerAction = uActionName
        oTrigger.uRetVar        = uRetVar
        oTrigger.uGetVar        = uGetVar
        oTrigger.uTriggerName   = uTrigger
        oTrigger.uGlobalDestVar = uRetVar
        oTrigger.uLocalDestVar  = uRetVar

        # If we link to an codsetcode setting
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
        return oTrigger

    def DelTrigger(self,uTrigger):
        """
        deletes a trigger

        :param string uTrigger: The Name of the trigger to delete
        """

        if uTrigger in self.dTriggers:
            del self.dTriggers[uTrigger]

    def GetTrigger(self,uTrigger):
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

    def CallTrigger(self,oTrigger,uResponse):
        """
        calls a trigger

        :param cBaseTrigger oTrigger: The trigger object
        :param string uResponse: The response of the trigger action
        :return: None
        """
        # if oTrigger.uTriggerAction=='':
        #    self.ShowWarning(u'No Trigger Action defined for Trigger:' + oTrigger.uTriggerName)
        #    # return

        self.ShowDebug(oTrigger.uTriggerName+":"u'Trigger Action:'+oTrigger.uTriggerAction)

        oAction = None

        if oTrigger.uGetVar.startswith(u'codesetcode:'):
            uActionName = self.MakeLocalActionName(oTrigger.uGetVar[12:])
            aActions = Globals.oActions.GetActionList(uActionName = uActionName, bNoCopy=False)
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
        uCmd,uRetVal                = self.oInterFace.ParseResult(oAction,uResponse,self)
        if isinstance(uRetVal,tuple):
            uRetVal=uRetVal[0]

        if oTrigger.uRetVar != u'' and uRetVal != u'':
            SetVar(uVarName = oTrigger.uRetVar, oVarValue = uRetVal)
        if oAction.uActionName != u'':
            aActions=Globals.oEvents.CreateSimpleActionList([{'string':'call','actionname':oTrigger.uTriggerAction,'name':oAction.uActionName}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions,Globals.oTheScreen.oCurrentPage.oWidgetBackGround)


    def DeInit(self):
        """ Deinits the interfaces """
        Clock.unschedule(self.FktDisconnect)
        self.Disconnect()
    def FktDisconnect(self,*largs):
        """ Helper for scheduled (timed) disconnect """
        self.Disconnect()
    def Disconnect(self):
        """ Basic disconnect function """
        self.ShowDebug(u'Base Disconnect #1:Closing Connection')
        if not self.bIsConnected:
            return False
        self.ShowDebug(u'Base Disconnect #2:Closing Connection')
        self.bIsConnected = False
        if self.bOnError:
            return False
        self.ShowDebug(u'Closing Connection')
        Clock.unschedule(self.FktDisconnect)
        return True
