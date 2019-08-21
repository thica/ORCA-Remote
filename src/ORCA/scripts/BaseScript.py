# -*- coding: utf-8 -*-

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

from kivy.logger                      import Logger

from ORCA.BaseObject                  import cBaseObject
from ORCA.scripts.ScriptConfig        import cScriptConfig
from ORCA.scripts.BaseScriptSettings  import cBaseScriptSettings
from ORCA.utils.FileName              import cFileName
from ORCA.utils.ParseResult           import cResultParser
from ORCA.utils.XML                   import Orca_FromString
from ORCA.utils.CachedFile            import CachedFile

import ORCA.Globals as Globals

class cScriptResultParser(cResultParser):
    """ Resultparser object for Scripts  """
    def __init__(self,oScript):
        super(cScriptResultParser, self).__init__()
        self.oScript        = oScript
        self.uObjectName    = oScript.uObjectName
        self.uDebugContext  = "Script: % s :" % self.uObjectName
        self.uContext       = self.uObjectName

class cBaseScript(cBaseObject):
    """ basic script class to inherit all scripts from """

    class cScriptSettings(cBaseScriptSettings):
        """ Needs to be implemented by main script class """
        pass

    def __init__(self):

        """
        sortorder

        auto                = unspecified
        first               = begin of list in type
        last                = end of list in type
        before:scriptname   = before given script name
        after:scriptname   = after given script name

        on Logical conficts result is unspecified

        """

        super(cBaseScript,self).__init__()

        self.oFnConfig              = None
        self.oFnObject              = None
        self.oObjectConfig          = None
        self.uConfigName            = "SCRIPTDEFAULT"
        self.uSection               = u''
        self.oFnAction              = None
        self.uObjectType            = "script"

        self.uSortOrder             = u'auto'
        self.uSubType               = u'Generic'
        self.uType                  = u'Generic'
        self.uIniFileLocation       = "global"
        self.oResultParser          = None

    def Init(self,uObjectName,oFnObject=None):
        """ Initializes the script """
        super(cBaseScript, self).Init(uObjectName,oFnObject)

        self.oResultParser        = cScriptResultParser(self)
        self.oFnAction            = cFileName(self.oPathMyCode+"actions")+"customactions.xml"
        self.oObjectConfig        = cScriptConfig(self)
        self.oObjectConfig.Init()

    def RunScript(self, *args, **kwargs):
        """ Dummy """
        pass

    def ShowSettings(self):
        """  shows the settings dialog """
        Globals.oTheScreen.AddActionToQueue([{'string':'updatewidget','widgetname':'Scriptsettings'}])

    def LoadActions(self):
        """ parses the definition specific actions """
        Logger.info (u'Loading Actions for script:'+self.uObjectName)
        if self.oFnAction.Exists():
            sET_Data = CachedFile(self.oFnAction)
            oET_Root = Orca_FromString(sET_Data, None, self.oFnAction.string)
            Globals.oActions.LoadActionsSub(oET_Root,u'actions',         u'action',          Globals.oActions.dActionsCommands,  self.oFnAction.string)

    def GetNewSettingObject(self):
        return self.cScriptSettings(self)

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults):
        """ Base class """
        return {}

