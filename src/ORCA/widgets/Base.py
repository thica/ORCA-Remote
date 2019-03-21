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


from kivy.logger                       import Logger
from kivy.utils                        import get_color_from_hex
from kivy.graphics                     import Color
from kivy.metrics                      import dp,sp
from kivy.uix.layout                   import Layout
from kivy.uix.settings                 import Settings


from kivy.compat                       import PY2

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

import ORCA.Globals as Globals

__all__ = ['cWidgetBase','GetColorFromHex','GetHexFromColor','oWidgetType']

oLastWidget=None
oLastWidgetSave=None

class cWidgetType (object):
    """
    Helper Class to enumerate through widget names
    """
    def __init__(self):
        self.WidgetTypeToId = {}

        Elements = ["NoWidget"       ,
                    "BackGround"     ,
                    "TextField"      ,
                    "Button"         ,
                    "Picture"        ,
                    "Anchor"         ,
                    "TextInput"      ,
                    "Knob"           ,
                    "FileViewer"     ,
                    "Slider"         ,
                    "Rectangle"      ,
                    "Circle"         ,
                    "Video"          ,
                    "DropDown"       ,
                    "ColorPicker"    ,
                    "Settings"       ,
                    "Switch"         ,
                    "SkipWidget"     ,
                    "FileBrowser"    ,
                    "xITach2Keene"
                   ]

        for iValue, uName in enumerate(Elements):
            setattr(self,uName,iValue)
            self.WidgetTypeToId[uName.upper()] = iValue

def GetColorFromHex(uColor):
    """
    Helper function to get a rgba tuple from a hex string
    :rtype: tuple
    :param string uColor: HEX representation of a color eg:#00FF0040
    :return: A tuple in the format (r,g,b,a), wher all values are floats between 0 and 1, (return 0,1,0,1 in case of an error)
    """

    try:
        return get_color_from_hex(ReplaceVars(uColor.lower()))
    except Exception as e:
        return Color(0, 1, 0, 1)

def GetHexFromColor(aColor):
    try:
        return ''.join('{:02x}'.format(x*255) for x in aColor)
    except Exception as e:
        return "00000000"


