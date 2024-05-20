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

from __future__ import annotations
from typing     import Union
from typing     import Dict
from xml.etree.ElementTree            import Element
from abc        import ABC
from abc        import abstractmethod
from kivy.logger                      import Logger

from ORCA.settings.BaseObject import cBaseObject
from ORCA.scripts.ScriptConfig        import cScriptConfig
from ORCA.scripts.BaseScriptSettings  import cBaseScriptSettings
from ORCA.utils.FileName              import cFileName
from ORCA.utils.ParseResult           import cResultParser
from ORCA.utils.XML                   import Orca_FromString
from ORCA.utils.CachedFile            import CachedFile

from ORCA.Globals import Globals

class cScriptResultParser(cResultParser):
    """ Resultparser object for Scripts  """
    def __init__(self,oScript:cBaseScript):
        super().__init__()
        self.oScript:cBaseScript  = oScript
        self.uObjectName:str      = oScript.uObjectName
        self.uDebugContext        = f'Script: {self.uObjectName} :'
        self.uContext             = self.uObjectName

class cBaseScript(cBaseObject,ABC):
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

        super().__init__()

        # self.oFnConfig                            = None
        self.uConfigName                            = 'SCRIPTDEFAULT'
        self.uObjectType                            = 'script'
        self.uIniFileLocation                       = 'global'

        self.uSection:str                           = ''
        self.oFnAction:Union[cFileName,None]        = None
        self.uSortOrder:str                         = 'auto'
        self.uSubType:str                           = 'Generic'
        self.uType:str                              = 'Generic'
        self.oResultParser:cScriptResultParser      = cScriptResultParser(self)

    def Init(self,uObjectName:str,oFnObject:Union[cFileName,None]=None) -> None:
        """ Initializes the script """
        super().Init(uObjectName,oFnObject)
        self.oFnAction            = cFileName(self.oPathMyCode+'actions')+'customactions.xml'
        self.oObjectConfig        = cScriptConfig(self)
        self.oObjectConfig.Init()

    @abstractmethod
    def RunScript(self, *args, **kwargs) -> Union[Dict,None]:
        """ Dummy """
        return {}


    # noinspection PyMethodMayBeStatic
    def ShowSettings(self) -> None:
        """  shows the settings dialog """
        Globals.oTheScreen.AddActionToQueue(aActions=[{'string':'updatewidget','widgetname':'Scriptsettings'}])

    def LoadActions(self) -> None:
        """ parses the definition specific actions """
        Logger.info ('Loading Actions for script:'+self.uObjectName)
        if self.oFnAction.Exists():
            uET_Data = CachedFile(oFileName=self.oFnAction)
            oET_Root:Element = Orca_FromString(uET_Data=uET_Data, oDef=None, uFileName=str(self.oFnAction))
            Globals.oActions.LoadActionsSub(oET_Root=oET_Root,uSegmentTag='actions',uListTag='action',dTargetDic=Globals.oActions.dActionsCommands,uFileName=str(self.oFnAction))

    def GetNewSettingObject(self) -> cBaseScriptSettings:
        return self.cScriptSettings(self)

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults) -> Dict[str,Dict]:
        """ Base class """
        return {}

