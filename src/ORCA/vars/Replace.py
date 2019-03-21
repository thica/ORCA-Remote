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
import re

from kivy.logger                import Logger
from ORCA.utils.LogError        import LogError
from ORCA.utils.TypeConvert     import ToUnicode
import ORCA.Globals as Globals
import ORCA.vars.Globals

__all__ = ['ReplaceDefVars',
           'ReplaceVars'
          ]

rPatternVar     = r"\$var\(([\w\s\[\]\-\+_]+)\)"
rPatternLVar    = r"\$lvar\(([\w\s\[\]\-\+_]+)\)"
rPatternCVar    = r"\$cvar\(([\w\s\[\]\-\+_]+)\)"
rPatternDefVar  = r"\$dvar\(([\w\s\[\]\-\+_]+)\)"


def _VarDefReplace(oMatch):
    """
    Internal Helper function used by the regex function to parse the definition variable name and returns its value

    :param re.MatchObject oMatch: The regex match pattern
    :return: The definiton var with the given var name
    """

    # on Py27 elemtree cant deal with unicode
    # so we need to have all on string
    number = oMatch.string[oMatch.regs[1][0]:oMatch.regs[1][1]]
    uReturn = ORCA.vars.Globals.dDefVars.get(number)
    if uReturn is None:
        uReturn = oMatch.string[oMatch.regs[0][0]:oMatch.regs[0][1]]
        Logger.error(u'Vars: ReplaceDefVars: Var not found: [%s] in \n [%s]' % (number, ToUnicode(oMatch.string)))  # DumpDefinitionVars(this.dDefVars)

    uReturn = str(uReturn)
    return uReturn


def _VarReplace(oMatch):
    """
    Internal Helper function used by the regex function to parse the user variable name and returns its value

    :param re.MatchObject oMatch: The regex match pattern
    :return: The user var with the given var name
    """

    number = oMatch.string[oMatch.regs[1][0]:oMatch.regs[1][1]]
    uReturn = ORCA.vars.Globals.dUserVars.get(number)
    if uReturn is None:
        uReturn = oMatch.string[oMatch.regs[0][0]:oMatch.regs[0][1]]
        Logger.warning(u'Vars: ReplaceVars: Var not found:' + number)
    return uReturn


def _LanguageVarReplace(oMatch):
    """
    Internal Helper function used by the regex function to parse the language variable name and returns its value

    :param re.MatchObject oMatch: The regex match pattern
    :return: The language var with the given var name
    """

    number = oMatch.string[oMatch.regs[1][0]:oMatch.regs[1][1]]
    return Globals.oLanguage.StringIDToString(number)

def _ContextVarReplace(oMatch):
    """
    Internal Helper function used by the regex function to parse the variable name for a specific context and returns its value

    :param re.MatchObject oMatch: The regex match pattern
    :return: The user var with the given var name in the context
    """
    number = oMatch.string[oMatch.regs[1][0]:oMatch.regs[1][1]]
    return ORCA.vars.Globals.dUserVars.get(ORCA.vars.Globals.uRepContext + number)


def ReplaceDefVars(uOrgIn, aArray):
    """
    Replaces all occurences of $dvar(xxx) with the definition vars, with name xxx.
    Multiple var placeholder can be given in on string in any combination.
    Nested var placeholder "$dvar($dvar(xxx)) are not allowed.
    A warning will be given if the variable name xxx does not exist

    :rtype: string
    :param string uOrgIn: The string, where the variable placeholer should be replaced
    :param dict aArray: A dict of definition vars, which should be used for the replacement
    :return: The string with replaced variables or the orginal string, if not variables are defined
    """

    ORCA.vars.Globals.dDefVars = aArray
    uTmp = re.sub(rPatternDefVar, _VarDefReplace, uOrgIn)
    return uTmp


def ReplaceVars(uOrgIn, uContext=u''):
    """
    Replaces all occurences of $var(xxx) and $lvar(lll) with the uservars or language vars, with name xxx/lll.
    Multiple var placeholder can be given in on string in any combination.
    Nested var placeholder "$var($var(xxx)) are not allowed.
    A warning will be given if the variable name does not exist

    :rtype: string
    :param string uOrgIn: The string, where the variable placeholer should be replaced
    :param string uContext: The context for the var, default empty. This should be the same context as given in SetVar
    :return: The string with replaced variables or the orginal string, if not variables are defined
    """
    uTmp = ""

    if uOrgIn is None:
        return ""

    try:
        uTmp = re.sub(rPatternVar, _VarReplace, uOrgIn)
        uTmp = re.sub(rPatternLVar, _LanguageVarReplace, uTmp)
        if uContext != "":
            ORCA.vars.Globals.uRepContext = uContext
            uTmp = re.sub(rPatternCVar, _ContextVarReplace, uOrgIn)

    except Exception as e:
        if "$var(" in uOrgIn or "$lvar(" in uOrgIn:
            LogError(u'Vars: ReplaceVars: Runtime Error:' + ToUnicode(uOrgIn) + u':', e)
        else:
            uTmp = uOrgIn

    #uTmp=uTmp.replace('\\n','\n')
    return ToUnicode(uTmp)
