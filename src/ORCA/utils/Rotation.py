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

from kivy.logger            import Logger

from ORCA.utils.Platform    import OS_GetRotationObject

__all__ = ['cRotation']

class cRotation(object):
    """ Rotation abstraction layer """
    def __init__(self):
        Logger.debug (u'Loading Orientation Support' )
        self.bLocked = False
        self.oRotation = OS_GetRotationObject()
    def Lock(self):
        """ Locks the rotation on a device """
        Logger.debug (u'Orientation Lock' )
        if self.oRotation:
            self.oRotation.lock()
        self.bLocked = True
    def SetOrientation_Landscape(self):
        """rotate a device to landscape """
        Logger.debug (u'SetOrientation_Landscape' )
        if self.oRotation:
            self.oRotation.set_landscape()
    def SetOrientation_Portrait(self):
        """rotate a device to portrait """
        Logger.debug (u'SetOrientation_Portrait' )
        if self.oRotation:
            self.oRotation.set_portrait()

