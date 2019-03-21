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

from kivy.logger import Logger
import ORCA.vars.Globals
import ORCA.Globals as Globals
from ORCA.utils.TypeConvert import ToDic

__all__ = ['VarHasLinks',
           'SetVarLink',
           'DelVarLink',
           'DelVarLinks',
           'DelAllVarLinks',
           'TriggerLinkActions'
           ]


def VarHasLinks(uVarName):
    """
    Returns if a variable has linked actions

    :rtype: bool
    :param string uVarName: The name of the variable
    :return: True if the variable has linked actions, otherwise False
    """

    return (ORCA.vars.Globals.dUserVarLinks.get(uVarName) is not None)

def SetVarLink(uVarName, oActions):
    """
    Sets a variable link, means something will be executed if the value of a variable changes. You can set multipe var links to one variable, but not duplicate var links. There will be no error or warning, if you try to add a duplicate valink, or the variable name does not exist

    :rtype: None
    :param string uVarName: The variable name, for which the var link should get added
    :param object oActions: The executable actions, which will be passed to the event handler. Either a string, which represents a dict, or a list of dicts (NOT Strings)
    """
    aLinkedObjects = ORCA.vars.Globals.dUserVarLinks.get(uVarName, [])
    if not oActions in aLinkedObjects:
        aLinkedObjects.append(oActions)
    ORCA.vars.Globals.dUserVarLinks[uVarName] = aLinkedObjects


def DelVarLink(uVarName, oActions):
    """
    Removes a variable link from a variable. There will be no error or warning, if you try to remove a valink, which has not been added

    :rtype: None
    :param string uVarName: The variable name, for which the var link should get removed
    :param oActions: The actions which has been used to set var link. If you provide a * , all var links will be removed (see DelVarLinks)
    """

    if oActions == "*":
        DelVarLinks(uVarName=uVarName)
        return

    aLinkedObjects = ORCA.vars.Globals.dUserVarLinks.get(uVarName)
    if aLinkedObjects is None:
        return
    if oActions in aLinkedObjects:
        aLinkedObjects.remove(oActions)
    ORCA.vars.Globals.dUserVarLinks[uVarName] = aLinkedObjects


def DelVarLinks(uVarName):
    """
    Removes all variable links from a variable.

    :rtype: None
    :param string uVarName: The variable name, for which the var links should get removed
    """

    aLinkedObjects = ORCA.vars.Globals.dUserVarLinks.get(uVarName)
    if aLinkedObjects is None:
        return
    ORCA.vars.Globals.dUserVarLinks[uVarName] = []


def DelAllVarLinks():
    """
    Removes all variable links from all variables

    :rtype: None
    """
    ORCA.vars.Globals.dUserVarLinks.clear()


def TriggerLinkActions(uVarName):
    """
    Executes all Actions given as a variable link to a variable. The actions will get excecuted immmediatly

    :rtype: None
    :param string uVarName: The variable name, for which the actions should get executed
    """
    aVarLinks = ORCA.vars.Globals.dUserVarLinks.get(uVarName, [])
    for uCmd in aVarLinks:
        Logger.debug(u'Call Triggered Var Link Actions for:' + uVarName)
        if isinstance(uCmd, list):
            Globals.oTheScreen.AddActionToQueue(aActions=uCmd,bNewQueue=True)
        else:
            Globals.oTheScreen.AddActionToQueue(aActions=[ToDic(uCmd)],bNewQueue=True)
