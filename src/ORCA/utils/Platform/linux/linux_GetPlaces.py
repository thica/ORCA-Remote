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


from typing             import List
from typing             import Tuple
from typing             import Dict
from os.path            import expanduser
from ORCA.utils.Path    import cPath
from ORCA.utils.FileName import cFileName
from ORCA.vars.Replace  import ReplaceVars

aPlaces=["DESKTOP","DOWNLOAD","DOCUMENTS","MUSIC","PICTURES","VIDEOS"]
dPlaces:Dict[str,cPath] = {}


def GetAllKnownFolders():

    # /etc/xdg/user-dirs.defaults, or if it exists $HOME/.config/user-dirs.dirs.

    # GetAllKnownFoldersSub(oFnFile=cFileName('/etc/xdg/user-dirs.defaults'))
    GetAllKnownFoldersSub(oFnFile=cFileName(expanduser('~/.config/user-dirs.dirs')))

def GetAllKnownFoldersSub(*,oFnFile:cFileName) -> None:

    uLine:str
    uXDGPlace:str
    uPathPlace:str
    uPrefix:str
    uName:str
    uSuffix:str

    try:
        oFile = open(str(oFnFile), "r")
        aLines:List[str]=oFile.readlines()
        for uLine in aLines:
            if not uLine.rstrip().startswith('#'):
                uXDGPlace,uPathPlace = uLine.split('=')
                uPrefix,uName,uSuffix=uLine.split('_')
                if uName in aPlaces:
                    uPathPlace=uPathPlace.replace('$HOME','~').replace('"','').replace("'",'').replace('\n','')
                    dPlaces[uName]= cPath(expanduser(uPathPlace))
        oFile.close()
    except:
        pass


def GetDownloadFolder() -> cPath:
    return dPlaces.get('DOWNLOAD',cPath(''))

def GetDocumentsFolder() -> cPath:
    return dPlaces.get('DOCUMENTS',cPath(''))

def GetDesktopFolder() -> cPath:
    return dPlaces.get('DESKTOP',cPath(''))

def GetPicturesFolder() -> cPath:
    return dPlaces.get('PICTURES',cPath(''))

def GetVideosFolder() -> cPath:
    return dPlaces.get('VIDEOS',cPath(''))

def GetMusicFolder() -> cPath:
    return dPlaces.get('MUSIC',cPath(''))

def GetPlaces() -> List[Tuple[str,cPath]]:
    """
    Returns the list of available user places for the operating system
    """

    oPath:cPath
    aLocPlaces:List[Tuple[str,cPath]] = []
    uPlace:str

    oPath=GetDownloadFolder()
    if not oPath.IsEmpty():
        aLocPlaces.append((ReplaceVars('$lvar(1200)'),oPath))

    oPath=GetDocumentsFolder()
    if not oPath.IsEmpty():
        aLocPlaces.append((ReplaceVars('$lvar(1202)'),oPath))

    oPath=GetDesktopFolder()
    if not oPath.IsEmpty():
        aLocPlaces.append((ReplaceVars('$lvar(1201)'),oPath))

    oPath=GetPicturesFolder()
    if not oPath.IsEmpty():
        aLocPlaces.append((ReplaceVars('$lvar(1203)'),oPath))

    oPath=GetVideosFolder()
    if not oPath.IsEmpty():
        aLocPlaces.append((ReplaceVars('$lvar(1204)'),oPath))

    oPath=GetMusicFolder()
    if not oPath.IsEmpty():
        aLocPlaces.append((ReplaceVars('$lvar(1205)'),oPath))

    return aLocPlaces

GetAllKnownFolders()