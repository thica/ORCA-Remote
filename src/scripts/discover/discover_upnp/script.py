# -*- coding: utf-8 -*-
#

"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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
from typing import Callable

import threading

from time                                   import sleep
from xml.etree.ElementTree                  import Element

from kivy.network.urlrequest                import UrlRequest
from kivy.uix.button                        import Button

from ORCA.scripttemplates.Template_Discover_Broadcast import cDiscoverScriptTemplate_Broadcast
from ORCA.scripttemplates.Template_Discover_Broadcast import cThread_DiscoverTemplate_Broadcast

from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.utils.TypeConvert                 import ToList
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.XML                         import LoadXMLString
from ORCA.utils.Wildcard                    import MatchWildCard
from ORCA.vars.QueryDict                    import TypedQueryDict


from ORCA.Globals import Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>UPNP Discover</name>
      <description language='English'>Discover devices by upnp</description>
      <description language='German'>Erkennt bwz. sucht Geraete ueber upnp</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
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

class cScript(cDiscoverScriptTemplate_Broadcast):
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

    def __init__(self):
        super().__init__()
        self.uSubType:str                       = 'UPNP'
        self.uScriptTitle                       = 'SSDP/uPNP Discovery'

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(5035)','$lvar(5030)','$lvar(5031)','$lvar(5032)','$lvar(SCRIPT_DISC_UPNP_1)']


    def CreateArgs(self) -> Dict:

        return {'onlyonce':      0,
                'ipversion':     'All',
                'donotwait':       1,
                'ipv4':'239.255.255.250',
                'portv4':1900,
                'servicetypes': 'ssdp:all'
                }

    def GetRequests(self,dArgs:Dict)-> TypedQueryDict:
        """ This is could be overridden """
        dReq:TypedQueryDict = super().GetRequests(dArgs=dArgs)
        dReq.uModels        = dArgs.get('models', '')
        dReq.uManufacturer  = dArgs.get('manufacturer','')
        dReq.uFriendlyName  = dArgs.get('prettyname','')
        dReq.bReturnPort    = ToBool(dArgs.get('returnport','0'))
        return dReq

    def GetServiceTypes(self,dArgs:Dict)->List:
        """ This is a dummy function if not service types are required, than leave it as it is"""
        uParST:str           = dArgs.get('servicetypes','ssdp:all')
        return  uParST.split(',')

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:TypedQueryDict = oButton.dDevice

        uText:str=  '$lvar(5029): %s \n' \
                    '$lvar(5035): %s \n' \
                    '$lvar(5030): %s \n' \
                    '$lvar(5031): %s \n' \
                    '$lvar(5032): %s \n' \
                    '$lvar(SCRIPT_DISC_UPNP_1): %s \n '\
                    '\n'   \
                    '%s\n' \
                    '\n'   \
                    '%s' % (dDevice.uFoundIP,dDevice.uFoundHostName,dDevice.uFoundManufacturer,dDevice.uFoundModel,dDevice.uFoundFriendlyName,dDevice.uFoundServiceType,dDevice.sData,dDevice.uResult)

        ShowMessagePopUp(uMessage=uText)

    def ShowNotFoundMessage(self) -> None:
        """ needs to be overwritten """
        self.ShowWarning(uMsg='No device found device %s:%s:%s' % (self.dReq.uManufacturer, self.dReq.uModels, self.dReq.uFriendlyName))

    def ShowStartMessage(self) -> None:
        """ needs to be overwritten """
        self.ShowDebug (uMsg='Try to discover %s device by UPNP:  Models: %s , PrettyName: %s ' % (self.dReq.uManufacturer,self.dReq.uModels, self.dReq.uFriendlyName ))

    def CreateResult(self,bEmpty:bool=False,oException:Exception=None) -> Dict:

        if not bEmpty:
            return {'Host': self.aResults[0].uFoundIP,
                    'Hostname': self.aResults[0].uFoundHostName,
                    'Model': self.aResults[0].uFoundModel,
                    'FriendlyName': self.aResults[0].uFoundFriendlyName,
                    'Manufacturer': self.aResults[0].uFoundManufacturer,
                    'ServiceType': self.aResults[0].uFoundServiceType,
                    'IPVersion': self.aResults[0].uIPVersion,
                    'Exception': None}

        else:
            return {'Host': '',
                    'Hostname': '',
                    'Model': '',
                    'FriendlyName': '',
                    'Manufacturer': '',
                    'ServiceType': '',
                    'IPVersion': '',
                    'Exception': None}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return  {'Manufacturer':    {'type': 'string',       'order':0,  'title': '$lvar(6013)', 'desc': '$lvar(6014)', 'key': 'manufacturer',    'default':''           },
                 'Models':          {'type': 'string',       'order':1,  'title': '$lvar(6015)', 'desc': '$lvar(6016)', 'key': 'models',          'default':''           },
                 'PrettyName':      {'type': 'string',       'order':2,  'title': '$lvar(6017)', 'desc': '$lvar(6018)', 'key': 'prettyname',      'default':''           },
                 'ServiceTypes':    {'type': 'string',       'order':3,  'title': '$lvar(6023)', 'desc': '$lvar(6024)', 'key': 'servicetypes',    'default':'urn:dial-multiscreen-org:service:dial:1,urn:schemas-upnp-org:service:AVTransport:1'},
                 'IP Version':      {'type': 'scrolloptions','order':4,  'title': '$lvar(6037)', 'desc': '$lvar(6038)', 'key': 'ipversion',       'default':'IPv4Only', 'options':['IPv4Only','IPv6Only','All','Auto']},
                 'TimeOut':         {'type': 'numericfloat', 'order':6,  'title': '$lvar(6019)', 'desc': '$lvar(6020)', 'key': 'timeout',         'default':'15.0'}
                }

    # noinspection PyMethodMayBeStatic
    def GetThreadClass(self) -> Callable:
        return cThread_Discover_UPNP

        #'ReturnPort':      {'type': 'bool', 'order': 4, 'title': '$lvar(SCRIPT_DISC_UPNP_2)', 'desc': '$lvar(SCRIPT_DISC_UPNP_3)', 'key': 'returnport', 'default': '1'},


