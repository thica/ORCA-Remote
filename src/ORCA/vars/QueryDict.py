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

from typing import Any
from typing import Dict

from kivy.logger            import Logger
from ORCA.utils.LogError    import LogError
import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.BaseSettings import cBaseSettings
else:
    from typing import TypeVar
    cBaseSettings = TypeVar("cBaseSettings")


__all__ = ['QueryDict','TypedQueryDict','cMonitoredSettings']


class QueryDict(dict):
    """
    Copy of the kivy querydict, with better error handling. In fact u can use local variable, defines a querydict by its name. See details in the kivy querydict documentation
    """

    def __getattr__(self, attr):
        try:
            return self.__getitem__(attr)
        except KeyError:
            if attr!="__name__":
                LogError(uMsg=u'QueryDict: can''t find attribute:'+attr)
            return u''
    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)

class TypedQueryDict(QueryDict):
    """
    QueryDict with typing handling / Checking
    """

    def __setitem__(self, k, v) -> str:
        uName:str = NormalizeName(uName=k,vValue=v)
        super().__setitem__(uName, v)
        if Globals.bProtected:
            self.CheckSpelling()
        return uName

    def queryget(self,item:Any) -> Any:
        """
        Returns the value an item, independent of its type prefix, This enable easier handling of ini files, where you usually will not use a type prefix
        :param item: The key of the item
        :return: The value or none
        """
        ret = dict.get(self,item)
        if ret is not None: return ret
        for pre in "uifboad":
            ret = dict.get(self,pre+item)
            if ret is not None: return ret
        return None

    def CheckSpelling(self) -> None:
        """
        Debug helper function, which checks of the type prefix fits to the type of the var and if we have duplicate entries with different types
        This is automatic disabled in release version
        :return:
        """
        dCheck:Dict[str,str]={}
        key:str
        for key in self:
            if key.upper() in dCheck:
                Logger.error("Duplicate Key with mismatch spelling:"+ key+" "+dCheck[key.upper()])
                return
            dCheck[key.upper()]=key

        for key in self:
            if key[1:].upper() in dCheck:
                Logger.error("Duplicate Key with mismatch type:"+ key+" "+dCheck[key.upper()])
                return
            dCheck[key[1:].upper()]=key

        for key in self:
            if key[0] == "u" and not isinstance(self[key],str):
                Logger.error("TypedQueryDict Wrong str type:" + key + " " + str(self[key]) + " " + str(type(self[key])))
            elif key[0] == "í" and not isinstance(self[key],int):
                Logger.error("TypedQueryDict Wrong int type:" + key + " " + str(self[key]) + " " + str(type(self[key])))
            elif key[0] == "f" and not isinstance(self[key],float):
                Logger.error("TypedQueryDict Wrong float type:" + key + " " + str(self[key]) + " " + str(type(self[key])))
            elif key[0] == "b" and not isinstance(self[key],bool):
                Logger.error("TypedQueryDict Wrong bool type:" + key + " " + str(self[key]) + " " + str(type(self[key])))
            elif key[0] == "a" and not isinstance(self[key],list):
                Logger.error("TypedQueryDict Wrong list type:" + key + " " + str(self[key]) + " " + str(type(self[key])))
            elif key[0] == "d" and not isinstance(self[key],dict):
                Logger.error("TypedQueryDict Wrong dict type:" + key + " " + str(self[key]) + " " + str(type(self[key])))
            elif key[0].islower() and not key[1].isupper():
                Logger.error("TypedQueryDict Wrong key name (not lower/Uppercase) " + key)

class cMonitoredSettings(TypedQueryDict):
    """
    A sub of querydict, which writes changes of dict values automatically into a config files
    """
    def __init__(self, oBaseSettings:cBaseSettings, **kwargs):
        """
        Initializes the Querydict

        :type object oBaseSettings: The parent interfacesetting
        """
        super().__init__(**kwargs)
        self.oBaseSettings:cBaseSettings = oBaseSettings

    def WriteVar(self,uName:str,vValue:Any):
        """
        Dummy function to write the value into a config. Needs to be overloades
        :param uName: The key name
        :param vValue: The value
        """
        Logger.error("cMonitoredSettings: Overload for WriteVar is missing")
        pass

    def __setitem__(self, k, v):
        uName:str =super().__setitem__(k, v)
        self.WriteVar(uName=uName, vValue=v)


def NormalizeName(uName:str,vValue:Any) ->str:
    """
    Normalizes the type by adding a prefix which fits to the variable type
    :param uName:
    :param vValue:
    :return:
    """
    uPre:str = 'o'

    if len(uName)>1:
        if uName[0].islower() and uName[1].isupper():
            uPre = ''

    if uPre:
        if isinstance(vValue,str):
            uPre = 'u'
        elif type(vValue) is int:
            uPre = 'i'
        elif type(vValue) is float:
            uPre = 'f'
        elif type(vValue) is bool:
            uPre = 'b'
        elif type(vValue) is list:
            uPre = 'a'
        elif type(vValue) is dict:
            uPre = 'd'
        elif isinstance(vValue,object):
            uPre = 'o'
        else:
            Logger.error("Unknown Type for cMonitoredSettings:"+uName)

    return str(uPre+uName)
