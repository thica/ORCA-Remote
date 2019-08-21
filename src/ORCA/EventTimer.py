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

from kivy.clock                 import Clock
from kivy.logger                import Logger
from ORCA.utils.wait.IsWaiting  import IsWaiting

import ORCA.Globals as Globals

__all__ = ['cCustomTimer', 'cAllTimer']

class cAllTimer(object):
    """ Object for all event timer """
    aCustomTimer= {}
    def HasTimer(self,uTimerName):
        """ returns, if a timer exists"""
        return cAllTimer.aCustomTimer.get(uTimerName) is not None
    def AddTimer(self,uTimerName,oTimer):
        """ Adds a timer object """
        cAllTimer.aCustomTimer[uTimerName]=oTimer
    def DeleteTimer(self,uTimerName):
        """ Deletes a timer objects"""
        if self.HasTimer(uTimerName):
            cAllTimer.aCustomTimer[uTimerName].StopTimer()
            del cAllTimer.aCustomTimer[uTimerName]
    def DeleteAllTimer(self):
        """ Deletes all timer """
        if Clock is not None:
            for uTimerName in cAllTimer.aCustomTimer:
                cAllTimer.aCustomTimer[uTimerName].StopTimer()
        cAllTimer.aCustomTimer.clear()

class cCustomTimer(object):
    """ a single timer object """
    def __init__(self, uTimerName, uActionName, fTimerIntervall):
        self.uTimerName       = uTimerName
        self.uActionName      = uActionName
        self.fTimerIntervall  = fTimerIntervall
        self.bStopped         = False

    def StartTimer(self):
        """ starts the timer """
        Clock.schedule_interval(self.DoTimer,self.fTimerIntervall)
    def StopTimer(self):
        """ stops the timer """
        Clock.unschedule(self.DoTimer)
        self.bStopped         = True

    def DoTimer(self,*largs):
        """ executes the timer """
        if IsWaiting():
            return True

        aActions=Globals.oActions.GetActionList(uActionName = self.uActionName, bNoCopy = False)
        if aActions is None:
            aActions = Globals.oEvents.CreateSimpleActionList([{'string': self.uActionName, 'name': self.uActionName, "force":True}])

        Globals.oEvents.ExecuteActions(aActions=aActions, oParentWidget=None)
        return True
