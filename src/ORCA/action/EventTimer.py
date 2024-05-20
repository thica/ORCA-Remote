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
from __future__                 import annotations

from typing                     import Dict
from typing                     import List
from kivy.clock                 import Clock
from ORCA.utils.wait.IsWaiting  import IsWaiting

from ORCA.Globals import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.action.Action import cAction
else:
    from typing import TypeVar
    cAction = TypeVar('cAction')

__all__ = ['cCustomTimer', 'cAllTimer']


# noinspection PyMethodMayBeStatic
class cAllTimer:
    """ Object for all event timer """
    aCustomTimer:Dict[str,cCustomTimer] = {}
    def HasTimer(self,*,uTimerName:str) -> bool:
        """ returns, if a timer exists"""
        return cAllTimer.aCustomTimer.get(uTimerName) is not None

    def AddTimer(self,*,uTimerName:str,oTimer:cCustomTimer) -> None:
        """ Adds a timer object """
        cAllTimer.aCustomTimer[uTimerName]=oTimer

    def DeleteTimer(self,*,uTimerName:str) -> None:
        """ Deletes a timer objects"""
        if self.HasTimer(uTimerName=uTimerName):
            cAllTimer.aCustomTimer[uTimerName].StopTimer()
            del cAllTimer.aCustomTimer[uTimerName]

    def DeleteAllTimer(self) -> None:
        """ Deletes all timer """
        if Clock is not None:
            for uTimerName in cAllTimer.aCustomTimer:
                cAllTimer.aCustomTimer[uTimerName].StopTimer()
        cAllTimer.aCustomTimer.clear()

class cCustomTimer:
    """ a single timer object """
    def __init__(self,*,uTimerName:str, uActionName:str, fTimerIntervall:float, bDoOnPause:bool):
        self.uTimerName:str         = uTimerName
        self.uActionName:str        = uActionName
        self.fTimerIntervall:float  = fTimerIntervall
        self.bStopped:bool          = False
        self.bDoOnPause:bool        = bDoOnPause

    def StartTimer(self) -> None:
        """ starts the timer """
        Clock.schedule_interval(self.DoTimer,self.fTimerIntervall)

    def StopTimer(self) -> None:
        """ stops the timer """
        Clock.unschedule(self.DoTimer)
        self.bStopped         = True

    # noinspection PyUnusedLocal
    def DoTimer(self,*largs) -> bool:
        """ executes the timer """
        if IsWaiting():
            if not self.bDoOnPause:
                return True

        aActions:List[cAction]=Globals.oActions.GetActionList(uActionName = self.uActionName, bNoCopy = False)
        if aActions is None:
            aActions = Globals.oEvents.CreateSimpleActionList(aActions=[{'string': self.uActionName, 'name': self.uActionName, 'force':True}])

        #Globals.oEvents.ExecuteActions(aActions=aActions, oParentWidget=None)
        Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions, oParentWidget=None, bForce=self.bDoOnPause,uQueueName="DoTimer")
        return True
