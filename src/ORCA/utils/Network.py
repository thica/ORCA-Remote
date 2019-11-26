# -*- coding: utf-8 -*-

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

from typing import Tuple
from typing import List

import select
import socket
import threading
import re
import uuid

from kivy.clock                     import Clock
from kivy.logger                    import Logger
from kivy.event                     import EventDispatcher

from ORCA.utils.Sleep               import fSleep
from ORCA.utils.LogError            import LogError
from ORCA.ui.RaiseQuestion          import ShowQuestionPopUp
from ORCA.utils.Platform            import OS_SystemIsOnline, OS_Ping
from ORCA.utils.wait.StartWait      import StartWait
from ORCA.utils.wait.StopWait       import StopWait
from ORCA.vars.Access               import ExistLVar

import ORCA.Globals as Globals

__all__ = ['GetLocalIPV4','GetLocalIPV6','GetMACAddress','cWaitForConnectivity','Ping']


def Ping(uHostname:str) ->bool:
    """ Ping function """
    return OS_Ping(uHostname)

def GetLocalIPV6()->Tuple:

    # Under construction

    uMyIP:str       = u''
    uMyGateway:str  = u'2a00:1450:4001:808::200e' # this is wrong (IPv6 Google, we leave it as long I have not found a way to detect it)

    # Fast but not safe
    s:socket.socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        # Not necessary successfull
        s.connect(('2001:0db8:85a3:0000:0000:8a2e:0370:7334', 1))
        uMyIP = s.getsockname()[0]
    except Exception:
        return uMyIP, uMyGateway
    finally:
        s.close()
    return uMyIP,uMyGateway

def GetLocalIPV4()->Tuple:

    # Fast but not safe
    uMyIP:str
    s:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Not necessary successfull
        s.connect(('10.255.255.255', 0))
        uMyIP = s.getsockname()[0]
    except:
        uMyIP = GetLocalIPV4_FallBack()
    finally:
        s.close()

    tTmp:List[str,str,str,str] = uMyIP.split('.')
    uMyGateway:str = tTmp[0] + '.' + tTmp[1] + '.' + tTmp[2] + '.1'
    uMySubNet:str  = tTmp[0] + '.' + tTmp[1] + '.' + tTmp[2] + '.255'
    return uMyIP,uMyGateway,uMySubNet

def GetLocalIPV4_FallBack() ->str:
    """ gets the local IP by opening a socket to itself """
    def udp_listening_server()->str:
        """ the server component """
        bMsg: bytes
        tAddress: Tuple
        try:
            oInSocket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oInSocket.bind(("0.0.0.0", 18888))
            oInSocket.setblocking(False)
            while True:
                tResult:Tuple = select.select([oInSocket],[],[])
                bMsg, tAddress = tResult[0][0].recvfrom(1024)
                if bMsg == b'ORCAIPREQUEST':
                    aIP.append(tAddress[0])
                    break
            oInSocket.close()
        except Exception as exc:
            LogError(uMsg=u'GetLocalIp:udp_listening_server:',oException=exc)
            return u'127.0.0.0'

    try:
        Logger.debug("Using Fallback to detect V4 IP Address")
        aIP:List  = []
        oThread:threading.Thread = threading.Thread(target=udp_listening_server)
        oThread.aIP = aIP
        oThread.start()
        oOutSocket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        oOutSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        i:int = 0
        while len(aIP)==0:
            oOutSocket.sendto(b'ORCAIPREQUEST', ("255.255.255.255", 18888))
            fSleep(0.1)
            i+=1
            if i==10:
                break
        oOutSocket.close()
        if len(aIP)>0:
            return aIP[0]
        else:
            return u'127.0.0.0'
    except Exception as e:
        LogError(uMsg='GetLocalIpV4:',oException=e)
        return u'127.0.0.0'

def GetMACAddress()->Tuple:
    """ gets the mac adrress of the device """
    uRetColon:str = u'00:00:00:00:00:00'
    uRetDash:str  = u'00-00-00-00-00-00'
    # todo: this doesnt work on non rooted android devices wizh high api level,we need to wrap it with java
    # WifiManager wm = (WifiManager)
    # getSystemService(Context.WIFI_SERVICE);
    # String mac = wm.getConnectionInfo().getMacAddress();
    # return uRetColon, uRetDash

    try:
        uRetColon = u':'.join(re.findall('..', '%012x' % uuid.getnode()))
        uRetDash  = u'-'.join(re.findall('..', '%012x' % uuid.getnode()))
    except Exception as e:
        LogError(uMsg='GetMACAdress:',oException=e)
    return uRetColon,uRetDash


