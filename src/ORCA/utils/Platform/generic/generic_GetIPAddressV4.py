# -*- coding: utf-8 -*-

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

from typing import List
from typing import Dict
from typing import Tuple

from kivy import Logger

import select
import socket
import threading

from ORCA.utils.LogError            import LogError
from ORCA.utils.Sleep               import fSleep


try:
    import netifaces
    Logger.debug("Loaded netifaces")
except Exception as ex:
    Logger.error("Can't load netifaces:"+str(ex))

__all__ = ['GetIPAddressV4']

def GetIPAddressV4() -> str:

    uPreferredAdapter:str = u'eth0'
    uInet_Type:str        = u'AF_INET'
    uRet:str              = u'127.0.0.1'
    aFound:List[str]      = []
    iInet_num:int

    try:
        iInet_num = getattr(netifaces, uInet_Type)
        aInterfaces:List = netifaces.interfaces()

        for uNetiface in aInterfaces:
            dNetInfo:Dict    = netifaces.ifaddresses(uNetiface)
            aNetDetails:List = dNetInfo.get(iInet_num)
            if aNetDetails is not None and len(aNetDetails)>0:
                dNetDetails:Dict = aNetDetails[0]
                aFound.append(dNetDetails["addr"])
                if uNetiface == uPreferredAdapter:
                    aFound = [dNetDetails["addr"]]
                    break
    except Exception as e:
        Logger.error("Error on GetIPAddressV4:"+str(e))

    # we prefer a local subnet if given
    for uFound in aFound:
        if uFound.startswith("192"):
            uRet=uFound
            break
        if not uFound.startswith("127"):
            uRet=uFound

    if uRet.startswith(u'127'):
        uRet=GetLocalIPV4()

    return uRet

def GetLocalIPV4()->str:

    # Fast but not safe
    uMyIP:str
    s:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Not necessary successful
        s.connect(('10.255.255.255', 0))
        uMyIP = s.getsockname()[0]
    except:
        uMyIP = GetLocalIPV4_FallBack()
    finally:
        s.close()

    return uMyIP

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
            fSleep(fSeconds=0.1)
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
