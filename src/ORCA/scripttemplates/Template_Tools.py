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

from typing import Dict
from typing import Union
from ORCA.scripts.BaseScript import cBaseScript
from ORCA.utils.FileName import cFileName

import ORCA.Globals as Globals

class cToolsTemplate(cBaseScript):
    """ template class for discover scripts """
    def __init__(self):
        cBaseScript.__init__(self)
        self.uType:str                      = u'TOOLS'
        self.iHash:int                      = 0
        self.oFnXML:Union[cFileName,None]   = None
        # self.aScriptSettingPlugins        = []

    def Init(self,uObjectName:str,oFnObject:Union[cFileName,str]=None) -> None:
        cBaseScript.Init(self,uObjectName,oFnObject)
        self.oFnXML     = cFileName(Globals.oScripts.dScriptPathList[self.uObjectName])+"script.xml"

    def RunScript(self, *args, **kwargs) -> Union[Dict,None]:
        """ main entry point to run the script """
        if 'register' in args or kwargs.get("caller")=="appstart":
            return self.Register(*args,**kwargs)
        elif "unregister" in args:
            return self.UnRegister(*args,**kwargs)
        return None

    def Register(self,*args,**kwargs) -> None:
        return None

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def UnRegister(self,*args,**kwargs) -> None:
        return None
