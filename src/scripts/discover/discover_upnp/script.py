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
from typing import Tuple

from kivy.clock                             import Clock

import select
import socket
import threading

from time                                   import sleep
from xml.etree.ElementTree                  import Element

from kivy.network.urlrequest                import UrlRequest
from kivy.uix.button                        import Button

from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.LogError                    import LogError
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToList
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.XML                         import LoadXMLString
from ORCA.utils.Wildcard                    import MatchWildCard
from ORCA.vars.QueryDict                    import TypedQueryDict


import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>UPNP Discover</name>
      <description language='English'>Discover devices by upnp</description>
      <description language='German'>Erkennt bwz. sucht Geraete ueber upnp</description>
      <author>Carsten Thielepape</author>
      <version>5.0.4</version>
      <minorcaversion>5.0.4</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_upnp</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_upnp.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

def RemoveURN(uData:str) -> str:

    iPos:int
    iPosEnd:int

    iPos=uData.find('xmlns="')
    while iPos!=-1:
        iPosEnd=uData.find('"',iPos+10)
        if iPosEnd!=-1:
            uData=uData[:iPos]+uData[iPosEnd+1:]
            iPos=uData.find('xmlns="')

    iPos=uData.find('xmlns:r="')
    while iPos!=-1:
        iPosEnd=uData.find('"',iPos+10)
        if iPosEnd!=-1:
            uData=uData[:iPos]+uData[iPosEnd+1:]
            iPos=uData.find('xmlns:r="')

    return uData

