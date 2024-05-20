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

from typing                             import Tuple
from kivy.uix.label                     import Label
from kivy.graphics                      import Color
from kivy.graphics                      import Rectangle
from kivy.properties                    import ListProperty

from ORCA.widgets.core.ButtonBehaviour  import cOrcaButtonBehaviour
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs
__all__ = ['cLabel']


# noinspection PyUnusedLocal
class cLabel(cOrcaButtonBehaviour,Label):
    """ base class for a label """

    # noinspection PyArgumentList
    background_color = ListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):

        Label.__init__(self,**RemoveNoClassArgs(dInArgs=kwargs,oObject=Label))
        cOrcaButtonBehaviour.__init__(self,**kwargs)

        if 'background_color' in kwargs:
            self.background_color=kwargs['background_color']

        if not self.background_color==[0, 0, 0, 0]:
            with self.canvas.before:
                Color(self.background_color[0],self.background_color[1], self.background_color[2],self.background_color[3])
                self.rect_bg = Rectangle(size=self.size,pos=self.pos)
            self.bind(pos=self.update_graphics_pos,size=self.update_graphics_size)

    def update_graphics_pos(self, instance, value:Tuple) -> None:
        """ Update the label after position change """
        self.rect_bg.pos = value

    def update_graphics_size(self, instance, value:Tuple)  -> None:
        """ Update the label after size change """
        self.rect_bg.size = value

    def on_touch_up(self, touch) -> bool:
        """ handles the touch event """
        if cOrcaButtonBehaviour.on_touch_up(self,touch):
            Label.on_touch_up(self,touch)
            return True
        else:
            return Label.on_touch_up(self,touch)
