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


from ORCA.widgets.GeoClass              import cWidgetGeoClass
from ORCA.widgets.core.TouchRectangle   import cTouchRectangle

__all__ = ['cWidgetRectangle']

class cWidgetRectangle(cWidgetGeoClass):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-RECTANGLE
    WikiDoc:TOCTitle:Rectangle
    = RECTANGLE =
    The rectangle widget creates a colored rectangle. You could add click/double click and wipe actions as well.
    There are only a few attributes for the rectangle widget.

    The following attributes are additional attributes to common widget attributes
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "RECTANGLE". Capital letters!
    |-
    |backgroundcolor
    |The background color of the rectangle in hexadecimal RGBA format. It has to start with a pound sign (eg: #ff00ffff). Please use only low capital chars.
    |}</div>

    Below you see an example for a rectangle
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="Rectangle 1" type="RECTANGLE" posx="%70" posy="%10" width="%8" height="of:width:self:*1.2"  backgroundcolor='#00FF0040' />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.oGeoClass=cTouchRectangle
