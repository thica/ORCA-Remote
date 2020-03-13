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

from typing import Tuple
from typing import Union
from ORCA.utils.ParseResult import cResultParser
from ORCA.Action            import cAction


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.interfaces.BaseInterfaceSettings  import cBaseInterFaceSettings
    from ORCA.interfaces.BaseInterface          import cBaseInterFace
else:
    from typing import TypeVar
    cBaseInterFace = TypeVar("cBaseInterFace")
    cBaseInterFaceSettings = TypeVar("cBaseInterFaceSettings")

class cInterFaceResultParser(cResultParser):
    """ Resultparser object for Interfaces  """
    def __init__(self,oInterFace:cBaseInterFace,uConfigName:str):
        super().__init__()
        self.oInterFace:cBaseInterFace                  = oInterFace
        self.uConfigName:str                            = uConfigName
        self.uObjectName                                = oInterFace.uObjectName
        self.uDebugContext                              = "Interface: % s , Config: %s:" % (self.uObjectName,self.uConfigName)
        self.uContext                                   = self.uObjectName + '/' + self.uConfigName
        self.oAction:cAction                            = Union[cAction,None]
        self.oSetting:Union[cBaseInterFaceSettings,None]= None

    def ParseResult(self,oAction,uResponse,oSetting) -> Tuple[str,str]:
        """

        :param cAction oAction: The Action object
        :param string uResponse: The response to parse
        :param cBaseInterFaceSettings oSetting: The interface setting of the action
        :return: The result of parse action
        """

        self.oAction      = oAction
        self.oSetting     = oSetting
        return self.Parse(uResponse=uResponse,
                          uGetVar=oAction.uGetVar,
                          uParseResultOption=oAction.uParseResultOption,
                          uGlobalDestVar=oAction.uGlobalDestVar,
                          uLocalDestVar=oAction.uLocalDestVar,
                          uTokenizeString=oAction.uParseResultTokenizeString,
                          uParseResultFlags=oAction.uParseResultFlags)
