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
from kivy.graphics                      import Line

from ORCA.utils.RemoveNoClassArgs          import RemoveNoClassArgs

__all__ = ['cBorder']

class cBorder(Widget):
    """ Core Widget which draws a border """
    def __init__(self,**kwargs):

        self.tBackGroundColor = kwargs.get('background_color',[0.5,0.5,0.5,1])
        self.fLineWidth       = float(kwargs.get('linewidth','1.0'))

        super(cBorder, self).__init__(**RemoveNoClassArgs(kwargs,cBorder))
        # create the graphics
        self.Create_Border()
        self.bind(pos=self.update_graphics_pos,size=self.update_graphics_size)

    def Create_Border(self):
        """ draws the border """
        with self.canvas:
            Color(self.tBackGroundColor[0],self.tBackGroundColor[1], self.tBackGroundColor[2],self.tBackGroundColor[3])
            self.oLine=Line(points=[self.pos[0],self.pos[1], self.pos[0]+self.width, self.pos[1],self.pos[0]+self.width,self.pos[1]+self.height,self.pos[0],self.pos[1]+self.height], close=True)

    def update_graphics_pos(self, instance, value):
        """ Redraws the border, if screen position changes """
        with self.canvas:
            self.canvas.clear()
        self.Create_Border()
        #self.rect_bg.pos = value

    def update_graphics_size(self, instance, value):
        """ Redraws the border, if screen size changes """
        with self.canvas:
            self.canvas.clear()
        self.Create_Border()

        #self.rect_bg.size = value

    def SetColor(self,tBackGroundColor):
        """ Sets the border color """
        self.tBackGroundColor=tBackGroundColor
        with self.canvas:
            self.canvas.clear()
        self.Create_Border()

