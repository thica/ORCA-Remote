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
from ORCA.widgets.base.BaseAction   import cWidgetBaseAction

from ORCA.vars.Replace              import ReplaceVars

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")

__all__ = ['cWidgetGeoClass']

class cWidgetGeoClass(cWidgetBase,cWidgetBaseAction,cWidgetBaseBase):
    """ base class for circles and rectangles """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.oGeoClass=None

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        self.AddArg('background_color',self.aBackGroundColor)
        if self.CreateBase(Parent=oParent, Class=self.oGeoClass):
            if self.uActionName !=u'' or self.uActionNameDoubleTap !=u'' :
                self.oObject.bind(on_q_release  = self.On_Button_Up)
                self.oObject.bind(on_q_press    = self.On_Button_Down)
            self.oObject.bind(on_gesture=self.On_Gesture)
            self.oParent.add_widget(self.oObject)
            return True
        return False

    def SetWidgetColor(self,uBackgroundColor) -> bool:
        super().SetWidgetColor(uBackgroundColor)
        if self.oObject:
            self.oObject.SetColor(self.aBackGroundColor)
        return True

    def UpdateWidget(self):
        self.SetWidgetColor(ReplaceVars(self.uBackGroundColor))
