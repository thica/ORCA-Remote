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
from ORCA.widgets.Rectangle         import cWidgetRectangle
from ORCA.widgets.Picture           import cWidgetPicture
import ORCA.Globals as Globals



from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage import cScreenPage
else:
    from typing import TypeVar
    cScreenPage = TypeVar("cScreenPage")


__all__ = ['cWidgetBackGround']

class cWidgetBackGround(cWidgetPicture,cWidgetRectangle):

    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-BACKGROUND
    WikiDoc:TOCTitle:Background
    = BACKGROUND =
    The Background widget creates a background. You can either have a solid color as a background or a picture. Pictures are scaled to fit to the screen.     You can place the background widget everywhere in your page definition, but it is recommended, to place it as the first widget. You could add click/double click and wipe actions as well.
    There are only a few attributes for the background widget.

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "BACKGROUND". Capital letters!
    |-
    |backgroundcolor
    |The background color of the background in hexedecimal RGBA format. It has to start with a pound sign (eg: #ff00ffff). Please use only low capital chars.
    |-
    |picturenormal
    |If you want to use a picture as background, you have to give the name of the picture file including the full path. You should use variables to provide the path to your picture file.
    |}</div>

    Below you see three examples for a background: One with a solid color, one with a dedicated picture as a background and one with the skin default background.

    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Background Main Screen' type='BACKGROUND' picturenormal='$var(SKINPATH)/pics/background.jpg'>
    </syntaxhighlight></div>

    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="Background Main Screen" type="BACKGROUND" picturenormal="background">
    </syntaxhighlight></div>

    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Background Main Screen' type='BACKGROUND' backgroundcolor="#ffffffff">
    </syntaxhighlight></div>
    WikiDoc:End
    """

    ''' Tricky: Background can be a picture or just a color
        We use Rectangle for just a color, as gestures are implemented here '''

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage,uAnchor:str=''):
        bRet1:bool = cWidgetPicture.InitWidgetFromXml(self,oXMLNode,oParentScreenPage, u'')
        bRet2:bool = cWidgetRectangle.InitWidgetFromXml(self,oXMLNode,oParentScreenPage, u'')
        self.iPosX = 0
        self.iPosY = 0
        self.iHeight = Globals.iAppHeight * self.oDef.fRationY
        self.iWidth = Globals.iAppWidth * self.oDef.fRationX

        self.uName = u'Background'
        if bRet1 and bRet2:
            return True
        return False

    def Create(self,oParent:Widget):
        bRet:bool
        if not self.oFnPictureNormal.IsEmpty():
            bRet = cWidgetPicture.Create(self, oParent)
        else:
            bRet= cWidgetRectangle.Create(self, oParent)
        return bRet