class cScript(cDiscoverScriptTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-Discover-UPNP
    WikiDoc:TOCTitle:Discover UPNP
    = Script Discover UPNP =

    The UPNP discover script discover devices which runs a upnp server.
    You can filter the discover result by passing the following parameters::
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |discovermanufacturer
    |Discover models only from a specific manufacturer
    |-
    |discovermodels
    |Discover specific models
    |-
    |discoverprettyname
    |Some devices reports a pretty name (like mac address, or IP addrees, a a further name). You can specify to discover just aspecific preetty name
    |-
    |servicetypes
    |Specifies the servicetypes for discover (eg.: upnp:rootdevice)
    |-
    |ipversion
    |Specifies which IPVersion to use for discovery: Could be IPv4Only,IPv6Only,All,Auto. Auto prefers IPv6, if available
    |-
    |timeout
    |Specifies the timout for discover
    |}</div>

    Blank options will not be used. You could eg use the pretty name just to match a specific device, or just the manufacturer name to match all devices in the network of this manufacturer.

    WikiDoc:End
    """

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cScript):
            super().__init__(oScript)
            self.aIniSettings.fTimeOut = 15.0

    def __init__(self):
        super().__init__()
        self.uSubType:str                       = u'UPNP'
        self.bStopWait:bool                     = False
        self.aResults:List[TypedQueryDict]      = []
        self.dReq                               = TypedQueryDict()
        self.bDoNotWait:Bool                    = False
        self.uScriptTitle                       = u"SSDP/uPNP Discovery"


    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """

        super().Init(uObjectName=uObjectName, oFnObject=oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(5035)','$lvar(5030)','$lvar(5031)','$lvar(5032)','$lvar(SCRIPT_DISC_UPNP_1)']

    def ListDiscover(self) -> None:
        self.SendStartNotification()
        Clock.schedule_once(self.ListDiscover_Step2, 0)
        return

    def ListDiscover_Step2(self, *largs) -> None:

        dArgs:Dict              = {"onlyonce":      0,
                                   "servicetypes":  "ssdp:all",
                                   "ipversion":     "All",
                                   "donotwait":1}

        dDevices:Dict[str,TypedQueryDict]                = {}
        dDevice: TypedQueryDict

        self.Discover(**dArgs)

        '''
        for dDevice in self.aResults:
            uTageLine:str = dDevice.uFoundIP+dDevice.uFoundHostName+dDevice.uFoundManufacturer+dDevice.uFoundModel+dDevice.uFoundFriendlyName+dDevice.uFoundServiceType
            if dDevices.get(uTageLine) is None:
               dDevices[uTageLine]=dDevice
               self.AddLine([dDevice.uFoundIP,dDevice.uFoundHostName,dDevice.uFoundManufacturer,dDevice.uFoundModel,dDevice.uFoundFriendlyName,dDevice.uFoundServiceType],dDevice)
        '''
        return

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:TypedQueryDict = oButton.dDevice

        uText:str=  u"$lvar(5029): %s \n" \
                    u"$lvar(5035): %s \n" \
                    u"$lvar(5030): %s \n"\
                    u"$lvar(5031): %s \n"\
                    u"$lvar(5032): %s \n"\
                    u"$lvar(SCRIPT_DISC_UPNP_1): %s \n"\
                    u"\n"\
                    u"%s\n"\
                    u"\n"\
                    u"%s" % (dDevice.uFoundIP,dDevice.uFoundHostName,dDevice.uFoundManufacturer,dDevice.uFoundModel,dDevice.uFoundFriendlyName,dDevice.uFoundServiceType,dDevice.sData,dDevice.uResult)

        ShowMessagePopUp(uMessage=uText)


    def Discover(self,**kwargs) -> Dict:

        self.dReq.clear()
        uConfigName:str              = kwargs.get('configname',self.uConfigName)
        oSetting:cBaseScriptSettings = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        self.dReq.uManufacturer  = kwargs.get('manufacturer',"")
        self.dReq.uModels        = kwargs.get('models',"")
        self.dReq.uFriendlyName  = kwargs.get('prettyname',"")
        self.dReq.bReturnPort    = ToBool(kwargs.get('returnport',"0"))
        fTimeOut:float           = ToFloat(kwargs.get('timeout',oSetting.aIniSettings.fTimeOut))
        uParST:str               = kwargs.get('servicetypes',"ssdp:all")
        uIPVersion:str           = kwargs.get('ipversion',"IPv4Only")
        aST:List                 = uParST.split(',')
        bOnlyOnce:bool           = ToBool(kwargs.get('onlyonce',"1"))
        self.bDoNotWait          = ToBool(kwargs.get('donotwait',"0"))

        self.ShowDebug (uMsg=u'Try to discover %s device by UPNP:  Models: %s , PrettyName: %s ' % (self.dReq.uManufacturer,self.dReq.uModels, self.dReq.uFriendlyName ))

        del self.aResults[:]
        del self.aThreads[:]

        try:
            for uST in aST:
                if uIPVersion == "IPv4Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 == ""):
                    oThread = cThread_Discover_UPNP(bOnlyOnce=bOnlyOnce,dReq=self.dReq,uIPVersion="IPv4Only", fTimeOut=fTimeOut, uST=uST,oCaller=self)
                    self.aThreads.append(oThread)
                    self.aThreads[-1].start()
                if uIPVersion == "IPv6Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 != ""):
                    oThread = cThread_Discover_UPNP(bOnlyOnce=bOnlyOnce, dReq=self.dReq, uIPVersion="IPv6Only", fTimeOut=fTimeOut, uST=uST,oCaller=self)
                    self.aThreads.append(oThread)
                    self.aThreads[-1].start()

            if not self.bDoNotWait:
                for oT in self.aThreads:
                    oT.join()
                self.SendEndNotification()

                if len(self.aResults)>0:
                    return {"Host":self.aResults[0].uFoundIP,
                            "Hostname": self.aResults[0].uFoundHostName,
                            "Model":self.aResults[0].uFoundModel,
                            "FriendlyName":self.aResults[0].uFoundFriendlyName,
                            "Manufacturer":self.aResults[0].uFoundManufacturer,
                            "ServiceType":self.aResults[0].uFoundServiceType,
                            "IPVersion":self.aResults[0].uIPVersion,
                            'Exception': None}
                else:
                    self.ShowWarning(uMsg=u'No device found device %s:%s:%s' %(self.dReq.uManufacturer,self.dReq.uModels,self.dReq.uFriendlyName))
            else:
                self.ClockCheck=Clock.schedule_interval(self.CheckFinished,0.1)

            return {"Host": "",
                    "Hostname": "",
                    "Model": "",
                    "FriendlyName": "",
                    "Manufacturer": "",
                    "ServiceType": "",
                    "IPVersion": "",
                    'Exception': None}

        except Exception as e:
            LogError(uMsg=u'Error on discover uPnP',oException=e)
            return {"Host": "",
                    "Hostname": "",
                    "Model": "",
                    "FriendlyName": "",
                    "Manufacturer": "",
                    "ServiceType": "",
                    "IPVersion": "",
                    'Exception': e}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return  {"Manufacturer":    {"type": "string",       "order":0,  "title": "$lvar(6013)", "desc": "$lvar(6014)", "key": "manufacturer",    "default":""           },
                 "Models":          {"type": "string",       "order":1,  "title": "$lvar(6015)", "desc": "$lvar(6016)", "key": "models",          "default":""           },
                 "PrettyName":      {"type": "string",       "order":2,  "title": "$lvar(6017)", "desc": "$lvar(6018)", "key": "prettyname",      "default":""           },
                 "ServiceTypes":    {"type": "string",       "order":3,  "title": "$lvar(6023)", "desc": "$lvar(6024)", "key": "servicetypes",    "default":"urn:dial-multiscreen-org:service:dial:1,urn:schemas-upnp-org:service:AVTransport:1"},
                 "IP Version":      {"type": "scrolloptions","order":4,  "title": "$lvar(6037)", "desc": "$lvar(6038)", "key": "ipversion",       "default":"IPv4Only", "options":["IPv4Only","IPv6Only","All","Auto"]},
                 "TimeOut":         {"type": "numericfloat", "order":6,  "title": "$lvar(6019)", "desc": "$lvar(6020)", "key": "timeout",         "default":"15.0"}
                }


        #"ReturnPort":      {"type": "bool", "order": 4, "title": "$lvar(SCRIPT_DISC_UPNP_2)", "desc": "$lvar(SCRIPT_DISC_UPNP_3)", "key": "returnport", "default": "1"},


class cThread_Discover_UPNP(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, bOnlyOnce:bool,dReq:TypedQueryDict,uIPVersion:str, uST:str,fTimeOut:float,oCaller:cScript):
        threading.Thread.__init__(self)

        self.bOnlyOnce:bool     = bOnlyOnce
        self.uIPVersion:str     = uIPVersion
        self.oCaller:cScript    = oCaller
        self.fTimeOut:float     = fTimeOut
        self.uST:str            = uST
        self.bStopWait:bool     = False
        self.dReq:TypedQueryDict= dReq
        self.oUrlRequest:Union[None,UrlRequest] = None

    def run(self) -> None:

        bReturnNow:bool = False
        if self.bOnlyOnce:
            cThread_Discover_UPNP.oWaitLock.acquire()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            cThread_Discover_UPNP.oWaitLock.release()
        if bReturnNow:
            return
        self.Discover()

    def Discover(self) -> None:

        oSocket = None
        try:
            self.bStopWait      = False

            oSocket = self.SendDiscover()
            if oSocket:
                # Parse all results
                while True:
                    #we do not wait too long
                    aReady = select.select([oSocket], [], [],self.fTimeOut)
                    if aReady[0]:
                        # Get a response
                        byData, tSenderAddr = oSocket.recvfrom(1024)
                        uData = ToUnicode(byData)
                        dRet = self.GetDeviceDetails(uData=uData,tSenderAddr=tSenderAddr)
                        self.CheckDeviceDetails(dRet=dRet)
                        if dRet.bFound:
                            self.oCaller.ShowInfo(uMsg=u'Discovered device %s:%s:%s at %s:' %(dRet.uFoundManufacturer,dRet.uFoundModel,dRet.uFoundFriendlyName,dRet.uFoundIP))
                            try:
                                if dRet.uIPVersion == "IPv4":
                                    dRet.uFoundHostName = socket.gethostbyaddr(dRet.uFoundIP)[0]
                                elif dRet.uIPVersion == "IPv6":
                                    #todo: Does not work for unknown reasons
                                    dRet.uFoundHostName = socket.gethostbyaddr(dRet.uFoundIP)[0]
                            except Exception:
                                # Logger.error("Cant get Hostname:"+oRet.uFoundIP+" "+str(e))
                                pass
                            Globals.oNotifications.SendNotification(uNotification="DISCOVER_SCRIPTFOUND",**{"script":self,"scriptname":self.oCaller.uObjectName,"line":[dRet.uFoundIP,dRet.uFoundHostName,dRet.uFoundManufacturer,dRet.uFoundModel,dRet.uFoundFriendlyName,dRet.uFoundServiceType],"device":dRet})

                            cThread_Discover_UPNP.oWaitLock.acquire()
                            self.oCaller.aResults.append(dRet)
                            cThread_Discover_UPNP.oWaitLock.release()
                            if self.bOnlyOnce:
                                oSocket.close()
                                return
                    else:
                        break
                oSocket.close()
            # Logger.warning(u'No device found device %s:%s:%s' %(self.oReq.uManufacturer,self.oReq.uModels,self.oReq.uFriendlyName))
            return

        except Exception as e:
            self.oCaller.ShowError(uMsg=u'Error on discover uPnP (%s)' % self.uIPVersion, oException=e)
            if oSocket:
                oSocket.close()
            return

    def NewWait(self,delay):
        while self.oUrlRequest.resp_status is None:
            # noinspection PyProtectedMember
            self.oUrlRequest._dispatch_result(delay)
            sleep(delay)
            if self.bStopWait:
                self.bStopWait=False
                break

    # noinspection PyUnusedLocal
    def OnError(self,request,error):
        # todo re-enable when IPV6 address problem has been solved
        # self.oCaller.ShowError(uMsg=u'UPNP - Discover:Error Receiving Response',oException=error)
        self.bStopWait      = True

    def SendDiscover(self):

        iUDP_PORT = 1900

        if self.uIPVersion=="IPv4Only":
            uUDP_IP     = u'239.255.255.250'
            bMessage = ToBytes(u'M-SEARCH * HTTP/1.1\r\nHOST: %s:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: %s\r\n\r\n' % (uUDP_IP, iUDP_PORT, self.uST))

            oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            oSocket.sendto(bMessage, (uUDP_IP, iUDP_PORT))
            return oSocket

        if self.uIPVersion == "IPv6Only":

            # socket.IPPROTO_IPV6 might not be defined
            IPPROTO_IPV6 = 41
            try:
                IPPROTO_IPV6=socket.IPPROTO_IPV6
            except:
                pass

            uUDP_IP = u'FF02::C'
            bMessage = ToBytes(u'M-SEARCH * HTTP/1.1\r\nHOST: [%s]:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: %s\r\n\r\n' % (uUDP_IP, iUDP_PORT, self.uST))

            oSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(IPPROTO_IPV6, socket.IP_MULTICAST_TTL, 2)
            oSocket.sendto(bMessage, (uUDP_IP, iUDP_PORT))
            return oSocket

        return None


    def GetDeviceDetails(self,uData:str,tSenderAddr:Tuple) -> TypedQueryDict:
        oNode:Element
        aData:List[str]
        uFoundServiceType:str
        uLine:str
        iStatusCode:int
        uUrl:str                 = u""

        oRet                     = TypedQueryDict()
        oRet.uFoundManufacturer  = u""
        oRet.uFoundModel         = u""
        oRet.uFoundFriendlyName  = u""
        oRet.uFoundServiceType   = u""
        oRet.uFoundIP            = tSenderAddr[0]
        oRet.uIPVersion          = self.uIPVersion[:4]
        oRet.bFound              = False
        oRet.sData               = uData
        oRet.uResult             = u""
        oRet.uFoundHostName      = u""

        oRet.sData = ToUnicode(oRet.sData)

        if oRet.uIPVersion=="IPv6":
            oRet.uFoundIP="[%s]" % oRet.uFoundIP

        # if we got a response
        if '200 OK' in oRet.sData:
            aData = oRet.sData.splitlines()
            uFoundServiceType = ""
            # The location field as part of DIAL specification and contains a link to an XML with further device infos
            for uLine in aData:
                if uLine.upper().startswith('LOCATION:'):
                    uUrl = uLine[9:].strip()
                if uLine.startswith('ST'):
                    oRet.uFoundServiceType = uLine[3:].strip()
                    uFoundServiceType = uFoundServiceType

            self.oCaller.ShowDebug(uMsg=u'Trying to get device details from  %s ->IPVersion: %s' % (uUrl,oRet.uIPVersion))

            try:
                self.oUrlRequest = UrlRequest(uUrl, method="GET", req_body='', req_headers={"Connection": "Keep-Alive", "Accept-Encoding": "gzip"}, timeout=self.fTimeOut, on_error=self.OnError)
                self.NewWait(0.05)
                iStatusCode = self.oUrlRequest.resp_status

                if iStatusCode == 200 and "device" in self.oUrlRequest.result:
                    oRet.uResult             = RemoveURN(self.oUrlRequest.result)
                    oNode                    = LoadXMLString(uXML=oRet.uResult)
                    oNode                    = oNode.find("device")
                    oRet.uFoundManufacturer  = oNode.find("manufacturer").text
                    oRet.uFoundModel         = oNode.find("modelName").text

                    try:
                        oRet.uFoundFriendlyName = oNode.find("friendlyName").text
                    except Exception:
                        pass
                    oRet.bFound              = True
                    self.oCaller.ShowDebug(uMsg=u'Found Device Manufacturer=%s Model=%s Friendlyname=%s IP=%s ST=%s' % (oRet.uFoundManufacturer, oRet.uFoundModel, oRet.uFoundFriendlyName, oRet.uFoundIP,oRet.uFoundServiceType))
            except Exception as e:
                self.oCaller.ShowError(uMsg="Can''t get device details. skipping device: "+uUrl,oException=e)

        return oRet

    def CheckDeviceDetails(self,dRet:TypedQueryDict) -> None:
        if dRet.bFound:
            if self.dReq.uManufacturer != "":
                if not MatchWildCard(uValue=dRet.uFoundManufacturer, uMatchWithWildCard=self.dReq.uManufacturer):
                    dRet.bFound = False

            aModels = ToList(self.dReq.uModels)
            if len(aModels) > 0 and dRet.bFound:
                dRet.bFound = False
                for uModel in aModels:
                    if uModel.startswith("'") or uModel.startswith('"'):
                        uModel=uModel[1:-2]
                    if MatchWildCard(uValue=dRet.uFoundModel,uMatchWithWildCard=uModel):
                        dRet.bFound = True
                        break

            if self.dReq.uFriendlyName != "" and dRet.bFound:
                dRet.bFound = False
                if MatchWildCard(uValue=dRet.uFoundFriendlyName,uMatchWithWildCard=self.dReq.uFriendlyName):
                    dRet.bFound = True

