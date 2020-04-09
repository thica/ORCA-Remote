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

from copy                           import copy
from typing                         import List
from typing                         import Tuple
from typing                         import Union
from xml.etree.ElementTree          import Element
from kivy.uix.widget                import Widget
from kivy.uix.scrollview            import ScrollView
from kivy.uix.floatlayout           import FloatLayout
from ORCA.widgets.base.Base         import cWidgetBase

from ORCA.widgets.Picture           import cWidgetPicture
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.vars.Actions              import Var_GetArrayEx
from ORCA.vars.Replace              import ReplaceVars
from ORCA.vars.Helpers              import CopyDict

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")


__all__ = ['cWidgetScrollList']

class cWidgetScrollList(cWidgetPicture):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-SCROLLLIST
    WikiDoc:TOCTitle:ScrollList
    = ScrollList =

    The scrolllist widget is a container widget to place lines of widget in a scrollable widget
    The scrolllist widget is based on the picture widget, please use the documentation for the common attributes

    To Identify the the source widget in actions triggered by widgets in the scroll list:
    The "SCROLLLISTVALUE" value is added to the action pars which refers to the widget text
    The "SCROLLLISTINDEX" index is added to the action pars which refers to the line order, eg: "0" is the first line in the list
    The "SCROLLLISTVARINDEX" index is added to the action pars which refers to the index number of the vararray

    The list of lines within the container is build from the vararry of minimum one widget within the line definition. So, one widget must have a caption with an array variable
    You can place all kind of widgets (with the exception of dropdowns in a row/line of the container
    All widgets got an index "[x]" added to the widget name, to manage them thought the actions

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
    |-
    |rowheight
    |The rowheigth of a full line within the container: The line definition (all widgets in a line) must fir the this number
    |}</div>

    Below you see an example for a container definition
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='Anchor1' type='ANCHOR' posx='%2' posy='%20' width='%30' height='%60' >
      <elements>
        <element name="ScrollBox Left" type="SCROLLLIST" picturenormal="background boxes" container="container_1" rowheight="%25"  />
        <element name='Anchor1 Inner' type='ANCHOR'  height='%25' >
           <element name="First Button"       type="BUTTON" posx="left"  posy="top"    height="%100" width="%40" picturenormal='button wide*'    container="container_1" caption="First Button" action="Show Page" actionpars='{"pagename":"Page_Main"}'  />
           <element name="Second Button Top"  type="BUTTON" posx="right" posy="top"    height="%50" width="%60" picturenormal="button wide*"     container="container_1" caption="$var(scrollcontent_button1_text[])" action="Show Page" actionpars='{"pagename":"Page_Main"}'  />
           <element name="Second Button Down" type="BUTTON" posx="right" posy="bottom" height="%50" width="%60" picturenormal="button wide*"     container="container_1" caption="$var(scrollcontent_button2_text[])" action="Show Page" actionpars='{"pagename":"Page_Main"}'  />
        </element>
      </elements>
    </element>
    </syntaxhighlight></div>

    A second example with automated container assignment
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">

    </syntaxhighlight></div>


    WikiDoc:End
    """

    # noinspection PyUnusedLocal
    def __init__(self,**kwargs):
        super().__init__()
        self.oObjectContent:Union[FloatLayout,None] = None
        self.oObjectScroll:Union[ScrollView,None]   = None
        self.uRowHeightInit:str                     = u''
        self.iRowHeightScreen:int                   = 0
        self.iRowHeight:int                         = 0
        self.iNumRows:int                           = 0
        self.aListChilds:List[cWidgetBase]          = []
        self.aChilds:List[cWidgetBase]              = []


    def InitWidgetFromXml(self,*,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        self.uRowHeightInit = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag="rowheight",bMandatory=True,vDefault="%20")
        return super().InitWidgetFromXml(oXMLNode=oXMLNode,oParentScreenPage=oParentScreenPage ,uAnchor=uAnchor)

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        aChilds:List[cWidgetBase]
        aChilds:cWidgetBase
        aCaptions:List[str]
        self.iNumRows = 1

        if super().Create(oParent):
            self.CreateScrollList()
            return True
        return False

    def GetChilds(self) -> List[cWidgetBase]:
        aRet:List[cWidgetBase] = []

        # in case of recreation: Lets add the childs to the list of Screenpage widgets
        for oChild in self.aChilds:
            self.oParentScreenPage.aWidgets.append(oChild)
        # and remove the from the local list
        del self.aChilds[:]

        # save a copy of the screenpage widgets locally and mark them for deletion
        for oWidget in self.oParentScreenPage.aWidgets:
            if oWidget.uContainer==self.uContainer and oWidget!=self:
                aRet.append(oWidget)
                self.aChilds.append(copy(oWidget))
                self.oParentScreenPage.aErrorWidgets.append(oWidget)
        return aRet

    def GetCaptions(self,aChilds:List[cWidgetBase]) -> List[List[Tuple[str,str]]]:
        aCaptions:List[List[Tuple[str,str]]] = []
        aTmp:List[Tuple]
        tItem: Tuple
        aChildCaptions: List[Tuple[str, str]]
        for oChild in aChilds:
            aChildCaptions = []
            if hasattr(oChild,'uOrgCaption'):
                if oChild.uOrgCaption.endswith("[])"):
                    aTmp = Var_GetArrayEx(uVarName=oChild.uOrgCaption[5:-1], iLevel=1, bSort=False)
                    for tItem in aTmp:
                        aChildCaptions.append((u"$var(" + tItem[0] + ")",tItem[1]))
                    self.iNumRows = max(self.iNumRows, len(aChildCaptions))
            aCaptions.append(aChildCaptions)
        return aCaptions

    def CreateScrollList(self):
        aChilds:List[cWidgetBase]               = self.GetChilds()
        aCaptions:List[List[Tuple[str,str]]]    = self.GetCaptions(aChilds)
        self.iRowHeight                         = self.CalculateHeight(uHeight=self.uRowHeightInit, iAnchorHeight=self.iAnchorHeight)
        self.iRowHeightScreen                   = self.iRowHeight / self.oDef.fRationY
        self.oObjectScroll                      = ScrollView(size=self.oObject.size, pos=self.oObject.pos, do_scroll_x=False, scroll_type=['bars', 'content'], size_hint=(1, None), bar_width='10dp')
        self.oObjectContent                     = Widget(size=(self.oObject.width, self.iRowHeightScreen * self.iNumRows), size_hint=(1, None))
        self.oObject.add_widget(self.oObjectScroll)
        self.oObjectScroll.add_widget(self.oObjectContent)
        self.CreateChilds(aChilds, aCaptions)

    def DeleteScrollList(self):
        self.DeleteChilds()
        self.oObjectScroll.remove_widget(self.oObjectContent)
        self.oObject.remove_widget(self.oObjectScroll)

    def CreateChilds(self,aChilds:List[cWidgetBase],aCaptions:List[List[Tuple[str,str]]]):
        iIndex:int
        iSubIndex: int
        yPos:int
        iAdd:int
        uVarIndex:str
        dTmpdActionPars:Dict = {}

        for u in range(self.iNumRows):
            iIndex = 0
            uVarIndex = u'' # by purpose, we don't set it by child, we use the last known index, in case we have widgets without vars eg Buttons
            for oChild in aChilds:

                if hasattr(oChild,"dActionPars"):
                    dTmpdActionPars         = CopyDict(oChild.dActionPars)
                oTmpChild               = copy(oChild)
                oTmpChild.uName          = "%s[%s]" % (oTmpChild.uName, str(u))
                oTmpChild.iHeightInit   = self.iRowHeight * (oChild.iHeightInit/oChild.iAnchorHeight)
                oTmpChild.iPosXInit     = oTmpChild.iPosXInit - self.iPosXInit
                oTmpChild.iGapY         = (self.iPosY *-1) + (self.iRowHeightScreen * (u + 0))

                if len(aCaptions[iIndex]) > u:
                    if hasattr(oTmpChild,"uCaption"):
                        oTmpChild.uOrgCaption   = aCaptions[iIndex][u][0]
                        oTmpChild.uCaption      = ReplaceVars(aCaptions[iIndex][u][0])
                        uVarIndex               = ReplaceVars(aCaptions[iIndex][u][1])
                oTmpChild.Create(self.oObjectContent)

                if hasattr(oTmpChild,"dActionPars"):
                    try:
                        oTmpChild.dActionPars["SCROLLLISTVALUE"] = oTmpChild.oObject.text
                    except:
                        oTmpChild.dActionPars["SCROLLLISTVALUE"] = ""
                    oTmpChild.dActionPars["SCROLLLISTINDEX"]     = str(u)
                    oTmpChild.dActionPars["SCROLLLISTVARINDEX"]  = uVarIndex

                self.aListChilds.append(oTmpChild)
                self.oParentScreenPage.aAddWidgets.append(oTmpChild)
                oChild.dActionPars=dTmpdActionPars
                iIndex += 1

    def DeleteChilds(self):
        for oChild in self.aListChilds:
            self.oParentScreenPage.aWidgets.remove(oChild)
            self.oObjectContent.remove_widget(oChild.oObject)
        del self.aListChilds[:]
        self.iNumRows = 0

    def UpdateWidget(self) -> None:

        super().UpdateWidget()
        if self.oObjectScroll is not None:
            self.DeleteScrollList()
            self.CreateScrollList()
            self.oParentScreenPage.PostHandleErrorWidgets()
        return
