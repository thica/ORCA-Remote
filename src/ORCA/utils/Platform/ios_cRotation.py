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

from   kivy.logger           import Logger

try:
    from pyobjus import autoclassios
    from pyobjus.dylib_manager import load_framework
    Logger.debug("Sucessfully loaded autoclass, detach")
except Exception as e:
    Logger.error("Not able to load autoclassios" + str(e))

import ORCA.Globals as Globals

class cRotation(object):
    """ Rotation Object for IOS untested    """
    def __init__(self):
        try:

            load_framework('/System/Library/Frameworks/UIKit.framework')
            UIDevice = autoclassios('UIDevice')
            self.UIDevice = UIDevice.alloc().init()

            NSSelectorFromString = autoclassios('NSSelectorFromString')
            self.NSString = NSSelectorFromString.alloc().init()
        except Exception as e:
            Logger.error("Orca is not supporting rotation on this IOS Version:"+str(e))

            '''
            if (self.interfaceOrientation != UIInterfaceOrientationPortrait) {
                // http://stackoverflow.com/questions/181780/is-there-a-documented-way-to-set-the-iphone-orientation
                // http://openradar.appspot.com/radar?id=697
                // [[UIDevice currentDevice] setOrientation:UIInterfaceOrientationPortrait]; // Using the following code to get around apple's static analysis
                [[UIDevice currentDevice] performSelector:NSSelectorFromString(@"setOrientation:") withObject:(id)UIInterfaceOrientationPortrait];
            '''

    def set_no_preference(self):
        """ untested / unfinished """
        pass
    def lock(self):
        """ untested / unfinished """
        if Globals.uDeviceOrientation=='landscape':
            self.set_landscape()
        else:
            self.set_portrait()

    def set_landscape(self):
        """ untested / unfinished """
        try:
            self.UIDevice.setOrientation(1)
        except Exception as e:
            Logger.error("Orca is not supporting rotation on this IOS Version:"+str(e))
    def set_portrait(self):
        """ untested / unfinished """
        try:
            self.UIDevice.setOrientation(2)
        except Exception as e:
            Logger.error("Orca is not supporting rotation on this IOS Version:"+str(e))

