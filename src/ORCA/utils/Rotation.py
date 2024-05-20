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

from kivy.logger            import Logger
from ORCA.utils.Platform    import OS_GetRotationObject

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.utils.Platform.generic.generic_cRotation import cRotation
else:
    from typing import TypeVar
    cRotation   = TypeVar('cRotation')

__all__ = ['cRotationLayer']

class cRotationLayer:
    """ Rotation abstraction layer """
    def __init__(self):
        Logger.debug ('Loading Orientation Support' )
        self.bLocked:bool = False
        self.oRotation:cRotation = OS_GetRotationObject()
    def Lock(self):
        """ Locks the rotation on a device """
        Logger.debug ('Orientation Lock' )
        if self.oRotation:
            self.oRotation.lock()
        self.bLocked = True
    def SetOrientation_Landscape(self):
        """rotate a device to landscape """
        Logger.debug ('SetOrientation_Landscape' )
        if self.oRotation:
            self.oRotation.set_landscape()
    def SetOrientation_Portrait(self):
        """rotate a device to portrait """
        Logger.debug ('SetOrientation_Portrait' )
        if self.oRotation:
            self.oRotation.set_portrait()

