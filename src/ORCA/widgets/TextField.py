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
from ORCA.widgets.base.BaseBase     import cWidgetBaseBase
from ORCA.widgets.base.BaseText     import cWidgetBaseText
from ORCA.widgets.base.BaseAction   import cWidgetBaseAction

from ORCA.widgets.core.Label        import cLabel
from ORCA.utils.XML                 import GetXMLBoolAttribute
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")


__all__ = ['cWidgetTextField']

class cWidgetTextField(cWidgetBase,cWidgetBaseText,cWidgetBaseAction,cWidgetBaseBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-TEXTFIELD
    WikiDoc:TOCTitle:TextField
    = TEXTFIELD =

    The textfield widget enable you to place a text on a page
    There are different attributes to control text rendering. Please note: Text attributes are shared with other widgets like buttons as well.
    The following attributes are additional attributes to common widget attributs

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "TEXTFIELD". Capital letters!
    |-
    |htextalign
    |Horizontal text alignment of the text within the widgets rectangle. Could be "left", "center" or "right". Default is "center"
    |-
    |vtextalign
    |Vertical text alignment of the text within the widgets rectangle. Could be "top", "middle" or "bottom". Default is "middle"
    |-
    |bold
    |If set to "1", the font will be displayed as bold font. (If supported by the font)
    |-
    |italic
    |If set to "1", the font will be displayed as italic font. (If supported by the font)
    |-
    |fontid
    |The fontid to use for the font. Please read the fonts section for loading and using fonts. If no fontid is given, the default font from the skin or definiton parameters is used.
    |-
    |fontsize
    |The size for the font. This is a virtual font size, which is scaled to fit to the physical screen. If not fontsize if given, the default skin fontsize is used.
    |-
    |iconfontsize
    |The size for the font if an icon is shown. This is a virtual font size, which is scaled to fit to the physical screen.
    |-
    |textcolor
    |The color of the text in hexedecimal RGBA format. It has to start with a pound sign (eg: #ff00ffff). Please use only low capital chars. If not textcolor if given, the default skin textcolor is used.
    |-
    |caption
    |This defines the text to show. You can use fixed strings, but it is recommended to use a variable , which will be replaced at runtime. If the caption starts with icon: then the icon name follwed the colon is used (eg. icon:help). For icons you can also add a color as well (eg. icon:info color:$var(red) )
    |-
    |clock
    |If you set this attribute to "1", the widget will show the current time. Time format will come from the language settings (in future versions)
    |-
    |date
    |If you set this attribute to "1", the widget will show the current date. Date format wiill come from the language settings (in future versions)
    |}</div>

    Below you see an example for a textfield definition
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Text Volume' type='TEXTFIELD' posx='left' posy='middle' width='%30' height='of:width:self' fontsize='%h20' caption='Volume' />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        self.bIsClock:bool = False
        self.bIsDate:bool = False
        super().__init__()

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        self.bIsClock  = GetXMLBoolAttribute(oXMLNode,u'clock',    False,False)
        self.bIsDate   = GetXMLBoolAttribute(oXMLNode,u'date',    False,False)
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        if self.CreateBase(Parent=oParent,Class=cLabel):
            self.oParent.add_widget(self.oObject)
            self.oObject.bind(on_q_release=self.On_Button_Up)
            self.oObject.bind(on_q_press=self.On_Button_Down)
            self.oObject.bind(on_gesture=self.On_Gesture)
            return True
        return False
