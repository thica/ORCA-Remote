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

from ORCA.vars.Access import SetVar
from ORCA.definition.DefinitionPathes import cDefinitionPathes
import ORCA.Globals as Globals

__all__ = ['SetDefinitionPathes',
           'SetDefinitionContext',
           'RestoreDefinitionContext'
           ]

def SetDefinitionPathes(uDefinitionName, uDefinitionPathName=u''):
    """
    Sets the definition pathes to a specific definition
    """
    if not uDefinitionName in Globals.dDefinitionPathes:
        oDefinitionPathes = cDefinitionPathes(uDefinitionName, uDefinitionPathName)
        Globals.dDefinitionPathes[uDefinitionName] = oDefinitionPathes

    Globals.oDefinitionPathes = Globals.dDefinitionPathes[uDefinitionName]

    SetVar(uVarName=u'DEFINITIONPATH',                  oVarValue=Globals.oDefinitionPathes.oPathDefinition.string)
    SetVar(uVarName=u'DEFINITIONFILENAME',              oVarValue=Globals.oDefinitionPathes.oFnDefinition.string)
    SetVar(uVarName=u'DEFINITIONNAME',                  oVarValue=Globals.uDefinitionName)
    SetVar(uVarName=u'DEFINITIONPATHSKINELEMENTS',      oVarValue=Globals.oDefinitionPathes.oPathDefinitionSkinElements.string)


def SetDefinitionContext(uDefinitionName, uDefinitionPathName=u''):
    """
    Changes the context (mainly the the definition pathes) to a specific definition
    """
    if Globals.uDefinitionContext != uDefinitionName:
        Globals.uDefinitionContext = uDefinitionName
        SetDefinitionPathes(uDefinitionName, uDefinitionPathName)


def RestoreDefinitionContext():
    """
    Restores the context (mainly the the definition pathes) to the main definition
    """

    SetDefinitionContext(Globals.uDefinitionName)
