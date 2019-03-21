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

from math                           import radians, degrees
from kivy.uix.scatter               import Scatter
from kivy.vector                    import Vector
from kivy.graphics.transformation   import Matrix
from ORCA.utils.RemoveNoClassArgs   import RemoveNoClassArgs

__all__ = ['cRotateScatter']

class cRotateScatter(Scatter):
    """ base class for a rotate scatter """
    def __init__(self, **kwargs):
        super(cRotateScatter, self).__init__(**RemoveNoClassArgs(kwargs,Scatter))
        self.register_event_type('on_widget_turned')
        self.bInit                  = False
        self.fTotalAngle            = 0.0
        self.iAngle                 = 0
        self.iLeftBoundaryAngle     = 0
        self.iRightBoundaryAngle    = 0
        self.uDirection             = u'right'
        self.iRightBoundaryAngle    = 90
        self.uMoveType              = ''
        self.xx=0
        self.yy=0

    def on_widget_turned(self):
        """ dummy """
        pass
    def transform_with_touch(self, touch):
        self.uMoveType =u'move'
        self.On_Rotate(touch)
    def on_touch_up(self, touch):
        # no need for test on colloide as we might get the up outside of the button
        self.uMoveType =u'up'
        self.On_Rotate(touch)
        return super(cRotateScatter, self).on_touch_up(touch)

    def On_Rotate(self, touch):
        """ handles the rotation event """
        if not self.bInit:
            self.xx=self.x
            self.yy=self.y
            self.bInit=True

        points = [Vector(self._last_touch_pos[t]) for t in self._touches]
        if len(points)==0:
            # LogError(u'cRotateScatter: On_Rotate shouldnt get called')
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

    def SetValueSub(self, iRad):
        """ Sets the value """
        if self.iLeftBoundaryAngle!=self.iRightBoundaryAngle:
            iCheckAngle=int(degrees(self.fTotalAngle+iRad)*-1)
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

        if iRad>0:
            self.uDirection=u'left'
        else:
            self.uDirection=u'right'
        self.fTotalAngle=self.fTotalAngle+iRad
        self.iAngle=int(degrees(self.fTotalAngle))*-1
        anchor=(self.xx+self.width/2,self.yy+self.height/2)

        '''
        print 'Angle:',self.fTotalAngle
        print 'Angle:', int(self.fTotalAngle*-57.5)
        print 'Angle:', degrees(self.fTotalAngle)*-1
        self.iAngle=int(degrees(self.fTotalAngle)*-1)
        print 'Angle:',self.iAngle
        '''
        self.apply_transform(Matrix().rotate(iRad, 0, 0, 1), anchor=anchor)

    def SetValue(self, iNewDegree):
        """ sets the value """
        if not self.bInit:
            self.xx=self.x
            self.yy=self.y
            self.bInit=True
        iCurrentAngle=degrees(self.fTotalAngle)*-1
        iDelta=iCurrentAngle-iNewDegree
        iRadDelta=radians(iDelta)
        self.SetValueSub(iRadDelta)
