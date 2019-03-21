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


from ORCA.widgets.Base              import oWidgetType
from ORCA.widgets.Button            import cWidgetButton
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.vars.Access               import SetVar
from ORCA.vars.Access               import GetVar
from ORCA.vars.Actions              import Var_Invert
from ORCA.utils.FileName            import cFileName

__all__ = ['cWidgetSwitch']

class cWidgetSwitch(cWidgetButton):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-SWITCH
    WikiDoc:TOCTitle:Switch
    = SWITCH =

    The switch widget action is based on the button widget, so refer the the button widget for further information. The switch widget can only be used for picture buttons, and it toggles the "normal" and the "pressed" pictures. The state of the button will passed to variable you have to provide, and toogles to '0" and '1"
    The following attributes are additional attributes to button widget attributes

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "SWITCH". Capital letters!
    |-
    |destvar
    |The destination variable , which will be switched on state change. Will be set to "0" or "1"
    |}</div>

    Below you see an example for a switch widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="ButtonBiState" type="SWITCH"  posy="%40" height="of:width:self:*0.25" fontsize='%h50' caption='Switch Button' htextalign='center' vtextalign='middle' picturenormal="button wide*" destvar="STATUSBUTTONBISTATE" action="ToggleButtonBiState"/>
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super(cWidgetSwitch, self).__init__(**kwargs)
        self.oFnButtonPictureNormalOrg  = cFileName(u'')
        self.oFnButtonPicturePressedOrg = cFileName(u'')
        self.uDestVar                   = u''
        self.uGroup                     = u''

    def InitWidgetFromXml(self,oXMLNode,oParentScreenPage, uAnchor):
        """ Reads further Widget attributes from a xml node """
        bRet=super(cWidgetSwitch, self).InitWidgetFromXml(oXMLNode,oParentScreenPage, uAnchor)
        self.uDestVar          = GetXMLTextAttribute(oXMLNode,u'destvar',    False,self.uName+'_switchstate')
        self.uGroup            = GetXMLTextAttribute(oXMLNode,u'group',      False,'')
        self.oFnButtonPictureNormalOrg        = cFileName(self.oFnButtonPictureNormal)
        self.oFnButtonPicturePressedOrg       = cFileName(self.oFnButtonPicturePressed)
        if GetVar(uVarName = self.uDestVar)=='1':
            self.oFnButtonPictureNormal,self.oFnButtonPicturePressed=self.oFnButtonPicturePressed,self.oFnButtonPictureNormal
        return bRet

    def On_Button_Up(self,instance):
        self.Invert(instance)
        self.GroupSwitch()
        super(cWidgetSwitch, self).On_Button_Up(instance)

    def On_Button_Down(self,instance):
        pass

    def Invert(self,instance):
        """ Inverts the button state """
        if self.uGroup=='':
            self.InvertSwitch(instance)
            return
        if GetVar(uVarName = self.uDestVar)=='1':
            return
        self.InvertSwitch(instance)

    def InvertSwitch(self,instance):
        """ Inverts and button and the var """
        if GetVar(uVarName = self.uDestVar)=='1':
            SetVar(uVarName = self.uDestVar, oVarValue = '0')
            self.SetPictureNormal( self.oFnButtonPictureNormalOrg.string,True)
            self.SetPicturePressed(self.oFnButtonPicturePressedOrg.string)
        else:
            SetVar(uVarName = self.uDestVar, oVarValue = '1')
            self.SetPictureNormal( self.oFnButtonPicturePressedOrg.string,True)
            self.SetPicturePressed( self.oFnButtonPictureNormalOrg.string)

    def GroupSwitch(self):
        """ Switches the button as part of a button group """
        if self.uGroup!='':
            if GetVar(uVarName = self.uDestVar)=='1':
                for oWidget in self.oParentScreenPage.aWidgets:
                    if oWidget.iWidgetType==oWidgetType.Switch:
                        if not oWidget== self:
                            if oWidget.uGroup==self.uGroup:
                                SetVar(uVarName = oWidget.uDestVar, oVarValue = '1')
                                oWidget.InvertSwitch(None)

    def UpdateWidget(self):
        """ Updates the switch states based on the vars """
        if self.uGroup:
            if GetVar(uVarName = self.uDestVar)=='1':
                self.GroupSwitch()
                #return
        Var_Invert(self.uDestVar)
        self.InvertSwitch(None)
        super(cWidgetSwitch, self).UpdateWidget()
        return

    def AllButtonsOff(self):
        """ Sets all button / switches to off """
        if self.uGroup!='':
            for oWidget in self.oParentScreenPage.aWidgets:
                if oWidget.iWidgetType==oWidgetType.Switch:
                    if oWidget.uGroup==self.uGroup:
                        SetVar(uVarName = oWidget.uDestVar, oVarValue = '1')
                        oWidget.InvertSwitch(None)

