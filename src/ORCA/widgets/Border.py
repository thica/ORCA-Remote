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

from xml.etree.ElementTree          import Element
from kivy.uix.widget                import Widget
from kivy.metrics                   import dp
from ORCA.utils.TypeConvert         import ToInt
from ORCA.utils.TypeConvert         import ToFloat
from ORCA.utils.XML                 import GetXMLTextAttributeVar

from ORCA.widgets.base.Base         import cWidgetBase
from ORCA.widgets.core.Border       import cBorder
import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")


__all__ = ['cWidgetBorder']

class cWidgetBorder(cWidgetBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-BORDER
    WikiDoc:TOCTitle:Border
    = BORDER =
    The border widget creates a colored border. You could specify the thickness of the border and the color
    There are only a few attributes for the border widget.

    The following attributes are additional attributes to common widget attributes
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "BORDER". Capital letters!
    |-
    |backgroundcolor
    |The background color of the border in hexadecimal RGBA format. It has to start with a pound sign (eg: #ff00ffff). Please use only low capital chars.
    |-
    |linewidth
    |The width of the line, should be a percentage with the same systax os for the width attribute

    |}</div>

    Below you see an example for a rectangle
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="Border 1" type="BORDER" posx="%70" posy="%10" width="%8" height="of:width:self:*1.2"  backgroundcolor='#00FF0040'  />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.uLineWidth: str    = u''
        self.iLineWidth: int = 1

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """

        bRet:bool=self.ParseXMLBaseNode(oXMLNode, oParentScreenPage, uAnchor)
        if bRet:
            self.uLineWidth  = GetXMLTextAttributeVar(oXMLNode,u'linewidth',    False,"1.0")
            if self.uBackGroundColor=="#00000000":
                self.aBackGroundColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('color border')

            fPercentage:float=-1.0
            if not self.uLineWidth==u'':
                if self.uLineWidth.startswith('of:'):
                    self.iLineWidth=self._ParseDimPosValue(self.uLineWidth)
                elif self.uLineWidth[0]==u'%':
                    fPercentage=ToFloat(self.uLineWidth[1:])
                elif self.uLineWidth[0]==u'd':
                   self.iLineWidth=dp(ToInt(self.uLineWidth[1:]))+self.iAnchorPosX
                else:
                    self.iLineWidth=ToInt(self.uLineWidth)
            if not fPercentage == -1.0:
                self.iLineWidth = ToInt(self.iAnchorPosX + ((fPercentage / 100) * self.iAnchorWidth) - (self.iWidth * (fPercentage / 100)))
            self.iLineWidth = max(1,self.iLineWidth)

        return bRet

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        self.AddArg('background_color',self.aBackGroundColor)
        self.AddArg('linewidth',str(self.iLineWidth))
        if self.CreateBase(Parent=oParent, Class=cBorder):
            self.oParent.add_widget(self.oObject)
            return True
        return False
