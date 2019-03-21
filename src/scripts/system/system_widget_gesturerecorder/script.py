# -*- coding: utf-8 -*-
#

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

from ORCA.scripttemplates.Template_System   import cSystemTemplate
from kivy.gesture                           import GestureDatabase
from kivy.graphics                          import Color
from kivy.graphics                          import Ellipse
from kivy.graphics                          import Line

from ORCA.widgets.core.TouchRectangle       import cTouchRectangle
from ORCA.widgets.core.ButtonBehaviour      import simplegesture
from ORCA.widgets.Base                      import cWidgetBase

import ORCA.Globals as Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>Widget Gesturerecorder</name>
      <description language='English'>Additional Widget to record gestures</description>
      <description language='German'>Zusätzliches Widgets um Gesten aufzuzeichnen</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/system/system_widget_gesturerecorder</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/system_widget_gesturerecorder.zip</sourcefile>
          <targetpath>scripts/system</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/system/system_widget_gesturerecorder/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


class cGestureBoard(cTouchRectangle):
    """ base class for recording gestures """
    def __init__(self, **kwargs):
        super(cGestureBoard, self).__init__(**kwargs)
        self.gdb = GestureDatabase()

    def on_touch_down(self, touch):

        #self.DrawStandardGestures()
        # start collecting points in touch.ud
        # create a line to display the points

        if not self.collide_point(touch.x, touch.y):
            return False
        touch.grab(self)

        userdata = touch.ud
        with self.canvas:
            Color(1, 1, 0)
            d = 10.
            Ellipse(pos=(touch.x - d/2, touch.y - d/2), size=(d, d))
            userdata['line'] = Line(points=(touch.x, touch.y))
        return True

    def on_touch_move(self, touch):

        if touch.grab_current is not self:
            return

        # store points of the touch movement
        try:
            touch.ud['line'].points += [touch.x, touch.y]
            return True
        except KeyError:
            pass
        return True

    def on_touch_up(self, touch):

        if touch.grab_current is not self:
            return

        g = simplegesture('',zip(touch.ud['line'].points[::2], touch.ud['line'].points[1::2]))
        # print "gesture representation:", ':',self.gdb.gesture_to_str(g)
        uLogName=Globals.oFnGestureLog.string

        oLogFile = open(uLogName, 'a')
        oLogFile.write('Gesturecode:'+self.gdb.gesture_to_str(g)+'\n')
        oLogFile.close()
        return True


class cWidgetGestureRecorder(cWidgetBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-GESTURERECORDER
    WikiDoc:TOCTitle:GestureRecorder
    = GESTURERECORDER =

    The GestureRecorder widget lets the user record gestures. This is a more like internal widget

    There are no further attributes to the common widget attributes

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "GESTURERECORDER". Capital letters!
    |}</div>

    Below you see an example for a gesturerecorder widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='GestureRecorder' type='GESTURERECORDER' posx="center" posy="middle" width="%90" height="%90" backgroundcolor='#454545ff' />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self, **kwargs):
        super(cWidgetGestureRecorder, self).__init__(**kwargs)

    def InitWidgetFromXml(self,oXMLNode,oParentScreenPage, uAnchor):
        """ Reads further Widget attributes from a xml node """
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Create(self,oParent):
        """ creates the Widget """

        if self.CreateBase(Parent=oParent,Class=cGestureBoard):
            self.oParent.add_widget(self.oObject)
            return True
        return False



class cScript(cSystemTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-system-widget-gesturereorder
    WikiDoc:TOCTitle:Script Widget Gesturerecorder
    = Widget extension for the gesture recoder converter =

    This script provides a further widget, used by the gesture recoder converter tool
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |cmd_type
    |The requested helper function: Only "Register" od "UnRegister"
    |}</div>

    WikiDoc:End
    """

    def __init__(self):
        cSystemTemplate.__init__(self)
        self.uSubType       = u'WIDGET'
        self.uSortOrder     = u"auto"

    def RunScript(self, *args, **kwargs):
        Globals.oNotifications.RegisterNotification("UNKNOWNWIDGET",fNotifyFunction=self.AddWidgetFromXmlNode,uDescription="Script Widget GestureRecorder")

    def AddWidgetFromXmlNode(self,*args,**kwargs):
        oScreenPage = kwargs.get("SCREENPAGE")
        oXMLNode    = kwargs.get("XMLNODE")
        uAnchor     = kwargs.get("ANCHOR")
        oWidget     = kwargs.get("WIDGET")

        if uAnchor is None or oScreenPage is None or oXMLNode is None or oWidget is None:
            return None

        if oWidget.uTypeString != "GESTURERECORDER":
            return None

        Ret = oScreenPage._AddWidgetFromXmlNode_Class(oXMLNode=oXMLNode,  uAnchor=uAnchor,oClass=cWidgetGestureRecorder)
        return {"ret":Ret}

