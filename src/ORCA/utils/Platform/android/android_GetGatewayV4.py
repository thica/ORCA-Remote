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

from kivy import Logger
import ORCA.Globals as Globals

__all__ = ['GetGatewayV4']

def GetGatewayV4() -> str:
    # this is not really correct, but works a work around until we got netifaces working on android
    uIP:str = Globals.uIPAddressV4[:Globals.uIPAddressV4.rfind(".")] + '.1'
    Logger.debug("Found Gateway4 Address:"+uIP)
    return uIP