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

from math                           import radians, degrees
from kivy.uix.scatter               import Scatter
from kivy.vector                    import Vector
from kivy.graphics.transformation   import Matrix
from ORCA.utils.RemoveNoClassArgs   import RemoveNoClassArgs
from ORCA.Globals import Globals

__all__ = ['cRotateScatter']

class cRotateScatter(Scatter):
    """ base class for a rotate scatter """
    def __init__(self, **kwargs):
        super().__init__(**RemoveNoClassArgs(dInArgs=kwargs,oObject=Scatter))
        self.register_event_type('on_widget_turned')
        self.bInit:bool                 = False
        self.fTotalAngle:float          = 0.0
        self.iAngle:int                 = 0
        self.iLeftBoundaryAngle:int     = 0
        self.iRightBoundaryAngle:int    = 0
        self.uDirection:str             = 'right'
        self.iRightBoundaryAngle:int    = 90
        self.uMoveType:str              = ''
        self.xx:int                     = 0
        self.yy:int                     = 0

    def on_widget_turned(self):
        """ dummy """
        pass
    def transform_with_touch(self, touch):
        self.uMoveType ='move'
        self.On_Rotate(touch)
    def on_touch_up(self, touch):
        # no need for test on collide as we might get the up outside of the button
        if not Globals.oTheScreen.GuiIsBlocked():
            self.uMoveType ='up'
            self.On_Rotate(touch)
            return super(cRotateScatter, self).on_touch_up(touch)
        else:
            return False

    def On_Rotate(self, touch) -> None:
        """ handles the rotation event """

        if Globals.oTheScreen.GuiIsBlocked():
            return

        if not self.bInit:
            self.xx=self.x
            self.yy=self.y
            self.bInit=True

        points = [Vector(self._last_touch_pos[t]) for t in self._touches]
        if len(points)==0:
            # LogError('cRotateScatter: On_Rotate shouldnt get called')
            return

        anchor= Vector(self.xx+self.width/2,self.yy+self.height/2)
        farthest = max(points, key=anchor.distance)
        if points.index(farthest) != self._touches.index(touch):
            return

        old_line = Vector(*touch.ppos) - anchor
        new_line = Vector(*touch.pos) - anchor

        iRad = radians(new_line.angle(old_line)) * self.do_rotation
        self.SetValueSub(iRad)

        self.dispatch('on_widget_turned')

    def SetValueSub(self, fRad:float) -> None:
        """ Sets the value """
        if self.iLeftBoundaryAngle!=self.iRightBoundaryAngle:
            iCheckAngle:int = int(degrees(self.fTotalAngle+fRad)*-1)
            # print iCheckAngle,' ',self.iLeftBoundaryAngle,' ',self.iRightBoundaryAngle
            if self.iRightBoundaryAngle>0:
                if iCheckAngle>self.iRightBoundaryAngle:
                    return
            else:
                if iCheckAngle<self.iRightBoundaryAngle:
                    return
            if self.iLeftBoundaryAngle<0:
                if iCheckAngle<self.iLeftBoundaryAngle:
                    return
            else:
                if iCheckAngle>self.iLeftBoundaryAngle:
                    return

        if fRad>0.0:
            self.uDirection='left'
        else:
            self.uDirection='right'
        self.fTotalAngle += fRad
        self.iAngle       = int(degrees(self.fTotalAngle))*-1
        anchor            = (self.xx+self.width/2,self.yy+self.height/2)

        '''
        print 'Angle:',self.fTotalAngle
        print 'Angle:', int(self.fTotalAngle*-57.5)
        print 'Angle:', degrees(self.fTotalAngle)*-1
        self.iAngle=int(degrees(self.fTotalAngle)*-1)
        print 'Angle:',self.iAngle
        '''
        self.apply_transform(Matrix().rotate(fRad, 0, 0, 1), anchor=anchor)

    def SetValue(self, fNewDegree:float):
        """ sets the value """
        if not self.bInit:
            self.xx     = self.x
            self.yy     = self.y
            self.bInit  = True
        fCurrentAngle:float = degrees(self.fTotalAngle)*-1
        fDelta:float        = fCurrentAngle-fNewDegree
        fRadDelta:float     = radians(fDelta)
        self.SetValueSub(fRadDelta)
