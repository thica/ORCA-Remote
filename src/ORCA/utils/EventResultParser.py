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

from ORCA.utils.TypeConvert  import ToDic
from ORCA.utils.ParseResult import cResultParser

__all__ = ['cEventScriptResultParser']

class cEventScriptResultParser(cResultParser):
    """ the result parser for actions """

    def __init__(self,oAction):
        super(cEventScriptResultParser, self).__init__()
        self.oAction  = oAction
        uScriptName=oAction.dActionPars.get("scriptname","")
        self.uDebugContext  = "Action: % s , Script: %s:" % (oAction.uActionName,uScriptName)
        self.uContext       = oAction.uActionName + '/' + uScriptName

    def ParseResult(self,uResponse, uParseOptions):
        """
        The parser function

        :rtype: tuple
        :param string uResponse: The reponse to parse
        :param string uParseOptions: A string representing the parse options (string of a dict)
        :return: The result of the parsing
        """
        if uParseOptions!= u'':
            aParseOptions               = ToDic(uParseOptions)
            uGetVar                     = aParseOptions.get('getvar',u'')
            uGlobalDestVar              = aParseOptions.get('gdestvar',u'')
            uLocalDestVar               = aParseOptions.get('ldestvar',u'')
            uParseResultOption          = aParseOptions.get('parseoption',u'store')
            uParseResultTokenizeString  = aParseOptions.get('parsetoken',u':')

            return self.Parse(uResponse,uGetVar,uParseResultOption,uGlobalDestVar,uLocalDestVar,uParseResultTokenizeString)
        return "",""
