# -*- coding: utf-8 -*-
# telnet

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

from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
from ORCA.vars.Replace      import ReplaceVars
from ORCA.vars.Access       import SetVar

from ORCA.utils.TypeConvert import ToUnicode

from ORCA.utils.wait.StartWait  import StartWait
from kivy.clock                 import Clock
import telnetlib
import socket
from threading                  import Thread

'''
<root>
  <repositorymanager>
    <entry>
      <name>Telnet</name>
      <description language='English'>Interface to send telnet commands</description>
      <description language='German'>Interface um Telnet Kommandos zu senden</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
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
        <file>telnet/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):
        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.bStopThreadEvent                         = False
            self.oTelnet                                  = None
            self.oThread                                  = None
            self.uRetVar                                  = u''
            self.uResponse                                = u''
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


        def ReadConfigFromIniFile(self,sConfigName):
            cBaseInterFaceSettings.ReadConfigFromIniFile(self,sConfigName)
            self.aIniSettings.uResultEndString           = self.aIniSettings.uResultEndString.replace('[LF]','\n')
            self.aIniSettings.uResultEndString           = self.aIniSettings.uResultEndString.replace('[CR]','\r')
            return

        def SetOption(self, socket, command, option):

            if command == telnetlib.DO and option == "\x18":
                # Promise we'll send a terminal type
                socket.send("%s%s\x18" % (telnetlib.IAC, telnetlib.WILL))
            elif command == telnetlib.DO and option == "\x01":
                # Pinky swear we'll echo
                socket.send("%s%s\x01" % (telnetlib.IAC, telnetlib.WILL))
            elif command == telnetlib.DO and option == "\x1f":
                # And we should probably tell the server we will send our window
                # size
                socket.send("%s%s\x1f" % (telnetlib.IAC, telnetlib.WILL))
            elif command == telnetlib.DO and option == "\x20":
                # Tell the server to sod off, we won't send the terminal speed
                socket.send("%s%s\x20" % (telnetlib.IAC, telnetlib.WONT))
            elif command == telnetlib.DO and option == "\x23":
                # Tell the server to sod off, we won't send an x-display terminal
                socket.send("%s%s\x23" % (telnetlib.IAC, telnetlib.WONT))
            elif command == telnetlib.DO and option == "\x27":
                # We will send the environment, though, since it might have nethack
                # specific options in it.
                socket.send("%s%s\x27" % (telnetlib.IAC, telnetlib.WILL))
            elif self.oTelnet.rawq.startswith("\xff\xfa\x27\x01\xff\xf0\xff\xfa"):
               # set a dummy environment
               # and set the terminal

                socket.send("%s%s\x27\x00%s%s%s" %
                            (telnetlib.IAC,
                             telnetlib.SB,
                             '\x00"OPTIONS"\x01"%s"' % "",
                             telnetlib.IAC,
                             telnetlib.SE))

                self.aIniSettings.uTerminalType = "linux"

                socket.send("%s%s\x18\x00%s%s%s" %
                            (telnetlib.IAC,
                             telnetlib.SB,
                             self.aIniSettings.uTerminalType,
                             telnetlib.IAC,
                             telnetlib.SE))

                # "xterm",

            else:
                socket.send("%s%s%s" % (telnetlib.IAC, telnetlib.WONT,option))

        def Connect(self):

            if not cBaseInterFaceSettings.Connect(self):
                return False

            try:
                try:
                    #due to a telnet unicode bug in python 2.7, we need to convert to string

                    self.ShowDebug(u'Connecting to %s:%s with user: [%s] , password: [%s]' % (str(self.aIniSettings.uHost) ,str(self.aIniSettings.uPort),self.aIniSettings.uUser,self.aIniSettings.uPassword))

                    self.oTelnet = telnetlib.Telnet(str(self.aIniSettings.uHost),str(self.aIniSettings.uPort),self.aIniSettings.fTimeOut)

                    oSocket = self.oTelnet.get_socket()
                    oSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

                    if not self.aIniSettings.uTerminalType      == u'':
                        self.oTelnet.set_option_negotiation_callback(self.SetOption)

                    if not self.aIniSettings.uUser==u'':
                        self.oTelnet.read_until("login: ",2)
                        self.ShowDebug(u'Sending Username')
                        self.oTelnet.write(str(self.aIniSettings.uUser) + "\n")
                        if not self.aIniSettings.uPassword==u'':
                            self.oTelnet.read_until("assword: ",5)
                            self.ShowDebug(u'Sending Password')
                            self.oTelnet.write(str(self.aIniSettings.uPassword + "\n"))
                except socket.gaierror as e:
                    self.ShowError(u'Cannot open telnet session:'+self.aIniSettings.uHost,e)
                    self.bOnError=True
                    return
                except socket.error as e:
                    self.ShowError(u'Connection refused:'+self.aIniSettings.uHost,e)
                    self.bOnError=True
                    return
                self.ShowDebug(u'Connected!')

                if self.oThread:
                    self.bStopThreadEvent = True
                    self.oThread.join()
                    self.oThread = None
                self.bStopThreadEvent = False

                self.oThread = Thread(target = self.Receive,)
                self.oThread.start()

                self.bIsConnected =True
            except Exception as e:
                self.ShowError(u'Cannot open socket #2:'+self.aIniSettings.uHost,e)
                self.bOnError=True

        def Disconnect(self):
            if not cBaseInterFaceSettings.Disconnect(self):
                return False
            self.bStopThreadEvent=True
            if self.oThread:
                self.oThread.join()
                self.oThread = None
            self.bOnError = False

        def Receive(self):
            #Main Listening Thread to receice Telnet messages

            #Loop until closed by external flag
            try:
                while not self.bStopThreadEvent:
                    if self.oTelnet is not None:
                        self.uResponse=u''
                        if not self.aIniSettings.uResultEndString==u'':
                            self.uResponse= self.oTelnet.read_until(self.aIniSettings.uResultEndString,10)
                        else:
                            self.uResponse= self.oTelnet.read_eager()
                        self.uResponse=ToUnicode(self.uResponse)
                        if not self.uResponse==u'':
                            uCmd,uRetVal=self.oInterFace.ParseResult(self.oAction,self.uResponse,self)
                            self.ShowDebug(u'Parsed Resonse:'+uRetVal)
                            if not self.uRetVar==u'':
                                SetVar(uVarName = self.uRetVar, oVarValue =  uRetVal)
                            # we have a notification issued by the device, so lets have a look, if we have a trigger assigned to it
                            oActionTrigger=self.GetTrigger(uRetVal)
                            if oActionTrigger is not None:
                                self.CallTrigger(oActionTrigger,uRetVal)
                            else:
                                self.ShowDebug(u'Discard message:'+uRetVal+":"+self.uResponse)
                            StartWait(0)
            except Exception as e:
                self.ShowError(u'Error Receiving Response:',e)
                self.bIsConnected=False

            try:
                self.oTelnet.write("exit\n")
                self.oTelnet.close()
            except Exception as e:
                self.ShowError(u'Error closing socket in Thread',e)


    def __init__(self):
        cBaseInterFace.__init__(self)
        self.aSettings      = {}
        self.oSetting       = None
        self.uResponse      = u''
        self.iWaitMs        = 2000

    def Init(self, uObjectName, oFnObject=None):
        cBaseInterFace.Init(self, uObjectName, oFnObject)
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

    def DeInit(self, **kwargs):
        cBaseInterFace.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def GetConfigJSON(self):
        cBaseInterFace.GetConfigJSON(self)
        return {"TerminalType":    {"active": "enabled", "order": 8, "type": "string", "title": "$lvar(IFACE_TELNET_3)", "desc": "$lvar(IFACE_TELNET_4)", "section": "$var(ObjectConfigSection)", "key": "TerminalType",    "default":"" },
                "ResultEndString": {"active": "enabled", "order": 9, "type": "string", "title": "$lvar(IFACE_TELNET_1)", "desc": "$lvar(IFACE_TELNET_2)", "section": "$var(ObjectConfigSection)", "key": "ResultEndString", "default": "[LF]"},
                }


    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        iTryCount=0
        iRet=1

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        oSetting.uRetVar=uRetVar

        uMsg=oAction.uCmd
        uMsg=ReplaceVars(uMsg,self.uObjectName+'/'+oSetting.uConfigName)
        uMsg=ReplaceVars(uMsg)

        #Logger.info ('Interface '+self.uObjectName+': Sending Command: '+sCommand + ' to '+oSetting.sHost+':'+oSetting.sPort)
        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                #time.sleep(2)
                try:
                    self.ShowInfo(u'Sending Command: "'+uMsg + u'" to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,oSetting.uConfigName)
                    uMsg=uMsg.replace('\\n','\n')
                    uMsg=uMsg.replace('\\r','\r')
                    #Bypass unicode bug in python 2.7
                    uMsg=str(uMsg)
                    if oAction.bWaitForResponse==True:
                        #All response comes to receiver thread, so we should hold the queue until vars are set
                        StartWait(self.iWaitMs)

                    oSetting.oTelnet.write(uMsg)
                    iRet=0
                    break
                except Exception as e:
                    self.ShowError(u'can\'t Send Message',oSetting.uConfigName,e)
                    iRet=1
                    oSetting.Disconnect()
        if oSetting.bIsConnected:
            if oSetting.aIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aIniSettings.iTimeToClose)
        return iRet

