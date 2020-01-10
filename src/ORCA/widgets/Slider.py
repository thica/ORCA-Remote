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

from typing                          import Union
from xml.etree.ElementTree           import Element
from kivy.uix.widget                 import Widget
from ORCA.utils.Atlas                import ToAtlas
from ORCA.utils.LogError             import LogError
from ORCA.utils.TypeConvert          import ToFloat
from ORCA.utils.TypeConvert          import ToUnicode
from ORCA.utils.XML                  import GetXMLBoolAttributeVar
from ORCA.utils.XML                  import GetXMLIntAttribute
from ORCA.utils.XML                  import GetXMLTextAttribute
from ORCA.utils.XML                  import GetXMLTextAttributeVar
from ORCA.vars.Replace               import ReplaceVars
from ORCA.vars.Helpers               import Round
from ORCA.vars.Access                import SetVar
from ORCA.vars.Access                import GetVar
from ORCA.widgets.base.Base          import cWidgetBase
from ORCA.widgets.base.BaseBase      import cWidgetBaseBase
from ORCA.widgets.base.BaseText      import cWidgetBaseText
from ORCA.widgets.base.BaseAction    import cWidgetBaseAction

from ORCA.widgets.core.SliderEx      import cSliderEx
from ORCA.utils.FileName             import cFileName

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")


__all__ = ['cWidgetSlider']

