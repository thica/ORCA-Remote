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

from __future__                        import annotations #todo: remove in Python 4.0

from typing                            import Union
from typing                            import Dict
from typing                            import List
from typing                            import Callable

from xml.etree.ElementTree             import Element

from kivy.logger                       import Logger
from kivy.metrics                      import dp,sp
from kivy.uix.widget                   import Widget

from ORCA.utils.LogError               import LogError
from ORCA.utils.TypeConvert            import ToInt
from ORCA.utils.XML                    import GetXMLBoolAttribute
from ORCA.utils.XML                    import GetXMLTextAttribute
from ORCA.utils.XML                    import GetXMLIntAttribute
from ORCA.vars.Replace                 import ReplaceVars
from ORCA.widgets.helper.WidgetType    import eWidgetType
from ORCA.widgets.helper.HexColor      import GetColorFromHex
from ORCA.widgets.helper.HexColor      import GetHexFromColor
from ORCA.widgets.helper.HexColor      import aColorUndefined
from ORCA.widgets.helper.HexColor      import uColorUndefined

from ORCA.Globals import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.screen.ScreenPage import cScreenPage
    from ORCA.widgets.base.Base     import cWidgetBase
else:
    from typing import TypeVar
    cScreenPage   = TypeVar('cScreenPage')
    cWindgetBase  = TypeVar('cWindgetBase')

__all__ = ['cWidgetBaseText']

from ORCA.widgets.base.BaseBase import cWidgetBaseBase

