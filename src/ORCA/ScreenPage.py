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

from typing                         import Union
from typing                         import List
from typing                         import Dict
from typing                         import Callable
from typing                         import Tuple
from typing                         import Any

from collections                    import defaultdict
from xml.etree.ElementTree          import tostring
from xml.etree.ElementTree          import Element
from kivy.logger                    import Logger
from kivy.uix.screenmanager         import Screen
from kivy.uix.widget                import Widget

from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp
from ORCA.utils.CachedFile          import CachedFile
from ORCA.utils.LogError            import LogError
from ORCA.utils.wait.StopWait       import StopWait
from ORCA.utils.XML                 import GetXMLBoolValue
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import GetXMLTextValue
from ORCA.utils.XML                 import Orca_FromString
from ORCA.utils.XML                 import Orca_include
from ORCA.utils.XML                 import XMLPrettify
from ORCA.utils.XML                 import orca_et_loader
from ORCA.vars.Access               import SetVar
from ORCA.vars.Replace              import ReplaceDefVars
from ORCA.vars.Replace              import ReplaceVars
from ORCA.widgets.Anchor            import cWidgetAnchor
from ORCA.widgets.BackGround        import cWidgetBackGround
from ORCA.widgets.base.Base         import cWidgetBase
from ORCA.widgets.helper.WidgetType import eWidgetType
from ORCA.widgets.Button            import cWidgetButton
from ORCA.widgets.Circle            import cWidgetCircle
from ORCA.widgets.ColorPicker       import cWidgetColorPicker
from ORCA.widgets.DropDown          import cWidgetDropDown
from ORCA.widgets.FileBrowser       import cWidgetFileBrowser
from ORCA.widgets.FileViewer        import cWidgetFileViewer
from ORCA.widgets.Knob              import cWidgetKnob
from ORCA.widgets.Picture           import cWidgetPicture
from ORCA.widgets.Rectangle         import cWidgetRectangle
from ORCA.widgets.Settings          import cWidgetSettings
from ORCA.widgets.Slider            import cWidgetSlider
from ORCA.widgets.Switch            import cWidgetSwitch
from ORCA.widgets.TextField         import cWidgetTextField
from ORCA.widgets.TextInput         import cWidgetTextInput
from ORCA.widgets.Video             import cWidgetVideo
from ORCA.widgets.ScrollContainer   import cWidgetScrollContainer
from ORCA.widgets.Border            import cWidgetBorder
from ORCA.utils.FileName            import cFileName

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.definition.Definition import cDefinition
else:
    from typing import TypeVar
    cDefinition = TypeVar("cDefinition")


