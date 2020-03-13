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
from typing import Union

from    ORCA.utils.Wildcard     import MatchWildCard

__all__ = ['ParseDictKeyTree',
           'ParseDictAny']


def ParseDictKeyTree(*,vObj:Union[List,Dict], aKeys:List) -> List:
    """Pull all values of specified key from nested JSON."""
    iLevel:int      = 0
    aResult:List    = []
    iOrgLevel:int


    # noinspection PyShadowingNames
    def Extract(vObj:Union[List,Dict], aResult:List, aKeys:List,iLevel:int):
        """Recursively search for values of key in JSON tree."""
        uSearchKey:str = aKeys[iLevel]
        iLevel += 1
        uFoundKey:str
        vValue:Union[List,Dict,str]
        uResult:str

        if isinstance(vObj, dict):
            for uFoundKey, vValue in vObj.items():
                if MatchWildCard(uValue=uFoundKey,uMatchWithWildCard=uSearchKey):
                    if isinstance(vValue, dict):
                        Extract(vValue, aResult, aKeys,iLevel)
                    elif isinstance(vValue,list) and len(vValue) > 0 and isinstance(vValue[0], (dict,list)):
                        Extract(vValue, aResult, aKeys,iLevel)
                    elif isinstance(vValue,list):
                        for uResult in vValue:
                            aResult.append(uResult)
                    else:
                        aResult.append(vValue)
        elif isinstance(vObj, list):
            for vItem in vObj:
                iOrgLevel =  iLevel
                Extract(vItem, aResult, aKeys, iLevel-1)
                iLevel = iOrgLevel
        return aResult

    return Extract(vObj, aResult, aKeys,iLevel)

def ParseDictAny(*,vObj:Union[List,Dict], uSearchKey:str, bSingleValue:bool=False) -> Union[List,str]:
    """Pull all values of specified key from nested JSON."""
    aResult:List    = []

    # noinspection PyShadowingNames
    def Extract(vObj:Union[List,Dict], aResult:List, uSearchKey):
        """Recursively search for values of key in JSON tree."""
        uFoundKey:str
        vValue:Union[List,Dict,str]
        uResult:str

        if isinstance(vObj, dict):
            for uFoundKey, vValue in vObj.items():
                if isinstance(vValue, dict):
                    Extract(vValue, aResult, uSearchKey)
                elif isinstance(vValue,list) and len(vValue) > 0 and isinstance(vValue[0], (dict,list)):
                    Extract(vValue, aResult, uSearchKey)
                elif isinstance(vValue,list):
                    if MatchWildCard(uValue=uFoundKey,uMatchWithWildCard=uSearchKey):
                        for uResult in vValue:
                            aResult.append(uResult)
                else:
                    if MatchWildCard(uValue=uFoundKey,uMatchWithWildCard=uSearchKey):
                        aResult.append(vValue)
        elif isinstance(vObj, list):
            for vItem in vObj:
                Extract(vItem, aResult, uSearchKey)
        return aResult

    Extract(vObj, aResult, uSearchKey)
    if bSingleValue:
        if len(aResult)>0:
            return aResult[0]
        else:
            return ""
    else:
        return aResult

