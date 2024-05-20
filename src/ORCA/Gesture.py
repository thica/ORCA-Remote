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

from kivy.gesture           import Gesture
from xml.etree.ElementTree  import Element
from ORCA.utils.XML         import GetXMLTextAttribute

__all__ = ['cGesture']

class cGesture:
    """ Gesture Abstraction Object """
    def __init__(self):
        self.uGestureName:str           =  ''
        self.oGesture:Gesture           =  Gesture()
        self.uGestureString:str         =  ''
    def ParseGestureFromXMLNode(self,*,oXMLNode:Element) -> None:
        """ Parses a gesture from an xml object """
        self.uGestureName               =  GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='name',bMandatory=True,vDefault='')
        self.uGestureString             =  GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='data',bMandatory=True,vDefault='')
