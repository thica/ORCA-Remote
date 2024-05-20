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

from typing                                     import Dict
from typing                                     import Optional

from wakeonlan                                  import send_magic_packet
from kivy.logger                                import Logger
from ORCA.interfaces.BaseInterface              import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings      import cBaseInterFaceSettings
from ORCA.action.Action import cAction
from ORCA.actions.ReturnCode                    import eReturnCode
from ORCA.utils.FileName                        import cFileName


import struct, socket
from ORCA.Globals import Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>Wake-On-LAN</name>
      <description language='English'>Interface to send a WOL command to device</description>
      <description language='German'>Interface ein WOL Kommando an ein Gerät zu senden</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
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


    # noinspection PyUnusedLocal
    # we us it, as it handles some configuration topics on connect
    class cInterFaceSettings(cBaseInterFaceSettings):
        pass

    def __init__(self):
        super().__init__()
        self.dSettings:Dict   = {}
        self.oSetting       = None


    def Init(self, uObjectName: str, oFnObject: Optional[cFileName] = None) -> None:
        super().Init(uObjectName=uObjectName, oFnObject=oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = 'enabled'
        self.oObjectConfig.dDefaultSettings['MAC']['active']                         = 'enabled'


    def DoAction(self,oAction:cAction) -> eReturnCode:
        self.ShowDebug(uMsg='Request Action Wakeup')
        uConfigName:str = oAction.dActionPars.get('configname','')
        oSetting:cBaseInterFaceSettings = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        oSetting.Connect()
        oSetting.Disconnect()
        if oAction.dActionPars.get('commandname')=='power_on':
            return self.WakeOnLan(uMacAddress=oSetting.aIniSettings.uMAC, uHost=oSetting.aIniSettings.uHost,uConfigName=uConfigName)
        else:
            Logger.error('wake_lan interface only supports the power_on command')
            return eReturnCode.Error


    def WakeOnLan(self,*,uMacAddress:str,uHost:str,uConfigName:str) -> eReturnCode:
        ''' We do it on different ways to bypass windows x multihomed broadcast problems'''
        self.ShowInfo(uMsg='Sending Magic Package for '+uMacAddress)
        uMacAddressNorm:str=self.NormalizeMac(uMacAddress,uConfigName)
        send_magic_packet(uMacAddressNorm)
        send_magic_packet(uMacAddressNorm,  ip_address=uHost)
        send_magic_packet(uMacAddressNorm, ip_address=Globals.uIPSubNetV4)
        send_magic_packet(uMacAddressNorm, ip_address=Globals.uIPGateWayV4)
        # this is required on multihomed devives but does not work on windows
        #send_magic_packet(uMacAddressNorm, interface=Globals.uIPGateWayV4)

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
            self.ShowError(uMsg="Wrong format for MAC Address:"+uMacAddress,uParConfigName=uConfigName)
        return uRet

    # noinspection PyMethodMayBeStatic
    def wake_on_lan(self,uMacAddress):
        """ As usual, Microsoft is not able to code properly, so we need some more code to get it working on Windows """

        i:int


        # Pad the synchronization stream.
        uData = ''.join(['FFFFFFFFFFFF', uMacAddress* 20])
        bySend_data =  b''

        # Split up the hex values and pack.
        for i in range(0, len(uData), 2):
            bySend_data = b''.join([bySend_data, struct.pack('B', int(uData[i: i + 2], 16))])

        # Broadcast it to the LAN
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(bySend_data, ('255.255.255.255', 9))
        sock.sendto(bySend_data, (Globals.uIPSubNetV4, 9)) # This should do it, the rest is fallback
        sock.sendto(bySend_data, ("192.168.1.150", 9))  # This should do it, the rest is fallback
        sock.sendto(bySend_data, (Globals.uIPGateWayV4, 7))
        sock.sendto(bySend_data, ('255.255.255.255', 7))
        sock.sendto(bySend_data, (Globals.uIPSubNetV4, 7))

        sock.close()
