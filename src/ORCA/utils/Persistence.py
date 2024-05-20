# -*- coding: utf-8 -*-

"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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

from xml.etree.ElementTree  import Element
from xml.etree.ElementTree  import SubElement
from kivy.logger            import Logger

import ORCA.vars.Globals
from ORCA.Globals import Globals

from ORCA.utils.LogError                import LogError
from ORCA.utils.TypeConvert             import EscapeUnicode
from ORCA.utils.XML                     import LoadXMLFile
from ORCA.utils.XML                     import XMLPrettify
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.vars.Access                   import GetVar
from ORCA.vars.Access                   import SetVar

class cPersistence:

    def __init__(self):
        self.uCurrentPage:str = ''

    def Register(self):
        return
        if Globals.bPersistence_OnSleep:
            Globals.oNotifications.RegisterNotification(uNotification='on_pause',  fNotifyFunction=self.Write, uDescription='Write Persistence File (Sleep)')
        if Globals.bPersistence_OnPageStart:
            Globals.oNotifications.RegisterNotification(uNotification='on_showpage', fNotifyFunction=self.Write, uDescription='Write Persistence File (Page Start)')
        Globals.oNotifications.RegisterNotification(uNotification='on_stopapp', fNotifyFunction=self.Kill, uDescription='Delete Persistence File')
        Globals.oNotifications.RegisterNotification(uNotification='on_resume', fNotifyFunction=self.Kill, uDescription='Delete Persistence File')

    def Write(self,**kwargs) -> None:
        return
        try:

            oVal: Element
            uContent: str
            uRoot: str

            if GetVar(uVarName='CURRENTPAGE') == GetVar(uVarName='FIRSTPAGE'):
                self.Kill(Dummy=True)
                return

            Logger.debug("Write Persistence data [vars]")

            oXMLRoot: Element = Element('persistence')
            oVal = SubElement(oXMLRoot, 'version')
            oVal.text = '1.00'
            ORCA.vars.Globals.Vars_Persistence_WriteToXMLNode(oXMLNode=oXMLRoot)

            # for oEntry in self.aRepManagerEntries:
            #    Logger.debug(f'Saving Repository-Entry [{oEntry.oFnEntry}]')

            oFSFile     = open(Globals.oFnPersistence.string, 'w')
            uContent    = XMLPrettify(oElem=oXMLRoot)
            oFSFile.write(uContent)
            oFSFile.close()

        except Exception as e:
            LogError(uMsg="Failed to write persistence data",oException=e)

    def Kill(self,**kwargs) -> None:
        Globals.oFnPersistence.Delete()

    def Read(self) -> None:
        return
        try:
            Logger.debug('Read Persistence data [vars]')
            oXMLRoot: Element = LoadXMLFile(oFile=Globals.oFnPersistence)
            ORCA.vars.Globals.Vars_Persistence_ReadFromXMLNode(oXMLNode=oXMLRoot)
            SetVar(uVarName='PERSISTENCESTARTPAGE',oVarValue=GetVar(uVarName='CURRENTPAGE'))
        except Exception as e:
            LogError(uMsg="Failed to read persistence data",oException=e)

    def HasOldSession(self) -> bool:
        return False
        return Globals.oFnPersistence.Exists()
