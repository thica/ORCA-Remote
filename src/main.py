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

from kivy.logger    import Logger
from ORCA.App       import ORCA_App


ORCA = None
try:
    ORCA = ORCA_App()
    if __name__ in ('__android__', '__main__'):
        ORCA.run()
except Exception as exception:
    uMsg = 'ORCA:Unexpected error:'+ str(exception)
    Logger.critical(uMsg)
    uMsg = traceback.format_exc()
    Logger.critical(uMsg)
    if ORCA:
        ORCA.StopApp()
