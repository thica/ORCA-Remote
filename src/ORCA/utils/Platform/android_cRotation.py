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

from os                                     import environ
from kivy.logger                            import Logger
from jnius                                  import autoclass
from jnius                                  import detach
from jnius                                  import cast
from ORCA.utils.Platform.android_helper     import GetAndroidModule

import ORCA.Globals as Globals

class cRotation(object):
    """
    Rotation object for Android
    CTH: Code adopted from code from Alexander Taylor"
    """

    def __init__(self):
        self.activity = None
        try:

            if 'PYTHON_SERVICE_ARGUMENT' in environ:
                self.PythonService = GetAndroidModule("PythonService")
                self.activity = self.PythonService.mService
            else:
                self.PythonActivity = GetAndroidModule("PythonActivity")
                self.activity = self.PythonActivity.mActivity

            self.ActivityInfo = autoclass('android.content.pm.ActivityInfo')
        except Exception as e:
            Logger.error("Orca is not supporting rotation on this Android Version:"+str(e))
    def set_no_preference(self):
        """ Leaves all orientation choices to the system (activity below, user settings etc.) """
        if self.activity:
            self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED)

    # Doesn't lock....
    def lockOld(self):
        """ Locks to the current screen orientation. """
        try:
            if self.activity:
                self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_LOCKED)
                #self.activity.setRequestedOrientation(14)
        except Exception as e:
            Logger.error("Orca is not supporting lock rotation on this Android Version:"+str(e))

    def lock(self):
        """ Locks to the current screen orientation. """
        Logger.debug("Adroid Locking orienation to "+Globals.uDeviceOrientation)

        if Globals.uDeviceOrientation=='landscape':
            self.set_landscape()
        else:
            self.set_portrait()

    def set_from_behind(self):
        """ Uses the orientation of the activity behind the current one. """
        if self.activity:
            self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_BEHIND)

    def set_landscape(self,mode='normal', user=False):
        """
        Asks the activity to take a landscape orientation. Can optionally
        take either landscape direction, or use sensor information
        with/without listening to user settings.

        :param mode: One of 'normal', 'reverse', 'sensor' or 'user'.
        :param user: If True, tries to obey the user's orientation
                     settings where applicable. Defaults to False.
        """

        if self.activity:
            if mode == 'normal':
                self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE)
            if mode == 'reverse':
                self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_REVERSE_LANDSCAPE)
            if mode == 'sensor':
                if user:
                    self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_USER_LANDSCAPE)
                else:
                    self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE)

    def set_portrait(self,mode='normal', user=False):
        """
        Asks the activity to take a portrait orientation. Can optionally
        take either portrait direction, or use sensor information
        with/without listening to user settings.

        :param mode: One of 'normal', 'reverse', 'sensor' or 'user'.
        :param user: If True, tries to obey the user's orientation
                     settings where applicable. Defaults to False.
        """

        if self.activity:
            if mode == 'normal':
                self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT)
            if mode == 'reverse':
                self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_REVERSE_PORTRAIT)
            if mode == 'sensor':
                if user:
                    self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_USER_PORTRAIT)
                else:
                    self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_SENSOR_PORTRAIT)

    def set_free(self,user=False, full=False):
        """
        Allows any orientation, following the sensors.

        :param user: If True, try to follow the user's orientation
                     settings. Defaults to False.
        :param full: If True, tries to use the full range of orientations
                     even on devices that don't naturally support them.
                     Defaults to False.
        """
        if self.activity:
            if user:
                if full:
                    self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_FULL_USER)
                else:
                    self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_USER)
            else:
                if full:
                    self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_FULL_SENSOR)
                else:
                    self.activity.setRequestedOrientation(self.ActivityInfo.SCREEN_ORIENTATION_SENSOR)

