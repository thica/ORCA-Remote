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



from typing                            import Union
from typing                            import Callable
from typing                            import Any
from xml.etree.ElementTree             import Element
from kivy.uix.widget                   import Widget
from ORCA.widgets.core.Border          import cBorder
from ORCA.widgets.helper.WidgetType    import eWidgetType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.definition.Definition import cDefinition
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")
    cDefinition   = TypeVar("cDefinition")

__all__ = ['cWidgetBaseBase']


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class cWidgetBaseBase:
    def __init__(self,**kwargs):

        self._bEnabled:bool                             = True
        self._uName:str                                 = u'noname'
        self._uAnchorName: str                          = u''
        self._eWidgetType:eWidgetType                   = eWidgetType.NoWidget

        self._iAnchorHeight:int                         = 0
        self._iAnchorPosX:int                           = 0
        self._iAnchorPosY:int                           = 0
        self._iAnchorWidth:int                          = 0

        self._iGapX:int                                 = 0
        self._iGapY:int                                 = 0
        self._iHeight:int                               = 10
        self._iHeightInit:int                           = 10
        self._iPosX:int                                 = 0
        self._iPosXInit:int                             = 0
        self._iPosY:int                                 = 0
        self._iPosYInit:int                             = 0
        self._iWidth:int                                = 10
        self._iWidthInit:int                            = 10
        self._fRationX:float                            = 1.0
        self._fRationY:float                            = 1.0
        self._fScale:float                              = 1.0
        self._fOrgOpacity:float                         = 1.0

        self._oBorder:Union[cBorder,None]               = None
        self._oDef:Union[cDefinition,None]              = None
        self._oObject:Union[Widget,None]                = None         # oObject is the kivy Widget
        self._oParent:Union[Widget,None]                = None
        self._oParentScreenPage:Union[cScreenPage,None] = None

    bIsEnabled:bool          = property(lambda self: self._bEnabled,       lambda self, value: setattr(self, '_bEnabled',value))
    uName:str                = property(lambda self: self._uName,          lambda self, value: setattr(self, '_uName',value))
    uAnchorName:str          = property(lambda self: self._uAnchorName,    lambda self, value: setattr(self, '_uAnchorName',value))
    eWidgetType:eWidgetType  = property(lambda self: self._eWidgetType,    lambda self, value: setattr(self, '_eWidgetType',value))

    iAnchorHeight:int        = property(lambda self: self._iAnchorHeight,  lambda self, value: setattr(self, '_iAnchorHeight',value))
    iAnchorWidth:int         = property(lambda self: self._iAnchorWidth,   lambda self, value: setattr(self, '_iAnchorWidth',value))
    iAnchorPosX:int          = property(lambda self: self._iAnchorPosX,    lambda self, value: setattr(self, '_iAnchorPosX',value))
    iAnchorPosY:int          = property(lambda self: self._iAnchorPosY,    lambda self, value: setattr(self, '_iAnchorPosY',value))
    iGapX:int                = property(lambda self: self._iGapX,          lambda self, value: setattr(self, '_iGapX',value))
    iGapY:int                = property(lambda self: self._iGapY,          lambda self, value: setattr(self, '_iGapY',value))
    iHeight:int              = property(lambda self: self._iHeight,        lambda self, value: setattr(self, '_iHeight',value))
    iHeightInit:int          = property(lambda self: self._iHeightInit,    lambda self, value: setattr(self, '_iHeightInit',value))
    iWidth:int               = property(lambda self: self._iWidth,         lambda self, value: setattr(self, '_iWidth',value))
    iWidthInit:int           = property(lambda self: self._iWidthInit,     lambda self, value: setattr(self, '_iWidthInit',value))
    iPosX:int                = property(lambda self: self._iPosX,          lambda self, value: setattr(self, '_iPosX',value))
    iPosXInit:int            = property(lambda self: self._iPosXInit,      lambda self, value: setattr(self, '_iPosXInit',value))
    iPosY:int                = property(lambda self: self._iPosY,          lambda self, value: setattr(self, '_iPosY',value))
    iPosYInit:int            = property(lambda self: self._iPosYInit,      lambda self, value: setattr(self, '_iPosYInit',value))
    fRationX:float           = property(lambda self: self._fRationX,       lambda self, value: setattr(self, '_fRationX',value))
    fRationY:float           = property(lambda self: self._fRationY,       lambda self, value: setattr(self, '_fRationY',value))
    fScale:float             = property(lambda self: self._fScale,         lambda self, value: setattr(self, '_fScale',value))
    fOrgOpacity:float        = property(lambda self: self._fOrgOpacity,    lambda self, value: setattr(self, '_fOrgOpacity',value))

    oBorder:Union[cBorder, None]               = property(lambda self: self._oBorder,           lambda self, value: setattr(self, '_oBorder',value))
    oDef:Union[cDefinition, None]              = property(lambda self: self._oDef,              lambda self, value: setattr(self, '_oDef',value))
    oObject:Union[Widget, None]                = property(lambda self: self._oObject,           lambda self, value: setattr(self, '_oObject',value))
    oParent:Union[Widget, None]                = property(lambda self: self._oParent,           lambda self, value: setattr(self, '_oParent',value))
    oParentScreenPage:Union[cScreenPage, None] = property(lambda self: self._oParentScreenPage, lambda self, value: setattr(self, '_oParentScreenPage',value))

    # as we can use most widgets as Anchors, we need to have interface and config generic
    uConfigName:str          = property(lambda self: self._uConfigName,      lambda self, value: setattr(self, '_uConfigName',value))
    uInterFace:str           = property(lambda self: self._uInterFace,       lambda self, value: setattr(self, '_uInterFace',value))


    def ParseXMLBaseNode (self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        return True
    def CreateBase(self,Parent:Widget,Class:Union[Callable,str]) -> bool:
        return True
    def SetCaption(self,uCaption:str) -> bool:
        return True
    def SetSecondCaption(self) -> bool:
        return True
    def UpdateWidget(self) -> bool:
        return True
    def UpdateWidgetSecondCaption(self) -> bool:
        return True
    def SetWidgetFontStyle(self,bBold:Union[bool,None],bItalic:Union[bool,None],uColor:Union[str,None]) -> bool:
        return True
    def GetWidgetFontStyle(self,uType:str) -> str:
        return u""
    def GetCaption(self) -> str:
        return u""
    def AddArg(self,uKey:str,oValue:Any) -> None:
        return

