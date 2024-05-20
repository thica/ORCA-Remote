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

from ifaddr import get_adapters

from kivy import Logger
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.vars.QueryDict    import TypedQueryDict

from ORCA.Globals import Globals


__all__ = ['GetInterfaceName']


def GetInterfaceName() -> TypedQueryDict:

    dRet:TypedQueryDict=TypedQueryDict()
    dRet.uPysicalAdapterName=''
    dRet.uOSAdapterName=''
    dRet.uOSAdapterNiceName=''

    try:

        aAdapters:List

        aAdapters = get_adapters()
        for oAdapter in aAdapters:
            # print ("IPs of network adapter " + oAdapter.nice_name)
            for oIP in oAdapter.ips:
                # print ("%s %s" % (oIP.ip,Globals.uIPAddressV4))
                # print (oIP)
                if oIP.ip == Globals.uIPAddressV4:
                    dRet.uPysicalAdapterName    = oAdapter.nice_name
                    dRet.uOSAdapterName         = ToUnicode(oAdapter.name)
                    dRet.uOSAdapterNiceName     = oIP.nice_name
                    return dRet

    except Exception as e:
        Logger.error('Error on GetInterfaceName:'+str(e))

    return dRet





