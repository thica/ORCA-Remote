# -*- coding: utf-8 -*-
# Keene Kira

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

from kivy.clock import Clock

from ORCA.Compat                import PY2
from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.utils.LogError        import LogError
from ORCA.utils.TypeConvert     import ToHex
from ORCA.utils.TypeConvert     import ToInt
from ORCA.utils.TypeConvert     import ToBytes
from ORCA.utils.TypeConvert     import ToUnicode
from ORCA.vars.Replace          import ReplaceVars

'''
<root>
  <repositorymanager>
    <entry>
      <name>Keene Kira IR Control</name>
      <description language='English'>Sends commands to Keene Kira devices to submit IR comands</description>
      <description language='German'>Sendet Befehle zu Keene Kira Geräten um IR Befehle zu senden</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
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
        <file>Keene_Kira/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

import ORCA.Globals as Globals

oBaseInterFaceInfrared = Globals.oInterFaces.LoadInterface('generic_infrared')


class cInterface(oBaseInterFaceInfrared.cInterface):

    class cInterFaceSettings(oBaseInterFaceInfrared.cInterface.cInterFaceSettings):
        def __init__(self,oInterFace):
            oBaseInterFaceInfrared.cInterface.cInterFaceSettings.__init__(self,oInterFace)
            self.oSocket      = None
            self.aInterFaceIniSettings.uHost = u"discover"
            self.aInterFaceIniSettings.uPort = u"65432"
            self.aInterFaceIniSettings.uFNCodeset = u"Select"
            self.aInterFaceIniSettings.uDiscoverScriptName = u"discover_kira"
            self.aInterFaceIniSettings.iTimeToClose             = 0
            self.aInterFaceIniSettings.fTimeOut = 2.0

        def Connect(self):

            if not oBaseInterFaceInfrared.cInterface.cInterFaceSettings.Connect(self):
                return False
            try:
                for res in socket.getaddrinfo(self.aInterFaceIniSettings.uHost, int(self.aInterFaceIniSettings.uPort), socket.AF_INET, socket.SOCK_DGRAM):
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
                    self.ShowError(u'Cannot open socket'+self.aInterFaceIniSettings.uHost+':'+self.aInterFaceIniSettings.uPort)
                    self.bOnError=True
                    return
                self.bIsConnected =True

            except Exception as e:
                self.ShowError(u'Cannot open socket #2'+self.aInterFaceIniSettings.uHost+':'+self.aInterFaceIniSettings.uPort,e)
                self.bOnError=True

        def Disconnect(self):
            if oBaseInterFaceInfrared.cInterface.cInterFaceSettings.Disconnect(self):
                return False
            try:
                if self.oSocket:
                    self.oSocket.close()
                self.bOnError = False
            except Exception as e:
                self.ShowError(u'can\'t Disconnect'+self.aInterFaceIniSettings.uHost+':'+self.aInterFaceIniSettings.uPort,e)


    def __init__(self):
        oBaseInterFaceInfrared.cInterface.__init__(self)
        self.aSettings   = {}
        self.oSetting = None
        self.uResponse = u''
        self.iBufferSize=1024

    def Init(self, uInterFaceName, oFnInterFace=None):
        cBaseInterFace.Init(self, uInterFaceName, oFnInterFace)
        self.oInterFaceConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oInterFaceConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oInterFaceConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oInterFaceConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oInterFaceConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self, **kwargs):
        oBaseInterFaceInfrared.cInterface.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        iRet=1

        if oAction.uCCF_Code != u"":
            oAction.uCmd=CCfToKeene(oAction.uCCF_Code,ToInt(oAction.uRepeatCount))
            oAction.uCCF_Code = u""

        uCmd=ReplaceVars(oAction.uCmd)

        self.ShowInfo(u'Sending Command: '+uCmd + u' to '+oSetting.aInterFaceIniSettings.uHost+':'+oSetting.aInterFaceIniSettings.uPort,oSetting.uConfigName)

        oSetting.Connect()
        if oSetting.bIsConnected:
            uMsg=uCmd+u'\r\n'
            try:
                uMsg=ReplaceVars(uMsg,self.uInterFaceName+'/'+oSetting.uConfigName)
                if PY2:
                    oSetting.oSocket.sendto(uMsg, (oSetting.aInterFaceIniSettings.uHost, int(oSetting.aInterFaceIniSettings.uPort)))
                else:
                    oSetting.oSocket.sendto(ToBytes(uMsg), (oSetting.aInterFaceIniSettings.uHost, int(oSetting.aInterFaceIniSettings.uPort)))
                self.sResponse, addr =  oSetting.oSocket.recvfrom(self.iBufferSize)
                if not PY2:
                    self.sResponse = ToUnicode(self.sResponse)
                self.ShowDebug(u'Response'+self.sResponse,oSetting.uConfigName)
                if 'ACK' in self.sResponse:
                    iRet=0
                else:
                    iRet=1
            except Exception as e:
                if e.message!="timed out":
                    self.ShowError(u'Can\'t send message',oSetting.uConfigName,e)
                else:
                    self.ShowWarning(u'Can\'t send message: time out',oSetting.uConfigName)

                iRet=1
        if oSetting.bIsConnected:
            if oSetting.aInterFaceIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aInterFaceIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aInterFaceIniSettings.iTimeToClose)
        return iRet

def CCfToKeene(sCCFString,iRepeatCount):
    iX          = 0
    iy          = 0
    sTmpStr     = ''
    iFreq       = 0
    iPair_Count = 0
    iLead_in    = 0
    iMyInt      = []
    iTint       = 0
    aBurst_Time = []
    iCycle_time = 0

    if sCCFString=='':
        return sCCFString
    if sCCFString[0]=='{':
        return sCCFString

    sData       = sCCFString.strip()
    iCodeLength = len(sData)
    bError      = True
    try:

        while iX<255:
            aBurst_Time.append(0)
            iX=iX+1

        iX=0
        while iX<iCodeLength:
            sTmpStr = sData[iX: iX + 4]
            aBurst_Time[iy]=int(sTmpStr,16)
            iy=iy+1
            iX=iX+5

        iLast_code = iy / 2
        iFreq = int (4145 / aBurst_Time[1])

        iPair_Count = aBurst_Time[2]
        if iPair_Count == 0:
            iPair_Count = aBurst_Time[3]

        #print "Frequency = " , iFreq
        #print "Pair_count = " , iPair_Count

        iX=0
        while iX<iy:
            iMyInt.append(0)
            iX=iX+1

        iMyInt[0]       = int(iFreq * 256 + iPair_Count)
        iCycle_time     = 1000 / iFreq
        iLead_in        = aBurst_Time[4] * iCycle_time
        iMyInt[1]       = iLead_in
        iMyInt[2]       = aBurst_Time[5] * iCycle_time # lead space
        iPair_Count     = iPair_Count - 1  # only loop data pairs
        iX              = 0
        iEnd            = iPair_Count * 2

        while iX<iEnd:
            iTint = int(aBurst_Time[iX + 6] * iCycle_time)
            iMyInt[iX + 3] = iTint
            iX=iX+1

        iMyInt[iX + 2] = 8192   # over write the lead out space with 2000 X is one over when exits from for loop
        sData = ""

        iX              = 0
        iEnd            = (iPair_Count * 2) + 3
        while iX<iEnd:
            sData = sData + ToHex(iMyInt[iX]) + " "
            iX=iX+1
        bError = False
    except Exception as e:
        LogError('CCfToKeene:Can''t Convert',e)
        LogError(sCCFString)

    if bError:
        return ""
    else:
        sRet="K "+ sData.strip().upper()
        if iRepeatCount>1:
            sRet=sRet+' 4000 '+str(iRepeatCount)
        return sRet


