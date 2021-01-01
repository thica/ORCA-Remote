# -*- coding: utf-8 -*-
# telnet

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

from __future__                             import annotations
from typing                                 import Optional
from typing                                 import Dict
from typing                                 import List

import telnetlib
import socket
from threading                              import Thread
from ORCA.interfaces.BaseInterface          import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings  import cBaseInterFaceSettings
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.utils.TypeConvert                 import ToInt
from ORCA.utils.wait.StartWait              import StartWait
from ORCA.vars.Access                       import SetVar
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.Action                            import cAction
from ORCA.utils.FileName                    import cFileName
from ORCA.actions.ReturnCode                import eReturnCode

'''
<root>
  <repositorymanager>
    <entry>
      <name>Telnet</name>
      <description language='English'>Interface to send telnet commands</description>
      <description language='German'>Interface um Telnet Kommandos zu senden</description>
      <author>Carsten Thielepape</author>
      <version>5.0.4</version>
      <minorcaversion>5.0.4</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/telnet</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/telnet.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>UPNP Discover</name>
        </dependency>
      </dependencies>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):
        def __init__(self,oInterFace:cInterface):
            super().__init__(oInterFace)
            self.bStopThreadEvent:bool                    = False
            self.oTelnet:Optional[telnetlib.Telnet]       = None
            self.oThread:Optional[Thread]                 = None
            self.uRetVar:str                              = u''
            self.uResponse:str                            = u''
            self.aIniSettings.fTimeOut                    = 2.0
            self.aIniSettings.iTimeToClose                = -1
            self.aIniSettings.uFNCodeset                  = u"Select"
            self.aIniSettings.uHost                       = u"discover"
            self.aIniSettings.uParseResultOption          = u'store'
            self.aIniSettings.uPort                       = u"23"
            self.aIniSettings.uDiscoverScriptName         = u"discover_upnp"
            self.aIniSettings.fDISCOVER_UPNP_timeout      = 5.0
            self.aIniSettings.uDISCOVER_UPNP_manufacturer = ""
            self.aIniSettings.uDISCOVER_UPNP_models       = u"[]"
            self.aIniSettings.uDISCOVER_UPNP_prettyname   = ""
            self.aIniSettings.uDISCOVER_UPNP_servicetypes = "upnp:rootdevice"

        def ReadConfigFromIniFile(self,uConfigName:str) -> None:
            super().ReadConfigFromIniFile(uConfigName=uConfigName)
            self.aIniSettings.uResultEndString           = self.aIniSettings.uResultEndString.replace('[LF]','\n')
            self.aIniSettings.uResultEndString           = self.aIniSettings.uResultEndString.replace('[CR]','\r')
            return

        def SetOption(self, oSocket:socket.socket, command, option:str) -> None:

            if command == telnetlib.DO and option == b"\x18":
                # Promise we'll send a terminal type
                oSocket.send(ToBytes("%s%s\x18" % (ToUnicode(telnetlib.IAC), ToUnicode(telnetlib.WILL))))
            elif command == telnetlib.DO and option == b"\x01":
                # Pinky swear we'll echo
                oSocket.send(ToBytes("%s%s\x01" % (ToUnicode(telnetlib.IAC), ToUnicode(telnetlib.WILL))))
            elif command == telnetlib.DO and option == b"\x1f":
                # And we should probably tell the server we will send our window
                # size
                oSocket.send(ToBytes("%s%s\x1f" % (ToUnicode(telnetlib.IAC), ToUnicode(telnetlib.WILL))))
            elif command == telnetlib.DO and option == b"\x20":
                # Tell the server to sod off, we won't send the terminal speed
                oSocket.send(ToBytes("%s%s\x20" % (ToUnicode(telnetlib.IAC), ToUnicode(telnetlib.WONT))))
            elif command == telnetlib.DO and option == b"\x23":
                # Tell the server to sod off, we won't send an x-display terminal
                oSocket.send(ToBytes("%s%s\x23" % (ToUnicode(telnetlib.IAC), ToUnicode(telnetlib.WONT))))
            elif command == telnetlib.DO and option == b"\x27":
                # We will send the environment, though, since it might have nethack
                # specific options in it.
                oSocket.send(ToBytes("%s%s\x27" % (ToUnicode(telnetlib.IAC), ToUnicode(telnetlib.WILL))))
            elif self.oTelnet.rawq.startswith(b"\xff\xfa\x27\x01\xff\xf0\xff\xfa"):
               # set a dummy environment
               # and set the terminal

                oSocket.send(ToBytes("%s%s\x27\x00%s%s%s" %
                            (ToUnicode(telnetlib.IAC),
                             ToUnicode(telnetlib.SB),
                             '\x00"OPTIONS"\x01"%s"' % "",
                             ToUnicode(telnetlib.IAC),
                             ToUnicode(telnetlib.SE))))

                self.aIniSettings.uTerminalType = "linux"

                oSocket.send(ToBytes("%s%s\x18\x00%s%s%s" %
                            (ToUnicode(telnetlib.IAC),
                             ToUnicode(telnetlib.SB),
                             self.aIniSettings.uTerminalType,
                             ToUnicode(telnetlib.IAC),
                             ToUnicode(telnetlib.SE))))

                # "xterm",

            else:
                oSocket.send(ToBytes("%s%s%s" % (ToUnicode(telnetlib.IAC), ToUnicode(telnetlib.WONT),option)))

        def Connect(self) -> bool:

            oSocket:socket.socket

            if not super().Connect():
                return False

            try:
                try:
                    self.ShowDebug(uMsg=u'Connecting to %s:%s with user: [%s] , password: [%s]' % (str(self.aIniSettings.uHost) ,str(self.aIniSettings.uPort),self.aIniSettings.uUser,self.aIniSettings.uPassword))
                    self.oTelnet = telnetlib.Telnet(ToBytes(self.aIniSettings.uHost),ToInt(self.aIniSettings.uPort),self.aIniSettings.fTimeOut)

                    oSocket = self.oTelnet.get_socket()
                    oSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

                    '''
                    if not self.aIniSettings.uTerminalType      == u'' and False:
                        self.oTelnet.set_option_negotiation_callback(self.SetOption)
                    '''

                    if not self.aIniSettings.uUser==u'':
                        self.oTelnet.read_until(ToBytes("login: "),2)
                        self.ShowDebug(uMsg=u'Sending Username')
                        self.oTelnet.write(ToBytes(self.aIniSettings.uUser + "\n"))
                        if not self.aIniSettings.uPassword==u'':
                            self.oTelnet.read_until(ToBytes("assword: "),5)
                            self.ShowDebug(uMsg=u'Sending Password')
                            self.oTelnet.write(ToBytes(self.aIniSettings.uPassword + "\n"))
                except socket.gaierror as e:
                    self.ShowError(uMsg=u'Cannot open telnet session:'+self.aIniSettings.uHost,oException=e)
                    self.bOnError=True
                    return False
                except socket.error as e:
                    self.ShowError(uMsg=u'Connection refused:'+self.aIniSettings.uHost,oException=e)
                    self.bOnError=True
                    return False
                self.ShowDebug(uMsg=u'Connected!')

                if self.oThread:
                    self.bStopThreadEvent = True
                    self.oThread.join()
                    self.oThread = None
                self.bStopThreadEvent = False

                self.oThread = Thread(target = self.Receive,)
                self.oThread.start()

                self.bIsConnected =True
            except Exception as e:
                self.ShowError(uMsg=u'Cannot open socket #2:'+self.aIniSettings.uHost,oException=e)
                self.bOnError=True
                return False
            return True

        def Disconnect(self) -> bool:

            if not super().Disconnect():
                return False
            self.bStopThreadEvent=True
            if self.oThread:
                self.oThread.join()
                self.oThread = None
            self.bOnError = False
            return True

        def Receive(self) -> None:
            #Main Listening Thread to receive Telnet messages

            aActionTrigger:List[cBaseTrigger]

            #Loop until closed by external flag
            try:
                while not self.bStopThreadEvent:
                    if self.oTelnet is not None:
                        self.uResponse=u''
                        bResponse:bytes
                        if not self.aIniSettings.uResultEndString==u'':
                            bResponse= self.oTelnet.read_until(ToBytes(self.aIniSettings.uResultEndString),10)
                        else:
                            bResponse= self.oTelnet.read_eager()
                        self.uResponse=ToUnicode(bResponse)
                        if not self.uResponse==u'':
                            uCmd,uRetVal=self.oInterFace.ParseResult(oAction=self.oAction,uResponse=self.uResponse,oSetting=self)
                            self.ShowDebug(uMsg=u'Parsed Resonse:'+uRetVal)
                            if not self.uRetVar==u'':
                                SetVar(uVarName = self.uRetVar, oVarValue =  uRetVal)
                            # we have a notification issued by the device, so lets have a look, if we have a trigger assigned to it
                            aActionTrigger=self.GetTrigger(uRetVal)
                            if len(aActionTrigger)>0:
                                for oActionTrigger in aActionTrigger:
                                    self.CallTrigger(oActionTrigger,uRetVal)
                            else:
                                self.ShowDebug(uMsg=u'Discard message:'+uRetVal+":"+self.uResponse)
                            StartWait(0)
            except Exception as e:
                self.ShowError(uMsg=u'Error Receiving Response:',oException=e)
                self.bIsConnected=False


            try:
                self.oTelnet.write(ToBytes("exit\n"))
                self.oTelnet.close()
            except Exception as e:
                self.ShowError(uMsg=u'Error closing socket in Thread',oException=e)


    def __init__(self):
        cInterFaceSettings = self.cInterFaceSettings
        super().__init__()
        self.dSettings:Dict                             = {}
        self.oSetting:Optional[cInterFaceSettings]      = None
        self.uResponse                                  = u''
        self.iWaitMs:int                                = 2000

    def Init(self, uObjectName: str, oFnObject: Optional[cFileName] = None) -> None:
        super().Init(uObjectName=uObjectName, oFnObject=oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['User']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Password']['active']                    = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['ParseResult']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['TokenizeString']['active']              = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self, **kwargs) -> None:
        super().DeInit(**kwargs)
        for uSettingName in self.dSettings:
            self.dSettings[uSettingName].DeInit()

    def GetConfigJSON(self) -> Dict:
        super().GetConfigJSON()
        return {"TerminalType":    {"active": "enabled", "order": 8, "type": "string", "title": "$lvar(IFACE_TELNET_3)", "desc": "$lvar(IFACE_TELNET_4)", "section": "$var(ObjectConfigSection)", "key": "TerminalType",    "default":"" },
                "ResultEndString": {"active": "enabled", "order": 9, "type": "string", "title": "$lvar(IFACE_TELNET_1)", "desc": "$lvar(IFACE_TELNET_2)", "section": "$var(ObjectConfigSection)", "key": "ResultEndString", "default": "[LF]"},
                }

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        super().SendCommand(oAction=oAction,oSetting=oSetting,uRetVar=uRetVar,bNoLogOut=bNoLogOut)

        iTryCount:int     = 0
        eRet:eReturnCode  = eReturnCode.Error
        uMsg:str
        byMsg:bytes

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        oSetting.uRetVar=uRetVar

        uMsg=oAction.uCmd
        uMsg=ReplaceVars(uMsg,self.uObjectName+'/'+oSetting.uConfigName)
        uMsg=ReplaceVars(uMsg)

        #Logger.info ('Interface '+self.uObjectName+': Sending Command: '+sCommand + ' to '+oSetting.sHost+':'+oSetting.sPort)
        while iTryCount<self.iMaxTryCount:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                #time.sleep(2)
                try:
                    self.ShowInfo(uMsg=u'Sending Command: "'+uMsg + u'" to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,uParConfigName=oSetting.uConfigName)
                    uMsg=uMsg.replace('\\n','\n')
                    uMsg=uMsg.replace('\\r','\r')
                    byMsg=ToBytes(uMsg)

                    if oAction.bWaitForResponse:
                        #All response comes to receiver thread, so we should hold the queue until vars are set
                        StartWait(self.iWaitMs)

                    oSetting.oTelnet.write(byMsg)
                    eRet = eReturnCode.Success
                    break

                except Exception as e:
                    self.ShowError(uMsg= u'can\'t Send Message',uParConfigName=oSetting.uConfigName,oException=e)
                    eRet = eReturnCode.Error
                    oSetting.Disconnect()
        self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet

