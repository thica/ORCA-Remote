# -*- coding: utf-8 -*-
# cec_rpi
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

'''
<root>
  <repositorymanager>
    <entry>
      <name>CEC Control (RPI)</name>
      <description language='English'>CEC Control using the Raspberry PI</description>
      <description language='German'>CEC Steuerung über den Raspberry PI</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
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
        <file>cec_rpi/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

from ORCA.vars.Access       import SetVar
import ORCA.Globals as Globals

oInterFaceTelnet = Globals.oInterFaces.LoadInterface('telnet')

class cInterface(oInterFaceTelnet.cInterface):
    class cInterFaceSettings(oInterFaceTelnet.cInterface.cInterFaceSettings):
        def __init__(self,oInterFace):
            oInterFaceTelnet.cInterface.cInterFaceSettings.__init__(self,oInterFace)
            self.aInterFaceIniSettings.uSource_DeviceType      =  u"Recording 1"
            self.aInterFaceIniSettings.uSource_DeviceID        =  u"00000"
            self.aInterFaceIniSettings.uDestination_DeviceType =  u"TV"
            self.aInterFaceIniSettings.uFNCodeset              =  u"CODESET_cec_rpi_telnet.xml"

        def ReadConfigFromIniFile(self,uConfigName):

            oInterFaceTelnet.cInterface.cInterFaceSettings.ReadConfigFromIniFile(self,uConfigName)

            try:
                self.SetContextVar('SOURCEID',self.aInterFaceIniSettings.uSource_DeviceID)

                uSourceDevice='1'
                uDestinationDevice='0'
                for uKey in self.oInterFace.aTargets:
                    if self.oInterFace.aTargets[uKey]==self.aInterFaceIniSettings.uSource_DeviceType:
                        uSourceDevice=uKey
                        self.SetContextVar('SOURCETYPE' ,uKey)
                    if self.oInterFace.aTargets[uKey]==self.aInterFaceIniSettings.uDestination_DeviceType:
                        uDestinationDevice=uKey
                        self.SetContextVar('DESTTYPE' ,uKey )

                self.uTarget = uSourceDevice+uDestinationDevice
                self.SetContextVar('TARGET' ,self.uTarget)
            except Exception as e:
                self.ShowError(u'Cannot read config name:'+self.oInterFace.oInterFaceConfig.oFnConfig.string + u' Section:'+self.uSection,e)
            return

    def __init__(self):
        oInterFaceTelnet.cInterface.__init__(self)
        self.aTargets={'0':'TV','1':'Recording 1','2':'Recording 2','3':'Tuner 1','4':'Playback 1','5':'Audio system','6':'Tuner 2','7':'Tuner 3','8':'Playback 2','9':'Playback 3','A':'Tuner 4','B':'Playback 3','C':'Reserved (C)','D':'Reserved (D)','E':'Reserved (E)','F':'Unregistered'}
        uValueString=u''
        for uKey in self.aTargets:
            uValueString+=u'\"'+self.aTargets[uKey]+u'\",'
        uValueString=uValueString[1:-2]
        SetVar(uVarName = "VALUESTRING", oVarValue = uValueString)

    def GetConfigJSON(self):
        dRet = oInterFaceTelnet.cInterface.GetConfigJSON(self)
        dAdd = {"Source_DeviceType":      {"active": "enabled", "order": 10, "type": "scrolloptions",  "title": "Source Device Type",      "desc": "$lvar(6005)",  "section": "$var(InterfaceConfigSection)","key": "Source_DeviceType",           "default":"Recording 1", "options":["$var(VALUESTRING)"]},
                "Source_DeviceID":        {"active": "enabled", "order": 11, "type": "string",         "title": "Source Device ID",        "desc": "$lvar(6005)",  "section": "$var(InterfaceConfigSection)","key": "Source_DeviceID",             "default":"00000"       },
                "Destination_DeviceType": {"active": "enabled", "order": 12, "type": "scrolloptions",  "title": "Destination Device Type", "desc": "$lvar(6003)",  "section": "$var(InterfaceConfigSection)","key": "Destination_DeviceType",      "default":"TV", "options":["$var(VALUESTRING)"]}
              }

        dRet.update(dAdd)
        return dRet

