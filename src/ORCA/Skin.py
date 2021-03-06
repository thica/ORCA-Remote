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

from typing                         import Dict
from typing                         import Any

from xml.etree.ElementTree          import Element
from kivy.logger                    import Logger
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp
from ORCA.utils.FileName            import cFileName
from ORCA.utils.LogError            import LogError
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import GetXMLTextValue
from ORCA.utils.XML                 import LoadXMLFile
from ORCA.utils.Atlas               import CreateAtlas
from ORCA.utils.Path                import cPath
from ORCA.vars.Replace              import ReplaceVars
from ORCA.vars.Access               import SetVar
from ORCA.widgets.helper.HexColor   import GetColorFromHex

import ORCA.Globals as Globals

__all__ = ['cSkin']

class cSkin:
    """ Represents the Skin """
    def __init__(self):
        self.dSkinAttributes:Dict[str,Any]            = {}
        self.dSkinPics:Dict[str,cFileName]            = {}
        self.dSkinRedirects:Dict[str,cFileName]       = {}

    def LoadSkinDescription(self):
        """ Loads the a skin description """
        #AddGlobalVars:we do it here again: Todo: check if it either can be split or out somewhere else

        oET_Root:Element
        oXMLPics:Element
        oXMLColors:Element
        oXMLAtts:Element
        oXMLRedirects:Element
        oXMLAtt:Element
        uPicName:str
        uColorName:str
        uColor:str
        uAttName:str
        uAtt:str

        Globals.oTheScreen.AddGlobalVars()

        try:
            oET_Root = LoadXMLFile(oFile=Globals.oFnSkinXml)
            if oET_Root is not None:
                Logger.debug (u'TheScreen: Loading Skin Description (pics)')
                oXMLPics = oET_Root.find('pics')
                if oXMLPics is not None:
                    for oXMLPic in oXMLPics.findall('pic'):
                        uPicName = GetXMLTextAttribute(oXMLNode=oXMLPic,uTag=u'name',bMandatory=False, vDefault=u'')
                        self.dSkinPics[uPicName]= cFileName('').ImportFullPath(uFnFullName=GetXMLTextAttribute(oXMLNode=oXMLPic,uTag=u'file',bMandatory=False,vDefault=u''))

                Logger.debug (u'TheScreen: Loading Skin Description (colors)')
                oXMLColors = oET_Root.find('colors')
                if oXMLColors is not None:
                    for oXMLColor in oXMLColors.findall('color'):
                        uColorName  = GetXMLTextAttribute(oXMLNode=oXMLColor,uTag=u'name',bMandatory=True,vDefault=u'black')
                        uColor      = GetXMLTextValue(oXMLNode=oXMLColor,    uTag='',     bMandatory=True,vDefault=u'#000000ff')
                        SetVar(uVarName = uColorName, oVarValue = uColor)

                Logger.debug (u'TheScreen: Loading Skin Description (redirects)')
                oXMLRedirects = oET_Root.find('redirects')
                if oXMLRedirects is not None:
                    for oXMLRedirect in oXMLRedirects.findall('redirect'):
                        oFrom:cFileName   = cFileName('').ImportFullPath(uFnFullName=GetXMLTextAttribute(oXMLNode=oXMLRedirect,uTag=u'from',bMandatory=True,vDefault=u''))
                        oTo:cFileName     = cFileName('').ImportFullPath(uFnFullName=GetXMLTextAttribute(oXMLNode=oXMLRedirect,uTag=u'to',  bMandatory=True,vDefault=u''))
                        self.dSkinRedirects[oFrom.string]=oTo

                Logger.debug (u'TheScreen: Loading Skin Description (attributes)')
                oXMLAtts = oET_Root.find('attributes')
                if oXMLAtts is not None:
                    for oXMLAtt in oXMLAtts.findall('attribute'):
                        uAttName = GetXMLTextAttribute(oXMLNode=oXMLAtt,uTag=u'name',bMandatory=False,vDefault=u'')
                        uAtt     = ReplaceVars(GetXMLTextAttribute(oXMLNode=oXMLAtt,uTag=u'att',bMandatory=False,vDefault=u''))
                        self.dSkinAttributes[uAttName]=uAtt
                        SetVar(uVarName = uAttName, oVarValue = uAtt)

                if self.dSkinAttributes.get('color font button'):
                    SetVar(uVarName = u'SKIN_FONTCOLOR_BUTTON', oVarValue = self.dSkinAttributes['color font button'])
                    self.dSkinAttributes['color font button']        =  GetColorFromHex(self.dSkinAttributes['color font button'])
                if self.dSkinAttributes.get('color font text'):
                    SetVar(uVarName = u'SKIN_FONTCOLOR_TEXT', oVarValue = self.dSkinAttributes['color font text'])
                    self.dSkinAttributes['color font text']  =  GetColorFromHex(self.dSkinAttributes['color font text'])
                if self.dSkinAttributes.get('color font file'):
                    SetVar(uVarName = u'SKIN_FONTCOLOR_FILE', oVarValue = self.dSkinAttributes['color font file'])
                    self.dSkinAttributes['color font file']          =  GetColorFromHex(self.dSkinAttributes['color font file'])
                if self.dSkinAttributes.get('color border'):
                    SetVar(uVarName = u'SKIN_COLOR_BORDER', oVarValue = self.dSkinAttributes['color border'])
                    self.dSkinAttributes['color border']             =  GetColorFromHex(self.dSkinAttributes['color border'])


            oPathSkinAtlas:cPath = Globals.oPathSkin + 'atlas'
            oPathSkinAtlas.Create()
            Globals.oFnAtlasSkin = cFileName(oPathSkinAtlas) + "skin.atlas"
            CreateAtlas(oPicPath=Globals.oPathSkin+"pics", oAtlasFile=Globals.oFnAtlasSkin, uDebugMsg=u'Create Skin Atlas Files')

            Globals.oTheScreen.LoadAtlas()
            Globals.oTheScreen.oFonts.ParseFontFromXMLNode(oXMLNode=oET_Root)
            Globals.oTheScreen.oFonts.ParseIconsFromXMLNode(oXMLNode=oET_Root)

        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'TheScreen:  __LoadSkinDescription: can\'t load SkinDescription',oException=e))

