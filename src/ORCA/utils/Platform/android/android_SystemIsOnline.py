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

from kivy.logger                          import Logger
# noinspection PyUnresolvedReferences
from jnius                                import detach
from ORCA.utils.LogError                  import LogError
from ORCA.utils.Platform.android_helper   import GetAndroidModule


def SystemIsOnline():
    """
    verifies, if the system has a network connection by system APIs (not by ping)
    returns true, if OS doesn't support it
    """
    try:
        Logger.debug("Checking Android network connectivity")
        cActivity            = GetAndroidModule("Activity","android.app")
        cPythonActivity      = GetAndroidModule("PythonActivity")
        cConnectivityManager = GetAndroidModule("ConnectivityManager","android.net")
        oPythonActivity      = cPythonActivity.mActivity
        oConnectionManager   = oPythonActivity.getSystemService(cActivity.CONNECTIVITY_SERVICE)
        bConnection          = oConnectionManager.getNetworkInfo(cConnectivityManager.TYPE_WIFI).isConnectedOrConnecting()

        if bConnection:
            detach()
            return True
        else:
            bConnection = oConnectionManager.getNetworkInfo(cConnectivityManager.TYPE_MOBILE).isConnectedOrConnecting()
            detach()
            if bConnection:
                return True
            else:
                return False
    except Exception as e:
        LogError('SystemIsOnline:',e)
        return True


def SystemIsOnlineOld():
    """
    verifies, if the system has a network connection by system APIs (not by ping)
    returns true, if OS doesn't support it
    """
    try:
        Logger.debug("Checking Android network connectivity")
        Hardware = GetAndroidModule("Hardware")
        bRet=Hardware.checkNetwork()
        detach()
        return bRet
    except Exception as e:
        LogError('SystemIsOnline:',e)
        return True

