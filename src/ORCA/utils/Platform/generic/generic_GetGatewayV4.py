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

from typing import Dict
from kivy import Logger
import ORCA.Globals as Globals

try:
    import netifaces
except Exception as ex:
    Logger.error("Can't load netifaces:"+str(ex))

__all__ = ['GetGatewayV4']

def GetGatewayV4() -> str:

    uFamily:str    = u'AF_INET'
    iInet_num:int

    try:
        iInet_num = getattr(netifaces, uFamily)
        dGateways:Dict = netifaces.gateways()
        # noinspection PyTypeChecker
        uIP  = dGateways['default'][iInet_num][0]
    except Exception as e:
        Logger.error("Error on GetGatewayV4, using fallback:"+str(e))
        uIP:str = Globals.uIPAddressV4[:Globals.uIPAddressV4.rfind(".")] + '.1'
    return uIP