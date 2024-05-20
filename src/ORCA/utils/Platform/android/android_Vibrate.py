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

# This is an replacement for the broken plyer code
# can be removed, if plyer is working again

'''Implementation Vibrator for Android.'''


try:
    from kivy.logger                          import Logger
    # noinspection PyUnresolvedReferences
    from jnius                                import autoclass
    # noinspection PyUnresolvedReferences
    from plyer.platforms.android              import activity
    # noinspection PyUnresolvedReferences
    from plyer                                import vibrator as Vibrator

    Context             = autoclass('android.content.Context')
    vibrator            = activity.getSystemService(Context.VIBRATOR_SERVICE)
    VibrationEffect     = autoclass('android.os.VibrationEffect')
except Exception as e1:
    Logger.error('Can\'t load Android Vibrator from jnius:'+str(e1))

from ORCA.Globals import Globals

def Vibrate(fDuration:float=0.05) -> None:
    """ Vibrates a device """

    if Globals.bVibrate:
        try:
            Vibrator.vibrate(fDuration)
        except Exception:
            try:
                vibrator.vibrate(VibrationEffect.createOneShot(1000 * fDuration, VibrationEffect.DEFAULT_AMPLITUDE))
            except Exception as e:
                Logger.error('Error in Vibrate:'+str(e))
