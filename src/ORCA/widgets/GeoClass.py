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

from ORCA.widgets.Base              import cWidgetBase
from ORCA.vars.Replace              import ReplaceVars

__all__ = ['cWidgetGeoClass']

class cWidgetGeoClass(cWidgetBase):
    """ base class for circles and rectangles """
    def __init__(self,**kwargs):
        super(cWidgetGeoClass, self).__init__(**kwargs)
        self.oGeoClass=None

    def InitWidgetFromXml(self,oXMLNode,oParentScreenPage, uAnchor):
        """ Reads further Widget attributes from a xml node """
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Create(self,oParent):
        """ creates the Widget """
        self.AddArg('background_color',self.tBackGroundColor)
        if self.CreateBase(Parent=oParent, Class=self.oGeoClass):
            if self.uActionName !=u'' or self.uActionNameDoubleTap !=u'' :
                self.oObject.bind(on_q_release  = self.On_Button_Up)
                self.oObject.bind(on_q_press    = self.On_Button_Down)
            self.oObject.bind(on_gesture=self.On_Gesture)
            self.oParent.add_widget(self.oObject)
            return True
        return False

    def SetWidgetColor(self,uBackgroundColor):
        super(cWidgetGeoClass, self).SetWidgetColor(uBackgroundColor)
        if self.oObject:
            self.oObject.SetColor(self.tBackGroundColor)

    def UpdateWidget(self):
        uBackgroundColor=ReplaceVars(self.uBackGroundColor)
        self.SetWidgetColor(uBackgroundColor)
