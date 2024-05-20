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

import select
import socket
import threading

from kivy.logger                            import Logger
from kivy.uix.button                        import Button
from kivy.clock                             import Clock

from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.LogError                    import LogError
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.vars.QueryDict                    import TypedQueryDict
from ORCA.utils.FileName                    import cFileName

from ORCA.Globals import Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Keene Kira Discover</name>
      <description language='English'>Discover Keene Kira devices</description>
      <description language='German'>Erkennt sucht Keene Kira Geräte</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_kira</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_kira.zip</sourcefile>
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
    WikiDoc:Page:Scripts-Discover-Kira
    WikiDoc:TOCTitle:Discover Kira
    = Script Discover Keene Kira =

    The Kira discover script discover Keene Kira Infrared transmitter devices.
    You can filter the discover result by passing the following parameters::
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |timeout
    |Specifies the timout for discover
    |}</div>

    WikiDoc:End
    """
    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cScript):
            super().__init__(oScript)
            self.aIniSettings.fTimeOut  = 10.0

    def __init__(self):
        super().__init__()
        self.uSubType:str                       = 'Keene Kira'
        self.aResults:List[TypedQueryDict]      = []
        self.aThreads:List[threading.Thread]    = []
        self.dReq                               = TypedQueryDict()
        self.bDoNotWait:bool                    = False
        self.uScriptTitle                       = 'Keene Kira Discovery'

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """

        super().Init(uObjectName=uObjectName, oFnObject=oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = 'enabled'

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(5035)','$lvar(6002)']

    def ListDiscover(self) -> None:
        self.SendStartNotification()
        Clock.schedule_once(self.ListDiscover_Step2, 0)
        return

    def ListDiscover_Step2(self, *largs):

        dArgs:Dict                   = {'onlyonce': 0,
                                        'ipversion': 'IPv4Only',
                                        'donotwait':1}
        dDevices:Dict[str,TypedQueryDict] = {}
        dDevice:TypedQueryDict
        self.Discover(**dArgs)
        return

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:TypedQueryDict = oButton.dDevice

        uText=  '$lvar(5029): %s \n' \
                '$lvar(6002): %s \n' \
                '$lvar(5035): %s \n' \
                '\n' \
                '%s' % (dDevice.uFoundIP,dDevice.uFoundPort,dDevice.uFoundHostName,dDevice.sData)

        ShowMessagePopUp(uMessage=uText)


    def Discover(self,**kwargs):

        self.dReq.clear()
        uConfigName:str              = kwargs.get('configname',self.uConfigName)
        oSetting:cBaseScriptSettings = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        self.dReq.bReturnPort        = ToBool(kwargs.get('returnport','0'))
        fTimeOut:float               = ToFloat(kwargs.get('timeout',oSetting.aIniSettings.fTimeOut))
        uIPVersion:str               = kwargs.get('ipversion','IPv4Only')
        bOnlyOnce:bool               = ToBool(kwargs.get('onlyonce','1'))
        self.bDoNotWait              = ToBool(kwargs.get('donotwait','0'))

        Logger.debug ('Try to discover device by Kira Discovery (%s)' % uIPVersion)

        del self.aResults[:]
        del self.aThreads[:]

        try:
            if uIPVersion == 'IPv4Only' or uIPVersion == 'All' or (uIPVersion == 'Auto' and Globals.uIPAddressV6 == ''):
                oThread = cThread_Discover_Kira(bOnlyOnce=bOnlyOnce,dReq=self.dReq,uIPVersion='IPv4Only', fTimeOut=fTimeOut, oCaller=self)
                self.aThreads.append(oThread)
                self.aThreads[-1].start()
            if uIPVersion == 'IPv6Only' or uIPVersion == 'All' or (uIPVersion == 'Auto' and Globals.uIPAddressV6 != ''):
                oThread = cThread_Discover_Kira(bOnlyOnce=bOnlyOnce, dReq=self.dReq, uIPVersion='IPv6Only', fTimeOut=fTimeOut, oCaller=self)
                self.aThreads.append(oThread)
                self.aThreads[-1].start()

            if not self.bDoNotWait:
                for oT in self.aThreads:
                    oT.join()
                self.SendEndNotification()

                if len(self.aResults)>0:
                    return {'Host':self.aResults[0].uFoundIP,
                            'Hostname': self.aResults[0].uFoundHostName,
                            'Exception': None}
                else:
                    Logger.warning('Kira Discover: No device found' )
            else:
                self.ClockCheck=Clock.schedule_interval(self.CheckFinished,0.1)
            return {'Host': '',
                    'Hostname': '',
                    'Exception': None}

        except Exception as e:
            LogError(uMsg='Error on discover uPnP',oException=e)
            return {'Host': '',
                    'Hostname': '',
                    'Exception': e}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return  {'Name':            {'type': 'string',       'order':0,  'title': '$lvar(6013)', 'desc': '$lvar(6014)', 'key': 'name',            'default':''           },
                 'IP Version':      {'type': 'scrolloptions','order':4,  'title': '$lvar(6037)', 'desc': '$lvar(6038)', 'key': 'ipversion',       'default':'IPv4Only', 'options':['IPv4Only','IPv6Only','All','Auto']},
                 'TimeOut':         {'type': 'numericfloat', 'order':6,  'title': '$lvar(6019)', 'desc': '$lvar(6020)', 'key': 'timeout',         'default':'15.0'}
                }

        #"ReturnPort":      {"type": "bool", "order": 4, "title": "$lvar(SCRIPT_DISC_UPNP_2)", "desc": "$lvar(SCRIPT_DISC_UPNP_3)", "key": "returnport", "default": "1"},


'''
ff02::c

'''

class cThread_Discover_Kira(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, bOnlyOnce:bool,dReq:TypedQueryDict,uIPVersion:str,fTimeOut:float,oCaller:cScript):
        threading.Thread.__init__(self)

        self.bOnlyOnce:bool     = bOnlyOnce
        self.uIPVersion:str     = uIPVersion
        self.oCaller:cScript    = oCaller
        self.fTimeOut:float     = fTimeOut
        self.bStopWait:bool     = False
        self.dReq               = dReq

    def run(self) -> None:

        bReturnNow:bool = False
        if self.bOnlyOnce:
            cThread_Discover_Kira.oWaitLock.acquire()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            cThread_Discover_Kira.oWaitLock.release()
        if bReturnNow:
            return
        self.Discover()

    def Discover(self) -> None:

        oSocket = None
        try:
            self.bStopWait      = False

            oSocket = self.SendDiscover()
            if oSocket:
                # Parse all results
                while True:
                    #we do not wait too long
                    aReady = select.select([oSocket], [], [],self.fTimeOut)
                    if aReady[0]:
                        # Get a response
                        byData, tSenderAddr = oSocket.recvfrom(1024)
                        uData = ToUnicode(byData)
                        dRet = self.GetDeviceDetails(uData=uData,tSenderAddr=tSenderAddr)
                        self.CheckDeviceDetails(dRet=dRet)
                        if dRet.bFound:
                            Logger.info('Bingo: Discovered device  %s:' %dRet.uFoundIP)
                            try:
                                dRet.uFoundHostName = socket.gethostbyaddr(dRet.uFoundIP)[0]
                            except Exception:
                                pass
                            cThread_Discover_Kira.oWaitLock.acquire()
                            self.oCaller.aResults.append(dRet)
                            cThread_Discover_Kira.oWaitLock.release()
                            if self.bOnlyOnce:
                                oSocket.close()
                                return
                    else:
                        break
                oSocket.close()
            # Logger.warning('No device found device %s:%s:%s' %(self.oReq.uManufacturer,self.oReq.uModels,self.oReq.uFriendlyName))
            return

        except Exception as e:
            LogError(uMsg='Error on discover Kira (%s)' % self.uIPVersion,oException=e)
            if oSocket:
                oSocket.close()
            return


    def SendDiscover(self):

        bMessage = b'disD'
        iUDP_PORT = 30303

        if self.uIPVersion=='IPv4Only':
            uUDP_IP     = '239.255.255.250'
            oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)
            oSocket.sendto(bMessage, (uUDP_IP, iUDP_PORT))
            return oSocket

        if self.uIPVersion == 'IPv6Only':

            # socket.IPPROTO_IPV6 might not be defined
            IPPROTO_IPV6 = 41
            try:
                IPPROTO_IPV6=socket.IPPROTO_IPV6
            except:
                pass

            uUDP_IP = 'ff02::f'

            oSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(IPPROTO_IPV6, socket.IP_MULTICAST_TTL, 20)
            oSocket.sendto(bMessage, (uUDP_IP, iUDP_PORT))
            return oSocket

        return None


    def GetDeviceDetails(self,uData:str,tSenderAddr):
        dRet                     = TypedQueryDict()
        dRet.uFoundIP            = tSenderAddr[0]
        dRet.uFoundPort          = tSenderAddr[1]
        dRet.bFound              = True
        dRet.sData               = uData
        dRet.uIPVersion          = self.uIPVersion
        return dRet

    def CheckDeviceDetails(self,dRet:TypedQueryDict) -> None:
        return
