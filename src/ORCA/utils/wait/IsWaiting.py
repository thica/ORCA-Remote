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
from kivy.logger                        import Logger
from ORCA.utils.Sleep                   import fSleep
import ORCA.utils.wait.Globals

__all__ = ['IsWaiting']

def IsWaiting() -> bool:
    """
    returns if we are in a interface wait state or app wait state
    """

    if ORCA.utils.wait.Globals.bOnPause:
        fSleep(fSeconds=0.001)
        return True

    ORCA.utils.wait.Globals.oWaitLock.acquire()

    if ORCA.utils.wait.Globals.oWaitEndTime == ORCA.utils.wait.Globals.oWaitZeroTime:
        ORCA.utils.wait.Globals.oWaitLock.release()
        return False
    if datetime.now() > ORCA.utils.wait.Globals.oWaitEndTime:
        Logger.warning("Interface waiting timed out!!")
        ORCA.utils.wait.Globals.oWaitEndTime = ORCA.utils.wait.Globals.oWaitZeroTime
        ORCA.utils.wait.Globals.oWaitLock.release()
        return False
    fSleep(fSeconds=0.01)
    ORCA.utils.wait.Globals.oWaitLock.release()
    return True
