# -*- coding: utf-8 -*-
# Ping

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


from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.utils.Network     import Ping

'''
<root>
  <repositorymanager>
    <entry>
      <name>Ping</name>
      <description language='English'>Interface to verify, if devices respond to ping</description>
      <description language='German'>Interface um zu prüfen, ob Geräte auf einen Ping antworten</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/ping</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/ping.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>ping/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


class cInterface(cBaseInterFace):

    def Init(self, uInterFaceName, oFnInterFace=None):
        cBaseInterFace.Init(self, uInterFaceName, oFnInterFace)
        self.oInterFaceConfig.dDefaultSettings['Host']['active']  = "enabled"
        self.oInterFaceConfig.dDefaultSettings['Host']['desc']    = "$lvar(IFACE_PING_1)"

    def DoAction(self,oAction):
        oSetting=self.GetSettingObjectForConfigName(oAction.dActionPars.get(u'configname',u''))
        if Ping(oSetting.aInterFaceIniSettings.uHost):
            return 0
        else:
            return 1