# noinspection PyUnusedLocal
def IsOnline(*largs):
    """ checks, if the device is connected to the network """
    if not Globals.bConfigCheckForNetwork:
        Logger.debug("Skipping wait for connecivity")
        Globals.oWaitForConnectivity.bIsOnline = True
    elif Globals.uNetworkCheckType=="ping":
        Logger.debug("Checking for network connectivity (ping)")
        uPingAddress:str=Globals.uConfigCheckNetWorkAddress
        if uPingAddress=="auto":
            uPingAddress=Globals.uIPGateWayAssumedV4
        Logger.debug("Pinging "+uPingAddress)
        Globals.oWaitForConnectivity.bIsOnline = Ping(uPingAddress)
    elif Globals.uNetworkCheckType=="system":
        Globals.oWaitForConnectivity.bIsOnline = OS_SystemIsOnline()
    else:
        Globals.oWaitForConnectivity.bIsOnline = True
    Clock.schedule_once(Globals.oWaitForConnectivity.on_onlinestatechecked, 0)
    #self.dispatch('on_onlinestatechecked')

class cWaitForConnectivity(EventDispatcher):
    """ Waits, if device is connected to the network """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bCancel:bool         = False
        self.bIsWaiting:bool      = False
        self.bIsOnline:bool       = False
        self.oPopup               = None
        self.oThread              = None
        # noinspection PyUnresolvedReferences
        self.register_event_type('on_waitforconnectivity_finished')

    # noinspection PyUnusedLocal
    def IsOnline(self, *largs)-> None:
        """ sub function to test, if online """

        if not Globals.bConfigCheckForNetwork:
            Logger.debug("Skipping wait for connecivity")
            self.bIsOnline = True
        elif Globals.uNetworkCheckType=="ping":
            Logger.debug("Checking for network connectivity (ping)")
            Logger.debug("Pinging "+Globals.uConfigCheckNetWorkAddress)
            self.bIsOnline = Ping(Globals.uConfigCheckNetWorkAddress)
        elif Globals.uNetworkCheckType=="system":
            self.bIsOnline=OS_SystemIsOnline()
        else:
            self.bIsOnline = True
        # noinspection PyUnresolvedReferences
        self.dispatch('on_onlinestatechecked')

    # noinspection PyUnusedLocal
    def on_onlinestatechecked(self, *largs)-> None:
        """ called, when the tsated has been checked """
        Logger.debug("Checking for network connectivity online state checked")
        if not self.bIsWaiting:
            return
        if not self.bIsOnline:
            Clock.schedule_once(self.StartNextThread, 0)
            fSleep(0.6)
            return
        self.StopWait()

    # noinspection PyUnusedLocal
    def StartNextThread(self,*largs)-> None:
        """ Starts the next thread to check, if online """
        #Logger.debug("Checking for network connectivity start thread")
        #fSleep(0.01)
        #Clock.schedule_once(IsOnline, 0)
        #return

        if self.oThread is not None:
            self.oThread.join()

        self.oThread = threading.Thread(target=IsOnline, name="WaitNetworkThread")
        self.oThread.start()

    def Wait(self)-> bool:
        """ Main entry point to wait """
        Logger.debug("Checking for network connectivity")
        self.bIsWaiting    = True
        self.bCancel       = False
        StartWait()
        self.bIsOnline     = False

        bLangLoaded = ExistLVar('5012')
        if bLangLoaded:
            uMessage    = u'$lvar(5012)'
        else:
            uMessage    = "Waiting for network connectivity"

        self.oPopup=ShowQuestionPopUp(uTitle=u'$lvar(5010)',uMessage= uMessage,fktYes=self.CancelWaitForConnectivity,uStringYes=u'$lvar(5009)',uSound= u'message')
        Clock.schedule_once(self.StartNextThread, 0)
        return False

    def StopWait(self)-> None:
        """ Main entry point to stop waiting """
        if self.oPopup:
            self.oPopup.ClosePopup()
        self.CancelWaitForConnectivity()

    # noinspection PyUnusedLocal
    def CancelWaitForConnectivity(self, *largs)-> None:
        """ Called, when the user pushes the cancel button """
        if self.oThread is not None:
            self.oThread.join()
        self.bCancel    = True
        self.bIsWaiting = False
        self.oPopup     = None
        StopWait()
        self.bIsWaiting = False
        # noinspection PyUnresolvedReferences
        self.dispatch('on_waitforconnectivity_finished')

    def on_waitforconnectivity_finished(self)-> None:
        """  Dummy for the event dispatcher """
        pass
