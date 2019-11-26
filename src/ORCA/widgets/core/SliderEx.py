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

from typing import Union
from typing import Tuple
from kivy.metrics           import sp

from kivy.uix.slider        import Slider
from kivy.uix.label         import Label
from kivy.graphics          import BorderImage
from kivy.graphics          import Color
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs
import ORCA.Globals as Globals

__all__ = ['cSliderEx']


class cSliderEx(Slider):
    def __init__(self, **kwargs):
        self.uBackgroundPic:str             = kwargs['background_pic']
        self.uButtonPic:str                 = kwargs['button_pic']
        self.uMoveType:str                  = u''
        self.oText:Union[Label,None]        = None
        fGap:float
        self.x:float
        self.y:float
        self.fBackGroundSize:float
        tKnobPos:Tuple
        tKnobSize: Tuple
        self.oKnob:BorderImage
        self.oBorderImage:BorderImage
        uText:str

        super().__init__(**RemoveNoClassArgs(kwargs,Slider))
        self.register_event_type('on_slider_moved')
        self.canvas.clear()
        if self.orientation==u'horizontal':
            fGap                     = (self.height - sp(32))/2
            self.x                   = self.x + fGap
            self.fBackGroundSize     = self.height / 4 - fGap * 2
            tKnobPos                 = (self.value_pos[0] - (self.height/2), self.value_pos[1] )
            tKnobSize                = (self.height, self.height)
            self.oKnob               = BorderImage(border=(0, 0, 0, 0),pos= tKnobPos, size= tKnobSize,source=self.uButtonPic)
            self.canvas.add(Color(1., 1., 1.))
            self.oBorderImage:BorderImage = BorderImage(border=(0, 0, 0, 0), pos= (self.x, self.center_y - (self.fBackGroundSize/2)) ,size= (self.width-fGap, self.fBackGroundSize), source=self.uBackgroundPic)
            self.canvas.add(self.oBorderImage)
        else:
            fGap                    = (self.width - sp(32))/2
            self.y                  = self.y + fGap
            self.height             = self.height - fGap * 2
            self.fBackGroundSize    = self.width/4
            tKnobPos                = (self.value_pos[0] , self.value_pos[1] - (self.width/2))
            tKnobSize               = (self.width, self.width)
            self.oKnob              = BorderImage(border=(0, 0, 0, 0),pos= tKnobPos, size= tKnobSize,source=self.uButtonPic)
            self.canvas.add(Color(1., 1., 1.))
            self.oBorderImage       = BorderImage(border=(0, 0, 0, 0), pos= (self.center_x - (self.fBackGroundSize/2), self.y ) ,size= (self.fBackGroundSize, self.height-fGap), source=self.uBackgroundPic)
            self.canvas.add(self.oBorderImage)

        self.canvas.add(self.oKnob)
        uText=kwargs.get('text')
        if uText:
            self.oText=Label(**RemoveNoClassArgs(kwargs,Label))
            self.oText.pos=tKnobPos
            self.oText.size=tKnobSize
            self.add_widget(self.oText)

    def on_slider_moved(self) -> None:
        pass

    # noinspection PyUnusedLocal
    def update_graphics_pos(self, instance, value) -> None:
        self.oBorderImage.pos = value

    # noinspection PyUnusedLocal
    def update_graphics_size(self, instance, value) -> None:
        self.oBorderImage.size = value

    def on_touch_down(self, touch) -> bool:
        if self.collide_point(*touch.pos) and not Globals.oTheScreen.GuiIsBlocked():
            self.uMoveType=u'down'
            Slider.on_touch_down(self,touch)
            touch.grab(self)
            self.UpdateButtonPos()
            return True
        else:
            return super(cSliderEx, self).on_touch_down(touch)

    def on_touch_move(self, touch) -> bool:
        if touch.grab_current is self and not Globals.oTheScreen.GuiIsBlocked():
            self.uMoveType=u'move'
            Slider.on_touch_move(self,touch)
            self.UpdateButtonPos()
            return True
        else:
            return super(cSliderEx, self).on_touch_move(touch)
    def on_touch_up(self, touch) -> bool:
        if touch.grab_current is self and not Globals.oTheScreen.GuiIsBlocked():
            self.uMoveType=u'up'
            Slider.on_touch_up(self,touch)
            self.UpdateButtonPos()
            touch.ungrab(self)
            return True
        else:
            return super(cSliderEx, self).on_touch_up(touch)

    def UpdateButtonPos(self,bNoDispatch=False):
        tNewPos:Tuple
        if self.orientation==u'horizontal':
            tNewPos = self.value_pos[0]- (self.height/2) ,self.value_pos[1]
        else:
            tNewPos = self.value_pos[0] ,self.value_pos[1]- (self.width/2)

        self.oKnob.pos=tNewPos
        if self.oText is not None:
            self.oText.pos=tNewPos
        if not bNoDispatch:
            self.dispatch('on_slider_moved')
    def SetValue(self,fNewValue):
        self.value=fNewValue
        self.UpdateButtonPos(True)

