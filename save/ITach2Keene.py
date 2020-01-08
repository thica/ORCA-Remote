# -*- coding: utf-8 -*

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


from xml.etree.ElementTree              import Element
from kivy.uix.widget                    import Widget
from ORCA.widgets.Base                  import cWidgetBase
from ORCA.widgets.core.ITach2KeeneCore  import cITachToKeene
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")

__all__ = ['cWidgetITach2Keene']

class cWidgetITach2Keene(cWidgetBase):

    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-ITACH2KEENE
    WikiDoc:TOCTitle:ITach2Keene
    = ITACH2KEENE =

    The ITach2Keene widget converts ITach IR Codes to Keene Kira IR Codes. This is a more like internal widget

    There are no further attributes to the common widget attributes

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "ITACH2KEENE". Capital letters!
    |}</div>

    Below you see an example for a ITAch2Keene widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='ITACH2KEENE' type='ITACH2KEENE' posx="center" posy="middle" width="%90" height="%90" backgroundcolor='#454545ff' />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super(cWidgetITach2Keene, self).__init__(**kwargs)

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        if self.CreateBase(Parent=oParent,Class=cITachToKeene):
            self.oParent.add_widget(self.oObject)
            return True
        return False
