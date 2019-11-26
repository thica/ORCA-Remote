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


from kivy.uix.scrollview                import ScrollView
from kivy.uix.label                     import Label
from kivy.properties                    import StringProperty
from ORCA.widgets.core.TouchRectangle   import cTouchRectangle

__all__ = ['cScrollableLabel']

# noinspection PyUnusedLocal
# not sure, if this is used anymore
class cScrollableLabel(cTouchRectangle):

    text = StringProperty('')
    def __init__(self,**kwargs):

        self.oScrollView    = self
        self.oLabel         = None
        self.aKwArgs        = kwargs
        self.iLineHeight    = 0

        cTouchRectangle.__init__(self,**self.aKwArgs)

        self.aKwArgs['bar_width']=0
        self.oScrollView=ScrollView(**kwargs)
        self.add_widget(self.oScrollView)

        #if self.aKwArgs.has_key('pos'):
        #    del self.aKwArgs['pos']

        #if self.aKwArgs.has_key('size'):
        #    del self.aKwArgs['size']

        self.aKwArgs['text_size']     = (self.aKwArgs['size'][0],None)

        self.aKwArgs['size_hint_y']     = None
        self.aKwArgs['size_hint_x']     = None

        #test
        #self.aKwArgs['text_size']     = self.size
        #self.aKwArgs['valign']     = 'top'


        self.oLabel = Label(**self.aKwArgs)
        self.oLabel.oScrollView=self
        self.oLabel.bind(texture_size=self._set_height)
        self.oScrollView.add_widget(self.oLabel)

        self.oLabel.bind(texture_size=self._set_height)

    def on_pos(self,instance,pos):
        if self.oScrollView is not None:
            self.oScrollView.pos=pos

    def _set_height(self, instance, size):
        instance.height = size[1]
        instance.width = size[0]
        if self.iLineHeight==0:
            self.iLineHeight=instance.height
            if self.iLineHeight>instance.font_size*2:
                self.iLineHeight=instance.font_size**1.128

    def on_text(self, instance, value):
        if self.oLabel is not None:
            self.oLabel.text=value

