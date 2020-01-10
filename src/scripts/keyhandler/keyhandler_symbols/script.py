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

from typing import Dict
from ORCA.scripttemplates.Template_Keyhandler import cKeyhandlerTemplate

'''
<root>
  <repositorymanager>
    <entry>
      <name>Keyhandler Symbols</name>
      <description language='English'>Script to translate keycodes to symbolic names</description>
      <description language='German'>Script keycodes in symbolische Namen to ändern </description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/keyhandler/keyhandler_symbols</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/keyhandler_symbols.zip</sourcefile>
          <targetpath>scripts/keyhandler</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cScript(cKeyhandlerTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-keyhandler_symbols
    WikiDoc:TOCTitle:Script Key Symbols
    = Script to translate keycodes to symbolic names =

    Core script to translate keycodes to symbolic names
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |cmd_type
    |The requested helper function: Only "Register" od "UnRegister"
    |}</div>

    WikiDoc:End
    """

    def __init__(self):
        cKeyhandlerTemplate.__init__(self)
        self.uSubType           = u'SYSTEM'
        self.uSortOrder         = u'first'
        self.uIniFileLocation   = u'none'

        #this might get adjusted fo different platforms
        self.dTranslation:Dict = {   "27": "ESC",
                                    "282": "F1",
                                    "283": "F2",
                                    "284": "F3",
                                    "285": "F4",
                                    "286": "F5",
                                    "287": "F6",
                                    "288": "F7",
                                    "289": "F8",
                                    "290": "F9",
                                    "291": "F10",
                                    "292": "F11",
                                    "293": "F12"
                                }

    def HandleKey(self,**kwargs) -> Dict:
        cKeyhandlerTemplate.HandleKey(self, **kwargs)

        uKey:str     = kwargs.get("key",0)
        uKeyNew:str = self.dTranslation.get(uKey,uKey)
        return {"key":uKeyNew}
