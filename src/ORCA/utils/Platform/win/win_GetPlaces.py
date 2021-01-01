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

import ctypes
from ctypes             import windll, wintypes
from uuid               import UUID

from ORCA.utils.Path    import cPath
from ORCA.vars.Replace  import ReplaceVars


#we dont use the translated vars, as they are not available at app start
aPlaces:List[Tuple[str,str,str]] = \
          [("$lvar(1200)",'{374DE290-123F-4565-9164-39C4925E467B}','Downloads'),
           ("$lvar(1200)",'{088e3905-0323-4b02-9826-5d99428e115f}','Downloads V2'),
           ("$lvar(1201)",'{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}','Desktop'),
           ("$lvar(1202)",'{d3162b92-9365-467a-956b-92703aca08af}','Dokumente'),
           ("$lvar(1202)",'{A8CDFF1C-4878-43be-B5FD-F8091C1C60D0}','Dokumente V2'),
           ("$lvar(1202)",'{FDD39AD0-238F-46AF-ADB4-6C85480369C7}','Dokumente V3'),
           ("$lvar(1205)",'{4BD8D571-6D19-48D3-BE97-422220080E43}','Music'),
           ("$lvar(1205)",'{1CF1260C-4DD0-4ebb-811F-33C572699FDE}','Music V2'),
           ("$lvar(1205)",'{3dfdf296-dbec-4fb4-81d1-6a3438bcf4de}','Music V3'),
           ("$lvar(1203)",'{3ADD1653-EB32-4cb0-BBD7-DFA0ABB5ACCA}','Pictures'),
           ("$lvar(1203)",'{24ad3ad4-a569-4530-98e1-ab02f9417aa8}','Pictures V2'),
           ("$lvar(1203)",'{33E28130-4E1E-4676-835A-98395C3BC3BB}','Pictures V3'),
           ("$lvar(1204)",'{18989B1D-99B5-455B-841C-AB7C74E4DDFC}','Videos'),
           ("$lvar(1204)",'{A0953C92-50DC-43bf-BE83-3742FED03C9C}','Videos V2'),
           ("$lvar(1204)",'{f86fa3ab-70d2-4fc7-9c99-fcbf05467f3a}','Videos V3')
          ]

dPlaces:Dict[str,cPath] = {}

class cGUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8)
    ]

    def __init__(self, uuidstr):
        uuid = UUID(uuidstr)
        ctypes.Structure.__init__(self)
        self.Data1, self.Data2, self.Data3, \
        self.Data4[0], self.Data4[1], rest = uuid.fields
        for i in range(2, 8):
            self.Data4[i] = rest>>(8-i-1)*8 & 0xff

SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
SHGetKnownFolderPath.argtypes = [ctypes.POINTER(cGUID), wintypes.DWORD,wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)]

def GetAllKnownFolders():
    global dPlaces
    uPathPlace:str
    if len(dPlaces)==0:
        for tPlace in aPlaces:
            if dPlaces.get(tPlace[0]) is None:
                uPathPlace = GetKnownFolderPath(tPlace[1])
                if uPathPlace:
                    dPlaces[tPlace[0]]= cPath(uPathPlace)
                    print (tPlace[0],":",uPathPlace)

def GetKnownFolderPath(uUuidstr:str) ->str:

    try:
        pathptr = ctypes.c_wchar_p()
        guid = cGUID(uUuidstr)
        if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
            return u''
        else:
            return pathptr.value
    except:
        pass
    return u''

def GetDownloadFolder() -> cPath:
    return dPlaces.get("$lvar(1200)",cPath(""))

def GetDocumentsFolder() -> cPath:
    return dPlaces.get("$lvar(1202)",cPath(""))

def GetDesktopFolder() -> cPath:
    return dPlaces.get("$lvar(1201)",cPath(""))

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

    oPath=GetDesktopFolder()
    if oPath.string is not "":
        aLocPlaces.append((ReplaceVars("$lvar(1201)"),oPath))

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