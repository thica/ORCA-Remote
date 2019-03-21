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

from kivy.compat            import string_types
from ORCA.vars.Links        import TriggerLinkActions
from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.TypeConvert import ToUnicode
import ORCA.vars.Globals
import ORCA.Globals         as Globals

__all__ = ['DelVar',
           'GetVar',
           'SetDefVar',
           'SetVar',
           'ExistLVar',
           'ExistVar',
           'SetVarWithOutVarTranslation'
          ]

def _SetVarSub(uVarName, oVarValue):
    """
    Sub Routine to set a value to a variable. internal use only. Triggers will be executed on a change

    :rtype: None
    :param string uVarName: Variable name to use
    :param object oVarValue: Value to set, usually a unicode string, can be any other object
    """
    NewValue = oVarValue
    OldValue = ORCA.vars.Globals.dUserVars.get(uVarName)
    ORCA.vars.Globals.dUserVars[uVarName] = NewValue
    if OldValue != NewValue:
        TriggerLinkActions(uVarName=uVarName)

def SetDefVar(uVarName, uVarValue, dArray):
    """
    Sets a definition variable

    :rtype: None
    :param string uVarName: The name of the definition variable
    :param string uVarValue: The value for the definition variable
    :param dict dArray: The array which holds all definition vars for this context
    """
    dArray[uVarName] = uVarValue

def SetVar(uVarName, oVarValue, uContext=u''):
    """
    Sets a specific variable with a given value.

    :rtype: None
    :param string uVarName: Variable name to use. This can be a variable as well
    :param object oVarValue: Value to set, usually a unicode string, can be any other object.
    If you pass a dict, then for each dict member a varname with its value will get assigned (the dict member names will be separed by an underscore)
    If you pass a list or tuple, then for each list member a varname with its value will get assigned as a array [x] where x starts with 0)
    :param string uContext: The context for the variable. Internally the context will be added as a prefix to the variable name
    """

    SetVarWithOutVarTranslation(ReplaceVars(uVarName), oVarValue, uContext)

def SetVarWithOutVarTranslation(uVarName, oVarValue, uContext=u''):
    """
    Sets a specific variable with a given value.

    :rtype: None
    :param string uVarName: Variable name to use. This can't be a variable
    :param object oVarValue: Value to set, usually a unicode string, can be any other object.
    If you pass a dict, then for each dict member a varname with its value will get assigned (the dict member names will be separed by an underscore)
    If you pass a list or tuple, then for each list member a varname with its value will get assigned as a array [x] where x starts with 0)
    :param string uContext: The context for the variable. Internally the context will be added as a prefix to the variable name
    """

    uRealVarName = uContext + uVarName

    if isinstance(oVarValue, string_types):
        _SetVarSub(uVarName = uRealVarName, oVarValue = oVarValue)
        return

    if type(oVarValue) == dict:
        for uKey in oVarValue:
            _SetVarSub(uVarName = uRealVarName + u'_' + uKey, oVarValue = oVarValue[uKey])
        return

    if type(oVarValue) == list or type(oVarValue) == tuple:
        i = 0
        for uValue in oVarValue:
            _SetVarSub(uVarName = uRealVarName + u'_[' + ToUnicode(i)+u']', oVarValue = oVarValue[uValue])
            i += 1
        return
    _SetVarSub(uVarName = uRealVarName, oVarValue = oVarValue)


def DelVar(uVarName, uContext=u''):
    """
    Deletes a variable from the internal storage. This will not trigger a var link action by purpose. No error of warning is raised if the var does not exist

    :rtype: None
    :param string uVarName: The variable, which should be deleted
    :param string uContext: The context for the variable. Internally the context will be added as a prefix to the variable name
    """

    dDestArray = ORCA.vars.Globals.dUserVars
    if uContext + uVarName in dDestArray:
        del dDestArray[uContext + uVarName]


def GetVar(uVarName, uContext=u''):
    """
    Returns the value of a variable. Returns an empty string, if the variable does not exist

    :rtype: string, object
    :param string uVarName: The variable name from where the value should get returned. Can a variable name itself
    :param string uContext: The context for the variable. Internally the context will be added as a prefix to the variable name
    :return: The variable value assigned to the variable. Usually a string, but can be an object as well
    """
    return ORCA.vars.Globals.dUserVars.get(uContext + ReplaceVars(uVarName),u'')

def ExistLVar(uVarName):
    """
    Checks, if a language Var exists

    :rtype: bool
    :param string uVarName: The language variable name to check
    :return: True/False, depends of the language var exists
    """

    return Globals.oLanguage.dIDToString.get(uVarName) is not None


def ExistVar(uVarName,  uContext=u''):
    """
    Checks, if a Var exists

    :rtype: bool
    :param string uVarName: The variable name to check
    :param string uContext: The context for the variable. Internally the context will be added as a prefix to the variable name
    :return: True/False, depends of the var exists
    """

    return ORCA.vars.Globals.dUserVars.get(uContext + ReplaceVars(uVarName)) is not None
