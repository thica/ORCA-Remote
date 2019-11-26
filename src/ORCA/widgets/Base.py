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

from __future__                        import annotations #todo: remove in Python 4.0


'''
WikiDoc:Doc
WikiDoc:Context:Widgets
WikiDoc:Page:Widgets-Overview
WikiDoc:TOCTitle:Overview

Widgets are elements you can place on the screen. There are widgets to show information (Text, Pictures, etc), Widgets to start actions (Buttons, Backgrounds), and Widgets to structure your definition (Anchors).

Widgets are defined by a xml line as part of your page definition. You can control position, size, captions and other attributes of your widget by adjusting the xml attributes of your widget in the xml section.

The following widgets are available

WikiDoc:TOC:Widgets:List
 
WikiDoc:End
'''


from typing                            import Tuple
from typing                            import Union
from typing                            import Dict
from typing                            import List
from typing                            import Callable
from typing                            import Any

from xml.etree.ElementTree             import Element

from kivy.logger                       import Logger
from kivy.utils                        import get_color_from_hex
from kivy.metrics                      import dp,sp
from kivy.uix.layout                   import Layout
from kivy.uix.widget                   import Widget

from ORCA.utils.CheckCondition         import CheckCondition
from ORCA.utils.LogError               import LogError
from ORCA.utils.Platform               import OS_Vibrate
from ORCA.utils.TypeConvert            import ToDic
from ORCA.utils.TypeConvert            import ToInt
from ORCA.utils.XML                    import GetXMLBoolAttribute
from ORCA.utils.XML                    import GetXMLTextAttribute
from ORCA.utils.XML                    import SplitMax
from ORCA.vars.Replace                 import ReplaceVars
from ORCA.widgets.core.Border          import cBorder
from ORCA.widgets.helper.WidgetType    import eWidgetType
from ORCA.widgets.helper.WidgetType    import dWidgetTypeToId
from ORCA.widgets.helper.HexColor      import GetColorFromHex
from ORCA.widgets.helper.HexColor      import GetHexFromColor
from ORCA.widgets.helper.HexColor      import aColorUndefined
from ORCA.widgets.helper.HexColor      import uColorUndefined

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.definition.Definition import cDefinition
    from ORCA.ScreenPage            import cScreenPage
    from ORCA.widgets.Anchor        import cWidgetAnchor
    from ORCA.Action                import cAction
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")
    cDefinition   = TypeVar("cDefinition")
    cWidgetAnchor = TypeVar("cWidgetAnchor")
    cAction       = TypeVar("cAction")

__all__ = ['cWidgetBase']

oLastWidget:Union[cWidgetBase,None]     = None
oLastWidgetSave:Union[cWidgetBase,None] = None

