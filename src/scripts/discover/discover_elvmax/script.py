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

import socket
import select

from kivy.uix.button                        import Button
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.vars.QueryDict                    import TypedQueryDict
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.TypeConvert                 import ToUnicode

import ORCA.Globals as Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>ELV MAX Discover</name>
      <description language='English'>Discover ELV MAX cubes</description>
      <description language='German'>Erkennt bwz. sucht ELV MAX Cubes</description>
      <author>Carsten Thielepape</author>
      <version>5.0.0</version>
      <minorcaversion>5.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_elvmax</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_elvmax.zip</sourcefile>
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
    WikiDoc:Page:Scripts-Discover-ELVMAX
    WikiDoc:TOCTitle:Discover ELVMAX
    = Script Discover ELVMAX =

    The ELV MAX discover script discovers ELV MAX cubes for heaing control.
    You can filter the discover result by passing the following parameters::
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |serial
    |Discover models only with a specific serial number (leave it blank to discover all)
    |-
    |timeout
    |Specifies the timout for discover
    |}</div>

    WikiDoc:End
    """

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cScript):
            super().__init__(oScript)
            self.aIniSettings.fTimeOut                     = 5.0

    def __init__(self):
        super().__init__()
        self.uSubType:str                   = u'ELVMAX'
        self.uSerial:str                    = u''
        self.aResults:List[TypedQueryDict]  = []

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        super().Init(uObjectName= uObjectName, oFnObject=oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(SCRIPT_DISC_ELVMAX_1)','$lvar(5035)']

    def ListDiscover(self):

        dDevice: TypedQueryDict
        dArgs:Dict = {}

        self.Discover(**dArgs)
        for dDevice in self.aResults:
            self.AddLine([dDevice.uFoundIP,dDevice.uFoundSerial,dDevice.uFoundHostName],dDevice)


    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:TypedQueryDict = oButton.dDevice

        uText=  u"$lvar(5029): %s \n" \
                u"$lvar(5035): %s \n" \
                u"$lvar(1063): %s \n" \
                u"$lvar(SCRIPT_DISC_ELVMAX_1): %s " % (dDevice.uFoundIP,dDevice.uFoundHostName,dDevice.uFoundName,dDevice.uFoundSerial)

        ShowMessagePopUp(uMessage=uText)


    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return  {"Serial Number":   {"type": "string",       "order":0,  "title": "$lvar(SCRIPT_DISC_ELVMAX_1)", "desc": "$lvar(SCRIPT_DISC_ELVMAX_1)", "key": "serialnumber",    "default":"" }
                }

    def Discover(self,**kwargs):

        oSendSocket:Union[socket.socket,None]    = None
        oReceiveSocket:Union[socket.socket,None] = None
        iPort:int                                = 23272
        uSerial:str                              = kwargs.get('serialnumber',"")
        uConfigName:str                          = kwargs.get('configname',self.uConfigName)
        oSetting:cBaseScriptSettings             = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut:float                           = ToFloat(kwargs.get('timeout', oSetting.aIniSettings.fTimeOut))
        del self.aResults[:]

        self.ShowDebug (uMsg=u'Try to discover ELV MAX device:  %s ' % uSerial)

        try:
            oSendSocket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            oSendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
            oSendSocket.settimeout(10)

            byData:bytearray =  bytearray("eQ3Max", "utf-8") + \
                                bytearray("*\0",    "utf-8") + \
                                bytearray('*' * 10, "utf-8") + \
                                bytearray('I',      "utf-8")

            if Globals.uPlatform != 'win':
                oSendSocket.sendto(byData,("255.255.255.255",iPort))
            else:
                oSendSocket.sendto(byData, (Globals.uIPSubNetV4, iPort))

            oReceiveSocket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oReceiveSocket.settimeout(fTimeOut)
            oReceiveSocket.bind(("0.0.0.0", iPort))

            while True:
                # we do not wait too long
                aReady:Tuple = select.select([oReceiveSocket],[],[],fTimeOut)
                if aReady[0]:
                    # Get a response
                    byData, tSenderAddr = oReceiveSocket.recvfrom(50)
                    dRet = self.GetDeviceDetails(byData, tSenderAddr)
                    if uSerial=="" or dRet.uSerial == uSerial:
                        self.aResults.append(dRet)
                else:
                    break

            if oSendSocket:
                oSendSocket.close()
            if oReceiveSocket:
                oReceiveSocket.close()

            if len(self.aResults)>0:
                return TypedQueryDict([("Host", self.aResults[0].uFoundIP),("Hostname",self.aResults[0].uFoundHostName), ("Serial",self.aResults[0].uFoundSerial), ("Name",self.aResults[0].uFoundName)])

        except Exception as e:
            self.ShowError(uMsg="Error on Discover",oException=e)

        if oSendSocket:
            oSendSocket.close()
        if oReceiveSocket:
            oReceiveSocket.close()

        self.ShowWarning(uMsg=u'No ELV MAX Cube found %s' % uSerial)
        return TypedQueryDict([("Host", ""), ("Hostname", ""), ("Serial", ""), ("Name", "")])

    # noinspection PyMethodMayBeStatic
    def GetDeviceDetails(self,byData:bytes,tSenderAddr:Tuple) -> TypedQueryDict:

        dRet:TypedQueryDict      = TypedQueryDict()
        dRet.uFoundIP            = tSenderAddr[0] # ==10
        dRet.uData               = ToUnicode(byData[:18])
        dRet.uFoundName          = byData[0:8].decode('utf-8')
        dRet.uFoundSerial        = byData[8:18].decode('utf-8')
        dRet.uFoundHostName      = socket.gethostbyaddr(dRet.uFoundIP)[0]
        dRet.uIPVersion          = u"IPv4"
        self.ShowInfo(uMsg=u'Discovered device %s:%s:%s at %s' % (dRet.uFoundName, dRet.uFoundHostName, dRet.uFoundSerial, dRet.uFoundIP))
        return dRet
