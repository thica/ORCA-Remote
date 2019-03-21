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


from kivy.uix.widget                    import Widget
from kivy.graphics                      import Color
from kivy.graphics                      import Ellipse
from ORCA.widgets.core.ButtonBehaviour  import cOrcaButtonBehaviour
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs

__all__ = ['cTouchCircle']

class cTouchCircle(cOrcaButtonBehaviour,Widget):
    def __init__(self,**kwargs):
        self.tBackGroundColor=kwargs['background_color']
        Widget.__init__(self,**RemoveNoClassArgs(kwargs,Widget))
        cOrcaButtonBehaviour.__init__(self,**kwargs)
        # create the graphics
        with self.canvas:
            Color(self.tBackGroundColor[0],self.tBackGroundColor[1], self.tBackGroundColor[2],self.tBackGroundColor[3])
            self.rect_bg = Ellipse( pos=self.pos, size=self.size, angle_end=kwargs['angle_end'], angle_start=kwargs['angle_start'], source=kwargs['source'])

        self.bind(pos=self.update_graphics_pos,size=self.update_graphics_size)

    def update_graphics_pos(self, instance, value):
        self.rect_bg.pos = value

    def update_graphics_size(self, instance, value):
        self.rect_bg.size = value

    def SetColor(self,tBackGroundColor):
        self.tBackGroundColor=tBackGroundColor
        with self.canvas:
            self.canvas.clear()
            Color(self.tBackGroundColor[0],self.tBackGroundColor[1], self.tBackGroundColor[2],self.tBackGroundColor[3])
            self.rect_bg = Ellipse( pos=self.pos, size=self.size)
    def ModifyAngle(self,**kwargs):
        with self.canvas:
            self.canvas.clear()
            Color(self.tBackGroundColor[0],self.tBackGroundColor[1], self.tBackGroundColor[2],self.tBackGroundColor[3])
            self.rect_bg = Ellipse( pos=self.pos, size=self.size, angle_end=kwargs['angle_end'], angle_start=kwargs['angle_start'], source=kwargs['source'])


