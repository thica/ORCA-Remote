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

from kivy.logger             import Logger
from ORCA.utils.TypeConvert  import ToUnicode
import ORCA.Globals as Globals

try:
    # noinspection PyUnresolvedReferences
    from   plyer                 import vibrator
    Logger.info("plyer/vibrator available")
except Exception as e:
    Logger.info("plyer/vibrator not available")


def Vibrate(fDuration:float=0.05) -> bool:
    """ Vibrates a device """
    if Globals.bVibrate:
        try:
            vibrator.vibrate(fDuration)
        except NotImplementedError:
            pass
        except Exception as ex:
            uMsg=u'Globals: can\'t Vibrate:'+ToUnicode(ex)
            Logger.info (uMsg)
            return False
    return True