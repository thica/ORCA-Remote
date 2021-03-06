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

from typing                 import Dict
from typing                 import List
from typing                 import Tuple
from typing                 import Any
from typing                 import cast
from typing                 import Callable

from importlib              import import_module
from kivy.logger            import Logger
from kivy.utils             import platform
import kivy.core.window

import ORCA.Globals as Globals
from ORCA.utils.LogError import LogError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.utils.Path import cPath
else:
    from typing import TypeVar
    cPath = TypeVar("cPath")



__all__ = ['OS_ToPath',
           'OS_SystemIsOnline',
           'OS_Ping',
           'OS_CheckPermissions',
           'OS_GetUserDataPath',
           'OS_GetDefaultNetworkCheckMode',
           'OS_GetDefaultStretchMode',
           'OS_GetWindowSize',
           'OS_GetLocale',
           'OS_GetRotationObject',
           'OS_GetUserDownloadsDataPath',
           'OS_GetSystemUserPath',
           'OS_GetSystemTmpPath',
           'OS_GetInstallationDataPath',
           'OS_Platform',
           'OS_RegisterSoundProvider',
           'OS_RequestPermissions',
           'OS_Vibrate',
           'OS_GetGatewayV4',
           'OS_GetGatewayV6',
           'OS_GetIPAddressV4',
           'OS_GetIPAddressV6',
           'OS_GetSubnetV4',
           'OS_GetSubnetV6',
           'OS_GetMACAddress',
           'OS_GetDrives',
           'OS_GetPlaces'
          ]

# noinspection PyUnusedLocal
def FunctionDummy(**kwargs):
    """
    Dummy function in case, nothing is found
    :param kwargs:
    :return: None
    """
    return None

dFunctionCache:Dict[str,Callable]   = {}
dResultCache:Dict[str,Any]          = {}

def GetFunction(uFunctionName:str) -> Callable:
    """

    :param uFunctionName:
    :return:
    """
    oFunction: Callable
    uModule:   str
    uPlatform: str


    # python 3.9 should look this this?
    # if oFunction:=dFunctionCache.get(uFunctionName) is not None:
    #    return oFunction

    oFunction=dFunctionCache.get(uFunctionName)
    if oFunction is not None:
        return oFunction

    for uPlatform in [Globals.uPlatform,"generic"]:
        uModule =  u'%s.%s.%s_%s' % ("ORCA.utils.Platform",uPlatform,uPlatform,uFunctionName)
        try:
            oFunction = getattr(import_module(uModule), uFunctionName)
            Logger.info(u"Loaded platform module "+uModule)
            dFunctionCache[uFunctionName] = oFunction
            return oFunction
        except ModuleNotFoundError:
            pass
        except Exception as e:
            LogError (uMsg="Loading platform module '%s' failed!" % uModule,oException=e)

    Logger.error("Can't load platform module "+ uFunctionName)
    dFunctionCache[uFunctionName] = FunctionDummy
    return FunctionDummy

def CallFromCache(uFunctionName) -> Any:
    """ Returns a value of a function from the cache if already called
        Otherwise it will call the function a put the return value into the cache
    """
    oRet:Any
    if dResultCache.get(uFunctionName) is not None:
        return dResultCache.get(uFunctionName)
    oRet = GetFunction(uFunctionName)()
    dResultCache[uFunctionName] = oRet
    return oRet

def OS_CheckPermissions() -> bool:
    """  check and retrieve required permissions """
    return cast(bool,GetFunction("CheckPermissions")())

def OS_RequestPermissions() -> bool:
    """  Requests permissions from OS """
    return cast(bool,GetFunction("RequestPermissions")())

def OS_Platform() -> str:
    """
    Gets the current platform. Abstraction of the kivy platform function
    :return: A string, representing the platform
    """
    return platform

def OS_ToPath(uPath:str) -> str:
    """ converts a path to a valid os specific path string """
    return cast(str,GetFunction("ToPath")(uPath))

def OS_Ping(uHostname:str) -> bool:
    """ executes an ping statement """
    return cast(bool,GetFunction("Ping")(uHostname))

def OS_GetUserDataPath() -> cPath:
    """ Gets the path to the user folder (This might NOT be the OS User Folder"""
    return cast(cPath,CallFromCache("GetUserDataPath"))