class cThread_Discover_UPNP(cThread_DiscoverTemplate_Broadcast):
    oWaitLock = threading.Lock()

    def __init__(self, bOnlyOnce:bool,dReq:TypedQueryDict,uIPVersion:str, uST:str,fTimeOut:float,oCaller:cDiscoverScriptTemplate_Broadcast):
        super(cThread_Discover_UPNP, self).__init__(bOnlyOnce,dReq,uIPVersion, uST,fTimeOut,oCaller)
        self.oUrlRequest:Union[None,UrlRequest] = None

    def ShowFoundMessage(self,dRet:TypedQueryDict):
        """ needs to be overwritten """
        self.oCaller.ShowInfo(uMsg='Discovered device %s:%s:%s at %s:' % (dRet.uFoundManufacturer, dRet.uFoundModel, dRet.uFoundFriendlyName, dRet.uFoundIP))

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
        # self.oCaller.ShowError(uMsg='UPNP - Discover:Error Receiving Response',oException=error)
        self.bStopWait      = True

    def CreatePayloadV4(self) -> bytes:
        """ needs to be overwritten """
        return ToBytes('M-SEARCH * HTTP/1.1\r\nHOST: %s:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: %s\r\n\r\n' % (self.uBroadcastIPV4, self.iPortV4, self.uST))

    def CreatePayloadV6(self) -> bytes:
        """ needs to be overwritten """
        return ToBytes('M-SEARCH * HTTP/1.1\r\nHOST: [%s]:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: %s\r\n\r\n' % (self.uBroadcastIPV6, self.iPortV6, self.uST))


    def SendFoundNotification(self,dRet:TypedQueryDict):
        Globals.oNotifications.SendNotification(uNotification='DISCOVER_SCRIPTFOUND',
                                                **{"script": self, "scriptname": self.oCaller.uObjectName, "line": [dRet.uFoundIP, dRet.uFoundHostName, dRet.uFoundManufacturer, dRet.uFoundModel, dRet.uFoundFriendlyName, dRet.uFoundServiceType],
                                                   "device": dRet})

    def CreateTagLine(self,dRet:TypedQueryDict) -> str:
        return dRet.uFoundIP + dRet.uFoundModel + dRet.uFoundServiceType


    def GetDeviceDetails(self,byData:bytes,tSenderAddr:Tuple) -> TypedQueryDict:
        dRet: TypedQueryDict = super().GetDeviceDetails(byData, tSenderAddr)
        oNode:Element
        aData:List[str]
        uFoundServiceType:str
        uLine:str
        iStatusCode:int
        uUrl:str                 = ''
        uData:str                = ToUnicode(byData)

        dRet.uFoundManufacturer  = ''
        dRet.uFoundModel         = ''
        dRet.uFoundFriendlyName  = ''
        dRet.uFoundServiceType   = ''
        dRet.bFound              = False
        dRet.sData               = uData
        dRet.uResult             = ''
        dRet.uFoundHostName      = ''

        if dRet.uIPVersion=='IPv6':
            dRet.uFoundIP= f'[{dRet.uFoundIP}]'

        # if we got a response
        if '200 OK' in dRet.sData:
            aData = dRet.sData.splitlines()
            uFoundServiceType = ''
            # The location field as part of DIAL specification and contains a link to an XML with further device infos
            for uLine in aData:
                if uLine.upper().startswith('LOCATION:'):
                    uUrl = uLine[9:].strip()
                if uLine.startswith('ST'):
                    dRet.uFoundServiceType = uLine[3:].strip()
                    uFoundServiceType = uFoundServiceType

            self.oCaller.ShowDebug(uMsg='Trying to get device details from  %s ->IPVersion: %s' % (uUrl,dRet.uIPVersion))

            try:
                self.oUrlRequest = UrlRequest(uUrl, method='GET', req_body='', req_headers={'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'}, timeout=self.fTimeOut, on_error=self.OnError)
                self.NewWait(0.05)
                iStatusCode = self.oUrlRequest.resp_status

                if iStatusCode == 200 and "device" in self.oUrlRequest.result:
                    dRet.uResult             = RemoveURN(self.oUrlRequest.result)
                    oNode                    = LoadXMLString(uXML=dRet.uResult)
                    oNode                    = oNode.find('device')
                    dRet.uFoundManufacturer  = oNode.find('manufacturer').text
                    dRet.uFoundModel         = oNode.find('modelName').text

                    try:
                        dRet.uFoundFriendlyName = oNode.find('friendlyName').text
                    except Exception:
                        pass
                    dRet.bFound              = True
                    self.oCaller.ShowDebug(uMsg='Found Device Manufacturer=%s Model=%s Friendlyname=%s IP=%s ST=%s' % (dRet.uFoundManufacturer, dRet.uFoundModel, dRet.uFoundFriendlyName, dRet.uFoundIP,dRet.uFoundServiceType))
            except Exception as e:
                self.oCaller.ShowError(uMsg='Can\'t get device details. skipping device: '+uUrl,oException=e)

        return dRet

    def CheckDeviceDetails(self,dRet:TypedQueryDict) -> None:

        if dRet.bFound:
            if self.dReq.uManufacturer != '':
                if not MatchWildCard(uValue=dRet.uFoundManufacturer, uMatchWithWildCard=self.dReq.uManufacturer):
                    dRet.bFound = False
                    return

            aModels = ToList(self.dReq.uModels)
            if len(aModels) > 0 and dRet.bFound:
                dRet.bFound = False
                for uModel in aModels:
                    if uModel.startswith("'") or uModel.startswith('"'):
                        uModel=uModel[1:-2]
                    if MatchWildCard(uValue=dRet.uFoundModel,uMatchWithWildCard=uModel):
                        dRet.bFound = True
                        break

            if self.dReq.uFriendlyName != '' and dRet.bFound:
                dRet.bFound = False
                if MatchWildCard(uValue=dRet.uFoundFriendlyName,uMatchWithWildCard=self.dReq.uFriendlyName):
                    dRet.bFound = True

