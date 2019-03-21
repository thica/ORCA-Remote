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

import socket
import re
import select
import threading

from struct                                 import pack

from kivy.logger                            import Logger
from kivy.compat                            import PY2

from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.LogError                    import LogError
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToList
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.vars.QueryDict                    import QueryDict

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>EISCP Discover</name>
      <description language='English'>Discover EISCP/Onkyo devices</description>
      <description language='German'>Erkennt sucht EISCP/Onkyo Geräte über upnp</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_eiscp</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_eiscp.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/discover/discover_eiscp/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cScript(cDiscoverScriptTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-Discover-EISCP
    WikiDoc:TOCTitle:Discover EISCP
    = Script Discover EISCP =

    The EISCP discover script discover ONKYO devices which supports the EISCP protocol.
    You can filter the discover result by passing the following parameters::
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |models
    |Discover only specific Onkyo models
    |-
    |timeout
    |Specifies the timout for discover
    |}</div>

    Blank options will not be used.

    WikiDoc:End
    """
    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aScriptIniSettings.fTimeOut                     = 10.0

    def __init__(self):
        cDiscoverScriptTemplate.__init__(self)
        self.uSubType        = u'EISCP (Onkyo)'
        self.aResults        = []
        self.aThreads        = []
        self.oReq            = QueryDict()
        self.bOnlyOnce       = True
        self.uIPVersion      = "Auto"

    def Init(self,uScriptName,uScriptFile=u''):
        """
        Init function for the script

        :param string uScriptName: The name of the script (to be passed to all scripts)
        :param uScriptFile: The file of the script (to be passed to all scripts)
        """

        cDiscoverScriptTemplate.Init(self, uScriptName, uScriptFile)
        self.oScriptConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def GetHeaderLabels(self):
        return ['$lvar(5029)','$lvar(6002)','$lvar(5031)','$lvar(5032)']

    def ListDiscover(self):
        dArgs                   = {}
        dArgs["onlyonce"]       = 0
        dArgs["ipversion"]      = "All"
        aDevices                = {}

        self.Discover(**dArgs)

        for aDevice in self.aResults:
            uTageLine = aDevice.sFoundIP + aDevice.uFoundModel + aDevice.uFoundIdentifier
            if aDevices.get(uTageLine) is None:
               aDevices[uTageLine]=aDevice
               self.AddLine([aDevice.sFoundIP, aDevice.uFoundPort, aDevice.uFoundModel, aDevice.uFoundIdentifier], aDevice)
        return

    def CreateDiscoverList_ShowDetails(self,instance):
        uText=  u"$lvar(5029): %s \n"\
                u"$lvar(6002): %s \n"\
                u"$lvar(5031): %s \n"\
                u"$lvar(5032): %s \n"\
                u"\n"\
                u"%s" % (instance.oDevice.sFoundIP,instance.oDevice.uFoundPort,instance.oDevice.uFoundModel,instance.oDevice.uFoundIdentifier,instance.oDevice.sData)

        ShowMessagePopUp(uMessage=uText)


    def Discover(self,**kwargs):

        self.oReq.clear()
        uConfigName             = kwargs.get('configname',self.uConfigName)
        oSetting                = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut                = ToFloat(kwargs.get('timeout',oSetting.aScriptIniSettings.fTimeOut))
        self.oReq.uModels       = kwargs.get('models',"")
        bOnlyOnce               = ToBool(kwargs.get('onlyonce',"1"))
        uIPVersion              = kwargs.get('ipversion',"IPv4Only")

        Logger.debug (u'Try to discover Onkyo device by EISCP:  Models: %s ' % self.oReq.uModels)

        del self.aResults[:]
        del self.aThreads[:]

        try:
            oThread = None
            if uIPVersion == "IPv4Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 == ""):
                oThread = cThread_Discover_EISCP(bOnlyOnce=bOnlyOnce,oReq=self.oReq,uIPVersion="IPv4Only", fTimeOut=fTimeOut, oCaller=self)
                self.aThreads.append(oThread)
                self.aThreads[-1].start()
            if uIPVersion == "IPv6Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 != ""):
                oThread = cThread_Discover_EISCP(bOnlyOnce=bOnlyOnce, oReq=self.oReq, uIPVersion="IPv6Only", fTimeOut=fTimeOut, oCaller=self)
                self.aThreads.append(oThread)
                self.aThreads[-1].start()

            for oT in self.aThreads:
                oT.join()

            if len(self.aResults)>0:
                return {'Model': self.aResults[0].uFoundModel, 'Host': self.aResults[0].sFoundIP,'Port': self.aResults[0].uFoundPort, 'Category': self.aResults[0].uFoundCategory, 'Exception': None}
            else:
                Logger.warning(u'No device found Models: %s' % self.oReq.uModels)
            return  {'Model':'','Host':'','Port':'','Category':'','Exception':None}

        except Exception as e:
            Logger.debug (u'No EISCP device found, possible timeout')
            return {'Model':'','Host':'','Port':'','Category':'','Exception':e}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults):
        return {"TimeOut": {"type": "numericfloat","active":"enabled", "order":0,  "title": "$lvar(6019)", "desc": "$lvar(6020)","key": "timeout", "default":"2.0"},
                "Models":  {"type": "string",      "active":"enabled", "order":1,  "title": "$lvar(SCRIPT_DISC_EISCP_1)", "desc": "$lvar(SCRIPT_DISC_EISCP_2)","key": "models", "default":""},
                "IP Version": {"type": "scrolloptions", "order": 4, "title": "$lvar(6037)", "desc": "$lvar(6038)", "key": "ipversion", "default": "IPv4Only", "options": ["IPv4Only", "IPv6Only", "All", "Auto"]}
                }


class cThread_Discover_EISCP(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, bOnlyOnce,oReq,uIPVersion, fTimeOut,oCaller):
        threading.Thread.__init__(self)
        self.bOnlyOnce  = bOnlyOnce
        self.uIPVersion = uIPVersion
        self.oCaller    = oCaller
        self.fTimeOut   = fTimeOut
        self.oReq       = oReq
        self.iOnkyoPort = 60128
        self.rMatch           = r'''
                    !
                    (?P<device_category>\d)
                    ECN
                    (?P<model_name>[^/]*)/
                    (?P<iscp_port>\d{5})/
                    (?P<area_code>\w{2})/
                    (?P<identifier>.{0,12})
                    '''

        self.bOnkyoMagic= self.CreateEISPPacket('!xECNQSTN\r')

    def CreateEISPPacket(self, iscp_message):
        # Test for discover
        iscp_message = str(iscp_message)
        # We attach data separately, because Python's struct module does
        # not support variable length strings,
        return pack('! 4s I I b 3b', b'ISCP', 16, len(iscp_message), 0x01, 0x00, 0x00, 0x00) +ToBytes(iscp_message)

    def run(self):
        bReturnNow = False
        if self.bOnlyOnce:
            cThread_Discover_EISCP.oWaitLock.acquire()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            cThread_Discover_EISCP.oWaitLock.release()
        if bReturnNow:
            return
        self.Discover()

    def Discover(self):

        oSocket = None
        try:
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
                            Logger.info(u'Bingo: Discovered device %s:%s at %s:' % (oRet.uFoundIdentifier, oRet.uFoundModel, oRet.sFoundIP))
                            cThread_Discover_EISCP.oWaitLock.acquire()
                            self.oCaller.aResults.append(oRet)
                            cThread_Discover_EISCP.oWaitLock.release()
                            if self.bOnlyOnce:
                                oSocket.close()
                                return
                    else:
                        break
                oSocket.close()
            return

        except Exception as e:
            LogError(u'Error on discover EISCP (%s)' % (self.uIPVersion),e)
            if oSocket:
                oSocket.close()
            return

    def SendDiscover(self):
        if self.uIPVersion=="IPv4Only":
            oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)
            oSocket.sendto(self.bOnkyoMagic, ('239.255.255.250', self.iOnkyoPort))
            return oSocket

        if self.uIPVersion == "IPv6Only":
            #Not Tested
            # socket.IPPROTO_IPV6 might not be defined
            IPPROTO_IPV6 = 41
            try:
                IPPROTO_IPV6=socket.IPPROTO_IPV6
            except:
                pass


            oSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(IPPROTO_IPV6, socket.IP_MULTICAST_TTL, 20)
            oSocket.sendto(self.bOnkyoMagic, (u'ff02::c', self.iOnkyoPort))
            return oSocket

        return None

    def GetDeviceDetails(self,sData,tSenderAddr):
        oRet                     = QueryDict()
        oRet.bFound              = False
        oRet.sFoundIP            = ""
        oRet.uFoundPort          = ""
        oRet.uFoundModel         = ""
        oRet.uFoundIdentifier    = ""
        oRet.uFoundCategory      = ""
        oRet.sData               = ""

        if PY2:
            uResponse = sData[16:]
        else:
            uResponse = ToUnicode(sData)[16:]

        if uResponse.find('ECN') != -1:
            info = re.match(self.rMatch, uResponse.strip(), re.VERBOSE).groupdict()
            uResponse = uResponse[10:]
            oRet.sFoundIP            = tSenderAddr[0]
            oRet.uFoundPort          = ToUnicode(info['iscp_port'])
            oRet.uFoundModel         = info['model_name']
            oRet.uFoundIdentifier    = info['identifier']
            oRet.uFoundCategory      = ToUnicode(info['device_category'])
            oRet.sData               = uResponse
            oRet.bFound              = True
        return oRet

    def CheckDeviceDetails(self, oRet):
        if oRet.bFound:
            aModels = ToList(self.oReq.uModels)
            if len(aModels) > 0:
                oRet.bFound = False
                for uModel in aModels:
                    if uModel.endswith("*"):
                        if uModel[:-1] == oRet.uFoundModel[:len(uModel) - 1]:
                            oRet.bFound = True
                            break
                    else:
                        if uModel.startswith("'") or uModel.startswith('"'):
                            uModel = uModel[1:-1]
                        if uModel == oRet.uFoundModel:
                            oRet.bFound = True
                            break


