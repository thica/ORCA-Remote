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


from typing             import List
from typing             import Tuple
from typing             import Dict

# noinspection PyUnresolvedReferences
from jnius              import autoclass

from ORCA.utils.Path    import cPath
from ORCA.vars.Replace  import ReplaceVars
dPlaces:Dict[str,cPath] = {}


def GetAllKnownFolders():

    try:
        Environment = autoclass('android.os.Environment')
        aPlaces:List[Tuple[str,str,str]] = \
            [("$lvar(1200)",Environment.DIRECTORY_DOWNLOADS,'Downloads'),
             ("$lvar(1202)",Environment.DIRECTORY_DOCUMENTS,'Documents'),
             ("$lvar(1205)",Environment.DIRECTORY_MUSIC,'Music'),
             ("$lvar(1203)",Environment.DIRECTORY_PICTURS,'Pictures'),
             ("$lvar(1204)",Environment.DIRECTORY_MOVIES,'Videos'),
            ]
        for tPlace in aPlaces:
            uRetPath = Environment.getExternalStoragePublicDirectory(tPlace[1]).getPath()
            dPlaces[tPlace[0]]=cPath(uRetPath)
            Logger.debug("Android %s Folder = %s" % (tPlace[2],uRetPath))
    except Exception as e:
        Logger.error("GetPath for Android failed:"+str(e))

def GetDownloadFolder() -> cPath:
    return dPlaces.get("$lvar(1200)",cPath(""))

def GetDocumentsFolder() -> cPath:
    return dPlaces.get("$lvar(1202)",cPath(""))

def GetPicturesFolder() -> cPath:
    return dPlaces.get("$lvar(1203)",cPath(""))

def GetVideosFolder() -> cPath:
    return dPlaces.get("$lvar(1204)",cPath(""))

def GetMusicFolder() -> cPath:
    return dPlaces.get("$lvar(1205)",cPath(""))

def GetPlaces() -> List[Tuple[str,cPath]]:
    """
    Returns the list of available user places for the operating system
    """

    oPath:cPath
    aLocPlaces:List[Tuple[str,cPath]] = []
    uPlace:str

    oPath=GetDownloadFolder()
    if oPath.string is not "":
        aLocPlaces.append((ReplaceVars("$lvar(1200)"),oPath))

    oPath=GetDocumentsFolder()
    if oPath.string is not "":
        aLocPlaces.append((ReplaceVars("$lvar(1202)"),oPath))

    oPath=GetPicturesFolder()
    if oPath.string is not "":
        aLocPlaces.append((ReplaceVars("$lvar(1203)"),oPath))

    oPath=GetVideosFolder()
    if oPath.string is not "":
        aLocPlaces.append((ReplaceVars("$lvar(1204)"),oPath))

    oPath=GetMusicFolder()
    if oPath.string is not "":
        aLocPlaces.append((ReplaceVars("$lvar(1205)"),oPath))

    return aLocPlaces

GetAllKnownFolders()