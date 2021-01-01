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

from kivy.logger        import Logger
from ORCA.utils.Path    import cPath
from ORCA.vars.Helpers  import GetEnvVar

def GetInstallationDataPath() -> cPath:
    """ Gets the path to the folder where the installer places the ORCA files"""

    '''
    The environment ist
    'ANDROID_ROOT': '/system', 'ANDROID_ASSETS': '/system/app', 'ANDROID_DATA': '/data', 'ANDROID_STORAGE': '/storage', 'EXTERNAL_STORAGE': '/sdcard', 'ASEC_MOUNTPOINT': '/mnt/asec', 'BOOTCLASSPATH': '/system/framework/core-oj.jar:/system/framework/core-libart.jar:/system/framework/conscrypt.jar:/system/framework/okhttp.jar:/system/framework/core-junit.jar:/system/framework/bouncycastle.jar:/system/framework/ext.jar:/system/framework/framework.jar:/system/framework/telephony-common.jar:/system/framework/voip-common.jar:/system/framework/ims-common.jar:/system/framework/apache-xml.jar:/system/framework/org.apache.http.legacy.boot.jar', 'SYSTEMSERVERCLASSPATH': '/system/framework/services.jar:/system/framework/ethernet-service.jar:/system/framework/wifi-service.jar', 'ANDROID_SOCKET_zygote': '8', 'ANDROID_ENTRYPOINT': 'main.pyc', 'ANDROID_ARGUMENT': '/data/user/0/org.orca.orca/files/app', 'ANDROID_APP_PATH': '/data/user/0/org.orca.orca/files/app', 'ANDROID_PRIVATE': '/data/user/0/org.orca.orca/files', 'ANDROID_UNPACK': '/data/user/0/org.orca.orca/files/app', 'PYTHONHOME': '/data/user/0/org.orca.orca/files/app', 'PYTHONPATH': '/data/user/0/org.orca.orca/files/app:/data/user/0/org.orca.orca/files/app/lib', 'PYTHONOPTIMIZE': '2', 'P4A_BOOTSTRAP': 'SDL2', 'PYTHON_NAME': 'python', 'P4A_IS_WINDOWED': 'True', 'P4A_ORIENTATION': 'sensor', 'P4A_NUMERIC_VERSION': 'None', 'P4A_MINSDK': '21', 'LC_CTYPE': 'C.UTF-8'})
    # we expect as result
    # /data/data/org.orca.orca/files/app
    
    Access to the environment looks like

    Environment     = autoclass('android.os.Environment')
    tt1:str  = Environment.getStorageDirectory().getPath()
    tt2:str   = Environment.getRootDirectory().getPath()
    tt3:str   = Environment.getDataDirectory().getPath()

    Android getStorageDirectory() = /storage
    Android getRootDirectory() = /system
    Android getDataDirectory() = /data
    
    So we make it simple to utilize the environment var
    
    '''

    oPath = cPath(GetEnvVar(u"ANDROID_APP_PATH"))
    Logger.debug("Android GetInstallationDataPath = "+oPath.string)
    return oPath


