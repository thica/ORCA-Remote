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
from datetime                           import datetime
from datetime                           import timedelta
from kivy.logger                        import Logger
from ORCA.utils.Sleep                   import fSleep
import ORCA.utils.wait.Globals

__all__ = ['StartWait']

def StartWait(iWaitTime:int=-1) -> None:
    """
    wait function for interfaces / and to stop the queue if necessary
    iWaitTime 0: Stops Wait and let the status pass thought
    iWaittime -1: Sets the App on Pause
    iWaittime > 0: Holds the queue for the given time
    """

    if iWaitTime == -1:
        ORCA.utils.wait.Globals.bOnPause = True
        Logger.debug("System start wait")
        return

    ORCA.utils.wait.Globals.oWaitLock.acquire()  # will block if lock is already held

    if iWaitTime == 0:
        ORCA.utils.wait.Globals.oWaitEndTime = ORCA.utils.wait.Globals.oWaitZeroTime
        fSleep(fSeconds=0.01)
    else:
        ORCA.utils.wait.Globals.oWaitEndTime = datetime.now() + timedelta(milliseconds=iWaitTime)

    ORCA.utils.wait.Globals.oWaitLock.release()
