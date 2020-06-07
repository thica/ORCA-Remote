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

from typing                             import Optional
from typing                             import Union
from typing                             import List
from typing                             import cast

from kivy.logger                        import Logger

from ORCA.Action                        import cAction
from ORCA.ScreenPage                    import cScreenPage
from ORCA.actions.Base                  import cEventActionBase
from ORCA.actions.ReturnCode            import eReturnCode
from ORCA.definition.Definition         import cDefinition
from ORCA.ui.ShowErrorPopUp             import ShowErrorPopUp
from ORCA.utils.FileName                import cFileName
from ORCA.utils.LogError                import LogError
from ORCA.utils.TypeConvert             import ToBool
from ORCA.utils.TypeConvert             import ToFloat
from ORCA.utils.TypeConvert             import ToUnicode
from ORCA.vars.Access                   import SetVar
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.widgets.base.Base             import cWidgetBase
from ORCA.widgets.Button                import cWidgetButton
from ORCA.widgets.Circle                import cWidgetCircle
from ORCA.widgets.Knob                  import cWidgetKnob
from ORCA.widgets.Picture               import cWidgetPicture
from ORCA.widgets.Slider                import cWidgetSlider
from ORCA.widgets.Switch                import cWidgetSwitch
from ORCA.widgets.Video                 import cWidgetVideo
from ORCA.widgets.helper.WidgetType     import eWidgetType

import ORCA.Globals as Globals

__all__ = ['cEventActionsWidgetControl']

