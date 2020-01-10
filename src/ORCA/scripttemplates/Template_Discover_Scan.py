# -*- coding: utf-8 -*-
#

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
from __future__                             import annotations

from typing                                 import Dict
from typing                                 import List
from typing                                 import Union
from typing                                 import Callable
from typing                                 import Tuple

import threading
from kivy.logger                            import Logger
from kivy.uix.button                        import Button

from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.LogError                    import LogErrorSmall
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.vars.QueryDict                    import QueryDict
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.Network                     import Ping

import ORCA.Globals as Globals


class cDiscoverScriptTemplate_Scan(cDiscoverScriptTemplate):

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cDiscoverScriptTemplate_Scan):
            cBaseScriptSettings.__init__(self,oScript)
            self.aIniSettings.fTimeOut = 1.0

    def __init__(self):
        cDiscoverScriptTemplate.__init__(self)
        self.uSubType:str                       = u''
        self.iPort:int                          = 80
        self.aResults:List[QueryDict]           = []
        self.aThreads:List[threading.Thread]    = []
        self.uNothingFoundMessage               = u'Discover - Networkcan: Could not find a device on the network'

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """
        cDiscoverScriptTemplate.Init(self, uObjectName, oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def ListDiscover(self) -> None:
        dArgs:Dict = {"onlyonce": 0}
        dDevice:QueryDict
        dResult: QueryDict
        self.Discover(**dArgs)

        try:
            for dResult in self.aResults:
                uTageLine,dDevice,aLine       = self.ParseResult(dResult)
                if self.dDevices.get(uTageLine) is None:
                    self.dDevices[uTageLine] = dDevice
                    self.AddLine(aLine, dDevice)
        except Exception as e:
            LogErrorSmall(uMsg=u'Error on scan discover',oException=e)


    def Discover(self,**kwargs) -> Dict:

        uIP:str

        uConfigName:str                = kwargs.get('configname',self.uConfigName)
        oSetting:cBaseScriptSettings   = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut:float                 = ToFloat(kwargs.get('timeout',oSetting.aIniSettings.fTimeOut))
        bOnlyOnce:bool                 = ToBool(kwargs.get('onlyonce', "1"))
        uIPSubNet:str                  = Globals.uIPGateWayV4
        uIPSubNet:str                  = uIPSubNet[:uIPSubNet.rfind(".")]+"."

        del self.aResults[:]
        del self.aThreads[:]

        for i in range(1,255):
            uIP = uIPSubNet+str(i)
            oThread:cThread_CheckIP = self.GetThreadClass()(uIP=uIP,bOnlyOnce=bOnlyOnce,fTimeOut=fTimeOut, oCaller=self)
            self.aThreads.append(oThread)
            oThread.start()

        for oThread in self.aThreads:
            oThread.join()

        if len(self.aResults) >0:
            return self.CreateReturnDict(self.aResults[0])
        else:
            Logger.debug(self.uNothingFoundMessage)
            return self.CreateReturnDict(None)

    def GetHeaderLabels(self) -> List[str]:
        # Empty function
        Logger.error("You must implement GetHeaderLabels")
        return ['']

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:
        Logger.error("You must implement CreateDiscoverList_ShowDetails")
        dDevice:QueryDict = oButton.dDevice
        uText:str = u"$lvar(5029): %s \n" % dDevice.sFoundIP
        ShowMessagePopUp(uMessage=uText)

    # noinspection PyMethodMayBeStatic
    def CreateReturnDict(self,dResult:Union[QueryDict,None]) -> Dict:
        Logger.error("You must implement CreateReturnDict")
        uHost: str = u""
        if dResult is not None:
            uHost= dResult["uIP"]
        return {'Host': uHost,'Exception': None}

    # noinspection PyMethodMayBeStatic
    def ParseResult(self,dResult:QueryDict) -> Tuple[str,QueryDict,List]:
        Logger.error("You must implement ParseResult")
        dDevice:QueryDict = QueryDict()
        dDevice.sFoundIP  = dResult["uIP"]
        uTageLine:str     = dDevice.sFoundIP
        aLine:List        = [dDevice.sFoundIP]
        Logger.info(u'Bingo: Discovered Enigma device %s:%s' % (dDevice.uFoundModel, dDevice.sFoundIP))
        return uTageLine,dDevice,aLine

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return {"TimeOut":{"type": "numericfloat", "order":0, "title": "$lvar(6019)", "desc": "$lvar(6020)","key": "timeout", "default":"1.0"}}

    # noinspection PyMethodMayBeStatic
    def GetThreadClass(self) -> Callable:
        Logger.error("You must implement GetThreadClass")
        return cThread_CheckIP

# this is dummy code, which just pings the IP. must be replaced which real code to find a device by scan
class cThread_CheckIP(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, uIP:str, bOnlyOnce:bool,fTimeOut:float,oCaller:cDiscoverScriptTemplate_Scan):
        threading.Thread.__init__(self)
        self.uIP:str                                = uIP
        self.bOnlyOnce:bool                         = bOnlyOnce
        self.oCaller:cDiscoverScriptTemplate_Scan   = oCaller
        self.fTimeOut:float                         = fTimeOut

    def run(self) -> None:
        bReturnNow = False
        if self.bOnlyOnce:
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
        if bReturnNow:
            return
        self.SendCommand()

    def SendCommand(self) -> None:
        dResult:QueryDict = QueryDict()
        try:
            if Ping(self.uIP):
                dResult.uIP          = self.uIP
                self.oCaller.aResults.append(dResult)
        except Exception as e:
            self.oCaller.ShowError(uMsg="Error on send:", oException=e)
        return

