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

from time import sleep
import threading
import socket
from kivy.logger                            import Logger
from kivy.network.urlrequest                import UrlRequest
from kivy.compat                            import PY2
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


'''
<root>
  <repositorymanager>
    <entry>
      <name>Enigma Discover</name>
      <description language='English'>Discover Enigma Receiver via the webinterface</description>
      <description language='German'>Erkennt Enigma Reveiver mittels des Web Interfaces</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_enigma</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_enigame.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/discover_enigma/script.pyc</file>
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
        def __init__(self,oScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aIniSettings.fTimeOut                     = 1.0

    def __init__(self):
        cDiscoverScriptTemplate.__init__(self)
        self.uSubType        = u'Enigma'
        self.iPort           = 80
        self.bStopWait       = False
        self.aResults        = []
        self.aThreads        = []

    def Init(self,uObjectName,uScriptFile=u''):
        """
        Init function for the script

        :param string uObjectName: The name of the script (to be passed to all scripts)
        :param uScriptFile: The file of the script (to be passed to all scripts)
        """
        cDiscoverScriptTemplate.Init(self, uObjectName, uScriptFile)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def GetHeaderLabels(self):
        return ['$lvar(5029)','$lvar(5035)','$lvar(6002)','$lvar(5031)']

    def ListDiscover(self):
        oSetting                = self.GetSettingObjectForConfigName(uConfigName=self.uConfigName)
        dArgs                   = {"onlyonce": 0}

        self.Discover(**dArgs)

        try:

            for dResult in self.aResults:
                aDevice                 = QueryDict()
                aDevice.sFoundIP        = dResult["ip"]
                aDevice.uFoundPort      = str(dResult["port"])
                aDevice.uFoundModel     = dResult["model"]
                aDevice.uFoundHostName  = dResult["hostname"]
                Logger.info(u'Bingo: Discovered device %s:%s' % (aDevice.uFoundModel, aDevice.sFoundIP))
                uTageLine = aDevice.sFoundIP + aDevice.uFoundModel
                if self.aDevices.get(uTageLine) is None:
                    self.aDevices[uTageLine] = aDevice
                    self.AddLine([aDevice.sFoundIP, aDevice.uFoundHostName, aDevice.uFoundPort, aDevice.uFoundModel], aDevice)
        except Exception as e:
            LogErrorSmall(u'Error on Enigma discover',e)

    def CreateDiscoverList_ShowDetails(self,instance):
        uText=  u"$lvar(5029): %s \n" \
                u"$lvar(5035): %s \n" \
                u"$lvar(6002): %s \n"\
                u"$lvar(5031): %s \n" % (instance.oDevice.sFoundIP,instance.oDevice.uFoundHostName,instance.oDevice.uFoundPort,instance.oDevice.uFoundModel)

        ShowMessagePopUp(uMessage=uText)

    def Discover(self,**kwargs):

        uConfigName             = kwargs.get('configname',self.uConfigName)
        oSetting                = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut                = ToFloat(kwargs.get('timeout',oSetting.aIniSettings.fTimeOut))
        bOnlyOnce               = ToBool(kwargs.get('onlyonce', "1"))

        del self.aResults[:]
        del self.aThreads[:]

        uIPSubNet = Globals.uIPGateWayAssumedV4
        uIPSubNet = uIPSubNet[:uIPSubNet.rfind(".")]+"."

        for i in range(154,155):
            uIP = uIPSubNet+str(i)
            oThread = cThread_CheckIP(uIP=uIP,bOnlyOnce=bOnlyOnce,fTimeOut=fTimeOut, oCaller=self)
            self.aThreads.append(oThread)
            oThread.start()

        for oT in self.aThreads:
            oT.join()

        if len(self.aResults):
            uHost      = self.aResults[0]["ip"]
            uPort      = self.aResults[0]["port"]
            uModel     = self.aResults[0]["model"]
            uHostName  = self.aResults[0]["hostname"]
            uIPVersion = self.aResults[0]["ipversion"]
            return {'Host':uHost,'Port':uPort,'Model':uModel,'Hostname':uHostName,"IPVersion":uIPVersion ,'Exception':None}

        LogErrorSmall("Enigma-Discover: Could not find a Enigma Receiver on the network")
        return {'Host':'','Port':'','Model':'','Hostname':'',"IPVersion":'' ,'Exception':None}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults):
        return {"TimeOut":{"type": "numericfloat", "order":0, "title": "$lvar(6019)", "desc": "$lvar(6020)","key": "timeout", "default":"1.0"}}


class cThread_CheckIP(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, uIP, bOnlyOnce,fTimeOut,oCaller):
        threading.Thread.__init__(self)
        self.uIP        = uIP
        self.bOnlyOnce  = bOnlyOnce
        self.oCaller    = oCaller
        self.fTimeOut   = fTimeOut
        self.bStopWait  = False
        self.oReq       = None

    def run(self):

        bReturnNow = False
        if self.bOnlyOnce:
            cThread_CheckIP.oWaitLock.acquire()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            cThread_CheckIP.oWaitLock.release()
        if bReturnNow:
            return
        self.SendCommand()

    def SendCommand(self):
        self.bStopWait      = False
        uUrlFull= "http://"+self.uIP+"/web/about"
        try:
            self.oReq = UrlRequest(uUrlFull,method="GET",timeout=self.fTimeOut,on_error=self.OnError,on_success=self.OnReceive)
            self.NewWait(0.05)
            if self.oReq.resp_status is not None:
                uResult = self.oReq.result
                if "<e2abouts>" in uResult:
                    if PY2:
                        oXmlRoot = fromstring(uResult.encode('ascii', 'xmlcharrefreplace'))
                    else:
                        oXmlRoot = fromstring(uResult)
                    oXmlAbout = oXmlRoot.find("e2about")
                    uModel = GetXMLTextValue(oXmlAbout, "e2model", False, "Enigma")
                    uFoundHostName = ""
                    try:
                        uFoundHostName = socket.gethostbyaddr(self.uIP)[0]
                    except Exception as e:
                        # Logger.error("Cant get Hostname:"+oRet.sFoundIP+" "+str(e))
                        pass

                    cThread_CheckIP.oWaitLock.acquire()
                    self.oCaller.aResults.append({"ip":self.uIP,"port":80,"model":uModel,"ipversion":"IPv4","hostname":uFoundHostName})
                    try:
                        uIP = ""
                        aIPs = socket.getaddrinfo(uFoundHostName,None)
                        for tIP in aIPs:
                            uIP =  "["+tIP[-1][0]+"]"
                            if ":" in uIP:
                                break
                        if ":" in uIP:
                            self.oCaller.aResults.append({"ip": uIP, "port": 80, "model": uModel, "ipversion": "IPv6","hostname":uFoundHostName})
                    except Exception as e:
                        pass


                    cThread_CheckIP.oWaitLock.release()
        except Exception as e:
            self.oCaller.ShowError("Error on send:",e)
        return

    def NewWait(self,delay):
        while self.oReq.resp_status is None:
            self.oReq._dispatch_result(delay)
            sleep(delay)
            if self.bStopWait:
                self.bStopWait=False
                break

    def OnError(self,request,error):
        self.bStopWait      = True

    def OnFailure(self,request,result):
        self.bStopWait      = True

    def OnReceive(self,oRequest,oResult):
        self.bStopWait      = True


