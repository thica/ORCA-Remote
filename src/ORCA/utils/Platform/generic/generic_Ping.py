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

import os
from kivy.logger             import Logger
from ORCA.utils.LogError     import LogError

def Ping(uHostname:str) -> bool:
    """ executes an ping statement (Windows Version) """

    try:
        #response = os.system(u"ping -c 1 -w 1 " + uHostname)
        uCmd:str = u"ping -w 500 -c 1 " + uHostname
        Logger.debug('Ping: Sending Command :'+uCmd)
        response = os.system(uCmd)
        Logger.debug('Ping returned :'+str(response))
    except Exception as e:
        LogError(uMsg='Ping: Error on Ping:',oException=e)
        return True

    return response == 0
