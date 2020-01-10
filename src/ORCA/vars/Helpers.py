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
from typing import List
from typing import Dict
from typing import Any
from typing import Union

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


def Round(fValue:Union[float,None],iPos:int) -> Union[float,int]:
    """
    Rounds a float value to the given pos. If the value is none, zero (0) will be returned.
    Example: Round(1.81,0) return 2. Round(1.81,1) returns 1.80

    :param float fValue: The float value to round
    :param int iPos: the round pos
    :return: Rounded Value
    """

    if (fValue is None) or (fValue==0.0):
        return 0.0
    fRet:float=fValue/abs(fValue) * int(abs(fValue) * 10**iPos + 0.5)/ 10**iPos
    if iPos==0:
        fRet = int(fRet)

    return fRet


def GetVarList(uFilter:str=u'') -> Dict[str,Any]:
    """
    Returns a dict of uservars

    :param str uFilter: A filter to just return vars, which CONTAINS the filter string
    :return: A dict which contains all user vars, which fits to uFilter or all, if uFilter is empty
    """

    dRet:Dict[str,Any] = {}
    if uFilter==u'':
        for uVarIdx in ORCA.vars.Globals.dUserVars:
            dRet[uVarIdx]=ORCA.vars.Globals.dUserVars[uVarIdx]
    else:
        for uVarIdx in sorted(ORCA.vars.Globals.dUserVars):
            if uFilter in uVarIdx:
                dRet[uVarIdx]=ORCA.vars.Globals.dUserVars[uVarIdx]
    return dRet


def UnSplit(aVars:List) ->None:
    #Unsplits a Json splitted array
    i=0
    while i < len(aVars):
        if not aVars[i]=='':
            if aVars[i][0:1]=='[':
                if not i==len(aVars)-1:
                    if aVars[i+1][-1]==']':
                        aVars[i]+=','
                        aVars[i]+=aVars[i+1]
                        del aVars[i+1]
        i+=1


def GetEnvVar(uVarName:str,uDefault:str="") -> str:
    """
    Returns the value of an environment var

    :param str uVarName: Name of the Environment variable to return
    :param str uDefault: Optional: The default value, if no environment is given
    :return: The value of the variable or an empty string if not found
    """
    uRet:str=os.getenv(uVarName)
    if uRet is None:
        uRet=uDefault
    else:
        uRet= ReplaceVars(uRet)
    return uRet

def Find_nth_Character(uStr1:str, uSubstr:str, iLevel:int) -> Union[int,None]:
    """
    Find the nTh position of a string with in string.
    Find_nth_Character(u"Test Test Test","Test",1) returns 0
    Find_nth_Character(u"Test Test Test","Test",2) returns 5
    Find_nth_Character(u"Test Test Test","Test",3) returns 10
    Find_nth_Character(u"Test Test Test","Test",6) returns None
    Find_nth_Character(u"Test Test Test","Foo",3) returns None

    :param str uStr1: The string to search in
    :param str uSubstr: The string to search for
    :param int iLevel: The occurance of the substring (starting with 1)
    :return: Position of the nTh occurance of the substring in string, or None if not found
    """
    iPos:int = -1
    for x in range(iLevel):
        iPos = uStr1.find(uSubstr, iPos + 1)
        if iPos == -1:
            return None
    return iPos


def CopyDict(dSrc:Dict) -> Dict:

    try:
        return json.loads(json.dumps(dSrc))
    except Exception:
        Logger.warning("Can't copy dict the preferred way:"+str(dSrc))
        return deepcopy(dSrc)
