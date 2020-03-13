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
from typing                             import Tuple
from kivy.uix.widget                    import Widget
from kivy.graphics                      import Color
from kivy.graphics                      import Ellipse
from ORCA.widgets.core.ButtonBehaviour  import cOrcaButtonBehaviour
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs

__all__ = ['cTouchCircle']

class cTouchCircle(cOrcaButtonBehaviour,Widget):
    def __init__(self,**kwargs):
        self.aBackGroundColor:List[float] = kwargs['background_color']
        Widget.__init__(self,**RemoveNoClassArgs(dInArgs=kwargs,oObject=Widget))
        cOrcaButtonBehaviour.__init__(self,**kwargs)
        # create the graphics
        with self.canvas:
            Color(self.aBackGroundColor[0],self.aBackGroundColor[1], self.aBackGroundColor[2],self.aBackGroundColor[3])
            self.rect_bg = Ellipse( pos=self.pos, size=self.size, angle_end=kwargs['angle_end'], angle_start=kwargs['angle_start'], source=kwargs['source'])

        self.bind(pos=self.update_graphics_pos,size=self.update_graphics_size)

    # noinspection PyUnusedLocal
    def update_graphics_pos(self, instance:Widget, value:Tuple) -> None:
        self.rect_bg.pos = value

    # noinspection PyUnusedLocal
    def update_graphics_size(self, instance:Widget, value:Tuple) -> None:
        self.rect_bg.size = value

    def SetColor(self,aBackGroundColor:List[float]) -> None:
        self.aBackGroundColor=aBackGroundColor
        with self.canvas:
            self.canvas.clear()
            Color(self.aBackGroundColor[0],self.aBackGroundColor[1], self.aBackGroundColor[2],self.aBackGroundColor[3])
            self.rect_bg = Ellipse( pos=self.pos, size=self.size)
    def ModifyAngle(self,**kwargs) -> None:
        with self.canvas:
            self.canvas.clear()
            Color(self.aBackGroundColor[0],self.aBackGroundColor[1], self.aBackGroundColor[2],self.aBackGroundColor[3])
            self.rect_bg = Ellipse( pos=self.pos, size=self.size, angle_end=kwargs['angle_end'], angle_start=kwargs['angle_start'], source=kwargs['source'])


