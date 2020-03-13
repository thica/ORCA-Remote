# -*- coding: utf-8 -*-
# Generic Base Interface for Infrared based interfaces. Handles loading and convertion of IR Codes

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

from typing import List
from typing import Union

from ORCA.interfaces.BaseInterface          import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings  import cBaseInterFaceSettings
from ORCA.Action                            import cAction
from ORCA.utils.FileName                    import cFileName

'''
<root>
  <repositorymanager>
    <entry>
      <name>Generic Infrared Interface</name>
      <description language='English'>Base Interface Class for Infrared based Interfaces</description>
      <description language='German'>Basis Schnittstelle für Infrarot Schnittstellen</description>
      <author>Carsten Thielepape</author>
      <version>5.0.0</version>
      <minorcaversion>5.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/generic_infrared</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/generic_infrared.zip</sourcefile>
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

    class cInterFaceSettings(cBaseInterFaceSettings):

        def __init__(self,oInterFace:cBaseInterFace):
            super().__init__(oInterFace)

        def ReadAction(self,oAction:cAction) -> None:
            super().ReadAction(oAction)
            oAction.uCCF_Code    = oAction.dActionPars.get(u'cmd_ccf',u'')
            oAction.uRepeatCount = oAction.dActionPars.get(u'repeatcount',u'´1')

    def GetConfigCodesetList(self)  -> List[str]:
        aRet:List[str]=super().GetConfigCodesetList()
        # adjust the codeset path to load infrared generic formats
        uTmpName:str=self.uObjectName
        self.uObjectName="infrared_ccf"
        aRet+=super().GetConfigCodesetList()
        self.uObjectName=uTmpName
        return aRet

    def FindCodesetFile(self, uFNCodeset:str) -> Union[cFileName,None]:

        uRet: Union[cFileName, None]
        uRet = super().FindCodesetFile(uFNCodeset)

        if uRet is None:
            uTmpName=self.uObjectName
            self.uObjectName="infrared_ccf"
            uRet = super().FindCodesetFile(uFNCodeset)
            self.uObjectName=uTmpName
        return uRet
