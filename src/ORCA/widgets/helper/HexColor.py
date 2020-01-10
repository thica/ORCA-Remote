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


from typing                            import List
from kivy.utils                        import get_color_from_hex
from ORCA.vars.Replace                 import ReplaceVars

__all__ = ['GetColorFromHex','GetHexFromColor','aColorUndefined','uColorUndefined']

uColorUndefined:str         = "#00000001"

def GetColorFromHex(uColor:str) -> List[float]:
    """
    Helper function to get a rgba tuple from a hex string
    :param str uColor: HEX representation of a color eg:#00FF0040
    :return: A list in the format (r,g,b,a), where all values are floats between 0 and 1, (return 0,0,0,0.1 in case of an error)
    """

    try:
        aRet = get_color_from_hex(ReplaceVars(uColor.lower()))
    except Exception:
        aRet = get_color_from_hex(uColorUndefined)

    iMissing:int = 4 - len(aRet)
    for i in range(iMissing):
        aRet.append(1.0)
    return aRet


def GetHexFromColor(aColor:List[float]) -> str:
    """
    Helper function to convert a kivy color (List of floats into a HEX string)
    :param List aColor: A list in the format (r,g,b,a), where all values are floats between 0 and 1
    :return: A Hex string (eg #00FF0040)
    """

    try:
        return ''.join('{:02x}'.format(int(x*255)) for x in aColor)
    except Exception:
        return u"00000000"


aColorUndefined:List[float]   = GetColorFromHex(uColorUndefined)

