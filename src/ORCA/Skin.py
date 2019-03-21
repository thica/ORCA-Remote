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

from kivy.logger                    import Logger
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp
from ORCA.utils.FileName            import cFileName
from ORCA.utils.LogError            import LogError
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import GetXMLTextValue
from ORCA.utils.XML                 import LoadXMLFile
from ORCA.utils.Atlas                      import CreateAtlas
from ORCA.vars.Replace              import ReplaceVars
from ORCA.vars.Access import SetVar
from ORCA.widgets.Base              import GetColorFromHex

import ORCA.Globals as Globals

__all__ = ['cSkin']

class cSkin(object):
    """ Represents the Skin """
    def __init__(self):
        self.dSkinAttributes        = {}
        self.dSkinPics              = {}
        self.dSkinRedirects         = {}

    def LoadSkinDescription(self):
        """ Loads the a skin description """
        #AddGlobalVars:we do it here again: Todo: check if it either can be split or out somewhere else
        Globals.oTheScreen.AddGlobalVars()

        try:
            oET_Root = LoadXMLFile(Globals.oFnSkinXml)
            if oET_Root is not None:
                Logger.debug (u'TheScreen: Loading Skin Description (pics)')
                oXMLPics = oET_Root.find('pics')
                if oXMLPics is not None:
                    for oXMLPic in oXMLPics.findall('pic'):
                        uPicName  = GetXMLTextAttribute(oXMLPic,u'name',False,u'')
                        self.dSkinPics[uPicName]= cFileName('').ImportFullPath(GetXMLTextAttribute(oXMLPic,u'file',False,u''))

                Logger.debug (u'TheScreen: Loading Skin Description (colors)')
                oXMLColors = oET_Root.find('colors')
                if oXMLColors is not None:
                    for oXMLColor in oXMLColors.findall('color'):
                        uColorName  = GetXMLTextAttribute(oXMLColor,u'name',True,u'black')
                        uColor      = GetXMLTextValue(oXMLColor,'',True,u'#000000ff')
                        SetVar(uVarName = uColorName, oVarValue = uColor)

                Logger.debug (u'TheScreen: Loading Skin Description (redirects)')
                oXMLRedirects = oET_Root.find('redirects')
                if oXMLRedirects is not None:
                    for oXMLRedirect in oXMLRedirects.findall('redirect'):
                        oFrom   = cFileName('').ImportFullPath(GetXMLTextAttribute(oXMLRedirect,u'from',True,u''))
                        oTo     = cFileName('').ImportFullPath(GetXMLTextAttribute(oXMLRedirect,u'to',True,u''))
                        self.dSkinRedirects[oFrom.string]=oTo

                Logger.debug (u'TheScreen: Loading Skin Description (attributes)')
                oXMLAtts = oET_Root.find('attributes')
                if oXMLAtts is not None:
                    for oXMLAtt in oXMLAtts.findall('attribute'):
                        uAttName  = GetXMLTextAttribute(oXMLAtt,u'name',False,u'')
                        uAtt      = ReplaceVars(GetXMLTextAttribute(oXMLAtt,u'att',False,u''))
                        self.dSkinAttributes[uAttName]=uAtt
                        SetVar(uVarName = uAttName, oVarValue = uAtt)

                if self.dSkinAttributes.get('fontcolor button'):
                    SetVar(uVarName = u'SKIN_FONTCOLOR_BUTTON', oVarValue = self.dSkinAttributes['fontcolor button'])
                    self.dSkinAttributes['fontcolor button']        =  GetColorFromHex(self.dSkinAttributes['fontcolor button'])
                if self.dSkinAttributes.get('fontcolor text'):
                    SetVar(uVarName = u'SKIN_FONTCOLOR_TEXT', oVarValue = self.dSkinAttributes['fontcolor text'])
                    self.dSkinAttributes['fontcolor text']  =  GetColorFromHex(self.dSkinAttributes['fontcolor text'])
                if self.dSkinAttributes.get('fontcolor file'):
                    SetVar(uVarName = u'SKIN_FONTCOLOR_FILE', oVarValue = self.dSkinAttributes['fontcolor file'])
                    self.dSkinAttributes['fontcolor file']          =  GetColorFromHex(self.dSkinAttributes['fontcolor file'])

            oPathSkinAtlas=Globals.oPathSkin + 'atlas'
            oPathSkinAtlas.Create()
            Globals.oFnAtlasSkin = cFileName(oPathSkinAtlas) + "skin.atlas"
            CreateAtlas(Globals.oPathSkin+"pics", Globals.oFnAtlasSkin, u'Create Skin Atlas Files')

            Globals.oTheScreen.LoadAtlas()
            Globals.oTheScreen.oFonts.ParseFontFromXMLNode(oET_Root)
            Globals.oTheScreen.oFonts.ParseIconsFromXMLNode(oET_Root)

        except Exception as e:
            uMsg=LogError(u'TheScreen:  __LoadSkinDescription: can\'t load SkinDescription',e)
            ShowErrorPopUp(uMessage=uMsg)

