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

from typing                         import Callable
from xml.etree.ElementTree          import Element
from kivy.uix.widget                import Widget
from ORCA.widgets.core.TouchButton  import cTouchButton
from ORCA.widgets.base.Base         import cWidgetBase
from ORCA.widgets.base.BaseBase     import cWidgetBaseBase
from ORCA.widgets.base.BaseText     import cWidgetBaseText
from ORCA.widgets.base.BaseAction   import cWidgetBaseAction

from ORCA.utils.Atlas               import ToAtlas
from ORCA.utils.XML                 import GetXMLTextAttribute, GetXMLBoolAttribute
from ORCA.utils.LogError            import LogError
from ORCA.utils.FileName            import cFileName

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")

__all__ = ['cWidgetButton']

class cWidgetButton(cWidgetBase,cWidgetBaseText,cWidgetBaseAction,cWidgetBaseBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-BUTTON
    WikiDoc:TOCTitle:Button
    = BUTTON =

    The button widget is one of the core widgets. If you press a button, an action is triggered
    The button widget shares the common widget attributes and the text widget attributes.

    The following attributes are additional attributes to common widget attributes and text attributes
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "BUTTON". Capital letters!
    |-
    |autohide
    |0/1: If the button text is empty on creation time, the button is disabled (invisible), if autohide is "1"
    |-
    |picturenormal
    |The picture to show, if the button is not pressed. You have to give the name of the picture file including the full path. You should use variables to provide the path to your picture file.
    |-
    |picturepressed
    |The picture to show, if the button is pressed. You have to give the name of the picture file including the full path. You should use variables to provide the path to your picture file.
    |-
    |picturedisabled
    |Reserved for future extension
    |}</div>

    There is a convinience function for defining pictures: If the picturenormal ends with an asterix "*", the strings " normal" and "pressed" will be added to define the full standard and the full pressed picture file name.

    Below you see an example for a button widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Button Channel Up' type='BUTTON' posx='%5' posy='of:bottom:Anchor Gap Media Circle' width='%20' height='of:width:self' picturenormal='button round*' action='Send Page Up' fontsize='%h50'  caption='icon:osd_next' />
    </syntaxhighlight></div>

    Some examples for buttons (taken from the silver_hires skin)

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Normal
    ! align="left" | Pressed
    |-
    |[[File:widget_button round framed normal.png|link=]]
    |[[File:widget_button round framed pressed.png|link=]]
    |-
    |[[File:widget_button round normal.png|link=]]
    |[[File:widget_button round pressed.png|link=]]
    |-
    |[[File:widget_button square framed normal.png|link=]]
    |[[File:widget_button square framed pressed.png|link=]]
    |-
    |[[File:widget_button wide framed normal.png|link=]]
    |[[File:widget_button wide framed pressed.png|link=]]
    |-
    |[[File:widget_button wide normal.png|link=]]
    |[[File:widget_button wide pressed.png|link=]]
    |}</div>


    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super().__init__()
        self.oFnButtonPictureNormal:cFileName        = cFileName('')
        self.oFnButtonPicturePressed:cFileName       = cFileName('')
        self.bAutoHide:bool                          = False
        # Disabled reserved for future
        self.oFnButtonPictureDisabled:cFileName      = cFileName('')
        self.ClassName:Callable                      = cTouchButton

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        bRet:bool =self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)
        if bRet:
            self.SetPictureNormal   (GetXMLTextAttribute(oXMLNode,u'picturenormal',     False,u''))
            self.SetPicturePressed  (GetXMLTextAttribute(oXMLNode,u'picturepressed',    False,u''))
            #self.SetPictureDisabled (GetXMLTextAttribute(oXMLNode,u'picturedisabled',    False,u''))
            self.bAutoHide  = GetXMLBoolAttribute(oXMLNode,u'autohide',False,False)
            if self.bAutoHide:
                if self.uCaption == u'':
                    self.EnableWidget(bEnable=False)
            if not self.oFnButtonPictureNormal.string.rfind('*')==-1:
                if self.oFnButtonPicturePressed.IsEmpty():
                    self.oFnButtonPicturePressed.ImportFullPath(self.oFnButtonPictureNormal.string.replace(u'*',u' pressed'))
                self.oFnButtonPictureNormal.ImportFullPath(self.oFnButtonPictureNormal.string.replace(u'*',u' normal'))

        return bRet

    # noinspection PyUnusedLocal
    def SetPictureNormal(self,uPictureNormal:str,bClearCache:bool=False) -> bool:
        """ sets the unpressed picture """
        if uPictureNormal!='':
            self.oFnButtonPictureNormal.ImportFullPath(uPictureNormal)
        if self.oObject:
            self.oObject.background_normal  =  ToAtlas(self.oFnButtonPictureNormal)
            # self.SetCaption(self.uCaption)
        return True

    def SetPicturePressed(self,uPicturePressed:str) -> bool:
        """ sets the pressed picture """

        if uPicturePressed!='':
            self.oFnButtonPicturePressed.ImportFullPath(uPicturePressed)

        if self.oObject:
            self.oObject.background_down = ToAtlas(self.oFnButtonPicturePressed)
        return True

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        try:
            if not self.oFnButtonPictureNormal.IsEmpty():
                self.AddArg('border',               (0,0,0,0))
                self.AddArg('background_normal',    ToAtlas(self.oFnButtonPictureNormal))
                if not self.oFnButtonPicturePressed.IsEmpty():
                    self.AddArg('background_down',  ToAtlas(self.oFnButtonPicturePressed))

            if self.uActionNameUpOnly:
                self.AddArg('forceup', '1')

            if self.CreateBase(Parent=oParent, Class=self.ClassName):
                self.oObject.bind(on_q_release  = self.On_Button_Up)
                self.oObject.bind(on_q_press    = self.On_Button_Down)
                self.oObject.bind(on_gesture    = self.On_Gesture)
                self.oParent.add_widget(self.oObject)
                return True
            return False
        except Exception as e:
            LogError(uMsg=u'cWidgetButton:Unexpected error Creating Object:',oException=e)
            return False

    def UpdateWidget(self) -> None:
        super().UpdateWidget()
        self.SetPictureNormal("")
        return

