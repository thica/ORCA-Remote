# -*- coding: utf-8 -*-

"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2020  Carsten Thielepape
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
import sys

from ORCA.utils.LogError    import LogError
from ORCA.vars.Access       import SetVar
from ORCA.vars.Access       import GetVar
from ORCA.utils.FileName    import cFileName

import ORCA.Globals as Globals

__all__ = ['Var_Save',
           'Var_Load',
           'Var_DeleteCookie',
           'CookieName',
           'GetCookieValue'
          ]

this = sys.modules[__name__]
this.rPatternCookie  =r"\$cookie\(([\|\w\s\[\]\-\+_]+)\)"


def NormalizeFileName(uFileName:str) -> str:
    """
    Removes all invalid characters in a filename

    :param str uFileName: Filename to normalize
    :return: Normalized file name
    """

    uNew="".join(x for x in uFileName if x.isalnum())
    return uNew

def Var_Save(uVarName:str,uPrefix:str) -> None:
    """ Saves a var to a cookie """
    uValue:str      = GetVar(uVarName = uVarName)
    oFN:cFileName   = CookieName(uVarName,u'var_'+uPrefix)
    try:
        oFile = open(oFN.string, 'w')
        oFile.write(uValue)
        oFile.close()
    except Exception as e:
        LogError(uMsg=u'Var_Save: can\'t safe var',oException=e)

def Var_Load(uVarName:str, uDefault:str,uPrefix:str) -> str:
    """ loads a var from a cookie """
    oFN:cFileName   = CookieName(uVarName,u'var_'+uPrefix)
    uVarValue:str   = uDefault
    if oFN.Exists():
        try:
            oFile = open(oFN.string, 'r')
            uVarValue=oFile.read()
            oFile.close()
        except Exception as e:
            LogError(uMsg=u'Var_Save: can\'t load var',oException=e)
    SetVar(uVarName = uVarName, oVarValue = uVarValue)
    return uVarValue

def Var_DeleteCookie(uVarName:str, uPrefix:str) -> None:
    """ deletes a cookiefile """
    CookieName(uVarName,u'var_'+uPrefix).Delete()

def CookieName(uVarName:str,uPrefix:str) -> cFileName:
    """ creates a cookie filename """
    oFnCookie:cFileName = cFileName(Globals.oPathCookie) + (uPrefix + "_" + NormalizeFileName(uVarName) + ".cok")
    return oFnCookie


# noinspection PyUnresolvedReferences
def GetCookieValue(uOrgIn:str) -> str:
    """ Returns the value stored in a cookie """
    uRet:str        = u''
    uDefault:str    = u''
    oMatch          = re.search(this.rPatternCookie,uOrgIn)
    if oMatch:
        uVarName:str=oMatch.string[oMatch.regs[1][0]:oMatch.regs[1][1]]
        if "|" in uVarName:
            uVarName,uDefault=uVarName.split('|')
        uRet=Var_Load(uVarName,uDefault,u'')
        uRet=uOrgIn[:oMatch.regs[0][0]]+uRet+uOrgIn[oMatch.regs[0][1]:]
    return uRet

