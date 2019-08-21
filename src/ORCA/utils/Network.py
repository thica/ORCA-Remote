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
from ORCA.utils.TypeConvert         import ToUnicode
from ORCA.utils.Platform            import OS_SystemIsOnline, OS_Ping
from ORCA.utils.wait.StartWait      import StartWait
from ORCA.utils.wait.StopWait       import StopWait
from ORCA.utils.PyXSocket           import cPyXSocket
from ORCA.vars.Access               import ExistLVar

import ORCA.Globals as Globals

__all__ = ['GetLocalIPV4','GetLocalIPV6','GetMACAddress','cWaitForConnectivity','Ping']


def Ping(uHostname):
    """ Ping function """
    return OS_Ping(uHostname)


'''

to check: if we can use Routerc Discovery to get the gateway

Router Solicitation Message ->
Src: fe80::c072:7a5f:c1b5:24d1
Dst: ff02::2 (all routers multicast)
ICMPv6 Type 133 (RS)
Option:
 Src Link Layer Addr (my MAC addr)
<- Router Advertisement Message
Src: router's link local addr
Dst: ff02::1 (all nodes or solicitor)
ICMPv6 Type 134 (RA)
Flags (M=0, O=0, pref=0)
Router Lifetime: 1800
Reachable time: 0
Retrans time: 0
Options:
 Src Link Layer Addr (my Mac)
 MTU: 1500
 Prefix Info
 prefix: 2001:db8:ab:cd::/64
 valid life: 2592000

'''

def GetLocalIPV6():

    # Under construction

    uMyIP       = u''
    uMyGateway  = u'2a00:1450:4001:808::200e' # this is wrong (IPv6 Google, we leave it as long I have not found a way to detect it)

    # Fast but not safe
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        # Not necessary successfull
        s.connect(('2001:0db8:85a3:0000:0000:8a2e:0370:7334', 1))
        IP = s.getsockname()[0]
    except Exception:
        return uMyIP, uMyGateway
    finally:
        s.close()
    uMyIP = ToUnicode(IP)
    return uMyIP,uMyGateway

def GetLocalIPV4():

    GetLocalIPV6()

    # Fast but not safe
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Not necessary successfull
        s.connect(('10.255.255.255', 0))
        IP = s.getsockname()[0]
    except:
        IP = GetLocalIPV4_FallBack()
    finally:
        s.close()
    uMyIP = ToUnicode(IP)
    tTmp = uMyIP.split('.')
    uMyGateway = tTmp[0] + '.' + tTmp[1] + '.' + tTmp[2] + '.1'
    uMySubNet = tTmp[0] + '.' + tTmp[1] + '.' + '0' + '.255'
    return uMyIP,uMyGateway,uMySubNet

def GetLocalIPV4_FallBack():
    """ gets the local IP by opening a socket to itself """
    def udp_listening_server():
        """ the server component """
        try:
            oInSocket = cPyXSocket(socket.AF_INET, socket.SOCK_DGRAM)
            #s.bind(('<broadcast>', 8888))
            oInSocket.bind(("0.0.0.0", 18888))
            oInSocket.SetBlocking(0)
            while True:
                result = select.select([oInSocket],[],[])
                msg, address = result[0][0].recvfrom(1024)
                if msg == b'ORCAIPREQUEST':
                    IP.append(address[0])
                    break
            oInSocket.close()
        except Exception as e:
            LogError(u'GetLocalIp:udp_listening_server:',e)
            return
    try:
        IP        = []
        thread    = threading.Thread(target=udp_listening_server)
        thread.IP = IP
        thread.start()
        oOutSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        oOutSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        i=0
        while len(IP)==0:
            oOutSocket.sendto(b'ORCAIPREQUEST', ("255.255.255.255", 18888))
            fSleep(0.1)
            i+=1
            if i==10:
                break
        oOutSocket.close()
        if len(IP)>0:
            return IP[0]
        else:
            return u'127.0.0.0'
    except Exception as e:
        LogError('GetLocalIpV4:',e)
        return u'127.0.0.0'

def GetMACAddress():
    """ gets the mac adrress of the device """
    uRetColon=u'00:00:00:00:00:00'
    uRetDash=u'00-00-00-00-00-00'
    # todo: this doesnt work on non rooted android devices wizh high api level,we need to wrap it with java
    # WifiManager wm = (WifiManager)
    # getSystemService(Context.WIFI_SERVICE);
    # String mac = wm.getConnectionInfo().getMacAddress();
    # return uRetColon, uRetDash

    try:
        uRetColon= u':'.join(re.findall('..', '%012x' % uuid.getnode()))
        uRetDash= u'-'.join(re.findall('..', '%012x' % uuid.getnode()))
    except Exception as e:
        LogError('GetMACAdress:',e)
    return uRetColon,uRetDash


def IsOnline(*largs):
    """ checks, if the device is connected to the network """
    if not Globals.bConfigCheckForNetwork:
        Logger.debug("Skipping wait for connecivity")
        Globals.oWaitForConnectivity.bIsOnline = True
    elif Globals.uNetworkCheckType=="ping":
        Logger.debug("Checking for network connectivity (ping)")
        uPingAddress=Globals.uConfigCheckNetWorkAddress
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
        super(cWaitForConnectivity, self).__init__(*args, **kwargs)
        self.bCancel         = False
        self.pNotifyFunction = None
        self.bIsWaiting      = False
        self.bIsOnline       = False
        self.oPopup          = None
        self.oThread         = None
        #self.register_event_type('on_onlinestatechecked')
        self.register_event_type('on_waitforconnectivity_finished')

    def IsOnline(self, *largs):
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
        self.dispatch('on_onlinestatechecked')

    def on_onlinestatechecked(self, *largs):
        """ called, wehn the tsated has been checked """
        Logger.debug("Checking for network connectivity online state checked")
        if not self.bIsWaiting:
            return
        if not self.bIsOnline:
            Clock.schedule_once(self.StartNextThread, 0)
            fSleep(0.6)
            return
        self.StopWait()

    def StartNextThread(self,*largs):
        """ Starts the next thread to check, if online """
        #Logger.debug("Checking for network connectivity start thread")
        #fSleep(0.01)
        #Clock.schedule_once(IsOnline, 0)
        #return

        if self.oThread is not None:
            self.oThread.join()

        self.oThread = threading.Thread(target=IsOnline, name="WaitNetworkThread")
        self.oThread.start()

    def Wait(self):
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

    def StopWait(self):
        """ MAin entry point to stop waiting """
        if self.oPopup:
            self.oPopup.ClosePopup()
        self.CancelWaitForConnectivity()

    def CancelWaitForConnectivity(self, *largs):
        """ Called, when the user pushes the cancel button """
        if self.oThread is not None:
            self.oThread.join()
        self.bCancel    = True
        self.bIsWaiting = False
        self.oPopup = None
        StopWait()
        self.bIsWaiting            = False#
        self.dispatch('on_waitforconnectivity_finished')

    def on_waitforconnectivity_finished(self):
        """  Dummy for the event dispatcher """
        pass
