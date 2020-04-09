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

import ORCA.Globals as Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>Keyhandler Debugging</name>
      <description language='English'>Script to adding debugging fuctions on specific keys</description>
      <description language='German'>Script um debugging Funktionen auf einzelne Tasten zu legen</description>
      <author>Carsten Thielepape</author>
      <version>5.0.1</version>
      <minorcaversion>5.0.1</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/keyhandler/keyhandler_debug</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/keyhandler_debug.zip</sourcefile>
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
    WikiDoc:Page:Scripts-keyhandler_debug
    WikiDoc:TOCTitle:Script Key Debugger
    = Keyhandler for Debugging =

    This is a helper script to add debug functions to ORCA on specific keys. Normally not available in the final release
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
        super().__init__()
        self.uSubType           = u'DEBUG'
        self.uSortOrder         = u'last'
        self.uIniFileLocation   = u'none'

    def HandleKey(self,**kwargs) -> Dict:
        super().HandleKey(**kwargs)

        uKey:str   = kwargs.get("key",0)
        window     = kwargs.get("window",None)

        # On Windows: We emulate sleep and wake by F2 and F3
        if uKey ==  "F2":
            Globals.oApp.on_pause()
        elif uKey ==  "F3":
            Globals.oApp.on_resume()
        elif uKey ==  "F4":
            Globals.bShowBorders=not Globals.bShowBorders
            Globals.oTheScreen.AddActionToQueue(aActions=[{'string': 'updatewidget *@*'}])
        elif uKey == "F12" and window is not None:  # F12
            window.screenshot()
        elif uKey == "F11" and window is not None:  # F11
            window.rotation += 90
        return kwargs
