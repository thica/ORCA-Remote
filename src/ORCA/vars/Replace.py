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

from typing import Dict
import re

from kivy.logger                import Logger
from ORCA.utils.LogError        import LogError
from ORCA.utils.TypeConvert     import ToUnicode
from ORCA.Globals import Globals
import ORCA.vars.Globals

__all__ = ['ReplaceDefVars',
           'ReplaceVars'
          ]

rPatternVar     = r"\$var\(([\w\s\[\]\-\+_]+)\)"
rPatternLVar    = r"\$lvar\(([\w\s\[\]\-\+_]+)\)"
rPatternCVar    = r"\$cvar\(([\w\s\[\]\-\+_]+)\)"
rPatternDefVar  = r"\$dvar\(([\w\s\[\]\-\+_]+)\)"



def _VarDefReplace(oMatch) -> str:
    """
    Internal Helper function used by the regex function to parse the definition variable name and returns its value

    :param re.Match Object oMatch: The regex match pattern
    :return: The definition var with the given var name
    """

    uNumber:str = oMatch.string[oMatch.regs[1][0]:oMatch.regs[1][1]]
    uReturn:str = ORCA.vars.Globals.dDefVars.get(uNumber)
    if uReturn is None:
        uReturn = oMatch.string[oMatch.regs[0][0]:oMatch.regs[0][1]]
        Logger.error(f'Vars: ReplaceDefVars: Var not found: [{uNumber}] in [{ToUnicode(oMatch.string)}]')  # DumpDefinitionVars(this.dDefVars)
    uReturn = str(uReturn)
    return uReturn


def _VarReplace(oMatch) -> str:
    """
    Internal Helper function used by the regex function to parse the user variable name and returns its value

    :param re.Match Object oMatch: The regex match pattern
    :return: The user var with the given var name
    """

    uNumber:str = oMatch.string[oMatch.regs[1][0]:oMatch.regs[1][1]]
    uReturn:str = ORCA.vars.Globals.dUserVars.get(uNumber)
    if uReturn is None:
        uReturn = oMatch.string[oMatch.regs[0][0]:oMatch.regs[0][1]]
        Logger.warning('Vars: ReplaceVars: Var not found:' + uNumber)
    return uReturn


def _LanguageVarReplace(oMatch) -> str:
    """
    Internal Helper function used by the regex function to parse the language variable name and returns its value

    :param re.Match Object oMatch: The regex match pattern
    :return: The language var with the given var name
    """

    uNumber = oMatch.string[oMatch.regs[1][0]:oMatch.regs[1][1]]
    return Globals.oLanguage.StringIDToString(uNumber)

def _ContextVarReplace(oMatch) -> str:
    """
    Internal Helper function used by the regex function to parse the variable name for a specific context and returns its value

    :param re.Match Object oMatch: The regex match pattern
    :return: The user var with the given var name in the context
    """
    uNumber = oMatch.string[oMatch.regs[1][0]:oMatch.regs[1][1]]
    return ORCA.vars.Globals.dUserVars.get(ORCA.vars.Globals.uRepContext + uNumber)


def ReplaceDefVars(uOrgIn:str, dArray:Dict[str,str]) -> str:
    """
    Replaces all occurences of $dvar(xxx) with the definition vars, with name xxx.
    Multiple var placeholder can be given in on string in any combination.
    Nested var placeholder "$dvar($dvar(xxx)) are not allowed.
    A warning will be given if the variable name xxx does not exist

    :param str uOrgIn: The string, where the variable placeholer should be replaced
    :param dict dArray: A dict of definition vars, which should be used for the replacement
    :return: The string with replaced variables or the orginal string, if not variables are defined
    """

    ORCA.vars.Globals.dDefVars = dArray
    return re.sub(rPatternDefVar, _VarDefReplace, uOrgIn)


def ReplaceVars(uOrgIn:str, uContext:str='') -> str:
    """
    Replaces all occurences of $var(xxx) and $lvar(lll) with the uservars or language vars, with name xxx/lll.
    Multiple var placeholder can be given in on string in any combination.
    Nested var placeholder "$var($var(xxx)) are not allowed.
    A warning will be given if the variable name does not exist

    :param str uOrgIn: The string, where the variable placeholer should be replaced
    :param str uContext: The context for the var, default empty. This should be the same context as given in SetVar
    :return: The string with replaced variables or the orginal string, if not variables are defined
    """
    uTmp:str = ''

    if uOrgIn is None:
        return ''

    try:
        uTmp = re.sub(rPatternVar, _VarReplace, uOrgIn)
        uTmp = re.sub(rPatternLVar, _LanguageVarReplace, uTmp)
        if uContext != '':
            ORCA.vars.Globals.uRepContext = uContext
            uTmp = re.sub(rPatternCVar, _ContextVarReplace, uOrgIn)

    except Exception as e:
        if '$var(' in uOrgIn or '$lvar(' in uOrgIn:
            LogError(uMsg=f'Vars: ReplaceVars: Runtime Error: {ToUnicode(uOrgIn)} ', oException=e)
        else:
            uTmp = uOrgIn

    return uTmp
