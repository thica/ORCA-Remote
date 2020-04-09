# -*- coding: utf-8 -*-
# cec_rpi
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

from __future__             import annotations
from typing                 import Dict
from ORCA.vars.Access       import SetVar

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>CEC Control (RPI)</name>
      <description language='English'>CEC Control using the Raspberry PI</description>
      <description language='German'>CEC Steuerung über den Raspberry PI</description>
      <author>Carsten Thielepape</author>
      <version>5.0.1</version>
      <minorcaversion>5.0.1</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/cec_rpi</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/cec_rpi.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
            <dependency>
                <type>interfaces</type>
                <name>Telnet</name>
            </dependency>
      </dependencies>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interfaces.telnet.interface import cInterface as cInterFaceTelnet
else:
    cInterFaceTelnet = Globals.oInterFaces.LoadInterface('telnet').GetClass("cInterface")

class cInterface(cInterFaceTelnet):
    class cInterFaceSettings(cInterFaceTelnet.cInterFaceSettings):
        def __init__(self,oInterFace:cInterface):
            super().__init__(oInterFace)
            self.aIniSettings.uSource_DeviceType      =  u"Recording 1"
            self.aIniSettings.uSource_DeviceID        =  u"00000"
            self.aIniSettings.uDestination_DeviceType =  u"TV"
            self.aIniSettings.uFNCodeset              =  u"CODESET_cec_rpi_telnet.xml"
            self.uTarget:str                          =  u''

        def ReadConfigFromIniFile(self,uConfigName:str) -> None:

            super().ReadConfigFromIniFile(uConfigName)

            try:
                self.SetContextVar(uVarName='SOURCEID',uVarValue=self.aIniSettings.uSource_DeviceID)

                uSourceDevice:str      = u'1'
                uDestinationDevice:str = u'0'

                for uKey in self.oInterFace.aTargets:
                    if self.oInterFace.aTargets[uKey]==self.aIniSettings.uSource_DeviceType:
                        uSourceDevice=uKey
                        self.SetContextVar(uVarName='SOURCETYPE' ,uVarValue=uKey)
                    if self.oInterFace.aTargets[uKey]==self.aIniSettings.uDestination_DeviceType:
                        uDestinationDevice=uKey
                        self.SetContextVar(uVarName='DESTTYPE' ,uVarValue=uKey )

                self.uTarget = uSourceDevice+uDestinationDevice
                self.SetContextVar(uVarName='TARGET' ,uVarValue=self.uTarget)
            except Exception as e:
                self.ShowError(uMsg=u'Cannot read config name:'+self.oInterFace.oObjectConfig.oFnConfig.string + u' Section:'+self.uSection,oException=e)

    def __init__(self):
        super().__init__()
        self.dTargets:Dict[str,str] = {'0':'TV','1':'Recording 1','2':'Recording 2','3':'Tuner 1','4':'Playback 1','5':'Audio system','6':'Tuner 2','7':'Tuner 3','8':'Playback 2','9':'Playback 3','A':'Tuner 4','B':'Playback 3','C':'Reserved (C)','D':'Reserved (D)','E':'Reserved (E)','F':'Unregistered'}
        uValueString:str = u''
        for uKey in self.dTargets:
            uValueString+=u'\"'+self.dTargets[uKey]+u'\",'
        uValueString = uValueString[1:-2]
        SetVar(uVarName = "VALUESTRING", oVarValue = uValueString)

    def GetConfigJSON(self) -> Dict:
        dRet:Dict = super().GetConfigJSON()
        dAdd:Dict = {"Source_DeviceType":      {"active": "enabled", "order": 10, "type": "scrolloptions",  "title": "Source Device Type",      "desc": "$lvar(6005)",  "section": "$var(ObjectConfigSection)","key": "Source_DeviceType",           "default":"Recording 1", "options":["$var(VALUESTRING)"]},
                     "Source_DeviceID":        {"active": "enabled", "order": 11, "type": "string",         "title": "Source Device ID",        "desc": "$lvar(6005)",  "section": "$var(ObjectConfigSection)","key": "Source_DeviceID",             "default":"00000"       },
                     "Destination_DeviceType": {"active": "enabled", "order": 12, "type": "scrolloptions",  "title": "Destination Device Type", "desc": "$lvar(6003)",  "section": "$var(ObjectConfigSection)","key": "Destination_DeviceType",      "default":"TV", "options":["$var(VALUESTRING)"]}
                    }

        dRet.update(dAdd)
        return dRet