class cEventActionsWidgetControl(cEventActionBase):
    """ Actions for manipulating widgets """

    def ExecuteActionLoadElement(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-LoadElement
        WikiDoc:TOCTitle:loadelement
        = loadelement =
        Loads a given xml element at runtime. Helpful to adjust pages based on given conditions. Needs to happen, before the page has been initalized.
        Experimental: Loading (not replacing) is supported after page intialisizing as well

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |loadelement
        |-
        |filename
        |Filename to load. Can contain variables: eg: $var(STANDARDELEMENTSPATH)/block_topline.xml. The xml file must follow proper xml syntax
        |-
        |pagename
        |Pagename, to which the element should be added
        |-
        |anchor
        |Optional: Anchor within the page, where the element should be added to.
        |-
        |definitionvarcontext
        |Optional: The definitioncontext (definitionvars)  to be used. If not given, the context of the page is used
        |-
        |widgetname
        |If given, the loaded element will use size and prosition of the element with this name. Only the first element of the included xml element will be used. The original widget will be removed.
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="Add Topline" string="loadelement" filename="$var(STANDARDELEMENTSPATH)/block_topline.xml" pagename="Page_Device_Page_Device_$dvar(definition_alias_mediaplayer_template)_Net" />
        <action name="replace one of the buttons with the back button Button" string="loadelement" filename="$var(DEFINITIONPATH)/block_returntofiretv.xml" pagename="Page_Device_$dvar(definition_alias_mediaplayer_kodi)" widgetname="Button Power On"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'LoadElement',oAction=oAction)
        oDef:Optional[cDefinition] = None
        uFnElement: str
        oFileRedirect: cFileName

        uFnElement = oAction.dActionPars.get("filename","")
        ' twice by purpose'
        oFileRedirect = Globals.oTheScreen.oSkin.dSkinRedirects.get((cFileName('').ImportFullPath(uFnFullName=ReplaceVars(uFnElement))).string)
        if oFileRedirect is not None:
            uFnElement = oFileRedirect.string
        uFnElement = ReplaceVars(uFnElement)
        oFileRedirect = Globals.oTheScreen.oSkin.dSkinRedirects.get((cFileName('').ImportFullPath(uFnFullName=uFnElement)).string)
        if oFileRedirect is not None:
            uFnElement = oFileRedirect.string

        uPage:str                   = ReplaceVars(oAction.dActionPars.get("pagename",""))
        uAnchor:str                 = ReplaceVars(oAction.dActionPars.get("anchor",""))
        uWidgetName:str             = ReplaceVars(oAction.dActionPars.get("widgetname",""))
        uDefinitionVarContext:str   = oAction.dActionPars.get("definitionvarcontext",None)
        oPage:cScreenPage           = Globals.oTheScreen.oScreenPages.get(uPage)

        if uDefinitionVarContext is not None:
            oDef=Globals.oDefinitions[uDefinitionVarContext]
            if oDef is None:
                LogError(uMsg=u'Action: loadelelement: Can''t find Definition:'+uDefinitionVarContext)

        if oPage is None:
            LogError(uMsg=u'Action: LoadElement: Wrong page name:'+uPage )
            Globals.oTheScreen.DumpPages()
            return eReturnCode.Error
        if oPage.bIsInit and uWidgetName!='':
            LogError(uMsg=u'Action: LoadElement: Can''t replace elements of initialized page:'+uPage )
            return eReturnCode.Error
        if uWidgetName=='':
            if oPage.LoadElement(uFnElement=uFnElement, uAnchor=uAnchor, oDefinition=oDef):
                return eReturnCode.Success
            else:
                return eReturnCode.Error

        else:
            if oPage.ReplaceElement(uFnElement=uFnElement, uReplaceWidgetName=uWidgetName,oDefinition=oDef):
                return eReturnCode.Success
            else:
                return eReturnCode.Error


    def ExecuteActionUpdateWidget(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-UpdateWidget
        WikiDoc:TOCTitle:updatewidget
        = updatewidget =
        Updates the widget. For BUTTONs and TEXTFIELDs the caption is updated. Usefull, if the caption is bound to a variable. For KNOBs  this is the data value, bound to the KNOBs. The knob turns into the updated value of the variable.
        There are two special , reserved widgetnames:

        * {pageclocks}: Updates all clock widgets on the current page
        * {pagewidgets}: Updates all widgets  on the current page

        This action will not modify the error code
        You also could use a short form, where the widgetname is added directly to the string. eg. string="updatewidget Message Wait@Page_Wait_For_Device"

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |updatewidget
        |-
        |widgetname
        |Name of the widget to update
        could be on of the following:
            "{pageclocks}", updates all clock widgets
            widgetname: the name of the widget on the current page
            widgetname@pagename the name of the widget on a given pagename
            for widgetname and pagename a "*" could be used to either cover all widgets or all pages
            e.g.: *@* updates all widgets on all pages
        |-
        |option
        |some widgets supports a second update option. For widgets with text this could be "second" to set the second caption
        |-
        |ignoremissing
        |Dont raise an error if widget is missing
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="update wait message" string="updatewidget" widgetname="Message Wait@Page_Wait_For_Device" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.bDoNext = False
        uWidgetName:str               = ReplaceVars(oAction.dActionPars.get("widgetname",""))
        uOption:str                   = ReplaceVars(oAction.dActionPars.get("option",""))
        bIgnoreMissing:bool           = ToBool(ReplaceVars(oAction.dActionPars.get("ignoremissing","0")))
        iDateWidgetIndex:int
        oWidget:cWidgetBase
        aWidgets:List[cWidgetBase]

        if uWidgetName==u'{pageclocks}':
            SetVar(u'LOCALTIME', Globals.oLanguage.GetLocalizedTime(Globals.bClockWithSeconds))
            if Globals.oTheScreen.oCurrentPage is not None:
                for iClockWidgetIndex in Globals.oTheScreen.oCurrentPage.aClockWidgetsIndex:
                    if iClockWidgetIndex < len(Globals.oTheScreen.oCurrentPage.aWidgets):
                        Globals.oTheScreen.oCurrentPage.aWidgets[iClockWidgetIndex].UpdateWidget()
                    else:
                        LogError(uMsg="UpdateWidget: wrong index:[%s][%d]" % (Globals.oTheScreen.oCurrentPage.uPageName,iClockWidgetIndex))
            return eReturnCode.Nothing

        if uWidgetName==u'{pagedates}':
            SetVar(u'LOCALDATE', Globals.oLanguage.GetLocalizedDate(Globals.bLongDate, Globals.bLongMonth, Globals.bLongDay))
            if Globals.oTheScreen.oCurrentPage is not None:
                for iDateWidgetIndex in Globals.oTheScreen.oCurrentPage.aDateWidgetsIndex:
                    if iDateWidgetIndex < len(Globals.oTheScreen.oCurrentPage.aWidgets):
                        Globals.oTheScreen.oCurrentPage.aWidgets[iDateWidgetIndex].UpdateWidget()
                    else:
                        LogError(uMsg="UpdateWidget: wrong index:[%s][%d]" % (Globals.oTheScreen.oCurrentPage.uPageName,iDateWidgetIndex))
            return eReturnCode.Nothing

        self.oEventDispatcher.LogAction(uTxt=u'UpdateWidget',oAction=oAction)
        if oAction.oParentWidget is None:
            oParentScreenPage=Globals.oTheScreen.oCurrentPage
        else:
            oParentScreenPage=oAction.oParentWidget.oParentScreenPage

        aWidgets = Globals.oTheScreen.FindWidgets(uPageName=oParentScreenPage.uPageName,uWidgetName=uWidgetName, bIgnoreError=bIgnoreMissing)
        if len(aWidgets)>0:
            for oWidget in aWidgets:
                if uOption == u'':
                    oWidget.UpdateWidget()
                elif uOption == "second":
                    oWidget.UpdateWidgetSecondCaption()
        else:
            if not bIgnoreMissing:
                Logger.warning("UpdateWidget: wrong widget name:[%s][%s]" % (oParentScreenPage.uPageName, uWidgetName))
        return eReturnCode.Nothing

    def ExecuteActionAddGesture(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-AddGesture
        WikiDoc:TOCTitle:addgesture
        = addgesture =
        Adds a gesture to the background or a widget. Currently no widgets are supported, but you can add gestures to the background. You can add multiple gestures. For backgrounds , you should add gestures in the pagestartactions for the specific page. You can not assign gestures in the appstart or definitionstart sections. You can set the Interface / Configuration name as well.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |addgesture
        |-
        |widgetname
        |Name of the widget to add the gesture, could be Background to add a gesture to the screen
        |-
        |gesturename
        |Name of the gesture, which should be added. Must e name of a standard gesture, or a gesture name from the definition
        |-
        |actionname
        |Action to execute, when the gesture is recognized
        |}</div>

        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="addgesture" widgetname="Background" gesturename="$var($dvar(definition_alias_mediaplayer_template)_GESTURENAME[9])"    actionname="$var($dvar(definition_alias_mediaplayer_template)_GESTUREACTION[9])"  interface="$var($dvar(definition_alias_mediaplayer_template)_INTERFACE_MAIN)" configname="$var($dvar(definition_alias_mediaplayer_template)_CONFIGNAME_MAIN)" condition="$var($dvar(definition_alias_mediaplayer_template)_GESTUREACTION[9])!=NoAction"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'AddGestures',oAction=oAction)
        uWidgetName:str    = ReplaceVars(oAction.dActionPars.get("widgetname",""))
        uGestureName:str   = ReplaceVars(oAction.dActionPars.get("gesturename",""))
        uActionName:str    = ReplaceVars(oAction.dActionPars.get("actionname",""))
        oWidget:cWidgetBase

        if uWidgetName==u'Background':
            oBackGround=Globals.oTheScreen.oCurrentPage.oWidgetBackGround
            oBackGround.oObject.AddGesture(uGestureName,uActionName,oAction.dActionPars.get(u'interface',u''),oAction.dActionPars.get(u'configname',u''))
            return eReturnCode.Nothing
        aWidgets:List[cWidgetBase] = Globals.oTheScreen.FindWidgets(uPageName = oAction.oParentWidget.oParentScreenPage.uPageName,uWidgetName = uWidgetName)
        for oWidget in aWidgets:
            oWidget.oObject.AddGesture(uGestureName,uActionName)
        return eReturnCode.Nothing

    def ExecuteActionSetWidgetAttribute(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-SetWidgetAttribute
        WikiDoc:TOCTitle:setwidgetattribute
        = setwidgetattribute =
        Sets / changes some attributes of a TEXTFIELD , BUTTON, PICTURE, RECTANGLE, CIRCLE widget.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |setwidgetattribute
        |-
        |widgetname
        |Name of the widget, which attribute should be change
        |-
        |attributename
        |Name of the attribute to change. You can set the following attributes:
        *'bold': Changes the font to bold or not to bold (0/1)
        *'italic': Changes the font to italic or not to italic (0/1)
        *'textcolor': Sets the text color (hex RGBA)
        *'caption': Sets the caption of text
        *'fontsize': Sets the font size of text
        *'enable': Enable/Disables a widget (0/1)
        *'remove': Removes the widget from the page
        *'setfocus': Sets the focus to a widget. Used only for INPUTFIELDS to bring the keyboard to front
        *'picturenormal': Sets the picture of a BUTTON or PICTURE. For a BUTTON, this is the standard picture.
        *'picturepressed': Sets the pressed picture of a BUTTON.
        *'color': Sets the background color (hex RGBA), (RECTANGLE, CIRCLE only)
        *'transparency': Sets the transparency of a widget
        *'allbuttonsoff': Disables all buttons of a button group (SWITCH only)
        *'action': Sets the action of a widget
        *'startangle': For Circles: The start angle of the circle
        *'endangle': For Circles: The end angle of the circle
        *'min': For Knobs and Sliders: Sets the min value
        *'max': For Knobs and Sliders: Sets the max value
        *'filename': For Video: Sets the video filename/url
        |-
        |attributevalue
        |New Value of the attribute
        |-
        |touchtype
        |For action attribute: the touch type of the action
        * (nothing = Standard action)
        * Other options are 'double', 'up', 'down'
        |-
        |autoupdate
        |Calls UpdateWidget, after setting the new attribute
        |-
        |ignoremissing
        |Dont raise an error if widget is missing
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="wait some time" string="wait" time="500" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'SetWidgetAttribute',oAction=oAction)

        uWidgetName:str       = ReplaceVars(oAction.dActionPars.get("widgetname",""))
        uAttributeName:str    = ReplaceVars(oAction.dActionPars.get("attributename",""))
        uAttributeValue:str   = ReplaceVars(oAction.dActionPars.get("attributevalue",""))
        uTouchType:str        = ReplaceVars(oAction.dActionPars.get("touchtype",""))
        uAutoUpDate:str       = ReplaceVars(oAction.dActionPars.get("autoupdate",""))
        bIgnoreMissing:bool   = ToBool(ReplaceVars(oAction.dActionPars.get("ignoremissing","0")))
        oWidget:cWidgetBase
        uPageName:str
        bRet:bool
        aWidgets:List[cWidgetBase]

        self.oEventDispatcher.bDoNext = False
        try:
            uPageName = u''
            if oAction.oParentWidget is not None:
                uPageName = oAction.oParentWidget.oParentScreenPage.uPageName

            aWidgets = Globals.oTheScreen.FindWidgets(uPageName = uPageName,uWidgetName = uWidgetName, bIgnoreError=bIgnoreMissing)
            for oWidget in aWidgets:
                bRet = True
                if uAttributeName==u'bold':
                    bRet = oWidget.SetWidgetFontStyle(uAttributeValue=='1',None,None)
                elif uAttributeName==u'italic':
                    bRet = oWidget.SetWidgetFontStyle(None,uAttributeValue=='1',None)
                elif uAttributeName==u'textcolor':
                    bRet = oWidget.SetWidgetFontStyle(None,None,uAttributeValue)
                elif uAttributeName==u'caption':
                    bRet =  oWidget.SetCaption(uAttributeValue)
                elif uAttributeName==u'fontsize':
                    oWidget.oObject.font_size = uAttributeValue
                    bRet = True
                elif uAttributeName==u'picturenormal':
                    if oWidget.eWidgetType == eWidgetType.Picture or oWidget.eWidgetType == eWidgetType.Button or oWidget.eWidgetType == eWidgetType.Switch:
                        bRet = cast(Union[cWidgetPicture, cWidgetButton, cWidgetSwitch],oWidget).SetPictureNormal (uAttributeValue,True)
                elif uAttributeName==u'picturepressed':
                    if oWidget.eWidgetType == eWidgetType.Picture or oWidget.eWidgetType == eWidgetType.Button  or oWidget.eWidgetType == eWidgetType.Switch:
                        bRet = cast(Union[cWidgetPicture, cWidgetButton, cWidgetSwitch],oWidget).SetPicturePressed (uAttributeValue)
                elif uAttributeName==u'color':
                    bRet = oWidget.SetWidgetColor (uAttributeValue)
                elif uAttributeName==u'transparancy':
                    bRet = oWidget.SetTransparancy (ToFloat(uAttributeValue))
                elif uAttributeName==u'filename':
                    if oWidget.eWidgetType == eWidgetType.Video:
                        bRet = cast(cWidgetVideo,oWidget).SetFileName(uAttributeValue)
                elif uAttributeName==u'enable':
                    bRet =  oWidget.EnableWidget(bEnable=(uAttributeValue==u'1'))
                elif uAttributeName==u'remove':
                    bRet =  oWidget.oParentScreenPage.RemoveWidget(oWidget=oWidget)
                elif uAttributeName==u'setfocus':
                    bRet =  oWidget.SetFocus()
                elif uAttributeName==u'allbuttonsoff':
                    if oWidget.eWidgetType==eWidgetType.Switch:
                        cast(cWidgetSwitch,oWidget).AllButtonsOff()
                elif uAttributeName==u'startangle':
                    if oWidget.eWidgetType==eWidgetType.Circle:
                        cast(cWidgetCircle,oWidget).fStartAngle=ToFloat(uAttributeValue)
                elif uAttributeName==u'endangle':
                    if oWidget.eWidgetType==eWidgetType.Circle:
                        cast(cWidgetCircle,oWidget).fEndAngle=ToFloat(uAttributeValue)
                elif uAttributeName==u'min':
                    if oWidget.eWidgetType==eWidgetType.Knob or oWidget.eWidgetType==eWidgetType.Slider:
                        cast(Union[cWidgetKnob, cWidgetSlider],oWidget).SetMin(ToFloat(uAttributeValue))
                elif uAttributeName==u'max':
                    if oWidget.eWidgetType==eWidgetType.Knob or oWidget.eWidgetType==eWidgetType.Slider:
                        cast(Union[cWidgetKnob, cWidgetSlider],oWidget).SetMax(ToFloat(uAttributeValue))
                elif uAttributeName==u'action':
                    self.oEventDispatcher.bDoNext = True
                    oWidget.uActionString=uAttributeValue
                    if uTouchType=='':
                        oWidget.uActionName=uAttributeValue
                    elif uTouchType=='double':
                        oWidget.uActionNameDoubleTap=uAttributeValue
                    elif uTouchType=='up':
                        oWidget.uActionNameUpOnly=uAttributeValue
                    elif uTouchType=='down':
                        oWidget.uActionNameUpDownOnly=uAttributeValue
                    elif uTouchType=='long':
                        oWidget.uActionNameLong=uAttributeValue
                    else:
                        uMsg=u'Action: SetWidgetAttribute: Action not set %s %s %s :' % (uWidgetName,uAttributeName,uAttributeValue)
                        Logger.error (uMsg)
                        ShowErrorPopUp(uTitle='Warning',uMessage=uMsg)
                else:
                    uMsg=u'Action: SetWidgetAttribute: Attribute not Found %s %s' %(uWidgetName,uAttributeName)
                    Logger.error (uMsg)
                    ShowErrorPopUp(uTitle='Warning',uMessage=uMsg)
                    return eReturnCode.Error
                # Auto Update Widget
                if uAutoUpDate=='1':
                    bRet=(self.ExecuteActionUpdateWidget(oAction)==eReturnCode.Success)
                if bRet:
                    return eReturnCode.Success
                else:
                    return eReturnCode.Error
            return eReturnCode.Error
        except Exception as e:
            ShowErrorPopUp(uTitle='Warning',uMessage=LogError(uMsg='Action: SetWidgetAttribute: Could not set Attribute: %s:%s' % (uWidgetName,uAttributeName),oException=e))
            return eReturnCode.Error

    def ExecuteActionGetWidgetAttribute(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-GetWidgetAttribute
        WikiDoc:TOCTitle:getwidgetattribute
        = getwidgetattribute =
        Gets some attributes of widgets

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |getwidgetattribute
        |-
        |widgetname
        |Name of the widget, which attribute should be returned
        |-
        |attributename
        |Name of the attribute to return. You can get the following attributes:
        *'bold': Get the "bold" attribute of a font (0/1)
        *'italic': Get the "italic" attribute of a font (0/1)
        *'textcolor': Gets the text color (hex RGBA)
        *'fontsize': Gets the font size of text
        *'caption': Gets the caption of text
        *'enabled': Gets the Enable/Disable attribute of a widget (0/1)
        *'picturenormal': Gets the picture name of a BUTTON or PICTURE.
        *'picturepressed': Gets the pressed picture name of a BUTTON.
        *'color': Gets the background color (hex RGBA), (RECTANGLE, CIRCLE only)
        *'transparency': Gets the transparency of a widget
        *'action': Gets the action of a widget
        *'startangle': For Circles: Gets the start angle of the circe
        *'endangle': For Circles: Gets the end angle of the circe
        *'exists': Returns, if the widget exists (0/1)
        |-
        |retvar
        |the varname, which should hold the return value
        |-
        |ignoremissing
        |Dont raise an error if widget is missing
        |-
        |touchtype
        |For action attribute: the touch type of the action
        * (nothing = Standard action)
        * Other options are 'double', 'up', 'down'
        |}</div>
        A short example:
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'GetWidgetAttribute',oAction=oAction)

        uWidgetName:str       = ReplaceVars(oAction.dActionPars.get("widgetname",""))
        uAttributeName:str    = ReplaceVars(oAction.dActionPars.get("attributename",""))
        uRetVar:str           = ReplaceVars(oAction.dActionPars.get("retvar",""))
        # uTouchType:str        = ReplaceVars(oAction.dActionPars.get("touchtype",""))
        bIgnoreMissing:bool   = ToBool(ReplaceVars(oAction.dActionPars.get("ignoremissing","0")))

        uRet:str               = "error"
        eRet:eReturnCode       = eReturnCode.Success

        bIgnoreError:bool     = (uAttributeName == u'exists')
        oWidget:cWidgetBase
        aWidgets:List[cWidgetBase]

        try:
            uPageName:str=u''
            if oAction.oParentWidget is not None:
                uPageName=oAction.oParentWidget.oParentScreenPage.uPageName

            aWidgets=Globals.oTheScreen.FindWidgets(uPageName=uPageName,uWidgetName=uWidgetName, bIgnoreError=(bIgnoreError | bIgnoreMissing))
            if len(aWidgets)==1:
                oWidget=aWidgets[0]
                if uAttributeName==u'bold' or uAttributeName==u'italic' or uAttributeName==u'textcolor':
                    uRet = oWidget.GetWidgetFontStyle(uAttributeName)
                elif uAttributeName==u'caption':
                    uRet =  oWidget.GetCaption()
                elif uAttributeName==u'picturenormal':
                    if oWidget.eWidgetType == eWidgetType.Picture or oWidget.eWidgetType == eWidgetType.Button or oWidget.eWidgetType == eWidgetType.Switch:
                        uRet = cast(Union[cWidgetPicture, cWidgetButton, cWidgetSwitch],oWidget).oFnPictureNormal.string
                elif uAttributeName==u'picturepressed':
                    if oWidget.eWidgetType == eWidgetType.Button or oWidget.eWidgetType == eWidgetType.Switch:
                        uRet = cast(Union[cWidgetButton, cWidgetSwitch],oWidget).oFnButtonPicturePressed.string
                elif uAttributeName==u'color':
                    uRet =  oWidget.uBackGroundColor
                elif uAttributeName==u'fontsize':
                    uRet =  ToUnicode(oWidget.oObject.font_size)
                elif uAttributeName==u'transparancy':
                    uRet =  ToUnicode(oWidget.fOrgOpacity )
                elif uAttributeName==u'filename':
                    if oWidget.eWidgetType == eWidgetType.Video:
                        uRet =  cast(cWidgetVideo,oWidget).uFileName
                elif uAttributeName==u'enabled':
                    uRet = u"0"
                    if oWidget.bIsEnabled:
                        uRet= u"1"
                elif uAttributeName==u'startangle':
                    if oWidget.eWidgetType == eWidgetType.Circle:
                        uRet = ToUnicode(cast(cWidgetCircle,oWidget).fStartAngle)
                elif uAttributeName==u'endangle':
                    if oWidget.eWidgetType == eWidgetType.Circle:
                        uRet = ToUnicode(cast(cWidgetCircle,oWidget).fEndAngle)
                elif uAttributeName==u'action':
                    if hasattr(oWidget,"uActionName"):
                        uRet = oWidget.uActionName
                    else:
                        uRet = ""
                elif uAttributeName == u'exists':
                    uRet = "1"
                else:
                    uMsg=u'Action: GetWidgetAttribute: Attribute not Found %s %s' %(uWidgetName,uAttributeName)
                    Logger.error (uMsg)
                    ShowErrorPopUp(uTitle='Warning',uMessage=uMsg)
                    eRet = eReturnCode.Error
            else:
                if uAttributeName == u'exists':
                    uRet="0"
                else:
                    eRet = eReturnCode.Error

        except Exception as e:
            ShowErrorPopUp(uTitle='Warning',uMessage=LogError(uMsg='Action: GetWidgetAttribute: Could not set Attribut: %s:%s' % (uWidgetName,uAttributeName),oException=e))
            eRet = eReturnCode.Error

        SetVar(uRetVar,uRet)
        return eRet
