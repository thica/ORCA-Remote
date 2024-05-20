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

from ORCA.download.InstalledReps  import cInstalledReps
from ORCA.utils.TypeConvert       import ToUnicode

from ORCA.Globals import Globals

__all__ = ['RegisterDownLoad']

def RegisterDownLoad(*,uType:str,uName:str,iVersion:int):
    """ Registers a repository """

    if not uName=='':
        oConfig                = Globals.oOrcaConfigParser
        oInstalledRep          = cInstalledReps()
        oInstalledRep.uType    = uType
        oInstalledRep.uName    = uName
        oInstalledRep.iVersion = iVersion
        uKey                   = f'{oInstalledRep.uType}:{oInstalledRep.uName}'
        Globals.dInstalledReps[uKey]=oInstalledRep

        i=0
        for oInstalledRepKey in Globals.dInstalledReps:
            oInstalledRep=Globals.dInstalledReps[oInstalledRepKey]
            uKey= f'installedrep{i:d}_type'
            oConfig.set('ORCA', uKey, oInstalledRep.uType)
            uKey= f'installedrep{i:d}_name'
            oConfig.set('ORCA', uKey, oInstalledRep.uName)
            uKey= f'installedrep{i:d}_version'
            oConfig.set('ORCA', uKey, ToUnicode(oInstalledRep.iVersion))
            i+=1
        oConfig.write()
