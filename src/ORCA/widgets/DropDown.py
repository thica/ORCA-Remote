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

from typing                             import List
from typing                             import Union
from copy                               import copy
from xml.etree.ElementTree              import Element
from kivy.uix.dropdown                  import DropDown

from kivy.uix.widget                    import Widget
from ORCA.widgets.helper.HexColor       import GetColorFromHex
from ORCA.widgets.helper.HexColor       import aColorUndefined
from ORCA.widgets.Button                import cWidgetButton
from ORCA.widgets.core.TouchRectangle   import cTouchRectangle
from ORCA.utils.LogError                import LogError
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.vars.Actions                  import Var_GetArray
from ORCA.utils.XML                     import GetXMLBoolAttribute
from ORCA.utils.XML                     import GetXMLTextAttribute
from ORCA.utils.Path                    import cPath

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")

__all__ = ['cWidgetDropDown']


# noinspection PyUnresolvedReferences
class cWidgetDropDown(cWidgetButton):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-DROPDOWN
    WikiDoc:TOCTitle:DropDown
    = DROPDOWN =

    The dropdown list widget is one of the core widgets. It is based on a button widget, which adds further option buttons linked to the button, when the button is clicked
    If you press a button from the options buttons, an action is triggered
    The "DROPDOWNVALUE" value is added to the action pars which refers to the button text
    The "DROPDOWNINDEX" index is added to the action pars which refers to the button order, eg: "0" is the first button in the list

    The button widget shares the common widget attributes and the button widget attributes.
    The following attributes are additional attributes to button widget attributes:
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "DROPDOWN". Capital letters!
    |-
    |captions
    |List of captions for all option buttons. This is a comma separated list. You can pass $DIRLIST[mypath] as captions, which then expands to the list of folders within that path. You can pass an array of variables as well. In this case, you need to pass the variable name (without $var() (MyBottonText:::Myarray[]). Each of the elements will be seen as a variable, which will be expanded at runtime
    |-
    |actions
    |List of actions for each option button. This is a comma separated list. This list must match the numer of captions. If you do not want to bind a caption, leave it as a comma seperated empty list (e.g. ",,,,"). If you pass only one action, than this will be called for all events. In all cases, a function var will be passed with the value of the selected option. (eg. MYACTION_parameter_DROPDOWNVALUE)
    |-
    |framecolor
    |If you want a colored frame around the dropdown, this specifies the frame color.
    |-
    |framewidth
    |If you want a colored frame around the dropdown, this specifies the frame width, either in relative pixels or in percentage, If not given, a defult vaule will be used
    |-
    |sorted
    |(0/1) If set, the captions of the dropdown will be sorted, It will not sorte the actions, so use it only if you use the same action for each item

    |}</div>

    Below you see an example for a dropdown widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="Dropdown" type="DROPDOWN" fontsize='%h50' caption='My Dropdown' captions='Option 1,Option 2,Option 3,Option 4' actions=',,,' htextalign='center' vtextalign='middle' picturenormal="button wide*" framecolor='$var(dimmed)' framewidth='500'/>
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.oDropDownButtons:List[cWidgetButton]   = []
        self.aCaptions:List[str]                    = []
        self.aSecondCaptions:List[str]              = []
        self.uOrgCaptions:str                       = u''
        self.aOrgActionNames:List[str]              = []
        self.aActionNames:List[str]                 = []
        self.oObjectDropDown:Union[DropDown,None]   = None
        self.oDimmer:Union[cTouchRectangle,None]    = None
        self.iFrameWidth:int                        = 0
        self.uActionNames:str                       = u''
        self.aFrameColor:List[float]                = aColorUndefined
        self.bSorted:bool                           = False
        self.oXMLNode:Union[Element,None]           = None
        self.iTmpAnchorWidth:int                    = 0
        self.iTmpAnchorHeight:int                   = 0

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:

        uCaption:str = GetXMLTextAttribute(oXMLNode, "caption",False,"")
        bRet:bool    = super().InitWidgetFromXml(oXMLNode,oParentScreenPage, uAnchor)
        bDummy:bool

        oXMLNode.set("caption", uCaption)

        if bRet:
            self.aFrameColor        = GetColorFromHex(GetXMLTextAttribute(oXMLNode,u'framecolor',False,u'$var(dimmed)'))
            uFramewidth:str         = GetXMLTextAttribute(oXMLNode,u'framewidth',  False,str(int((self.oDef.iDefMaxX/self.fRationX)*0.02)))
            self.iFrameWidth,bDummy = self.CalculateWidth(uWidth=uFramewidth,iAnchorWidth=self.iWidth)
            self.iFrameWidth        = self.iFrameWidth / self.fRationX
            self.aCaptions          = GetXMLTextAttribute(oXMLNode,u'captions', False,u'unknown').split(u',')
            self.aActionNames       = GetXMLTextAttribute(oXMLNode,u'actions',  False,u'').split(u',')
            self.aOrgActionNames    = copy(self.aActionNames)
            self.bSorted            = GetXMLBoolAttribute(oXMLNode,u'sorted',   False,False)
            self.oXMLNode           = oXMLNode

            # this is a little bit tricky
            # we should parse all dropdown button here as well, but then,
            # updatewidget for the dropdown would not work
            # so we do it in create, but at that time, the dimensions of the achor is lost
            # so, we need to save the anchor dimensions here
            self.iTmpAnchorWidth = self.oTmpAnchor.iWidth
            self.iTmpAnchorHeight = self.oTmpAnchor.iHeight
        return bRet

    def Create(self, oParent: Widget) -> bool:

        del self.oDropDownButtons[:]

        try:
            self.GetCaptions()
            if self.GetActions():
                for num in range(len(self.aCaptions)):
                    oBtn:cWidgetButton = cWidgetButton()
                    # we cant use the touchbutton object, as Buttonbehaviour not work on buttons on scolllayout
                    #oBtn.ClassName           = Button
                    oBtn.bIsDropButton        = True
                    self.oXMLNode.set("caption",self.aCaptions[num])
                    self.oXMLNode.set("type","BUTTON")
                    # self.oXMLNode.set("action", self.aActionNames[num])
                    self.oXMLNode.set("action", "NoAction")

                    if self.uAnchorName:
                        oTmpAnchor = self.oParentScreenPage.dWidgets[self.uAnchorName][0]
                        oTmpAnchor.iWidth  = self.iTmpAnchorWidth
                        oTmpAnchor.iHeight = self.iTmpAnchorHeight

                    oBtn.InitWidgetFromXml(self.oXMLNode, self.oParentScreenPage, self.uAnchorName)
                    # oBtn.SetCaption(self.aCaptions[num])
                    oBtn.iAnchorPosX          = 0
                    oBtn.iAnchorPosY          = 0
                    oBtn.iPosX                = 0
                    oBtn.iPosY                = 0
                    oBtn.uActionNameDoubleTap = u''
                    oBtn.uActionNameDownOnly  = u''
                    oBtn.uActionNameUpOnly    = u''
                    oBtn.uActionNameLongTap   = u''
                    oBtn.iButtonNum           = num

                    self.oDropDownButtons.append(oBtn)

            if self.oObjectDropDown is None:
                super(cWidgetDropDown, self).Create(oParent)

            if self.oObject is not None:
                self.oObjectDropDown=DropDown()
                #self.dismiss_on_select=True

                if self.bSorted:
                    self.oDropDownButtons = sorted(self.oDropDownButtons, key=lambda oDropDownButtons: ReplaceVars(oDropDownButtons.uCaption))

                for oWidget in self.oDropDownButtons:
                    oWidget.Create(oParent)
                    oWidget.oObject.size        = self.oObject.size
                    oWidget.oObject.text_size   = self.oObject.text_size

                    if oWidget.bIcon and self.bIcon:
                        oWidget.oObject.font_size = self.oObject.font_size

                    if (not oWidget.bIcon) and (not self.bIcon):
                        oWidget.oObject.font_size = self.oObject.font_size

                    oWidget.uName                = "*DROPDOWNBUTTON*"+oWidget.uName
                    oBtn                        = oWidget.oObject
                    oWidget.oParent.remove_widget(oBtn)
                    oBtn.size_hint_y            = None
                    oBtn.unbind(on_q_release    = oWidget.On_Button_Up)
                    oBtn.bind(on_q_release      = self.DropDownSelect)
                    self.oObjectDropDown.add_widget(oBtn)
                self.oObject.bind(on_q_release  = self.OpenDropDown)
                self.oObjectDropDown.bind(on_dismiss = self.CloseDropDown)
                return True
            return False
        except Exception as e:
            LogError(uMsg="Can''t create Dropdown",oException=e)
            return False

    def GetActions(self) -> bool:
        if len(self.aActionNames) == 1 and len(self.aCaptions) > 1:
            # noinspection PyUnusedLocal
            self.aActionNames = [self.aActionNames[0] for x in range(len(self.aCaptions))]

        if self.uActionNameLongTap == u"":
            self.uActionNameLongTap = "noaction"

        if len(self.aActionNames) != len(self.aCaptions) and len(self.aCaptions) > 0:
            LogError(uMsg=u'cWidgetDropDown: [%s] Captions do not match Actions: %s' % (self.uName, self.uActionName))
            return False
        else:
            return True

    def GetCaptions(self) -> None:
        aCaptions: List[str]
        uCaptions: str

        del self.oDropDownButtons[:]
        if self.uCaption.endswith("[]"):
            aCaptions           = self.uCaption.split(u':::')
            self.uCaption       = aCaptions[0]
            uCaptions           = aCaptions[1]
            self.aCaptions      = Var_GetArray(uCaptions , 1)
            self.aCaptions      = [u"$var("+item+")" for item in self.aCaptions]
        elif u':::' in self.uCaption:
            aCaptions           = self.uCaption.split(u':::')
            self.uCaption       = aCaptions[0]
            self.aCaptions      = aCaptions[1:]
            self.aActionNames   = ReplaceVars(self.uActionName).split(u':::')
            self.uActionName    = u''
            super(cWidgetButton, self).SetCaption(self.uCaption)
        else:
            if self.aCaptions[0].startswith("$DIRLIST["):
                oPath:cPath = cPath(self.aCaptions[0][9:-1])
                self.aCaptions = oPath.GetFolderList()

    # noinspection PyUnusedLocal
    def OpenDropDown(self,instance:DropDown) -> None:
        """ opens the dropdown """
        Object=self.oObjectDropDown
        Object.open(self.oObject)
        self.oDimmer=cTouchRectangle(pos=(Object.pos[0]-self.iFrameWidth,Object.pos[1]-self.iFrameWidth),width=Object.width+self.iFrameWidth*2,height=Object.height+self.iFrameWidth*2,background_color=self.aFrameColor)
        self.oParent.add_widget(self.oDimmer)

    # noinspection PyUnusedLocal
    def CloseDropDown(self,instance:DropDown) -> None:
        """ closes the dropdown """
        self.oParent.remove_widget(self.oDimmer)

    def DropDownSelect(self,instance:DropDown) -> None:
        """ selects on item of dropdown """
        #self.SetCaption(instance.text)
        self.oObjectDropDown.dismiss()
        instance.oOrcaWidget.dActionPars["DROPDOWNVALUE"] = instance.text
        instance.oOrcaWidget.dActionPars["DROPDOWNINDEX"] = str(instance.oOrcaWidget.iButtonNum)
        instance.oOrcaWidget.uActionName = self.aActionNames[instance.oOrcaWidget.iButtonNum]
        instance.uTapType="down"
        instance.oOrcaWidget.On_Button_Down(instance)
        return

    def UpdateWidget(self) -> None:
        self.uCaption     = ReplaceVars(self.uOrgCaption)
        self.aActionNames = copy(self.aOrgActionNames)
        if self.oObject:
            self.Create(self.oParent)
        return

    def UpdateWidgetSecondCaption(self) -> None:
        uCaption:str = ReplaceVars(self.uOrgSecondCaption)
        if uCaption == u'':
            return
        self.uCaption = uCaption
        if self.oObject:
            self.Create(self.oParent)
        cWidgetButton.SetCaption(self,self.uCaption)
        return

