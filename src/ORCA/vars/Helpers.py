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

import os
import json
from copy                   import deepcopy
from kivy.logger            import Logger
from ORCA.vars.Replace      import ReplaceVars

import ORCA.vars.Globals

__all__ = ['Round',
           'GetVarList',
           'UnSplit',
           'GetEnvVar',
           'CopyDict',
           'Find_nth_Character']


def Round(Value,iPos):
    """
    Rounds a float value to the given pos. If the value is none, zero (0) will be returned.
    Example: Round(1.81,0) return 2. Round(1.81,1) returns 1.80

    :rtype: float
    :param float Value: The float value to round
    :param int iPos: the round pos
    :return: Rounded Value
    """

    if (Value is None) or (Value==0):
        return 0
    fRet=Value/abs(Value) * int(abs(Value) * 10**iPos + 0.5)/ 10**iPos
    if iPos==0:
        # fRet=float(int(fRet))
        fRet = int(fRet)

    return fRet


def GetVarList(uFilter=u''):
    """
    Returns a dict of uservars

    :rtype: dict
    :param string uFilter: A filter to just return vars, which CONTAINS the filter string
    :return: A dict which contains all user vars, which fits to uFilter or all, if uFilter is empty
    """

    dRet={}
    if uFilter==u'':
        for uVarIdx in ORCA.vars.Globals.dUserVars:
            dRet[uVarIdx]=ORCA.vars.Globals.dUserVars[uVarIdx]
    else:
        for uVarIdx in sorted(ORCA.vars.Globals.dUserVars):
            if uFilter in uVarIdx:
                dRet[uVarIdx]=ORCA.vars.Globals.dUserVars[uVarIdx]
    return dRet


def UnSplit(lVars):
    #Unsplits a Json splitted array
    i=0
    while i < len(lVars):
        if not lVars[i]=='':
            if lVars[i][0:1]=='[':
                if not i==len(lVars)-1:
                    if lVars[i+1][-1]==']':
                        lVars[i]+=','
                        lVars[i]+=lVars[i+1]
                        del lVars[i+1]
        i+=1


def GetEnvVar(uVarName,uDefault=""):
    """
    Returns the value of an environment var

    :rtype: string
    :param string uVarName: Name of the Environment variable to return
    :param string uDefault: Optional: The default value, if no environment is given
    :return: The value of the variable or an empty string if not found
    """
    uRet=os.getenv(uVarName)
    if uRet is None:
        uRet=uDefault
    else:
        uRet= ReplaceVars(uRet)
    return uRet


def Find_nth_Character(uStr1, uSubstr, iLevel):
    """
    Find the nTh position of a string with in string.
    Find_nth_Character(u"Test Test Test","Test",1) returns 0
    Find_nth_Character(u"Test Test Test","Test",2) returns 5
    Find_nth_Character(u"Test Test Test","Test",3) returns 10
    Find_nth_Character(u"Test Test Test","Test",6) returns None
    Find_nth_Character(u"Test Test Test","Foo",3) returns None

    :param uStr1: unicode: The string to search in
    :param uSubstr: unicode: The string to search for
    :param iLevel: int: The occurance of the substring (starting with 1)
    :return: int: Position of the nTh occurance of the substring in string, or None if not found
    """
    iPos = -1
    for x in range(iLevel):
        iPos = uStr1.find(uSubstr, iPos + 1)
        if iPos == -1:
            return None
    return iPos


def CopyDict(dSrc):

    try:
        return json.loads(json.dumps(dSrc))
    except Exception as e:
        Logger.warning("Can't copy dict the preffered way:"+str(dSrc))
        return deepcopy(dSrc)