class cWidgetBase(object):
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

    def __init__(self,**kwargs):

        self.bHasText=kwargs.get('hastext')
        if self.bHasText is None:
            self.bHasText=False

        self.aKwArgs             = {}
        self.bBold               = False
        self.bEnabled            = True
        self.bItalic             = False
        self.bIcon               = False
        self.bNoTextSize         = False
        self.dActionPars         = {} # Actionpars will be passed to Actions within command set, existing pars will be replaced!
        self.fOrgOpacity         = 1.0
        self.fScale              = 1.0
        self.fRationX            = 1.0
        self.fRationY            = 1.0
        self.iAnchorHeight       = 0
        self.iAnchorPosX         = 0
        self.iAnchorPosY         = 0
        self.iAnchorWidth        = 0
        self.iFontSize           = 30
        self.iIconFontSize       = 50
        self.iFontSizeInit       = 30
        self.iHeight             = 10
        self.iHeightInit         = 10
        self.iPosX               = 0
        self.iPosXInit           = 0
        self.iPosY               = 0
        self.iPosYInit           = 0
        self.iWidgetType         = oWidgetType.NoWidget
        self.iWidth              = 10
        self.iWidthInit          = 10
        self.oObject             = None         # oOBject is the kivy Widget
        self.oParent             = None
        self.oParentScreenPage   = None
        self.oTmpAnchor          = None
        self.tBackGroundColor    = ()
        self.tTextColor          = GetColorFromHex('#FFFFFFFF')
        self.uActionName         = u''
        self.uActionNameDoubleTap= u''
        self.uActionNameDownOnly = u''
        self.uActionNameLongTap  = u''
        self.uActionNameUpOnly   = u''
        self.uAnchorName         = u''
        self.uBackGroundColor    = u''
        self.uCaption            = u''
        self.uConfigName         = u''
        self.uDefinitionContext  = u''
        self.uFontIndex          = u'Sans'
        self.uhTextAlign         = u'center'
        self.uInterFace          = u''
        self.uTypeString         = u''
        self.uName               = u'noname'
        self.uOrgCaption         = u''
        self.uOrgSecondCaption   = u''
        self.uOrgFontIndex       = self.uFontIndex
        self.uPageName           = 0
        self.uSecondCaption      = u''
        self.uTapType            = u''
        self.uvTextAlign         = u'top'

    def ParseXMLBaseNode (self,oXMLNode,oParentScreenPage, uAnchor):

        try:

            global oLastWidget

            self.GetWidgetTypeFromXmlNode(oXMLNode)

            uDefinitionContext = GetXMLTextAttribute  (oXMLNode,u'definitioncontext',  False, Globals.uDefinitionContext)
            uAlias = oXMLNode.get('definitionalias')
            oDef = None
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
                self.oTmpAnchor=self.oParentScreenPage.dWidgets.get(self.uAnchorName)
                if self.oTmpAnchor is not None:
                    # oTmpAnchor is already aligned to screen size
                    self.iAnchorPosX         = self.oTmpAnchor.iPosX
                    self.iAnchorPosY         = self.oTmpAnchor.iPosY
                    self.iAnchorWidth        = self.oTmpAnchor.iWidth
                    self.iAnchorHeight       = self.oTmpAnchor.iHeight

            # We parse for Text and change later to integer
            self.iWidth = ReplaceVars(GetXMLTextAttribute(oXMLNode, u'width', False, u''))
            self.iHeight = ReplaceVars(GetXMLTextAttribute(oXMLNode, u'height', False, u''))

            iAnchorWidth        = (self.iAnchorWidth)
            iAnchorHeight       = (self.iAnchorHeight)

            bApplyWidth=False

            if self.iWidth==u'':
                self.iWidth=iAnchorWidth
            elif self.iWidth.startswith('of:height:self'):
                bApplyWidth=True
            elif self.iWidth.startswith('of:toleft'):
                bApplyWidth=True
            elif self.iWidth.startswith('of:'):
                self.iWidth=self._ParseDimPosValue(self.iWidth)
            elif self.iWidth[0]==u'%':
                fPercentage=float(self.iWidth[1:])
                self.iWidth=((fPercentage/100)*iAnchorWidth)
            elif self.iWidth[0]==u'd':
                # we define: First Value is dp value,
                # second value is absolute value (unscaled)
                # eg d20:50 would result either d20 or 50, whatever is larger
                tTmp=SplitMax(self.iWidth[1:])
                if tTmp[1]==0:
                    uVar=dp(tTmp[0])
                else:
                    uVar=max(dp(tTmp[0]),tTmp[1])

                self.iWidth=uVar
            else:
                #Logger.warning("Depriciated absolute width used:"+self.uName+ " from:"+self.uPageName)
                self.iWidth=int(self.iWidth)

            if self.iHeight==u'':
                self.iHeight=iAnchorHeight
            elif self.iHeight[0]==u'%':
                fPercentage=float(self.iHeight[1:])
                self.iHeight=((fPercentage/100)*iAnchorHeight)
            elif self.iHeight.startswith('of:'):
                if not bApplyWidth:
                    self.iHeight=self._ParseDimPosValue(self.iHeight)
                else:
                    self.iHeight=self._ParseDimPosValue(self.iHeight)
            elif self.iHeight[0]==u'd':
                # we define: First Value is dp value,
                # second value is absolute value (unscaled)
                tTmp=SplitMax(self.iHeight[1:])
                if tTmp[1]==0:
                    uVar=dp(tTmp[0])
                else:
                    uVar=max(dp(tTmp[0]),tTmp[1])

                self.iHeight=uVar
            else:
                #Logger.warning("Depriciated absolute height used:"+self.uName+ " from:"+self.uPageName)
                self.iHeight=int(self.iHeight)

            if bApplyWidth:
                self.iWidth=self._ParseDimPosValue(self.iWidth)

            #We parse for Text and change later to integer
            self.iPosX                = ReplaceVars(GetXMLTextAttribute  (oXMLNode,u'posx',   False, u'left'))
            self.iPosY                = ReplaceVars(GetXMLTextAttribute  (oXMLNode,u'posy',   False, u'top'))
            self.bEnabled             = GetXMLBoolAttribute (oXMLNode,u'enabled', False,True)
            self.uCaption             = u''
            self.uBackGroundColor     = GetXMLTextAttribute(oXMLNode,u'backgroundcolor',False,u'#00000000')
            self.tBackGroundColor     = GetColorFromHex(ReplaceVars(self.uBackGroundColor))
            self.uActionName          = GetXMLTextAttribute(oXMLNode,u'action',False,u'')
            self.uActionNameDoubleTap = GetXMLTextAttribute(oXMLNode,u'actiondoubletap',False,u'')
            self.uActionNameLongTap   = GetXMLTextAttribute(oXMLNode,u'actionlongtap',False,u'')
            self.uActionNameDownOnly  = GetXMLTextAttribute(oXMLNode,u'actiondownonly',False,u'')
            self.uActionNameUpOnly    = GetXMLTextAttribute(oXMLNode,u'actionuponly',False,u'')
            self.uInterFace           = GetXMLTextAttribute(oXMLNode,u'interface',False,u'')
            self.uConfigName          = GetXMLTextAttribute(oXMLNode,u'configname',False,u'')
            uActionPars               = GetXMLTextAttribute(oXMLNode,u'actionpars',False,u'{}')
            if uActionPars.startswith("$var("):
                uActionPars=ReplaceVars(uActionPars)

            self.dActionPars=ToDic(uActionPars)

            if self.uActionName.startswith("SendCommand "):
                if len(self.dActionPars)==0:
                    self.dActionPars={"commandname":self.uActionName[12:]}
                    self.uActionName="Send"

            if not self.uInterFace==u'':
                Globals.oInterFaces.dUsedInterfaces[self.uInterFace]=True

            fPercentage=-1.0
            if not self.iPosY==u'':
                if self.iPosY==u'bottom':
                    fPercentage=100.0
                elif self.iPosY.startswith('of:'):
                    self.iPosY=self._ParseDimPosValue(self.iPosY)
                elif self.iPosY==u'top':
                    fPercentage=0.0
                elif self.iPosY==u'middle':
                    fPercentage=50.0
                elif self.iPosY.isdigit():
                    Logger.warning("Depriciated absolute PosY used:"+self.uName+ " from:"+self.uPageName)
                    self.iPosY=(int(self.iPosY)+self.iAnchorPosY)
                elif self.iPosY[0]==u'%':
                    fPercentage=float(self.iPosY[1:])
                elif self.iPosY[0]==u'd':
                    self.iPosY=dp(float(self.iPosY[1:]))+self.iAnchorPosY
                    self.iPosY=Globals.iAppHeight-self.iHeight-self.iPosY
                elif self.iPosY[0]==u's':
                    self.iPosY=sp(float(self.iPosY[1:]))+self.iAnchorPosY
                    self.iPosY=Globals.iAppHeight-self.iHeight-self.iPosY
                else:
                    LogError(u'WidgetBase: Fatal Error:Wrong ypos:'+self.uName)
                    self.iPosY=0
                if not fPercentage==-1.0:
                    self.iPosY=self.iAnchorPosY+((fPercentage/100)*self.iAnchorHeight)-(self.iHeight*(fPercentage/100))

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
                    Logger.warning("Depriciated absolute PosX used:"+self.uName+ " from:"+self.uPageName)
                    self.iPosX=(int(self.iPosX))+self.iAnchorPosX
                elif self.iPosX[0]==u'%':
                    fPercentage=float(self.iPosX[1:])
                elif self.iPosX[0]==u'd':
                    self.iPosX=dp(float(self.iPosX[1:]))+self.iAnchorPosX
                elif self.iPosX[0]==u's':
                    self.iPosX=sp(float(self.iPosX[1:]))+self.iAnchorPosX
                else:
                    LogError(u'WidgetBase: Fatal Error:Wrong xpos:'+self.uName+ " "+str(self.iPosX))
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

                sFontSize               =   GetXMLTextAttribute (oXMLNode,u'fontsize',      False,'0')
                sIconFontSize           =   GetXMLTextAttribute (oXMLNode, u'iconfontsize', False, sFontSize)
                self.tTextColor         =   GetXMLTextAttribute (oXMLNode,u'textcolor',     False,u'')
                self.SetCaption(GetXMLTextAttribute(oXMLNode,u'caption',False,u''))
                self.uOrgSecondCaption  =   GetXMLTextAttribute(oXMLNode,u'secondcaption',False,u'')

                Globals.oTheScreen.oFonts.dUsedFonts[self.uFontIndex]=True

                if self.tTextColor == u'':
                    if self.iWidgetType == oWidgetType.Button or self.iWidgetType == oWidgetType.DropDown or self.iWidgetType == oWidgetType.Switch:
                        self.tTextColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('fontcolor button')
                    elif self.iWidgetType == oWidgetType.TextField or self.iWidgetType == oWidgetType.TextInput or self.iWidgetType == oWidgetType.Slider:
                        self.tTextColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('fontcolor text')
                    elif self.iWidgetType == oWidgetType.FileViewer or self.iWidgetType == oWidgetType.Settings:
                        self.tTextColor = Globals.oTheScreen.oSkin.dSkinAttributes.get('fontcolor file')
                    elif self.iWidgetType == oWidgetType.BackGround:
                        self.tTextColor = GetColorFromHex(u'#FFFFFFFF')
                    if self.tTextColor is None or self.tTextColor == u'':
                        self.tTextColor = GetColorFromHex(u'#FFFFFFFF')
                else:
                    self.tTextColor = GetColorFromHex(self.tTextColor)

                if sFontSize == "0":
                    if self.iWidgetType == oWidgetType.Button or self.iWidgetType == oWidgetType.DropDown or self.iWidgetType == oWidgetType.Switch:
                        sFontSize = str(oDef.iFontSize_Button)
                    elif self.iWidgetType == oWidgetType.TextField or self.iWidgetType == oWidgetType.TextInput or self.iWidgetType == oWidgetType.Slider:
                        sFontSize = str(oDef.iFontSize_Text)
                    elif self.iWidgetType == oWidgetType.FileViewer or self.iWidgetType == oWidgetType.Settings:
                        sFontSize = str(oDef.iFontSize_File)

                if sIconFontSize == "0":
                    if self.iWidgetType == oWidgetType.Button or self.iWidgetType == oWidgetType.DropDown or self.iWidgetType == oWidgetType.Switch:
                        sIconFontSize = str(oDef.iFontSize_Button)
                    elif self.iWidgetType == oWidgetType.TextField or self.iWidgetType == oWidgetType.TextInput or self.iWidgetType == oWidgetType.Slider:
                        sIconFontSize = str(oDef.iFontSize_Text)
                    elif self.iWidgetType == oWidgetType.FileViewer or self.iWidgetType == oWidgetType.Settings:
                        sIconFontSize = str(oDef.iFontSize_File)


                # todo: check where to scale fonts
                if sFontSize[0] == u'd':
                    self.iFontSize = dp(sFontSize[1:])   *self.fRationX
                elif sFontSize[0] == u's':
                    self.iFontSize = sp(sFontSize[1:])  *self.fRationX
                elif sFontSize.startswith(u'%h'):
                    self.iFontSize = ((int(sFontSize[2:])*self.iHeight)/100) # *self.fRationY
                elif sFontSize.startswith(u'%w'):
                    self.iFontSize = ((int(sFontSize[2:])*self.iWidth)/100) # *self.fRationX
                else:
                    self.iFontSize = ToInt(sFontSize)
                    if self.iFontSize != 0:
                        Logger.warning("Depriciated absolute fontsize used:"+self.uName+ " from:"+self.uPageName)

                if sIconFontSize[0] == u'd':
                    self.iIconFontSize = dp(sIconFontSize[1:])   *self.fRationX
                elif sIconFontSize[0] == u's':
                    self.iIconFontSize = sp(sIconFontSize[1:])  *self.fRationX
                elif sIconFontSize.startswith(u'%h'):
                    self.iIconFontSize = ((int(sIconFontSize[2:])*self.iHeight)/100) # *self.fRationY
                elif sIconFontSize.startswith(u'%w'):
                    self.iIconFontSize = ((int(sIconFontSize[2:])*self.iWidth)/100) # *self.fRationX
                else:
                    self.iIconFontSize = ToInt(sIconFontSize)
                    if self.iIconFontSize != 0:
                        Logger.warning("Depriciated absolute fontsize used:"+self.uName+ " from:"+self.uPageName)

            if not hasattr(self,'bIsDropButton'):
                oLastWidget = self

            self.iPosXInit      = self.iPosX
            self.iPosYInit      = self.iPosY
            self.iWidthInit     = self.iWidth
            self.iHeightInit    = self.iHeight
            self.iFontSizeInit  = self.iFontSize
            return True
        except Exception as e:
            LogError(u'Error parsing widget from element:['+self.uName+"",e)
            return False

    def _ParseDimPosValue(self,uValue):
        tSplit=uValue.split(":")
        fRetVal=0

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
            oWidget = oLastWidget
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
                    LogError(u'Unknown Reference:'+uDim)
            else:
                LogError(u'Unknown Widget:'+self.oParentScreenPage+":"+tSplit[2])

        if len(tSplit) > 3:
            uOperator = tSplit[3]
            if len(uOperator) > 1:
                if uOperator[0] == '*':
                    fRetVal = fRetVal*float(uOperator[1:])
                elif uOperator[0] == '/':
                    fRetVal = fRetVal/float(uOperator[1:])

                else:
                    LogError(u'Unknown Operator:'+uOperator)
        return fRetVal

    def CreateBase(self,Parent,Class):

        try:
            self.oParent        = Parent
            self.iPosX          = self.iPosXInit/self.oDef.fRationX
            self.iPosY          = self.iPosYInit/self.oDef.fRationY
            self.iWidth         = self.iWidthInit/self.oDef.fRationX
            self.iHeight        = self.iHeightInit/self.oDef.fRationY

            self.CalcFontSize()

            if self.iWidgetType==oWidgetType.BackGround:
                self.iGapX   = 0
                self.iGapY   = 0
                self.iHeight = Globals.iAppHeight
                self.iWidth  = Globals.iAppWidth

            iKivyPosX = self.iPosX+self.iGapX
            iKivyPosY = Globals.iAppHeight-self.iHeight-self.iPosY-self.iGapY

            self.AddArg('pos',(iKivyPosX,iKivyPosY ))
            self.AddArg('size',(self.iWidth,self.iHeight))
            if not self.tBackGroundColor==[0.0,0.0,0.0,0.0]:
                self.AddArg('background_color',self.tBackGroundColor)
            if not self.bEnabled:
                self.AddArg('opacity',0)

            if self.bHasText:
                self.AddArg('halign',               self.uhTextAlign)
                self.AddArg('valign',               self.uvTextAlign)
                self.AddArg('italic',               self.bItalic)
                self.AddArg('bold',                 self.bBold)
                if not self.bNoTextSize:
                    self.AddArg('text_size',        (self.iWidth,self.iHeight))
                self.AddArg('color',                self.tTextColor)
                self.AddArg('foreground_color',     self.tTextColor)
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
                    Globals.oTheScreen.oFonts.dUsedFonts[self.uFontIndex]=oFont

            if not Class=='':
                if Class.__name__.startswith("c"):
                    # Just add to ORCA classes, passing custom parameter to Kivy classes crashes on Python 3
                    self.aKwArgs['ORCAWIDGET']=self

                self.oObject = Class(**self.aKwArgs)
                self.oObject.oOrcaWidget = self
                if Globals.oParameter.bShowBorders:
                    if (not isinstance(self.oObject, Layout)) and (not self.iWidgetType == oWidgetType.Knob) and (not self.iWidgetType == oWidgetType.FileViewer):
                        self.oBorder = cBorder(**self.aKwArgs)
                        self.oObject.add_widget(self.oBorder)

            return True
        except Exception as e:
            LogError(u'Can''t create widget:'+self.uName,e)
            return False

    def CalcFontSize(self):
        if self.bIcon:
            self.iFontSize = int(self.iIconFontSize * self.fScale) / self.oDef.fRationX
        else:
            self.iFontSize = self.iFontSizeInit / self.oDef.fRationX

    def GetWidgetTypeFromXmlNode(self,oXMLNode):
        self.uTypeString = GetXMLTextAttribute (oXMLNode,u'type',True,u'')
        self.iWidgetType = oWidgetType.WidgetTypeToId.get(self.uTypeString,-1)
        if not CheckCondition(oXMLNode):
            self.iWidgetType = oWidgetType.SkipWidget

    def EnableWidget(self, bEnable):
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

    def UpdateWidget(self):
        return self.SetCaption(self.uOrgCaption)

    def UpdateWidgetSecondCaption(self):
        return self.SetSecondCaption()

    def SetFocus(self):
        if self.oObject:
            self.oObject.focus = True
        return True

    def SetTransparancy(self,fTransparancy):
        if self.oObject:
            self.oObject.opacity = fTransparancy/100
        self.fOrgOpacity = fTransparancy

    def SetWidgetColor(self,sBackgroundColor):
        sColor = ReplaceVars(sBackgroundColor)
        self.uBackGroundColor = sColor
        self.tBackGroundColor = GetColorFromHex(sColor)
        if self.oObject:
            self.oObject.background_color = self.tBackGroundColor

    def SetCaption(self,uCaption):

        if self.uOrgCaption == u'' and uCaption!=u'':
            self.uOrgCaption = uCaption

        if not u'$var(' in self.uOrgCaption:
            if not u'$lvar(' in self.uOrgCaption:
                if not self.uOrgCaption.startswith("icon:"):
                    if not ":::" in self.uOrgCaption and self.iWidgetType==oWidgetType.DropDown:
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

    def SetSecondCaption(self):

        uTmp=ReplaceVars(self.uOrgSecondCaption)
        if uTmp.startswith(u'$var(') or uTmp.startswith(u'$lvar('):
            self.uSecondCaption = u''
        else:
            self.uSecondCaption = uTmp

        if self.uSecondCaption==u'':
            return

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

    def HandleIcon(self, oWidget = None):

        if oWidget is None:
            oWidget = self

        uColor = ''
        uIcon  = oWidget.uCaption[5:]
        iPos   = uIcon.find(' color:')
        if iPos > 0:
            uColor = uIcon[iPos + 7:]
            uIcon = uIcon[:iPos]
            oWidget.tTextColor = uColor

        dIcon = Globals.dIcons.get(uIcon)
        if dIcon:
            oWidget.uCaption = dIcon["char"]
            if dIcon["fontname"]:
                oWidget.uFontIndex = dIcon["fontname"]
                self.bIcon = True
            oWidget.fScale = dIcon["scale"]

    def AddArg(self,sKey,oValue):
        self.aKwArgs[sKey] = oValue

    def SetWidgetFontStyle(self,bBold,bItalic,sColor):
        if bBold is not None:
            self.bBold = bBold
            if self.oObject:
                self.oObject.bold = self.bBold
        if bItalic is not None:
            self.bItalic = bItalic
            if self.oObject:
                self.oObject.italic = self.bItalic
        if sColor is not None:
            self.tTextColor = GetColorFromHex(sColor)
            if self.oObject:
                self.oObject.color = self.tTextColor
        return True

    def GetWidgetFontStyle(self,uType):
        uRet = "error"
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
                #todo:create function GetHexFromColor
                uRet=str(self.tTextColor)
        except Exception:
            pass
        return uRet


    def On_Button_Up(self,instance):

        if self.bEnabled:
            if hasattr(instance,'uTapType'):
                self.uTapType = instance.uTapType
            else:
                self.uTapType = u"up"

            Logger.debug (u'WidgetBase:On_Button_Up: Tap detected: %s:%s' %( self.uName, self.uTapType))

            self.OnButtonClicked()
            return

    def On_Button_Down(self,instance):

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

    def OnButtonClicked(self):

        uActionName          = ReplaceVars(self.uActionName)
        uActionNameDoubleTap = ReplaceVars(self.uActionNameDoubleTap)
        uActionNameUp        = ReplaceVars(self.uActionNameUpOnly)
        uActionNameDown      = ReplaceVars(self.uActionNameDownOnly)
        uActionNameLongTap   = ReplaceVars(self.uActionNameLongTap)
        aUseActionName       = []

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

        if self.iWidgetType == oWidgetType.Button or self.iWidgetType == oWidgetType.Picture:
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

        aActions=[]
        for uUseActionName in aUseActionName:
            aActionsTest=Globals.oActions.GetActionList(uActionName = uUseActionName, bNoCopy = True)
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

    def On_Gesture(self,instance):
        if self.bEnabled:
            if hasattr(instance,'aActions'):
                self.aWidgetActions=instance.aActions
                if self.aWidgetActions is not None:
                    Globals.oEvents.ExecuteActions( aActions=self.aWidgetActions,oParentWidget=self)

    def SaveLastWidgetPos(self):
        global oLastWidget,oLastWidgetSave
        oLastWidgetSave=oLastWidget
    def RestoreLastWidgetPos(self):
        global oLastWidget,oLastWidgetSave
        oLastWidget=oLastWidgetSave

    def Create(self,oParent):
        """ Dummy, needs to be overridden and not called """
        Logger.error(u'WidgetBase: Create called on base, not allowed [%s]' % self.uName)
        pass

oWidgetType         = cWidgetType()

