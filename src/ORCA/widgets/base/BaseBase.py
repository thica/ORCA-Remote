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

import uuid

from typing                            import Union
from typing                            import Callable
from typing                            import Any
from typing                            import Optional
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

        self.bEnabled:bool                             = True
        self.bIsCreated:bool                           = False
        self.eWidgetType:eWidgetType                   = eWidgetType.NoWidget
        self.fOrgOpacity:float                         = 1.0
        self.fRationX:float                            = 1.0
        self.fRationY:float                            = 1.0
        self.fScale:float                              = 1.0
        self.iAnchorHeight:int                         = 0
        self.iAnchorPosX:int                           = 0
        self.iAnchorPosY:int                           = 0
        self.iAnchorWidth:int                          = 0
        self.iGapX:int                                 = 0
        self.iGapY:int                                 = 0
        self.iHeight:int                               = 10
        self.iHeightInit:int                           = 10
        self.iPosX:int                                 = 0
        self.iPosXInit:int                             = 0
        self.iPosY:int                                 = 0
        self.iPosYInit:int                             = 0
        self.iWidth:int                                = 10
        self.iWidthInit:int                            = 10
        self.oBorder:Union[cBorder,None]               = None
        self.oDef:Union[cDefinition,None]              = None
        self.oObject:Union[Widget,None]                = None         # oObject is the kivy Widget
        self.oParent:Union[Widget,None]                = None
        self.oParentScreenPage:Union[cScreenPage,None] = None
        self.uAnchorName: str                          = u''
        self.uConfigName:str                           = u''  # as we can use most widgets as Anchors, we need to have interface and config generic
        self.uFileName:str                             = u''
        self.uID                                       = str(uuid.uuid4())
        self.uInterFace:str                            = u''  # as we can use most widgets as Anchors, we need to have interface and config generic
        self.uLastWidgetID                             = u''
        self.uName:str                                 = u'noname'

    def ParseXMLBaseNode (self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        # dummy
        return True
    def CreateBase(self,Parent:Widget,Class:Union[Callable,str]) -> bool:
        # dummy
        return True
    def SetCaption(self,uCaption:str) -> bool:
        # dummy
        return True
    def SetSecondCaption(self) -> bool:
        # dummy
        return True
    def UpdateWidget(self) -> bool:
        # dummy
        return True
    def UpdateWidgetSecondCaption(self) -> bool:
        # dummy
        return True
    def SetWidgetFontStyle(self,bBold:Union[bool,None],bItalic:Union[bool,None],uColor:Union[str,None]) -> bool:
        # dummy
        return True
    def GetWidgetFontStyle(self,uType:str) -> str:
        # dummy
        return u""
    def GetCaption(self) -> str:
        # dummy
        return u""
    def AddArg(self,uKey:str,oValue:Any) -> None:
        # dummy
        return

