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

from dataclasses import dataclass

__all__ = ['cBaseTrigger']

@dataclass
class cBaseTrigger:
    """ a trigger representation """
    uTriggerAction:str             = u''
    uTriggerName:str               = u''
    uGetVar:str                    = u''
    uRetVar:str                    = u''
    uGlobalDestVar:str             = u''
    uLocalDestVar:str              = u''
    # just to have them defined, no usage
    uCmd:str                       = u''

