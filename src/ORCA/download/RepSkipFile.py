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

from xml.etree.ElementTree      import Element
from xml.etree.ElementTree      import SubElement
from ORCA.utils.Filesystem      import AdjustPathToOs

__all__ = ['cRepSkipFile']

class cRepSkipFile:
    """
    sub class which is an representation of the skip files part the repository xml tree
    loads and writes the xml node
    """
    def __init__(self):
        self.uFile:str = u''
    def ParseFromXMLNode(self,*,oXMLNode:Element) -> None:
        """ Parses an xms string into object vars """
        self.uFile:str = AdjustPathToOs(uPath=oXMLNode.text)
    def WriteToXMLNode(self,*,oXMLNode:Element) -> None:
        """ writes object vars to an xml node """
        oVal:Element = SubElement(oXMLNode,'file')
        oVal.text=self.uFile