class cWidgetBase:
    # Base Class for all ORCA widgets
    # we do not derivite from kivy classes by purpose
    # Kivy classes are objects within the Orca classes

    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-Common Attributes
    WikiDoc:TOCTitle:Common Attributes

    Some widgets have attributes, which are unique to them, some other attributes are common to all widgets. Below you find a list and a explanation of all common attributes.

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |name
    |Optional: Name of the widget
    |-
    |posx
    |The horizontal position of the widget. Default is 0 (left). You can either use virtual pixel, a percentage value to the screen or position attributs. For percentange values, the value has to start with a percentage sign, followed by a value between 0 and 100 (eg %65). %0 would mean left aligned, %100 would mean right alignend and %50 would mean center. You could use the position attributs "left", "right" and "center" as well. Positioning is either based on the virtual screen coordinates, or based on the relevant anchor.
    |-
    |posy
    |The vertical position of the widget. Default is 0 (top). You can either use virtual pixel, a percentage value to the screen or position attributs. For percentange values, the value has to start with a percentage sign, followed by a value between 0 and 100 (eg %65). %0 would mean top aligned, %100 would mean bottom alignend and %50 would mean middle aligned. You could use the position attributs "top", "bottom" and "middle" as well. Positioning is either based on the virtual screen coordinates, or based on the relevant anchor.  T
    |-
    |width
    |The width of the widget in virtual pixel. If  no width is given, the width of the last ancor is used. You can use a % of the width of the last ancor as well (eg. '%30')
    |-
    |height
    |The height of the widget in virtual pixel. If  no height is given, the height of the last ancor is used. You can use a % of the height of the last ancor as well (eg. '%30').
    |-
    |Relative size and positions
    |There are special options to set the size and position based on other wigets or based on itself. The widget attribute (posx,posy,width,height) has to start with "of:". Than you need to specify, what attribut you would like to refer to too. This can be one of the following words:
    * top: You get the posy attribut from the referred widget
    * left: You get the posx attribut from the referred widget
    * bottom: You get the bottom attribut (posy+height) from the referred widget
    * right: You get the right attribut (posx+width) from the referred widget
    * width:  You get the width attribut from the referred widget
    * height: You get the height attribut from the referred widget
    * totop: Helpful to attach a widget on top on another: posy of the referred widget plus the own widget height
    * toleft:  Helpful to attach a widget to left on another: posy of the referred widget plus the own widget height
    The third element (after a colon) points to the referred widget. Can be either
    * widget name: refers to the widget with the given name
    * self: refers to the widget itself
    * last: refers to the last used widget
    The forth element (after a colon) is optional. You can multiply the pulled value with the vlue given here.

    Examples:
    width='of:height:self:*0.5'
    This creates a widget width half of its own height

    posy='of:totop:Anchor Name'
    Puts the widget on top of the Anchor with name "Anchor Name"
    |-
    |enabled
    |Specify, if a widget is enabled- By default all widgets are enabled. If a widget is disabled. it is not visible on the screen. There a actions to enable or disable widget at runtime. Please use "0" to disable a widget and "1" to enable a widget.
    |-
    |backgroundcolor
    |The background color of the widget in hexedecimal RGBA format. It has to start with a pound sign (eg: #ff00ffff). Please use only low capital chars.
    |-
    |anchor
    |You can specify an anchor to use for the xpos and ypos attributes. If you embedd the widget within a anchor, the anchor will be assigned automtic, otherwis you can specify the name of the nchor manually here.
    |-
    |action
    |If a widget supports action, you can specify the name of the action here. This is the singletap action
    |-
    |actiondoubletap
    |If a widget supports action, you can specify the name of the action here. This is the doubletap action
    |-
    |actionlongtap
    |If a widget supports action, you can specify the name of the action here. This is the longtap action
    |-
    |actiondownonly
    |If a widget supports action, you can specify the name of the action here. This is the action if you want to call something explicit on a touch down
    |-
    |actionuponly
    |If a widget supports action, you can specify the name of the action here. This is the action if you want to call something explicit on a touch up
    |-
    |actionpars
    |If a widget supports action, you can specify additional paramater to pass the action as an json string. For calls and functions a variable will be created for each action par (see actions:call)
    |-
    |interface
    |Sets the interface for this action. You can either use the direct interface name, or, even better, use a variable which points to the interface name. Please refer to section "Variables" to understand, how to use variables. You should just set the interface, if it is different from the page default interface or from the anchor interface.
    |-
    |configname
    |Sets the configuration for this action. You can either use the direct configuraton name, or, even better, use a variable which points to the configuration name. Please refer to section "Variables" to understand, how to use variables. You should just set the configuration name, if it is different from the page default configuration or from the anchor configuration.
    |}</div>

    An example line for a widget could look like the example below.

    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Button Power On' type='BUTTON' posx='left' posy='top' height='%50' picturenormal='button square*' action='Send Power On'  fontsize='%h70'  textcolor='$var(green)' caption='icon:power_on' />
    <element name="Button Back" type="BUTTON" posx="right" posy="top" width="%12" height="of:width:self" picturenormal="button wide*" action="Show Page" actionpars='{"pagename":"$var(LASTPAGE)"}' fontsize='%h40' caption="icon:close_window" />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    # noinspection PyUnresolvedReferences
    def __init__(self,**kwargs):

        self.bHasText=kwargs.get('hastext')
        if self.bHasText is None:
            self.bHasText=False

        self.aWidgetActions:List[Dict]                  = []
        self.bBold:bool                                 = False
        self.bEnabled:bool                              = True
        self.bItalic:bool                               = False
        self.bIcon:bool                                 = False
        self.bNoTextSize:bool                           = False
        self.dActionPars:Dict[str,str]                  = {} # Actionpars will be passed to Actions within command set, existing pars will be replaced!
        self.dKwArgs:Dict                               = {}
        self.fOrgOpacity:float                          = 1.0
        self.fScale:float                               = 1.0
        self.fRationX:float                             = 1.0
        self.fRationY:float                             = 1.0
        self.iAnchorHeight:int                          = 0
        self.iAnchorPosX:int                            = 0
        self.iAnchorPosY:int                            = 0
        self.iAnchorWidth:int                           = 0
        self.iFontSize:int                              = 30
        self.iGapX:int                                  = 0
        self.iGapY:int                                  = 0
        self.iIconFontSize:int                          = 50
        self.iFontSizeInit:int                          = 30
        self.iHeight:int                                = 10
        self.iHeightInit:int                            = 10
        self.iPosX:int                                  = 0
        self.iPosXInit:int                              = 0
        self.iPosY:int                                  = 0
        self.iPosYInit:int                              = 0
        self.eWidgetType:eWidgetType                    = eWidgetType.NoWidget
        self.iWidth:int                                 = 10
        self.iWidthInit:int                             = 10
        self.oBorder:Union[cBorder,None]                = None
        self.oDef:Union[cDefinition,None]               = None
        self.oObject:Union[Widget,None]                 = None         # oObject is the kivy Widget
        self.oParent:Union[Widget,None]                 = None
        self.oParentScreenPage:Union[cScreenPage,None]  = None
        self.oTmpAnchor:Union[cWidgetAnchor,None]       = None
        self.aBackGroundColor:List[float]               = aColorUndefined
        self.aTextColor:List[float]                     = GetColorFromHex('#FFFFFFFF')
        self.uActionName:str                            = u''
        self.uActionNameDoubleTap:str                   = u''
        self.uActionNameDownOnly:str                    = u''
        self.uActionNameLongTap:str                     = u''
        self.uActionNameUpOnly:str                      = u''
        self.uAnchorName:str                            = u''
        self.uBackGroundColor:str                       = u''
        self.uCaption:str                               = u''
        self.uConfigName:str                            = u''
        self.uDefinitionContext:str                     = u''
        self.uFontIndex:str                             = u'Sans'
        self.uhTextAlign:str                            = u'center'
        self.uInterFace:str                             = u''
        self.uContainer:str                             = u''
        self.uTypeString:str                            = u''
        self.uName:str                                  = u'noname'
        self.uOrgCaption:str                            = u''
        self.uOrgSecondCaption:str                      = u''
        self.uOrgFontIndex:str                          = self.uFontIndex
        self.uPageName:str                              = u''
        self.uSecondCaption:str                         = u''
        self.uTapType:str                               = u''
        self.uvTextAlign:str                            = u'top'
        self.dObject_kwargs:Dict                        = {} # The kwargs used to create the kivy object

    # noinspection PyUnresolvedReferences
    def ParseXMLBaseNode (self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:

        uDefinitionContext:str
        uAlias:str
        oDef:Union[cDefinition,None]
        iAnchorWidth:int
        iAnchorHeight:int
        bApplyWidth:bool
        fVar:float


        try:
            global oLastWidget

            self.GetWidgetTypeFromXmlNode(oXMLNode)

            uDefinitionContext  = GetXMLTextAttribute  (oXMLNode,u'definitioncontext',  False, Globals.uDefinitionContext)
            uAlias              = oXMLNode.get('definitionalias')
            oDef                = None
            if uAlias is not None:
                oDef = Globals.oDefinitions.dDefinitionList_Dict[uAlias]

            self.oDef               = oDef
            self.uDefinitionContext = uDefinitionContext
            self.uName              = GetXMLTextAttribute(oXMLNode,u'name',True,u'NoName')
            self.oParentScreenPage  = oParentScreenPage
            self.uPageName          = self.oParentScreenPage.uPageName

            #default anchor is screen
            self.iAnchorPosX         = 0
            self.iAnchorPosY         = 0
            self.iAnchorWidth        = self.oDef.iDefMaxX
            self.iAnchorHeight       = self.oDef.iDefMaxY
            self.iGapX               = oDef.iGapX
            self.iGapY               = oDef.iGapY
            self.fRationX            = oDef.fRationX
            self.fRationY            = oDef.fRationY
            self.uAnchorName         = GetXMLTextAttribute(oXMLNode,u'anchor',False,u'')

            if self.uAnchorName == u'':
                self.uAnchorName=uAnchor

            if self.uAnchorName:
                # we use only the first Anchor with that name
                aTmpAnchors=self.oParentScreenPage.dWidgets[self.uAnchorName]
                if aTmpAnchors:
                    self.oTmpAnchor=aTmpAnchors[-1]
                    # oTmpAnchor is already aligned to screen size
                    self.iAnchorPosX         = self.oTmpAnchor.iPosX
                    self.iAnchorPosY         = self.oTmpAnchor.iPosY
                    self.iAnchorWidth        = self.oTmpAnchor.iWidth
                    self.iAnchorHeight       = self.oTmpAnchor.iHeight
                else:
                    self.oTmpAnchor=None

            # We parse for Text and change later to integer
            uWidth  = ReplaceVars(GetXMLTextAttribute(oXMLNode, u'width', False, u''))
            uHeight = ReplaceVars(GetXMLTextAttribute(oXMLNode, u'height', False, u''))

            iAnchorWidth  = self.iAnchorWidth
            iAnchorHeight = self.iAnchorHeight

            self.iWidth,bApplyWidth = self.CalculateWidth(uWidth,iAnchorWidth)
            self.iHeight            = self.CalculateHeight(uHeight,iAnchorHeight)
            if bApplyWidth:
                self.iWidth = self._ParseDimPosValue(uWidth)

            #We parse for Text and change later to integer
            self.iPosX                = ReplaceVars(GetXMLTextAttribute  (oXMLNode,u'posx',   False, u'left'))
            self.iPosY                = ReplaceVars(GetXMLTextAttribute  (oXMLNode,u'posy',   False, u'top'))
            self.bEnabled             = GetXMLBoolAttribute (oXMLNode,u'enabled', False,True)
            self.uCaption             = u''
            self.uContainer           = GetXMLTextAttribute(oXMLNode, u'container', False, u'')
            self.uBackGroundColor     = GetXMLTextAttribute(oXMLNode,u'backgroundcolor',False,u'#00000000')
            self.aBackGroundColor     = GetColorFromHex(ReplaceVars(self.uBackGroundColor))
            self.uActionName          = GetXMLTextAttribute(oXMLNode,u'action',False,u'')
            self.uActionNameDoubleTap = GetXMLTextAttribute(oXMLNode,u'actiondoubletap',False,u'')
            self.uActionNameLongTap   = GetXMLTextAttribute(oXMLNode,u'actionlongtap',False,u'')
            self.uActionNameDownOnly  = GetXMLTextAttribute(oXMLNode,u'actiondownonly',False,u'')
            self.uActionNameUpOnly    = GetXMLTextAttribute(oXMLNode,u'actionuponly',False,u'')
            self.uInterFace           = GetXMLTextAttribute(oXMLNode,u'interface',False,u'')
            self.uConfigName          = GetXMLTextAttribute(oXMLNode,u'configname',False,u'')
            uActionPars:str           = GetXMLTextAttribute(oXMLNode,u'actionpars',False,u'{}')
            if uActionPars.startswith("$var("):
                uActionPars=ReplaceVars(uActionPars)

            self.dActionPars=ToDic(uActionPars)

            if self.uActionName.startswith("SendCommand "):
                if len(self.dActionPars)==0:
                    self.dActionPars={"commandname":self.uActionName[12:]}
                    self.uActionName="Send"

            if not self.uInterFace==u'':
                Globals.oInterFaces.dUsedInterfaces[self.uInterFace]=True

            uPosY = ReplaceVars(GetXMLTextAttribute  (oXMLNode,u'posy',   False, u'top'))
            self.iPosY=self.CalculatePosY(uPosY)


            fPercentage=-1.0
            if not self.iPosX==u'':
                if self.iPosX==u'right':
                    fPercentage=100.0
                elif self.iPosX.startswith('of:'):
                    self.iPosX=self._ParseDimPosValue(self.iPosX)
                elif self.iPosX==u'left':
                    fPercentage=0.0
                elif self.iPosX==u'center':
                    fPercentage=50.0
                elif self.iPosX.isdigit():
                    Logger.warning("Depreciated absolute PosX used:"+self.uName+ " from:"+self.uPageName)
                    self.iPosX=(int(self.iPosX))+self.iAnchorPosX
                elif self.iPosX[0]==u'%':
                    fPercentage=float(self.iPosX[1:])
                elif self.iPosX[0]==u'd':
                    self.iPosX=dp(float(self.iPosX[1:]))+self.iAnchorPosX
                elif self.iPosX[0]==u's':
                    self.iPosX=sp(float(self.iPosX[1:]))+self.iAnchorPosX
                else:
                    LogError(uMsg=u'WidgetBase: Fatal Error:Wrong xpos:'+self.uName+ " "+str(self.iPosX))
                    self.iPosX=0

                if not fPercentage==-1.0:
                    self.iPosX=self.iAnchorPosX+((fPercentage/100)*self.iAnchorWidth)-(self.iWidth*(fPercentage/100))

            if self.bHasText:
                self.uhTextAlign        =   GetXMLTextAttribute (oXMLNode,u'htextalign',    False,u'center')
                self.uvTextAlign        =   GetXMLTextAttribute (oXMLNode,u'vtextalign',    False,u'middle')
                self.bBold              =   GetXMLBoolAttribute (oXMLNode,u'bold',          False,False)
                self.bItalic            =   GetXMLBoolAttribute (oXMLNode,u'italic',        False,False)
                self.uFontIndex         =   GetXMLTextAttribute (oXMLNode,u'fontid',        False,oDef.uDefaultFont)
                self.uOrgFontIndex      =   self.uFontIndex

                uFontSize:str           =   GetXMLTextAttribute (oXMLNode,u'fontsize',      False,'0')
                uIconFontSize:str       =   GetXMLTextAttribute (oXMLNode, u'iconfontsize', False, uFontSize)
                self.aTextColor         =   GetColorFromHex(GetXMLTextAttribute (oXMLNode,u'textcolor',False,uColorUndefined))
                self.SetCaption(GetXMLTextAttribute(oXMLNode,u'caption',False,u''))
                self.uOrgSecondCaption  =   GetXMLTextAttribute(oXMLNode,u'secondcaption',False,u'')

                Globals.oTheScreen.oFonts.dUsedFonts[self.uFontIndex]=True

                if self.aTextColor == aColorUndefined:
                    if self.eWidgetType == eWidgetType.Button or self.eWidgetType == eWidgetType.DropDown or self.eWidgetType == eWidgetType.Switch:
                        self.aTextColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('fontcolor button')
                    elif self.eWidgetType == eWidgetType.TextField or self.eWidgetType == eWidgetType.TextInput or self.eWidgetType == eWidgetType.Slider:
                        self.aTextColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('fontcolor text')
                    elif self.eWidgetType == eWidgetType.FileViewer or self.eWidgetType == eWidgetType.Settings:
                        self.aTextColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('fontcolor file')
                    elif self.eWidgetType == eWidgetType.BackGround:
                        self.aTextColor = GetColorFromHex(u'#FFFFFFFF')
                    if self.aTextColor == aColorUndefined:
                        self.aTextColor = GetColorFromHex(u'#FFFFFFFF')

                if uFontSize == "0":
                    if self.eWidgetType == eWidgetType.Button or self.eWidgetType == eWidgetType.DropDown or self.eWidgetType == eWidgetType.Switch:
                        uFontSize = str(oDef.iFontSize_Button)
                    elif self.eWidgetType == eWidgetType.TextField or self.eWidgetType == eWidgetType.TextInput or self.eWidgetType == eWidgetType.Slider:
                        uFontSize = str(oDef.iFontSize_Text)
                    elif self.eWidgetType == eWidgetType.FileViewer or self.eWidgetType == eWidgetType.Settings:
                        uFontSize = str(oDef.iFontSize_File)

                if uIconFontSize == "0":
                    if self.eWidgetType == eWidgetType.Button or self.eWidgetType == eWidgetType.DropDown or self.eWidgetType == eWidgetType.Switch:
                        uIconFontSize = str(oDef.iFontSize_Button)
                    elif self.eWidgetType == eWidgetType.TextField or self.eWidgetType == eWidgetType.TextInput or self.eWidgetType == eWidgetType.Slider:
                        uIconFontSize = str(oDef.iFontSize_Text)
                    elif self.eWidgetType == eWidgetType.FileViewer or self.eWidgetType == eWidgetType.Settings:
                        uIconFontSize = str(oDef.iFontSize_File)


                # todo: check where to scale fonts
                if uFontSize[0] == u'd':
                    self.iFontSize = dp(uFontSize[1:])   *self.fRationX
                elif uFontSize[0] == u's':
                    self.iFontSize = sp(uFontSize[1:])  *self.fRationX
                elif uFontSize.startswith(u'%h'):
                    self.iFontSize = ((int(uFontSize[2:])*self.iHeight)/100) # *self.fRationY
                elif uFontSize.startswith(u'%w'):
                    self.iFontSize = ((int(uFontSize[2:])*self.iWidth)/100) # *self.fRationX
                else:
                    self.iFontSize = ToInt(uFontSize)
                    if self.iFontSize != 0:
                        Logger.warning("Depreciated absolute fontsize used:"+self.uName+ " from:"+self.uPageName)

                if uIconFontSize[0] == u'd':
                    self.iIconFontSize = dp(uIconFontSize[1:])   *self.fRationX
                elif uIconFontSize[0] == u's':
                    self.iIconFontSize = sp(uIconFontSize[1:])  *self.fRationX
                elif uIconFontSize.startswith(u'%h'):
                    self.iIconFontSize = ((int(uIconFontSize[2:])*self.iHeight)/100) # *self.fRationY
                elif uIconFontSize.startswith(u'%w'):
                    self.iIconFontSize = ((int(uIconFontSize[2:])*self.iWidth)/100) # *self.fRationX
                else:
                    self.iIconFontSize = ToInt(uIconFontSize)
                    if self.iIconFontSize != 0:
                        Logger.warning("Depreciated absolute fontsize used:"+self.uName+ " from:"+self.uPageName)

            if not hasattr(self,'bIsDropButton'):
                oLastWidget = self

            self.iPosXInit      = self.iPosX
            self.iPosYInit      = self.iPosY
            self.iWidthInit     = self.iWidth
            self.iHeightInit    = self.iHeight
            self.iFontSizeInit  = self.iFontSize
            return True
        except Exception as e:
            LogError(uMsg=u'Error parsing widget from element:['+self.uName+"",oException=e)
            return False

    def CalculatePosY(self,uPosY:str) -> int:
        fPercentage:float = -1.0
        iPosY:int = 0

        if not uPosY == u'':
            if uPosY == u'bottom':
                fPercentage = 100.0
            elif uPosY.startswith('of:'):
                iPosY = self._ParseDimPosValue(uPosY)
            elif uPosY == u'top':
                fPercentage = 0.0
            elif uPosY == u'middle':
                fPercentage = 50.0
            elif uPosY.isdigit():
                Logger.warning("Depreciated absolute PosY used:" + self.uName + " from:" + self.uPageName)
                iPosY = (int(self.iPosY) + self.iAnchorPosY)
            elif uPosY[0] == u'%':
                fPercentage = float(self.iPosY[1:])
            elif uPosY[0] == u'd':
                # iPosY = dp(float(self.iPosY[1:])) + self.iAnchorPosY
                iPosY = Globals.iAppHeight - self.iHeight - self.iPosY
            elif uPosY[0] == u's':
                # iPosY = sp(float(self.iPosY[1:])) + self.iAnchorPosY
                iPosY = Globals.iAppHeight - self.iHeight - self.iPosY
            else:
                LogError(uMsg=u'WidgetBase: Fatal Error:Wrong ypos:' + self.uName)
                iPosY = 0
            if not fPercentage == -1.0:
                iPosY = int(self.iAnchorPosY + ((fPercentage / 100) * self.iAnchorHeight) - (self.iHeight * (fPercentage / 100)))
            return iPosY

    def CalculateWidth(self,uWidth:str,iAnchorWidth:int) -> Tuple[int,bool]:

        bApplyWidth = False
        iWidth:int = 0

        if uWidth == u'':
            return iAnchorWidth,bApplyWidth
        elif uWidth.startswith('of:height:self'):
            bApplyWidth = True
        elif uWidth.startswith('of:toleft'):
            bApplyWidth = True
        elif uWidth.startswith('of:'):
            iWidth = self._ParseDimPosValue(uWidth)
        elif uWidth[0] == u'%':
            fPercentage: float = float(uWidth[1:])
            iWidth = int((fPercentage / 100) * iAnchorWidth)
        elif uWidth[0] == u'd':
            # we define: First Value is dp value,
            # second value is absolute value (unscaled)
            # eg d20:50 would result either d20 or 50, whatever is larger
            tTmp: Tuple[float, float] = SplitMax(uWidth[1:])
            if tTmp[1] == 0:
                fVar = dp(tTmp[0])
            else:
                fVar = max(dp(tTmp[0]), tTmp[1])
            iWidth = int(fVar)
        else:
            # Logger.warning("Depreciated absolute width used:"+self.uName+ " from:"+self.uPageName+":["+uWidth+"]")
            iWidth = int(uWidth)
        return iWidth, bApplyWidth

    def CalculateHeight(self,uHeight:str,iAnchorHeight:int) -> int:
        fPercentage:float
        if uHeight == u'':
            return iAnchorHeight
        elif uHeight[0] == u'%':
            fPercentage = float(uHeight[1:])
            return int((fPercentage / 100) * iAnchorHeight)
        elif uHeight.startswith('of:'):
            return int(self._ParseDimPosValue(uHeight))
        elif uHeight[0] == u'd':
            # we define: First Value is dp value,
            # second value is absolute value (unscaled)
            tTmp: Tuple[float, float] = SplitMax(uHeight[1:])
            if tTmp[1] == 0:
                fVar = dp(tTmp[0])
            else:
                fVar = max(dp(tTmp[0]), tTmp[1])

            return int(fVar)
        else:
            Logger.warning("Depreciated absolute height used:"+self.uName+ " from:"+self.uPageName)
            return int(uHeight)

    def _ParseDimPosValue(self,uValue:str) -> int:
        tSplit:List[str]=uValue.split(":")
        fRetVal:float=0

        'of:width:[last/self/widgetname:calc]'
        'of:height:[last/self/widgetname:calc]'

        'of:bottom:[last/self/widgetname:calc]'
        'of:top:[last/self/widgetname:calc]'
        'of:left:[last/self/widgetname:calc]'
        'of:right:[last/self/widgetname:calc]'
        'of:totop:[last/self/widgetname:calc]'
        'of:tobottom:[last/self/widgetname:calc]'
        'of:toleft:[last/self/widgetname:calc]'

        global oLastWidget

        if len(tSplit)>2:
            uDim    = tSplit[1]
            tFrom   = tSplit[2]
            if tFrom == 'last':
                tFrom = oLastWidget
            elif tFrom == 'self':
                tFrom = self
            else:
                aFrom = Globals.oTheScreen.FindWidgets(self.oParentScreenPage.uPageName,tSplit[2])
                if len(aFrom)>0:
                    tFrom=aFrom[0]
                else:
                    tFrom=None

            if tFrom is not None:
                if uDim == 'top':
                    fRetVal = tFrom.iPosY
                elif uDim == 'left':
                    fRetVal = tFrom.iPosX
                elif uDim == 'bottom':
                    fRetVal = tFrom.iPosY+tFrom.iHeight
                elif uDim == 'right':
                    fRetVal = tFrom.iPosX+tFrom.iWidth
                elif uDim == 'width':
                    fRetVal = tFrom.iWidth
                elif uDim == 'height':
                    fRetVal = tFrom.iHeight
                elif uDim =='totop':
                    fRetVal = tFrom.iPosY-self.iHeight
                elif uDim =='tobottom':
                    fRetVal = tFrom.iPosY+tFrom.iHeight-self.iHeight
                elif uDim =='toleft':
                    fRetVal = tFrom.iPosX -self.iWidth
                elif uDim =='toright':
                    fRetVal = tFrom.iPosX+tFrom.iWidth -self.iWidth

                else:
                    LogError(uMsg=u'Unknown Reference:'+uDim)
            else:
                LogError(uMsg=u'Unknown Widget:'+self.oParentScreenPage+":"+tSplit[2])

        if len(tSplit) > 3:
            uOperator = tSplit[3]
            if len(uOperator) > 1:
                if uOperator[0] == '*':
                    fRetVal = fRetVal*float(uOperator[1:])
                elif uOperator[0] == '/':
                    fRetVal = fRetVal/float(uOperator[1:])

                else:
                    LogError(uMsg=u'Unknown Operator:'+uOperator)
        return ToInt(fRetVal)

    def CreateBase(self,Parent:Widget,Class:Union[Callable,str]) -> bool:

        try:

            self.oParent        = Parent
            self.iPosX          = int(self.iPosXInit/self.oDef.fRationX)
            self.iPosY          = int(self.iPosYInit/self.oDef.fRationY)
            self.iWidth         = int(self.iWidthInit/self.oDef.fRationX)
            self.iHeight        = int(self.iHeightInit/self.oDef.fRationY)

            self.CalcFontSize()

            iKivyPosX:int = self.iPosX+self.iGapX
            # iKivyPosY:int = Globals.iAppHeight-self.iHeight-self.iPosY-self.iGapY
            iKivyPosY:int = Parent.height -self.iHeight-self.iPosY-self.iGapY

            self.AddArg('pos',(iKivyPosX,iKivyPosY ))
            self.AddArg('size',(self.iWidth,self.iHeight))
            if not self.aBackGroundColor==[0.0,0.0,0.0,0.0]:
                self.AddArg('background_color',self.aBackGroundColor)
            if not self.bEnabled:
                self.AddArg('opacity',0)

            if self.bHasText:
                self.AddArg('halign',               self.uhTextAlign)
                self.AddArg('valign',               self.uvTextAlign)
                self.AddArg('italic',               self.bItalic)
                self.AddArg('bold',                 self.bBold)
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


            if not Class=='':
                if Class.__name__.startswith("c"):
                    # Just add to ORCA classes, passing custom parameter to Kivy classes crashes on Python 3
                    self.dKwArgs['ORCAWIDGET']=self
                self.oObject = Class(**self.dKwArgs)
                self.oObject.oOrcaWidget = self
                self.FlipBorder()

            return True
        except Exception as e:
            LogError(uMsg=u'Can''t create widget:'+self.uName,oException=e)
            return False

    def FlipBorder(self) -> None:
        if self.oObject is not None:
            if Globals.bShowBorders:
                if self.oBorder is None:
                    if (not isinstance(self.oObject, Layout)) and (not self.eWidgetType == eWidgetType.FileViewer):
                        self.oBorder = cBorder(**self.dKwArgs)
                        self.oObject.add_widget(self.oBorder)
            else:
                if self.oBorder is not None:
                    self.oObject.remove_widget(self.oBorder)
                    self.oBorder = None

    def CalcFontSize(self) -> None:
        if self.bIcon:
            self.iFontSize = int(self.iIconFontSize * self.fScale) / self.oDef.fRationX
        else:
            self.iFontSize = self.iFontSizeInit / self.oDef.fRationX

    def GetWidgetTypeFromXmlNode(self,oXMLNode:Element) -> None:
        self.uTypeString = GetXMLTextAttribute (oXMLNode,u'type',True,u'')
        self.eWidgetType = dWidgetTypeToId.get(self.uTypeString,eWidgetType.ERROR)
        if not CheckCondition(oPar=oXMLNode):
            self.eWidgetType = eWidgetType.SkipWidget

    def EnableWidget(self, bEnable:bool) -> bool:
        if bEnable:
            if self.oObject:
                self.oObject.opacity = self.fOrgOpacity
        else:
            if self.oObject:
                if self.oObject.opacity > 0:
                    self.fOrgOpacity = self.oObject.opacity
                    self.oObject.opacity = 0.0
        self.bEnabled = bEnable

        return True

    def UpdateWidget(self) -> bool:
        self.FlipBorder()
        return self.SetCaption(self.uOrgCaption)

    def UpdateWidgetSecondCaption(self) -> bool:
        return self.SetSecondCaption()

    def SetFocus(self) -> bool:
        if self.oObject:
            self.oObject.focus = True
        return True

    def SetTransparancy(self,fTransparancy:float) -> bool:
        if self.oObject:
            self.oObject.opacity = fTransparancy/100
        else:
            return False
        self.fOrgOpacity = fTransparancy
        return True

    def SetWidgetColor(self,sBackgroundColor:str) -> None:
        sColor = ReplaceVars(sBackgroundColor)
        self.uBackGroundColor = sColor
        self.aBackGroundColor = GetColorFromHex(sColor)
        if self.oObject:
            self.oObject.background_color = self.aBackGroundColor

    def SetCaption(self,uCaption:str) -> bool:

        if self.uOrgCaption == u'' and uCaption!=u'':
            self.uOrgCaption = uCaption

        if not u'$var(' in self.uOrgCaption:
            if not u'$lvar(' in self.uOrgCaption:
                if not self.uOrgCaption.startswith("icon:"):
                    if not ":::" in self.uOrgCaption and self.eWidgetType==eWidgetType.DropDown:
                        self.uOrgCaption = uCaption

        uTmp=ReplaceVars(uCaption)
        if uTmp.startswith(u'$var(') or uTmp.startswith(u'$lvar('):
            self.uCaption = u''
        else:
            self.uCaption = uTmp

        self.bIcon = False
        self.uFontIndex = self.uOrgFontIndex

        if self.uCaption.startswith("icon:"):
            self.HandleIcon()

        if self.oObject:
            self.CalcFontSize()
            self.oObject.font_name = self.uFontIndex
            self.oObject.text      = self.uCaption
            self.oObject.font_size = self.iFontSize
        return True

    def SetSecondCaption(self) -> bool:

        uTmp:str = ReplaceVars(self.uOrgSecondCaption)
        if uTmp.startswith(u'$var(') or uTmp.startswith(u'$lvar('):
            self.uSecondCaption = u''
        else:
            self.uSecondCaption = uTmp

        if self.uSecondCaption==u'':
            return True

        self.bIcon = False
        self.uCaption = self.uSecondCaption
        self.uFontIndex = self.uOrgFontIndex

        if self.uSecondCaption.startswith("icon:"):
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
            oWidget.uCaption = dIcon["char"]
            if dIcon["fontname"]:
                oWidget.uFontIndex = dIcon["fontname"]
                self.bIcon = True
            oWidget.fScale = dIcon["scale"]

    def AddArg(self,uKey:str,oValue:Any) -> None:
        self.dKwArgs[uKey] = oValue

    def SetWidgetFontStyle(self,bBold:Union[bool,None],bItalic:Union[bool,None],uColor:Union[str,None]) -> bool:
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
        uRet:str = "error"
        try:
            if uType=="bold":
                uRet="0"
                if self.bBold:
                    uRet="1"
            elif uType=="italic":
                uRet="0"
                if self.bItalic:
                    uRet="1"
            elif uType=="textcolor":
                uRet=GetHexFromColor(self.aTextColor)
        except Exception:
            pass
        return uRet


    def On_Button_Up(self,instance:Widget) -> None:

        if self.bEnabled:
            if hasattr(instance,'uTapType'):
                self.uTapType = instance.uTapType
            else:
                self.uTapType = u"up"

            Logger.debug (u'WidgetBase:On_Button_Up: Tap detected: %s:%s' %( self.uName, self.uTapType))

            self.OnButtonClicked()
            return

    def On_Button_Down(self,instance:Widget) -> None:

        if self.bEnabled:
            Globals.oSound.PlaySound(u'click')
            OS_Vibrate()

            if hasattr(instance,'uTapType'):
                self.uTapType = instance.uTapType
            else:
                self.uTapType = u"down"
            Logger.debug (u'WidgetBase:On_Button_Down: Tap detected: %s:%s' %( self.uName, self.uTapType))

            self.OnButtonClicked()
            return

    def OnButtonClicked(self) -> None:

        if Globals.oTheScreen.GuiIsBlocked():
            return

        uActionName:str          = ReplaceVars(self.uActionName)
        uActionNameDoubleTap:str = ReplaceVars(self.uActionNameDoubleTap)
        uActionNameUp:str        = ReplaceVars(self.uActionNameUpOnly)
        uActionNameDown:str      = ReplaceVars(self.uActionNameDownOnly)
        uActionNameLongTap:str   = ReplaceVars(self.uActionNameLongTap)
        aUseActionName:List[str] = []

        if uActionNameDoubleTap != u'' and self.uTapType == u'double_up':
            aUseActionName.append(uActionNameDoubleTap)
        elif uActionNameLongTap != u'' and self.uTapType == u'long_up':
            aUseActionName.append(uActionNameLongTap)
        elif uActionNameDown    != u'' and self.uTapType == u"down":
            aUseActionName.append(uActionNameDown)
        elif uActionNameUp      != u'' and self.uTapType == u"up":
            aUseActionName.append(uActionNameUp)
        elif uActionName!=u'' and  self.uTapType== u'repeat_down' and uActionNameLongTap == u'':
            aUseActionName.append(uActionName)
        elif uActionName!=u'' and self.uTapType== u"up":
            aUseActionName.append(uActionName)

        # this a response optimisation, If we do have just one standard action
        # the we convert it to a down only action

        if self.eWidgetType == eWidgetType.Button or self.eWidgetType == eWidgetType.Picture:
            if self.uTapType == u"down":
                if self.uActionName != u"":
                    if self.uActionNameDoubleTap == u"":
                        if self.uActionNameLongTap == u"":
                            if self.uActionNameDownOnly == u"":
                                if self.uActionNameUpOnly == u"":
                                    aUseActionName.append(uActionName)

            if self.uTapType == u"up":
                if self.uActionName != u"":
                    if self.uActionNameDoubleTap == u"":
                        if self.uActionNameLongTap == u"":
                            if self.uActionNameDownOnly == u"":
                                if self.uActionNameUpOnly == u"":
                                    return

        # if we have a doubletap but no doubletap action, then execute two single taps
        if len(aUseActionName) == 0 and self.uTapType == u'double_up':
            aUseActionName.append(uActionName)
            aUseActionName.append(uActionName)

        aActions:List[cAction]=[]
        for uUseActionName in aUseActionName:
            aActionsTest:List[cAction] = Globals.oActions.GetActionList(uActionName = uUseActionName, bNoCopy = True)
            if aActionsTest:
                Globals.oEvents.AddToSimpleActionList(aActions,[{'string':'call'}])
                aActions[-1].dActionPars=self.dActionPars
                aActions[-1].dActionPars['actionname']=uUseActionName
                Logger.debug (u'WidgetBase: [%s] Action queued for Object [%s] [%s]' % (self.uTapType,self.uName,uUseActionName))
            else:
                Globals.oEvents.AddToSimpleActionList(aActions,[{'string':uUseActionName}])
                aActions[-1].dActionPars=self.dActionPars
        if len(aActions)>0:
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=self)
        return

    def On_Gesture(self,instance:Widget) -> None:

        if Globals.oTheScreen.GuiIsBlocked():
            return

        if self.bEnabled:
            if hasattr(instance,'aActions'):
                self.aWidgetActions=instance.aActions
                if self.aWidgetActions is not None:
                    Globals.oEvents.ExecuteActions( aActions=self.aWidgetActions,oParentWidget=self)

    # noinspection PyMethodMayBeStatic
    def SaveLastWidgetPos(self) -> None:
        global oLastWidget,oLastWidgetSave
        oLastWidgetSave=oLastWidget

    # noinspection PyMethodMayBeStatic
    def RestoreLastWidgetPos(self) -> None:
        global oLastWidget,oLastWidgetSave
        oLastWidget=oLastWidgetSave

    def Create(self,oParent:Widget) -> bool:
        """ Dummy, needs to be overridden and not called """
        Logger.error(u'WidgetBase: Create called on base, not allowed [%s]' % self.uName)
        return False

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Dummy, needs to be overridden and not called """
        Logger.error(u'WidgetBase: Create called on base, not allowed [%s]' % self.uName)
        return False

