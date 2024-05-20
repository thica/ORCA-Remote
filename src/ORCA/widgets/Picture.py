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

from xml.etree.ElementTree              import Element
from kivy.uix.widget                    import Widget
from ORCA.widgets.base.Base             import cWidgetBase
from ORCA.widgets.base.BaseBase         import cWidgetBaseBase
from ORCA.widgets.base.BaseAction       import cWidgetBaseAction

from ORCA.widgets.core.TouchImage       import cTouchImage
from ORCA.utils.Atlas                   import ToAtlas
from ORCA.utils.XML                     import GetXMLTextAttribute
from ORCA.utils.FileName                import cFileName
from ORCA.utils.GetSetDefinitionName    import GetSetDefinitionName
from ORCA.utils.LogError                import LogError
from ORCA.definition.DefinitionContext  import SetDefinitionContext
from ORCA.definition.DefinitionContext  import RestoreDefinitionContext
from ORCA.vars.Replace                  import ReplaceVars

from ORCA.Globals import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.screen.ScreenPage import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar('cScreenPage')

__all__ = ['cWidgetPicture']

class cWidgetPicture(cWidgetBase,cWidgetBaseAction,cWidgetBaseBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-PICTURE
    WikiDoc:TOCTitle:Picture
    = Picture =
    The picture widget enables you to place a picture on you page
    Pictures will be scaled, if they do not fit to the width and heigth attributes. You need to provide the width and height attributes
    You could add click/double click and wipe actions as well.
    There are only a few additional attributes to the common widget attributs

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "PICTURE". Capital letters!
    |-
    |picturenormal
    |You have to give the name of the picture file including the full path. You should use variables to provide the path to your picture file.
    |}</div>

    Below you see an example for a picture widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Picture BULB Lumi ON' type='PICTURE' posx='center' posy='top' height='of:width:self:*1.4' picturenormal='bulb on' enabled='0'/>
   </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.oFnPictureNormal:cFileName               = cFileName('')
        # we dont use a cFileName object by purpose, as we might need to handle vars and skin reference
        self.uFnPictureNormalVar:str            = ''

    def InitWidgetFromXml(self,*,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:

        """ Reads further Widget attributes from a xml node """
        bRet:bool = self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)
        self.SetPictureNormal (GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='picturenormal',bMandatory=False,vDefault=''))
        return bRet

    def SetPictureNormal(self,uFnPictureNormal:str,bClearCache:bool=False) -> bool:
        """ sets the picture """

        try:
            uNewDefinitionContext:str=''

            if 'DEFINITIONPATH[' in uFnPictureNormal:
                uNewDefinitionContext,uFnPictureNormal=GetSetDefinitionName(uText=uFnPictureNormal)
            elif Globals.uDefinitionContext!=self.uDefinitionContext:
                uNewDefinitionContext = self.uDefinitionContext
                SetDefinitionContext(uDefinitionName=uNewDefinitionContext)
            self.uFnPictureNormalVar    = uFnPictureNormal
            self.oFnPictureNormal     = self.oFnPictureNormal.Clear().ImportFullPath(uFnFullName=ReplaceVars(uFnPictureNormal))
            if self.oObject:
                self.oObject.source   =  ToAtlas(oFileName=self.oFnPictureNormal)
                if bClearCache:
                    if self.oObject._coreimage.filename is not None:
                        self.oObject.reload()
            if uNewDefinitionContext != '':
                RestoreDefinitionContext()
        except Exception as e:
            LogError(uMsg='Can\'t set picture:'+uFnPictureNormal, oException=e)
            return False

        return True

    def Create(self, oParent: Widget) -> bool:
        """ creates the Widget """
        #self.AddArg('allow_stretch',True)
        #self.AddArg('keep_ratio',False)
        self.AddArg('fit_mode', "fill")
        self.AddArg('source',ToAtlas(oFileName=self.oFnPictureNormal))

        if self.CreateBase(Parent=oParent, Class=cTouchImage):
            if self.uActionName !='' or self.uActionNameDoubleTap !='' :
                self.oObject.bind(on_q_release  = self.On_Button_Up)
                self.oObject.bind(on_q_press    = self.On_Button_Down)
            self.oObject.bind(on_gesture=self.On_Gesture)
            self.oParent.add_widget(self.oObject)
            return True
        return False

    def UpdateWidget(self) -> None:
        super().UpdateWidget()
        self.SetPictureNormal(self.uFnPictureNormalVar, bClearCache=True)
        return
