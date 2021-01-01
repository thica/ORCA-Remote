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
from typing                         import Optional
from typing                         import List
from typing                         import Dict
from typing                         import Callable
from typing                         import Tuple
from typing                         import Any
from typing                         import cast

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
from ORCA.widgets.ScrollList        import cWidgetScrollList
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
        self.oWidgetPictureTransmit:Optional[cWidgetPicture]   = None
        self.oWidgetPictureWait:Optional[cWidgetPicture]       = None
        self.uHexBackGroundColor:str                           = u'#000000'
        self.uPageName:str                                     = u'NoName'
        #Name indexed array of widgets
        self.dWidgets:defaultdict                              = defaultdict(list)
        #Dictionary of all Widgets by uID
        self.dWidgetsID: Dict[str,cWidgetBase]                 = {}
        #List of all widgets to remove after creation
        self.aErrorWidgets: List[cWidgetBase]                  = []
        #List of all widgets to add after creation
        self.aAddWidgets: List[cWidgetBase]                    = []
        #List of all Widgets grouped by Anchor, we be created on request by enablewidget
        self.dAnchorWidgets:Dict[str,List[cWidgetBase]]        = {}

        self.iESCPressCount:int                                = 0

        self.aClockWidgetsID:List[str]                         = []
        self.aDateWidgetsID:List[str]                          = []
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
        self.oScreen:Optional[Screen]                        = None

        self.dFktsCreateWidget[eWidgetType.BackGround]       = self.AddWidgetFromXmlNode_BackGround, None
        self.dFktsCreateWidget[eWidgetType.TextField]        = self.AddWidgetFromXmlNode_Class,     cWidgetTextField
        self.dFktsCreateWidget[eWidgetType.Anchor]           = self.AddWidgetFromXmlNode_Anchor,    cWidgetAnchor
        self.dFktsCreateWidget[eWidgetType.Button]           = self.AddWidgetFromXmlNode_Class,     cWidgetButton
        self.dFktsCreateWidget[eWidgetType.Switch]           = self.AddWidgetFromXmlNode_Class,     cWidgetSwitch
        self.dFktsCreateWidget[eWidgetType.Picture]          = self.AddWidgetFromXmlNode_Class,     cWidgetPicture
        self.dFktsCreateWidget[eWidgetType.TextInput]        = self.AddWidgetFromXmlNode_Class,     cWidgetTextInput
        self.dFktsCreateWidget[eWidgetType.Knob]             = self.AddWidgetFromXmlNode_Class,     cWidgetKnob
        self.dFktsCreateWidget[eWidgetType.FileViewer]       = self.AddWidgetFromXmlNode_Class,     cWidgetFileViewer
        self.dFktsCreateWidget[eWidgetType.Slider]           = self.AddWidgetFromXmlNode_Class,     cWidgetSlider
        self.dFktsCreateWidget[eWidgetType.Rectangle]        = self.AddWidgetFromXmlNode_Class,     cWidgetRectangle
        self.dFktsCreateWidget[eWidgetType.Circle]           = self.AddWidgetFromXmlNode_Class,     cWidgetCircle
        self.dFktsCreateWidget[eWidgetType.Video]            = self.AddWidgetFromXmlNode_Class,     cWidgetVideo
        self.dFktsCreateWidget[eWidgetType.DropDown]         = self.AddWidgetFromXmlNode_Class,     cWidgetDropDown
        self.dFktsCreateWidget[eWidgetType.ColorPicker]      = self.AddWidgetFromXmlNode_Class,     cWidgetColorPicker
        self.dFktsCreateWidget[eWidgetType.Settings]         = self.AddWidgetFromXmlNode_Class,     cWidgetSettings
        self.dFktsCreateWidget[eWidgetType.FileBrowser]      = self.AddWidgetFromXmlNode_Class,     cWidgetFileBrowser
        self.dFktsCreateWidget[eWidgetType.ScrollList]       = self.AddWidgetFromXmlNode_Container, cWidgetScrollList
        self.dFktsCreateWidget[eWidgetType.ScrollContainer]  = self.AddWidgetFromXmlNode_Container, cWidgetScrollContainer
        self.dFktsCreateWidget[eWidgetType.Border]           = self.AddWidgetFromXmlNode_Class,     cWidgetBorder
        self.dFktsCreateWidget[eWidgetType.NoWidget]         = self.AddWidgetFromXmlNode_None,      None
        self.dFktsCreateWidget[eWidgetType.SkipWidget]       = self.AddWidgetFromXmlNode_Skip,      None

    def InitPageFromXmlNode(self,*,oXMLNode:Element) -> None:
        """ Reads the page parameter from a Xml Node
        :param Element oXMLNode: The element tree element, root of the page xml
        :return: None
        :rtype: None
        """

        self.uPageName          = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=u'name',bMandatory=True,vDefault=u'')
        oRef:Element            = oXMLNode.find(u'page_parameter')
        self.uDefaultInterface  = GetXMLTextValue(oXMLNode=oRef,uTag=u'interface',      bMandatory=False,vDefault=u'')
        self.uDefaultConfigName = GetXMLTextValue(oXMLNode=oRef,uTag=u'configname',     bMandatory=False,vDefault=u'')
        self.bIsPopUp           = GetXMLBoolValue(oXMLNode=oRef,uTag=u'popup',          bMandatory=False,bDefault=False)
        self.bPreventPreInit    = GetXMLBoolValue(oXMLNode=oRef,uTag=u'preventpreinit', bMandatory=False,bDefault=False)

        # ToDo: this is temporary to validate some strange default value changes
        self.uDefaultInterface  = ReplaceVars(self.uDefaultInterface)
        self.uDefaultConfigName = ReplaceVars(self.uDefaultConfigName)

        #not used
        self.uOrientation       = GetXMLTextValue(oXMLNode=oRef,uTag=u'orientation',bMandatory=False,vDefault=Globals.uDeviceOrientation)

        if not self.uDefaultInterface==u'':
            Globals.oInterFaces.dUsedInterfaces[ReplaceVars(self.uDefaultInterface)]=True

    def AddPageElementsFromXmlNode(self,*,oXMLNode:Element) -> None:
        """ Adds elements defined in an xml node
        :param Element oXMLNode: The element tree element
        :return: None
        :rtype: None
        """

        self._AddElements(oXMLNode=oXMLNode, uAnchor=u'')

    def LoadElement(self,*,uFnElement:str, uAnchor:str, oDefinition:cDefinition) -> bool:
        """ Load an element at runtime to a page: the page must not be initialized
        :param str uFnElement: FileName of element to load
        :param str uAnchor: Target Anchor in Page to place the element into
        :param cDefinition oDefinition: Target Definition
        :return: True if successful, otherwise False
        :rtype:bool
        """

        oFnElement:cFileName
        uET_Data:str
        oET_Root:Element
        oWidget:cWidgetBase

        try:
            oFnElement=cFileName('').ImportFullPath(uFnFullName=uFnElement)
            SetVar(uVarName = 'ORCA_INCLUDEFILE', oVarValue = oFnElement.string)
            if oDefinition is None:
                oDef=self.oWidgetBackGround.oDef
            else:
                oDef=oDefinition
            uET_Data = CachedFile(oFileName=Globals.oFnElementIncludeWrapper)
            uET_Data = ReplaceDefVars(uET_Data,oDef.oDefinitionVars)
            oET_Root = Orca_FromString(uET_Data=uET_Data,oDef=oDef,uFileName=oFnElement.string)
            Orca_include(oET_Root,orca_et_loader)
            oWidget=self._AddElements(oXMLNode=oET_Root, uAnchor=uAnchor)
            if self.bIsInit:
                if oWidget is not None:
                    oWidget.Create(self.oWidgetBackGround.oObject)
            return True
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg="Can''t load element: %s:" % uFnElement,oException=e))
            return False

    def ReplaceElement(self,*,uFnElement:str, uReplaceWidgetName:str,oDefinition:cDefinition) -> bool:
        """ Replaces an element at runtime in a page: the page must not be initialized
        :param str uFnElement: FileName of element to load
        :param str uReplaceWidgetName: The Widgetname to be replaced
        :param cDefinition oDefinition: Target Definition
        :return: True if successful, otherwise False
        :rtype: bool
        """

        uFnFile:str = ''
        oDef:cDefinition
        uET_Data:str
        oET_Root:Element

        try:
            uFnFile=(cFileName(u'').ImportFullPath(uFnFullName=uFnElement)).string
            SetVar(uVarName = 'ORCA_INCLUDEFILE', oVarValue = uFnFile)
            if oDefinition is None:
                oDef=self.oWidgetBackGround.oDef
            else:
                oDef=oDefinition
            uET_Data = CachedFile(oFileName=Globals.oFnElementIncludeWrapper)
            uET_Data = ReplaceDefVars(uET_Data,oDef.oDefinitionVars)
            oET_Root = Orca_FromString(uET_Data=uET_Data,oDef=oDef,uFileName=uFnFile)
            Orca_include(oET_Root,orca_et_loader)
            self._ReplaceElements(oXMLNode=oET_Root, uReplaceWidgetName=uReplaceWidgetName)
            return True
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg="Can''t load element (replace): %s (%s):" % (uFnElement, uFnFile),oException=e))
            return False

    def _ReplaceElements(self,*,oXMLNode:Element, uReplaceWidgetName:str) -> None:
        """ Recursive replaces elements from a node
        """
        oXMLWidget:Element
        for oXMLWidget in oXMLNode:
            if oXMLWidget.tag==u'element':
                self._ReplaceWidgetFromXmlNode(oXMLNode=oXMLWidget, uReplaceWidgetName=uReplaceWidgetName)
                return
            elif oXMLWidget.tag==u'elements':
                self._ReplaceElements(oXMLNode=oXMLWidget, uReplaceWidgetName=uReplaceWidgetName)
            elif oXMLWidget.tag==u'page':
                self._ReplaceElements(oXMLNode=oXMLWidget.find('elements'), uReplaceWidgetName=uReplaceWidgetName)

    def _ReplaceWidgetFromXmlNode(self,*,oXMLNode:Element, uReplaceWidgetName:str) -> None:

        # first find the org Widgets
        # if you will replace a widget, which is multiple on a page, the outcome is unpredictable

        oWidget:cWidgetBase

        oXMLNode.set("posx","of:left:"+uReplaceWidgetName)
        oXMLNode.set("posy","of:top:"+uReplaceWidgetName)
        oXMLNode.set("width","of:width:"+uReplaceWidgetName)
        oXMLNode.set("height","of:height:"+uReplaceWidgetName)

        # Parse a specific Widget from an xml definition
        oTmpWidget:cWidgetBase=cWidgetBase()
        #First get the widget type to know which widget to create
        oTmpWidget.GetWidgetTypeFromXmlNode(oXMLNode)
        self.dFktsCreateWidget[oTmpWidget.eWidgetType][0](oXMLNode, "",self.dFktsCreateWidget[oTmpWidget.eWidgetType][1])
        self.RemoveWidget(oWidget=self.dWidgets[uReplaceWidgetName][0])
        return

    def RemoveWidget(self,*,oWidget:cWidgetBase) -> bool:
        """ Removes a widget from the page """
        oTmpWidget: cWidgetBase
        '''
        for oTmpWidget in self.dWidgets[oWidget.uName]:
            if oTmpWidget.oObject is not None:
                oTmpWidget.oObject.parent.remove_widget(oTmpWidget.oObject)
                oTmpWidget.oObject=None
        '''

        self.dWidgets.pop(oWidget.uName,None)
        if oWidget.oObject is not None:
            oWidget.oObject.parent.remove_widget(oWidget.oObject)
            oWidget.oObject = None

        self.dWidgetsID.pop(oWidget.uID,None)
        if oWidget.uID in self.aDateWidgetsID:
            self.aDateWidgetsID.remove(oWidget.uID)
        if oWidget.uID in self.aClockWidgetsID:
            self.aClockWidgetsID.remove(oWidget.uID)
        return True

    def RegisterWidget(self,*,oWidget:cWidgetBase) -> bool:
        """ Register / Adds a Widget to the page"""

        self.dWidgets[oWidget.uName].append(oWidget)

        '''
        if oWidget.uName:
            if len(self.dWidgets[oWidget.uName])>1:
                Logger.warning("Warning: Duplicate widget name %s on page %s, be aware of possible side effects" % (oWidget.uName,oWidget.uPageName))
        '''

        self.dWidgetsID[oWidget.uID] = oWidget
        if oWidget.eWidgetType == eWidgetType.TextField:
            if cast(cWidgetTextField,oWidget).bIsDate:
                self.aDateWidgetsID.append(oWidget.uID)
            if cast(cWidgetTextField, oWidget).bIsClock:
                self.aClockWidgetsID.append(oWidget.uID)

        return True


    def _AddElements(self,*,oXMLNode:Element, uAnchor:str) -> Union[cWidgetBase,None]:
        """
        Adds Elements to the Page

        :param Element oXMLNode: The element tree element, root of the page xml or the next nested "elements" element. Will recursivly call itself until the whole tree is parsed
        :param str uAnchor: The anchor of the tree (background at start)
        :return: The last added Element or None, if finished
        """

        oRet:Union[cWidgetBase,None] = None
        # Get list of all 'root elements', if not nested
        for oXMLWidget in oXMLNode:
            if oXMLWidget.tag==u'element':
                oRet=self.AddWidgetFromXmlNode(oXMLNode=oXMLWidget, uAnchor=uAnchor)
            elif oXMLWidget.tag==u'elements':
                oRet=self._AddElements(oXMLNode=oXMLWidget, uAnchor=uAnchor)
            elif oXMLWidget.tag==u'page':
                oRet=self._AddElements(oXMLNode=oXMLWidget.find('elements'), uAnchor=uAnchor)

        #Once we need to add the background
        if self.oWidgetBackGround.uName==u'noname':
            self._AddBackGroundFromXmlNodes(oXMLWidgets=oXMLNode)
        return oRet

    def _AddBackGroundFromXmlNodes(self,*,oXMLWidgets:Element) -> None:
        """
        Find the background widget, as this the root anchor widget. No includes or nested widgets allowed!

        :param Element oXMLWidgets: The element tree element, root of the page xml
        :rtype: None
        :return: Nothing, the background widget is parsed and added directly
        """

        oXMLWidget:Element
        for oXMLWidget in oXMLWidgets.findall('element'):
            self.oWidgetBackGround.GetWidgetTypeFromXmlNode(oXMLWidget)
            if self.oWidgetBackGround.eWidgetType==eWidgetType.BackGround:
                self.oWidgetBackGround.InitWidgetFromXml(oXMLNode=oXMLWidget,oParentScreenPage=self)
                return

    def AddWidgetFromXmlNode_Class(self,*,oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:
        """
        Adds a widget to the widget tree for a generic class

        :param Element oXMLNode: The element tree element, which defines the widget
        :param str uAnchor: The anchor, to where the widget is embedded
        :param Callable oClass: The class with base class cWidgetBase, which will created as an object
        :rtype: cWidgetBase
        :return: The created widget object
        """

        oTmpWidget:cWidgetBase=oClass()
        oTmpWidget.SaveLastWidgetPos()

        if oTmpWidget.InitWidgetFromXml(oXMLNode=oXMLNode,oParentScreenPage=self, uAnchor=uAnchor):
            if oClass==cWidgetButton:
                if u':::' in oTmpWidget.GetCaption():
                    oTmpWidget=cWidgetDropDown()
                    oTmpWidget.RestoreLastWidgetPos()

                    if not oTmpWidget.InitWidgetFromXml(oXMLNode=oXMLNode,oParentScreenPage=self, uAnchor=uAnchor):
                        return oTmpWidget
            self.RegisterWidget(oWidget=oTmpWidget)
            self._AddElements(oXMLNode=oXMLNode, uAnchor=uAnchor)
        return oTmpWidget

    def AddWidgetFromXmlNode_Anchor(self, *,oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:
        oTmpWidget:cWidgetBase = oClass()
        if oTmpWidget.InitWidgetFromXml(oXMLNode=oXMLNode,oParentScreenPage=self, uAnchor=uAnchor):
            self.RegisterWidget(oWidget=oTmpWidget)
            self._AddElements(oXMLNode=oXMLNode, uAnchor=oTmpWidget.uName)
        return oTmpWidget

    def AddWidgetFromXmlNode_Container(self, *,oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:
        oTmpWidget:cWidgetBase = oClass()
        if oTmpWidget.InitWidgetFromXml(oXMLNode=oXMLNode,oParentScreenPage=self, uAnchor=uAnchor):
            self.RegisterWidget(oWidget=oTmpWidget)
            oTmpWidget.SetContainer(uContainer=oTmpWidget.uContainer)
            self._AddElements(oXMLNode=oXMLNode, uAnchor=uAnchor)
            oTmpWidget.SetContainer(uContainer="")
        return oTmpWidget

    # noinspection PyUnusedLocal
    def AddWidgetFromXmlNode_BackGround(self,*, oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:
        return self._AddElements(oXMLNode=oXMLNode, uAnchor=u'')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def AddWidgetFromXmlNode_None(self,*, oXMLNode:Element, uAnchor:str, oClass:Callable)  -> cWidgetBase:
        ShowErrorPopUp(uMessage=LogError(uMsg=u'AddWidget: Invalid Widget:'+str(tostring(oXMLNode))))
        return cWidgetBase()

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def AddWidgetFromXmlNode_Skip(self,*, oXMLNode:Element, uAnchor:str, oClass:Callable) -> cWidgetBase:
        return cWidgetBase()

    def AddWidgetFromXmlNode(self,*,oXMLNode:Element, uAnchor:str) -> Union[bool,cWidgetBase]:
        # Parse a specific Widget from an xml definition

        oTmpWidget:cWidgetBase = cWidgetBase()
        #First get the widget type to know which widget to create
        oTmpWidget.GetWidgetTypeFromXmlNode(oXMLNode)
        #call the widget creation function

        if oTmpWidget.eWidgetType != eWidgetType.ERROR:
            try:
                return self.dFktsCreateWidget[oTmpWidget.eWidgetType][0](oXMLNode=oXMLNode,  uAnchor=uAnchor,oClass=self.dFktsCreateWidget[oTmpWidget.eWidgetType][1])
            except Exception as e:
                LogError(uMsg="can't create widget:"+XMLPrettify(oElem=oXMLNode),oException=e)
        else:
            Ret:Union[Dict,None] = Globals.oNotifications.SendNotification(uNotification="UNKNOWNWIDGET",**{"SCREENPAGE":self,"XMLNODE":oXMLNode,"ANCHOR":uAnchor,"WIDGET":oTmpWidget})
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
            for oWidget in self.dWidgetsID.values():
                if not oWidget.bIsCreated:
                    if not oWidget.Create(self.oWidgetBackGround.oObject):
                        self.aErrorWidgets.append(oWidget)

            self.PostHandleErrorWidgets()
            self.bIsInit=True

        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'ScreenPage: can\'t Create Page [%s]:' % self.uPageName,oException=e))

    def PostHandleErrorWidgets(self):
        for oWidget in self.aErrorWidgets:
            self.RemoveWidget(oWidget=oWidget)
        del self.aErrorWidgets[:]

        for oWidget in self.aAddWidgets:
            self.RegisterWidget(oWidget=oWidget)
        del self.aAddWidgets[:]

    def UpdateSetupWidgets(self) -> None:
        #Updates all widgets of a page
        #Its safe to call create again, in case, it did'nt happen by now
        self.Create()
        oWidget:cWidgetBase
        for oWidget in self.dWidgetsID.values():
            if oWidget.eWidgetType==eWidgetType.Settings:
                oWidget.UpdateWidget()

    def GetGestureAction(self,*,uGestureName:str):
        #return the gesture object to a given gesture name
        return self.dGestures.get(uGestureName)

    def SetTransmitterPicture(self,*,uTransmitterPictureName:str) -> None:
        #Sets the to use transmitter picture for interface activities
        oWidget:cWidgetBase
        for oWidget in self.dWidgetsID.values():
            if oWidget.uName == uTransmitterPictureName:
                if oWidget.eWidgetType==eWidgetType.Picture:
                    self.oWidgetPictureTransmit = oWidget

    def SetWaitPicture(self,*,uWaitPictureName:str) -> None:
        #Sets the to use wait picture for interface activities
        oWidget: cWidgetBase
        for oWidget in self.dWidgetsID.values():
            if oWidget.uName == uWaitPictureName:
                if oWidget.eWidgetType==eWidgetType.Picture:
                    self.oWidgetPictureWait = oWidget

    # noinspection PyUnusedLocal
    def OnKey(self,window,uKey:str) -> bool:

        # Logger.debug (u'ScreenPage: KeyPressed: '+uKey)

        # Fallback to prevent unstoppable apps
        if uKey == 'key_ESC':
            self.iESCPressCount += 1
            if self.iESCPressCount > 2:
                StopWait()
                aActions=Globals.oActions.GetActionList(uActionName = "askonexit", bNoCopy = False)
                if aActions is not None:
                    Globals.oEvents.ExecuteActions( aActions=aActions,oParentWidget=None)
        else:
            self.iESCPressCount = 0

        return True

    def CreateAnchorWidgets(self):
        oWidget:cWidgetBase
        aAnchorWidgets:List[cWidgetBase]
        for oWidget in self.dWidgetsID.values():
            uAnchorName = oWidget.uAnchorName
            if uAnchorName!="":
                if self.dAnchorWidgets.get(uAnchorName) is None:
                    self.dAnchorWidgets[uAnchorName] = []
                self.dAnchorWidgets[uAnchorName].append(oWidget)


