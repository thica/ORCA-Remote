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

from __future__ import annotations
from typing import Dict
from typing import List
from typing import Any
from typing import Union

from xml.etree.ElementTree      import Element
from xml.etree.ElementTree      import SubElement
# from ORCA.utils.XML             import GetXMLTextValue


cLinkPar = Union[str,List[Dict]]
oLinkPar:cLinkPar = ''

dUserVars:Dict[str,Any]                     = {}
dUserVarLinks:Dict[str,List[cLinkPar]]      = {}
dDefVars:Dict[str,str]                      = {}
uRepContext:str                             = ''


def InitSystemVars() -> None:
    """
    Initializes the variable system. Should only be called once
    """
    dUserVars.clear()
    dUserVarLinks.clear()


def Vars_Persistence_WriteToXMLNode(*,oXMLNode:Element) -> None:
    """ writes object vars to a xml node """

    oXMLVars: Element
    oXMLVar:Element
    oXmlVarEntry: Element
    oXmlVarEntryName: Element
    oXmlVarEntryValue: Element

    oXMLVarLinks:Element
    uVarName:str

    oXMLVars: Element = SubElement(oXMLNode, 'vars')
    for uVarName in dUserVars.keys():
        oXmlVarEntry = SubElement(oXMLVars, 'var')
        oXmlVarEntryName= SubElement(oXmlVarEntry, 'name')
        oXmlVarEntryName.text=uVarName
        oXmlVarEntryValue= SubElement(oXmlVarEntry, 'value')
        oXmlVarEntryValue.text=dUserVars[uVarName]


def Vars_Persistence_ReadFromXMLNode(*,oXMLNode:Element) -> None:

    oXMLVars: Element
    oXMLVar:Element
    uVarName:str

    oXMLVars: Element = oXMLNode.find('vars')
    if oXMLVars is not None:
        for oXMLVar in oXMLVars.findall('var'):
            uVarName = oXMLVar.find('name').text
            dUserVars[uVarName]=oXMLVar.find('value').text

