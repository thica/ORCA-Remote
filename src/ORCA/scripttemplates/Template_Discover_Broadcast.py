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
from typing import Callable

from kivy.clock                             import Clock

import select
import socket
import threading

from kivy.logger                            import Logger
from kivy.uix.button                        import Button
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.LogError                    import LogError
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.TypeConvert                 import ToInt
from ORCA.vars.QueryDict                    import TypedQueryDict
from ORCA.Globals import Globals

class cDiscoverScriptTemplate_Broadcast(cDiscoverScriptTemplate):

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cDiscoverScriptTemplate_Broadcast):
            super().__init__(oScript)
            self.aIniSettings.fTimeOut = 15.0

    def __init__(self):
        super().__init__()
        self.bStopWait:bool                     = False
        self.aResults:List[TypedQueryDict]      = []
        self.dReq                               = TypedQueryDict()
        self.bDoNotWait:bool                    = False
        self.uScriptTitle                       = 'Template for Broadcast Discovery'

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """

        super().Init(uObjectName=uObjectName, oFnObject=oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = 'enabled'

    def ListDiscover(self) -> None:
        self.SendStartNotification()
        Clock.schedule_once(self.ListDiscover_Step2, 0)
        return

    def CreateArgs(self) -> Dict:
        # Empty function
        Logger.error('You must implement CreateArgs')

        return {'onlyonce':      0,
                'ipversion':     'All',
                'donotwait':1}


    def ListDiscover_Step2(self, *largs) -> None:
        dArgs:Dict              = self.CreateArgs()
        self.Discover(**dArgs)
        return

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:
        Logger.error('You must implement CreateDiscoverList_ShowDetails')
        dDevice:TypedQueryDict = oButton.dDevice
        uText:str = '$lvar(5029): %s \n' % dDevice.uFoundIP
        ShowMessagePopUp(uMessage=uText)

    def GetServiceTypes(self,dArgs:Dict)->List:
        """ This is a dummy function if not service types are required, than leave it as it is"""
        return ["default"]

    def GetRequests(self,dArgs:Dict)-> TypedQueryDict:
        """ This is could be overridden """
        dReq = TypedQueryDict()
        dReq.iPortV4              = ToInt(dArgs.get('portv4','1900'))
        dReq.uBroadcastIPV4       = dArgs.get('ipv4','239.255.255.250')
        dReq.iPortV6              = ToInt(dArgs.get('portv6',dReq.iPortV4))
        dReq.uBroadcastIPV6       = dArgs.get('ipv6','FF02::C')
        return dReq

    def CreateResult(self,bEmpty:bool=False,oException:Exception=None) -> Dict:
        """ This is a dummy function, needs to be replaced """
        return {'Host': '127.0.0.1',
                'Hostname': 'localhost',
                'Exception': oException}

    def Discover(self,**kwargs) -> Dict:

        self.dReq.clear()
        uConfigName:str              = kwargs.get('configname',self.uConfigName)
        oSetting:cBaseScriptSettings = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        self.dReq                    = self.GetRequests(kwargs)
        aST:List                     = self.GetServiceTypes(kwargs)
        fTimeOut:float               = ToFloat(kwargs.get('timeout',oSetting.aIniSettings.fTimeOut))
        uIPVersion:str               = kwargs.get('ipversion','IPv4Only')
        bOnlyOnce:bool               = ToBool(kwargs.get('onlyonce','1'))
        self.bDoNotWait              = ToBool(kwargs.get('donotwait','0'))

        del self.aResults[:]
        del self.aThreads[:]

        self.ShowStartMessage()

        try:
            for uST in aST:
                if uIPVersion == 'IPv4Only' or uIPVersion == 'All' or (uIPVersion == 'Auto' and Globals.uIPAddressV6 == ''):
                    oThread = self.GetThreadClass()(bOnlyOnce=bOnlyOnce,dReq=self.dReq,uIPVersion='IPv4Only', fTimeOut=fTimeOut, uST=uST,oCaller=self)
                    self.aThreads.append(oThread)
                    self.aThreads[-1].start()
                if uIPVersion == 'IPv6Only' or uIPVersion == 'All' or (uIPVersion == 'Auto' and Globals.uIPAddressV6 != ''):
                    #todo: Disabled until found a better way to handle devices with no IPV6 support
                    pass
                    #oThread = self.GetThreadClass()(bOnlyOnce=bOnlyOnce, dReq=self.dReq, uIPVersion='IPv6Only', fTimeOut=fTimeOut, uST=uST,oCaller=self)
                    #self.aThreads.append(oThread)
                    #self.aThreads[-1].start()

            if not self.bDoNotWait:
                for oT in self.aThreads:
                    oT.join()
                self.SendEndNotification()

                if len(self.aResults)>0:
                    return self.CreateResult()
                else:
                    self.ShowNotFoundMessage()
            else:
                self.ClockCheck=Clock.schedule_interval(self.CheckFinished,0.1)
            return self.CreateResult(bEmpty=True)

        except Exception as e:
            LogError(uMsg='Error on discover',oException=e)
            return self.CreateResult(bEmpty=True,oException=e)

    def ShowNotFoundMessage(self) -> None:
        """ needs to be overwritten """
        self.ShowWarning(uMsg='No device found by broadcast')

    def ShowStartMessage(self) -> None:
        """ needs to be overwritten """
        self.ShowDebug (uMsg='Try to discover device by broadcast')

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return {'TimeOut':{'type': 'numericfloat', 'order':0, 'title': '$lvar(6019)', 'desc': '$lvar(6020)','key': 'timeout', 'default':'1.0'}}

    # noinspection PyMethodMayBeStatic
    def GetThreadClass(self) -> Callable:
        Logger.error('You must implement GetThreadClass')
        return cThread_DiscoverTemplate_Broadcast


class cThread_DiscoverTemplate_Broadcast(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, bOnlyOnce:bool,dReq:TypedQueryDict,uIPVersion:str, uST:str,fTimeOut:float,oCaller:cDiscoverScriptTemplate_Broadcast):
        threading.Thread.__init__(self)
        self.iReceiveSize:int   = 1024
        self.bOnlyOnce:bool     = bOnlyOnce
        self.uIPVersion:str     = uIPVersion
        self.oCaller:cDiscoverScriptTemplate_Broadcast = oCaller
        self.fTimeOut:float     = fTimeOut
        self.uST:str            = uST
        self.bStopWait:bool     = False
        self.dReq:TypedQueryDict= dReq
        self.iPortV4            = dReq.iPortV4
        self.uBroadcastIPV4     = dReq.uBroadcastIPV4
        self.iPortV6            = dReq.iPortV6
        self.uBroadcastIPV6     = dReq.uBroadcastIPV6

    def Lock(self):
        cThread_DiscoverTemplate_Broadcast.oWaitLock.acquire()
    def UnLock(self):
        cThread_DiscoverTemplate_Broadcast.oWaitLock.release()
    def run(self) -> None:

        bReturnNow:bool = False
        if self.bOnlyOnce:
            self.Lock()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            self.UnLock()
        if bReturnNow:
            return
        self.Discover()

    def Discover(self) -> None:

        self.fTimeOut = 20
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
                        byData, tSenderAddr = oSocket.recvfrom(self.iReceiveSize)
                        dRet = self.GetDeviceDetails(byData=byData,tSenderAddr=tSenderAddr)
                        self.CheckDeviceDetails(dRet=dRet)
                        if dRet.bFound:
                            self.ShowFoundMessage(dRet=dRet)
                            try:
                                if dRet.uIPVersion == 'IPv4':
                                    dRet.uFoundHostName = socket.gethostbyaddr(dRet.uFoundIP)[0]
                                elif dRet.uIPVersion == 'IPv6':
                                    #todo: Does not work for unknown reasons
                                    dRet.uFoundHostName = socket.gethostbyaddr(dRet.uFoundIP)[0]
                            except Exception as e:
                                # Logger.error("Cant get Hostname:"+dRet.uFoundIP+" "+str(e))
                                i=1
                                pass
                            uTageLine:str = self.CreateTagLine(dRet=dRet)
                            if self.oCaller.dDevices.get(uTageLine) is None or uTageLine=='':
                                self.oCaller.dDevices[uTageLine]=dRet
                                self.SendFoundNotification(dRet)

                            self.Lock()
                            self.oCaller.aResults.append(dRet)
                            self.UnLock()
                            if self.bOnlyOnce:
                                oSocket.close()
                                return
                    else:
                        break
                oSocket.close()
            # Logger.warning('No device found device %s:%s:%s' %(self.oReq.uManufacturer,self.oReq.uModels,self.oReq.uFriendlyName))
            return

        except Exception as e:
            self.oCaller.ShowError(uMsg=f'Error on discover Broadcast {self.uIPVersion}' , oException=e)
            if oSocket:
                oSocket.close()
            return

    def ShowFoundMessage(self,dRet:TypedQueryDict):
        """ needs to be overwritten """
        self.oCaller.ShowInfo(uMsg='Discovered device')

    def CreatePayloadV4(self) -> bytes:
        """ needs to be overwritten """
        return ToBytes('')

    def CreatePayloadV6(self) -> bytes:
        """ needs to be overwritten """
        return self.CreatePayloadV4()

    def CreateTagLine(self,dRet:TypedQueryDict) -> str:
        """ needs to be overwritten """
        return dRet.uFoundIP + dRet.uFoundModel

    def SendFoundNotification(self,dRet:TypedQueryDict):
        """ needs to be overwritten """
        Globals.oNotifications.SendNotification(uNotification='DISCOVER_SCRIPTFOUND',uDescription=f"from {self.uScriptTitle}",
                                            **{"script": self, "scriptname": self.oCaller.uObjectName, "line": [dRet.uFoundIP, dRet.uFoundHostName, dRet.uFoundManufacturer, dRet.uFoundModel, dRet.uFoundFriendlyName, dRet.uFoundServiceType],
                                               "device": dRet})

    def CreateV4Socket(self)->socket:
        try:
            oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            oSocket.bind((Globals.uIPAddressV4,0))
            return oSocket
        except Exception as e:
            self.oCaller.ShowError(uMsg=f'Error on CreateV4Socket', oException=e)

    def CreateV6Socket(self)->socket:
        # socket.IPPROTO_IPV6 might not be defined
        IPPROTO_IPV6 = 41
        try:
            IPPROTO_IPV6 = socket.IPPROTO_IPV6
        except:
            pass
        oSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        oSocket.settimeout(self.fTimeOut)
        oSocket.setsockopt(IPPROTO_IPV6, socket.IP_MULTICAST_TTL, 2)
        oSocket.bind((Globals.uIPAddressV6, 0))
        return oSocket

    def SendDiscover(self) -> socket:

        try:

            if self.uIPVersion=='IPv4Only':
                try:
                    bMessage = self.CreatePayloadV4()
                    oSocket:socket=self.CreateV4Socket()
                    oSocket.sendto(bMessage, (self.uBroadcastIPV4, self.iPortV4))
                    return oSocket
                except Exception as e:
                    self.oCaller.ShowError(uMsg=f'Error on SendDiscover IPV4', oException=e)

            if self.uIPVersion == 'IPv6Only':
                try:
                    bMessage = self.CreatePayloadV6()
                    oSocket:socket=self.CreateV6Socket()
                    oSocket.sendto(bMessage, (self.uBroadcastIPV6, self.iPortV6))
                    return oSocket
                except Exception as e:
                    self.oCaller.ShowError(uMsg=f'Error on SendDiscover IPV6', oException=e)

        except Exception as e:
            self.oCaller.ShowError(uMsg=f'Error on SendDiscover', oException=e)

        return None

    # noinspection PyUnusedLocal
    def GetDeviceDetails(self,byData:bytes,tSenderAddr:Tuple) -> TypedQueryDict:
        """ needs to be overwritten """
        dRet: TypedQueryDict    = TypedQueryDict()
        dRet.bFound             = False
        dRet.uFoundIP           = tSenderAddr[0]
        dRet.uIPVersion         = self.uIPVersion[:4]
        return dRet

    # noinspection PyUnusedLocal
    def CheckDeviceDetails(self,dRet:TypedQueryDict) -> None:
        """ needs to be overwritten """
        return None
