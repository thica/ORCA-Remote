# -*- coding: utf-8 -*-
# ITach

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

from __future__                     import annotations
from typing                         import Optional
from typing                         import Dict
from typing                         import List
import socket

from ORCA.vars.Replace              import ReplaceVars
from ORCA.utils.FileName            import cFileName
from ORCA.utils.TypeConvert         import ToInt
from ORCA.utils.TypeConvert         import ToBytes
from ORCA.utils.TypeConvert         import ToUnicode
from ORCA.Action                    import cAction
from ORCA.actions.ReturnCode        import eReturnCode

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>iTach IR Control</name>
      <description language='English'>Sends commands to iTach devices to submit IR comands</description>
      <description language='German'>Sendet Befehle zu iTach Geräten um IR Befehle zu senden</description>
      <author>Carsten Thielepape</author>
      <version>5.0.1</version>
      <minorcaversion>5.0.1</minorcaversion>
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
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interfaces.generic_infrared.interface import cInterface as cBaseInterFaceInfrared
else:
    cBaseInterFaceInfrared = Globals.oInterFaces.LoadInterface('generic_infrared').GetClass("cInterface")

class cInterface(cBaseInterFaceInfrared):

    class cInterFaceSettings(cBaseInterFaceInfrared.cInterFaceSettings):
        def __init__(self,oInterFace:cInterface):
            super().__init__(oInterFace)
            self.oSocket:Optional[socket.socket]       = None
            self.aIniSettings.uHost                    = u"discover"
            self.aIniSettings.uPort                    = u"4998"
            self.aIniSettings.iModule                  = 3
            self.aIniSettings.iConnector               = 1
            self.aIniSettings.uDiscoverScriptName      = u"discover_itach"
            self.bIsConnected                          = False
            self.bOnError                              = False

        def Connect(self) -> bool:

            if not super().Connect():
                return False

            if self.aIniSettings.uHost=='':
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
                    self.ShowError(uMsg=u'Cannot open socket'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort)
                    self.bOnError=True
                    return False
                self.bIsConnected = True
                return True

            except Exception as e:
                self.ShowError(uMsg=u'Cannot open socket #2'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,oException=e)
                self.bOnError=True
                return False

        def Disconnect(self) -> bool:
            if not super().Disconnect():
                return False
            try:
                self.oSocket.close()
                self.bOnError = False
                return True
            except Exception as e:
                self.ShowError(uMsg=u'can\'t Disconnect'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,oException=e)
                return False

    def __init__(self):
        cInterFaceSettings = self.cInterFaceSettings
        super().__init__()
        self.dSettings:Dict                             = {}
        self.oSetting:Optional[cInterFaceSettings]      = None
        self.iBufferSize:int                            = 1024
        # this starts discover in background
        Globals.oScripts.LoadScript("discover_itach")
        self.aDiscoverScriptsWhiteList = ["iTach (Global Cache)"]

    def Init(self, uObjectName: str, oFnObject: cFileName = None) -> None:

        super().Init(uObjectName=uObjectName, oFnObject=oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self, **kwargs) -> None:
        super().DeInit(**kwargs)
        for uSettingName in self.dSettings:
            self.dSettings[uSettingName].DeInit()

    # noinspection PyMethodMayBeStatic
    def GetConfigJSON(self) -> Dict:
        return {"Connector": {"active": "enabled", "order": 3, "type": "numeric",        "title": "$lvar(IFACE_ITACH_1)",   "desc": "$lvar(IFACE_ITACH_2)", "section": "$var(ObjectConfigSection)","key": "Connector",               "default":"3"          },
                "Module":    {"active": "enabled", "order": 4, "type": "numeric",        "title": "$lvar(IFACE_ITACH_3)",   "desc": "$lvar(IFACE_ITACH_4)", "section": "$var(ObjectConfigSection)","key": "Module",                  "default":"1"          }
                }

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        super().SendCommand(oAction=oAction,oSetting=oSetting,uRetVar=uRetVar,bNoLogOut=bNoLogOut)
        eRet:eReturnCode = eReturnCode.Error

        if oAction.uCCF_Code:
            # noinspection PyUnresolvedReferences
            oAction.uCmd=CCF2ITach(oAction.uCCF_Code,ToInt(oAction.uRepeatCount))
            oAction.uCCF_Code = u""

        uCmd:str=ReplaceVars(oAction.uCmd,self.uObjectName+u'/'+oSetting.uConfigName)
        uCmd=ReplaceVars(uCmd)
        self.ShowInfo(uMsg=u'Sending Command: '+uCmd + u' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort)

        oSetting.Connect()
        if oSetting.bIsConnected:
            uMsg:str=uCmd+u'\r\n'
            try:
                oSetting.oSocket.sendall(ToBytes(uMsg))
                byResponse = oSetting.oSocket.recv(self.iBufferSize)
                self.ShowDebug(uMsg=u'Response'+ToUnicode(byResponse),uParConfigName=oSetting.uConfigName)
                if 'completeir' in ToUnicode(byResponse):
                    eRet = eReturnCode.Success
                else:
                    eRet = eReturnCode.Error
            except Exception as e:
                self.ShowError(uMsg=u'can\'t Send Message',uParConfigName=u'',oException=e)
                eRet = eReturnCode.Error

        self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet

iSeq = 0

def CCF2ITach(uCCFString:str,iRepeatCount:int) -> str:
    global iSeq
    uDelimiter:str   = u' '
    iSeq            += 1
    aArray:List      = uCCFString.split(uDelimiter)
    # iNumElements = len(aArray)
    iFreqVal:int     = int(aArray[1],16)
    iFreq:int        = int((((41450 / iFreqVal) + 5) / 10) * 1000)
    uFinalString:str = "sendir,$cvar(CONFIG_MODULE):$cvar(CONFIG_CONNECTOR)," + str(iSeq) + "," + str(iFreq) + ","+str(iRepeatCount)+",1"

    for uElement in aArray[4:]:
        iVal = int(uElement,16)
        uFinalString = uFinalString + "," + str(iVal)
    return uFinalString

