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


from kivy.uix.button                    import Button
from ORCA.widgets.core.ButtonBehaviour  import cOrcaButtonBehaviour
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs

class cTouchButton(cOrcaButtonBehaviour,Button):
    def __init__(self,**kwargs):
        Button.__init__(self,**RemoveNoClassArgs(dInArgs=kwargs,oObject=Button))
        cOrcaButtonBehaviour.__init__(self,**kwargs)

    def on_touch_down(self, touch) -> bool:
        if cOrcaButtonBehaviour.on_touch_down(self,touch):
            Button.on_touch_down(self,touch)
            return True
        else:
            return False

    def on_touch_up(self, touch) -> bool:
        if cOrcaButtonBehaviour.on_touch_up(self,touch):
            Button.on_touch_up(self,touch)
            return True
        else:
            return Button.on_touch_up(self,touch)
