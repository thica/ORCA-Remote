# -*- coding: utf-8 -*-
# ITach

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

import socket

from kivy.logger            import Logger
from kivy.clock             import Clock

from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.TypeConvert import ToInt
from ORCA.utils.PyXSocket   import cPyXSocket
import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>iTach IR Control</name>
      <description language='English'>Sends commands to iTach devices to submit IR comands</description>
      <description language='German'>Sendet Befehle zu iTach Geräten um IR Befehle zu senden</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/iTach</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/iTach.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>iTach Discover</name>
        </dependency>
        <dependency>
          <type>interfaces</type>
          <name>Generic Infrared Interface</name>
        </dependency>
      </dependencies>
      <skipfiles>
        <file>iTach/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

oBaseInterFaceInfrared = Globals.oInterFaces.LoadInterface('generic_infrared')

class cInterface(oBaseInterFaceInfrared.cInterface):

    class cInterFaceSettings(oBaseInterFaceInfrared.cInterface.cInterFaceSettings):
        def __init__(self,oInterFace):
            oBaseInterFaceInfrared.cInterface.cInterFaceSettings.__init__(self,oInterFace)
            self.oSocket                               = None
            self.aIniSettings.uHost                    = u"discover"
            self.aIniSettings.uPort                    = u"4998"
            self.aIniSettings.iModule                  = 3
            self.aIniSettings.iConnector               = 1
            self.aIniSettings.uDiscoverScriptName      = u"discover_itach"
            self.bIsConnected                          = False
            self.bOnError                              = False

        def Connect(self):

            if not oBaseInterFaceInfrared.cInterface.cInterFaceSettings.Connect(self):
                return False

            if self.aIniSettings.uHost=='':
                return False

            try:
                for res in socket.getaddrinfo(self.aIniSettings.uHost, int(self.aIniSettings.uPort), socket.AF_INET, socket.SOCK_STREAM):
                    af, socktype, proto, canonname, sa = res
                    try:
                        self.oSocket = cPyXSocket(af, socktype, proto)
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
                    return False
                self.bIsConnected = True
                return True

            except Exception as e:
                self.ShowError(u'Cannot open socket #2'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.bOnError=True
                return False

        def Disconnect(self):
            if not oBaseInterFaceInfrared.cInterface.cInterFaceSettings.Disconnect(self):
                return False
            try:
                self.oSocket.close()
                self.bOnError = False
            except Exception as e:
                self.ShowError(u'can\'t Disconnect'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)

    def __init__(self):
        oBaseInterFaceInfrared.cInterface.__init__(self)
        self.aSettings   = {}
        self.oSetting    = None
        self.uResponse   = u''
        self.iBufferSize = 1024
        self.sResponse   = ''
        # this starts discover in background
        Globals.oScripts.LoadScript("discover_itach")
        self.aDiscoverScriptsWhiteList = ["iTach (Global Cache)"]

    def Init(self, uObjectName, oFnObject=None):
        cBaseInterFace.Init(self,uObjectName, oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self, **kwargs):
        oBaseInterFaceInfrared.cInterface.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    # noinspection PyMethodMayBeStatic
    def GetConfigJSON(self):
        return {"Connector": {"active": "enabled", "order": 3, "type": "numeric",        "title": "$lvar(IFACE_ITACH_1)",   "desc": "$lvar(IFACE_ITACH_2)", "section": "$var(ObjectConfigSection)","key": "Connector",               "default":"3"          },
                "Module":    {"active": "enabled", "order": 4, "type": "numeric",        "title": "$lvar(IFACE_ITACH_3)",   "desc": "$lvar(IFACE_ITACH_4)", "section": "$var(ObjectConfigSection)","key": "Module",                  "default":"1"          }
                }

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        if oAction.uCCF_Code:
            oAction.uCmd=CCF2ITach(oAction.uCCF_Code,ToInt(oAction.uRepeatCount))
            oAction.uCCF_Code = u""

        uCmd=ReplaceVars(oAction.uCmd,self.uObjectName+u'/'+oSetting.uConfigName)
        uCmd=ReplaceVars(uCmd)
        self.ShowInfo(u'Sending Command: '+uCmd + u' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,oSetting.uConfigName)

        oSetting.Connect()
        iRet=1
        if oSetting.bIsConnected:
            uMsg=uCmd+u'\r\n'
            try:
                oSetting.oSocket.SendAll(uMsg)
                self.sResponse = oSetting.oSocket.recv(self.iBufferSize)
                Logger.debug(u'Interface '+self.uObjectName+': resonse:'+self.sResponse)
                self.ShowDebug(u'Response'+self.sResponse,oSetting.uConfigName)
                if 'completeir' in self.sResponse:
                    iRet=0
                else:
                    iRet=1
            except Exception as e:
                self.ShowError(u'can\'t Send Message',u'',e)
                iRet=1
        if oSetting.bIsConnected:
            if oSetting.aIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aIniSettings.iTimeToClose)
        return iRet

iSeq = 0

def CCF2ITach(uCCFString,iRepeatCount):
    global iSeq
    uDelimiter   = u' '
    iSeq         = iSeq +1
    aArray       = uCCFString.split(uDelimiter)
    # iNumElements = len(aArray)
    iFreqVal     = int(aArray[1],16)
    iFreq        = ((((41450 / iFreqVal) + 5) / 10) * 1000)
    uFinalString = "sendir,$cvar(CONFIG_MODULE):$cvar(CONFIG_CONNECTOR)," + str(iSeq) + "," + str(iFreq) + ","+str(iRepeatCount)+",1"

    for uElement in aArray[4:]:
        iVal = int(uElement,16)
        uFinalString = uFinalString + "," + str(iVal)
    return uFinalString

