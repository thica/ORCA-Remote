# -*- coding: utf-8 -*-
# aquos
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

from kivy.logger            import Logger
from kivy.clock             import Clock
import socket


'''
<root>
  <repositorymanager>
    <entry>
      <name>Sharp Aquos (IP)</name>
      <description language='English'>SHARP Aquos IP Interface (Non-EU models) This is under development and likely not working</description>
      <description language='German'>SHARP Aquos IP Interface (Nicht EU Modelle) Nicht fertiggestellt und wahrscheinlich nicht funktionierend</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/aquos_v1</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/aquos_v1.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>aquos_v1/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):
        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.oSocket      = None

            self.aIniSettings.uHost                    = u"discover"
            self.aIniSettings.uPort                    = u"4998"
            self.aIniSettings.uUser                    = u"user"
            self.aIniSettings.uPassword                = u"pass"
            self.aIniSettings.uFNCodeset               = u"CODESET_aquos_v1_AQUOS.xml"
            self.aIniSettings.fTimeOut                 = 2.0
            self.aIniSettings.iTimeToClose             = -1
            self.aIniSettings.uDiscoverScriptName      = u"discover_upnp"
            self.sResponse                             = ''

        def Connect(self):

            if not cBaseInterFaceSettings.Connect(self):
                return False
            try:
                for res in socket.getaddrinfo(self.aIniSettings.uHost, int(self.aIniSettings.uPort), socket.AF_INET, socket.SOCK_STREAM):
                    af, socktype, proto, canonname, sa = res
                    try:
                        self.oSocket = socket.socket(af, socktype, proto)
                        self.oSocket.settimeout(5.0)
                    except socket.error:
                        self.oSocket = None
                        continue
                    try:
                        self.oSocket.connect(sa)
                    except socket.error:
                        self.oSocket.close()
                        self.oSocket = None
                        continue
                    break
                if self.oSocket is None:
                    self.ShowError(u'Cannot open socket'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort)
                    self.bOnError=True
                    return
                if not self.aIniSettings.uUser==u'':
                    self.oSocket.send(self.aIniSettings.uUser + "\r" + self.aIniSettings.uPassword + "\r")
                    # Receive the prompts (will be "Login:\r\nPassword:")
                    self.sResponse = self.oSocket.recv(2048)
                    self.ShowDebug(u'Login Response'+self.sResponse)

                self.oSocket.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.bIsConnected =True
            except Exception as e:
                self.ShowError(u'Cannot open socket #2'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.bOnError=True

        def Disconnect(self):
            if not cBaseInterFaceSettings.Disconnect(self):
                return False
            try:
                self.oSocket.close()
                self.bOnError = False
            except Exception as e:
                self.ShowError(u'Cant Disconnect'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)

    def __init__(self):
        cBaseInterFace.__init__(self)
        self.aSettings      = {}
        self.oSetting       = None
        self.uResponse      = u''
        self.iBufferSize    = 1024

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


    def DeInit(self, **kwargs):
        cBaseInterFace.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)
        uCmd=oAction.uCmd
        uCmd=(uCmd+"       ")[:8]
        self.ShowInfo(u'Sending Command: '+uCmd + u' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,oSetting.uConfigName)

        oSetting.Connect()
        iRet=1
        if oSetting.bIsConnected:
            uMsg=uCmd+u'\r'
            try:
                uMsg=ReplaceVars(uMsg,self.uObjectName+'/'+oSetting.uConfigName)
                uMsg=ReplaceVars(uMsg)
                oSetting.oSocket.sendall(uMsg)
                self.sResponse = oSetting.oSocket.recv(self.iBufferSize)
                Logger.debug(u'Interface '+self.uObjectName+': resonse:'+self.sResponse)
                self.ShowDebug(u'Response'+self.sResponse,oSetting.uConfigName)

                if 'OK' in self.sResponse:
                    iRet=0
                else:
                    iRet=1
            except Exception as e:
                self.ShowError(u'Cant Send Message',u'',e)
                iRet=1
        if oSetting.bIsConnected:
            if oSetting.aIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aIniSettings.iTimeToClose)

        self.iLastRet=iRet
        return iRet
