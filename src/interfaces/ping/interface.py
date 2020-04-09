# -*- coding: utf-8 -*-
# Ping

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


from ORCA.interfaces.BaseInterface          import cBaseInterFace
from ORCA.utils.Network                     import Ping
from ORCA.utils.FileName                    import cFileName
from ORCA.Action                            import cAction
from ORCA.interfaces.BaseInterfaceSettings  import cBaseInterFaceSettings
from ORCA.actions.ReturnCode                import eReturnCode

'''
<root>
  <repositorymanager>
    <entry>
      <name>Ping</name>
      <description language='English'>Interface to verify, if devices respond to ping</description>
      <description language='German'>Interface um zu prüfen, ob Geräte auf einen Ping antworten</description>
      <author>Carsten Thielepape</author>
      <version>5.0.1</version>
      <minorcaversion>5.0.1</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/ping</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/ping.zip</sourcefile>
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
    def Init(self, uObjectName: str, oFnObject: cFileName = None) -> None:
        super().Init(uObjectName=uObjectName, oFnObject=oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['Host']['desc']    = "$lvar(IFACE_PING_1)"

    def DoAction(self,oAction:cAction) -> eReturnCode:
        oSetting:cBaseInterFaceSettings=self.GetSettingObjectForConfigName(uConfigName=oAction.dActionPars.get(u'configname',u''))
        if Ping(uHostname=oSetting.aIniSettings.uHost):
            return eReturnCode.Success
        else:
            return eReturnCode.Error
