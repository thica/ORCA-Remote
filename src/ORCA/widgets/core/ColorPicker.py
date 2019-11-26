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

from typing import Callable
from kivy.uix.colorpicker           import ColorPicker
from ORCA.utils.RemoveNoClassArgs   import RemoveNoClassArgs

__all__ = ['cColorPicker']

class cColorPicker(ColorPicker):
    """ Core Widget for a colorpicker """
    def __init__(self,**kwargs):

        super().__init__(**RemoveNoClassArgs(kwargs,ColorPicker))
        self.register_event_type('on_colorset')
        self.cFktTouchUp:Callable = self.wheel.on_touch_up
        self.wheel.on_touch_up=self.On_TouchUpColorWheel

    def On_TouchUpColorWheel(self,touch) -> None:
        """ action will be scheduled on a colorpicker click """
        self.cFktTouchUp(touch)
        self.dispatch('on_colorset')

    def on_colorset(self,**kwargs) -> None:
        """ dummy """
        pass

    '''
    self.hex_color trigger setzen
    '''

