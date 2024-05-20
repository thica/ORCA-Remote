# -*- coding: utf-8 -*-
#

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

from typing import Dict
from typing import Union
from typing import Any

from ORCA.ui.ShowErrorPopUp     import ShowErrorPopUp
from ORCA.utils.FileName        import cFileName
from ORCA.utils.LogError        import LogError

# noinspection PyDeprecation
import imp


class cModule:
    def __init__(self,oModule):
        self.__oModule = oModule
    def GetClass(self,uClassName:str) -> Any:
        if self.__oModule is not None:
            return getattr(self.__oModule,uClassName,None)
        else:
            return None
    def GetModule(self):
        return self.__oModule

class cModuleLoader:
    def __init__(self):
        self.dModules:Dict[str,cModule] = {}
    def LoadModule(self,*, oFnModule:cFileName, uModuleName:str) -> Union[cModule,None]:

        if uModuleName in self.dModules:
            return self.dModules[uModuleName]
        try:
            # noinspection PyDeprecation
            oModule                    = imp.load_source(uModuleName, str(oFnModule))
            self.dModules[uModuleName] = cModule(oModule)
            return self.dModules[uModuleName]
        except Exception as e:
            uMsg: str = LogError(uMsg=f'ModulLoader: Fatal Error loading module {uModuleName} from file: {oFnModule}', oException=e)
            ShowErrorPopUp(uMessage=uMsg)
            return None

