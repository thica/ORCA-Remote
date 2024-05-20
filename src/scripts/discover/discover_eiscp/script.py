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
import re
import threading

from typing import Dict
from typing import List
from typing import Tuple
from typing import Callable


from struct                                 import pack
from kivy.uix.button                        import Button
from ORCA.scripttemplates.Template_Discover_Broadcast import cDiscoverScriptTemplate_Broadcast
from ORCA.scripttemplates.Template_Discover_Broadcast import cThread_DiscoverTemplate_Broadcast
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.utils.TypeConvert                 import ToList
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.Wildcard                    import MatchWildCard
from ORCA.vars.QueryDict                    import TypedQueryDict

from ORCA.Globals import Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>EISCP Discover</name>
      <description language='English'>Discover EISCP/Onkyo devices</description>
      <description language='German'>Erkennt sucht EISCP/Onkyo Geräte über upnp</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
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

class cScript(cDiscoverScriptTemplate_Broadcast):
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
    |Specifies the timeout for discover
    |}</div>

    Blank options will not be used.

    WikiDoc:End
    """

    def __init__(self):
        super().__init__()
        self.uSubType:str                       = 'EISCP (Onkyo)'
        self.uScriptTitle                       = 'Onkyo/EISCP Discovery'

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(6002)','$lvar(5031)','$lvar(5032)']

    def CreateArgs(self) -> Dict:

        return {'onlyonce':      0,
                'ipversion':     'IPv4Only',
                'donotwait':       1,
                'ipv4':'239.255.255.250',
                'portv4':60128
                }

    def GetRequests(self,dArgs:Dict)-> TypedQueryDict:
        """ This is could be overridden """
        dReq:TypedQueryDict=super().GetRequests(dArgs=dArgs)
        dReq.uModels = dArgs.get('models', '')
        dReq.iPortV4   = 60128
        return dReq

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:TypedQueryDict = oButton.dDevice
        uText:str = f'$lvar(5029): {dDevice.uFoundIP} \n$lvar(6002): {dDevice.uFoundPort} \n$lvar(5031): {dDevice.uFoundModel} \n$lvar(5032): {dDevice.uFoundIdentifier} \n\n{dDevice.uData}'
        ShowMessagePopUp(uMessage=uText)

    def ShowNotFoundMessage(self) -> None:
        """ needs to be overwritten """
        self.ShowWarning(uMsg='No EISCP device found, Models: %s' % self.dReq.uModels)

    def ShowStartMessage(self) -> None:
        """ needs to be overwritten """
        self.ShowDebug(uMsg='Try to discover Onkyo device by EISCP:  Models: %s ' % self.dReq.uModels)

    def CreateResult(self,bEmpty:bool=False,oException:Exception=None) -> Dict:

        if not bEmpty:
            return {'Model': self.aResults[0].uFoundModel, 'Host': self.aResults[0].uFoundIP, 'Port': self.aResults[0].uFoundPort, 'Category': self.aResults[0].uFoundCategory, 'Exception': None}
        else:
            return  {'Model':'','Host':'','Port':'','Category':'','Exception':None}

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return {'TimeOut': {'type': 'numericfloat','active':'enabled', 'order':0,  'title': '$lvar(6019)', 'desc': '$lvar(6020)','key': 'timeout', 'default':'2.0'},
                'Models':  {'type': 'string',      'active':'enabled', 'order':1,  'title': '$lvar(SCRIPT_DISC_EISCP_1)', 'desc': '$lvar(SCRIPT_DISC_EISCP_2)','key': 'models', 'default':''},
                'IP Version': {'type': 'scrolloptions', 'order': 4, 'title': '$lvar(6037)', 'desc': '$lvar(6038)', 'key': 'ipversion', 'default': 'IPv4Only', 'options': ['IPv4Only', 'IPv6Only', 'All', 'Auto']}
                }

    # noinspection PyMethodMayBeStatic
    def GetThreadClass(self) -> Callable:
        return cThread_Discover_EISCP


class cThread_Discover_EISCP(cThread_DiscoverTemplate_Broadcast):
    oWaitLock = threading.Lock()

    def __init__(self, bOnlyOnce:bool,dReq:TypedQueryDict,uIPVersion:str, uST:str,fTimeOut:float,oCaller:cDiscoverScriptTemplate_Broadcast):

        try:
            super(cThread_Discover_EISCP, self).__init__(bOnlyOnce,dReq,uIPVersion, uST,fTimeOut,oCaller)
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
        except Exception as e:
            self.oCaller.ShowError(uMsg="Error on cThread_Discover_EISCP.__init__", oException=e)

    # noinspection PyMethodMayBeStatic
    def CreateEISPHeader(self,uMessage:str) -> bytes:
        """
        Creates an EISP Header for the given command and and adds the command
        :param str uMessage: The
        :return: The Header plus command
        """
        # struct.pack doesnt not work reliable on some Android Platform processors
        try:
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
        except Exception as e:
            self.oCaller.ShowError(uMsg="Error on CreateEISPHeader", oException=e)
            return b''

    # noinspection PyMethodMayBeStatic
    def CreateEISPPacket(self, iscp_message:str) -> bytes:
        # Test for discover
        # We attach data separately, because Python's struct module does
        # not support variable length strings,
        try:
            return pack('! 4s I I b 3b', b'ISCP', 16, len(iscp_message), 0x01, 0x00, 0x00, 0x00) +ToBytes(iscp_message)
        except Exception as e:
            self.oCaller.ShowError(uMsg="Error on CreateEISPPacket",oException=e)
            return b''

    def ShowFoundMessage(self,dRet:TypedQueryDict):
        """ needs to be overwritten """
        self.oCaller.ShowInfo(uMsg=f'Discovered Onkyo device {dRet.uFoundIdentifier}:{dRet.uFoundModel} at {dRet.uFoundIP}:')

    def CreatePayloadV4(self) -> bytes:
        return self.bOnkyoMagic

    def SendFoundNotification(self,dRet:TypedQueryDict):
        Globals.oNotifications.SendNotification(uNotification='DISCOVER_SCRIPTFOUND',  **{'script': self, 'scriptname': self.oCaller.uObjectName, 'line': [dRet.uFoundIP, dRet.uFoundPort, dRet.uFoundModel, dRet.uFoundIdentifier], 'device': dRet})

    def CreateTagLine(self,dRet:TypedQueryDict) -> str:
        return dRet.uFoundIP + dRet.uFoundModel + dRet.uFoundIdentifier


    def GetDeviceDetails(self,byData:bytes,tSenderAddr:Tuple) -> TypedQueryDict:
        dRet:TypedQueryDict      = super().GetDeviceDetails(byData,tSenderAddr)
        dRet.uFoundPort          = ''
        dRet.uFoundModel         = ''
        dRet.uFoundIdentifier    = ''
        dRet.uFoundCategory      = ''
        dRet.uData               = ''
        uResponse                = ToUnicode(byData)[16:]

        if uResponse.find('ECN') != -1:
            info = re.match(self.rMatch, uResponse.strip(), re.VERBOSE).groupdict()
            uResponse = uResponse[10:]
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

