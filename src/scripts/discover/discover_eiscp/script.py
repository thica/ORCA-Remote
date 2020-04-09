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
import socket
import re
import select
import threading

from typing import Dict
from typing import List
from typing import Union
from typing import Tuple
from typing import Optional

from struct                                 import pack
from kivy.uix.button                        import Button

from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.TypeConvert                 import ToBool
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToList
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.Wildcard                    import MatchWildCard
from ORCA.vars.QueryDict                    import TypedQueryDict

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>EISCP Discover</name>
      <description language='English'>Discover EISCP/Onkyo devices</description>
      <description language='German'>Erkennt sucht EISCP/Onkyo Geräte über upnp</description>
      <author>Carsten Thielepape</author>
      <version>5.0.1</version>
      <minorcaversion>5.0.1</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_eiscp</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_eiscp.zip</sourcefile>
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
        def __init__(self,oScript:cScript):
            super().__init__(oScript)
            self.aIniSettings.fTimeOut = 10.0

    def __init__(self):
        super().__init__()
        self.uSubType:str                       = u'EISCP (Onkyo)'
        self.aResults:List[TypedQueryDict]      = []
        self.aThreads:List[threading.Thread]    = []
        self.dReq:TypedQueryDict                = TypedQueryDict()
        self.bOnlyOnce:bool                     = True
        self.uIPVersion:str                     = u'Auto'

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """

        super().Init(uObjectName=uObjectName,oFnObject=oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(6002)','$lvar(5031)','$lvar(5032)']

    def ListDiscover(self) -> None:
        dArgs:Dict              = {"onlyonce": 0,
                                   "ipversion": "All"}

        dDevices:Dict[str,TypedQueryDict] = {}
        dDevice:TypedQueryDict

        self.Discover(**dArgs)

        for dDevice in self.aResults:
            uTageLine:str = dDevice.uFoundIP + dDevice.uFoundModel + dDevice.uFoundIdentifier
            if dDevices.get(uTageLine) is None:
               dDevices[uTageLine]=dDevice
               self.AddLine([dDevice.uFoundIP, dDevice.uFoundPort, dDevice.uFoundModel, dDevice.uFoundIdentifier], dDevice)
        return

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:TypedQueryDict = oButton.dDevice

        uText:str = u"$lvar(5029): %s \n"\
                    u"$lvar(6002): %s \n"\
                    u"$lvar(5031): %s \n"\
                    u"$lvar(5032): %s \n"\
                    u"\n"\
                    u"%s" % (dDevice.uFoundIP,dDevice.uFoundPort,dDevice.uFoundModel,dDevice.uFoundIdentifier,dDevice.uData)

        ShowMessagePopUp(uMessage=uText)


    def Discover(self,**kwargs) -> Dict:

        self.dReq.clear()
        uConfigName:str                 = kwargs.get('configname',self.uConfigName)
        oSetting:cBaseScriptSettings    = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut:float                  = ToFloat(kwargs.get('timeout',oSetting.aIniSettings.fTimeOut))
        self.dReq.uModels               = kwargs.get('models',"")
        bOnlyOnce:bool                  = ToBool(kwargs.get('onlyonce',"1"))
        uIPVersion:str                  = kwargs.get('ipversion',"IPv4Only")

        self.ShowDebug(uMsg=u'Try to discover Onkyo device by EISCP:  Models: %s ' % self.dReq.uModels)
        del self.aResults[:]
        del self.aThreads[:]

        try:
            oThread:cThread_Discover_EISCP
            if uIPVersion == "IPv4Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 == ""):
                oThread = cThread_Discover_EISCP(bOnlyOnce=bOnlyOnce,dReq=self.dReq,uIPVersion="IPv4Only", fTimeOut=fTimeOut, oCaller=self)
                self.aThreads.append(oThread)
                self.aThreads[-1].start()
            if uIPVersion == "IPv6Only" or uIPVersion == "All" or (uIPVersion == "Auto" and Globals.uIPAddressV6 != ""):
                oThread = cThread_Discover_EISCP(bOnlyOnce=bOnlyOnce, dReq=self.dReq, uIPVersion="IPv6Only", fTimeOut=fTimeOut, oCaller=self)
                self.aThreads.append(oThread)
                self.aThreads[-1].start()

            for oT in self.aThreads:
                oT.join()

            if len(self.aResults)>0:
                return {'Model': self.aResults[0].uFoundModel, 'Host': self.aResults[0].uFoundIP,'Port': self.aResults[0].uFoundPort, 'Category': self.aResults[0].uFoundCategory, 'Exception': None}
            else:
                self.ShowWarning(uMsg='No device found, Models: %s' % self.dReq.uModels)
            return  {'Model':'','Host':'','Port':'','Category':'','Exception':None}

        except Exception as e:
            self.ShowDebug(uMsg=u'No EISCP device found, possible timeout')
            return {'Model':'','Host':'','Port':'','Category':'','Exception':e}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return {"TimeOut": {"type": "numericfloat","active":"enabled", "order":0,  "title": "$lvar(6019)", "desc": "$lvar(6020)","key": "timeout", "default":"2.0"},
                "Models":  {"type": "string",      "active":"enabled", "order":1,  "title": "$lvar(SCRIPT_DISC_EISCP_1)", "desc": "$lvar(SCRIPT_DISC_EISCP_2)","key": "models", "default":""},
                "IP Version": {"type": "scrolloptions", "order": 4, "title": "$lvar(6037)", "desc": "$lvar(6038)", "key": "ipversion", "default": "IPv4Only", "options": ["IPv4Only", "IPv6Only", "All", "Auto"]}
                }


class cThread_Discover_EISCP(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, bOnlyOnce:bool,dReq:TypedQueryDict,uIPVersion:str, fTimeOut:float,oCaller:cScript):
        threading.Thread.__init__(self)
        self.bOnlyOnce:bool     = bOnlyOnce
        self.uIPVersion:str     = uIPVersion
        self.oCaller:cScript    = oCaller
        self.fTimeOut:float     = fTimeOut
        self.dReq:TypedQueryDict= dReq
        self.iOnkyoPort:int     = 60128
        self.rMatch     = r'''
                    !
                    (?P<device_category>\d)
                    ECN
                    (?P<model_name>[^/]*)/
                    (?P<iscp_port>\d{5})/
                    (?P<area_code>\w{2})/
                    (?P<identifier>.{0,12})
                    '''

        self.bOnkyoMagic:bytes = self.CreateEISPPacket('!xECNQSTN\r')


    # noinspection PyMethodMayBeStatic

    def CreateEISPHeader(self,uMessage:str) -> bytes:
        """
        Creates an EISP Header for the given command and and adds the command
        :param str uMessage: The
        :return: The Header plus command
        """
        # struct.pack doesnt not work reliable on some Android Platform processors

        iDataSize:int       = len(uMessage)
        iReserved:int       = 0
        iHeaderSize:int     = 16
        iVersion:int        = 0
        bHeaderSize:bytes   = iHeaderSize.to_bytes(4, byteorder='big')
        bDataSize:bytes     = iDataSize.to_bytes(4, byteorder='big')
        bVersion:bytes      = iVersion.to_bytes(1, byteorder='big')
        bReserved:bytes     = iReserved.to_bytes(3, byteorder='big')
        bMessage:bytes      = b'ISCP'+bHeaderSize+bDataSize+bVersion+bReserved+ToBytes(uMessage)
        return bMessage

    # noinspection PyMethodMayBeStatic
    def CreateEISPPacket(self, iscp_message:str) -> bytes:
        # Test for discover
        # We attach data separately, because Python's struct module does
        # not support variable length strings,
        return pack('! 4s I I b 3b', b'ISCP', 16, len(iscp_message), 0x01, 0x00, 0x00, 0x00) +ToBytes(iscp_message)

    def run(self) -> None:
        bReturnNow:bool = False
        if self.bOnlyOnce:
            cThread_Discover_EISCP.oWaitLock.acquire()
            if len(self.oCaller.aResults)>0:
                bReturnNow=True
            cThread_Discover_EISCP.oWaitLock.release()
        if bReturnNow:
            return
        self.Discover()

    def Discover(self) -> None:

        byData:bytes
        tSenderAddr:Tuple
        oRet:TypedQueryDict

        oSocket:Optional[socket.socket] = None
        try:
            oSocket = self.SendDiscover()
            if oSocket:
                # Parse all results
                while True:
                    #we do not wait too long
                    aReady:List = select.select([oSocket], [], [],self.fTimeOut)
                    if aReady[0]:
                        # Get a response
                        byData, tSenderAddr = oSocket.recvfrom(1024)
                        dRet = self.GetDeviceDetails(byData=byData,tSenderAddr=tSenderAddr)
                        self.CheckDeviceDetails(dRet=dRet)
                        if dRet.bFound:
                            self.oCaller.ShowInfo(uMsg=u'Discovered device %s:%s at %s:' % (dRet.uFoundIdentifier, dRet.uFoundModel, dRet.uFoundIP))
                            cThread_Discover_EISCP.oWaitLock.acquire()
                            self.oCaller.aResults.append(dRet)
                            cThread_Discover_EISCP.oWaitLock.release()
                            if self.bOnlyOnce:
                                oSocket.close()
                                return
                    else:
                        break
                oSocket.close()
            return

        except Exception as e:
            self.oCaller.ShowError(uMsg=u'Error on discover EISCP (%s)' % self.uIPVersion, oException=e)
            if oSocket:
                oSocket.close()
            return

    def SendDiscover(self) -> Union[socket.socket,None]:
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

    def GetDeviceDetails(self,byData:bytes,tSenderAddr:Tuple) -> TypedQueryDict:
        dRet:TypedQueryDict      = TypedQueryDict()
        dRet.bFound              = False
        dRet.uFoundIP            = u""
        dRet.uFoundPort          = u""
        dRet.uFoundModel         = u""
        dRet.uFoundIdentifier    = u""
        dRet.uFoundCategory      = u""
        dRet.uData               = u""

        uResponse = ToUnicode(byData)[16:]

        if uResponse.find('ECN') != -1:
            info = re.match(self.rMatch, uResponse.strip(), re.VERBOSE).groupdict()
            uResponse = uResponse[10:]
            dRet.uFoundIP            = tSenderAddr[0]
            dRet.uFoundPort          = ToUnicode(info['iscp_port'])
            dRet.uFoundModel         = info['model_name']
            dRet.uFoundIdentifier    = info['identifier']
            dRet.uFoundCategory      = ToUnicode(info['device_category'])
            dRet.uData               = uResponse
            dRet.bFound              = True
        return dRet

    def CheckDeviceDetails(self, dRet:TypedQueryDict) -> None:
        if dRet.bFound:
            aModels:List[str] = ToList(self.dReq.uModels)
            if len(aModels) > 0:
                dRet.bFound = False
                for uModel in aModels:
                    if uModel.startswith("'") or uModel.startswith('"'):
                        uModel = uModel[1:-2]
                    if MatchWildCard(uValue=dRet.uFoundModel,uMatchWithWildCard=uModel):
                        dRet.bFound = True
                        break
