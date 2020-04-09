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

import logging
import time

from kivy.logger  import Logger
from ORCA.scripttemplates.Template_System import cSystemTemplate

'''
<root>
  <repositorymanager>
    <entry>
      <name>System Debug Logger</name>
      <description language='English'>Script to add timestamps to the logfile</description>
      <description language='German'>Script um einen Zeitstempel zum Logfile hinzuzufügen</description>
      <author>Carsten Thielepape</author>
      <version>5.0.1</version>
      <minorcaversion>5.0.1</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/system/system_debuglogger</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/system_debuglogger.zip</sourcefile>
          <targetpath>scripts/system</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class LoggerPatch:
    """ Patches the logger to add timestamp """
    def __init__(self):

        self.emit_org = None
        # we create a formatter object once to avoid
        # inialisation on every log line
        self.oFormatter=logging.Formatter(None)

        # we just need to patch the first Handler
        # as we change the message itself
        oHandler = Logger.handlers[0]
        self.emit_org=oHandler.emit
        oHandler.emit=self.emit


    def emit(self,record) -> None:
        """ we do not use the formatter by purpose as it runs on failure
        if the message string contains format characters   """

        try:
            ct = self.oFormatter.converter(record.created)
            t:str       = time.strftime("%Y-%m-%d %H|%M|%S", ct)
            s:str       = u"%s.%03d: " % (t, record.msecs)
            msg:str     = record.msg
            if len(msg)>500:
                if not "Traceback (most recent call last)" in msg:
                    record.msg=msg[:500]+u"..."

            # record.msg = s+str(record.msg.encode('ascii', 'ignore'))
            record.msg = s + record.msg
            self.emit_org(record)
        except Exception:
            pass


class cScript(cSystemTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-system_debuglogger
    WikiDoc:TOCTitle:Script System Debuglogger
    = System Debugging extension for Logfiles=

    This is a helper script to add debug information to the ORCA logfiles. Normally not available in the final release
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
        self.oLoggerPatch       = None
        self.uIniFileLocation   = 'none'

    def Register(self,*args,**kwargs) -> None:
        if Logger.level == logging.DEBUG:
            self.oLoggerPatch = LoggerPatch()

