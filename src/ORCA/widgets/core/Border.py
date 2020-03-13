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

from typing                             import List
from typing                             import Union

from kivy.uix.widget                    import Widget
from kivy.graphics                      import Color
from kivy.graphics                      import Line
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs

__all__ = ['cBorder']


# noinspection PyUnusedLocal
class cBorder(Widget):
    """ Core Widget which draws a border """
    def __init__(self,**kwargs):

        self.aBackGroundColor:List[float]                   = kwargs.get('background_color',[0.5,0.5,0.5,1.0])
        self.fLineWidth:float                               = float(kwargs.get('linewidth','1.0'))
        self.oLine:Union[Line,None]                         = None
        super(cBorder, self).__init__(**RemoveNoClassArgs(dInArgs=kwargs,oObject=cBorder))
        # create the graphics
        self.Create_Border()
        self.bind(pos=self.update_graphics_pos,size=self.update_graphics_size)


    def Create_Border(self) -> None:
        """ draws the border """
        with self.canvas:
            Color(self.aBackGroundColor[0],self.aBackGroundColor[1], self.aBackGroundColor[2],self.aBackGroundColor[3])
            # noinspection PyArgumentList
            self.oLine = Line(points=[self.pos[0],self.pos[1], self.pos[0]+self.width, self.pos[1],self.pos[0]+self.width,self.pos[1]+self.height,self.pos[0],self.pos[1]+self.height], close=True, width=self.fLineWidth, cap="none")
            # self.oLine: Line = Line(rectangle=(self.pos[0], self.pos[1],self.width,self.height), width=self.fLineWidth)

    def update_graphics_pos(self, instance, value) -> None:
        """ Redraws the border, if screen position changes """
        with self.canvas:
            self.canvas.clear()
        self.Create_Border()

    def update_graphics_size(self, instance, value) -> None:
        """ Redraws the border, if screen size changes """
        with self.canvas:
            self.canvas.clear()
        self.Create_Border()

        #self.rect_bg.size = value

    def SetColor(self,aBackGroundColor:List[float]):
        """ Sets the border color """
        self.aBackGroundColor=aBackGroundColor
        with self.canvas:
            self.canvas.clear()
        self.Create_Border()
