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

import                              logging
from kivy.logger                    import Logger
from kivy.core.text                 import LabelBase
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import GetXMLFloatAttribute
from ORCA.utils.XML                 import GetXMLTextValue
from ORCA.utils.FileName            import cFileName
from ORCA.utils.LogError            import LogError
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp

import ORCA.Globals as Globals

__all__ = ['cFonts', 'cFontDef']

class cFontDef(object):
    """
    Object which holds the definition of a named font to
    be able to be used by a definition
    """

    def __init__(self):
        self.uName                  = u''

        self.oFnNormal              = cFileName(u'')
        self.oFnBold                = cFileName(u'')
        self.oFnItalic              = cFileName(u'')
        self.oFnBoldItalic          = cFileName(u'')

    def ParseFontFromXMLNode(self,oXMLFont):
        """
        Parses a font definition from an xml node

        :rtype: int
        :return: The Number of fonts, defined in the XML
        :param Element oXMLFont: An elementree xml node
        """
        self.uName = GetXMLTextValue(oXMLFont,u'name',True,u'NoName')
        iCount = 0
        for oXMLSingleFont in oXMLFont.findall(u'file'):
            iCount=iCount+1
            uFontStyle = GetXMLTextAttribute(oXMLSingleFont,u'face',True,u'')
            if uFontStyle==u'normal':
                self.oFnNormal.ImportFullPath(oXMLSingleFont.text)
            elif uFontStyle==u'bold':
                self.oFnBold.ImportFullPath(oXMLSingleFont.text)
            elif uFontStyle==u'italic':
                self.oFnItalic.ImportFullPath(oXMLSingleFont.text)
            elif uFontStyle==u'bolditalic':
                self.oFnBoldItalic.ImportFullPath(oXMLSingleFont.text)
            else:
                uMsg=LogError(u'FontParser: Invalid Tag:'+uFontStyle)
                ShowErrorPopUp(uMessage=uMsg)
        return iCount

    def Register(self):
        Logger.debug(u'Register Font: ' + self.oFnNormal)

        uFnNormal           = self.oFnNormal.string
        uFnItalic           = self.oFnItalic.string
        uFnBold             = self.oFnBold.string
        uFnBoldItalic       = self.oFnBoldItalic.string

        if uFnNormal == '':     uFnNormal = None
        if uFnItalic =='':      uFnItalic = None
        if uFnBold =='':        uFnBold   = None
        if uFnBoldItalic =='':  uFnBoldItalic = None

        LabelBase.register(self.uName, uFnNormal, uFnItalic, uFnBold, uFnBoldItalic)


class cFonts(object):
    """ Represents the Font Object """
    def __init__(self):
        self.dFonts                 = {}
        self.dUsedFonts             = {}

    def DeInit(self):
        """ we do nothing by purpose  """
        pass

    def ParseDirect(self,uFontName, uFontFileNormal):
        oTmpFont = cFontDef()
        oTmpFont.uName = uFontName
        oTmpFont.oFnNormal = cFileName("").ImportFullPath(uFontFileNormal)
        self.dFonts[oTmpFont.uName] = oTmpFont

    def ParseIconsFromXMLNode(self,oET_Root):
        oXMLIcons = oET_Root.find('icons')
        if oXMLIcons is not None:
            Logger.info(u'Loading Icons')
            for oXMLIcon in oXMLIcons.findall('icon'):
                uIconName = GetXMLTextAttribute(oXMLIcon, u'name', True, u'')
                oFnIconFont = cFileName("").ImportFullPath(GetXMLTextAttribute(oXMLIcon, u'font', True, u''))
                uIconChar = GetXMLTextAttribute(oXMLIcon, u'char', True, u'')
                uFontName = oFnIconFont.basename
                fIconScale = GetXMLFloatAttribute(oXMLIcon, u'scale', False, 1)
                Globals.dIcons[uIconName] = {"fontfile": oFnIconFont.string, "char": uIconChar, "fontname":uFontName, "scale":fIconScale}
                Globals.oTheScreen.oFonts.ParseDirect(uFontName=uFontName, uFontFileNormal=oFnIconFont.string)

    def ParseFontFromXMLNode(self,oET_Root):
        oXMLFonts = oET_Root.find('fonts')
        iCount = 0
        if oXMLFonts is not None:
            for oXMLFont in oXMLFonts.findall('font'):
                oTmpFont=cFontDef()
                iCount = iCount + oTmpFont.ParseFontFromXMLNode(oXMLFont=oXMLFont)
                self.dFonts[oTmpFont.uName]=oTmpFont
        return iCount

    def RegisterFonts(self,uFontName,fSplashScreenPercentageStartValue):
        """ Register the a specific font, or schedules the registration of all fonts """

        fSplashScreenPercentageRange=10.0

        if not uFontName:
            Logger.debug (u'TheScreen: Register Fonts')
            fPercentage=fSplashScreenPercentageStartValue
            fPercentageStep=fSplashScreenPercentageRange/len(self.dFonts)

            # Scheduling Loading Fonts
            aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message the we register the fonts','string':'showsplashtext','maintext':'$lvar(417)'}])

            for oFontIndex in self.dFonts:
                oFont=self.dFonts[oFontIndex]
                fPercentage=fPercentage+fPercentageStep
                if Logger.getEffectiveLevel() != logging.DEBUG:
                    aCommands = []
                else:
                    aCommands = [{'name':'Update Percentage and Font Name','string':'showsplashtext','subtext':oFont.uName,'percentage':str(fPercentage)}]
                aCommands.append({'name':'Register the Font','string':'registerfonts','fontname':oFont.uName})
                Globals.oEvents.AddToSimpleActionList(aActions,aCommands)
                Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        else:
            oFont=self.dFonts[uFontName]
            # todo: either we always load all fonts, or we need to check in widget if font is required in case we load elements as runtime
            if oFont.uName in self.dUsedFonts or True:
                oFont.Register()
