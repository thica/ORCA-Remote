# -*- coding: utf-8 -*-
# Keene Kira

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

from __future__                 import annotations

from typing                     import Optional
from typing                     import Dict
from typing                     import List

import socket

from ORCA.utils.LogError        import LogError
from ORCA.utils.TypeConvert     import ToHex
from ORCA.utils.TypeConvert     import ToInt
from ORCA.utils.TypeConvert     import ToBytes
from ORCA.utils.TypeConvert     import ToUnicode
from ORCA.vars.Replace          import ReplaceVars
from ORCA.utils.FileName        import cFileName
from ORCA.Action                import cAction
from ORCA.actions.ReturnCode    import eReturnCode

'''
<root>
  <repositorymanager>
    <entry>
      <name>Keene Kira IR Control</name>
      <description language='English'>Sends commands to Keene Kira devices to submit IR comands</description>
      <description language='German'>Sendet Befehle zu Keene Kira Geräten um IR Befehle zu senden</description>
      <author>Carsten Thielepape</author>
      <version>5.0.0</version>
      <minorcaversion>5.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/Keene_Kira</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/Keene_Kira.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>Keene Kira Discover</name>
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

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interfaces.generic_infrared.interface import cInterface as cBaseInterFaceInfrared
else:
    cBaseInterFaceInfrared = Globals.oInterFaces.LoadInterface('generic_infrared').GetClass("cInterface")

class cInterface(cBaseInterFaceInfrared):

    class cInterFaceSettings(cBaseInterFaceInfrared.cInterFaceSettings):
        def __init__(self,oInterFace:cInterface):
            super().__init__(oInterFace)
            self.oSocket:Optional[socket.socket]    = None
            self.aIniSettings.uHost                 = u"discover"
            self.aIniSettings.uPort                 = u"65432"
            self.aIniSettings.uFNCodeset            = u"Select"
            self.aIniSettings.uDiscoverScriptName   = u"discover_kira"
            self.aIniSettings.iTimeToClose          = 0
            self.aIniSettings.fTimeOut              = 2.0
            self.bIsConnected                       = False
            self.bOnError                           = False

        def Connect(self) -> bool:

            if not super().Connect():
                return False
            try:
                for res in socket.getaddrinfo(self.aIniSettings.uHost, int(self.aIniSettings.uPort), socket.AF_INET, socket.SOCK_DGRAM):
                    af, socktype, proto, canonname, sa = res
                    try:
                        self.oSocket = socket.socket(af, socktype, proto)
                        self.oSocket.bind(('', int(self.oAction.uPort)))
                        self.oSocket.settimeout(5.0)
                    except socket.error:
                        self.oSocket = None
                        continue
                    break
                if self.oSocket is None:
                    self.ShowError(uMsg=u'Cannot open socket'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort)
                    self.bOnError=True
                    return False
                self.bIsConnected =True
                return True

            except Exception as e:
                self.ShowError(uMsg=u'Cannot open socket #2'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,oException=e)
                self.bOnError=True
                return False

        def Disconnect(self) -> bool:
            if super().Disconnect():
                return False
            try:
                if self.oSocket:
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

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        super().SendCommand(oAction=oAction,oSetting=oSetting,uRetVar=uRetVar,bNoLogOut=bNoLogOut)

        eRet:eReturnCode = eReturnCode.Error

        if oAction.uCCF_Code != u"":
            # noinspection PyUnresolvedReferences
            oAction.uCmd=CCfToKeene(oAction.uCCF_Code,ToInt(oAction.uRepeatCount))
            oAction.uCCF_Code = u""

        uCmd:str=ReplaceVars(oAction.uCmd)

        self.ShowInfo(uMsg=u'Sending Command: '+uCmd + u' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort)

        oSetting.Connect()
        if oSetting.bIsConnected:
            uMsg=uCmd+u'\r\n'
            try:
                uMsg=ReplaceVars(uMsg,self.uObjectName+'/'+oSetting.uConfigName)
                oSetting.oSocket.sendto(ToBytes(uMsg), (oSetting.aIniSettings.uHost, int(oSetting.aIniSettings.uPort)))
                byResponse, addr =  oSetting.oSocket.recvfrom(self.iBufferSize)
                uResponse = ToUnicode(byResponse)
                self.ShowDebug(uMsg=u'Response'+uResponse,uParConfigName=oSetting.uConfigName)
                if 'ACK' in uResponse:
                    eRet = eReturnCode.Success
                else:
                    eRet = eReturnCode.Error
            except Exception as e:
                if str(e)!="timed out":
                    self.ShowError(uMsg=u'Can\'t send message',uParConfigName=oSetting.uConfigName,oException=e)
                else:
                    self.ShowWarning(uMsg=u'Can\'t send message: time out',uParConfigName=oSetting.uConfigName)

                eRet = eReturnCode.Error

        self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet

def CCfToKeene(uCCFString:str,iRepeatCount:int):
    iX:int           = 0
    iy:int           = 0
    iMyInt:List      = []
    aBurst_Time:List = []

    if uCCFString=='':
        return uCCFString
    if uCCFString[0]=='{':
        return uCCFString

    uData:str        = uCCFString.strip()
    iCodeLength:int = len(uData)
    bError:bool     = True
    try:

        while iX<255:
            aBurst_Time.append(0)
            iX += 1

        iX=0
        while iX<iCodeLength:
            uTmpStr = uData[iX: iX + 4]
            aBurst_Time[iy]=int(uTmpStr,16)
            iy += 1
            iX += 5

        iFreq = int (4145 / aBurst_Time[1])

        iPair_Count = aBurst_Time[2]
        if iPair_Count == 0:
            iPair_Count = aBurst_Time[3]

        iX=0
        while iX<iy:
            iMyInt.append(0)
            iX += 1

        iMyInt[0]       = int(iFreq * 256 + iPair_Count)
        iCycle_time     = 1000 / iFreq
        iLead_in        = aBurst_Time[4] * iCycle_time
        iMyInt[1]       = iLead_in
        iMyInt[2]       = aBurst_Time[5] * iCycle_time # lead space
        iPair_Count    -= 1  # only loop data pairs
        iX              = 0
        iEnd            = iPair_Count * 2

        while iX<iEnd:
            iTint = int(aBurst_Time[iX + 6] * iCycle_time)
            iMyInt[iX + 3] = iTint
            iX += 1

        iMyInt[iX + 2] = 8192   # over write the lead out space with 2000 X is one over when exits from for loop
        uData = ""

        iX              = 0
        iEnd            = (iPair_Count * 2) + 3
        while iX<iEnd:
            uData = uData + ToHex(iMyInt[iX]) + " "
            iX += 1
        bError = False
    except Exception as e:
        LogError(uMsg = 'CCfToKeene:Can''t Convert',oException=e)
        LogError(uMsg = uCCFString)

    if bError:
        return ""
    else:
        uRet="K "+ uData.strip().upper()
        if iRepeatCount>1:
            uRet=uRet+' 4000 '+str(iRepeatCount)
        return uRet


