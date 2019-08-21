# -*- coding: utf-8 -*-
# WEBSOCKET

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

from ws4py.client.threadedclient                import WebSocketClient

from kivy.compat            import string_types


from ORCA.interfaces.BaseInterface              import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings      import cBaseInterFaceSettings
from ORCA.vars.Replace                          import ReplaceVars
from ORCA.vars.Access                           import SetVar
from ORCA.utils.TypeConvert                     import ToUnicode
from ORCA.utils.wait.StartWait                  import StartWait

from ORCA.utils.Sleep                           import fSleep
from kivy.clock                                 import Clock


'''
<root>
  <repositorymanager>
    <entry>
      <name>Websocket</name>
      <description language='English'>Sends commands via the Websocket protocol</description>
      <description language='German'>Sendet Befehle via dem Websocket protokoll</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/websocket</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/websocket.zip</sourcefile>
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
        <file>websocket/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):

        class cWebSocketClient(WebSocketClient):

            def SetSettingObject(self, oSetting):
                self.oSetting = oSetting

            def opened(self):
                self.oSetting.ShowDebug("Websocket opened")

            def closed(self, code, reason=None):
                self.oSetting.ShowDebug("Websocket closed! Code:%d Reason: %s" % (code, reason))

            def received_message(self, m):
                self.oSetting.Receive(m.data)

        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.oWebSocket                                        = None
            self.uRetVar                                           = u''

            # default config fits for KODI
            self.aIniSettings.uHost                       = u"discover"
            self.aIniSettings.uPort                       = u"9090"
            self.aIniSettings.uService                    = u"ws://$cvar(HOST):$cvar(PORT)/jsonrpc"

            self.aIniSettings.uFNCodeset                  = u"CODESET_websocket_KODI-Leia.xml"
            self.aIniSettings.uParseResultOption          = u'json'
            self.aIniSettings.uDiscoverScriptName         = u"discover_upnp"
            self.aIniSettings.fDISCOVER_UPNP_timeout      = 5.0
            self.aIniSettings.uDISCOVER_UPNP_models       = u'["Kodi"]'
            self.aIniSettings.uDISCOVER_UPNP_servicetypes = "upnp:rootdevice"
            self.aIniSettings.uDISCOVER_UPNP_manufacturer = "XBMC Foundation"
            self.aIniSettings.uDISCOVER_UPNP_prettyname   = ""
            self.aIniSettings.bDISCOVER_UPNP_returnport   = False

        def Connect(self):

            if not cBaseInterFaceSettings.Connect(self):
                return False

            self.ShowDebug(u'Interface trying to connect...')

            try:
                if self.oWebSocket is None or self.oWebSocket.sock is None:
                    uURL = ReplaceVars(self.aIniSettings.uService)
                    uURL = ReplaceVars(uURL,self.oInterFace.uObjectName+'/'+self.uConfigName+"CONFIG_")
                    self.oWebSocket=self.cWebSocketClient(uURL, heartbeat_freq=2.0)
                    self.oWebSocket.SetSettingObject(self)
                self.oWebSocket.connect()
                self.bInConnect   = True
                self.bIsConnected = True
                tRet= self.ExecuteStandardAction('logon')
                self.bInConnect = False
                self.bIsConnected =True
            except Exception as e:
                self.ShowError(u'Interface not connected: Cannot open socket #2:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.bOnError=True
                return

            self.ShowDebug(u'Interface connected!')

        def Disconnect(self):

            if not cBaseInterFaceSettings.Disconnect(self):
                self.ShowDebug(u'Interface Disconnect #1: Connection is already closed, no further actions')
                return False
            self.ShowDebug(u'Interface Disconnect #2:Closing Connection')

            try:
                tRet = self.ExecuteStandardAction('logoff')
                self.oWebSocket.close()
            except Exception:
                pass
            self.bOnError = False

        def Receive(self, uResponse):
            uResponse = ToUnicode(uResponse)
            if self.oAction is not None:
                uCmd,uRetVal=self.oInterFace.ParseResult(self.oAction,uResponse,self)
                self.ShowDebug(u'Parsed Respones:'+uRetVal)
                if not self.uRetVar==u'' and not uRetVal==u'':
                    SetVar(uVarName = self.uRetVar, oVarValue = uRetVal)
                # We do not need to wait for an response anymore
                StartWait(0)
                self.oAction=None
            else:
                oAction = self.dStandardActions["defaultresponse"]
                if oAction:
                    uCommand = self.oInterFace.ParseResult(oAction, uResponse, self)
                    if not isinstance(uCommand, string_types):
                        if len(uCommand)>0:
                            uCommand = uCommand[1]

                    # we have a notification issued by the device, so lets have a look, if we have a trigger assigned to it
                    oActionTrigger=self.GetTrigger(uCommand)
                    if oActionTrigger is not None:
                        self.CallTrigger(oActionTrigger,uResponse)
                    else:
                        self.ShowDebug(u'Discard message:'+uCommand +':'+uResponse)

    def __init__(self):
        cBaseInterFace.__init__(self)
        self.aSettings      = {}
        self.oSetting       = None
        self.uResponse      = u''
        self.iWaitMs        = 100

    def Init(self, uObjectName, oFnObject=None):
        cBaseInterFace.Init(self, uObjectName, oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['User']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Password']['active']                    = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def GetConfigJSON(self):
        return {"Service": {"active": "enabled", "order": 3, "type": "string",         "title": "$lvar(IFACE_WEBSOCKET_1)", "desc": "$lvar(IFACE_WEBSOCKET_2)", "section": "$var(ObjectConfigSection)","key": "Service",                  "default":"ws://$cvar(HOST):$cvar(PORT)/jsonrpc"}}

    def DeInit(self, **kwargs):
        cBaseInterFace.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        iTryCount=0
        iRet=1
        #Logger.info ('Interface '+self.sInterFaceName+': Sending Command: '+sCommand + ' to '+oSetting.sHost+':'+oSetting.sPort)
        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()
            # we need to verify if we are really connected, as the connection might have died
            # and .sendall will not return on error in this case
            #bIsConnected=oSetting.IsConnected()

            if oSetting.bIsConnected:
                uMsg=oAction.uCmd
                try:

                    uMsg=ReplaceVars(uMsg,self.uObjectName+'/'+oSetting.uConfigName)
                    uMsg=ReplaceVars(uMsg)
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar,self.uObjectName+'/'+oSetting.uConfigName)
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar)

                    oSetting.uMsg=uMsg
                    oSetting.uRetVar=uRetVar
                    oSetting.uRetVar=uRetVar
                    self.ShowInfo (u'Sending Command: '+uMsg + ' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,oSetting.uConfigName)
                    #All response comes to receiver thread, so we should hold the queue until vars are set
                    if oSetting.oAction.bWaitForResponse:
                        StartWait(self.iWaitMs)
                    oSetting.oWebSocket.send(uMsg)
                    fSleep(0.01)
                    iRet=0
                    break
                except Exception as e:
                    self.ShowError(u'Can\'t send message',oSetting.uConfigName,e)
                    iRet=1
                    oSetting.Disconnect()
                    oSetting.bOnError=True
                    if not uRetVar==u'':
                        SetVar(uVarName = uRetVar, oVarValue = u"Error")
            else:
                if not uRetVar==u'':
                    SetVar(uVarName = uRetVar, oVarValue = u"Error")

        if oSetting.bIsConnected:
            if oSetting.aIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aIniSettings.iTimeToClose)
        return iRet

