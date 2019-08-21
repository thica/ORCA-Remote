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

from ORCA.BaseSettings                      import cBaseSettings

class cBaseScriptSettings(cBaseSettings):
    """ A base class for the script settings """
    def __init__(self, oScript):
        # some default settings, which should be there even if not configured by the script
        # use the exact spelling as in the settings json

        super(cBaseScriptSettings,self).__init__(oScript)
        self.oScript                                            = oScript
        self.uConfigName                                        = "SCRIPTDEFAULT"
        self.uType                                              = "script"
