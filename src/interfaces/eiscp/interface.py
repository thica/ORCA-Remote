# -*- coding: utf-8 -*-
#  Onkyo eiscp
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

from __future__                            import annotations
from typing                                import Dict
from typing                                import List
from typing                                import Tuple
from typing                                import Optional
from typing                                import Union
from typing                                import cast
from typing                                import TYPE_CHECKING
from time                                  import sleep
from threading                             import Thread
from threading                             import currentThread
from copy                                  import copy

import select
import socket
import binascii

from kivy.logger                           import Logger
from kivy.network.urlrequest               import UrlRequest
from ORCA.interfaces.BaseInterface         import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
from ORCA.interfaces.BaseTrigger           import cBaseTrigger
from ORCA.vars.Replace                     import ReplaceVars
from ORCA.vars.Access                      import SetVar
from ORCA.vars.Actions                     import Var_Int2Hex
from ORCA.utils.TypeConvert                import ToUnicode
from ORCA.utils.TypeConvert                import ToBytes

from ORCA.utils.wait.StartWait             import StartWait
from ORCA.utils.FileName                   import cFileName
from ORCA.action.Action import cAction
from ORCA.actions.ReturnCode               import eReturnCode
from ORCA.Globals import Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Onkyo EISCP (LAN)</name>
      <description language='English'>Onkyo EISCP Interface (LAN/IP)</description>
      <description language='German'>Onkyo EISCP Interface (LAN/IP)</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/eiscp</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/eiscp.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>EISCP Discover</name>
        </dependency>
      </dependencies>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''



