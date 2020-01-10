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

# this is temporary as long netifaces does not work on android

import socket
from kivy import Logger
from ORCA.utils.LogError  import LogError


__all__ = ['GetIPAddressV6']

def GetIPAddressV6() -> str:

    # Under construction

    uIP:str       = u''

    # Fast but not safe
    try:
        s:socket.socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        # Not necessary successfull
        s.connect(('2001:0db8:85a3:0000:0000:8a2e:0370:7334', 1))
        uIP = s.getsockname()[0]
    except Exception as e:
        LogError(uMsg="Failure on GetIPAddressV6", oException=e)
        return uIP
    finally:
        s.close()

    Logger.debug("Found IPv6 Address:"+uIP)

    return uIP
