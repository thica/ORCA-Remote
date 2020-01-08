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

# this is temporary as long netifaces does not work on android

'''
This module allows you to get the IP address of your Kivy/python-for-android app.
It was created by Ryan Marvin and is free to use. (marvinryan@ymail.com)
Credit to Bruno Adele for the int_to_ip method
'''
#Required : ACCESS_WIFI_STATE permission, pyjnius

from kivy.logger                                    import Logger
from ORCA.utils.LogError                            import LogError
# noinspection PyUnresolvedReferences
from jnius                                          import detach
from ORCA.utils.Platform.android.android_helper     import GetAndroidModule

__all__ = ['GetIPAddressV4']

def Int2IP(iIP_Num:int) -> str:
    iOc1:int = int(iIP_Num / 16777216) % 256
    iOc2:int = int(iIP_Num / 65536) % 256
    iOc3:int = int(iIP_Num / 256) % 256
    iOc4:int = int(iIP_Num) % 256
    return '%d.%d.%d.%d' %(iOc4,iOc3,iOc2,iOc1)

def GetIPAddressV4() -> str:

    uIP = "127.0.0.0"
    try:
        cContext             = GetAndroidModule("Context","android.content")
        cPythonActivity      = GetAndroidModule("PythonActivity")
        oPythonActivity      = cPythonActivity.mActivity
        oWifiManager         = oPythonActivity.getSystemService(cContext.WIFI_SERVICE)

        oIP = oWifiManager.getConnectionInfo()
        iIP = oIP.getIpAddress()
        uIP = Int2IP(int(iIP))
        # detach()
        Logger.debug("Found IPv4 Address:"+uIP)

    except Exception as e:
        LogError(uMsg='GetGatewayV4:',oException=e)

    return uIP
