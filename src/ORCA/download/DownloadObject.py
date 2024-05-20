# -*- coding: utf-8 -*-

"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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
from typing import Any
import json

__all__ = ['cDownLoadObject']


class cDownLoadObject:
    """ Representation of a single object to download"""
    def __init__(self):
        self.dPars:Dict[str,Any] =    { 'Url'     : '',
                                        'Dest'    : '',
                                        'Target'  : '',
                                        'Type'    : '',
                                        'Name'    : '',
                                        'Version' : 0,
                                        'Finalize': ''}
    def ToString(self) -> str:
        """ Dumps the pars of the object """
        return json.dumps(self.dPars)
    def FromString(self,*,uPars:str) -> None:
        """ loads the parameters from a json string """
        self.dPars=json.loads(uPars)
