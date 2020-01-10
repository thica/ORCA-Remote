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

from xml.etree.ElementTree          import Element

from kivy.logger                    import Logger
from kivy.uix.widget                import Widget
from ORCA.widgets.core.ScrollableLabelLarge   import cScrollableLabelLarge
from ORCA.widgets.base.Base         import cWidgetBase
from ORCA.widgets.base.BaseBase     import cWidgetBaseBase
from ORCA.widgets.base.BaseText     import cWidgetBaseText

from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.LoadFile            import LoadFile
from ORCA.utils.FileName            import cFileName
from ORCA.vars.Replace              import ReplaceVars

from typing                         import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")
__all__ = ['cWidgetFileViewer']


class cWidgetFileViewer(cWidgetBase,cWidgetBaseText,cWidgetBaseBase):

    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-FileViewer
    WikiDoc:TOCTitle:FileViewer
    = FILEVIEWER =

    The fileviewer widget enables you show the content of of a text file. This widget shares the same attributes as the the textfield widget. Instead of the caption you have to set the filename of the file to show. Even if the user can edit the the file on screen, changes are not saved to the file.
    You need to call the updatewidget action to read and show the file
    The following attributes are additional attributes to common widget attributes

    The following attributes are additional attributes to common widget attributes and text attributes
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "FILEVIEWER". Capital letters!
    |-
    |filename
    |This defines the filename to show.
    |}</div>

    Below you see an example for a fileviewer widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="Shows a definition files" type="FILEVIEWER"  filename="$var(DEFINITIONPATH)/definition.xml" htextalign="left" vtextalign="top" backgroundcolor='#FFFFFFFF' />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super().__init__()
        self.uFileName:str = "" #we don't  use cFileName by purpose to handle vars properly

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        self.uFileName  = GetXMLTextAttribute(oXMLNode,u'filename',    False,"")
        self.bNoTextSize = True
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def LoadFile(self):
        """ loads a file to show """
        oFn = cFileName('').ImportFullPath(ReplaceVars(self.uFileName))
        Logger.debug("Reading File:"+oFn)
        self.uCaption=LoadFile(oFn)

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        if self.CreateBase(Parent=oParent,Class=cScrollableLabelLarge):
            self.oParent.add_widget(self.oObject)
            return True
        return False

    def UpdateWidget(self):

        if self.oObject is  None:
            return
        self.LoadFile()
        self.oObject.text   =   self.uCaption

