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

from kivy.logger                            import Logger
from kivy.compat                            import PY2

from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.LogError                    import LogError
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.vars.QueryDict                    import QueryDict

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Keene Kira Discover</name>
      <description language='English'>Discover Keene Kira devices</description>
      <description language='German'>Erkennt sucht Keene Kira Geräte</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_kira</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_kira.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/discover/discover_kira/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


class cScript(cDiscoverScriptTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-Discover-Kira
    WikiDoc:TOCTitle:Discover Kira
    = Script Discover Keene Kira =

    The Kira discover script discover Keene Kira Infrared transmitter devices.
    You can filter the discover result by passing the following parameters::
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |timeout
    |Specifies the timout for discover
    |}</div>

    WikiDoc:End
    """
    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aScriptIniSettings.fTimeOut                     = 10.0

    def __init__(self):
        cDiscoverScriptTemplate.__init__(self)
        self.uSubType        = u'Keene Kira'
        self.aResults        = []
        self.aThreads        = []
        self.oReq            = QueryDict()

    def Init(self,uScriptName,uScriptFile=u''):
        """
        Init function for the script

        :param string uScriptName: The name of the script (to be passed to all scripts)
        :param uScriptFile: The file of the script (to be passed to all scripts)
        """
        cDiscoverScriptTemplate.Init(self, uScriptName, uScriptFile)
        self.oScriptConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def GetHeaderLabels(self):
        return ['$lvar(5029)','$lvar(5035)','$lvar(6002)']

    def ListDiscover(self):

        dArgs                   = {}
        dArgs["onlyonce"]       = 0
        dArgs["ipversion"]      = "IPv4Only"
        aDevices                = {}

        self.Discover(**dArgs)

        for aDevice in self.aResults:
            uTageLine=aDevice.sFoundIP+aDevice.uFoundHostName+aDevice.uFoundPort
            if aDevices.get(uTageLine) is None:
               aDevices[uTageLine]=aDevice
               self.AddLine([aDevice.sFoundIP,aDevice.uFoundHostName,aDevice.uFoundPort],aDevice)
        return

    def CreateDiscoverList_ShowDetails(self,instance):

        uText=  u"$lvar(5029): %s \n" \
                u"$lvar(6002): %s \n" \
                u"$lvar(5035): %s \n"\
                u"\n"\
                u"%s" % (instance.oDevice.sFoundIP,instance.oDevice.uFoundPort,instance.oDevice.uFoundHostName,instance.oDevice.sData)

        ShowMessagePopUp(uMessage=uText)


    def Discover(self,**kwargs):

        self.oReq.clear()
        uConfigName              = kwargs.get('configname',self.uConfigName)
        oSetting                 = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        self.oReq.bReturnPort    = ToBool(kwargs.get('returnport',"0"))
        fTimeOut                 = ToFloat(kwargs.get('timeout',oSetting.aScriptIniSettings.fTimeOut))
        uIPVersion               = kwargs.get('ipversion',"IPv4Only")
        bOnlyOnce                = ToBool(kwargs.get('onlyonce',"1"))

        Logger.debug (u'Try to discover device by Kira Discovery (%s)' % uIPVersion)

        del self.aResults[:]
        del self.aThreads[:]

        try:
            oThread = None
            if uIPVersion == "IPv4Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 == ""):
                oThread = cThread_Discover_Kira(bOnlyOnce=bOnlyOnce,oReq=self.oReq,uIPVersion="IPv4Only", fTimeOut=fTimeOut, oCaller=self)
                self.aThreads.append(oThread)
                self.aThreads[-1].start()
            if uIPVersion == "IPv6Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 != ""):
                oThread = cThread_Discover_Kira(bOnlyOnce=bOnlyOnce, oReq=self.oReq, uIPVersion="IPv6Only", fTimeOut=fTimeOut, oCaller=self)
                self.aThreads.append(oThread)
                self.aThreads[-1].start()

            for oT in self.aThreads:
                oT.join()

            if len(self.aResults)>0:
                return {"Host":self.aResults[0].sFoundIP,
                        "Hostname": self.aResults[0].uFoundHostName,
                        'Exception': None}
            else:
                Logger.warning(u'Kira Discover: No device found' )
            return {"Host": "",
                    "Hostname": "",
                    'Exception': None}

        except Exception as e:
            LogError(u'Error on discover uPnP',e)
            return {"Host": "",
                    "Hostname": "",
                    'Exception': e}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults):
        return  {"Name":            {"type": "string",       "order":0,  "title": "$lvar(6013)", "desc": "$lvar(6014)", "key": "name",            "default":""           },
                 "IP Version":      {"type": "scrolloptions","order":4,  "title": "$lvar(6037)", "desc": "$lvar(6038)", "key": "ipversion",       "default":"IPv4Only", "options":["IPv4Only","IPv6Only","All","Auto"]},
                 "TimeOut":         {"type": "numericfloat", "order":6,  "title": "$lvar(6019)", "desc": "$lvar(6020)", "key": "timeout",         "default":"15.0"}
                }


        #"ReturnPort":      {"type": "bool", "order": 4, "title": "$lvar(SCRIPT_DISC_UPNP_2)", "desc": "$lvar(SCRIPT_DISC_UPNP_3)", "key": "returnport", "default": "1"},


'''
ff02::c

'''

class cThread_Discover_Kira(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, bOnlyOnce,oReq,uIPVersion,fTimeOut,oCaller):
        threading.Thread.__init__(self)

        self.bOnlyOnce  = bOnlyOnce
        self.uIPVersion = uIPVersion
        self.oCaller    = oCaller
        self.fTimeOut   = fTimeOut
        self.bStopWait  = False
        self.oReq       = oReq

    def run(self):

        bReturnNow = False
        if self.bOnlyOnce:
            cThread_Discover_Kira.oWaitLock.acquire()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            cThread_Discover_Kira.oWaitLock.release()
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
                            Logger.info(u'Bingo: Discovered device  %s:' %oRet.sFoundIP)
                            try:
                                oRet.uFoundHostName = socket.gethostbyaddr(oRet.sFoundIP)[0]
                            except Exception:
                                pass
                            cThread_Discover_Kira.oWaitLock.acquire()
                            self.oCaller.aResults.append(oRet)
                            cThread_Discover_Kira.oWaitLock.release()
                            if self.bOnlyOnce:
                                oSocket.close()
                                return
                    else:
                        break
                oSocket.close()
            # Logger.warning(u'No device found device %s:%s:%s' %(self.oReq.uManufacturer,self.oReq.uModels,self.oReq.uFriendlyName))
            return

        except Exception as e:
            LogError(u'Error on discover Kira (%s)' % (self.uIPVersion), e)
            if oSocket:
                oSocket.close()
            return


    def SendDiscover(self):


        if self.uIPVersion=="IPv4Only":
            uUDP_IP     = u'239.255.255.250'
            iUDP_PORT   = 30303
            uMessage = u'disD'

            oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)
            if PY2:
                oSocket.sendto(uMessage, (uUDP_IP, iUDP_PORT))
            else:
                oSocket.sendto(ToBytes(uMessage), (uUDP_IP, iUDP_PORT))
            return oSocket

        if self.uIPVersion == "IPv6Only":

            # socket.IPPROTO_IPV6 might not be defined
            IPPROTO_IPV6 = 41
            try:
                IPPROTO_IPV6=socket.IPPROTO_IPV6
            except:
                pass

            uUDP_IP = u'ff02::f'
            iUDP_PORT = 30303
            uMessage = u'disD'

            oSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            oSocket.settimeout(self.fTimeOut)
            oSocket.setsockopt(IPPROTO_IPV6, socket.IP_MULTICAST_TTL, 20)
            if PY2:
                oSocket.sendto(uMessage, (uUDP_IP, iUDP_PORT))
            else:
                oSocket.sendto(ToBytes(uMessage), (uUDP_IP, iUDP_PORT))
            return oSocket

        return None


    def GetDeviceDetails(self,sData,tSenderAddr):
        oRet                     = QueryDict()
        oRet.sFoundIP            = tSenderAddr[0]
        oRet.uFoundPort          = tSenderAddr[1]
        oRet.bFound              = True
        oRet.sData               = sData
        oRet.uIPVersion          = self.uIPVersion
        return oRet

    def CheckDeviceDetails(self,oRet):
        return

