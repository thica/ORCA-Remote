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

from colorsys                      import hsv_to_rgb

from kivy.clock                    import Clock
from kivy.graphics                 import Color
from kivy.logger                   import Logger
from kivy.uix.boxlayout            import BoxLayout

from ORCA.utils.TypeConvert        import ToFloat
from ORCA.utils.XML                import GetXMLTextAttribute
from ORCA.vars.Access              import GetVar
from ORCA.vars.Access              import SetVar
from ORCA.widgets.Base             import cWidgetBase
from ORCA.widgets.Base             import GetColorFromHex
from ORCA.widgets.core.ColorPicker import cColorPicker

__all__ = ['cWidgetColorPicker']


class cWidgetColorPicker(cWidgetBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-COLORPICKER
    WikiDoc:TOCTitle:Colorpicker
    = Colorpicker =

    The Coloricker shows a complex widget to let the user chose a color from a colorwheel or by sliders. The value is returned into a user variable. You can update the colorpicker as well, by changing the assigned user variable and then call the updatewidget action.
    You can specify an action as well which is called. when the user changes the color
    The following attributes are additional attributes to common widget attributes
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "COLORPICKER". Capital letters!
    |-
    |destvar
    |The destinatio var for the colorpicker value. The dafault variable name is 'colorpicker'.
    |}</div>

    Below you see an example for a colorpicker widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="ColorPicker HUE" type="COLORPICKER" posx="%15" posy='of:totop:Anchor BottomGap' width="%30" height="%85" destvar="hue" action="$dvar(definition_alias_philips_hue) Set Lights Philips Hue by Widget" />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super(cWidgetColorPicker, self).__init__(**kwargs)
        self.fOldValue                  = 10000.23445
        self.fValue                     = 0
        self.oTrigger                   = Clock.create_trigger(self.On_Color_Wheel)
        self.uDestVar                   = u''
        self.oObjectColorPicker         = cColorPicker()

    def InitWidgetFromXml(self,oXMLNode,oParentScreenPage, uAnchor):
        """ Reads further Widget attributes from a xml node """
        self.uDestVar                   = GetXMLTextAttribute(oXMLNode,u'destvar',    False,u'colorpicker')
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Create(self,oParent):
        """ creates the Widget """
        if self.CreateBase(Parent=oParent,Class=BoxLayout):
            self.oParent.add_widget(self.oObject)
            self.oObject.add_widget(self.oObjectColorPicker)
            #self.oObjectColorPicker.bind(on_colorset= self.On_Color_Wheel)
            self.oObjectColorPicker.bind(on_colorset= self.oTrigger)
            #self.oObjectColorPicker.bind(color=self.oTrigger)
            self.UpdateWidget()
            return True
        return False

    def On_Color_Wheel(self, *largs):
        """ updates the deasvars, of the colorpicker color has changed """
        instance=self.oObjectColorPicker
        self.fValue = instance.hex_color
        if self.uDestVar:
            SetVar(uVarName = self.uDestVar, oVarValue = self.fValue )
            SetVar(uVarName = self.uDestVar+"_hex", oVarValue = self.fValue )
            h,s,v=instance.hsv[0],instance.hsv[1],instance.hsv[2]

            SetVar(uVarName = self.uDestVar+"_h", oVarValue = str(int(h*255)))
            SetVar(uVarName = self.uDestVar+"_s", oVarValue = str(int(s*255)))
            SetVar(uVarName = self.uDestVar+"_v", oVarValue = str(int(v*255)))

            SetVar(uVarName = self.uDestVar+"_r", oVarValue = str(int(instance.color[0]*255) ))
            SetVar(uVarName = self.uDestVar+"_g", oVarValue = str(int(instance.color[1]*255) ))
            SetVar(uVarName = self.uDestVar+"_b", oVarValue = str(int(instance.color[2]*255) ))
            SetVar(uVarName = self.uDestVar+"_a", oVarValue = str(int(instance.color[3]*255) ))

            Logger.debug("Setting Var:"+self.uDestVar+"="+str(self.fValue))
            Logger.debug("Setting Var:"+self.uDestVar+"_hex"+"="+str(self.fValue))
            Logger.debug("Setting Var:"+self.uDestVar+"_h"+"="+str(str(int(h*255))))
            Logger.debug("Setting Var:"+self.uDestVar+"_s"+"="+str(str(int(s*255))))
            Logger.debug("Setting Var:"+self.uDestVar+"_v"+"="+str(str(int(v*255))))

            Logger.debug("Setting Var:"+self.uDestVar+"_r"+"="+str(int(instance.color[0]*255)))
            Logger.debug("Setting Var:"+self.uDestVar+"_g"+"="+str(int(instance.color[1]*255)))
            Logger.debug("Setting Var:"+self.uDestVar+"_b"+"="+str(int(instance.color[2]*255)))
            Logger.debug("Setting Var:"+self.uDestVar+"_a"+"="+str(int(instance.color[3]*255)))

            #SetVar(self.uDestVar+"_rgba",instance.color)

        if self.uActionName:
            if self.fOldValue != self.fValue:
                self.fOldValue = self.fValue
                self.On_Button_Up(instance)

    def UpdateWidget(self):

        if not self.uDestVar==u'':

            h=GetVar(uVarName = self.uDestVar+u'_h')
            s=GetVar(uVarName = self.uDestVar+u'_s')
            v=GetVar(uVarName = self.uDestVar+u'_v')

            r=''

            if h!='':
                h=ToFloat(h)/255
                s=ToFloat(s)/255
                v=ToFloat(v)/255
                r,g,b=hsv_to_rgb(h,s,v)
            else:
                r=GetVar(uVarName = self.uDestVar+u'_r')
                g=GetVar(uVarName = self.uDestVar+u'_g')
                b=GetVar(uVarName = self.uDestVar+u'_b')

            if r=='':
                oColor=GetColorFromHex(GetVar(uVarName = self.uDestVar))
                if len(oColor)==0:
                    oColor= Color(1, 1, 1, 1)
                else:
                    r,g,b,a=GetColorFromHex(GetVar(uVarName = self.uDestVar))

            if r!='':
                r = ToFloat(r) / 255
                g = ToFloat(g) / 255
                b = ToFloat(b) / 255
                self.oObjectColorPicker.color=(r,g,b,1)
