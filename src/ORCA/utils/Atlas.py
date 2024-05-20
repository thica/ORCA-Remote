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

import os

from typing                 import Optional
from typing                 import List

from kivy.atlas             import Atlas
from kivy.cache             import Cache
from kivy.logger            import Logger

from ORCA.utils.FileName    import cFileName
from ORCA.utils.Path        import cPath
from ORCA.utils.LogError    import LogError
from ORCA.utils.TypeConvert import ToUnicode

from ORCA.Globals import Globals

__all__ = ['ToAtlas','CreateAtlas','ClearAtlas']

def ToAtlas(*,oFileName: cFileName) -> str:
    """
    checks if a a picture is already available in a atlas file

    :param cFileName oFileName:
    :return: Found FileName
    """
    uRetFileName: str               = str(oFileName)
    oFnSkinPic: Optional[cFileName] = Globals.oTheScreen.oSkin.dSkinPics.get(uRetFileName)
    oFn:cFileName
    oAtlas:Atlas

    if not oFnSkinPic is None:
        uRetFileName = str(oFnSkinPic)

    if Globals.bIgnoreAtlas:
        return uRetFileName

    uKey: str = os.path.splitext(os.path.basename(uRetFileName))[0]

    if uRetFileName.startswith(str(Globals.oPathSkin)):
        oFn = Globals.oFnAtlasSkin
    elif uRetFileName.startswith(str(Globals.oDefinitionPathes.oPathDefinition)):
        oFn = Globals.oDefinitionPathes.oFnDefinitionAtlas
    else:
        return uRetFileName

    oAtlas = Cache.get('kv.atlas', str(oFn))

    if oAtlas:
        if not oAtlas.textures.get(uKey) is None:
            return ToUnicode('atlas://'+str(oFn)+'/'+uKey)

    return uRetFileName

def CreateAtlas(*,oPicPath: cPath,oAtlasFile: cFileName,uDebugMsg: str) -> None:
    """
    creates an atlas file from all picture files in a folder

    :param cPath oPicPath: The Path to a Picture Folder
    :param cFileName oAtlasFile: The Atlas Files to Create
    :param string uDebugMsg: A Debug Message for the function
    :return:
    """

    aExtensions:List[str]
    aPicFiles:List[str]
    aFileList:List[str]
    uExtension:str
    uFileName:str

    if Globals.bIgnoreAtlas:
        return

    #can\'t get JPEG lib included in package, so just ignore atlas
    if Globals.uPlatform=='macosx'  or Globals.uPlatform=='ios':
        return

    try:
        if not oAtlasFile.Exists():
            Logger.debug(uDebugMsg)
            #aExtensions=['.png','.jpg','.bmp','.gif']
            # we exclude gifs as they might be animated
            aExtensions = ['.png','.jpg','.bmp']
            aPicFiles   = []

            aFileList = oPicPath.GetFileList(bSubDirs=False , bFullPath=True)
            for uFileName in aFileList:
                uExtension = os.path.splitext(uFileName)[1].lower()
                if uExtension in aExtensions:
                    if uFileName.find(str(Globals.oPathSkin) + '/atlas/')==-1:
                        aPicFiles.append(uFileName)
            try:
                Atlas.create(str(oAtlasFile)[:-6],aPicFiles,1024)
            except Exception as e:
                LogError(uMsg='Error creating Atlas File (1):', oException=e)
    except Exception as e:
        LogError(uMsg='Error creating Atlas File (2):',oException=e)

def ClearAtlas() -> None:
    """ deletes all atlas files """
    #we clear all cache files for all definitions by purpose

    uSkinName:str
    uDefinitionName:str
    oPathAtlasSkin: cPath
    oPathDefinitionAtlas: cPath

    for uSkinName in Globals.aSkinList:
        oPathAtlasSkin = Globals.oPathRoot + f'skins/{uSkinName}/atlas'
        oPathAtlasSkin.Clear()
    for uDefinitionName in Globals.aDefinitionList:
        oPathDefinitionAtlas = Globals.oPathRoot + f'definitions/{uDefinitionName}/atlas'
        oPathDefinitionAtlas.Clear()
