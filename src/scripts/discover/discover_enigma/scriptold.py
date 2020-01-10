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
from __future__ import annotations

from typing import Dict
from typing import List
from typing import Union

from time import sleep
import threading
import socket
from xml.etree.ElementTree                  import Element

from kivy.logger                            import Logger
from kivy.network.urlrequest                import UrlRequest
from kivy.uix.button                        import Button
from xml.etree.ElementTree                  import fromstring

from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.LogError                    import LogErrorSmall
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.vars.QueryDict                    import QueryDict
from ORCA.utils.XML                         import GetXMLTextValue
import ORCA.Globals as Globals
from ORCA.utils.FileName                    import cFileName


'''
<root>
  <repositorymanager>
    <entry>
      <name>Enigma Discover</name>
      <description language='English'>Discover Enigma Receiver via the webinterface</description>
      <description language='German'>Erkennt Enigma Reveiver mittels des Web Interfaces</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_enigma</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_enigame.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


class cScript(cDiscoverScriptTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-Discover-Enigma
    WikiDoc:TOCTitle:Discover Enigma
    = Script Discover Enigma =

    The Enigma discover script discovers Enigma2 Receiver which have the web interface running. The engima have to be powered on and not in deep standby. In fact it get through al IP's from the subnet (1 to 255)
    You can filter the discover result by passing the following parameters::
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |timeout
    |Specifies the timout for discover
    |}</div>

    The Enigma Discovery will not peform a pure IP6 discovery, but will return a valid IPv& address as well (if available)

    WikiDoc:End
    """
    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aIniSettings.fTimeOut = 1.0

    def __init__(self):
        cDiscoverScriptTemplate.__init__(self)
        self.uSubType:str                       = u'Enigma'
        self.iPort:int                          = 80
        self.bStopWait:bool                     = False
        self.aResults:List[QueryDict]           = []
        self.aThreads:List[threading.Thread]    = []

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """
        cDiscoverScriptTemplate.Init(self, uObjectName, oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(5035)','$lvar(6002)','$lvar(5031)']

    def ListDiscover(self) -> None:
        dArgs:Dict = {"onlyonce": 0}
        dDevice:QueryDict
        dResult: QueryDict
        self.Discover(**dArgs)

        try:

            for dResult in self.aResults:
                dDevice                 = QueryDict()
                dDevice.sFoundIP        = dResult["ip"]
                dDevice.uFoundPort      = str(dResult["port"])
                dDevice.uFoundModel     = dResult["model"]
                dDevice.uFoundHostName  = dResult["hostname"]
                Logger.info(u'Bingo: Discovered device %s:%s' % (dDevice.uFoundModel, dDevice.sFoundIP))
                uTageLine = dDevice.sFoundIP + dDevice.uFoundModel
                if self.dDevices.get(uTageLine) is None:
                    self.dDevices[uTageLine] = dDevice
                    self.AddLine([dDevice.sFoundIP, dDevice.uFoundHostName, dDevice.uFoundPort, dDevice.uFoundModel], dDevice)
        except Exception as e:
            LogErrorSmall(uMsg=u'Error on Enigma discover',oException=e)

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:QueryDict = oButton.dDevice

        uText:str = u"$lvar(5029): %s \n" \
                    u"$lvar(5035): %s \n" \
                    u"$lvar(6002): %s \n"\
                    u"$lvar(5031): %s \n" % (dDevice.sFoundIP,dDevice.uFoundHostName,dDevice.uFoundPort,dDevice.uFoundModel)

        ShowMessagePopUp(uMessage=uText)

    def Discover(self,**kwargs) -> Dict:

        uIP:str

        uConfigName:str                = kwargs.get('configname',self.uConfigName)
        oSetting:cBaseScriptSettings   = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut:float                 = ToFloat(kwargs.get('timeout',oSetting.aIniSettings.fTimeOut))
        bOnlyOnce:bool                 = ToBool(kwargs.get('onlyonce', "1"))

        del self.aResults[:]
        del self.aThreads[:]

        uIPSubNet:str = Globals.uIPGateWayV4
        uIPSubNet:str = uIPSubNet[:uIPSubNet.rfind(".")]+"."

        for i in range(1,255):
            uIP = uIPSubNet+str(i)
            oThread:cThread_CheckIP = cThread_CheckIP(uIP=uIP,bOnlyOnce=bOnlyOnce,fTimeOut=fTimeOut, oCaller=self)
            self.aThreads.append(oThread)
            oThread.start()

        for oT in self.aThreads:
            oT.join()

        if len(self.aResults):
            uHost:str      = self.aResults[0]["ip"]
            uPort:str      = self.aResults[0]["port"]
            uModel:str     = self.aResults[0]["model"]
            uHostName:str  = self.aResults[0]["hostname"]
            uIPVersion:str = self.aResults[0]["ipversion"]
            return {'Host':uHost,'Port':uPort,'Model':uModel,'Hostname':uHostName,"IPVersion":uIPVersion ,'Exception':None}

        LogErrorSmall(uMsg="Enigma-Discover: Could not find a Enigma Receiver on the network")
        return {'Host':'','Port':'','Model':'','Hostname':'',"IPVersion":'' ,'Exception':None}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return {"TimeOut":{"type": "numericfloat", "order":0, "title": "$lvar(6019)", "desc": "$lvar(6020)","key": "timeout", "default":"1.0"}}


# noinspection PyUnusedLocal
class cThread_CheckIP(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, uIP:str, bOnlyOnce:bool,fTimeOut:float,oCaller:cScript):
        threading.Thread.__init__(self)
        self.uIP:str         = uIP
        self.bOnlyOnce:bool  = bOnlyOnce
        self.oCaller:cScript = oCaller
        self.fTimeOut:float  = fTimeOut
        self.bStopWait:bool  = False
        self.oReq:Union[UrlRequest,None] = None

    def run(self) -> None:

        bReturnNow = False
        if self.bOnlyOnce:
            cThread_CheckIP.oWaitLock.acquire()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            cThread_CheckIP.oWaitLock.release()
        if bReturnNow:
            return
        self.SendCommand()

    def SendCommand(self) -> None:
        dResult:QueryDict = QueryDict()
        self.bStopWait      = False
        uUrlFull:str = "http://"+self.uIP+"/web/about"
        try:
            self.oReq = UrlRequest(uUrlFull,method="GET",timeout=self.fTimeOut,on_error=self.OnError,on_success=self.OnReceive)
            self.NewWait(0.05)
            if self.oReq.resp_status is not None:
                uResult:str = self.oReq.result
                if "<e2abouts>" in uResult:
                    oXmlRoot:Element    = fromstring(uResult)
                    oXmlAbout:Element   = oXmlRoot.find("e2about")
                    uModel:str          = GetXMLTextValue(oXmlAbout, "e2model", False, "Enigma")
                    uFoundHostName:str  = ""
                    try:
                        uFoundHostName = socket.gethostbyaddr(self.uIP)[0]
                    except Exception:
                        # Logger.error("Cant get Hostname:"+oRet.sFoundIP+" "+str(e))
                        pass

                    cThread_CheckIP.oWaitLock.acquire()
                    dResult.ip          = self.uIP
                    dResult.port        = 80
                    dResult.model       = uModel
                    dResult.ipversion   = "IPv4"
                    dResult.hostname    = uFoundHostName

                    self.oCaller.aResults.append(dResult)
                    try:
                        uIP = ""
                        aIPs = socket.getaddrinfo(uFoundHostName,None)
                        for tIP in aIPs:
                            uIP =  "["+tIP[-1][0]+"]"
                            if ":" in uIP:
                                break
                        if ":" in uIP:
                            dResult.ip          = uIP
                            dResult.port        = 80
                            dResult.model       = uModel
                            dResult.ipversion   = "IPv6"
                            dResult.hostname    = uFoundHostName
                            self.oCaller.aResults.append(dResult)
                    except Exception:
                        pass

                    cThread_CheckIP.oWaitLock.release()
        except Exception as e:
            self.oCaller.ShowError(uMsg="Error on send:", oException=e)
        return

    def NewWait(self,delay) -> None:
        while self.oReq.resp_status is None:
            # noinspection PyProtectedMember
            self.oReq._dispatch_result(delay)
            sleep(delay)
            if self.bStopWait:
                self.bStopWait=False
                break

    def OnError(self,request,error) -> None:
        self.bStopWait      = True

    def OnFailure(self,request,result) -> None:
        self.bStopWait      = True

    def OnReceive(self,oRequest,oResult) -> None:
        self.bStopWait      = True


