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

from typing                         import List
from typing                         import Optional
from kivy.uix.widget                import Widget
from kivy.uix.scrollview            import ScrollView
from kivy.uix.floatlayout           import FloatLayout
from ORCA.widgets.base.Base         import cWidgetBase
from ORCA.widgets.Picture           import cWidgetPicture


__all__ = ['cWidgetScrollContainer']

class cWidgetScrollContainer(cWidgetPicture):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-SCROLLCONTAINER
    WikiDoc:TOCTitle:ScrollContainer
    = ScrollContainer =

    The scrollcontainer widget is a container widget to place widgets in a scrollable widget
    The scrolllist widget is based on the picture widget, please use the documentation for the common attributes

    You can place all kind of widgets (with the exception of dropdowns into the container
    The following attributes are additional attributes to common picture attributes

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "SCROLLCONTAINER". Capital letters!
    |-
    |container
    |A string, which identifies the container AND all elements to place into the row of the container. If blank, a random value is used
    |}</div>

    Below you see an example for a container definition
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Anchor1' type='ANCHOR' posx='center' posy='of:bottom:Anchor Top' width='%23' height='%70' >
      <elements>
        <element name="ScollBox Left" type="SCROLLCONTAINER" picturenormal="background boxes"  >
          <element name='Anchor1 Inner' type='ANCHOR' width='%200' height="of:width:self:*1.5"  >
            <xi:include href="$var(DEFINITIONPATHSKINELEMENTS)/block_buttons_main_menu.xml" parse="xml" />
          </element>
        </element>
      </elements>
    </element>

    </syntaxhighlight></div>
    WikiDoc:End
    """

    # noinspection PyUnusedLocal
    def __init__(self,**kwargs):
        super().__init__()
        self.oObjectContent:Optional[FloatLayout]   = None
        self.oObjectScroll:Optional[ScrollView]     = None
        self.aChilds:List[cWidgetBase]              = []
        self.iMaxX:int                              = 0
        self.iMaxY:int                              = 0

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        aChilds:List[cWidgetBase]

        if super().Create(oParent):
            self.CreateScrollContainer()
            return True
        return False

    def GetChilds(self) -> None:
        """
         save a copy of the screenpage widgets locally
        """

        for oWidget in self.oParentScreenPage.dWidgetsID.values():
            if oWidget.uContainer == self.uContainer and oWidget!=self:
                oWidget.iPosXInit = oWidget.iPosXInit - self.iPosXInit
                oWidget.iPosYInit = oWidget.iPosYInit - self.iPosYInit
                self.iMaxX        = max(self.iMaxX, oWidget.iPosXInit + oWidget.iWidthInit)
                self.iMaxY        = max(self.iMaxY, oWidget.iPosYInit + oWidget.iHeightInit)
                self.aChilds.append(oWidget)
        self.iMaxX = int(self.iMaxX/self.oDef.fRationX)
        self.iMaxY = int(self.iMaxY/self.oDef.fRationY)
        return None

    def CreateChilds(self):
        oChild: cWidgetBase
        for oChild in self.aChilds:
            oChild.Create(oParent = self.oObjectContent)

    def CreateScrollContainer(self):
        self.GetChilds()
        self.oObjectScroll  = ScrollView(size=self.oObject.size, pos=self.oObject.pos, do_scroll_x=True,do_scroll_y=True, scroll_type=['bars', 'content'], size_hint=(1, None), bar_width='10dp')
        self.oObjectContent = Widget(size=(self.iMaxX, self.iMaxY), size_hint=(None, None))
        self.oObject.add_widget(self.oObjectScroll)
        self.oObjectScroll.add_widget(self.oObjectContent)
        self.CreateChilds()



