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

import threading

from kivy.clock                     import Clock
from kivy.logger                    import Logger
from kivy.event                     import EventDispatcher

from ORCA.utils.Sleep               import fSleep
from ORCA.ui.RaiseQuestion          import ShowQuestionPopUp
from ORCA.utils.Platform            import OS_CheckPermissions
from ORCA.utils.Platform            import OS_RequestPermissions
from ORCA.utils.wait.StartWait      import StartWait
from ORCA.utils.wait.StopWait       import StopWait
from ORCA.vars.Access               import ExistLVar

import ORCA.Globals as Globals

__all__ = ['HasPermissions','cCheckPermissions']


# noinspection PyUnusedLocal
def HasPermissions(*largs):
    """ checks, if the device has write permissions """
    Globals.oCheckPermissions.bHasPermissions = OS_CheckPermissions()
    Clock.schedule_once(Globals.oCheckPermissions.on_permissionschecked, 0)

class cCheckPermissions(EventDispatcher):
    """ Waits, unitl we have the permissions """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bCancel: bool         = False
        self.bIsWaiting: bool      = False
        self.bHasPermissions: bool = False
        self.oPopup                = None
        self.oThread               = None
        # noinspection PyUnresolvedReferences
        self.register_event_type('on_checkpermissions_finished')

    # noinspection PyUnusedLocal
    def HasPermissions(self, *largs):
        """ sub function to test, if we have permissions """
        self.bHasPermissions = OS_CheckPermissions()
        # noinspection PyUnresolvedReferences
        self.dispatch('on_permissionschecked')

    # noinspection PyUnusedLocal
    def on_permissionschecked(self, *largs):
        """ called, wehn the tsated has been checked """
        # Logger.debug("Checking permissions")
        if not self.bIsWaiting:
            return
        if not self.bHasPermissions:
            Clock.schedule_once(self.StartNextThread, 0)
            fSleep(fSeconds=0.6)
            return
        self.StopWait()

    # noinspection PyUnusedLocal
    def StartNextThread(self,*largs):
        """ Starts the next thread to check, if online """
        #Logger.debug("Checking for network connectivity start thread")
        #fSleep(0.01)
        #Clock.schedule_once(IsOnline, 0)
        #return

        if self.oThread is not None:
            self.oThread.join()

        self.oThread = threading.Thread(target=HasPermissions(), name="CheckPermissionsThread")
        self.oThread.start()

    def Wait(self):
        """ Main entry point to wait """

        Logger.debug("Checking for permissions")
        self.bIsWaiting    = True
        self.bCancel       = False
        self.bHasPermissions = OS_CheckPermissions()
        if self.bHasPermissions:
            Globals.bHasPermissions=True
            return True

        StartWait()

        bLangLoaded: bool = ExistLVar('5042')
        if bLangLoaded:
            uMessage: str    = u'$lvar(5042)'
            uGrant: str      = u'$lvar(5043)'
        else:
            uMessage: str    = "ORCA requires write access, please grant"
            uGrant: str      = "Grant Access"

        self.oPopup=ShowQuestionPopUp(uTitle=u'$lvar(5010)',uMessage= uMessage,fktYes=self.GrantAccess,fktNo=self.StopApp,uStringYes=uGrant,uStringNo=u'$lvar(5005)',uSound= u'message')
        Clock.schedule_once(self.StartNextThread, 0)
        return False

    def StopWait(self):
        """ MAin entry point to stop waiting """
        if self.oPopup:
            self.oPopup.ClosePopup()

        Globals.bHasPermissions = self.bHasPermissions
        self.CancelCheckPermissions()

    # noinspection PyUnusedLocal
    def CancelCheckPermissions(self, *largs):
        """ Called, when the user pushes the cancel button """
        if self.oThread is not None:
            self.oThread.join()
        self.bCancel    = True
        self.bIsWaiting = False
        self.oPopup     = None
        StopWait()
        self.bIsWaiting = False#
        # noinspection PyUnresolvedReferences
        self.dispatch('on_checkpermissions_finished')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def StopApp(self, *largs):
        Globals.oApp.StopApp()
        pass

    # noinspection PyUnusedLocal
    def GrantAccess(self, *largs):
        """ Called, when the user pushes the grant accces button """
        self.StopWait()
        self.Wait()
        OS_RequestPermissions()
        return

    def on_checkpermissions_finished(self):
        """  Dummy for the event dispatcher """
        pass
