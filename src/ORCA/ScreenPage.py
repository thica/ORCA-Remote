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

from collections                    import defaultdict
from xml.etree.ElementTree          import tostring
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
from ORCA.widgets.Base              import cWidgetBase
from ORCA.widgets.Base              import oWidgetType
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
from ORCA.utils.FileName            import cFileName

import ORCA.Globals as Globals

class cScreenPage(object):

    """
    Representation of a screen page and all it's widgets
    """

    def __init__(self):
        self.oWidgetBackGround      = cWidgetBackGround()
        self.oWidgetPictureTransmit = None
        self.oWidgetPictureWait     = None
        self.uHexBackGroundColor    = u'#000000'
        self.uPageName              = u'NoName'
        #ordered array of widgets
        self.aWidgets               = []
        #indexed array of widgets
        self.dWidgets               = defaultdict(list)

        self.iESCPressCount         = 0

        self.aClockWidgetsIndex     = []
        self.aDateWidgetsIndex      = []
        self.dGestures              = {}
        self.bIsInit                = False
        self.uDefaultInterface      = u''
        self.uDefaultConfigName     = u''
        self.dFktsCreateWidget      = {}
        self.bIsPopUp               = False
        self.bPreventPreInit        = False
        self.uCallingPageName       = u''
        #not used
        self.uOrientation           = u''

        # Embedded kivy Screen Object
        self.oScreen                 = None

        self.dFktsCreateWidget[oWidgetType.BackGround]       = self._AddWidgetFromXmlNode_BackGround,None
        self.dFktsCreateWidget[oWidgetType.TextField]        = self._AddWidgetFromXmlNode_Text,cWidgetTextField
        self.dFktsCreateWidget[oWidgetType.Anchor]           = self._AddWidgetFromXmlNode_Anchor,cWidgetAnchor
        self.dFktsCreateWidget[oWidgetType.Button]           = self._AddWidgetFromXmlNode_Class,cWidgetButton
        self.dFktsCreateWidget[oWidgetType.Switch]           = self._AddWidgetFromXmlNode_Class,cWidgetSwitch
        self.dFktsCreateWidget[oWidgetType.Picture]          = self._AddWidgetFromXmlNode_Class,cWidgetPicture
        self.dFktsCreateWidget[oWidgetType.TextInput]        = self._AddWidgetFromXmlNode_Class,cWidgetTextInput
        self.dFktsCreateWidget[oWidgetType.Knob]             = self._AddWidgetFromXmlNode_Class,cWidgetKnob
        self.dFktsCreateWidget[oWidgetType.FileViewer]       = self._AddWidgetFromXmlNode_Class,cWidgetFileViewer
        self.dFktsCreateWidget[oWidgetType.Slider]           = self._AddWidgetFromXmlNode_Class,cWidgetSlider
        self.dFktsCreateWidget[oWidgetType.Rectangle]        = self._AddWidgetFromXmlNode_Class,cWidgetRectangle
        self.dFktsCreateWidget[oWidgetType.Circle]           = self._AddWidgetFromXmlNode_Class,cWidgetCircle
        self.dFktsCreateWidget[oWidgetType.Video]            = self._AddWidgetFromXmlNode_Class,cWidgetVideo
        self.dFktsCreateWidget[oWidgetType.DropDown]         = self._AddWidgetFromXmlNode_Class,cWidgetDropDown
        self.dFktsCreateWidget[oWidgetType.ColorPicker]      = self._AddWidgetFromXmlNode_Class,cWidgetColorPicker
        self.dFktsCreateWidget[oWidgetType.Settings]         = self._AddWidgetFromXmlNode_Class,cWidgetSettings
        self.dFktsCreateWidget[oWidgetType.FileBrowser]      = self._AddWidgetFromXmlNode_Class,cWidgetFileBrowser
        self.dFktsCreateWidget[oWidgetType.NoWidget]         = self._AddWidgetFromXmlNode_None,None
        self.dFktsCreateWidget[oWidgetType.SkipWidget]       = self._AddWidgetFromXmlNode_Skip,None


    def InitPageFromXmlNode(self,oXMLNode):
        """ Get Page Definitions """
        self.uPageName          = GetXMLTextAttribute(oXMLNode,u'name',True,u'')
        oRef                    = oXMLNode.find(u'page_parameter')
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

    def AddPageElementsFromXmlNode(self,oXMLNode):
        """ Adds elements defined in an xml node"""

        self._AddElements(oXMLNode=oXMLNode, uAnchor=u'')

    def LoadElement(self,uFnElement, uAnchor, oDefinition):
        """ Load an element at runtime to a page: the page must not be initalized
        :param string uFnElement: FileName of element to load
        :param string uAnchor: Target Anchor in Page to place the element into
        :param cDefinition oDefinition: Target Definition
        :rtype: bool
        :return: True if successful, otherwise False

        """

        oFnElement = None

        try:
            oFnElement=cFileName('').ImportFullPath(uFnElement)
            SetVar(uVarName = 'ORCA_INCLUDEFILE', oVarValue = oFnElement.string)
            if oDefinition is None:
                oDef=self.oWidgetBackGround.oDef
            else:
                oDef=oDefinition
            sET_Data = CachedFile(Globals.oFnElementIncludeWrapper)
            sET_Data = ReplaceDefVars(sET_Data,oDef.oDefinitionVars)
            oET_Root = Orca_FromString(sET_Data,oDef,oFnElement.string)
            Orca_include(oET_Root,orca_et_loader)
            oWidget=self._AddElements(oXMLNode=oET_Root, uAnchor=uAnchor)
            if self.bIsInit:
                if oWidget is not None:
                    oWidget.Create(self.oWidgetBackGround.oObject)
            return True
        except Exception as e:
            uMsg=LogError("Can''t load element: %s:" % oFnElement.string,e)
            ShowErrorPopUp(uMessage=uMsg)
            return False

    def ReplaceElement(self,uFnElement, uReplaceWidgetName,oDefinition):
        """ Replaces an element at runtime in a page: the page must not be initalized
        :param string uFnElement: FileName of element to load
        :param string uReplaceWidgetName: The Widgetname to be replaced
        :param cDefinition oDefinition: Target Definition
        :rtype: bool
        :return: True if successful, otherwise False

        """

        uFnFile = ''

        try:
            uFnFile=(cFileName(u'').ImportFullPath(uFnElement)).string
            SetVar(uVarName = 'ORCA_INCLUDEFILE', oVarValue = uFnFile)
            if oDefinition is None:
                oDef=self.oWidgetBackGround.oDef
            else:
                oDef=oDefinition
            sET_Data = CachedFile(Globals.oFnElementIncludeWrapper)
            sET_Data = ReplaceDefVars(sET_Data,oDef.oDefinitionVars)
            oET_Root = Orca_FromString(sET_Data,oDef,uFnFile)
            Orca_include(oET_Root,orca_et_loader)
            self._ReplaceElements(oXMLNode=oET_Root, uReplaceWidgetName=uReplaceWidgetName)
            return True
        except Exception as e:
            uMsg=LogError("Can''t load element (replace): %s (%s):" % (uFnElement, uFnFile),e)
            ShowErrorPopUp(uMessage=uMsg)
            return False

    def _ReplaceElements(self,oXMLNode, uReplaceWidgetName):
        # Get list of all 'root elements', if not nested
        for oXMLWidget in oXMLNode:
            if oXMLWidget.tag==u'element':
                self._ReplaceWidgetFromXmlNode(oXMLNode=oXMLWidget, uReplaceWidgetName=uReplaceWidgetName)
                return
            elif oXMLWidget.tag==u'elements':
                self._ReplaceElements(oXMLNode=oXMLWidget, uReplaceWidgetName=uReplaceWidgetName)
            elif oXMLWidget.tag==u'page':
                self._ReplaceElements(oXMLNode=oXMLWidget.find('elements'), uReplaceWidgetName=uReplaceWidgetName)

    def _ReplaceWidgetFromXmlNode(self,oXMLNode, uReplaceWidgetName):

        # first find the org Widgets
        # if you will replace a widget, which is multiple on a page, the outcome is unpredictable

        for oWidget in self.dWidgets[uReplaceWidgetName]:

            oXMLNode.set("posx","of:left:"+uReplaceWidgetName)
            oXMLNode.set("posy","of:top:"+uReplaceWidgetName)
            oXMLNode.set("width","of:width:"+uReplaceWidgetName)
            oXMLNode.set("height","of:height:"+uReplaceWidgetName)

            # Parse a spefific Widget from an xml definition
            oTmpWidget=cWidgetBase()
            #First get the widget type to know which widget to create
            oTmpWidget.GetWidgetTypeFromXmlNode(oXMLNode)
            self.dFktsCreateWidget[oTmpWidget.iWidgetType][0](oXMLNode, "",self.dFktsCreateWidget[oTmpWidget.iWidgetType][1])

            self.dWidgets.pop(uReplaceWidgetName)
            self.aWidgets.remove(oWidget)
            if oWidget.oObject is not None:
                oWidget.oObject.parent.remove_widget(oWidget.oObject)
            #oNewWidget.Create(self.oWidgetBackGround.oObject)

        return

    def RemoveWidget(self,oWidget):
        """ Removes a widget from the page """

        self.dWidgets.pop(oWidget.uName)
        self.aWidgets.remove(oWidget)
        if oWidget.oObject is not None:
            oWidget.oObject.parent.remove_widget(oWidget.oObject)

    def _AddElements(self,oXMLNode, uAnchor):
        """
        Adds Elemenst to the Page

        :rtype: cWidgetBase
        :param oXMLNode:
        :param string uAnchor:
        :return: The Last Added Element
        """
        oRet=None
        # Get list of all 'root elements', if not nested
        for oXMLWidget in oXMLNode:
            if oXMLWidget.tag==u'element':
                oRet=self._AddWidgetFromXmlNode(oXMLWidget, uAnchor)
            elif oXMLWidget.tag==u'elements':
                oRet=self._AddElements(oXMLNode=oXMLWidget, uAnchor=uAnchor)
            elif oXMLWidget.tag==u'page':
                oRet=self._AddElements(oXMLNode=oXMLWidget.find('elements'), uAnchor=uAnchor)

        #Once we need to add the background
        if self.oWidgetBackGround.uName==u'noname':
            self._AddBackGroundFromXmlNodes(oXMLNode)
        return oRet

    def _AddBackGroundFromXmlNodes(self,oXMLWidgets):
        # Find the Background widget in all defined widgets
        for oXMLWidget in oXMLWidgets.findall('element'):
            self.oWidgetBackGround.GetWidgetTypeFromXmlNode(oXMLWidget)
            if self.oWidgetBackGround.iWidgetType==oWidgetType.BackGround:
                self.oWidgetBackGround.InitWidgetFromXml(oXMLWidget,self)
                return

    def _AddWidgetFromXmlNode_Class(self,oXMLNode, uAnchor, oClass):

        oTmpWidget=oClass()
        oTmpWidget.SaveLastWidgetPos()

        if oTmpWidget.InitWidgetFromXml(oXMLNode,self, uAnchor):
            if oClass==cWidgetButton:
                if u':::' in oTmpWidget.uCaption:
                    oTmpWidget=cWidgetDropDown()
                    oTmpWidget.RestoreLastWidgetPos()

                    if not oTmpWidget.InitWidgetFromXml(oXMLNode,self, uAnchor):
                        return oTmpWidget
            self.aWidgets.append(oTmpWidget)
            self.dWidgets[oTmpWidget.uName].append(oTmpWidget)
            self._AddElements(oXMLNode=oXMLNode, uAnchor=uAnchor)
        return oTmpWidget

    def _AddWidgetFromXmlNode_Anchor(self,oXMLNode, uAnchor,oClass):
        oTmpAnchor=oClass()
        if oTmpAnchor.InitWidgetFromXml(oXMLNode,self, uAnchor):
            self.aWidgets.append(oTmpAnchor)
            self.dWidgets[oTmpAnchor.uName].append(oTmpAnchor)
            self._AddElements(oXMLNode=oXMLNode, uAnchor=oTmpAnchor.uName)

    def _AddWidgetFromXmlNode_Text(self,oXMLNode, uAnchor,oClass):
        oTmpText=oClass()
        if oTmpText.InitWidgetFromXml(oXMLNode,self, uAnchor):
            self.aWidgets.append(oTmpText)
            self.dWidgets[oTmpText.uName].append(oTmpText)
            if oTmpText.bIsClock:
                self.aClockWidgetsIndex.append(len(self.aWidgets)-1)
            if oTmpText.bIsDate:
                self.aDateWidgetsIndex.append(len(self.aWidgets)-1)

            self._AddElements(oXMLNode=oXMLNode, uAnchor=uAnchor)

    def _AddWidgetFromXmlNode_BackGround(self,oXMLNode, uAnchor,oClass):
        self._AddElements(oXMLNode=oXMLNode, uAnchor=u'')

    def _AddWidgetFromXmlNode_None(self,oXMLNode, uAnchor,oClass):
        uMsg=LogError(u'AddWidget: Invalid Widget:'+tostring(oXMLNode))
        ShowErrorPopUp(uMessage=uMsg)

    def _AddWidgetFromXmlNode_Skip(self,oXMLNode, uAnchor,oClass):
        pass

    def _AddWidgetFromXmlNode(self,oXMLNode, uAnchor):
        # Parse a spefific Widget from an xml definition

        oTmpWidget=cWidgetBase()
        #First get the widget type to know which widget to create
        oTmpWidget.GetWidgetTypeFromXmlNode(oXMLNode)
        #call the widget creation function

        if oTmpWidget.iWidgetType != -1:
            try:
                return self.dFktsCreateWidget[oTmpWidget.iWidgetType][0](oXMLNode=oXMLNode,  uAnchor=uAnchor,oClass=self.dFktsCreateWidget[oTmpWidget.iWidgetType][1])
            except Exception as e:
                LogError("can't create widget:"+XMLPrettify(oXMLNode),e)
        else:
            Ret = Globals.oNotifications.SendNotification("UNKNOWNWIDGET",**{"SCREENPAGE":self,"XMLNODE":oXMLNode,"ANCHOR":uAnchor,"WIDGET":oTmpWidget})
            if Ret is None:
                Logger.error("Unknown Widget Type %s : Page: %s" % (oTmpWidget.uTypeString, self.uPageName))
                return False
        return False

    def Create(self):
        #create the Screen as a kivy screen object and add it the root (Screen Manager)
        try:
            if self.bIsInit:
                return

            Logger.debug (u'ScreenPage: Creating Page: '+self.uPageName)

            if not self.bIsPopUp:
                self.oScreen = Screen()
                self.oScreen.name = self.uPageName
                Globals.oTheScreen.oRootSM.add_widget(self.oScreen)
            else:
                self.oScreen= Widget()
                Globals.oTheScreen.dPopups[self.uPageName]=self.oScreen

            self.oWidgetBackGround.Create(self.oScreen)

            ErrorWidgets=[]
            #Create all the widgets of the page
            for oWidget in self.aWidgets:
                if not oWidget.Create(self.oWidgetBackGround.oObject):
                    ErrorWidgets.append(oWidget)

            for oWidget in ErrorWidgets:
                self.aWidgets.remove(oWidget)

            self.bIsInit=True

        except Exception as e:
            uMsg=LogError(u'ScreenPage: can\'t Create Page [%s]:' % (self.uPageName),e)
            ShowErrorPopUp(uMessage=uMsg)

    def UpdateSetupWidgets(self):
        #Updates all widgets of a page
        #Its safe to call create again, in case, it did'nt happen by now
        self.Create()
        for oWidget in self.aWidgets:
            if oWidget.iWidgetType==oWidgetType.Settings:
                oWidget.UpdateWidget()

    def GetGestureAction(self,uGestureName):
        #return the gesture object to a given gesture name
        return self.dGestures.get(uGestureName)

    def SetTransmitterPicture(self,uTransmitterPictureName):
        #Sets the to use transmitter picture for interface activities
        for oWidget in self.aWidgets:
            if oWidget.uName == uTransmitterPictureName:
                if oWidget.iWidgetType==oWidgetType.Picture:
                    self.oWidgetPictureTransmit = oWidget

    def SetWaitPicture(self,uWaitPictureName):
        #Sets the to use wait picture for interface activities
        for oWidget in self.aWidgets:
            if oWidget.uName == uWaitPictureName:
                if oWidget.iWidgetType==oWidgetType.Picture:
                    self.oWidgetPictureWait = oWidget

    def OnKey(self,window,uKey):

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

