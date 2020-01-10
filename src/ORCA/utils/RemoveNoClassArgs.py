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

from typing import Dict
from typing import List
from typing import Any
from typing import Callable

_ArgCache:dict={}


def getmro(aClass:Any, recurse:Callable) ->List:
    mro = [aClass]
    for base in aClass.__bases__: mro.extend(recurse(base, recurse))
    return mro


def all_members(aClass:Any) -> Dict:
    try:
        # Try getting all relevant classes in method-resolution order
        mro = list(aClass.__mro__)
    except AttributeError:
        # If a class has no _ _mro_ _, then it's a classic class
        mro = getmro(aClass, getmro)
    mro.reverse(  )
    members = {}
    for someClass in mro: members.update(vars(someClass))
    return members

def RemoveNoClassArgs(dInArgs:Dict, oObject:Any) -> Dict:
    """ In python3 it triggers an error, if we pass ORCA Args at __Init__ to Kivy Widgets
        so we remove them
    """

    dAllMembers:Dict=_ArgCache.get(oObject.__name__)
    if dAllMembers is None:
        dAllMembers=all_members(oObject)
        _ArgCache[oObject.__name__]=dAllMembers

    dOutArgs:Dict = {}
    for key in dInArgs:
        if key in dAllMembers:
            dOutArgs[key]=dInArgs[key]

    return dOutArgs

