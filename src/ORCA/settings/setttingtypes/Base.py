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

from typing                             import List
from kivy.uix.widget                    import Widget
from kivy.uix.settings                  import SettingItem
import ORCA.Globals as Globals

__all__ = ['SettingSpacer',
           'SettingHidden',
           'GetLanguageList',
           'GetGestureList',
           'GetPageList',
           'GetActionList',
           'GetSendActionList']

class SettingSpacer(Widget):
    """ Internal class, not documented. """
    pass

class SettingHidden(SettingItem):
    """ a hidden setting """
    pass

def GetLanguageList() -> List[str]:
    """ Return the list of all defined language vars """

    uKey:str
    uValue:str

    if "aList" not in vars(GetLanguageList):
        GetLanguageList.aList=[]
        for uKey in Globals.oLanguage.dIDToString:
            uValue="%s [[%s]]" % (Globals.oLanguage.dIDToString[uKey],uKey)
            if not uValue in GetLanguageList.aList or True:
                GetLanguageList.aList.append(uValue)
        GetLanguageList.aList.sort()
    return GetLanguageList.aList

def GetGestureList() -> List[str]:
    """ Return the list of all Gesture Names"""

    uKey:str
    if "aList" not in vars(GetGestureList):
        GetGestureList.aList=[]
        for uKey in Globals.oTheScreen.dGestures:
            GetGestureList.aList.append(uKey)
        GetGestureList.aList.sort()
    return GetGestureList.aList

def GetPageList() -> List[str]:
    """ Return the list of all Page Names"""
    uKey:str
    if "aList" not in vars(GetPageList):
        GetPageList.aList=[]
        for uKey in Globals.oTheScreen.oScreenPages:
            GetPageList.aList.append(uKey)
        GetPageList.aList.sort()
    return GetPageList.aList

def GetActionList()  -> List[str]:
    """ Return the list of all Action Names"""
    uKey:str

    if "aList" not in vars(GetActionList):
        GetActionList.aList=[]
        for uKey in Globals.oActions.dActionsCommands:
            GetActionList.aList.append(uKey)
        GetActionList.aList.sort()
    return GetActionList.aList

def GetSendActionList() -> List[str]:
    """ Return the list of all Send Action Names"""
    uKey:str

    if "aList" not in vars(GetSendActionList):
        GetSendActionList.aList=[]
        for uKey in Globals.oActions.dActionsCommands:
            if uKey.startswith("Send "):
                GetSendActionList.aList.append(uKey)
        GetSendActionList.aList.sort()
    return GetSendActionList.aList
