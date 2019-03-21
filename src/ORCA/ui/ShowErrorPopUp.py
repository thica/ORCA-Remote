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

import traceback

from ORCA.ui.RaiseQuestion          import cRaiseQuestion
from ORCA.utils.wait.StartWait      import StartWait
from ORCA.utils.wait.StopWait       import StopWait

import ORCA.Globals as Globals

__all__ = ['ShowErrorPopUp','ShowMessagePopUp']

class cShowErrorPopUp(cRaiseQuestion):
    """ Class to show an error popup """
    def ShowError(self,uTitle='',uMessage='',bAbort=False,uTextContinue='',uTextQuit='',uStringDetails=u''):
        """Show an Error Message as Popup

        sTitle:      Title for Popup
        sMessage:    Message to Show
        bAbort:      Terminates application after showing the popup (User decision)
        Returns:     Nothing
        """

        StartWait()

        if bAbort:
            self.RaiseQuestion(uTitle=uTitle,uMessage=uMessage, fktYes=self.fktContinue,fktNo=self.fktErrorPopUpClose,uStringYes= uTextContinue,uStringNo = uTextQuit,uStringDetails=uStringDetails)
        else:
            self.RaiseQuestion(uTitle=uTitle,uMessage=uMessage, fktYes=self.fktContinue,uStringYes=uTextContinue,uStringDetails=uStringDetails)
        return

    def fktErrorPopUpClose(self, *largs):
        """ Stops ORCA on user request """
        Globals.oApp.StopApp()

    def fktContinue(self, *largs):
        """ Stops waiting and continues ORCA """
        StopWait()

def ShowErrorPopUp(uTitle='$lvar(5017)',uMessage=u'',bAbort=False,uTextContinue=u'$lvar(5000)',uTextQuit=u'$lvar(5005)',uStringDetails=u''):
    """ Convinience function """
    oShowErrorPopUp     = cShowErrorPopUp()

    if uStringDetails==u'':
        uStringDetails=traceback.format_exc()

    Globals.oSound.PlaySound(u'error')
    oShowErrorPopUp.ShowError(uTitle=uTitle, uMessage=uMessage, bAbort=bAbort, uTextContinue=uTextContinue, uTextQuit=uTextQuit,uStringDetails=uStringDetails)
    return oShowErrorPopUp

def ShowMessagePopUp(uTitle=u'$lvar(5010)',uMessage=u'',uTextContinue=u'$lvar(5000)',uTextQuit=u'$lvar(5005)'):
    """ Convinience function """
    oShowErrorPopUp     = cShowErrorPopUp()
    Globals.oSound.PlaySound(u'message')
    oShowErrorPopUp.ShowError(uTitle=uTitle, uMessage=uMessage, bAbort=False, uTextContinue=uTextContinue, uTextQuit=uTextQuit)
    return oShowErrorPopUp
