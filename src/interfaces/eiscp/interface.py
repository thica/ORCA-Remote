# -*- coding: utf-8 -*-
#  Onkyo eiscp
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

from __future__                            import annotations
from typing                                import Dict
from typing                                import List
from typing                                import Tuple
from typing                                import Union
from typing                                import cast
from typing                                import TYPE_CHECKING
from time                                  import sleep
from threading                             import Thread
from threading                             import currentThread

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
from ORCA.Action                           import cAction
from ORCA.actions.ReturnCode               import eReturnCode
import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Onkyo EISCP (LAN)</name>
      <description language='English'>Onkyo EISCP Interface (LAN/IP)</description>
      <description language='German'>Onkyo EISCP Interface (LAN/IP)</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
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
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.oSocket:Union[socket.socket,None]          = None
            self.uMsg:str                                   = u''
            self.iBufferSize:int                            = 2048

            self.bHeader:bytes                              = b'ISCP'
            self.iHeaderSize:int                            = 16
            self.iVersion:int                               = 1
            self.bStopThreadEvent:bool                      = False
            self.uRetVar:str                                = u''
            self.dResponseActions:Dict                      = {}
            self.bBusy:bool                                 = False

            self.aIniSettings.uHost                         = u"discover"
            self.aIniSettings.uPort                         = u"60128"
            self.aIniSettings.uFNCodeset                    = u"CODESET_eiscp_ONKYO_AVR.xml"
            self.aIniSettings.fTimeOut                      = 2.0
            self.aIniSettings.iTimeToClose                  = -1
            self.aIniSettings.uDiscoverScriptName           = u"discover_eiscp"
            self.aIniSettings.uParseResultOption            = u'store'
            self.aIniSettings.fDISCOVER_EISCP_timeout       = 2.0
            self.aIniSettings.uDISCOVER_EISCP_models        = []
            self.aIniSettings.uDISCOVER_UPNP_servicetypes   = "upnp:rootdevice"
            self.aIniSettings.uDISCOVER_UPNP_manufacturer   = "Onkyo & Pioneer Corporation"
            self.oThread                                    = None

        def Connect(self) -> bool:

            if self.oResultParser is None:
                # Initiate Resultparser
                self.oInterFace.ParseResult(cAction(),"",self)

            if not cBaseInterFaceSettings.Connect(self):
                return False

            if (self.aIniSettings.uHost=="") or (self.aIniSettings.uPort==u""):
                self.ShowError(u'Cannot connect on empty host of port ')
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

                self.oThread = Thread(target = self.Receive,)
                self.bStopThreadEvent = False
                self.oThread.oParent = self
                self.oThread.start()
            except socket.error as e:
                self.ShowError(u'Cannot open socket:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.oSocket.close()
                self.oSocket = None
            except Exception as e:
                self.ShowError(u'Cannot open socket#2:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.bOnError=True

            if self.oSocket is None:
                self.bOnError=True
                return False

            self.bIsConnected =True
            return self.bIsConnected

        def Disconnect(self) -> bool:
            if not cBaseInterFaceSettings.Disconnect(self):
                return False

            if self.oThread:
                self.bStopThreadEvent = True
                self.oThread.join()
                self.oThread = None
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

            uMessage:str        = u'!' + str(self.aIniSettings.iUnitType) + uCmd + '\x0a'
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
                return u'', ''

            try:
                byHeaderRet = byResponseIn[0:4]
                # iHeaderSize = int.from_bytes(byResponseIn[4:8], byteorder='big', signed=False) # we dont need it
                iDataSize   = int.from_bytes(byResponseIn[8:12], byteorder='big', signed=False)
                iVersionRet = byResponseIn[12]
                # struct.unpack doesnt not work reliable on all Android Platform processors
                # byHeaderRet, iHeaderSize, iDataSize, iVersionRet = unpack('!4sIIBxxx', byResponseIn[0:self.iHeaderSize])
                if byHeaderRet != self.bHeader:
                    self.ShowDebug(u'Received packet not ISCP: '+ToUnicode(byHeaderRet))
                    return u'',''
                if iVersionRet != self.iVersion:
                    self.ShowDebug(u'ISCP version not supported: '+ToUnicode(iVersionRet))
                    return u'',''
                if len(byResponseIn)==16:
                    byResponse=self.Helper_ReceiveAll(self.oSocket,iDataSize)
                else:
                    byResponse= byResponseIn[17:]
                if byResponse:
                    uMessage        = byResponse.decode("utf-8").rstrip('\x1a\r\n')
                    iMessageSize    = len(uMessage)
                    # parse message
                    # sUnitType     = uMessage[1]
                    uCommand        = ToUnicode(uMessage[2:5])
                    uParameter      = uMessage[5:iMessageSize]
                    return uCommand,uParameter
                else:
                    self.ShowDebug(u'Got empty response: '+ToUnicode(byResponseIn))
                    return "", ""
            except Exception as e:
                self.ShowError(u'Cannot parse response:'+ToUnicode(byResponse)+":"+ToUnicode(byResponseIn),e)
                return u'',''

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
                            self.ShowError("Can't get complete response 1 ({}) ({})".format(iMissing,byData) )
                        return byData
                    byData += byPacket
                return byData
            except Exception as e:
                self.ShowError(u"ReceiveAll:Can't receive response 2",e)
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
            oTmpAction: Union[cBaseTrigger,cAction]

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
                                i = i + 1
                                if i > 200:
                                    oParent.ShowError("Busy Time Out")
                                    self.bBusy = False
                            self.bBusy = True

                            byResponseHeader:bytes = oParent.Helper_ReceiveAll(aReadSocket[0], 16)
                            # noinspection PyInterpreter
                            if len(byResponseHeader)>0:
                                # Get the Command and the payload
                                uCommand,uResponse=oParent.UnpackEISPResponse(byResponseHeader)

                                # print ("Receive:",uCommand,":",sResponse)

                                # This returns ASCII of sResponse, we will convert it one line later
                                # we might get a response without dedicated requesting it, so lets use an action
                                # from previous request to get the return vars

                                bHandleSpecialResponse:bool = False
                                # Default is the last action (That is the command, where we MIGHT get the response from
                                oTmpAction = self.oAction
                                if uCommand == self.uMsg[:3]:
                                    # if we have a response to the last action, lets store the action for future use
                                    # in case we got a response without requesting it
                                    # Not 100% logic, but should fit in 99.9 % of the cases
                                    if oParent.GetTrigger(uCommand) is None:
                                        oParent.dResponseActions[uCommand] = oTmpAction
                                        bHandleSpecialResponse = True

                                # Lets check , if we have an Trigger set for unrequested responses
                                oActionTrigger:cBaseTrigger = oParent.GetTrigger(uCommand)
                                if oActionTrigger:
                                    oTmpAction=oActionTrigger
                                    bHandleSpecialResponse = True
                                elif not bHandleSpecialResponse:
                                    # If we dont have an trigger and its not a response to the action
                                    # lets use the stored action, if we have it
                                    if uCommand in oParent.dResponseActions:
                                        oTmpAction = oParent.dResponseActions[uCommand]
                                        bHandleSpecialResponse = True

                                if bHandleSpecialResponse:
                                    if uCommand==u'NLS':
                                        # This might return an adjusted Response
                                        uCommand,uResponse=oParent.oInterFace.Handle_NLS(oTmpAction,uResponse,self)
                                # uResponse=ToUnicode(uResponse)
                                if bHandleSpecialResponse:
                                    if uCommand == u'NRI':
                                        oParent.oInterFace.Handle_NRI(oTmpAction, uResponse, oParent)
                                    elif uCommand==u'NJA':
                                        uCommand,uResponse=oParent.oInterFace.Handle_NJA(oTmpAction,uResponse,oParent)
                                    elif uCommand==u'LMD':
                                        uResponse=oParent.oInterFace.ISCP_LMD_To_Text(uResponse)
                                    elif uCommand==u'IFA':
                                        oParent.oInterFace.Split_IFA(oTmpAction,uResponse,oParent)
                                    elif uCommand==u'IFV':
                                         oParent.oInterFace.Split_IFV(oTmpAction,uResponse,oParent)
                                    elif uCommand==u'MVL' or uCommand==u'CTL' or uCommand==u'SWL':
                                        if uResponse!=u'N/A':
                                            uResponse=str(int(uResponse, 16))
                                # If the returned Command is a response to the send message
                                if uCommand==oParent.uMsg[:3]:
                                    #uCmd,uRetVal=self.oInterFace.ParseResult(self.oAction,uResponse,self)
                                    uRetVal:str = u''
                                    if not oParent.uRetVar==u'':
                                        uTmp=oParent.oAction.uGlobalDestVar
                                        oParent.oAction.uGlobalDestVar=oParent.uRetVar
                                        uCmd,uRetVal=oParent.oInterFace.ParseResult(oParent.oAction,uResponse,oParent)
                                        oParent.oAction.uGlobalDestVar=uTmp
                                    if not oParent.uRetVar==u'' and not uRetVal==u'':
                                        SetVar(uVarName = self.uRetVar, oVarValue = uRetVal)

                                    # we got our response, all other responses are for somebody else
                                    #self.uMsg=''
                                # we have a notification issued by the device, so lets have a look, if we have a trigger code to it
                                oActionTrigger=oParent.GetTrigger(uCommand)

                                if oActionTrigger:
                                    oParent.ShowInfo(u'Calling Trigger for:' + uCommand)
                                    oParent.CallTrigger(oActionTrigger,uResponse)
                                else:
                                    if not uCommand==oParent.uMsg[:3]:
                                        if not uCommand==u'LTN':
                                            if not uCommand==u'':
                                                if not uCommand+ ':'+uResponse=="NST:p--":
                                                    oParent.ShowDebug(u'Discard message:'+uCommand+ ':'+uResponse+': Looking for ('+oParent.uMsg[:3]+')')
#                               self.uMsg=''
                                # We do not need to wait for an response anymore
                                StartWait(0)
                            else:
                                Logger.warning("Onkyo close request")
                                oParent.Disconnect()
                                oParent.Conncet()
                            self.bBusy = False


            except Exception as e:
                self.ShowError(u'Receive:Error Receiving Response:',e)
                self.bIsConnected = False
                self.bBusy = False
            try:
                if self.oSocket is not None:
                    self.ShowDebug(u'Closing socket in Thread')
                    self.oSocket.close()
                    self.oSocket = None
            except Exception as e:
                self.ShowError(u'Error closing socket in Thread',e)

    def __init__(self):
        cBaseInterFace.__init__(self)

        cInterFaceSettings=cInterface.cInterFaceSettings

        self.dSettings:Dict[cInterFaceSettings]     = {}
        self.oSetting:Union[cInterFaceSettings,None]= None
        self.uResponse:str                          = u''
        self.iBufferSize:int                        = 2048
        self.iWaitMs:int                            = 2000
        self.uPictureType:str                       = u'.bmp'
        self.uRetVar:str                            = u''
        self.uPictureData:str                       = u''
        self.iCursorPos:int                         = 0
        self.iCntNLS:int                            = 0
        self.dDeviceSettings:Dict                   = {}
        self.dLMD_Text:Dict[str,str]                = {}
        self.cDeviceSettings                        = None
        self.InitLVM()
        self.aDiscoverScriptsBlackList:List         = ["iTach (Global Cache)","Keene Kira","ELVMAX","Enigma Discover"]

    def Init(self, uObjectName:str, oFnObject:Union[cFileName,None]=None) -> None:
        cBaseInterFace.Init(self,uObjectName, oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

        if TYPE_CHECKING:
            from interfaces.eiscp.DeviceSettings import cDeviceSettings
            self.cDeviceSettings = cDeviceSettings
        else:
            oFnDeviceSettings = cFileName(self.oPathMyCode) + u'DeviceSettings.py'
            oModule = Globals.oModuleLoader.LoadModule(oFnDeviceSettings, 'DeviceSettings')
            self.cDeviceSettings = oModule.GetClass("cDeviceSettings")

    def DeInit(self, **kwargs) -> None:
        cBaseInterFace.DeInit(self,**kwargs)
        for uSettingName in self.dSettings:
            self.dSettings[uSettingName].DeInit()

    def GetConfigJSON(self) -> Dict:
        return {"UnitType": {"active": "enabled", "order": 3, "type": "numeric", "title": "$lvar(IFACE_EISCP_1)", "desc": "$lvar(IFACE_EISCP_2)", "section": "$var(ObjectConfigSection)","key": "UnitType", "default":"1" }}

    def DoAction(self,oAction:cAction) -> eReturnCode:
        uCmd:str=oAction.dActionPars.get("commandname",'')
        if uCmd=='favorite pgup' or uCmd=='favorite pgdn':
            self.NLSPage(oAction,uCmd)
        return cBaseInterFace.DoAction(self,oAction)

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        uTst:str
        uFormat:str
        uKey:str

        iTryCount:int       = 0
        eRet:eReturnCode    = eReturnCode.Error
        uMsg:str            = oAction.uCmd

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        uTst=uMsg[:3]
        if uTst==u'MVL' and uMsg!=u'MVLUP' and uMsg!=u'MVLDOWN' and not uMsg.endswith("QSTN"):
            Var_Int2Hex(uVarName = self.uObjectName+'/'+oSetting.uConfigName+'volumetoset')
        if (uTst==u'CTL' or uTst==u'SWL') and not uMsg.endswith("QSTN"):
            uFormat='{:+03X}'
            uKey = oSetting.aIniSettings.uHost + oSetting.aIniSettings.uPort
            if uKey in self.dDeviceSettings:
                if uTst == u'CTL':
                    uFormat=self.dDeviceSettings[uKey].uVar_CTLFormat
                else:
                    uFormat = self.dDeviceSettings[uKey].uVar_SWLFormat
            Var_Int2Hex(uVarName = self.uObjectName + '/' + oSetting.uConfigName + 'volumetoset', uFormat = uFormat)

        uMsg             = ReplaceVars(uMsg,self.uObjectName+'/'+oSetting.uConfigName)
        uMsg             = ReplaceVars(uMsg)
        oSetting.uMsg    = uMsg
        oSetting.uRetVar = uRetVar

        if uTst == u"NRI":
            uKey = oSetting.aIniSettings.uHost + oSetting.aIniSettings.uPort
            if uKey in self.dDeviceSettings and False:
                self.dDeviceSettings[uKey].WriteVars(uVarPrefix=uRetVar, oAction=oAction)
                return eReturnCode.Success
            else:
                self.dDeviceSettings[uKey] = self.cDeviceSettings(self, oSetting)
                # we write the defaults to var, in case we can't connect to the receiver
                self.dDeviceSettings[uKey].WriteVars(uVarPrefix=uRetVar, oAction=oAction)

        #Logger.info (u'Interface '+self.uObjectName+': Sending Command: '+sCommand + ' to '+oSetting.sHost+':'+oSetting.sPort)
        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()

            if oSetting.bIsConnected:
                try:
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar,self.uObjectName+'/'+oSetting.uConfigName)
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar)

                    self.ShowInfo (u'Sending Command: '+uMsg + ' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,oSetting.uConfigName)
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
                    self.ShowError(uMsg = u'Can\'t Send Message',uParConfigName=oSetting.uConfigName,oException=e)
                    eRet = eReturnCode.Error
                    oSetting.Disconnect()
                    if not uRetVar==u'':
                        SetVar(uVarName = uRetVar, oVarValue = u"Error")
            else:
                if iTryCount==2:
                    self.ShowWarning(u'Nothing done,not connected! ->[%s]' % oAction.uActionName, oSetting.uConfigName)
                if uRetVar:
                    SetVar(uVarName = uRetVar, oVarValue = u"?")

        self.CloseSettingConnection(oSetting=oSetting,bNoLogOut=bNoLogOut)
        return eRet

    def NLSPage(self,oAction:cAction,uCmd:str) -> None:

        oSetting:cInterface.cInterFaceSettings=self.GetSettingObjectForConfigName(oAction.dActionPars.get(u'configname',u''))
        iSteps:int

        if uCmd=='favorite pgup':
            # iSteps=self.iCursorPos-(self.iCntNLS+1)-1
            iSteps=(self.iCursorPos*-1)-1
        else:
            iSteps=(self.iCntNLS+1)-self.iCursorPos-1
            if iSteps==0:
                iSteps=1

        oSetting.SetContextVar("PAGESIZE"," " * abs(iSteps))
        Logger.debug('Cmd:'+uCmd+" count:"+str(self.iCntNLS)+" Pos:"+str(self.iCursorPos)+ " Steps:"+str(iSteps))

    def Split_IFA(self,oAction:cAction,uResponse:str,oSetting:cInterFaceSettings) -> None:
        # handles the return of Audio Information Request
        uTmp:str=oAction.uGlobalDestVar
        if not oSetting.uRetVar==u'':
            oAction.uGlobalDestVar=oSetting.uRetVar

        aResponses:List=uResponse.split(',')

        if len(aResponses)>1:
            oSetting.oResultParser.SetVar2(aResponses[0], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Input Selection', uAddName=u'_audio_input_selection')
            oSetting.oResultParser.SetVar2(aResponses[1], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Input Codec', uAddName=u'_audio_input_codec')
        if len(aResponses)>2:
            oSetting.oResultParser.SetVar2(aResponses[2], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Input Frequency', uAddName=u'_audio_input_frequency')
        if len(aResponses)>3:
            oSetting.oResultParser.SetVar2(aResponses[3], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Input Channels', uAddName=u'_audio_input_channels')
        if len(aResponses)>4:
            oSetting.oResultParser.SetVar2(aResponses[4], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Output Effect', uAddName=u'_audio_output_effect')
        if len(aResponses)>5:
            oSetting.oResultParser.SetVar2(aResponses[5], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Output Channels', uAddName=u'_audio_output_channels')

        if uTmp!=u'':
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
                        oSetting.oResultParser.SetVar2(uValue=u'',uLocalDestVar=oAction.uLocalDestVar, uGlobalDestVar=oAction.uGlobalDestVar,uDebugMessage= u'NLS Value', uAddName=u"[" + ToUnicode(i) + u"]")
                    return u'NLS',u''
                return u'',u''


            if uResponse[0]==u'U' or uResponse[0]==u'A':
                uTmp=oAction.uGlobalDestVar
                iIndex=int(uResponse[1])

                #this is redundent, but sometimes the Receiver doesn't send a page clear
                if iIndex==0:
                    for i in range(10):
                        oSetting.oResultParser.SetVar2(uValue=u'', uLocalDestVar=oAction.uLocalDestVar, uGlobalDestVar=oAction.uGlobalDestVar, uDebugMessage=u'NLS Value', uAddName=u"[" + ToUnicode(i) + u"]")

                sText=uResponse[3:]
                uText=''
                if uResponse[0]=='A':
                    uText=ToUnicode(sText)
                if uResponse[0]=='U':
                    uText=ToUnicode(sText)
                oSetting.oResultParser.SetVar2(uValue=uText, uLocalDestVar=oAction.uLocalDestVar, uGlobalDestVar=oAction.uGlobalDestVar, uDebugMessage=u'NLS Value', uAddName=u"[" + ToUnicode(iIndex) + u"]")
                if uTmp!=u'':
                    oSetting.uRetVar=uTmp
                self.iCntNLS=iIndex
                self.uRetVar=uTmp
                return u'NLS',uText
        return u"NLS",ToUnicode(uResponse[3:])

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
            if sResponse[1]==u'0' or sResponse[1]==u'-':
                self.uPictureData=sResponse[2:]
                self.uPictureType = u".bmp"
                if sResponse[0]==u'1':
                    self.uPictureType=u'.jpg'
                if sResponse[0]==u'2':
                    self.uPictureType=u'.href'
            if sResponse[0]==u'n':
                #todo: delete old file picture if we get a no picture response
                Logger.debug("Onkyo Receiver has no picture to return")
                return "NJA",""

            if sResponse[1]==u'1':
                self.uPictureData+=sResponse[2:]
                return u"",u""
            if sResponse[1]==u'2' or sResponse[1]==u'-':
                if sResponse[1] == u'2':
                    self.uPictureData=sResponse[2:]

                try:
                    bHex = True

                    if self.uPictureType == u'.href':
                        self.uPictureData,self.uPictureType = self.GetPictureByUrl(self.uPictureData, oSetting)
                        bHex = False

                    if len(self.uPictureData)>0:
                        oFileName:cFileName = cFileName(Globals.oPathTmp) + oAction.uGlobalDestVar + self.uPictureType

                        f = open(oFileName.string, 'wb')
                        if bHex:
                            f.write( binascii.a2b_hex(self.uPictureData))
                        else:
                            f.write(cast(self.uPictureData,bytes))
                        f.close()
                        oSetting.oResultParser.SetVar2(oFileName.string, oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing MediaPicture')
                        SetVar(uVarName = u'NJAPIC', oVarValue = oFileName.string)
                        return u"NJA",oFileName.string
                    else:
                        self.ShowWarning(u'Skipping empty picture:', oSetting.uConfigName)
                        return u'', u''

                except Exception as e:
                    self.ShowError(uMsg=u'Unexpected error writing file', uParConfigName=oSetting.uConfigName, oException=e)

        return u'',u''

    def GetPictureByUrl(self, uUrl:str, oSetting:cInterFaceSettings) -> Tuple[str,str]:

        uPictureData:str = u''
        uPictureType:str = u''
        uHeader:str
        iPos:int
        iPosEnd:int

        try:
            oReq = UrlRequest(uUrl)
            oReq.wait()
            uPictureData = oReq.result
            uHeader = oReq.resp_headers.get("content-type")
            if uHeader is None:
                iPos = uPictureData.lower().find("content-type:")
                iPosEnd = uPictureData.find("\n",iPos)
                if iPos>-1 and iPosEnd>-1:
                    uHeader = uPictureData[iPos:iPosEnd]
                    iPos = uPictureData.find("\n\n")
                    if iPos > -1:
                        uPictureData=uPictureData[iPos+2:]
            if uHeader:
                uPictureType = uHeader.split("/")[-1]
            else:
                self.ShowWarning("Invaid URL/Content Type when pulling picture from device:"+str(uHeader),oSetting.uConfigName)
                uPictureType = uUrl.split(".")[-1]

            uPictureType = "."+uPictureType

        except Exception as e:
            self.ShowError(uMsg=u'Unexpected error reading picture by URL:', uParConfigName=oSetting.uConfigName, oException=e)

        return uPictureData,uPictureType

    def Split_IFV(self,oAction:cAction,uResponse:str,oSetting:cInterFaceSettings) -> None:
        # handles the return of Video Information Request
        uTmp:str=oAction.uGlobalDestVar
        if not oSetting.uRetVar==u'':
            oAction.uGlobalDestVar=oSetting.uRetVar

        aResponses:List=uResponse.split(',')
        if len(aResponses)>1:
            oSetting.oResultParser.SetVar2(aResponses[0], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Input Selection', uAddName=u"_video_input_selection")
            oSetting.oResultParser.SetVar2(aResponses[1], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Input Resolution', uAddName=u"_video_input_resolution")
        if len(aResponses)>2:
            oSetting.oResultParser.SetVar2(aResponses[2], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Input Color', uAddName=u"_video_input_color")
        if len(aResponses)>3:
            oSetting.oResultParser.SetVar2(aResponses[3], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Input Bits', uAddName=u"_video_input_bits")
        if len(aResponses)>4:
            oSetting.oResultParser.SetVar2(aResponses[4], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Selection', uAddName=u"_video_output_selection")
        if len(aResponses)>5:
            oSetting.oResultParser.SetVar2(aResponses[5], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Resolution', uAddName=u"_video_output_resolution")
        if len(aResponses)>6:
            oSetting.oResultParser.SetVar2(aResponses[6], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Color', uAddName=u"_video_output_color")
        if len(aResponses)>7:
            oSetting.oResultParser.SetVar2(aResponses[7], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Bits', uAddName=u"_video_output_bits")
        if len(aResponses)>8:
            oSetting.oResultParser.SetVar2(aResponses[8], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Effect', uAddName=u"_video_output_bits")

        if uTmp!=u'':
            oSetting.uRetVar=uTmp

    def ISCP_LMD_To_Text(self,uLMD:str) -> str:

        uRet:str = self.dLMD_Text.get(uLMD)
        if uRet is None:
            uRet=u"unknown"
        return uRet

    def InitLVM(self) -> None:
        self.dLMD_Text= {'00': u'STEREO',
                         '01': u'DIRECT',
                         '02': u'SURROUND',
                         '03': u'FILM',
                         '04': u'THX',
                         '05': u'ACTION',
                         '06': u'MUSICAL',
                         '07': u'MONO MOVIE',
                         '08': u'ORCHESTRA',
                         '09': u'UNPLUGGED',
                         '0A': u'STUDIO-MIX',
                         '0B': u'TV LOGIC',
                         '0C': u'ALL CH STEREO',
                         '0D': u'THEATER-DIMENSIONAL',
                         '0E': u'ENHANCED',
                         '0F': u'MONO',
                         '11': u'PURE AUDIO',
                         '12': u'MULTIPLEX',
                         '13': u'FULL MONO',
                         '14': u'DOLBY VIRTUAL',
                         '15': u'DTS Surround Sensation',
                         '16': u'Audyssey DSX',
                         '1F': u'Whole House Mode',
                         '40': u'5.1ch Surround',
                         '41': u'DTS ES',
                         '42': u'THX Cinema',
                         '43': u'THX Surround EX',
                         '44': u'THX Music',
                         '45': u'THX Games',
                         '50': u'THX Cinema',
                         '51': u'THX MusicMode',
                         '52': u'THX Games Mode',
                         '80': u'PLII/PLIIx Movie',
                         '81': u'PLII/PLIIx Music',
                         '82': u'Neo:X Cinema',
                         '83': u'Neo:X Music',
                         '84': u'PLII/PLIIx THX Cinema',
                         '85': u'Neo:X THX Cinema',
                         '86': u'PLII/PLIIx Game',
                         '87': u'Neural Surr',
                         '88': u'Neural THX',
                         '89': u'PLII/PLIIx THX Games',
                         '8A': u'Neo:X THX Games',
                         '8B': u'PLII/PLIIx THX Music',
                         '8C': u'Neo:X THX Music',
                         '8D': u'Neural THX Cinema',
                         '8E': u'Neural THX Music',
                         '8F': u'Neural THX Games',
                         '90': u'PLIIz Height',
                         '91': u'Neo:6 Cinema DTS Surround Sensation',
                         '92': u'Neo:6 Music DTS Surround Sensation',
                         '93': u'Neural Digital Music',
                         '94': u'PLIIz Height + THX Cinema',
                         '95': u'PLIIz Height + THX Music',
                         '96': u'PLIIz Height + THX Games',
                         '97': u'PLIIz Height + THX U2/S2 Cinema',
                         '98': u'PLIIz Height + THX U2/S2 Music',
                         '99': u'PLIIz Height + THX U2/S2 Games',
                         '9A': u'Neo:X Game',
                         'A0': u'PLIIx/PLII Movie + Audyssey DSX',
                         'A1': u'PLIIx/PLII Music + Audyssey DSX',
                         'A2': u'PLIIx/PLII Game + Audyssey DSX',
                         'A3': u'Neo:6 Cinema + Audyssey DSX',
                         'A4': u'Neo:6 Music + Audyssey DSX',
                         'A5': u'Neural Surround + Audyssey DSX',
                         'A6': u'Neural Digital Music + Audyssey DSX',
                         'A7': u'Dolby EX + Audyssey DSX',
                         'FF': u'Auto Surround'}



    '''
    def GenerateXMLFile(self):

        from collections import OrderedDict


                for sCommands in COMMANDS:
            # print sCommands

            print "  <!--\n      Section:",sCommands+ "\n  -->"
            for sSubCommand in COMMANDS[sCommands]:
                # print sSubCommand
                # print COMMANDS[sCommands][sSubCommand]
                oItems=COMMANDS[sCommands][sSubCommand]
                print "  <!--\n      Category:"+oItems['description']+ "\n  -->"
                #for oItem in oItems:
                if True:
                    for sValue in oItems['values']:
                        oValue=oItems['values'][sValue]

                        if not oValue['name']==None:
                            if type(oValue['name']).__name__=="str":
                                sName=oValue['name']
                            else:
                                sName=oValue['name'][0]
                        else:
                            sName="!!!!!!!!!!!!!!!!!value!!!!!!!!!!!!!!!!"

                        if not type(sValue).__name__=="str":
                            sValue="Varrange from "+ str(sValue[0])+" to "+str(sValue[1])

                        sDescription=oValue['description']
                        if type(sDescription).__name__=="unicode":
                            sDescription=sDescription.encode("utf-8","replace")

                        print "  <action string="codeset" name=\""+sCommands+"."+COMMANDS[sCommands][sSubCommand]['name']+"."+sName+"\" desc=\""+sDescription +  "\"  cmd=\""+sSubCommand+sValue+"\" />"
        '''

