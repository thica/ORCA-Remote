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
from typing                         import Union
from xml.etree.ElementTree          import Element
from kivy.uix.widget                import Widget
from kivy.uix.label                 import Label
from ORCA.ui.InputKeyboard          import ShowKeyBoard
from ORCA.vars.Access               import GetVar
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.widgets.TextField         import cWidgetTextField

from ORCA.Globals import Globals


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.screen.ScreenPage import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar('cScreenPage')
__all__ = ['cWidgetTextInput']


# noinspection PyUnusedLocal
class cWidgetTextInput(cWidgetTextField):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-TEXTINPUT
    WikiDoc:TOCTitle:TextInput
    = TEXTINPUT =

    The textinput widget enable you to place a widget, where a user can input a free text. If it receives the focus, an input page with an virtual keyboard will be shown.
    Please note: This widget supports actions.
    The common widget attributes and the text attibutes are valid for this widget
    The following attributes are additional to these attributes
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "TEXTINPUT". Capital letters!
    |-
    |destvar
    |defines the system variable, where the user input should be stored into. Default is 'inputstring'
    |-
    |picturenormal
    |You can place a background image at your input field. You have to give the name of the picture file including the full path. You should use variables to provide the path to your picture file. Please provide "none" if you do not want a background picture.
    |}</div>

    Below you see an example for a textinput widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Inputfield' type='TEXTINPUT' posx='center' posy='%97' height='%70' width='%95'  fontsize='%h80' vtextalign='bottom' htextalign='left' destvar='inputstring' action='Send String' picturenormal='none' />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super().__init__()
        self.uDestVar:str       = ''
        self.oInputKeyboard = None
    def InitWidgetFromXml(self,*,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        bRet:bool = super(cWidgetTextInput, self).InitWidgetFromXml(oXMLNode=oXMLNode,oParentScreenPage=oParentScreenPage, uAnchor=uAnchor)
        self.uDestVar = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='destvar', bMandatory=False,vDefault='inputstring')
        uTmp:str = GetVar(uVarName = self.uDestVar)
        if uTmp:
            self.uCaption=uTmp
        return bRet

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        if super().Create(oParent):
            self.oObject.unbind(on_q_release    = self.On_Button_Up)
            self.oObject.bind(on_q_release    = self.On_Button_Up1)
            return True
        return False
    def On_Button_Up1(self,instance:Label) -> None:
        """ Shows the keyboard, when the textfield has been clicked """
        if not Globals.oTheScreen.GuiIsBlocked():
            self.oInputKeyboard=ShowKeyBoard(uDestVar=self.uDestVar,oFktNotify=self.On_Enter)
    def On_Focus(self,instance:Union[Label,None], value) -> None:
        """ Shows the keyboard, when the textfield got the focus """
        if not Globals.oTheScreen.GuiIsBlocked():
            if self.oObject:
                self.oInputKeyboard=ShowKeyBoard(uDestVar=self.uDestVar,oFktNotify=self.On_Enter)
    def On_Enter(self,uText:str) -> None:
        """ Accepts the user input """
        self.oObject.text=uText
        self.On_Button_Up(self.oObject)

    def SetFocus(self) -> bool:
        """ Sets the focus """
        self.On_Focus(None, True)
        return True



