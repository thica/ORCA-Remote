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

from typing                             import Union
from xml.etree.ElementTree              import Element
from kivy.uix.image                     import Image
from kivy.uix.widget                    import Widget
from ORCA.vars.Helpers                  import Round
from ORCA.vars.Access                   import SetVar
from ORCA.vars.Access                   import GetVar
from ORCA.utils.TypeConvert             import ToFloat
from ORCA.utils.TypeConvert             import ToUnicode
from ORCA.widgets.base.Base             import cWidgetBase
from ORCA.widgets.base.BaseBase         import cWidgetBaseBase
from ORCA.widgets.base.BaseAction       import cWidgetBaseAction

from ORCA.widgets.core.RotateScatter    import cRotateScatter
from ORCA.utils.Atlas                   import ToAtlas
from ORCA.utils.FileName                import cFileName
from ORCA.utils.XML                     import GetXMLTextAttributeVar
from ORCA.utils.XML                     import GetXMLFloatAttributeVar
from ORCA.utils.XML                     import GetXMLIntAttributeVar
from ORCA.utils.XML                     import GetXMLIntAttribute
from ORCA.utils.XML                     import GetXMLBoolAttributeVar
from ORCA.utils.XML                     import GetXMLTextAttribute

from ORCA.widgets.core.Border           import cBorder

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")

__all__ = ['cWidgetKnob']

