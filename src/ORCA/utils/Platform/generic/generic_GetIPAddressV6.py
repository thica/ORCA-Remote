# -*- coding: utf-8 -*-

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

from typing import List
from typing import Dict
from kivy import Logger
import socket


from ORCA.Globals import Globals


try:
    import netifaces
except Exception as ex:
    Logger.error('Can\'t load netifaces:'+str(ex))

__all__ = ['GetIPAddressV6']

# we need to detect the IPV6 first and than find the V6IP address on the same adapter

def GetIPAddressV6() -> str:

    uInet_Type:str        = 'AF_INET6'
    uRet:str              = '127.0.0.0'
    iInet_num:int
    dNetInfo: Dict
    aNetDetails: List

    try:
        iInet_num = getattr(netifaces, uInet_Type)
        if Globals.uIPInterfaceName_OS != '':
            dNetInfo = netifaces.ifaddresses(Globals.uIPInterfaceName_OS)
            aNetDetails = dNetInfo.get(iInet_num)
            if aNetDetails is not None and len(aNetDetails)>0:
                dNetDetails:Dict = aNetDetails[0]
                uRet = dNetDetails['addr']
                # We select the local link address
                if True:
                    for dNetDetails in aNetDetails:
                        if  dNetDetails['addr'].startswith('fe80'):
                            uRet = dNetDetails['addr']
                            break

    except Exception as e:
        Logger.error('Using Fallback on GetIPAddressV6:'+str(e))
        uRet = GetIPAddressV6_Fallback()

    return uRet


def GetIPAddressV6_Fallback() -> str:
    oSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        oSocket.connect(('2001:db8::', 1027))
    except:
        return ''
    return oSocket.getsockname()[0]

