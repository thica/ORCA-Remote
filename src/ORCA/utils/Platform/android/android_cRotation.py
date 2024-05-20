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

from kivy.logger                           import Logger
from ORCA.Globals import Globals

try:
    # noinspection PyUnresolvedReferences
    from plyer import orientation
    Logger.info('plyer/orientation available')
except Exception as e:
    Logger.info('plyer/orientation not available')


# noinspection PyMethodMayBeStatic
class cRotation:
    """
    Rotation object for Android
    CTH: Reworked to use plyer
    """

    def __init__(self):
        pass

    def lock(self) -> None:
        """ Locks to the current screen orientation. """
        Logger.debug('Android Locking orienation to '+Globals.uDeviceOrientation)

        if Globals.uDeviceOrientation=='landscape':
            orientation.set_landscape()
        else:
            orientation.set_portrait()


    def set_landscape(self) -> None:
        """
        Asks the activity to take a landscape orientation.
        """

        orientation.set_landscape()

    def set_portrait(self) -> None:
        """
        Asks the activity to take a portrait orientation.
        """

        orientation.set_portrait()

