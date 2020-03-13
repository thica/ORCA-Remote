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
import ORCA.Globals as Globals

__all__ = ['GetSubnetV4']

def GetSubnetV4() -> str:

    uPreferredAdapter:str = u'eth0'
    uInet_Type:str        = u'AF_INET'
    uRet:str              = u'192.168.1.255'
    aFound:List[Dict]     = []
    bLoaded:bool          = False
    dFound:Dict
    iInet_num:int

    try:
        try:
            import netifaces
            bLoaded = True
        except Exception as ex:
            Logger.error("GetSubnetV4: Can't load netifaces, using fallback:"+str(ex))

        if bLoaded:
            # noinspection PyUnboundLocalVariable
            iInet_num = getattr(netifaces, uInet_Type)
            aInterfaces:List = netifaces.interfaces()

            for uNetiface in aInterfaces:
                dNetInfo:Dict    = netifaces.ifaddresses(uNetiface)
                aNetDetails:List = dNetInfo.get(iInet_num)
                if aNetDetails is not None and len(aNetDetails)>0:
                    dNetDetails:Dict = aNetDetails[0]
                    aFound.append(dNetDetails)
                    if uNetiface == uPreferredAdapter:
                        aFound = [dNetDetails]
                        break

            # we prefer a local subnet if given
            if len(aFound)>0:
                uRet = aFound[-1]['broadcast']

            for dFound in aFound:
                if dFound["addr"].startswith("192"):
                    uRet=dFound['broadcast']
                    break
        else:
            # Fallback on all platforms, if netifaces doesn't work
            aIPV4:List=Globals.uIPAddressV4.split(".")
            uRet  = aIPV4[0] + '.' + aIPV4[1] + '.' + aIPV4[2] + '.255'
    except Exception as e:
        Logger.error("Error on GetSubnetV4:"+str(e))
    return uRet