class cScreenPage:

    """
    Representation of a screen page and all it's widgets
    """

    def __init__(self):
        self.oWidgetBackGround:cWidgetBackGround               = cWidgetBackGround()
        self.oWidgetPictureTransmit:Union[cWidgetPicture,None] = None
        self.oWidgetPictureWait:Union[cWidgetPicture,None]     = None
        self.uHexBackGroundColor:str                           = u'#000000'
        self.uPageName:str                                     = u'NoName'
        #ordered array of widgets
        self.aWidgets:List[cWidgetBase]                        = []
        #indexed array of widgets
        self.dWidgets:defaultdict                              = defaultdict(list)
        #List of all widgets to remove after creation
        self.aErrorWidgets: List[cWidgetBase] = []
        #List of all widgets to add after creation
        self.aAddWidgets: List[cWidgetBase] = []


        self.iESCPressCount:int                                = 0

        self.aClockWidgetsIndex:List[int]                      = []
        self.aDateWidgetsIndex:List[int]                       = []
        self.dGestures:Dict                                    = {}
        self.bIsInit:bool                                      = False
        self.uDefaultInterface:str                             = u''
        self.uDefaultConfigName:str                            = u''
        self.dFktsCreateWidget:Dict[eWidgetType,Tuple[Callable,Any]]   = {}
        self.bIsPopUp:bool                                     = False
        self.bPreventPreInit:bool                              = False
        self.uCallingPageName:str                              = u''
        self.uCalledByPageName:str                             = u''

        #not used
        self.uOrientation:str                                  = u''

        # Embedded kivy Screen Object
        self.oScreen:Union[Screen,None]                        = None

        self.dFktsCreateWidget[eWidgetType.BackGround]       = self.AddWidgetFromXmlNode_BackGround, None
        self.dFktsCreateWidget[eWidgetType.TextField]        = self.AddWidgetFromXmlNode_Text, cWidgetTextField
        self.dFktsCreateWidget[eWidgetType.Anchor]           = self.AddWidgetFromXmlNode_Anchor, cWidgetAnchor
        self.dFktsCreateWidget[eWidgetType.Button]           = self.AddWidgetFromXmlNode_Class, cWidgetButton
        self.dFktsCreateWidget[eWidgetType.Switch]           = self.AddWidgetFromXmlNode_Class, cWidgetSwitch
        self.dFktsCreateWidget[eWidgetType.Picture]          = self.AddWidgetFromXmlNode_Class, cWidgetPicture
        self.dFktsCreateWidget[eWidgetType.TextInput]        = self.AddWidgetFromXmlNode_Class, cWidgetTextInput
        self.dFktsCreateWidget[eWidgetType.Knob]             = self.AddWidgetFromXmlNode_Class, cWidgetKnob
        self.dFktsCreateWidget[eWidgetType.FileViewer]       = self.AddWidgetFromXmlNode_Class, cWidgetFileViewer
        self.dFktsCreateWidget[eWidgetType.Slider]           = self.AddWidgetFromXmlNode_Class, cWidgetSlider
        self.dFktsCreateWidget[eWidgetType.Rectangle]        = self.AddWidgetFromXmlNode_Class, cWidgetRectangle
        self.dFktsCreateWidget[eWidgetType.Circle]           = self.AddWidgetFromXmlNode_Class, cWidgetCircle
        self.dFktsCreateWidget[eWidgetType.Video]            = self.AddWidgetFromXmlNode_Class, cWidgetVideo
        self.dFktsCreateWidget[eWidgetType.DropDown]         = self.AddWidgetFromXmlNode_Class, cWidgetDropDown
        self.dFktsCreateWidget[eWidgetType.ColorPicker]      = self.AddWidgetFromXmlNode_Class, cWidgetColorPicker
        self.dFktsCreateWidget[eWidgetType.Settings]         = self.AddWidgetFromXmlNode_Class, cWidgetSettings
        self.dFktsCreateWidget[eWidgetType.FileBrowser]      = self.AddWidgetFromXmlNode_Class, cWidgetFileBrowser
        self.dFktsCreateWidget[eWidgetType.ScrollContainer]  = self.AddWidgetFromXmlNode_Class, cWidgetScrollContainer
        self.dFktsCreateWidget[eWidgetType.Border]           = self.AddWidgetFromXmlNode_Class, cWidgetBorder
        self.dFktsCreateWidget[eWidgetType.NoWidget]         = self.AddWidgetFromXmlNode_None, None
        self.dFktsCreateWidget[eWidgetType.SkipWidget]       = self.AddWidgetFromXmlNode_Skip, None

    def InitPageFromXmlNode(self,oXMLNode:Element) -> None:
        """ Get Page Definitions """
        self.uPageName          = GetXMLTextAttribute(oXMLNode,u'name',True,u'')
        oRef:Element            = oXMLNode.find(u'page_parameter')
        self.uDefaultInterface  = GetXMLTextValue(oRef,u'interface',False,u'')
        self.uDefaultConfigName = GetXMLTextValue(oRef,u'configname',False,u'')
        self.bIsPopUp           = GetXMLBoolValue(oRef,u'popup',False,False)
        self.bPreventPreInit    = GetXMLBoolValue(oRef,u'preventpreinit',False,False)

        # ToDo: this is temporary to validate some strange default value changes
        self.uDefaultInterface  = ReplaceVars(self.uDefaultInterface)
        self.uDefaultConfigName = ReplaceVars(self.uDefaultConfigName)

        #not used
        self.uOrientation       = GetXMLTextValue(oRef,u'orientation',False,Globals.uDeviceOrientation)

        if not self.uDefaultInterface==u'':
            Globals.oInterFaces.dUsedInterfaces[ReplaceVars(self.uDefaultInterface)]=True

    def AddPageElementsFromXmlNode(self,oXMLNode:Element) -> None:
        """ Adds elements defined in an xml node"""

        self._AddElements(oXMLNode=oXMLNode, uAnchor=u'')

    def LoadElement(self,uFnElement:str, uAnchor:str, oDefinition:cDefinition) -> bool:
        """ Load an element at runtime to a page: the page must not be initalized
        :param str uFnElement: FileName of element to load
        :param str uAnchor: Target Anchor in Page to place the element into
        :param cDefinition oDefinition: Target Definition
        :return: True if successful, otherwise False

        """

        oFnElement:cFileName
        uET_Data:str
        oET_Root:Element
        oWidget:cWidgetBase

        try:
            oFnElement=cFileName('').ImportFullPath(uFnElement)
            SetVar(uVarName = 'ORCA_INCLUDEFILE', oVarValue = oFnElement.string)
            if oDefinition is None:
                oDef=self.oWidgetBackGround.oDef
            else:
                oDef=oDefinition
            uET_Data = CachedFile(oFileName=Globals.oFnElementIncludeWrapper)
            uET_Data = ReplaceDefVars(uET_Data,oDef.oDefinitionVars)
            oET_Root = Orca_FromString(uET_Data,oDef,oFnElement.string)
            Orca_include(oET_Root,orca_et_loader)
            oWidget=self._AddElements(oXMLNode=oET_Root, uAnchor=uAnchor)
            if self.bIsInit:
                if oWidget is not None:
                    oWidget.Create(self.oWidgetBackGround.oObject)
            return True
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg="Can''t load element: %s:" % uFnElement,oException=e))
            return False

    def ReplaceElement(self,uFnElement:str, uReplaceWidgetName:str,oDefinition:cDefinition) -> bool:
        """ Replaces an element at runtime in a page: the page must not be initalized
        :param str uFnElement: FileName of element to load
        :param str uReplaceWidgetName: The Widgetname to be replaced
        :param cDefinition oDefinition: Target Definition
        :return: True if successful, otherwise False

        """

        uFnFile:str = ''
        oDef:cDefinition
        uET_Data:str
        oET_Root:Element

        try:
            uFnFile=(cFileName(u'').ImportFullPath(uFnElement)).string
            SetVar(uVarName = 'ORCA_INCLUDEFILE', oVarValue = uFnFile)
            if oDefinition is None:
                oDef=self.oWidgetBackGround.oDef
            else:
                oDef=oDefinition
            uET_Data = CachedFile(oFileName=Globals.oFnElementIncludeWrapper)
            uET_Data = ReplaceDefVars(uET_Data,oDef.oDefinitionVars)
            oET_Root = Orca_FromString(uET_Data,oDef,uFnFile)
            Orca_include(oET_Root,orca_et_loader)
            self._ReplaceElements(oXMLNode=oET_Root, uReplaceWidgetName=uReplaceWidgetName)
            return True
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg="Can''t load element (replace): %s (%s):" % (uFnElement, uFnFile),oException=e))
            return False

    def _ReplaceElements(self,oXMLNode:Element, uReplaceWidgetName:str) -> None:
        # Get list of all 'root elements', if not nested
        oXMLWidget:Element
        for oXMLWidget in oXMLNode:
            if oXMLWidget.tag==u'element':
                self._ReplaceWidgetFromXmlNode(oXMLNode=oXMLWidget, uReplaceWidgetName=uReplaceWidgetName)
                return
            elif oXMLWidget.tag==u'elements':
                self._ReplaceElements(oXMLNode=oXMLWidget, uReplaceWidgetName=uReplaceWidgetName)
            elif oXMLWidget.tag==u'page':
                self._ReplaceElements(oXMLNode=oXMLWidget.find('elements'), uReplaceWidgetName=uReplaceWidgetName)

    def _ReplaceWidgetFromXmlNode(self,oXMLNode:Element, uReplaceWidgetName:str) -> None:

        # first find the org Widgets
        # if you will replace a widget, which is multiple on a page, the outcome is unpredictable

        oWidget:cWidgetBase

        for oWidget in self.dWidgets[uReplaceWidgetName]:

            oXMLNode.set("posx","of:left:"+uReplaceWidgetName)
            oXMLNode.set("posy","of:top:"+uReplaceWidgetName)
            oXMLNode.set("width","of:width:"+uReplaceWidgetName)
            oXMLNode.set("height","of:height:"+uReplaceWidgetName)

            # Parse a spefific Widget from an xml definition
            oTmpWidget:cWidgetBase=cWidgetBase()
            #First get the widget type to know which widget to create
            oTmpWidget.GetWidgetTypeFromXmlNode(oXMLNode)
            self.dFktsCreateWidget[oTmpWidget.eWidgetType][0](oXMLNode, "",self.dFktsCreateWidget[oTmpWidget.eWidgetType][1])

            self.dWidgets.pop(uReplaceWidgetName)
            self.aWidgets.remove(oWidget)
            if oWidget.oObject is not None:
                oWidget.oObject.parent.remove_widget(oWidget.oObject)
            #oNewWidget.Create(self.oWidgetBackGround.oObject)

        return

    def RemoveWidget(self,oWidget:cWidgetBase) -> bool:
        """ Removes a widget from the page """

        self.dWidgets.pop(oWidget.uName)
        self.aWidgets.remove(oWidget)
        if oWidget.oObject is not None:
            oWidget.oObject.parent.remove_widget(oWidget.oObject)
        return True

    def _AddElements(self,oXMLNode:Element, uAnchor:str) -> Union[cWidgetBase,None]:
        """
        Adds Elemenst to the Page

        :param oXMLNode:
        :param str uAnchor:
        :return: The Last Added Element
        """
        oRet:Union[cWidgetBase,None] = None
        # Get list of all 'root elements', if not nested
        for oXMLWidget in oXMLNode:
            if oXMLWidget.tag==u'element':
                oRet=self.AddWidgetFromXmlNode(oXMLWidget, uAnchor)
            elif oXMLWidget.tag==u'elements':
                oRet=self._AddElements(oXMLNode=oXMLWidget, uAnchor=uAnchor)
            elif oXMLWidget.tag==u'page':
                oRet=self._AddElements(oXMLNode=oXMLWidget.find('elements'), uAnchor=uAnchor)

        #Once we need to add the background
        if self.oWidgetBackGround.uName==u'noname':
            self._AddBackGroundFromXmlNodes(oXMLNode)
        return oRet

    def _AddBackGroundFromXmlNodes(self,oXMLWidgets:Element) -> None:
        # Find the Background widget in all defined widgets
        oXMLWidget:Element
        for oXMLWidget in oXMLWidgets.findall('element'):
            self.oWidgetBackGround.GetWidgetTypeFromXmlNode(oXMLWidget)
            if self.oWidgetBackGround.eWidgetType==eWidgetType.BackGround:
                self.oWidgetBackGround.InitWidgetFromXml(oXMLWidget,self)
                return

    def AddWidgetFromXmlNode_Class(self, oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:

        oTmpWidget:cWidgetBase=oClass()
        oTmpWidget.SaveLastWidgetPos()

        if oTmpWidget.InitWidgetFromXml(oXMLNode,self, uAnchor):
            if oClass==cWidgetButton:
                if u':::' in oTmpWidget.GetCaption():
                    oTmpWidget=cWidgetDropDown()
                    oTmpWidget.RestoreLastWidgetPos()

                    if not oTmpWidget.InitWidgetFromXml(oXMLNode,self, uAnchor):
                        return oTmpWidget
            self.aWidgets.append(oTmpWidget)
            self.dWidgets[oTmpWidget.uName].append(oTmpWidget)
            self._AddElements(oXMLNode=oXMLNode, uAnchor=uAnchor)
        return oTmpWidget

    def AddWidgetFromXmlNode_Anchor(self, oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:
        oTmpAnchor:cWidgetBase = oClass()
        if oTmpAnchor.InitWidgetFromXml(oXMLNode,self, uAnchor):
            self.aWidgets.append(oTmpAnchor)
            self.dWidgets[oTmpAnchor.uName].append(oTmpAnchor)
            self._AddElements(oXMLNode=oXMLNode, uAnchor=oTmpAnchor.uName)
        return oTmpAnchor

    def AddWidgetFromXmlNode_Text(self, oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:
        oTmpText:cWidgetTextField=oClass()
        if oTmpText.InitWidgetFromXml(oXMLNode,self, uAnchor):
            self.aWidgets.append(oTmpText)
            self.dWidgets[oTmpText.uName].append(oTmpText)
            if oTmpText.bIsClock:
                self.aClockWidgetsIndex.append(len(self.aWidgets)-1)
            if oTmpText.bIsDate:
                self.aDateWidgetsIndex.append(len(self.aWidgets)-1)

            self._AddElements(oXMLNode=oXMLNode, uAnchor=uAnchor)
        return oTmpText

    # noinspection PyUnusedLocal
    def AddWidgetFromXmlNode_BackGround(self, oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:
        return self._AddElements(oXMLNode=oXMLNode, uAnchor=u'')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def AddWidgetFromXmlNode_None(self, oXMLNode:Element, uAnchor:str, oClass:Callable)  -> cWidgetBase:
        ShowErrorPopUp(uMessage=LogError(uMsg=u'AddWidget: Invalid Widget:'+tostring(oXMLNode)))
        return cWidgetBase()

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def AddWidgetFromXmlNode_Skip(self, oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:
        return cWidgetBase()

    def AddWidgetFromXmlNode(self,oXMLNode:Element, uAnchor:str) -> Union[bool,cWidgetBase]:
        # Parse a specific Widget from an xml definition

        oTmpWidget:cWidgetBase = cWidgetBase()
        #First get the widget type to know which widget to create
        oTmpWidget.GetWidgetTypeFromXmlNode(oXMLNode)
        #call the widget creation function

        if oTmpWidget.eWidgetType != eWidgetType.ERROR:
            try:
                return self.dFktsCreateWidget[oTmpWidget.eWidgetType][0](oXMLNode=oXMLNode,  uAnchor=uAnchor,oClass=self.dFktsCreateWidget[oTmpWidget.eWidgetType][1])
            except Exception as e:
                LogError(uMsg="can't create widget:"+XMLPrettify(oXMLNode),oException=e)
        else:
            Ret:Union[Dict,None] = Globals.oNotifications.SendNotification("UNKNOWNWIDGET",**{"SCREENPAGE":self,"XMLNODE":oXMLNode,"ANCHOR":uAnchor,"WIDGET":oTmpWidget})
            if Ret is None:
                Logger.error("Unknown Widget Type %s : Page: %s" % (oTmpWidget.uTypeString, self.uPageName))
                return False
        return False

    def Create(self) -> None:
        #create the Screen as a kivy screen object and add it the root (Screen Manager)
        try:
            if self.bIsInit:
                return

            Logger.debug (u'ScreenPage: Creating Page: '+self.uPageName)

            if not self.bIsPopUp:
                self.oScreen = Screen(size=(Globals.iAppWidth,Globals.iAppHeight))
                self.oScreen.name = self.uPageName
                Globals.oTheScreen.oRootSM.add_widget(self.oScreen)
            else:
                self.oScreen= Widget(size=(Globals.iAppWidth,Globals.iAppHeight))
                Globals.oTheScreen.dPopups[self.uPageName]=self.oScreen

            self.oWidgetBackGround.Create(self.oScreen)

            #Create all the widgets of the page
            for oWidget in self.aWidgets:
                if not oWidget.Create(self.oWidgetBackGround.oObject):
                    self.aErrorWidgets.append(oWidget)

            self.PostHandleErrorWidgets()
            self.bIsInit=True

        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'ScreenPage: can\'t Create Page [%s]:' % self.uPageName,oException=e))

    def PostHandleErrorWidgets(self):
        for oWidget in self.aErrorWidgets:
            if oWidget.oObject is not None:
                oWidget.oParent.remove_widget(oWidget.oObject)
            if oWidget in self.aWidgets:
                self.aWidgets.remove(oWidget)
        del self.aErrorWidgets[:]

        for oWidget in self.aAddWidgets:
            self.aWidgets.append(oWidget)
        del self.aAddWidgets[:]

    def UpdateSetupWidgets(self) -> None:
        #Updates all widgets of a page
        #Its safe to call create again, in case, it did'nt happen by now
        self.Create()
        oWidget:cWidgetBase
        for oWidget in self.aWidgets:
            if oWidget.eWidgetType==eWidgetType.Settings:
                oWidget.UpdateWidget()

    def GetGestureAction(self,uGestureName:str):
        #return the gesture object to a given gesture name
        return self.dGestures.get(uGestureName)

    def SetTransmitterPicture(self,uTransmitterPictureName:str) -> None:
        #Sets the to use transmitter picture for interface activities
        oWidget:cWidgetBase
        for oWidget in self.aWidgets:
            if oWidget.uName == uTransmitterPictureName:
                if oWidget.eWidgetType==eWidgetType.Picture:
                    self.oWidgetPictureTransmit = oWidget

    def SetWaitPicture(self,uWaitPictureName:str) -> None:
        #Sets the to use wait picture for interface activities
        oWidget: cWidgetBase
        for oWidget in self.aWidgets:
            if oWidget.uName == uWaitPictureName:
                if oWidget.eWidgetType==eWidgetType.Picture:
                    self.oWidgetPictureWait = oWidget

    # noinspection PyUnusedLocal
    def OnKey(self,window,uKey:str) -> bool:

        # Logger.debug (u'ScreenPage: KeyPressed: '+uKey)

        # Fallback to prevent unstoppable apps
        if uKey == 'key_ESC':
            self.iESCPressCount = self.iESCPressCount + 1
            if self.iESCPressCount > 2:
                StopWait()
                aActions=Globals.oActions.GetActionList(uActionName = "askonexit", bNoCopy = False)
                if aActions is not None:
                    Globals.oEvents.ExecuteActions( aActions=aActions,oParentWidget=None)
        else:
            self.iESCPressCount = 0

        return True

