# -*- coding: utf-8 -*-
# Generic Base Interface for Infrared based interfaces. Handles loading and convertion of IR Codes

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
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings

'''
<root>
  <repositorymanager>
    <entry>
      <name>Generic Infrared Interface</name>
      <description language='English'>Base Interface Class for Infrared based Interfaces</description>
      <description language='German'>Basis Schnittstelle für Infrarot Schnittstellen</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/generic_infrared</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/generic_infrared.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>generic_infrared/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):

        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)

        def ReadAction(self,oAction):
            cBaseInterFaceSettings.ReadAction(self,oAction)
            oAction.uCCF_Code    = oAction.dActionPars.get(u'cmd_ccf',u'')
            oAction.uRepeatCount = oAction.dActionPars.get(u'repeatcount',u'´1')

    def GetConfigCodesetList(self):
        aRet=cBaseInterFace.GetConfigCodesetList(self)
        # adjust the codeset path to load infrared generic formats
        uTmpName=self.uInterFaceName
        self.uInterFaceName="infrared_ccf"
        aRet+=cBaseInterFace.GetConfigCodesetList(self)
        self.uInterFaceName=uTmpName
        return aRet


    def FindCodesetFile(self, uFNCodeset):
        uRet = cBaseInterFace.FindCodesetFile(self,uFNCodeset)
        if uRet:
            return uRet
        uTmpName=self.uInterFaceName
        self.uInterFaceName="infrared_ccf"
        uRet = cBaseInterFace.FindCodesetFile(self,uFNCodeset)
        self.uInterFaceName=uTmpName
        return uRet
