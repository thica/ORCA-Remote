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
from ORCA.utils.ParseResult import cResultParser


class cInterFaceResultParser(cResultParser):
    """ Resultparser object for Interfaces  """
    def __init__(self,oInterFace,uConfigName):
        super(cInterFaceResultParser, self).__init__()
        self.oInterFace     = oInterFace
        self.uConfigName    = uConfigName
        self.uObjectName    = oInterFace.uObjectName
        self.uDebugContext  = "Interface: % s , Config: %s:" % (self.uObjectName,self.uConfigName)
        self.uContext       = self.uObjectName + '/' + self.uConfigName
        self.oAction        = None
        self.oSetting       = None

    def ParseResult(self,oAction,uResponse,oSetting):
        """

        :rtype: string
        :param cAction oAction: The Action object
        :param string uResponse: The response to parse
        :param cBaseInterFaceSettings oSetting: The interface setting of the action
        :return: The result of parse action
        """

        self.oAction      = oAction
        self.oSetting     = oSetting
        return self.Parse(uResponse,oAction.uGetVar,oAction.uParseResultOption,oAction.uGlobalDestVar,oAction.uLocalDestVar,oAction.uParseResultTokenizeString)
