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
import kivy.core.window
import ORCA.Globals as Globals

class cRotation(object):
    """ Rotation object for Windows based OS"""
    def __init__(self):
        self.bLocked=False
    def set_landscape(self):
        """ sets landscape (changes x/y values) """
        if Globals.iAppWidth<Globals.iAppHeight:
            self.DoRotate()
    def DoRotate(self):
        """ rotates to the required rotation """
        if not self.bLocked:
            Globals.iAppWidth,Globals.iAppHeight = Globals.iAppHeight, Globals.iAppWidth,
            kivy.core.window.Window.size=(Globals.iAppWidth,Globals.iAppHeight)
            for oDef in Globals.oDefinitions:
                oDef.fRationX,oDef.fRationY = oDef.fRationY,oDef.fRationX
    def set_portrait(self):
        """ sets portrait (changes x/y values) """
        if Globals.iAppWidth>Globals.iAppHeight:
            self.DoRotate()
    def lock(self):
        """ dummy """
        self.bLocked=True