# noinspection PyMethodMayBeStatic
class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):
        def __init__(self,oInterFace):
            super().__init__(oInterFace)
            #cBaseInterFaceSettings.__init__(self,oInterFace)
            self.oSocket:Optional[socket.socket]            = None
            self.uMsg:str                                   = ''
            self.iBufferSize:int                            = 2048

            self.bHeader:bytes                              = b'ISCP'
            self.iHeaderSize:int                            = 16
            self.iVersion:int                               = 1
            self.bStopThreadEvent:bool                      = False
            self.uRetVar:str                                = ''
            self.dResponseActions:Dict                      = {}
            self.bBusy:bool                                 = False

            self.aIniSettings.uHost                         = 'discover'
            self.aIniSettings.uPort                         = '60128'
            self.aIniSettings.uFNCodeset                    = 'CODESET_eiscp_ONKYO_AVR.xml'
            self.aIniSettings.fTimeOut                      = 2.0
            self.aIniSettings.iTimeToClose                  = -1
            self.aIniSettings.uDiscoverScriptName           = 'discover_eiscp'
            self.aIniSettings.uParseResultOption            = 'store'
            self.aIniSettings.fDISCOVER_EISCP_timeout       = 2.0
            self.aIniSettings.uDISCOVER_EISCP_models        = ''
            self.aIniSettings.uDISCOVER_UPNP_servicetypes   = 'upnp:rootdevice'
            self.aIniSettings.uDISCOVER_UPNP_manufacturer   = 'Onkyo & Pioneer Corporation'
            self.oThread                                    = None

        def Connect(self) -> bool:

            if self.oResultParser is None:
                # Initiate Resultparser
                self.oInterFace.ParseResult(cAction(),'',self)

            # if not cBaseInterFaceSettings.Connect(self):

            if not super().Connect():
                return False

            self.bIsConnected = False

            if (self.aIniSettings.uHost=='') or (self.aIniSettings.uPort==''):
                self.ShowError(uMsg='Cannot connect on empty host or port ')
                self.bOnError=True
                return False

            try:
                self.oSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.oSocket.setblocking(False)
                self.oSocket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.oSocket.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.oSocket.settimeout(self.aIniSettings.fTimeOut)
                self.oSocket.connect((str(self.aIniSettings.uHost),int(self.aIniSettings.uPort)))

                if self.oThread:
                    self.bStopThreadEvent = True
                    self.oThread.join()
                    self.oThread = None

                if self.oThread is None:
                    self.oThread = Thread(target = self.Receive,)
                self.bStopThreadEvent = False
                self.oThread.oParent = self
                self.oThread.start()
            except socket.error as e:
                self.ShowError(uMsg='Cannot open socket:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,oException=e)
                self.oSocket.close()
                self.oSocket = None
            except Exception as e:
                self.ShowError(uMsg='Cannot open socket#2:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,oException=e)
                self.bOnError=True

            if self.oSocket is None:
                self.bOnError=True
                return False

            self.bIsConnected =True
            return self.bIsConnected

        def Disconnect(self) -> bool:

            if self.oThread:
                self.bStopThreadEvent = True
                self.oThread.join()
                self.oThread = None

            if not super().Disconnect():
                return False

            self.bOnError = False
            return True

        def CreateEISPHeader(self,uCmd:str) -> bytes:
            """
            Creates an EISP Header for the given command and and adds the command
            :param str uCmd: The
            :return: The Header plus command
            """
            # struct.pack doesnt not work reliable on all Android Platform processors
            # bMessage = pack('!4sIIBxxx', self.bHeader, self.iHeaderSize, iDataSize, self.iVersion) + ToBytes(uMessage)

            uMessage:str        = '!' + str(self.aIniSettings.iUnitType) + uCmd + '\x0a'
            iDataSize:int       =  len(uMessage)
            iReserved:int       = 0
            bHeaderSize:bytes   = self.iHeaderSize.to_bytes(4, byteorder='big')
            bDataSize:bytes     = iDataSize.to_bytes(4, byteorder='big')
            bVersion:bytes      = self.iVersion.to_bytes(1, byteorder='big')
            bReserved:bytes     = iReserved.to_bytes(3, byteorder='big')
            bMessage:bytes      = self.bHeader+bHeaderSize+bDataSize+bVersion+bReserved+ToBytes(uMessage)
            return bMessage

        def UnpackEISPResponse(self,byResponseIn:bytes) -> Tuple[str,str]:

            byResponse:bytes=b''

            if len(byResponseIn)==0:
                return '', ''

            try:
                byHeaderRet = byResponseIn[0:4]
                # iHeaderSize = int.from_bytes(byResponseIn[4:8], byteorder='big', signed=False) # we dont need it
                iDataSize   = int.from_bytes(byResponseIn[8:12], byteorder='big', signed=False)
                iVersionRet = byResponseIn[12]
                # struct.unpack doesnt not work reliable on all Android Platform processors
                # byHeaderRet, iHeaderSize, iDataSize, iVersionRet = unpack('!4sIIBxxx', byResponseIn[0:self.iHeaderSize])
                if byHeaderRet != self.bHeader:
                    self.ShowDebug(uMsg='Received packet not ISCP: '+ToUnicode(byHeaderRet))
                    return '',''
                if iVersionRet != self.iVersion:
                    self.ShowDebug(uMsg='ISCP version not supported: '+ToUnicode(iVersionRet))
                    return '',''
                if len(byResponseIn)==16:
                    byResponse=self.Helper_ReceiveAll(self.oSocket,iDataSize)
                else:
                    byResponse= byResponseIn[17:]
                if byResponse:
                    uMessage        = byResponse.decode('utf-8').rstrip('\x1a\r\n')
                    iMessageSize    = len(uMessage)
                    # parse message
                    # sUnitType     = uMessage[1]
                    uCommand        = ToUnicode(uMessage[2:5])
                    uParameter      = uMessage[5:iMessageSize]
                    return uCommand,uParameter
                else:
                    self.ShowDebug(uMsg='Got empty response: '+ToUnicode(byResponseIn))
                    return "", ""
            except Exception as e:
                self.ShowError(uMsg='Cannot parse response:'+ToUnicode(byResponse)+':'+ToUnicode(byResponseIn),oException=e)
                return '',''

        def Helper_ReceiveAll(self, oSocket:socket.socket, iSize:int) -> bytes:
            # Helper function to recv n bytes or return None if EOF is hit
            # As windows is ignoring the select timeout we need to ignore the errors

            byData:bytes = bytes()
            byPacket:bytes

            try:
                while len(byData) < iSize:
                    iMissing:int = iSize - len(byData)
                    byPacket = oSocket.recv(iMissing)
                    if not byPacket:
                        if len(byData)>0:
                            self.ShowError(uMsg='Can\t get complete response 1 ({0}) ({1!r})'.format(iMissing,byData) )
                        return byData
                    byData += byPacket
                return byData
            except Exception as e:
                self.ShowError(uMsg='ReceiveAll:Can\'t receive response 2',oException=e)
                return byData

        def Receive(self):

            # Main Listening Thread to receive eiscp messages
            # self (the settings object) is not reliable passed , to we use it passed from the Thread object

            oThread = currentThread()
            # noinspection PyUnresolvedReferences
            oParent:cInterFaceSettings = oThread.oParent
            aReadSocket:List
            aWriteSocket:List
            aExceptional:List
            uCommand:str
            uResponse:str
            oTmpAction:Union[cBaseTrigger,cAction]
            aTmpAction:List[Union[cBaseTrigger,cAction]] = []
            aActionTrigger:Optional[List[cBaseTrigger]]

            #Loop until closed by external flag
            try:
                while not oParent.bStopThreadEvent:
                    if oParent.oSocket is not None:

                        # on Windows, the timeout does not work, (known error)
                        # which means the the receiveall will run on error, so we need to skip the error message
                        aReadSocket, aWriteSocket, aExceptional = select.select([oParent.oSocket],[],[],0.1)

                        if len(aReadSocket) >0 and aReadSocket[0]:

                            i:int = 0
                            while self.bBusy:
                                sleep(0.01)
                                i += 1
                                if i > 200:
                                    oParent.ShowError(uMsg="Busy Time Out")
                                    self.bBusy = False
                            self.bBusy = True

                            byResponseHeader:bytes = oParent.Helper_ReceiveAll(aReadSocket[0], 16)
                            # noinspection PyInterpreter
                            if len(byResponseHeader)>0:
                                # Get the Command and the payload
                                uCommand,uResponse=oParent.UnpackEISPResponse(byResponseHeader)

                                # print ('Receive:',uCommand,':',uResponse)

                                # This returns ASCII of sResponse, we will convert it one line later
                                # we might get a response without dedicated requesting it, so lets use an action
                                # from previous request to get the return vars

                                bHandleSpecialResponse:bool = False
                                # Default is the last action (That is the command, where we MIGHT get the response from
                                del aTmpAction[:]
                                aTmpAction.append(self.oAction)

                                if uCommand == self.uMsg[:3]:
                                    # if we have a response to the last action, lets store the action for future use
                                    # in case we got a response without requesting it
                                    # Not 100% logic, but should fit in 99.9 % of the cases
                                    if len(oParent.GetTrigger(uCommand))==0:
                                        oParent.dResponseActions[uCommand] = copy(aTmpAction[0])
                                        bHandleSpecialResponse = True

                                # Lets check , if we have a trigger set for unrequested responses
                                aActionTrigger = oParent.GetTrigger(uCommand)

                                if len(aActionTrigger)>0:
                                    aTmpAction=aActionTrigger
                                    bHandleSpecialResponse = True
                                elif not bHandleSpecialResponse:
                                    # If we don't have an trigger and its not a response to the action
                                    # lets use the stored action, if we have it
                                    if uCommand in oParent.dResponseActions:
                                        aTmpAction[0] = oParent.dResponseActions[uCommand]
                                        bHandleSpecialResponse = True

                                if bHandleSpecialResponse:
                                    if uCommand=='NLS':
                                        # This might return an adjusted Response
                                        # We don't support multiple triggers on NLS so we just take the first action
                                        uCommand,uResponse=oParent.oInterFace.Handle_NLS(aTmpAction[0],uResponse,self)
                                # uResponse=ToUnicode(uResponse)
                                if bHandleSpecialResponse:
                                    if uCommand == 'NRI':
                                        for oTmpAction in aTmpAction:
                                            oParent.oInterFace.Handle_NRI(oTmpAction, uResponse, oParent)
                                    elif uCommand=='NJA':
                                        # multiple trigger on jacket infos (the picture split into multiple parts) not supported
                                        uCommand,uResponse=oParent.oInterFace.Handle_NJA(aTmpAction[0],uResponse,oParent)
                                    elif uCommand=='LMD':
                                        uResponse=oParent.oInterFace.ISCP_LMD_To_Text(uResponse)
                                    elif uCommand=='IFA':
                                        for oTmpAction in aTmpAction:
                                            oParent.oInterFace.Split_IFA(oTmpAction,uResponse,oParent)
                                    elif uCommand=='IFV':
                                        for oTmpAction in aTmpAction:
                                            oParent.oInterFace.Split_IFV(oTmpAction,uResponse,oParent)
                                    elif uCommand=='MVL' or uCommand=='CTL' or uCommand=='SWL':
                                        if uResponse!='N/A':
                                            uResponse=str(int(uResponse, 16))
                                # If the returned Command is a response to the send message
                                if uCommand==oParent.uMsg[:3]:
                                    #uCmd,uRetVal=self.oInterFace.ParseResult(self.oAction,uResponse,self)
                                    uRetVal:str = ''
                                    if not oParent.uRetVar=='':
                                        uTmp=oParent.oAction.uGlobalDestVar
                                        oParent.oAction.uGlobalDestVar=oParent.uRetVar
                                        uCmd,uRetVal=oParent.oInterFace.ParseResult(oParent.oAction,uResponse,oParent)
                                        oParent.oAction.uGlobalDestVar=uTmp
                                    if not oParent.uRetVar=='' and not uRetVal=='':
                                        SetVar(uVarName = self.uRetVar, oVarValue = uRetVal)

                                    # we got our response, all other responses are for somebody else
                                    #self.uMsg=''
                                # we have a notification issued by the device, so lets have a look, if we have a trigger code to it
                                aActionTrigger=oParent.GetTrigger(uCommand)

                                if len(aActionTrigger)>0:
                                    oParent.ShowInfo(uMsg='Calling Trigger for:' + uCommand)
                                    for oActionTrigger in aActionTrigger:
                                        if uResponse!="N/A":
                                            oParent.CallTrigger(oActionTrigger,uResponse)
                                        else:
                                            self.ShowError(uMsg="Wrong command syntax (Trigger Response):"+uCommand)
                                else:
                                    if not uCommand==oParent.uMsg[:3]:
                                        if not uCommand=='LTN':
                                            if not uCommand=='':
                                                if not uCommand+ ':'+uResponse=="NST:p--":
                                                    oParent.ShowDebug(uMsg=f'Discard message: [{uCommand}]:[{uResponse}]: Looking for [{oParent.uMsg[:3]}]')
#                               self.uMsg=''
                                # We do not need to wait for an response anymore
                                StartWait(0)
                            else:
                                Logger.warning('Onkyo close request')
                                oParent.bStopThreadEvent = True
                                # oParent.Disconnect()
                                # oParent.Connect()
                            self.bBusy = False

            except Exception as e:
                self.ShowError(uMsg='Receive:Error Receiving Response:',oException=e)
                self.bIsConnected = False
                self.bBusy = False
            try:
                if self.oSocket is not None:
                    self.ShowDebug(uMsg='Closing socket in thread')
                    self.bIsConnected = False
                    self.oSocket.close()
                    self.oSocket = None
            except Exception as e:
                self.ShowError(uMsg='Error closing socket in Thread',oException=e)

    def __init__(self):
        super().__init__()

        cInterFaceSettings=cInterface.cInterFaceSettings

        self.dSettings:Dict[cInterFaceSettings]     = {}
        self.oSetting:Optional[cInterFaceSettings]  = None
        self.uResponse:str                          = ''
        self.iBufferSize:int                        = 2048
        self.iWaitMs:int                            = 2000
        self.uPictureType:str                       = '.bmp'
        self.uRetVar:str                            = ''
        self.uPictureData:str                       = ''
        self.iCursorPos:int                         = 0
        self.iCntNLS:int                            = 0
        self.dDeviceSettings:Dict                   = {}
        self.dLMD_Text:Dict[str,str]                = {}
        self.cDeviceSettings                        = None
        self.InitLVM()
        self.aDiscoverScriptsBlackList:List         = ['iTach (Global Cache)','Keene Kira','ELVMAX','Enigma']

    def Init(self, uObjectName:str, oFnObject:Optional[cFileName]=None) -> None:
        super().Init(uObjectName= uObjectName,oFnObject=oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = 'enabled'
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = 'enabled'
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = 'enabled'
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = 'enabled'
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = 'enabled'
        self.oObjectConfig.dDefaultSettings['RetryCount']['active']                  = 'enabled'
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = 'enabled'
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = 'enabled'
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = 'enabled'

        if TYPE_CHECKING:
            from interfaces.eiscp.DeviceSettings import cDeviceSettings
            self.cDeviceSettings = cDeviceSettings
        else:
            oFnDeviceSettings = cFileName(self.oPathMyCode) + 'DeviceSettings.py'
            oModule = Globals.oModuleLoader.LoadModule(oFnModule=oFnDeviceSettings,uModuleName='DeviceSettings')
            self.cDeviceSettings = oModule.GetClass('cDeviceSettings')

    def DeInit(self, **kwargs) -> None:
        super().DeInit(**kwargs)
        for uSettingName in self.dSettings:
            self.dSettings[uSettingName].DeInit()

    def GetConfigJSON(self) -> Dict:
        return {'UnitType': {'active': 'enabled', 'order': 3, 'type': 'numeric', 'title': '$lvar(IFACE_EISCP_1)', 'desc': '$lvar(IFACE_EISCP_2)', 'section': '$var(ObjectConfigSection)','key': 'UnitType', 'default':'1' }}

    def DoAction(self,oAction:cAction) -> eReturnCode:
        uCmd:str=oAction.dActionPars.get('commandname','')
        if uCmd=='favorite pgup' or uCmd=='favorite pgdn':
            self.NLSPage(oAction,uCmd)
        return super().DoAction(oAction=oAction)

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        super().SendCommand(oAction=oAction,oSetting=oSetting,uRetVar=uRetVar,bNoLogOut=bNoLogOut)

        uTst:str
        uFormat:str
        uKey:str

        iTryCount:int       = 0
        eRet:eReturnCode    = eReturnCode.Error
        uMsg:str            = oAction.uCmd

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        uTst=uMsg[:3]
        if uTst=='MVL' and uMsg!='MVLUP' and uMsg!='MVLDOWN' and not uMsg.endswith('QSTN'):
            Var_Int2Hex(uVarName = self.uObjectName+'/'+oSetting.uConfigName+'volumetoset')
        if (uTst=='CTL' or uTst=='SWL') and not uMsg.endswith('QSTN'):
            uFormat='{:+03X}'
            uKey = oSetting.aIniSettings.uHost + oSetting.aIniSettings.uPort
            if uKey in self.dDeviceSettings:
                if uTst == 'CTL':
                    uFormat=self.dDeviceSettings[uKey].uVar_CTLFormat
                else:
                    uFormat = self.dDeviceSettings[uKey].uVar_SWLFormat

            Var_Int2Hex(uVarName = self.uObjectName + '/' + oSetting.uConfigName + 'volumetoset', uFormat = uFormat)

        uMsg             = ReplaceVars(uMsg,self.uObjectName+'/'+oSetting.uConfigName)
        uMsg             = ReplaceVars(uMsg)
        oSetting.uMsg    = uMsg
        oSetting.uRetVar = uRetVar

        if uTst == 'NRI':
            uKey = oSetting.aIniSettings.uHost + oSetting.aIniSettings.uPort
            if uKey in self.dDeviceSettings and False:
                self.dDeviceSettings[uKey].WriteVars(uVarPrefix=uRetVar, oAction=oAction)
                return eReturnCode.Success
            else:
                self.dDeviceSettings[uKey] = self.cDeviceSettings(self, oSetting)
                # we write the defaults to var, in case we can't connect to the receiver
                self.dDeviceSettings[uKey].WriteVars(uVarPrefix=uRetVar, oAction=oAction)

        #Logger.info ('Interface '+self.uObjectName+': Sending Command: '+uCommand + ' to '+oSetting.sHost+':'+oSetting.sPort)
        while iTryCount<oSetting.aIniSettings.iRetryCount:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                try:
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar,self.uObjectName+'/'+oSetting.uConfigName)
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar)

                    self.ShowInfo (uMsg='Sending Command: '+uMsg + ' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,uParConfigName=oSetting.uConfigName)
                    byMsg:bytes = oSetting.CreateEISPHeader(uMsg)
                    if oAction.bWaitForResponse:
                        #All response comes to receiver thread, so we should hold the queue until vars are set
                        if uTst!='NRI':
                            StartWait(self.iWaitMs)
                        else:
                            StartWait(2000)
                    oSetting.oSocket.sendall(byMsg)
                    eRet = eReturnCode.Success
                    break
                except Exception as e:
                    self.ShowError(uMsg = 'Can\'t Send Message',uParConfigName=oSetting.uConfigName,oException=e)
                    eRet = eReturnCode.Error
                    oSetting.Disconnect()
                    if not uRetVar=='':
                        SetVar(uVarName = uRetVar, oVarValue = 'Error')
            else:
                if iTryCount==self.iMaxTryCount:
                    self.ShowWarning(uMsg='Nothing done,not connected! ->[%s]' % oAction.uActionName, uParConfigName=oSetting.uConfigName)
                if uRetVar:
                    SetVar(uVarName = uRetVar, oVarValue = '?')

        self.CloseSettingConnection(oSetting=oSetting,bNoLogOut=bNoLogOut)
        return eRet

    def NLSPage(self,oAction:cAction,uCmd:str) -> None:

        oSetting:cInterface.cInterFaceSettings = cast(cInterface.cInterFaceSettings,self.GetSettingObjectForConfigName(uConfigName=oAction.dActionPars.get('configname','')))
        iSteps:int

        if uCmd=='favorite pgup':
            # iSteps=self.iCursorPos-(self.iCntNLS+1)-1
            iSteps=(self.iCursorPos*-1)-1
        else:
            iSteps=(self.iCntNLS+1)-self.iCursorPos-1
            if iSteps==0:
                iSteps=1

        oSetting.SetContextVar(uVarName="PAGESIZE",uVarValue=" " * abs(iSteps))
        Logger.debug('Cmd:'+uCmd+" count:"+str(self.iCntNLS)+" Pos:"+str(self.iCursorPos)+ " Steps:"+str(iSteps))

    def Split_IFA(self,oAction:cAction,uResponse:str,oSetting:cInterFaceSettings) -> None:
        # handles the return of Audio Information Request
        uTmp:str=oAction.uGlobalDestVar
        if not oSetting.uRetVar=='':
            oAction.uGlobalDestVar=oSetting.uRetVar

        aResponses:List=uResponse.split(',')

        if len(aResponses)>1:
            oSetting.oResultParser.SetVar2(aResponses[0], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Audio Input Selection', uAddName='_audio_input_selection')
            oSetting.oResultParser.SetVar2(aResponses[1], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Audio Input Codec', uAddName='_audio_input_codec')
        if len(aResponses)>2:
            oSetting.oResultParser.SetVar2(aResponses[2], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Audio Input Frequency', uAddName='_audio_input_frequency')
        if len(aResponses)>3:
            oSetting.oResultParser.SetVar2(aResponses[3], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Audio Input Channels', uAddName='_audio_input_channels')
        if len(aResponses)>4:
            oSetting.oResultParser.SetVar2(aResponses[4], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Audio Output Effect', uAddName='_audio_output_effect')
        if len(aResponses)>5:
            oSetting.oResultParser.SetVar2(aResponses[5], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Audio Output Channels', uAddName='_audio_output_channels')

        if uTmp!='':
            oSetting.uRetVar=uTmp

    def Handle_NRI(self,oAction:cAction,uResponse:str,oSetting:cInterFaceSettings) -> None:
        # Parses the Onkyo Device Information and writes them into vars
        uKey:str = oSetting.aIniSettings.uHost + oSetting.aIniSettings.uPort
        if uKey not in self.dDeviceSettings:
            self.dDeviceSettings[uKey] = self.cDeviceSettings(self, oSetting)

        self.dDeviceSettings[uKey].ParseXML(uResponse, oAction)
        self.dDeviceSettings[uKey].WriteVars(uVarPrefix=oAction.uGlobalDestVar, oAction=oAction)

    def Handle_NLS(self,oAction:cAction,uResponse:str,oSetting:cInterFaceSettings) -> Tuple[str,str]:
        # Handles the NET/USB List Info
        uCurPos:str
        uTmpCmd:str

        if len(uResponse)>2:
            if uResponse[0]=='C':
                uCurPos=uResponse[1]
                if uCurPos.isdigit():
                    self.iCursorPos=int(uCurPos)
                # if new page delete all old vars
                if uResponse[2]=='P':
                    for i in range(10):
                        oSetting.oResultParser.SetVar2(uValue='',uLocalDestVar=oAction.uLocalDestVar, uGlobalDestVar=oAction.uGlobalDestVar,uDebugMessage= 'NLS Value', uAddName='[' + ToUnicode(i) + ']')
                    return 'NLS',''
                return '',''


            if uResponse[0]=='U' or uResponse[0]=='A':
                uTmp=oAction.uGlobalDestVar
                iIndex=int(uResponse[1])

                #this is redundant, but sometimes the Receiver doesn't send a page clear
                if iIndex==0:
                    for i in range(10):
                        oSetting.oResultParser.SetVar2(uValue='', uLocalDestVar=oAction.uLocalDestVar, uGlobalDestVar=oAction.uGlobalDestVar, uDebugMessage='NLS Value', uAddName='[' + ToUnicode(i) + ']')

                sText=uResponse[3:]
                uText=''
                if uResponse[0]=='A':
                    uText=ToUnicode(sText)
                if uResponse[0]=='U':
                    uText=ToUnicode(sText)
                oSetting.oResultParser.SetVar2(uValue=uText, uLocalDestVar=oAction.uLocalDestVar, uGlobalDestVar=oAction.uGlobalDestVar, uDebugMessage='NLS Value', uAddName='[' + ToUnicode(iIndex) + ']')
                if uTmp!='':
                    oSetting.uRetVar=uTmp
                self.iCntNLS=iIndex
                self.uRetVar=uTmp
                return 'NLS',uText
        return 'NLS',ToUnicode(uResponse[3:])

    # noinspection PyUnusedLocal
    def Handle_NLT(self,oAction:cAction,uResponse:str,oSetting:cInterFaceSettings):
        # Handles the NET/USB List Info
        pass
        '''
        
        "xxuycccciiiillsraabbssnnn...nnn" 
        ('Receive:', u'NLT', ':', '1C22000000000001001C00')
        
        xx 1C scheint Amazon Music
        
        NET/USB List Title Info
        xx : Service Type
         00 : Music Server (DLNA), 01 : Favorite, 02 : vTuner, 03 : SiriusXM, 04 : Pandora, 05 : Rhapsody, 06 : Last.fm,
         07 : Napster, 08 : Slacker, 09 : Mediafly, 0A : Spotify, 0B : AUPEO!, 0C : radiko, 0D : e-onkyo,
         0E : TuneIn Radio, 0F : MP3tunes, 10 : Simfy, 11:Home Media, 12:Deezer, 13:iHeartRadio, 18:Airplay, 1A:onkyo music,
         1B:TIDAL, F0 : USB/USB(Front) F1 : USB(Rear), F2 : Internet Radio, F3 : NET, FF : None
        u : UI Type
         0 : List, 1 : Menu, 2 : Playback, 3 : Popup, 4 : Keyboard, "5" : Menu List
        y : Layer Info
         0 : NET TOP, 1 : Service Top,DLNA/USB/iPod Top, 2 : under 2nd Layer
        cccc : Current Cursor Position (HEX 4 letters)
        iiii : Number of List Items (HEX 4 letters)
        ll : Number of Layer(HEX 2 letters)
        s : Start Flag
         0 : Not First, 1 : First
        r : Reserved (1 leters, don't care)
        aa : Icon on Left of Title Bar
         00 : Internet Radio, 01 : Server, 02 : USB, 03 : iPod, 04 : DLNA, 05 : WiFi, 06 : Favorite
         10 : Account(Spotify), 11 : Album(Spotify), 12 : Playlist(Spotify), 13 : Playlist-C(Spotify)
         14 : Starred(Spotify), 15 : What's New(Spotify), 16 : Track(Spotify), 17 : Artist(Spotify)
         18 : Play(Spotify), 19 : Search(Spotify), 1A : Folder(Spotify)
         FF : None
        bb : Icon on Right of Title Bar
         00 : Muisc Server (DLNA), 01 : Favorite, 02 : vTuner, 03 : SiriusXM, 04 : Pandora, 05 : Rhapsody, 06 : Last.fm,
         07 : Napster, 08 : Slacker, 09 : Mediafly, 0A : Spotify, 0B : AUPEO!, 0C : radiko, 0D : e-onkyo,
         0E : TuneIn Radio, 0F : MP3tunes, 10 : Simfy, 11:Home Media, 12:Deezer, 13:iHeartRadio, 18:Airplay, 1A:onkyo music,
        1B:TIDAL, F0:USB/USB(Front), F1:USB(Rear),
         FF : None
        ss : Status Info
         00 : None, 01 : Connecting, 02 : Acquiring License, 03 : Buffering
         04 : Cannot Play, 05 : Searching, 06 : Profile update, 07 : Operation disabled
         08 : Server Start-up, 09 : Song rated as Favorite, 0A : Song banned from station,
         0B : Authentication Failed, 0C : Spotify Paused(max 1 device), 0D : Track Not Available, 0E : Cannot Skip
        nnn...nnn : Character of Title Bar (variable-length, 64 Unicode letters [UTF-8 encoded] max)
        
        '''


    def Handle_NJA(self,oAction:cAction,sResponse:str,oSetting:cInterFaceSettings) -> Tuple[str,str]:

        if len(sResponse)>1:
            if sResponse[1]=='0' or sResponse[1]=='-':
                self.uPictureData=sResponse[2:]
                self.uPictureType = '.bmp'
                if sResponse[0]=='1':
                    self.uPictureType='.jpg'
                if sResponse[0]=='2':
                    self.uPictureType='.href'
            if sResponse[0]=='n':
                #todo: delete old file picture if we get a no picture response
                Logger.debug('Onkyo Receiver has no picture to return')
                return 'NJA',''

            if sResponse[1]=='1':
                self.uPictureData+=sResponse[2:]
                return '',''
            if sResponse[1]=='2' or sResponse[1]=='-':
                if sResponse[1] == '2':
                    self.uPictureData=sResponse[2:]

                try:
                    bHex = True

                    if self.uPictureType == '.href':
                        self.uPictureData,self.uPictureType = self.GetPictureByUrl(self.uPictureData, oSetting)
                        bHex = False

                    if len(self.uPictureData)>0:
                        oFileName:cFileName = cFileName(Globals.oPathTmp) + oAction.uGlobalDestVar + self.uPictureType

                        f = open(str(oFileName), 'wb')
                        if bHex:
                            f.write( binascii.a2b_hex(self.uPictureData))
                        else:
                            f.write(cast(bytes,self.uPictureData))
                        f.close()
                        oSetting.oResultParser.SetVar2(str(oFileName), oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing MediaPicture')
                        SetVar(uVarName = 'NJAPIC', oVarValue = str(oFileName))
                        return 'NJA',str(oFileName)
                    else:
                        self.ShowWarning(uMsg='Skipping empty picture:', uParConfigName=oSetting.uConfigName)
                        return '', ''

                except Exception as e:
                    self.ShowError(uMsg='Unexpected error writing file', uParConfigName=oSetting.uConfigName, oException=e)

        return '',''

    def GetPictureByUrl(self, uUrl:str, oSetting:cInterFaceSettings) -> Tuple[str,str]:

        uPictureData:str = ''
        uPictureType:str = ''
        uHeader:str
        iPos:int
        iPosEnd:int

        try:
            oReq = UrlRequest(uUrl)
            oReq.wait()
            uPictureData = oReq.result
            uHeader = oReq.resp_headers.get('content-type')
            if uHeader is None:
                iPos = uPictureData.lower().find('content-type:')
                iPosEnd = uPictureData.find('\n',iPos)
                if iPos>-1 and iPosEnd>-1:
                    uHeader = uPictureData[iPos:iPosEnd]
                    iPos = uPictureData.find('\n\n')
                    if iPos > -1:
                        uPictureData=uPictureData[iPos+2:]
            if uHeader:
                uPictureType = uHeader.split('/')[-1]
            else:
                self.ShowWarning(uMsg='Invaid URL/Content Type when pulling picture from device:'+str(uHeader),uParConfigName=oSetting.uConfigName)
                uPictureType = uUrl.split('.')[-1]

            uPictureType = '.'+uPictureType

        except Exception as e:
            self.ShowError(uMsg='Unexpected error reading picture by URL:', uParConfigName=oSetting.uConfigName, oException=e)

        return uPictureData,uPictureType

    def Split_IFV(self,oAction:cAction,uResponse:str,oSetting:cInterFaceSettings) -> None:
        # handles the return of Video Information Request
        uTmp:str=oAction.uGlobalDestVar
        if not oSetting.uRetVar=='':
            oAction.uGlobalDestVar=oSetting.uRetVar

        aResponses:List=uResponse.split(',')
        if len(aResponses)>1:
            oSetting.oResultParser.SetVar2(aResponses[0], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Video Input Selection', uAddName='_video_input_selection')
            oSetting.oResultParser.SetVar2(aResponses[1], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Video Input Resolution', uAddName='_video_input_resolution')
        if len(aResponses)>2:
            oSetting.oResultParser.SetVar2(aResponses[2], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Video Input Color', uAddName='_video_input_color')
        if len(aResponses)>3:
            oSetting.oResultParser.SetVar2(aResponses[3], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Video Input Bits', uAddName='_video_input_bits')
        if len(aResponses)>4:
            oSetting.oResultParser.SetVar2(aResponses[4], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Video Output Selection', uAddName='_video_output_selection')
        if len(aResponses)>5:
            oSetting.oResultParser.SetVar2(aResponses[5], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Video Output Resolution', uAddName='_video_output_resolution')
        if len(aResponses)>6:
            oSetting.oResultParser.SetVar2(aResponses[6], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Video Output Color', uAddName='_video_output_color')
        if len(aResponses)>7:
            oSetting.oResultParser.SetVar2(aResponses[7], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Video Output Bits', uAddName='_video_output_bits')
        if len(aResponses)>8:
            oSetting.oResultParser.SetVar2(aResponses[8], oAction.uLocalDestVar, oAction.uGlobalDestVar, 'Storing Video Output Effect', uAddName='_video_output_bits')

        if uTmp!='':
            oSetting.uRetVar=uTmp

    def ISCP_LMD_To_Text(self,uLMD:str) -> str:

        uRet:str = self.dLMD_Text.get(uLMD)
        if uRet is None:
            uRet='unknown'
        return uRet

    def InitLVM(self) -> None:
        self.dLMD_Text= {'00': 'STEREO',
                         '01': 'DIRECT',
                         '02': 'SURROUND',
                         '03': 'FILM',
                         '04': 'THX',
                         '05': 'ACTION',
                         '06': 'MUSICAL',
                         '07': 'MONO MOVIE',
                         '08': 'ORCHESTRA',
                         '09': 'UNPLUGGED',
                         '0A': 'STUDIO-MIX',
                         '0B': 'TV LOGIC',
                         '0C': 'ALL CH STEREO',
                         '0D': 'THEATER-DIMENSIONAL',
                         '0E': 'ENHANCED',
                         '0F': 'MONO',
                         '11': 'PURE AUDIO',
                         '12': 'MULTIPLEX',
                         '13': 'FULL MONO',
                         '14': 'DOLBY VIRTUAL',
                         '15': 'DTS Surround Sensation',
                         '16': 'Audyssey DSX',
                         '1F': 'Whole House Mode',
                         '40': '5.1ch Surround',
                         '41': 'DTS ES',
                         '42': 'THX Cinema',
                         '43': 'THX Surround EX',
                         '44': 'THX Music',
                         '45': 'THX Games',
                         '50': 'THX Cinema',
                         '51': 'THX MusicMode',
                         '52': 'THX Games Mode',
                         '80': 'PLII/PLIIx Movie',
                         '81': 'PLII/PLIIx Music',
                         '82': 'Neo:X Cinema',
                         '83': 'Neo:X Music',
                         '84': 'PLII/PLIIx THX Cinema',
                         '85': 'Neo:X THX Cinema',
                         '86': 'PLII/PLIIx Game',
                         '87': 'Neural Surr',
                         '88': 'Neural THX',
                         '89': 'PLII/PLIIx THX Games',
                         '8A': 'Neo:X THX Games',
                         '8B': 'PLII/PLIIx THX Music',
                         '8C': 'Neo:X THX Music',
                         '8D': 'Neural THX Cinema',
                         '8E': 'Neural THX Music',
                         '8F': 'Neural THX Games',
                         '90': 'PLIIz Height',
                         '91': 'Neo:6 Cinema DTS Surround Sensation',
                         '92': 'Neo:6 Music DTS Surround Sensation',
                         '93': 'Neural Digital Music',
                         '94': 'PLIIz Height + THX Cinema',
                         '95': 'PLIIz Height + THX Music',
                         '96': 'PLIIz Height + THX Games',
                         '97': 'PLIIz Height + THX U2/S2 Cinema',
                         '98': 'PLIIz Height + THX U2/S2 Music',
                         '99': 'PLIIz Height + THX U2/S2 Games',
                         '9A': 'Neo:X Game',
                         'A0': 'PLIIx/PLII Movie + Audyssey DSX',
                         'A1': 'PLIIx/PLII Music + Audyssey DSX',
                         'A2': 'PLIIx/PLII Game + Audyssey DSX',
                         'A3': 'Neo:6 Cinema + Audyssey DSX',
                         'A4': 'Neo:6 Music + Audyssey DSX',
                         'A5': 'Neural Surround + Audyssey DSX',
                         'A6': 'Neural Digital Music + Audyssey DSX',
                         'A7': 'Dolby EX + Audyssey DSX',
                         'FF': 'Auto Surround'}



    '''
    def GenerateXMLFile(self):

        from collections import OrderedDict


                for sCommands in COMMANDS:
            # print sCommands

            print '  <!--\n      Section:',sCommands+ '\n  -->'
            for sSubCommand in COMMANDS[sCommands]:
                # print sSubCommand
                # print COMMANDS[sCommands][sSubCommand]
                oItems=COMMANDS[sCommands][sSubCommand]
                print '  <!--\n      Category:'+oItems['description']+ '\n  -->'
                #for oItem in oItems:
                if True:
                    for sValue in oItems['values']:
                        oValue=oItems['values'][sValue]

                        if not oValue['name']==None:
                            if type(oValue['name']).__name__=='str':
                                sName=oValue['name']
                            else:
                                sName=oValue['name'][0]
                        else:
                            sName='!!!!!!!!!!!!!!!!!value!!!!!!!!!!!!!!!!'

                        if not type(sValue).__name__=='str':
                            sValue='Varrange from '+ str(sValue[0])+' to '+str(sValue[1])

                        sDescription=oValue['description']
                        if type(sDescription).__name__=='unicode':
                            sDescription=sDescription.encode('utf-8','replace')

                        print '  <action string='codeset' name=\''+sCommands+'.'+COMMANDS[sCommands][sSubCommand]['name']+'.'+sName+'\' desc=\''+sDescription +  '\'  cmd=\''+sSubCommand+sValue+'\' />'
        '''

