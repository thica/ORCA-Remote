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

from kivy.uix.widget import Widget

__all__ = ['SettingSpacer', 'cBasePopup', 'IsPopupActive', 'CloseActivePopup']


class SettingSpacer(Widget):
    """ Internal class, not documented. """
    pass


class cBasePopup(object):
    """  Base class for Application Popups """

    aPopUps = []

    def __init__(self):
        cBasePopup.aPopUps.append(self)
        self.oPopup = None
        self.bPreventCloseOnEscKey = False

    def ClosePopup(self):
        """ closes the popup """
        if self.oPopup:
            # don't use animation, as this conflicts with scheduled init
            self.oPopup.dismiss(animation=False)
        self.oPopup = None
        if self in cBasePopup.aPopUps:
            cBasePopup.aPopUps.remove(self)


def IsPopupActive():
    """ checks, if we already show a popup """
    return not len(cBasePopup.aPopUps) == 0


def CloseActivePopup(oPopUp=None, bTriggeredByESCKey=False):
    """ closes the latest popup """
    if oPopUp is None:
        if not len(cBasePopup.aPopUps) == 0:
            oPopUp = cBasePopup.aPopUps[-1]
            if bTriggeredByESCKey and oPopUp.bPreventCloseOnEscKey:
                return
            oPopUp.ClosePopup()
    else:
        if bTriggeredByESCKey and oPopUp.bPreventCloseOnEscKey:
            return
        oPopUp.ClosePopup()
