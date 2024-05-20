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

from ORCA.vars.Access import SetVar
from ORCA.definition.DefinitionPathes import cDefinitionPathes
from ORCA.Globals import Globals

__all__ = ['SetDefinitionPathes',
           'SetDefinitionContext',
           'RestoreDefinitionContext'
           ]

def SetDefinitionPathes(*,uDefinitionName:str, uDefinitionPathName:str='') -> None:
    """
    Sets the definition path's to a specific definition
    """
    if not uDefinitionName in Globals.dDefinitionPathes:
        oDefinitionPathes:cDefinitionPathes = cDefinitionPathes(uDefinitionName=uDefinitionName, uDefinitionPathName=uDefinitionPathName)
        Globals.dDefinitionPathes[uDefinitionName] = oDefinitionPathes

    Globals.oDefinitionPathes = Globals.dDefinitionPathes[uDefinitionName]

    SetVar(uVarName='DEFINITIONPATH',                  oVarValue=str(Globals.oDefinitionPathes.oPathDefinition))
    SetVar(uVarName='DEFINITIONFILENAME',              oVarValue=str(Globals.oDefinitionPathes.oFnDefinition))
    SetVar(uVarName='DEFINITIONNAME',                  oVarValue=Globals.uDefinitionName)
    SetVar(uVarName='DEFINITIONPATHSKINELEMENTS',      oVarValue=str(Globals.oDefinitionPathes.oPathDefinitionSkinElements))
    return None

def SetDefinitionContext(*,uDefinitionName:str, uDefinitionPathName:str='') -> None:
    """
    Changes the context (mainly the the definition pathes) to a specific definition
    """
    if Globals.uDefinitionContext != uDefinitionName:
        Globals.uDefinitionContext = uDefinitionName
        SetDefinitionPathes(uDefinitionName=uDefinitionName, uDefinitionPathName=uDefinitionPathName)
    return None

def RestoreDefinitionContext() -> None:
    """
    Restores the context (mainly the the definition pathes) to the main definition
    """
    SetDefinitionContext(uDefinitionName=Globals.uDefinitionName)
    return None
