# -*- coding: utf-8 -*

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
from typing                             import Callable
from xml.etree.ElementTree              import Element
from kivy.logger                        import Logger
from kivy.uix.widget                    import Widget
from ORCA.widgets.GeoClass              import cWidgetGeoClass
from ORCA.widgets.core.TouchCircle      import cTouchCircle
from ORCA.utils.Atlas                   import ToAtlas
from ORCA.utils.XML                     import GetXMLFloatAttributeVar
from ORCA.utils.XML                     import GetXMLTextAttributeVar
from ORCA.utils.FileName                import cFileName
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")

__all__ = ['cWidgetCircle']

class cWidgetCircle(cWidgetGeoClass):

    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-CIRCLE
    WikiDoc:TOCTitle:Circle
    = Circle =
    The circle widget creates a colored circle or ellipse.
    You could add click/double click and wipe actions as well. Below you see an example for  a circle

    The following attributes are additional attributes to common widget attributes
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "CIRCLE". Capital letters!
    |-
    |backgroundcolor
    |The background color of the circle in hexadecimal RGBA format. It has to start with a pound sign (eg: #ff00ffff). Please use only low capital chars.
    |-
    |startangle
    |If you don't want to have a full circle, and just want a have a part of the cake, you can set the starting angle of the circle here
    |-
    |stopangle
    |If you don't want to have a full circle, and just want a have a part of the cake, you can set the stop angle of the circle here
    |-
    |picturenormal
    |Instead of a color, you can use a picture as a circle background, For that, give the picturename here
    |}</div>

    Below you see an example for a circle
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="Colorcicle" type="CIRCLE" posx="center" posy="top" width="%50"  height="of:width:self" backgroundcolor='#000000ff' />
    <element name="Picturecircle" type="CIRCLE" posx="%80" posy="%65" width="%8" height="of:width:self:*1.2" backgroundcolor='#FFFFFFFF' startangle='45' stopangle='120' picturenormal="button round normal"/>
    </syntaxhighlight></div>
    Note:posx and posy are NOT the center of the circle, thy defines the upper left corner.
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.oGeoClass:Callable      = cTouchCircle
        self.fStartAngle:float       = 0.0
        self.fEndAngle:float         = 360.0
        self.oFnPictureNormal        = cFileName(u"")

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        self.oFnPictureNormal           = cFileName("").ImportFullPath(uFnFullName=GetXMLTextAttributeVar(oXMLNode=oXMLNode,uTag=u'picturenormal',bMandatory=False,uDefault=u''))
        self.fStartAngle                = GetXMLFloatAttributeVar(oXMLNode=oXMLNode,uTag=u'startangle', bMandatory=False, fDefault=0.0)
        self.fEndAngle                  = GetXMLFloatAttributeVar(oXMLNode=oXMLNode,uTag=u'stopangle',  bMandatory=False, fDefault=0.0)
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Create(self,oParent:Widget) -> bool:
        self.AddArg('source',       ToAtlas(oFileName=self.oFnPictureNormal))
        self.AddArg('angle_start',  self.fStartAngle)
        self.AddArg('angle_end',    self.fEndAngle)
        return super(cWidgetCircle, self).Create(oParent)

    def ModifyAngle(self) -> bool:
        """ Modifies the angle """
        self.AddArg('angle_start',  self.fStartAngle)
        self.AddArg('angle_end',    self.fEndAngle)
        if self.oObject is None:
            Logger.error("Can't modify Angle of Circle before its created:"+self.uName)
            return False
        return self.oObject.ModifyAngle(**self.dKwArgs)
    def UpdateWidget(self) -> None:
        super().UpdateWidget()
        if self.oObject is not None:
            self.ModifyAngle()
