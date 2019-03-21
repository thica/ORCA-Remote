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

from kivy.logger            import Logger
from kivy.compat            import string_types
from ORCA.utils.LogError    import LogError
import ORCA.Globals as Globals

__all__ = ['QueryDict','cMonitoredSettings']


class QueryDict(dict):
    """
    Copy of the kivy querydict, with better error handling. In fact u can use local variable, defines a querydict by its name. See details in the kivy querydict documentation
    """

    def __getattr__(self, attr):
        try:
            return self.__getitem__(attr)
        except KeyError:
            if attr!="__name__":
                LogError(u'QueryDict: can''t find attribute:'+attr)
            return u''

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)


class cMonitoredSettings(QueryDict):
    def __init__(self, oBaseSettings, **kwargs):
        """
        Initializes the Querydict

        :type object oBaseSettings: The parent interfacesetting
        """
        super(cMonitoredSettings, self).__init__(**kwargs)
        self.oBaseSettings = oBaseSettings

    def __NormalizeName(self,uName,value):

        uPre = 'o'

        if len(uName)>1:
            if uName[0].islower() and uName[1].isupper():
                uPre = ''

        if uPre:
            if isinstance(value,string_types):
                uPre = 'u'
            elif type(value) is int:
                uPre = 'i'
            elif type(value) is float:
                uPre = 'f'
            elif type(value) is bool:
                uPre = 'b'
            elif type(value) is list:
                uPre = 'a'
            elif isinstance(value,object):
                uPre = 'o'
            else:
                Logger.error("Unknown Type for cMonitoredSettings:"+uName)

        return str(uPre+uName)

    def WriteVar(self,sName,oValue):
        # DUMMY
        pass

    def __setitem__(self, k, v):

        sName = self.__NormalizeName(uName=k,value=v)
        super(cMonitoredSettings, self).__setitem__(sName, v)
        self.WriteVar(sName=sName, oValue=v)
        if Globals.bProtected:
            self.CheckSpelling() # todo: remove in release'

    '''
    def __setattr__(self, attr, value):
        """
        Sets the Attribute in the Querydict AND set the contextvar

        :param string attr: The attribute name
        :param value: The attribute value
        """
        sName=self.__NormalizeName(uName=attr,value=value)
        super(cMonitoredSettings, self).__setattr__(sName, value)
        self.WriteVar(sName=sName, oValue=value)
        self.CheckSpelling() # todo: remove in release'
    '''

    def CheckSpelling(self):
        dCheck={}
        #for key in self.iterkeys():
        for key in self:
            if key.upper() in dCheck:
                Logger.error("Duplicate Key with mismatch spelling:"+ key+" "+dCheck[key.upper()])
                return
            dCheck[key.upper()]=key

        #for key in self.iterkeys():
        for key in self:
            if key[1:].upper() in dCheck:
                Logger.error("Duplicate Key with mismatch type:"+ key+" "+dCheck[key.upper()])
                return
            dCheck[key[1:].upper()]=key

    def queryget(self,item):

        ret = dict.get(self,item)
        if ret is not None: return ret
        for pre in "uifboa":
            ret = dict.get(self,pre+item)
            if ret is not None: return ret
        return None

