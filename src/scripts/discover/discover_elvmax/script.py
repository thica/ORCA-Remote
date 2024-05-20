# -*- coding: utf-8 -*-
#

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

from __future__ import annotations

from typing import Dict
from typing import List
from typing import Union
from typing import Tuple

import socket
import select
import threading

from kivy.clock                             import Clock
from kivy.uix.button                        import Button
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.vars.QueryDict                    import TypedQueryDict
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.Wildcard                    import MatchWildCard
from ORCA.Globals import Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>ELV MAX Discover</name>
      <description language='English'>Discover ELV MAX cubes</description>
      <description language='German'>Erkennt bwz. sucht ELV MAX Cubes</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_elvmax</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_elvmax.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


class cScript(cDiscoverScriptTemplate):

    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-Discover-ELVMAX
    WikiDoc:TOCTitle:Discover ELVMAX
    = Script Discover ELVMAX =

    The ELV MAX discover script discovers ELV MAX cubes for heating control.
    You can filter the discover result by passing the following parameters::
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |serial
    |Discover models only with a specific serial number (leave it blank to discover all)
    |-
    |timeout
    |Specifies the timout for discover
    |}</div>

    WikiDoc:End
    """

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cScript):
            super().__init__(oScript)
            self.aIniSettings.fTimeOut                     = 5.0

    def __init__(self):
        super().__init__()
        self.uSubType:str                       = 'ELVMAX'
        self.aResults:List[TypedQueryDict]      = []
        self.dDevices:Dict[str,TypedQueryDict]  = {}
        self.dReq                               = TypedQueryDict()
        self.uScriptTitle                       = 'ELV:MAX Discovery'
        self.bDoNotWait:bool                    = False

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        super().Init(uObjectName= uObjectName, oFnObject=oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = 'enabled'

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(SCRIPT_DISC_ELVMAX_1)','$lvar(5035)']

    def ListDiscover(self) -> None:
        self.SendStartNotification()
        Clock.schedule_once(self.ListDiscover_Step2, 0)
        return

    # noinspection PyUnusedLocal
    def ListDiscover_Step2(self, *largs):

        dDevice: TypedQueryDict
        dArgs:Dict              = {"onlyonce":      0,
                                   "ipversion":     "All",
                                   "donotwait":1}
        self.dDevices.clear()
        self.Discover(**dArgs)

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:TypedQueryDict = oButton.dDevice

        uText=  '$lvar(5029): %s \n' \
                '$lvar(5035): %s \n' \
                '$lvar(1063): %s \n' \
                '$lvar(SCRIPT_DISC_ELVMAX_1): %s ' % (dDevice.uFoundIP,dDevice.uFoundHostName,dDevice.uFoundName,dDevice.uFoundSerial)

        ShowMessagePopUp(uMessage=uText)


    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return  {"Serial Number":   {"type": "string",       "order":0,  "title": "$lvar(SCRIPT_DISC_ELVMAX_1)", "desc": "$lvar(SCRIPT_DISC_ELVMAX_1)", "key": "serialnumber",    "default":"" }
                }

    def Discover(self,**kwargs):

        self.dReq.uSerial                        = kwargs.get('serialnumber','')
        uConfigName:str                          = kwargs.get('configname',self.uConfigName)
        oSetting:cBaseScriptSettings             = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut:float                           = ToFloat(kwargs.get('timeout', oSetting.aIniSettings.fTimeOut))
        bOnlyOnce:bool                           = ToBool(kwargs.get('onlyonce','1'))
        self.bDoNotWait                          = ToBool(kwargs.get('donotwait','0'))

        del self.aResults[:]
        del self.aThreads[:]

        self.ShowDebug (uMsg='Try to discover ELV MAX device:  %s ' % self.dReq.uSerial)

        try:
            oThread = cThread_Discover_ELVMAX(bOnlyOnce=bOnlyOnce,dReq=self.dReq,uIPVersion='IPv4Only', fTimeOut=fTimeOut, oCaller=self)
            self.aThreads.append(oThread)
            self.aThreads[-1].start()
            if not self.bDoNotWait:
                for oT in self.aThreads:
                    oT.join()
                self.SendEndNotification()
                if len(self.aResults)>0:
                    return TypedQueryDict([('Host', self.aResults[0].uFoundIP),('Hostname',self.aResults[0].uFoundHostName), ('Serial',self.aResults[0].uFoundSerial), ('Name',self.aResults[0].uFoundName)])
                else:
                    self.ShowWarning(uMsg='No ELV MAX Cube found %s' % self.dReq.uSerial)
            else:
                self.ClockCheck=Clock.schedule_interval(self.CheckFinished,0.1)

        except Exception as e:
            self.ShowError(uMsg='Error on Discover',oException=e)

        return TypedQueryDict([('Host', ''), ('Hostname', ''), ('Serial', ''), ('Name', '')])


class cThread_Discover_ELVMAX(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, bOnlyOnce:bool,dReq:TypedQueryDict,uIPVersion:str, fTimeOut:float,oCaller:cScript):
        threading.Thread.__init__(self)
        self.bOnlyOnce:bool     = bOnlyOnce
        self.uIPVersion:str     = uIPVersion
        self.oCaller:cScript    = oCaller
        self.fTimeOut:float     = fTimeOut
        self.dReq:TypedQueryDict= dReq
        self.iPort:int          = 23272


    def run(self) -> None:
        bReturnNow:bool = False
        if self.bOnlyOnce:
            cThread_Discover_ELVMAX.oWaitLock.acquire()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            cThread_Discover_ELVMAX.oWaitLock.release()
        if bReturnNow:
            return
        self.Discover()

    def Discover(self) -> None:

        oSendSocket:Union[socket.socket,None]    = None
        oReceiveSocket:Union[socket.socket,None] = None

        try:
            # todo: we need to loop through all interfaces, as we might have virtual adapters in windows, in that case it might not work
            # as by now, we are stucked on python 3.7 as kivy is not working on 3.8
            # and the socket.if_nameindex() is available on windows starting python 3.8
            # we need to wait a while

            oSendSocket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            # oSendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
            oSendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            oSendSocket.settimeout(10)

            byData:bytearray =  bytearray('eQ3Max', 'utf-8') + \
                                bytearray('*\0',    'utf-8') + \
                                bytearray('*' * 10, 'utf-8') + \
                                bytearray('I',      'utf-8')

            oSendSocket.sendto(byData,('<broadcast>',self.iPort))
            # oSendSocket.sendto(byData,('239.255.255.250',self.iPort))

            oReceiveSocket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oReceiveSocket.settimeout(self.fTimeOut)
            oReceiveSocket.bind(('0.0.0.0', self.iPort))

            while True:
                # we do not wait too long
                aReady:Tuple = select.select([oReceiveSocket],[],[],self.fTimeOut)
                if aReady[0]:
                    # Get a response
                    byData, tSenderAddr = oReceiveSocket.recvfrom(50)
                    dRet = self.GetDeviceDetails(byData, tSenderAddr)
                    self.CheckDeviceDetails(dRet=dRet)
                    if dRet.bFound:
                        uTageLine:str = dRet.uFoundIP+dRet.uFoundSerial+dRet.uFoundHostName
                        if self.oCaller.dDevices.get(uTageLine) is None:
                            cThread_Discover_ELVMAX.oWaitLock.acquire()
                            self.oCaller.dDevices[uTageLine]=dRet
                            self.oCaller.aResults.append(dRet)
                            Globals.oNotifications.SendNotification(uNotification='DISCOVER_SCRIPTFOUND',**{'script':self,'scriptname':self.oCaller.uObjectName,'line':[dRet.uFoundIP,dRet.uFoundSerial,dRet.uFoundHostName],'device':dRet})
                            cThread_Discover_ELVMAX.oWaitLock.release()
                else:
                    break

            if oSendSocket:
                oSendSocket.close()
            if oReceiveSocket:
                oReceiveSocket.close()

        except Exception as e:
            self.oCaller.ShowError(uMsg='Error on Discover',oException=e)

        if oSendSocket:
            oSendSocket.close()
        if oReceiveSocket:
            oReceiveSocket.close()

    def GetDeviceDetails(self,byData:bytes,tSenderAddr:Tuple) -> TypedQueryDict:

        dRet:TypedQueryDict      = TypedQueryDict()
        dRet.bFound              = True
        dRet.uFoundIP            = tSenderAddr[0] # ==10
        dRet.uData               = ToUnicode(byData[:18])
        dRet.uFoundName          = byData[0:8].decode('utf-8')
        dRet.uFoundSerial        = byData[8:18].decode('utf-8')
        dRet.uFoundHostName      = socket.gethostbyaddr(dRet.uFoundIP)[0]
        dRet.uIPVersion          = 'IPv4'
        self.oCaller.ShowInfo(uMsg=f'Discovered device {dRet.uFoundName}:{dRet.uFoundHostName}:{dRet.uFoundSerial} at {dRet.uFoundIP}')
        return dRet

    def CheckDeviceDetails(self, dRet:TypedQueryDict) -> None:
        if dRet.bFound:
            if self.dReq.uSerial != '':
                if MatchWildCard(uValue=dRet.uFoundSerial,uMatchWithWildCard=self.dReq.uSerial):
                    dRet.bFound = True
                else:
                    dRet.bFound = False

