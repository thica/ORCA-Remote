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
from typing                         import Optional
from typing                         import Dict
from typing                         import List

import                              logging
from xml.etree.ElementTree          import Element
from kivy.logger                    import Logger
from kivy.core.text                 import LabelBase
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import GetXMLFloatAttribute
from ORCA.utils.XML                 import GetXMLTextValue
from ORCA.utils.FileName            import cFileName
from ORCA.utils.LogError            import LogError
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.Action import cAction
else:
    from typing import TypeVar
    cAction = TypeVar("cAction")


__all__ = ['cFonts', 'cFontDef']

class cFontDef:
    """
    Object which holds the definition of a named font to
    be able to be used by a definition
    """

    def __init__(self):
        self.uName:str                        = u''
        self.oFnNormal:cFileName              = cFileName(u'')
        self.oFnBold:cFileName                = cFileName(u'')
        self.oFnItalic:cFileName              = cFileName(u'')
        self.oFnBoldItalic:cFileName          = cFileName(u'')

    def ParseFontFromXMLNode(self,*,oXMLNode:Element) -> int:
        """
        Parses a font definition from an xml node

        :return: The Number of fonts, defined in the XML
        :param oXMLNode: An elementree xml node
        """

        uFontStyle:str
        self.uName = GetXMLTextValue(oXMLNode=oXMLNode,uTag=u'name',bMandatory=True,vDefault=u'NoName')
        iCount:int = 0
        for oXMLSingleFont in oXMLNode.findall(u'file'):
            iCount += 1
            uFontStyle = GetXMLTextAttribute(oXMLNode=oXMLSingleFont,uTag=u'face',bMandatory=True,vDefault=u'')
            if uFontStyle==u'normal':
                self.oFnNormal.ImportFullPath(uFnFullName=oXMLSingleFont.text)
            elif uFontStyle==u'bold':
                self.oFnBold.ImportFullPath(uFnFullName=oXMLSingleFont.text)
            elif uFontStyle==u'italic':
                self.oFnItalic.ImportFullPath(uFnFullName=oXMLSingleFont.text)
            elif uFontStyle==u'bolditalic':
                self.oFnBoldItalic.ImportFullPath(uFnFullName=oXMLSingleFont.text)
            else:
                ShowErrorPopUp(uMessage=LogError(uMsg=u'FontParser: Invalid Tag:'+uFontStyle))
        return iCount

    def Register(self) -> None:
        Logger.debug(u'Register Font: ' + self.oFnNormal)

        uFnNormal:Optional[str]        = self.oFnNormal.string
        uFnItalic:[str,None]           = self.oFnItalic.string
        uFnBold:[str,None]             = self.oFnBold.string
        uFnBoldItalic:[str,None]       = self.oFnBoldItalic.string

        if uFnNormal == '':     uFnNormal = None
        if uFnItalic =='':      uFnItalic = None
        if uFnBold =='':        uFnBold   = None
        if uFnBoldItalic =='':  uFnBoldItalic = None

        LabelBase.register(self.uName, uFnNormal, uFnItalic, uFnBold, uFnBoldItalic)


class cFonts:
    """ Represents the Font Object """
    def __init__(self):
        self.dFonts:Dict[str,cFontDef]     = {}
        self.dUsedFonts:Dict[str,bool]     = {}

    def DeInit(self) -> None:
        """ we do nothing by purpose  """
        pass

    def ParseDirect(self,*,uFontName:str, uFontFileNormal:str) -> None:
        oTmpFont:cFontDef   = cFontDef()
        oTmpFont.uName      = uFontName
        oTmpFont.oFnNormal  = cFileName("").ImportFullPath(uFnFullName=uFontFileNormal)
        self.dFonts[oTmpFont.uName] = oTmpFont

    # noinspection PyMethodMayBeStatic
    def ParseIconsFromXMLNode(self,*,oXMLNode:Element) -> None:
        oXMLIcons:Element = oXMLNode.find('icons')
        if oXMLIcons is not None:
            Logger.info(u'Loading Icons')
            for oXMLIcon in oXMLIcons.findall('icon'):
                uIconName:str           = GetXMLTextAttribute(oXMLNode=oXMLIcon,uTag=u'name',bMandatory=True, vDefault=u'')
                oFnIconFont:cFileName   = cFileName("").ImportFullPath(uFnFullName=GetXMLTextAttribute(oXMLNode=oXMLIcon, uTag=u'font', bMandatory=True, vDefault=u''))
                uIconChar:str           = GetXMLTextAttribute(oXMLNode=oXMLIcon, uTag=u'char', bMandatory=True, vDefault=u'')
                uFontName:str           = oFnIconFont.basename
                fIconScale:float        = GetXMLFloatAttribute(oXMLNode=oXMLIcon, uTag=u'scale', bMandatory=False, fDefault=1.0)
                Globals.dIcons[uIconName] = {"fontfile": oFnIconFont.string, "char": uIconChar, "fontname":uFontName, "scale":fIconScale}
                Globals.oTheScreen.oFonts.ParseDirect(uFontName=uFontName, uFontFileNormal=oFnIconFont.string)

    def ParseFontFromXMLNode(self,*,oXMLNode:Element) -> int:
        oXMLFonts:Element = oXMLNode.find('fonts')
        iCount:int = 0
        if oXMLFonts is not None:
            for oXMLFont in oXMLFonts.findall('font'):
                oTmpFont:cFontDef=cFontDef()
                iCount += oTmpFont.ParseFontFromXMLNode(oXMLNode=oXMLFont)
                self.dFonts[oTmpFont.uName]=oTmpFont
        return iCount

    def RegisterFonts(self,*,uFontName:str,fSplashScreenPercentageStartValue:float) -> None:
        """ Register the a specific font, or schedules the registration of all fonts """

        fPercentage:float
        fSplashScreenPercentageRange:float = 10.0
        uFontIndex:str
        aCommands:List[Dict]
        oFont:cFontDef

        if not uFontName:
            Logger.debug (u'TheScreen: Register Fonts')
            fPercentage=fSplashScreenPercentageStartValue
            fPercentageStep=fSplashScreenPercentageRange/len(self.dFonts)

            # Scheduling Loading Fonts
            aActions:List[cAction]=Globals.oEvents.CreateSimpleActionList(aActions=[{'name':'Show Message the we register the fonts','string':'showsplashtext','maintext':'$lvar(417)'}])

            for uFontIndex in self.dFonts:
                oFont=self.dFonts[uFontIndex]
                fPercentage += fPercentageStep
                if Logger.getEffectiveLevel() != logging.DEBUG:
                    aCommands = []
                else:
                    aCommands = [{'name':'Update Percentage and Font Name','string':'showsplashtext','subtext':oFont.uName,'percentage':str(fPercentage)}]
                aCommands.append({'name':'Register the Font','string':'registerfonts','fontname':oFont.uName})
                Globals.oEvents.AddToSimpleActionList(aActionList=aActions,aActions=aCommands)
                Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        else:
            oFont=self.dFonts[uFontName]
            # todo: either we always load all fonts, or we need to check in widget if font is required in case we load elements as runtime
            if oFont.uName in self.dUsedFonts or True:
                oFont.Register()
