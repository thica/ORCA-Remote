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

from typing import Tuple
from ORCA.definition.DefinitionContext import SetDefinitionContext

def GetSetDefinitionName(*,uText:str) ->Tuple:
    """
    Gets the definitionname from a string and sets the definitioncontext
    :param uText:
    :return: A Tuple of definitionname and long definition description
    """
    uRet:str = ''
    iLoc2:int
    iLoc:int = uText.find('[')
    if not iLoc == -1:
        iLoc2= uText.find(']',iLoc)
        if not iLoc2 == -1:
            uRet=uText[iLoc+1:iLoc2]
            if not uRet=='':
                SetDefinitionContext(uDefinitionName=uRet)
                uText=uText[:iLoc]+uText[iLoc2+1:]

    return uRet,uText
