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

from typing                                 import Dict
from typing                                 import List
from typing                                 import Union
from typing                                 import Tuple
from typing                                 import Callable

import threading
import socket

from time                                   import sleep
from xml.etree.ElementTree                  import Element

from kivy.logger                            import Logger
from kivy.network.urlrequest                import UrlRequest
from kivy.uix.button                        import Button
from xml.etree.ElementTree                  import fromstring

from ORCA.scripttemplates.Template_Discover_Scan import cDiscoverScriptTemplate_Scan
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.vars.QueryDict                    import QueryDict
from ORCA.utils.XML                         import GetXMLTextValue


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


class cScript(cDiscoverScriptTemplate_Scan):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-Discover-Enigma
    WikiDoc:TOCTitle:Discover Enigma
    = Script Discover Enigma =

    The Enigma discover script discovers Enigma2 Receiver which have the web interface running. The enigma have to be powered on and not in deep standby. In fact it get through al IP's from the subnet (1 to 255)
    You can filter the discover result by passing the following parameters::
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |timeout
    |Specifies the timeout for discover
    |}</div>

    The Enigma discovery will not perform a pure IP6 discovery, but will return a valid IPv6 address as well (if available)

    WikiDoc:End
    """

    def __init__(self):
        cDiscoverScriptTemplate_Scan.__init__(self)
        self.uSubType:str                       = u'Enigma'
        self.iPort:int                          = 80
        self.bStopWait:bool                     = False
        self.uNothingFoundMessage               = "Enigma-Discover: Could not find a Enigma Receiver on the network"

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(5035)','$lvar(6002)','$lvar(5031)']

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:
        dDevice:QueryDict = oButton.dDevice
        uText:str = u"$lvar(5029): %s \n" \
                    u"$lvar(5035): %s \n" \
                    u"$lvar(6002): %s \n"\
                    u"$lvar(5031): %s \n" % (dDevice.uFoundIP,dDevice.uFoundHostName,dDevice.uFoundPort,dDevice.uFoundModel)

        ShowMessagePopUp(uMessage=uText)

    # noinspection PyMethodMayBeStatic
    def CreateReturnDict(self,dResult:Union[QueryDict,None]) -> Dict:
        if dResult is not None:
            uHost:str      = dResult["ip"]
            iPort:int      = dResult["port"]
            uModel:str     = dResult["model"]
            uHostName:str  = dResult["hostname"]
            uIPVersion:str = dResult["ipversion"]
            return {'Host':uHost,'Port':iPort,'Model':uModel,'Hostname':uHostName,"IPVersion":uIPVersion ,'Exception':None}
        return {'Host':'','Port':0,'Model':'','Hostname':'',"IPVersion":'' ,'Exception':None}

    # noinspection PyMethodMayBeStatic
    def ParseResult(self,dResult:QueryDict) -> Tuple[str,QueryDict,List]:
        dDevice:QueryDict       = QueryDict()
        dDevice.uFoundIP        = dResult["ip"]
        dDevice.uFoundPort      = str(dResult["port"])
        dDevice.uFoundModel     = dResult["model"]
        dDevice.uFoundHostName  = dResult["hostname"]

        uTageLine:str     = dDevice.uFoundIP + dDevice.uFoundModel
        aLine:List        = [dDevice.uFoundIP, dDevice.uFoundHostName, dDevice.uFoundPort, dDevice.uFoundMode]
        Logger.info(u'Bingo: Discovered Enigma device %s' % dDevice.uFoundIP)
        return uTageLine,dDevice,aLine

    # noinspection PyMethodMayBeStatic
    def GetThreadClass(self) -> Callable:
        return cThread_CheckIP


# noinspection PyUnusedLocal
class cThread_CheckIP(threading.Thread):
    def __init__(self, uIP:str, bOnlyOnce:bool,fTimeOut:float,oCaller:cScript):
        threading.Thread.__init__(self)
        self.uIP:str                     = uIP
        self.bOnlyOnce:bool              = bOnlyOnce
        self.oCaller:cScript             = oCaller
        self.fTimeOut:float              = fTimeOut
        self.bStopWait:bool              = False
        self.oReq:Union[UrlRequest,None] = None

    def run(self) -> None:
        if self.bOnlyOnce:
            if len(self.oCaller.aResults)>0:
                return
        self.SendCommand()

    def SendCommand(self) -> None:
        dResult:QueryDict = QueryDict()
        self.bStopWait      = False
        uUrlFull:str = "http://"+self.uIP+"/web/about"
        try:
            self.oReq = UrlRequest(uUrlFull,method="GET",timeout=self.fTimeOut,on_error=self.OnResponse,on_success=self.OnResponse)
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
                        # Logger.error("Cant get Hostname:"+oRet.uFoundIP+" "+str(e))
                        pass

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

    def OnResponse(self,request,error) -> None:
        self.bStopWait = True


