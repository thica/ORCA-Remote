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

from typing import List
from kivy.logger import Logger
import ORCA.vars.Globals
from ORCA.Globals import Globals
from ORCA.utils.TypeConvert import ToDic
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.vars.Globals import cLinkPar

oLinkPar:cLinkPar=''

__all__ = ['VarHasLinks',
           'SetVarLink',
           'DelVarLink',
           'DelVarLinks',
           'DelAllVarLinks',
           'TriggerLinkActions'
           ]


def VarHasLinks(uVarName:str) -> bool:
    """
    Returns if a variable has linked actions

    :param str uVarName: The name of the variable
    :return: True if the variable has linked actions, otherwise False
    """
    return ORCA.vars.Globals.dUserVarLinks.get(uVarName) is not None

def SetVarLink(uVarName:str, oActions:cLinkPar) -> None:
    """
    Sets a variable link, means something will be executed if the value of a variable changes. You can set multiple var links to one variable, but not duplicate var links. There will be no error or warning, if you try to add a duplicate valink, or the variable name does not exist

    :param str uVarName: The variable name, for which the var link should get added
    :param object oActions: The executable actions, which will be passed to the event handler. Either a string, which represents a dict, or a list of dicts (NOT Strings)
    """
    aLinkedObjects:List[cLinkPar] = ORCA.vars.Globals.dUserVarLinks.get(uVarName, [])
    if not oActions in aLinkedObjects:
        aLinkedObjects.append(oActions)
    ORCA.vars.Globals.dUserVarLinks[uVarName] = aLinkedObjects


def DelVarLink(uVarName:str, oActions:cLinkPar) -> None:
    """
    Removes a variable link from a variable. There will be no error or warning, if you try to remove a valink, which has not been added

    :param str uVarName: The variable name, for which the var link should get removed
    :param oActions: The actions which has been used to set var link. If you provide a * , all var links will be removed (see DelVarLinks)
    """

    if oActions == '*':
        DelVarLinks(uVarName=uVarName)
        return

    aLinkedObjects:List[cLinkPar] = ORCA.vars.Globals.dUserVarLinks.get(uVarName)
    if aLinkedObjects is None:
        return
    if oActions in aLinkedObjects:
        aLinkedObjects.remove(oActions)
    ORCA.vars.Globals.dUserVarLinks[uVarName] = aLinkedObjects

def DelVarLinks(uVarName:str) -> None:
    """
    Removes all variable links from a variable.

    :param str uVarName: The variable name, for which the var links should get removed
    """

    aLinkedObjects:List[cLinkPar] = ORCA.vars.Globals.dUserVarLinks.get(uVarName)
    if aLinkedObjects is None:
        return
    ORCA.vars.Globals.dUserVarLinks[uVarName] = []


def DelAllVarLinks() -> None:
    """
    Removes all variable links from all variables

    """
    ORCA.vars.Globals.dUserVarLinks.clear()

def TriggerLinkActions(uVarName:str) -> None:
    """
    Executes all Actions given as a variable link to a variable. The actions will get executed immediately
    :param str uVarName: The variable name, for which the actions should get executed
    """
    aVarLinks:cLinkPar = ORCA.vars.Globals.dUserVarLinks.get(uVarName, [])

    if len(aVarLinks)==0:
        return
    if isinstance(aVarLinks, list):
        aCmds:List = []
        for uCmd in aVarLinks:
            Logger.debug(f'Call Triggered Var Link Actions for: {uVarName} -> {ToUnicode(uCmd)}')
            if isinstance(uCmd, list):
                # Globals.oTheScreen.AddActionToQueue(aActions=uCmd, bNewQueue=True)
                aCmds = aCmds+uCmd
            else:
                # Globals.oTheScreen.AddActionToQueue(aActions=[ToDic(uCmd)], bNewQueue=True)
                aCmds.append(ToDic(uCmd))
        Globals.oTheScreen.AddActionToQueue(aActions=aCmds, bNewQueue=True)
    else:
        Globals.oTheScreen.AddActionToQueue(aActions=[ToDic(aVarLinks)], bNewQueue=True)

    """
    for uCmd in aVarLinks:
        Logger.debug('Call Triggered Var Link Actions for:' + uVarName)
        if isinstance(uCmd, list):
            Globals.oTheScreen.AddActionToQueue(aActions=uCmd,bNewQueue=True)
        else:
            Globals.oTheScreen.AddActionToQueue(aActions=[ToDic(uCmd)],bNewQueue=True)
    """