class cWidgetSlider(cWidgetBase,cWidgetBaseText,cWidgetBaseAction,cWidgetBaseBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-SLIDER
    WikiDoc:TOCTitle:Slider
    = Slider =
    The slider widget provides the function of a slider. If you move the slider by mouse or by touch, an action is triggered. You can add a text to the slider knob as well
    If you want to set the position of the slider (The Button Picture), you have to set [PREFIX]_value and the call the updatewidget action.
    The following attributes are additional attributes to common widget and text attributes

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "SLIDER". Capital letters!
    |-
    |picturenormal
    |The background picture to show. This pictrure will be shrinked  to 25% of its height to have a transparent background
    |-
    |picturebutton
    |The button picture to show. Could be a round or a square pricture
    |-
    |mindatavalue
    |This is the value, which is assigned to the slider, when it reaches the left boundary. Data values are float values, so you can use small numbers as well.
    |-
    |maxdatavalue
    |This is the value, which is assigned to the slider when it reaches the right boundary.
    |-
    |direction
    |The direction of the slider: Could be eiter
    * horizontal
    * vertical
    |-
    |destvar
    |This is the ''PREFIX'' for the variable, which holds the status of the slider. The slider widgets sets/updates the following variable, when it get moved:
    * [PREFIX]_value: The value assigned to the slider position within the data range.
    |-
    |roundpos
    |The position in digits, the  [PREFIX]_value should be rounded. Examples: If the  [PREFIX]_value is 10.623:
    * "0" will round to 11
    * "1" will round to 10.6
    |-
    |discardmoves
    |If you set this attribute to "1", you just get a notification, when the user finishes moving the widget. If not set, you get (a lot of) notifications, while the user is moving the widget on the screen. Can be usefull, if you would like to avoid an interface being swamped by commands.
    |}</div>

    Below you see an example for a slider
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="Amp Volume Center" type="SLIDER" posx="center" posy="middle" width="%70" height="%75" picturenormal="background boxes" picturebutton="button round normal" action="Set Center Volume By Widget"  mindatavalue="-12" maxdatavalue="12" destvar="volume_center" roundpos="0" orientation="vertical" discardmoves="1" fontsize='%w50' caption='icon:volume_up'/>
    </syntaxhighlight></div>
    WikiDoc:End
    """

    # noinspection PyUnusedLocal
    def __init__(self,**kwargs):
        super().__init__()
        self.oFnPictureNormal:Union[cFileName,None] = None
        self.oFnPictureButton:Union[cFileName,None] = None
        self.uDestVar:str                           = u'slider'
        self.uDeviceOrientation:str                 = u'horizontal'
        self.bDiscardMoves:bool                     = True
        self.fMin:float                             = 0.0
        self.fMax:float                             = 100.0
        self.uMin:str                               = u''
        self.uMax:str                               = u''
        self.fValue:float                           = 0.0
        self.fOldValue:float                        = 10000.23445
        self.fDataRange:float                       = 100.0
        self.iRoundPos:int                          = 0

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        bRet=self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)
        if bRet:
            self.oFnPictureNormal           = cFileName(u'').ImportFullPath(GetXMLTextAttributeVar(oXMLNode,u'picturenormal',    False,u''))
            self.oFnPictureButton           = cFileName(u'').ImportFullPath(GetXMLTextAttributeVar(oXMLNode,u'picturebutton',    False,u''))

            self.uMin                       = GetXMLTextAttribute(oXMLNode,u'mindatavalue',      False,u'0.0')
            self.uMax                       = GetXMLTextAttribute(oXMLNode,u'maxdatavalue',      False,u'100.0')
            self.uDestVar                   = GetXMLTextAttribute(oXMLNode,u'destvar',           False,self.uDestVar)
            #roundpos: the position, the  number should be rounded
            self.iRoundPos                  = GetXMLIntAttribute(oXMLNode,u'roundpos', False,0)
            self.uDeviceOrientation         = GetXMLTextAttribute(oXMLNode,u'orientation',        False,self.uDeviceOrientation)
            self.bDiscardMoves              = GetXMLBoolAttributeVar(oXMLNode,u'discardmoves',    False,False)
            self.fValue                     = self.fMin

        return bRet

    def Create(self, oParent: Widget) -> bool:
        """ creates the Widget """
        try:
            self.fMin = ToFloat(ReplaceVars(self.uMin))
            self.fMax = ToFloat(ReplaceVars(self.uMax))
            self.AddArg('min',              self.fMin)
            self.AddArg('max',              self.fMax)
            self.AddArg('orientation',      self.uDeviceOrientation)
            self.AddArg('value',            self.fMin)
            self.AddArg('background_pic',   ToAtlas(self.oFnPictureNormal))
            self.AddArg('button_pic',       ToAtlas(self.oFnPictureButton))
            if self.CreateBase(Parent=oParent, Class=cSliderEx):
                self.fDataRange=abs(self.fMax-self.fMin)
                self.oObject.bind(on_slider_moved=self.OnNotifyChange)
                # Capability to click on Knobs as well (needs to be implemented)
                if not self.uActionName==u'':
                    self.oObject.bind(on_release=self.On_Button_Up)
                    self.oObject.bind(on_press  =self.On_Button_Down)

                self.oParent.add_widget(self.oObject)
                self.UpdateWidget()
                return True
            return False
        except Exception as e:
            LogError ( uMsg=u'cWidgetSlider:Unexpected error Creating Object:',oException=e)
            return False

    def OnNotifyChange(self,instance):
        """ will be called, when the slider will be moved """

        if self.bDiscardMoves and (instance.uMoveType == u'move'):
            return

        if not self.bIsEnabled:
            return

        if not self.uDestVar==u'':
            if self.fMin<self.fMax:
                self.fValue=Round(self.oObject.value,self.iRoundPos)
            else:
                self.fValue=Round(self.fMax-self.oObject.value,self.iRoundPos)
            if self.iRoundPos==0:
                self.fValue=int(self.fValue)
            self.UpdateVars()
            if not self.uActionName==u'':
                if self.fOldValue!=self.fValue:
                    self.fOldValue=self.fValue
                    self.On_Button_Up(instance)

    def UpdateWidget(self) -> None:
        """ Updates the silder pos, based on the assigned Var """

        uValue:str
        fMax:float
        fMin:float

        super().UpdateWidget()

        if not self.uDestVar==u'':
            uValue=GetVar(uVarName = self.uDestVar)
            fNewValue=ToFloat(uValue)

            if GetVar(uVarName=self.uMax) != u'':
                fMax = ToFloat(GetVar(uVarName=self.uMax))
            else:
                fMax = self.fMax

            if GetVar(uVarName=self.uMin) != u'':
                fMin = ToFloat(GetVar(uVarName=self.uMin))
            else:
                fMin = self.fMin

            if fNewValue>fMax:
                fNewValue=fMax
            if fNewValue<fMin:
                fNewValue=fMin
            if self.oObject:
                self.oObject.SetValue(fNewValue)
            self.fValue=Round(fNewValue,self.iRoundPos)
        self.UpdateVars()

    def UpdateVars(self):
        """ Updates the vars, if the slider has been moved """
        if not self.uDestVar==u'':
            SetVar(uVarName = self.uDestVar, oVarValue = ToUnicode(self.fValue))

    def SetMax(self,fMax):
        """ Set the upper limit """
        self.fMax=fMax
        self.oObject.max=fMax
        self.UpdateWidget()

    def SetMin(self,fMin):
        """ Set the lower limit """
        self.fMin=fMin
        self.oObject.min=fMin
        self.UpdateWidget()