class cWidgetKnob(cWidgetBase,cWidgetBaseAction,cWidgetBaseBase):
    """ a knob widget """

    '''
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-KNOB
    WikiDoc:TOCTitle:Knob
    = KNOB =

    The knob widget provides the function of a turnable button. If you turn the button by mouse or by touch, an action is triggered
    The knob widget provides two modi:

    * Endless turn: You can turn the knob in both directions as much as you like
    * Limited turn: You can turn the the knob within defined boundaries. Each position is aligned to a specific level

    The following attributes are additional attributes to common widget attributes.

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "KNOB". Capital letters!
    |-
    |picturenormal
    |The picture to show. It is advised to use a round picture. If you use a marker, it should point to the upper , center position.
    |-
    |leftboundaryangle
    |If you want to have a KNOB with limited turn, you have to provide the angle/degree of the left and right limit. "o" (Null) is top center / North, -90 would be West, 90 would be East
    |-
    |rightboundaryangle
    |The angle/degree of the right limit
    |-
    |mindatavalue
    |For limited turn KNOBs, this is the value, which is assigned to the Knob, when it reaches the leftboundaryangle. Data values are float values, so you can use small numbers as well.
    |-
    |maxdatavalue
    |For limited turn KNOBs, this is the value, which is assigned to the Knob, when it reaches the rightboundaryangle. 
    |-
    |destvar
    |This is the ''PREFIX'' for the variable, which holds the status of the KNOB. The KNOB widgets sets/updates the following variables, when it get turned:
    * [PREFIX]_value: For limited turn KNOBs: The value assigned to the KNOB position within the data range.
    * [PREFIX]_degree: The angle/degree position of the KNOB. This will a negative value, if the KNOB is turned to the left from the null position. For endless turn KNOBs, this value extends for 360 / -360 after a full turn.
    * [PREFIX]_absdegree: The absolute angle/degree position of the KNOB. This is between 0 and 359 degree. After a full rotation, it begins with o again.
    * [PREFIX]_direction: The direction of the last turn: will be "left" or "right"
    |-
    |roundpos
    |The position in digits, the  [PREFIX]_value should be rounded. Examples: If the  [PREFIX]_value is 10.623:
    * "0" will round to 11
    * "1" will round to 10.6
    |-
    |discardmoves
    |if you set this attribute to "1", you just get a notification, when the user finishes moving the widget. If not set, you get (a lot of) notifications, while the user is moving the widget on the screen. Can be usefull, if you would like to avoid an interface being swamped by commands.
    |}</div>

    If you want to set the position of the KNOB (The Knob Picture) , meaningful for limited turn KNOBs only, you have to set [PREFIX]_value and the call the updatewidget action.

    WikiDoc:End
    '''

    ''' todo: add example for Knob '''

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.oFnPictureNormal:Union[cFileName,None]  = None
        self.iAbsAngle:int                           = 0
        self.fDataRange:float                        = 0.0
        self.fValue:float                            = 0.0
        self.oObjectPicture:Union[Image,None]        = None
        self.fMin:float                              = 0.0
        self.fMax:float                              = 100.0
        self.iRange:int                              = 360
        self.iLeftBoundaryAngle:int                  = 0
        self.iRightBoundaryAngle:int                 = 90
        self.oBorderInner:Union[cBorder,None]        = None
        self.bDiscardMoves:bool                      = True
        self.fOldValue:float                         = -1.0
        self.uDestVar:str                            = u''
        self.iRoundPos:int                           = 0

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        bRet=self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)
        if bRet:
            self.oFnPictureNormal           = cFileName("").ImportFullPath(uFnFullName=GetXMLTextAttributeVar(oXMLNode=oXMLNode,uTag=u'picturenormal',bMandatory=False,uDefault=u''))
            self.fMin                       = GetXMLFloatAttributeVar(oXMLNode=oXMLNode,uTag=u'mindatavalue',    bMandatory=False,fDefault=0.0)
            self.fMax                       = GetXMLFloatAttributeVar(oXMLNode=oXMLNode,uTag=u'maxdatavalue',    bMandatory=False,fDefault=100.0)
            self.iLeftBoundaryAngle         = GetXMLIntAttributeVar(oXMLNode=oXMLNode,uTag=u'leftboundaryangle', bMandatory=False,iDefault=0)
            self.iRightBoundaryAngle        = GetXMLIntAttributeVar(oXMLNode=oXMLNode,uTag=u'rightboundaryangle', bMandatory=False,iDefault=0)
            self.uDestVar                   = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=u'destvar',    bMandatory=False,vDefault=u'knob')
            self.bDiscardMoves              = GetXMLBoolAttributeVar(oXMLNode=oXMLNode,uTag=u'discardmoves',bMandatory=False,bDefault=False)
            #roundpos: the position, the  number should be rounded
            self.iRoundPos                  = GetXMLIntAttribute(oXMLNode=oXMLNode,uTag=u'roundpos', bMandatory=False,iDefault=0)
            self.fValue                     = 0.0
            self.fOldValue                  = 10000.23445
            self.iAbsAngle                  = 0
        return bRet

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        self.AddArg('allow_stretch',True)
        self.AddArg('keep_ratio',False)
        self.AddArg('source',ToAtlas(oFileName=self.oFnPictureNormal))
        self.CreateBase(Parent=oParent,Class=Image)
        self.oObjectPicture             = self.oObject
        self.AddArg('do_scale',False)
        self.AddArg('do_translation_y',False)
        self.AddArg('auto_bring_to_front',False)
        if self.CreateBase(Parent=oParent,Class=cRotateScatter):
            self.oObjectPicture.pos         = (0,0)
            self.fDataRange=abs(self.fMax-self.fMin)

            '''
            # Todo : Check and rework
            if self.fMin>0:
                self.fDataRange=self.fMin
            else:
                self.fDataRange=abs(self.fMin)

            if self.fMax>0:
                self.fDataRange=self.fMax-self.fDataRange
            else:
                self.fDataRange=self.fDataRange+abs(self.fMax)
            '''

            if self.iLeftBoundaryAngle>0:
                self.iRange=self.iLeftBoundaryAngle
            else:
                self.iRange=abs(self.iLeftBoundaryAngle)

            if self.iRightBoundaryAngle>0:
                self.iRange += self.iRightBoundaryAngle
            else:
                self.iRange += abs(self.iRightBoundaryAngle)

            self.oObject.iLeftBoundaryAngle=self.iLeftBoundaryAngle
            self.oObject.iRightBoundaryAngle=self.iRightBoundaryAngle
            self.oObject.bind(on_widget_turned=self.OnNotifyChange)

            # Capability to click on Knobs as well (seems not to work by now)
            if not self.uActionName==u'':
                self.oObject.bind(on_q_release=self.On_Button_Up)
                self.oObject.bind(on_q_press  =self.On_Button_Down)

            self.oParent.add_widget(self.oObject)
            self.oObject.add_widget(self.oObjectPicture)

            return True
        return False

    def OnNotifyChange(self,instance:Image) -> None:
        """ called, when the knob has been turned """

        iRangePos:int
        fRangeProz:float

        if self.bDiscardMoves and (instance.uMoveType == u'move'):
            return

        if not self.uDestVar==u'':
            iRangePos=self.oObject.iAngle-self.iLeftBoundaryAngle

            if not self.iRange==0:
                fRangeProz=float(iRangePos)/float(self.iRange)
            else:
                fRangeProz=0.0

            if self.fMin<self.fMax:
                self.fValue=Round(self.fMin+self.fDataRange*fRangeProz,self.iRoundPos)
            else:
                self.fValue=Round(self.fMin-self.fDataRange*fRangeProz,self.iRoundPos)
            if self.iRoundPos==0:
                self.fValue=int(self.fValue)
            #fValue=self.fMin+self.fDataRange*fRangeProz
            # print 'degree:',self.oObject.iAngle
            # print 'Range:',self.iRange
            # print 'DataRange:',self.fDataRange
            # print 'iRangePos:',iRangePos
            # print 'RangeProz:',fRangeProz
            # print 'Value:',fValue

            self.iAbsAngle=self.oObject.iAngle
            if self.iAbsAngle!=0:
                self.iAbsAngle= self.iAbsAngle % 360

            self.UpdateVars()
            if not self.uActionName==u'':
                if self.fOldValue!=self.fValue or (self.iLeftBoundaryAngle == self.iRightBoundaryAngle):
                    self.fOldValue=self.fValue
                    self.On_Button_Up(instance)

    def UpdateWidget(self) -> None:

        super().UpdateWidget()

        fNewValue:float
        fNewProz:float
        fNewDegree:float
        uValue:str

        if not self.uDestVar==u'':
            if not self.fDataRange==0:
                uValue      = GetVar(uVarName = self.uDestVar)
                fNewValue   = ToFloat(uValue)
                fNewProz    = (fNewValue-self.fMin)/self.fDataRange
                fNewDegree  = self.iLeftBoundaryAngle+self.iRange*fNewProz
                self.oObject.SetValue(fNewDegree)
                self.fValue = Round(fNewValue,self.iRoundPos)
            self.UpdateVars()

    def UpdateVars(self) -> None:
        """ updates the destination vars """
        if not self.uDestVar==u'':
            SetVar(uVarName = self.uDestVar, oVarValue = ToUnicode(self.fValue))
            if self.oObject:
                SetVar(uVarName = self.uDestVar+u'_degree',    oVarValue = ToUnicode(self.oObject.iAngle))
                SetVar(uVarName = self.uDestVar+u'_direction', oVarValue = ToUnicode(self.oObject.uDirection))
            SetVar(uVarName = self.uDestVar+u'_absdegree', oVarValue = ToUnicode(self.iAbsAngle))

    def SetMax(self,fMax:float) -> None:
        """ Set the upper limit """
        self.fMax        = fMax
        self.oObject.max = fMax
        self.UpdateWidget()

    def SetMin(self,fMin:float) -> None:
        """ Set the lower limit """
        self.fMin        = fMin
        self.oObject.min = fMin
        self.UpdateWidget()

    def FlipBorder(self) -> None:
        """ Creates/Flips the Border just for the inner Knob """

        if self.oObject != self.oObjectPicture and self.oObjectPicture is not  None:
            oTmpObject = self.oObject
            oTmpBorder = self.oBorder
            self.oBorder = self.oBorderInner
            self.oObject = self.oParent
            super().FlipBorder()
            self.oObject = oTmpObject
            self.oBorderInner = self.oBorder
            self.oBorder = oTmpBorder
