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

import os

from kivy.atlas             import Atlas
from kivy.cache             import Cache
from kivy.logger            import Logger

from ORCA.utils.FileName import cFileName
from ORCA.utils.Path import cPath
from ORCA.utils.LogError    import LogError
from ORCA.utils.TypeConvert import ToUnicode

import ORCA.Globals as Globals

__all__ = ['ToAtlas','CreateAtlas','ClearAtlas']

def ToAtlas(*,oFileName: cFileName) -> str:
    """
    checks if a a picture is already available in a atlas file

    :param cFileName oFileName:
    :return: Found FileName
    """
    uRetFileName: str       = oFileName.string
    oFnSkinPic: cFileName   = Globals.oTheScreen.oSkin.dSkinPics.get(uRetFileName)
    oFn:cFileName

    if not oFnSkinPic is None:
        uRetFileName = oFnSkinPic.string

    if Globals.bIgnoreAtlas:
        return uRetFileName

    uKey: str = os.path.splitext(os.path.basename(uRetFileName))[0]

    if uRetFileName.startswith(Globals.oPathSkin.string):
        oFn = Globals.oFnAtlasSkin
    elif uRetFileName.startswith(Globals.oDefinitionPathes.oPathDefinition.string):
        oFn = Globals.oDefinitionPathes.oFnDefinitionAtlas
    else:
        return uRetFileName

    oAtlas: Atlas = Cache.get('kv.atlas', oFn.string)

    if oAtlas:
        if not oAtlas.textures.get(uKey) is None:
            return ToUnicode(u'atlas://'+oFn.string+u'/'+uKey)

    return uRetFileName

def CreateAtlas(*,oPicPath: cPath,oAtlasFile: cFileName,uDebugMsg: str) -> None:
    """
    creates an atlas file from all picture files in a folder

    :param cPath oPicPath: The Path to a Picture Folder
    :param cFileName oAtlasFile: The Atlas Files to Create
    :param string uDebugMsg: A Debug Message for the function
    :return:
    """
    if Globals.bIgnoreAtlas:
        return

    #can\'t get JPEG lib included in package, so just ignore atlas
    if Globals.uPlatform=='macosx'  or Globals.uPlatform=="ios":
        return

    try:
        if not oAtlasFile.Exists():
            Logger.debug(uDebugMsg)
            #aExtensions=[u'.png',u'.jpg',u'.bmp',u'.gif']
            # we exclude gifs as they might be animated
            aExtensions=[u'.png',u'.jpg',u'.bmp']
            aPicFiles=[]

            aFileList=oPicPath.GetFileList(bSubDirs=False , bFullPath=True)
            for uFileName in aFileList:
                uExtension = os.path.splitext(uFileName)[1].lower()
                if uExtension in aExtensions:
                    if uFileName.find(Globals.oPathSkin.string + u'/atlas/')==-1:
                        aPicFiles.append(uFileName)
            try:
                Atlas.create(oAtlasFile.string[:-6],aPicFiles,1024)
            except Exception as e:
                LogError(uMsg=u'Error creating Atlas File (1):', oException=e)
                pass
    except Exception as e:
        LogError(uMsg=u'Error creating Atlas File (2):',oException=e)

def ClearAtlas() -> None:
    """ deletes all atlas files """
    #we clear all cache files for all definitions by purpose
    for uSkinName in Globals.aSkinList:
        oPathAtlasSkin: cPath = Globals.oPathRoot + ('skins/' + uSkinName + u'/atlas')
        oPathAtlasSkin.Clear()
    for uDefinitionName in Globals.aDefinitionList:
        oPathDefinitionAtlas: cPath = Globals.oPathRoot + ('definitions/' + uDefinitionName + u'/atlas')
        oPathDefinitionAtlas.Clear()