def OS_GetUserDownloadsDataPath() -> cPath:
    """ Gets the path to the user downloads folder """
    return cast(cPath,CallFromCache("GetUserDownloadsDataPath"))

def OS_GetSystemUserPath() -> cPath:
    """ Gets the path to the system user folder """
    return cast(cPath,CallFromCache("GetSystemUserPath"))

def OS_GetInstallationDataPath() -> cPath:
    """ Gets the path to the folder, where the installer places the Orca Files"""
    return cast(cPath,CallFromCache("GetInstallationDataPath"))

def OS_Vibrate(fDuration:float=0.05) -> bool:
    """ Vibrates a device """
    return cast(bool,GetFunction("Vibrate")(fDuration))

def OS_GetDefaultNetworkCheckMode() -> str:
    """ returns the default way for an OS hpw to check if a device is online"""
    return cast(str,CallFromCache("GetDefaultNetworkCheckMode"))

def OS_GetDefaultStretchMode() -> str:
    """ Stretchmode: could be "STRETCH" or "CENTER" or "TOPLEFT" or "RESIZE" """
    return cast(str,CallFromCache("GetDefaultStretchMode"))

def OS_GetLocale() -> str:
    """
    Returns the current locale
    :return: the locale string
    """
    return cast(str,CallFromCache("GetLocale"))

def OS_GetRotationObject() -> Callable:
    """ returns the os-specific object to perform rotation tasks"""
    return cast(Callable,GetFunction("cRotation")())

def OS_SystemIsOnline() -> bool:
    """
    verifies, if the system has a network connection by system APIs (not by ping)
    returns true, if OS doesn't support it
    """
    return cast(bool,GetFunction("SystemIsOnline")())

def OS_RegisterSoundProvider() -> None:
    """
    Registers the sound provider
    Sound provider must be registered as the kivy team has remove the capabilities to play mp3 files
    :return:
    """
    GetFunction("RegisterSoundProvider")()
    return None

def OS_GetWindowSize() -> None:
    """
    Detects the current windows sizes and stores it in the Global structure
    """
    Globals.iAppWidth  = kivy.core.window.Window.size[0]
    Globals.iAppHeight = kivy.core.window.Window.size[1]
    return None

def OS_GetIPAddressV4() -> str:
    """
    Gets the V4 IP Address
    :return: a string representing the IP Address eg 192.168.1.100
    """
    return cast(str,CallFromCache("GetIPAddressV4"))

def OS_GetSubnetV4() -> str:
    """
    Gets the V4 Subnet
    :return: a string representing the subnet
    """
    return cast(str,CallFromCache("GetSubnetV4"))

def OS_GetGatewayV4() -> str:
    """
    Gets the V4 Gateway
    :return: a string representing the gateway
    """
    return cast(str,CallFromCache("GetGatewayV4"))

def OS_GetIPAddressV6() -> str:
    """
    Gets the V6 IP Address
    :return: a string representing the IP Address
    """
    return cast(str,CallFromCache("GetIPAddressV6"))

def OS_GetSubnetV6() -> str:
    """
    Gets the V6 Gateway
    :return: a string representing the gateway
    """
    return cast(str,CallFromCache("GetSubnetV6"))

def OS_GetGatewayV6() -> str:
    """
    Gets the V6 Gateway. This is from a network view rubbish
    :return: a string representing the gateway
    """
    return cast(str,CallFromCache("GetGatewayV6"))

def OS_GetMACAddress() -> List[str]:
    """
    Gets the Mac address of the device
    :return: A list, with both type of mac addresses (colon and dash separated)
    """
    return cast(List[str],CallFromCache("GetMACAddress"))

def OS_GetDrives() -> List[Tuple[str,str]]:
    """
    gets a list of local drives (drive letters on windows, /mnt and /media folder on Linux)
    :return: A list of tuples of drives (Name,System representation)
    """
    return cast(List[Tuple[str,str]],GetFunction("GetDrives")())

def OS_GetPlaces() -> List[Tuple[str,cPath]]:
    """
    gets a list of user folders (ed Video, Music, ...)
    :return: A list of folders (Name, Path)
    """
    return cast(List[Tuple[str,cPath]],GetFunction("GetPlaces")())

def OS_GetSystemTmpPath() -> cPath:
    """ Gets the system temporary """
    return cast(cPath,CallFromCache("GetSystemTmpPath"))

