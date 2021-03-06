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

from __future__             import annotations
import sys
from typing                 import List
from ORCA.utils.Path        import cPath
from ORCA.vars.Helpers      import GetEnvVar
from ORCA.utils.Platform    import OS_GetSystemUserPath
from ORCA.vars.QueryDict    import TypedQueryDict
import argparse

__all__ = ['cParameter','cParserAction']

"""
Functions to parse and set given command line parameter
"""

class cParserAction(argparse.Action):
    """
    A Action object for the argparse parser
    """
    def __init__(self, option_strings,  oParameter:cParameter, *args, **kwargs):
        self.oParameter:cParameter = oParameter
        self.HandleValue(kwargs.get("dest"),kwargs.get("default"))
        super(cParserAction, self).__init__(option_strings=option_strings,*args, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        self.HandleValue(self.dest,values)
        setattr(namespace, self.dest, values)
    def HandleValue(self,uName:str,uValue:str):
        """
        Manages a given parameter of the command line
        identifies boolean parameter and paths for the home user folder across OS
        :param str uName: the name of the parameter
        :param str uValue: The value of he parameter
        :return:
        """
        if uName.startswith("oPath"):
            uTmp = uValue
            if uTmp.startswith("~"):
                uTmp = OS_GetSystemUserPath() + uTmp[1:]
            self.oParameter[uName]=cPath(uTmp)
        elif uName.startswith("b"):
            self.oParameter[uName] = (uValue!="")
        else:
            self.oParameter[uName]=uValue

class cParameter(TypedQueryDict):
    """
    Initializes and holds the the given command line parameter
    """
    def __init__(self):
        super(cParameter, self).__init__()
        oParser:argparse.ArgumentParser = argparse.ArgumentParser(description='ORCA Open Remote Control Application')
        self.AddParameter(oParser=oParser)
        aArgs=self.RemoveOtherArguments(oParser=oParser)
        oParser.parse_args(aArgs)

    def AddParameter(self,oParser:argparse.ArgumentParser) -> None:
        """
        Adds all valid command line arguments to the parser object
        :param oParser:
        :return:
        """
        oParser.add_argument('--debugpath',    default=GetEnvVar('DEBUGPATH'),       action=cParserAction, oParameter=self, dest="oPathDebug",     help='Changes the path for ORCA files (can be passed as DEBUGPATH environment var)')
        oParser.add_argument('--logpath',      default=GetEnvVar('ORCALOGPATH'),     action=cParserAction, oParameter=self, dest="oPathLog",       help='Changes the path for ORCA/Kivy log files (can be passed as ORCALOGPATH environment var)')
        oParser.add_argument('--tmppath',      default=GetEnvVar('ORCATMPPATH'),     action=cParserAction, oParameter=self, dest="oPathTmp",       help='Changes the path for ORCA temp folder (can be passed as ORCATMPPATH environment var)')
        oParser.add_argument('--smallscreen',  default=GetEnvVar('ORCASMALL'),       action=cParserAction, oParameter=self, dest="bSmallScreen",   help='If set ORCA switches to small screen (can be passed as ORCASMALL environment var)')

    # noinspection PyMethodMayBeStatic
    def RemoveOtherArguments(self,oParser) -> List:
        """ Removes all ORCA command line arguments from the command line, so it does not clash with kivy """
        aRet:List = []
        for uArg in sys.argv[1:]:
            # noinspection PyProtectedMember
            for uOption in oParser._option_string_actions:
                if uOption.lstrip("-")==uArg.split("=")[0].lstrip("-"):
                    aRet.append(uArg)
                    break
        return aRet