class cWidgetBaseText(cWidgetBaseBase):
    # BaseText Class for all ORCA widgets with Text Capabilities
    def __init__(self,**kwargs):

        super().__init__(**kwargs)

        self.bBold:bool                                 = False
        self.bShorten:bool                              = False
        self.bItalic:bool                               = False
        self.bIcon:bool                                 = False
        self.bNoTextSize:bool                           = False
        self.dActionPars:Dict[str,str]                  = {} # Actionpars will be passed to Actions within command set, existing pars will be replaced!
        self.dKwArgs:Dict                               = {}
        self.iFontSize:int                              = 30
        self.iIconFontSize:int                          = 50
        self.iFontSizeInit:int                          = 30
        self.iLines:int                                 = 0
        self.aTextColor:List[float]                     = GetColorFromHex('#FFFFFFFF')
        self.uFontIndex:str                             = 'Sans'
        self.uhTextAlign:str                            = 'center'
        self.uOrgCaption:str                            = ''
        self.uOrgSecondCaption:str                      = ''
        self.uOrgFontIndex:str                          = self.uFontIndex
        self.uSecondCaption:str                         = ''
        self.uvTextAlign:str                            = 'top'
        self.uCaption:str                               = ''

     # noinspection PyUnresolvedReferences
    def ParseXMLBaseNode (self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:

        try:
            super().ParseXMLBaseNode(oXMLNode, oParentScreenPage, uAnchor)
            self.uCaption           = ''
            self.uhTextAlign        =   GetXMLTextAttribute (oXMLNode=oXMLNode,uTag='htextalign',   bMandatory=False, vDefault='center')
            self.uvTextAlign        =   GetXMLTextAttribute (oXMLNode=oXMLNode,uTag='vtextalign',   bMandatory=False, vDefault='middle')
            self.bShorten           =   GetXMLBoolAttribute (oXMLNode=oXMLNode,uTag='shorten',      bMandatory=False, bDefault=False)
            self.bBold              =   GetXMLBoolAttribute (oXMLNode=oXMLNode,uTag='bold',         bMandatory=False, bDefault=False)
            self.bItalic            =   GetXMLBoolAttribute (oXMLNode=oXMLNode,uTag='italic',       bMandatory=False, bDefault=False)
            self.iLines             =   GetXMLIntAttribute  (oXMLNode=oXMLNode,uTag='lines',        bMandatory=False, iDefault=0)
            self.uFontIndex         =   GetXMLTextAttribute (oXMLNode=oXMLNode,uTag='fontid',       bMandatory=False, vDefault=self.oDef.uDefaultFont)
            self.uOrgFontIndex      =   self.uFontIndex
            uFontSize:str           =   GetXMLTextAttribute (oXMLNode=oXMLNode,uTag='fontsize',                 bMandatory=False, vDefault='0')
            uIconFontSize:str       =   GetXMLTextAttribute (oXMLNode=oXMLNode,uTag='iconfontsize',             bMandatory=False, vDefault=uFontSize)
            self.aTextColor         =   GetColorFromHex(GetXMLTextAttribute (oXMLNode=oXMLNode,uTag='textcolor',bMandatory=False, vDefault=uColorUndefined))
            self.SetCaption(GetXMLTextAttribute(oXMLNode=oXMLNode, uTag='caption',                              bMandatory=False, vDefault=''))
            self.uOrgSecondCaption  =   GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='secondcaption',             bMandatory=False, vDefault='')
            Globals.oTheScreen.oFonts.dUsedFonts[self.uFontIndex]=True

            if self.aTextColor == aColorUndefined:
                if self.eWidgetType == eWidgetType.Button or self.eWidgetType == eWidgetType.DropDown or self.eWidgetType == eWidgetType.Switch:
                    self.aTextColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('color font button')
                elif self.eWidgetType == eWidgetType.TextField or self.eWidgetType == eWidgetType.TextInput or self.eWidgetType == eWidgetType.Slider:
                    self.aTextColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('color font text')
                elif self.eWidgetType == eWidgetType.FileViewer or self.eWidgetType == eWidgetType.Settings:
                   self.aTextColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('color font file')
                elif self.eWidgetType == eWidgetType.BackGround:
                    self.aTextColor = GetColorFromHex('#FFFFFFFF')
                if self.aTextColor == aColorUndefined:
                    self.aTextColor = GetColorFromHex('#FFFFFFFF')

            if uFontSize == '0':
                if self.eWidgetType == eWidgetType.Button or self.eWidgetType == eWidgetType.DropDown or self.eWidgetType == eWidgetType.Switch:
                    uFontSize = self.oDef.uFontSize_Button
                elif self.eWidgetType == eWidgetType.TextField or self.eWidgetType == eWidgetType.TextInput or self.eWidgetType == eWidgetType.Slider:
                    uFontSize = self.oDef.uFontSize_Text
                elif self.eWidgetType == eWidgetType.FileViewer or self.eWidgetType == eWidgetType.Settings:
                    uFontSize = self.oDef.uFontSize_File

            if uIconFontSize == '0':
                if self.eWidgetType == eWidgetType.Button or self.eWidgetType == eWidgetType.DropDown or self.eWidgetType == eWidgetType.Switch:
                    uIconFontSize = self.oDef.uFontSize_Button
                elif self.eWidgetType == eWidgetType.TextField or self.eWidgetType == eWidgetType.TextInput or self.eWidgetType == eWidgetType.Slider:
                    uIconFontSize = self.oDef.uFontSize_Text
                elif self.eWidgetType == eWidgetType.FileViewer or self.eWidgetType == eWidgetType.Settings:
                    uIconFontSize = self.oDef.uFontSize_File

            # todo: check where to scale fonts
            if uFontSize[0] == 'd':
                self.iFontSize = dp(uFontSize[1:])   *self.fRationX
            elif uFontSize[0] == 's':
                self.iFontSize = sp(uFontSize[1:])  *self.fRationX
            elif uFontSize.startswith('%h'):
                self.iFontSize = ((int(uFontSize[2:])*self.iHeight)/100) # *self.fRationY
            elif uFontSize.startswith('%w'):
                self.iFontSize = ((int(uFontSize[2:])*self.iWidth)/100) # *self.fRationX
            else:
                self.iFontSize = ToInt(uFontSize)
                if self.iFontSize != 0:
                    Logger.warning('Depreciated absolute fontsize used:'+self.uName+ ' from:'+self.uPageName)

            if uIconFontSize[0] == 'd':
                self.iIconFontSize = dp(uIconFontSize[1:])   *self.fRationX
            elif uIconFontSize[0] == 's':
                self.iIconFontSize = sp(uIconFontSize[1:])  *self.fRationX
            elif uIconFontSize.startswith('%h'):
                self.iIconFontSize = ((int(uIconFontSize[2:])*self.iHeight)/100) # *self.fRationY
            elif uIconFontSize.startswith('%w'):
                self.iIconFontSize = ((int(uIconFontSize[2:])*self.iWidth)/100) # *self.fRationX
            else:
                self.iIconFontSize = ToInt(uIconFontSize)
                if self.iIconFontSize != 0:
                    Logger.warning('Depreciated absolute fontsize used:'+self.uName+ ' from:'+self.uPageName)

            self.iFontSizeInit  = self.iFontSize
            return True
        except Exception as e:
            LogError(uMsg='Error parsing widget from element (Text):['+self.uName+']',oException=e)
            return False

    def CreateBase(self,Parent:Widget,Class:Union[Callable,str]) -> bool:

        try:
            super().CreateBase(Parent, Class)
            self.CalcFontSize()
            self.AddArg('halign',               self.uhTextAlign)
            self.AddArg('valign',               self.uvTextAlign)
            self.AddArg('italic',               self.bItalic)
            self.AddArg('bold',                 self.bBold)
            self.AddArg('max_lines',            self.iLines)
            self.AddArg('shorten',              self.bShorten)
            if not self.bNoTextSize:
                self.AddArg('text_size',        (self.iWidth,self.iHeight))
            self.AddArg('color',                self.aTextColor)
            self.AddArg('foreground_color',     self.aTextColor)
            self.AddArg('font_name',            self.uFontIndex)
            self.AddArg('text'     ,            self.uCaption)
            self.SetCaption(self.uCaption)

            #self.oObject.shorten=   True
            if self.iFontSize > 0:
                # a further unicode bug in kivy: font_size just except strings not unicode strings
                self.AddArg('font_size',str(self.iFontSize)+'px')

            # Fonts are loaded at initialisation, but if we load elements at runtime, the font might not be registered
            if not self.uFontIndex in Globals.oTheScreen.oFonts.dUsedFonts:
                oFont=Globals.oTheScreen.oFonts.dFonts[self.uFontIndex]
                oFont.Register()
                Globals.oTheScreen.oFonts.dUsedFonts[self.uFontIndex]=True

            return True
        except Exception as e:
            LogError(uMsg='Can\'t create widget (Text):'+self.uName,oException=e)
            return False

    def CalcFontSize(self) -> None:
        if self.bIcon:
            self.iFontSize = int(self.iIconFontSize * self.fScale) / self.oDef.fRationX
        else:
            self.iFontSize = self.iFontSizeInit / self.oDef.fRationX

    def UpdateWidget(self) -> bool:
        super().UpdateWidget()
        return self.SetCaption(self.uOrgCaption)

    def UpdateWidgetSecondCaption(self) -> bool:
        super().UpdateWidgetSecondCaption()
        return self.SetSecondCaption()

    def SetCaption(self,uCaption:str) -> bool:
        super().SetCaption(uCaption)
        if self.uOrgCaption == '' and uCaption!='':
            self.uOrgCaption = uCaption

        if not '$var(' in self.uOrgCaption:
            if not '$lvar(' in self.uOrgCaption:
                if not self.uOrgCaption.startswith('icon:'):
                    if not ':::' in self.uOrgCaption and self.eWidgetType==eWidgetType.DropDown:
                        self.uOrgCaption = uCaption

        uTmp=ReplaceVars(uCaption)
        if uTmp.startswith('$var(') or uTmp.startswith('$lvar('):
            self.uCaption = ''
        else:
            self.uCaption = uTmp

        self.bIcon = False
        self.uFontIndex = self.uOrgFontIndex

        if self.uCaption.startswith('icon:'):
            self.HandleIcon()

        if self.oObject:
            self.CalcFontSize()
            self.oObject.font_name = self.uFontIndex
            self.oObject.text      = self.uCaption
            self.oObject.font_size = self.iFontSize
        return True

    def SetSecondCaption(self) -> bool:

        super().SetSecondCaption()

        uTmp:str = ReplaceVars(self.uOrgSecondCaption)
        if uTmp.startswith('$var(') or uTmp.startswith('$lvar('):
            self.uSecondCaption = ''
        else:
            self.uSecondCaption = uTmp

        if self.uSecondCaption=='':
            return True

        self.bIcon      = False
        self.uCaption   = self.uSecondCaption
        self.uFontIndex = self.uOrgFontIndex

        if self.uSecondCaption.startswith('icon:'):
            self.HandleIcon()
            self.uSecondCaption = self.uCaption

        if self.oObject:
            self.CalcFontSize()
            self.oObject.text      = self.uSecondCaption
            self.oObject.font_name = self.uFontIndex
            self.oObject.font_size = self.iFontSize

        return True

    def HandleIcon(self, oWidget:Union[cWidgetBase,None] = None) -> None:

        if oWidget is None:
            oWidget = self

        uIcon  = oWidget.uCaption[5:]
        iPos   = uIcon.find(' color:')
        if iPos > 0:
            uColor = uIcon[iPos + 7:]
            uIcon = uIcon[:iPos]
            oWidget.aTextColor = GetColorFromHex(uColor)

        dIcon = Globals.dIcons.get(uIcon)
        if dIcon:
            oWidget.uCaption = dIcon['char']
            if dIcon['fontname']:
                oWidget.uFontIndex = dIcon['fontname']
                self.bIcon = True
            oWidget.fScale = dIcon['scale']

    def SetWidgetFontStyle(self,bBold:Union[bool,None],bItalic:Union[bool,None],uColor:Union[str,None]) -> bool:

        super().SetWidgetFontStyle(bBold,bItalic,uColor)

        if bBold is not None:
            self.bBold = bBold
            if self.oObject:
                self.oObject.bold = self.bBold
        if bItalic is not None:
            self.bItalic = bItalic
            if self.oObject:
                self.oObject.italic = self.bItalic
        if uColor is not None:
            self.aTextColor = GetColorFromHex(uColor)
            if self.oObject:
                self.oObject.color = self.aTextColor
        return True

    def GetWidgetFontStyle(self,uType:str) -> str:
        super().GetWidgetFontStyle(uType)
        uRet:str = 'error'
        try:
            if uType=='bold':
                uRet='0'
                if self.bBold:
                    uRet='1'
            elif uType=='italic':
                uRet='0'
                if self.bItalic:
                    uRet='1'
            elif uType=='textcolor':
                uRet=GetHexFromColor(self.aTextColor)
        except Exception:
            pass
        return uRet

    def GetCaption(self) -> str:
        return self.uCaption

