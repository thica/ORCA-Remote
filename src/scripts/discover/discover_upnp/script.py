# -*- coding: utf-8 -*-
#

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

import select
import socket
import threading

from time                                   import sleep
from xml.etree.ElementTree                  import ElementTree, fromstring

from kivy.logger                            import Logger
from kivy.network.urlrequest                import UrlRequest

from ORCA.Compat                            import PY2
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.LogError                    import LogError
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToList
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.utils.PyXSocket                   import cPyXSocket

from ORCA.vars.QueryDict                    import QueryDict

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>UPNP Discover</name>
      <description language='English'>Discover devices by upnp</description>
      <description language='German'>Erkennt bwz. sucht Geraete ueber upnp</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_upnp</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_upnp.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/discover/discover_upnp/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

def RemoveURN(uData):

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
        def __init__(self,oScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aIniSettings.fTimeOut                     = 15.0

    def __init__(self):
        cDiscoverScriptTemplate.__init__(self)
        self.uSubType        = u'UPNP'
        self.bStopWait       = False
        self.aResults        = []
        self.aThreads        = []
        self.oReq            = QueryDict()

    def Init(self,uObjectName,uScriptFile=u''):
        cDiscoverScriptTemplate.Init(self, uObjectName, uScriptFile)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def GetHeaderLabels(self):
        return ['$lvar(5029)','$lvar(5035)','$lvar(5030)','$lvar(5031)','$lvar(5032)','$lvar(SCRIPT_DISC_UPNP_1)']

    def ListDiscover(self):

        dArgs                   = {"onlyonce":      0,
                                   "servicetypes":  "ssdp:all",
                                   "ipversion":     "All"}
        aDevices                = {}

        self.Discover(**dArgs)

        for aDevice in self.aResults:
            uTageLine=aDevice.sFoundIP+aDevice.uFoundHostName+aDevice.uFoundManufacturer+aDevice.uFoundModel+aDevice.uFoundFriendlyName+aDevice.uFoundServiceType
            if aDevices.get(uTageLine) is None:
               aDevices[uTageLine]=aDevice
               self.AddLine([aDevice.sFoundIP,aDevice.uFoundHostName,aDevice.uFoundManufacturer,aDevice.uFoundModel,aDevice.uFoundFriendlyName,aDevice.uFoundServiceType],aDevice)
        return

    def CreateDiscoverList_ShowDetails(self,instance):
        uText=  u"$lvar(5029): %s \n" \
                u"$lvar(5035): %s \n" \
                u"$lvar(5030): %s \n"\
                u"$lvar(5031): %s \n"\
                u"$lvar(5032): %s \n"\
                u"$lvar(SCRIPT_DISC_UPNP_1): %s \n"\
                u"\n"\
                u"%s\n"\
                u"\n"\
                u"%s" % (instance.oDevice.sFoundIP,instance.oDevice.uFoundHostName,instance.oDevice.uFoundManufacturer,instance.oDevice.uFoundModel,instance.oDevice.uFoundFriendlyName,instance.oDevice.uFoundServiceType,instance.oDevice.sData,instance.oDevice.uResult)

        ShowMessagePopUp(uMessage=uText)


    def Discover(self,**kwargs):

        self.oReq.clear()
        uConfigName              = kwargs.get('configname',self.uConfigName)
        oSetting                 = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        self.oReq.uManufacturer  = kwargs.get('manufacturer',"")
        self.oReq.uModels        = kwargs.get('models',"")
        self.oReq.uFriendlyName  = kwargs.get('prettyname',"")
        self.oReq.bReturnPort    = ToBool(kwargs.get('returnport',"0"))
        fTimeOut                 = ToFloat(kwargs.get('timeout',oSetting.aIniSettings.fTimeOut))
        uParST                   = kwargs.get('servicetypes',"ssdp:all")
        uIPVersion               = kwargs.get('ipversion',"IPv4Only")
        aST                      = uParST.split(',')
        bOnlyOnce                = ToBool(kwargs.get('onlyonce',"1"))

        Logger.debug (u'Try to discover %s device by UPNP:  Models: %s , PrettyName: %s ' % (self.oReq.uManufacturer,self.oReq.uModels, self.oReq.uFriendlyName ))

        del self.aResults[:]
        del self.aThreads[:]

        try:
            for uST in aST:
                oThread = None
                if uIPVersion == "IPv4Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 == ""):
                    oThread = cThread_Discover_UPNP(bOnlyOnce=bOnlyOnce,oReq=self.oReq,uIPVersion="IPv4Only", fTimeOut=fTimeOut, uST=uST,oCaller=self)
                    self.aThreads.append(oThread)
                    self.aThreads[-1].start()
                if uIPVersion == "IPv6Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 != ""):
                    oThread = cThread_Discover_UPNP(bOnlyOnce=bOnlyOnce, oReq=self.oReq, uIPVersion="IPv6Only", fTimeOut=fTimeOut, uST=uST,oCaller=self)
                    self.aThreads.append(oThread)
                    self.aThreads[-1].start()

            for oT in self.aThreads:
                oT.join()

            if len(self.aResults)>0:
                return {"Host":self.aResults[0].sFoundIP,
                        "Hostname": self.aResults[0].uFoundHostName,
                        "Model":self.aResults[0].uFoundModel,
                        "FriendlyName":self.aResults[0].uFoundFriendlyName,
                        "Manufacturer":self.aResults[0].uFoundManufacturer,
                        "ServiceType":self.aResults[0].uFoundServiceType,
                        "IPVersion":self.aResults[0].uIPVersion,
                        'Exception': None}
            else:
                Logger.warning(u'No device found device %s:%s:%s' %(self.oReq.uManufacturer,self.oReq.uModels,self.oReq.uFriendlyName))
            return {"Host": "",
                    "Hostname": "",
                    "Model": "",
                    "FriendlyName": "",
                    "Manufacturer": "",
                    "ServiceType": "",
                    "IPVersion": "",
                    'Exception': None}

        except Exception as e:
            LogError(u'Error on discover uPnP',e)
            return {"Host": "",
                    "Hostname": "",
                    "Model": "",
                    "FriendlyName": "",
                    "Manufacturer": "",
                    "ServiceType": "",
                    "IPVersion": "",
                    'Exception': e}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults):
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

    def __init__(self, bOnlyOnce,oReq,uIPVersion, uST,fTimeOut,oCaller):
        threading.Thread.__init__(self)

        self.bOnlyOnce  = bOnlyOnce
        self.uIPVersion = uIPVersion
        self.oCaller    = oCaller
        self.fTimeOut   = fTimeOut
        self.uST        = uST
        self.bStopWait  = False
        self.oReq       = oReq

    def run(self):

        bReturnNow = False
        if self.bOnlyOnce:
            cThread_Discover_UPNP.oWaitLock.acquire()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            cThread_Discover_UPNP.oWaitLock.release()
        if bReturnNow:
            return
        self.Discover()

    def Discover(self):

        oSocket = None
        try:
            self.bStopWait      = False

            oSocket = self.SendDiscover()
            if oSocket:
                # Parse all results
                while True:
                    #we do not wait too long
                    ready = select.select([oSocket], [], [],self.fTimeOut)
                    if ready[0]:
                        # Get a response
                        sData, tSenderAddr = oSocket.recvfrom(1024)
                        oRet = self.GetDeviceDetails(sData=sData,tSenderAddr=tSenderAddr)
                        self.CheckDeviceDetails(oRet=oRet)
                        if oRet.bFound:
                            Logger.info(u'Bingo: Discovered device %s:%s:%s at %s:' %(oRet.uFoundManufacturer,oRet.uFoundModel,oRet.uFoundFriendlyName,oRet.sFoundIP))
                            try:
                                if oRet.uIPVersion == "IPv4":
                                    oRet.uFoundHostName = socket.gethostbyaddr(oRet.sFoundIP)[0]
                                elif oRet.uIPVersion == "IPv6":
                                    #todo: Does not work for unknown reasons
                                    oRet.uFoundHostName = socket.gethostbyaddr(oRet.sFoundIP)[0]
                            except Exception as e:
                                # Logger.error("Cant get Hostname:"+oRet.sFoundIP+" "+str(e))
                                pass
                            cThread_Discover_UPNP.oWaitLock.acquire()
                            self.oCaller.aResults.append(oRet)
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
            LogError(u'Error on discover uPnP (%s)' % self.uIPVersion, e)
            if oSocket:
                oSocket.close()
            return

    def NewWait(self,delay):
        while self.oUrlRequest.resp_status is None:
            self.oUrlRequest._dispatch_result(delay)
            sleep(delay)
            if self.bStopWait:
                self.bStopWait=False
                break

    def OnError(self,request,error):
        LogError(u'Discover:Error Receiving Response',error)
        self.bStopWait      = True


    def SendDiscover(self):

        if self.uIPVersion=="IPv4Only":
            uUDP_IP     = u'239.255.255.250'
            iUDP_PORT   = 1900
            uMessage = u'M-SEARCH * HTTP/1.1\r\nHOST: %s:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: %s\r\n\r\n' % (uUDP_IP, iUDP_PORT, self.uST)

            oSocket = cPyXSocket(socket.AF_INET, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            oSocket.SendTo(uMessage, (uUDP_IP, iUDP_PORT))
            return oSocket

        if self.uIPVersion == "IPv6Only":

            # socket.IPPROTO_IPV6 might not be defined
            IPPROTO_IPV6 = 41
            try:
                IPPROTO_IPV6=socket.IPPROTO_IPV6
            except:
                pass

            uUDP_IP = u'FF02::C'
            iUDP_PORT = 1900
            uMessage = u'M-SEARCH * HTTP/1.1\r\nHOST: [%s]:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: %s\r\n\r\n' % (uUDP_IP, iUDP_PORT, self.uST)

            oSocket = cPyXSocket(socket.AF_INET6, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(IPPROTO_IPV6, socket.IP_MULTICAST_TTL, 2)
            oSocket.SendTo(uMessage, (uUDP_IP, iUDP_PORT))
            return oSocket

        return None


    def GetDeviceDetails(self,sData,tSenderAddr):
        oRet                     = QueryDict()
        oRet.uFoundManufacturer  = u""
        oRet.uFoundModel         = u""
        oRet.uFoundFriendlyName  = u""
        oRet.uFoundServiceType   = u""
        oRet.sFoundIP            = tSenderAddr[0]
        oRet.uIPVersion          = self.uIPVersion[:4]
        oRet.bFound              = False
        oRet.sData               = sData
        oRet.uResult             = u""
        oRet.uFoundHostName      = u""
        uUrl                     = u""

        if not PY2:
            oRet.sData = ToUnicode(oRet.sData)

        if oRet.uIPVersion=="IPv6":
            oRet.sFoundIP="[%s}" % oRet.sFoundIP

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

            Logger.debug(u'Trying to get device details from  %s' % uUrl)

            try:

                self.oUrlRequest = UrlRequest(uUrl, method="GET", req_body='', req_headers={"Connection": "Keep-Alive", "Accept-Encoding": "gzip"}, timeout=self.fTimeOut, on_error=self.OnError)
                self.NewWait(0.05)
                iStatusCode = self.oUrlRequest.resp_status

                if iStatusCode == 200 and "device" in self.oUrlRequest.result:
                    oRet.uResult             = RemoveURN(self.oUrlRequest.result)
                    oNode                    = ElementTree(fromstring(oRet.uResult))
                    oNode                    = oNode.find("device")
                    oRet.uFoundManufacturer  = oNode.find("manufacturer").text
                    oRet.uFoundModel         = oNode.find("modelName").text

                    try:
                        oRet.uFoundFriendlyName = oNode.find("friendlyName").text
                    except Exception as e:
                        pass
                    oRet.bFound              = True
                    Logger.debug(u'Found Device %s:%s:%s (%s)' % (oRet.uFoundManufacturer, oRet.uFoundModel, oRet.uFoundFriendlyName, oRet.sFoundIP))
            except Exception as e:
                LogError("Can''t get device details. skipping device: "+uUrl,e)

        return oRet

    def CheckDeviceDetails(self,oRet):
        if oRet.bFound:
            if self.oReq.uManufacturer != "":
                if self.oReq.uManufacturer != oRet.uFoundManufacturer:
                    oRet.bFound = False

            aModels = ToList(self.oReq.uModels)
            if len(aModels) > 0 and oRet.bFound:
                oRet.bFound = False
                for uModel in aModels:
                    if uModel.startswith("'") or uModel.startswith('"'):
                        uModel=uModel[1:-2]

                    if uModel.endswith("*"):
                        if uModel[:-1] == oRet.uFoundModel[:len(uModel) - 1]:
                            oRet.bFound = True
                            break
                    else:
                        if uModel.startswith("'") or uModel.startswith('"'):
                            uModel=uModel[1:-1]
                        if uModel == oRet.uFoundModel:
                            oRet.bFound = True
                            break

            if self.oReq.uFriendlyName != "" and oRet.bFound:
                oRet.bFound = False
                if self.oReq.uFriendlyName.endswith("*"):
                    if self.oReq.uFriendlyName[:-1] == oRet.uFoundFriendlyName[:len(oRet.uFriendlyName) - 1]:
                        oRet.bFound = True
                else:
                    if self.oReq.uFriendlyName == oRet.uFoundFriendlyName:
                        oRet.bFound = True

