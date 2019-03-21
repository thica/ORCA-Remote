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

from kivy.logger import Logger

from ORCA.interfaces.BaseInterface import cBaseInterFace

from wakeonlan import send_magic_packet

'''
<root>
  <repositorymanager>
    <entry>
      <name>Wake-On-LAN</name>
      <description language='English'>Interface to send a WOL command to device</description>
      <description language='German'>Interface ein WOL Kommando an ein Gerät zu senden</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/wake_on_lan</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/wake_on_lan.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>wake_on_lan/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    def __init__(self):
        cBaseInterFace.__init__(self)
        self.aSettings   = {}

    def GetConfigJSON(self):
        return {"MAC": {"active": "enabled", "order": 0, "type": "string", "title": "$lvar(IFACE_WOL_3)", "desc": "$lvar(IFACE_WOL_4)",  "section": "$var(InterfaceConfigSection)","key": "MAC",  "default":"aa:bb:cc:dd:ee:ff"}
                }

    def DoAction(self,oAction):
        self.ShowDebug(u'Request Action Wakeup')
        oSetting=self.GetSettingObjectForConfigName(oAction.dActionPars.get(u'configname',u''))
        if oAction.dActionPars.get("commandname")=="power_on":
            return self.WakeOnLan(oSetting.aInterFaceIniSettings.uMAC)
        else:
            Logger.error("wake_lan interface only supports the power_on command")
            return False

    def WakeOnLan(self,uMacAddress):
        self.ShowInfo(u'Sending Magic Package for '+uMacAddress)
        send_magic_packet(uMacAddress)
        return 1
