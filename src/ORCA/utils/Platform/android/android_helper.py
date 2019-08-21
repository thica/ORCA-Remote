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

def GetAndroidModule(uModuleName, uParClass = None):
    if uParClass is not None:
        lClasses = []
        lClasses.append(uParClass+".")
    else:
        lClasses = ('org.kivy.android.','org.renpy.android.')

    oModule  = None
    uLib     = ""

    try:
        # noinspection PyUnresolvedReferences
        from jnius import autoclass

        for uClass in lClasses:
            try:
                uLib = uClass + uModuleName
                Logger.debug("Try to load Android Lib from %s" % uLib)
                oModule = autoclass(uLib)
                Logger.debug("Sucessfully loaded Android Lib from %s" % uLib)
                break
            except Exception:
                pass
        if oModule is None:
            Logger.error("Unable able to load Android %s Lib [%s]" % (uModuleName,uLib))
    except Exception as e:
        Logger.error("Unable able to load Android %s [%s] Lib [%s]" % (uModuleName ,uLib,str(e)))

    return oModule
