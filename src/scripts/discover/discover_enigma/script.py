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
from typing                                 import Optional


import threading
import socket

from time                                   import sleep
from xml.etree.ElementTree                  import Element

from kivy.clock                             import Clock
from kivy.network.urlrequest                import UrlRequest
from kivy.uix.button                        import Button

from ORCA.scripttemplates.Template_Discover_Scan import cDiscoverScriptTemplate_Scan
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.vars.QueryDict                    import TypedQueryDict
from ORCA.utils.XML                         import GetXMLTextValue
from ORCA.utils.XML                         import LoadXMLString

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Enigma Discover</name>
      <description language='English'>Discover Enigma Receiver via the webinterface</description>
      <description language='German'>Erkennt Enigma Reveiver mittels des Web Interfaces</description>
      <author>Carsten Thielepape</author>
      <version>5.0.4</version>
      <minorcaversion>5.0.4</minorcaversion>
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
        super().__init__()
        self.uSubType:str                       = u'Enigma'
        self.iPort:int                          = 80
        self.bStopWait:bool                     = False
        self.uNothingFoundMessage               = u"Enigma-Discover: Could not find a Enigma Receiver on the network"
        self.uScriptTitle                       = u"Enigma Discovery local subnet"

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(5035)','$lvar(6002)','$lvar(5031)']

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:
        dDevice:TypedQueryDict = oButton.dDevice
        uText:str = u"$lvar(5029): %s \n" \
                    u"$lvar(5035): %s \n" \
                    u"$lvar(6002): %s \n"\
                    u"$lvar(5031): %s \n" % (dDevice.uIP,dDevice.uHostName,str(dDevice.iPort),dDevice.uModel)

        ShowMessagePopUp(uMessage=uText)

    # noinspection PyMethodMayBeStatic
    def CreateReturnDict(self,dResult:Optional[TypedQueryDict]) -> Dict:
        if dResult is not None:
            uHost:str      = dResult.uIP
            uPort:str      = str(dResult.iPort)
            uModel:str     = dResult.uModel
            uHostName:str  = dResult.uHostName
            uIPVersion:str = dResult.uIPVersion
            return {'Host':uHost,'Port':uPort,'Model':uModel,'Hostname':uHostName,"IPVersion":uIPVersion ,'Exception':None}
        return {'Host':'','Port':0,'Model':'','Hostname':'',"IPVersion":'' ,'Exception':None}

    # noinspection PyMethodMayBeStatic
    def ParseResult(self,dResult:TypedQueryDict) -> Tuple[str,TypedQueryDict,List]:
        dDevice:TypedQueryDict  = TypedQueryDict()
        dDevice.uFoundIP        = dResult.uIP
        dDevice.uFoundPort      = str(dResult.iPort)
        dDevice.uFoundModel     = dResult.uModel
        dDevice.uFoundHostName  = dResult.uHostName

        uTageLine:str     = dDevice.uFoundIP + dDevice.uFoundModel
        aLine:List        = [dDevice.uFoundIP, dDevice.uFoundHostName, dDevice.uFoundPort, dDevice.uFoundModel]
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

        self.bStopWait      = False
        uUrlFull:str = "http://"+self.uIP+"/web/about"
        try:
            self.oReq = UrlRequest(uUrlFull,method="GET",timeout=self.fTimeOut,on_error=self.OnResponse,on_success=self.OnResponse)
            self.NewWait(0.05)
            if self.oReq.resp_status is not None:
                uResult:str = self.oReq.result
                if "<e2abouts>" in uResult:
                    oXmlRoot:Element    = LoadXMLString(uXML=uResult)
                    oXmlAbout:Element   = oXmlRoot.find("e2about")
                    uModel:str          = GetXMLTextValue(oXMLNode=oXmlAbout, uTag="e2model", bMandatory=False, vDefault="Enigma")
                    uFoundHostName:str  = ""
                    try:
                        uFoundHostName = socket.gethostbyaddr(self.uIP)[0]
                    except Exception:
                        # Logger.error("Cant get Hostname:"+oRet.uFoundIP+" "+str(e))
                        pass

                    dResult:TypedQueryDict = TypedQueryDict()
                    dResult.uIP          = self.uIP
                    dResult.iPort        = 80
                    dResult.uModel       = uModel
                    dResult.uIPVersion   = "IPv4"
                    dResult.uHostName    = uFoundHostName
                    self.oCaller.aResults.append(dResult)
                    Globals.oNotifications.SendNotification(uNotification="DISCOVER_SCRIPTFOUND",**{"script":self,"scriptname":self.oCaller.uObjectName,"line":[dResult.uIP,dResult.uHostName, str(dResult.iPort), dResult.uModel],"device":dResult})
                    self.oCaller.ShowInfo(uMsg=u'Discovered Enigma device (V4) %s' % dResult.uIP)
                    try:
                        uIP = ""
                        aIPs = socket.getaddrinfo(uFoundHostName,None)
                        for tIP in aIPs:
                            uIP =  "["+tIP[-1][0]+"]"
                            if ":" in uIP:
                                break
                        if ":" in uIP:
                            dResult:TypedQueryDict = TypedQueryDict()
                            dResult.uIP          = uIP
                            dResult.iPort        = 80
                            dResult.uModel       = uModel
                            dResult.uIPVersion   = "IPv6"
                            dResult.uHostName    = uFoundHostName
                            self.oCaller.aResults.append(dResult)
                            Globals.oNotifications.SendNotification(uNotification="DISCOVER_SCRIPTFOUND",**{"script":self,"scriptname":self.oCaller.uObjectName,"line":[dResult.uIP,dResult.uHostName, str(dResult.iPort), dResult.uModel],"device":dResult})
                            self.oCaller.ShowInfo(uMsg=u'Discovered Enigma device (V6) %s' % dResult.uIP)
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


