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


from kivy.logger                                    import Logger
# noinspection PyUnresolvedReferences
from jnius                                          import detach
from ORCA.utils.Platform.android.android_helper     import GetAndroidModule

__all__ = ['GetMACAddress']

def GetMACAddress() -> List[str]:

    """
    Retrieves the MAC Address on an Android device

    :return: A List of MAC Addresses (strings): First with colon as separator, second with colon as separator
    """

    uRetColon:str = '00:00:00:00:00:00'
    uRetDash:str  = '00-00-00-00-00-00'

    try:
        cContext             = GetAndroidModule('Context','android.content')
        cPythonActivity      = GetAndroidModule('PythonActivity')
        oPythonActivity      = cPythonActivity.mActivity
        oWifiManager         = oPythonActivity.getSystemService(cContext.WIFI_SERVICE)
        uRetColon            = oWifiManager.getConnectionInfo().getMacAddress()
        uRetDash             = uRetColon.replace(':','-')
    except Exception as e:
        Logger.error('Error on GetMACAddress:'+str(e))

    return [uRetColon,uRetDash]
