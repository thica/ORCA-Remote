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

from ORCA.Globals import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.action.Action import cAction
else:
    from typing import TypeVar
    cAction = TypeVar('cAction')


__all__ = ['cFonts', 'cFontDef']

class cFontDef:
    """
    Object which holds the definition of a named font to
    be able to be used by a definition
    """

    def __init__(self)->None:
        self.uName:str                        = ''
        self.oFnNormal:cFileName              = cFileName('')
        self.oFnBold:cFileName                = cFileName('')
        self.oFnItalic:cFileName              = cFileName('')
        self.oFnBoldItalic:cFileName          = cFileName('')

    def ParseFontFromXMLNode(self,*,oXMLNode:Element) -> int:
        """
        Parses a font definition from an xml node

        :return: The Number of fonts, defined in the XML
        :param oXMLNode: An elementree xml node
        """

        uFontStyle:str
        self.uName = GetXMLTextValue(oXMLNode=oXMLNode,uTag='name',bMandatory=True,vDefault='NoName')
        iCount:int = 0
        for oXMLSingleFont in oXMLNode.findall('file'):
            iCount += 1
            uFontStyle = GetXMLTextAttribute(oXMLNode=oXMLSingleFont,uTag='face',bMandatory=True,vDefault='')
            if uFontStyle=='normal':
                self.oFnNormal.ImportFullPath(uFnFullName=oXMLSingleFont.text)
            elif uFontStyle=='bold':
                self.oFnBold.ImportFullPath(uFnFullName=oXMLSingleFont.text)
            elif uFontStyle=='italic':
                self.oFnItalic.ImportFullPath(uFnFullName=oXMLSingleFont.text)
            elif uFontStyle=='bolditalic':
                self.oFnBoldItalic.ImportFullPath(uFnFullName=oXMLSingleFont.text)
            else:
                ShowErrorPopUp(uMessage=LogError(uMsg='FontParser: Invalid Tag:'+uFontStyle))
        return iCount

    def Register(self) -> None:
        """
        Registers Font in the app system
        :return: None
        """
        Logger.debug('Register Font: ' + self.oFnNormal)

        uFnNormal:Optional[str]        = str(self.oFnNormal)
        uFnItalic:[str,None]           = str(self.oFnItalic)
        uFnBold:[str,None]             = str(self.oFnBold)
        uFnBoldItalic:[str,None]       = str(self.oFnBoldItalic)

        if uFnNormal == '':     uFnNormal = None
        if uFnItalic =='':      uFnItalic = None
        if uFnBold =='':        uFnBold   = None
        if uFnBoldItalic =='':  uFnBoldItalic = None

        LabelBase.register(self.uName, uFnNormal, uFnItalic, uFnBold, uFnBoldItalic)
        return None


class cFonts:
    """ Represents all Fonts Object """
    def __init__(self):
        self.dFonts:Dict[str,cFontDef]     = {}
        self.dUsedFonts:Dict[str,bool]     = {}

    def DeInit(self) -> None:
        """ we do nothing by purpose  """
        pass

    def ParseDirect(self,*,uFontName:str, uFontFileNormal:str) -> None:
        """"
        Adds a font object to the font list
        """
        oTmpFont:cFontDef   = cFontDef()
        oTmpFont.uName      = uFontName
        oTmpFont.oFnNormal  = cFileName(uFontFileNormal)
        self.dFonts[oTmpFont.uName] = oTmpFont

    # noinspection PyMethodMayBeStatic
    def ParseIconsFromXMLNode(self,*,oXMLNode:Element) -> None:
        """
        Parses all icon definitions from the xml objects
        """
        oXMLIcons:Element = oXMLNode.find('icons')
        if oXMLIcons is not None:
            Logger.info('Loading Icons')
            for oXMLIcon in oXMLIcons.findall('icon'):
                uIconName:str           = GetXMLTextAttribute(oXMLNode=oXMLIcon,uTag='name',bMandatory=True, vDefault='')
                oFnIconFont:cFileName   = cFileName(GetXMLTextAttribute(oXMLNode=oXMLIcon, uTag='font', bMandatory=True, vDefault=''))
                uIconChar:str           = GetXMLTextAttribute(oXMLNode=oXMLIcon, uTag='char', bMandatory=True, vDefault='')
                uFontName:str           = oFnIconFont.basename
                fIconScale:float        = GetXMLFloatAttribute(oXMLNode=oXMLIcon, uTag='scale', bMandatory=False, fDefault=1.0)
                Globals.dIcons[uIconName] = {'fontfile': str(oFnIconFont), 'char': uIconChar, 'fontname':uFontName, 'scale':fIconScale}
                Globals.oTheScreen.oFonts.ParseDirect(uFontName=uFontName, uFontFileNormal=str(oFnIconFont))

    def ParseFontFromXMLNode(self,*,oXMLNode:Element) -> int:
        """
        Parses all font definitions from the xml objects
        """
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
            Logger.debug ('TheScreen: Register Fonts')
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
                Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None,uQueueName='RegisterFonts')
        else:
            oFont=self.dFonts[uFontName]
            # todo: either we always load all fonts, or we need to check in widget if font is required in case we load elements as runtime
            if oFont.uName in self.dUsedFonts or True:
                oFont.Register()
