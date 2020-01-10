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

import uuid
import re

from kivy import Logger

try:
    import netifaces
except Exception as ex:
    Logger.error("Can't load netifaces:"+str(ex))

import ORCA.Globals as Globals

__all__ = ['GetMACAddress']

def GetMACAddress() -> List:

    uInet_Type:str        = u'AF_INET'
    iInet_num:int

    uRetColon:str = u'00:00:00:00:00:00'
    uRetDash:str  = u'00-00-00-00-00-00'

    try:
        iInet_num = getattr(netifaces, uInet_Type)
        aInterfaces:List = netifaces.interfaces()
        for uNetiface in aInterfaces:
            dNetInfo:Dict = netifaces.ifaddresses(uNetiface)
            aNetDetails:List = dNetInfo.get(iInet_num)
            if aNetDetails is not None and len(aNetDetails)>0:
                dNetDetails:Dict = aNetDetails[0]
                if dNetDetails["addr"] == Globals.uIPAddressV4:
                    uRetColon = netifaces.ifaddresses(uNetiface)[netifaces.AF_LINK][0]['addr']
                    uRetDash  = uRetColon.replace(":","-")
                    return uRetColon,uRetDash
    except Exception:
        pass

    try:
        uRetColon = u':'.join(re.findall('..', '%012x' % uuid.getnode()))
        uRetDash  = u'-'.join(re.findall('..', '%012x' % uuid.getnode()))
    except Exception as e:
        Logger.error("Error on GetMACAdress:"+str(e))
    return uRetColon,uRetDash
