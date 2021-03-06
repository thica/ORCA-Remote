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
from kivy import Logger

try:
    import netifaces
except Exception as ex:
    Logger.error("Can't load netifaces:"+str(ex))

__all__ = ['GetIPAddressV6']

def GetIPAddressV6() -> str:

    uPreferredAdapter:str = u'eth0'
    uInet_Type:str        = u'AF_INET6'
    uRet:str              = u'127.0.0.0'
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
                uIP = dNetDetails["addr"]
                if uIP != "::1":
                    aFound.append(uIP)
                    if uNetiface == uPreferredAdapter:
                        aFound = [uIP]
                        break
    except Exception as e:
        Logger.error("Error on GetIPAddressV6:"+str(e))

    if len(aFound)>0:
        uRet = aFound[-1]

    # remove stuff like %eth0 that gets thrown on end of some addrs
    uRet=uRet.split('%')[0]
    return uRet