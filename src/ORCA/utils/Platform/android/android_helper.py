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

from typing import Union, List

from   kivy.logger           import Logger

def GetAndroidModule(uModuleName:str, uParClass:Union[str,None] = None):
    Logger.info("GetAndroidmodule 0")
    if uParClass is not None:
        aClasses: List[str] = [uParClass+'.']
    else:
        aClasses = ['org.renpy.android.','org.kivy.android.']

    oModule      = None
    uLib:str     = ''

    try:
        # noinspection PyUnresolvedReferences
        from jnius import autoclass
        for uClass in aClasses:
            try:
                uLib = uClass + uModuleName
                Logger.debug(f'Try to load Android Lib from {uLib}')
                oModule = autoclass(uLib)
                Logger.debug(f'Successfully loaded Android Lib from {uLib}')
                break
            except Exception:
                pass
        if oModule is None:
            Logger.error(f'Unable able to load Android {uModuleName} Lib [{uLib}]')
    except Exception as e:
        Logger.error(f'Unable able to load Android {uModuleName} [{uLib}] Lib [{str(e)}]')

    return oModule
