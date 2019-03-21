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

from importlib              import import_module
from kivy.logger            import Logger
from kivy.utils             import platform
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.LogError    import LogError
import kivy.core.window

import ORCA.Globals as Globals

__all__ = ['OS_ToPath',
           'OS_SystemIsOnline',
           'OS_Ping',
           'OS_GetUserDataPath',
           'OS_GetDefaultNetworkCheckMode',
           'OS_GetDefaultStretchMode',
           'OS_GetWindowSize',
           'OS_GetLocale',
           'OS_GetRotationObject',
           'OS_GetUserDownloadsDataPath',
           'OS_GetSystemUserPath',
           'OS_GetInstallationDataPath'
           'OS_Platform',
           'OS_RegisterSoundProvider',
           'OS_Vibrate'
          ]


def FunctionDummy(**kwargs):
    return None

dFunctionCache={}

def GetFunction(uFunctionName):

    oFunction=dFunctionCache.get(uFunctionName)
    if oFunction is not None:
        return oFunction

    uModule =  u'%s.%s_%s' % ("ORCA.utils.Platform",Globals.uPlatform,uFunctionName)
    try:
        oFunction = getattr(import_module(uModule), uFunctionName)
        Logger.info(u"Loaded Platform Module "+uModule)
        dFunctionCache[uFunctionName] = oFunction
        return oFunction
    except Exception as e:
        # LogError ("loading failed:"+uModule,e)
        pass
    uModule =  '%s.%s_%s' % ("ORCA.utils.Platform","generic",uFunctionName)
    try:
        oFunction = getattr(import_module(uModule), uFunctionName)
        Logger.info(u"Loaded Platform Module "+uModule)
        dFunctionCache[uFunctionName] = oFunction
        return oFunction
    except Exception as e:
        # LogError ("loading failed:"+uModule,e)
        pass
    Logger.error("Can't load platform module "+ uFunctionName)
    dFunctionCache[uFunctionName] = FunctionDummy
    return FunctionDummy

def OS_Platform():
    return ToUnicode(platform)

def OS_ToPath(uPath):
    """ converts a path to a valid os specific path string """
    return GetFunction("ToPath")(uPath)

def OS_Ping(uHostname):
    """ executes an ping statement """
    return GetFunction("Ping")(uHostname)

def OS_GetUserDataPath():
    """ Gets the path to the user folder (This might NOT be the OS User Folder"""
    return GetFunction("GetUserDataPath")()

def OS_GetUserDownloadsDataPath():
    """ Gets the path to the user downloads folder """
    return GetFunction("GetUserDownloadsDataPath")()

def OS_GetSystemUserPath():
    """ Gets the path to the system user folder """
    return GetFunction("GetSystemUserPath")()

def OS_GetInstallationDataPath():
    """ Gets the path to the folder, where the installler places the Orca Files"""
    return GetFunction("GetInstallationDataPath")()

def OS_Vibrate(fDuration=0.05):
    """ Vibrates a device """
    return GetFunction("Vibrate")(fDuration)

def OS_GetDefaultNetworkCheckMode():
    """ returns the default way for an OS hpw to check if a device is online"""
    return GetFunction("GetDefaultNetworkCheckMode")()

def OS_GetDefaultStretchMode():
    """ Stretchmode: could be "STRETCH" or "CENTER" or "TOPLEFT" or "RESIZE" """
    return GetFunction("GetDefaultStretchMode")()

def OS_GetLocale():
    return GetFunction("GetLocale")()

def OS_GetRotationObject():
    """ returns the os-specific object to perform rotation tasks"""
    return GetFunction("cRotation")()

def OS_SystemIsOnline():
    """
    verifies, if the system has a network connection by system APIs (not by ping)
    returns true, if OS doesn't support it
    """
    return GetFunction("SystemIsOnline")()

def OS_RegisterSoundProvider():
    return GetFunction("RegisterSoundProvider")()

def OS_GetWindowSize():
    Globals.iAppWidth  = kivy.core.window.Window.size[0]
    Globals.iAppHeight = kivy.core.window.Window.size[1]

