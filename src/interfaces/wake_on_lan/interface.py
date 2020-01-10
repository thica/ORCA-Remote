# -*- coding: utf-8 -*-
# Wake-On-LAN
#
# Parts of Code take from Copyright notice below
#
# Copyright (C) 2002 by Micro Systems Marc Balmer
# Written by Marc Balmer, marc@msys.ch, http://www.msys.ch/
# This code is free software under the GPL

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

from typing                                     import Dict
from wakeonlan                                  import send_magic_packet
from kivy.logger                                import Logger
from ORCA.interfaces.BaseInterface              import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings      import cBaseInterFaceSettings
from ORCA.Action                                import cAction
from ORCA.actions.ReturnCode                    import eReturnCode

import struct, socket
import ORCA.Globals as Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>Wake-On-LAN</name>
      <description language='English'>Interface to send a WOL command to device</description>
      <description language='German'>Interface ein WOL Kommando an ein Gerät zu senden</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/wake_on_lan</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/wake_on_lan.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    def __init__(self):
        cBaseInterFace.__init__(self)
        self.dSettings:Dict   = {}

    def GetConfigJSON(self) -> Dict:
        return {"MAC": {"active": "enabled", "order": 0, "type": "string", "title": "$lvar(IFACE_WOL_3)", "desc": "$lvar(IFACE_WOL_4)",  "section": "$var(ObjectConfigSection)","key": "MAC",  "default":"aa:bb:cc:dd:ee:ff"}
                }

    def DoAction(self,oAction:cAction) -> eReturnCode:
        self.ShowDebug(u'Request Action Wakeup')
        uConfigName:str = oAction.dActionPars.get(u'configname',u'')
        oSetting:cBaseInterFaceSettings = self.GetSettingObjectForConfigName(uConfigName)
        if oAction.dActionPars.get("commandname")=="power_on":
            return self.WakeOnLan(oSetting.aIniSettings.uMAC, uConfigName)
        else:
            Logger.error("wake_lan interface only supports the power_on command")
            return eReturnCode.Error

    def WakeOnLan(self,uMacAddress,uConfigName:str) -> eReturnCode:
        self.ShowInfo(u'Sending Magic Package for '+uMacAddress)
        uMacAddressNorm:str=self.NormalizeMac(uMacAddress,uConfigName)
        send_magic_packet(uMacAddressNorm)
        self.wake_on_lan(uMacAddressNorm)
        return eReturnCode.Success

    # noinspection PyMethodMayBeStatic
    def NormalizeMac(self,uMacAddress:str,uConfigName:str) -> str:
        # Check macaddress format and try to compensate
        uRet:str = uMacAddress
        if len(uRet) == 12:
            pass
        elif len(uRet) == 12 + 5:
            sep = uRet[2]
            uRet = uRet.replace(sep, '')
        else:
            self.ShowError("Wrong format for MAC Address:"+uMacAddress,uConfigName)
        return uRet

    # noinspection PyMethodMayBeStatic
    def wake_on_lan(self,uMacAddress):
        """ As usual, Microsoft is not able to code properly, so we need some more code to get it working on Windows """

        i:int
        # Pad the synchronization stream
        byData = b'FFFFFFFFFFFF' + (uMacAddress * 20).encode()
        bySend_data = b''

        # Split up the hex values in pack
        for i in range(0, len(byData), 2):
            bySend_data += struct.pack('!B', int(byData[i: i + 2], 16))

        # Broadcast it to the LAN
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(bySend_data, ('255.255.255.255', 9))
        sock.sendto(bySend_data, (Globals.uIPSubNetV4, 9)) # This should do it, the rest is fallbal
        sock.sendto(bySend_data, ('255.255.255.255', 7))
        sock.sendto(bySend_data, (Globals.uIPSubNetV4, 7))
