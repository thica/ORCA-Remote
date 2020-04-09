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

from xml.etree.ElementTree          import Element
from kivy.uix.widget                import Widget
from ORCA.widgets.base.Base         import cWidgetBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage import cScreenPage
else:
    from typing import TypeVar
    cScreenPage = TypeVar("cScreenPage")

import ORCA.Globals as Globals

__all__ = ['cWidgetAnchor']

class cWidgetAnchor(cWidgetBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-ANCHOR
    WikiDoc:TOCTitle:Anchor
    = ANCHOR =
    The anchor widget has not a screen representation. It is used to create a virtual rectangle, where you can place widgets into. All widget coordinates are relative to the anchor position.

    There is only one additional attribute to common widget attributs

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "ANCHOR". Capital letters!
    |}</div>

    Below you see an example for an anchor
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Anchor Left Buttons' type='ANCHOR' posx='%10' posy='of:totop:Anchor BottomGap' width='%19'  height='of:width:self:*2.8' >
        <xi:include href="$var(DEFINITIONPATH)/block_buttons_left.xml" parse="xml" />
    </element>
    </syntaxhighlight></div>
    WikiDoc:End
    """


    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # For the Border
        self.AddArg('background_color', [1.0, 0.0, 1.0, 1.0])
        self.AddArg('linewidth', "2")

    def InitWidgetFromXml(self,*,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads from Xml """
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage, uAnchor)

    def Create(self,oParent:Widget) -> bool:
        """ Creates the Widget """
        if Globals.bShowBorders:
            self.CreateBase(Parent=oParent,Class="")
            self.oObject = self.oParent
            self.FlipBorder()
            self.oObject = None
        return True

    def UpdateWidget(self):
        self.oObject = self.oParent
        self.FlipBorder()
        self.oObject = None
        return True
