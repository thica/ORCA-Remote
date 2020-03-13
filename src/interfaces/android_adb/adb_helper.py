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
from __future__  import annotations
from typing      import List
from typing      import Optional

import re

from kivy.logger            import Logger
from ORCA.utils.Path        import cPath
from ORCA.utils.Platform    import OS_GetSystemUserPath
from ORCA.vars.Access       import GetVar
from ORCA.vars.Access       import SetVar

import ORCA.Globals as Globals

from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

# noinspection PyUnusedLocal
class cADB_Helper:

    def __init__(self):
        self.aGlobalRSA_KEYS:List               = []
        self.oDevice:Optional[AdbDeviceTcp]     = None
        self.uHost:str                          = ''
        self.Load_RSA_KEYS()

    def Connect(self,uHost:str, uPort:str ,fTimeOut:float) -> cADB_Helper:
        self.uHost   = uHost
        self.oDevice = AdbDeviceTcp(uHost, int(uPort), default_timeout_s=fTimeOut)
        self.oDevice.connect(rsa_keys=self.aGlobalRSA_KEYS, auth_timeout_s=20.1)
        return self
    def Load_RSA_KEYS(self) -> None:
        # default adb key path
        aKeyPathes:List[cPath] = [cPath(OS_GetSystemUserPath() + '.android/adbkey')]

        #default Android Path
        if Globals.uPlatform==u'android':
            aKeyPathes.append(cPath(OS_GetSystemUserPath()+'misc/adb/adb_keys/adbkey'))

        #Download path
        aKeyPathes.append(Globals.oPathUserDownload+"/adbkey")

        for oPath in aKeyPathes:
            if oPath.Exists():
                try:
                    with open(oPath.string) as f:
                        oPriv   = f.read()
                        oSigner = PythonRSASigner('', oPriv)
                        self.aGlobalRSA_KEYS.append(oSigner)
                        Logger.info("RSA Keyfiles loaded from "+oPath.string)
                except Exception as e:
                    Logger.error("Error Loading RSA Keys from "+oPath.string+" "+str(e))
            else:
                Logger.debug("No RSA Keyfiles at "+oPath)

    # noinspection PyUnusedLocal
    def Shell(self, uCommand:str, fTimeOut:float=1.0) -> str:
        """Run command on the device, returning the output."""
        return self.oDevice.shell(uCommand)

    def GetAppList(self, uCommand:str, fTimeOut:float=1.0) -> str:
        """fetches the list of all installed apps from an Android device
           The result will be saved for later calls
         """
        uAppList: str = GetVar("ADB_APPLIST_" + self.uHost)
        if uAppList=='':
            uAppList = self.Shell(uCommand=uCommand, fTimeOut=fTimeOut)
            # Logger.debug("GetAppList:"+str(uAppList))
            # print (uAppList)
            SetVar("ADB_APPLIST_" + self.uHost, uAppList)
        return uAppList

    def GetAppName(self, uCommand:str, fTimeOut:float=1.0) -> str:
        uAppList:str=GetVar("ADB_APPLIST_"+self.uHost)
        return self.FindPackageName(uAppName=uCommand,uAppList=uAppList)

    # noinspection PyMethodMayBeStatic
    def GetAppIntent(self, uCommand:str, fTimeOut:float=1.0) ->str:

        uAppName:str
        uAppDump:str
        uIntent:str = u''
        uSearch:str
        uAppName,uAppDump = uCommand.split("|||")
        uSearch = uAppName+"/."
        aDumpLines:List[str] = uAppDump.splitlines()

        for uLine in aDumpLines:
            if uSearch in uLine:
                uIntent = uLine
            if "android.intent.category.LAUNCHER" in uLine or "android.intent.category.LEANBACK_LAUNCHER" in uLine:
                break
        if uIntent:
            uIntent = uIntent.strip().split(" ")[1]
        else:
            uSearch = uAppName
            for uLine in aDumpLines:
                if uSearch in uLine:
                    uIntent = uLine
                if "android.intent.category.LAUNCHER" in uLine or "android.intent.category.LEANBACK_LAUNCHER" in uLine:
                    break
            if uIntent:
                if "cmp=" in uIntent:
                    uIntent = uIntent.strip().split("cmp=")[1]
                    uIntent = uIntent[:-1]
                    # something hacky until we identify why this is wrong identified from the dump
                    uIntent=uIntent.replace(".nvidia","")
                else:
                    uIntent = uIntent.strip().split(" ")[1]
        return uIntent

    def Close(self) -> None:
        self.oDevice.close()

    # noinspection PyMethodMayBeStatic
    def FindPackageName(self,*,uAppList:str,uAppName:str) -> str:

        """  ^(?=.*amazon)(?=.*music).*$ """

        uPackageName:str = uAppName

        try:
            oResult=re.compile(uAppName,re.MULTILINE).search(uAppList)
            if oResult:
                # noinspection PyUnresolvedReferences
                uResult=uAppList[oResult.regs[0][0]:oResult.regs[0][1]]
                uPackageName = uResult.split(u"=")[-1]
        except Exception as e:
            Logger.info("FindPackageName: couldn't validate Appname as regex, returning the default value: %s (%s)" % (uAppName,str(e)))
        return uPackageName

