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

from typing import Union
from kivy.uix.boxlayout                 import BoxLayout
from kivy.uix.popup                     import Popup
from kivy.uix.textinput                 import TextInput
from kivy.uix.widget                    import Widget
from kivy.uix.slider                    import Slider
from kivy.uix.settings                  import SettingNumeric

from ORCA.utils.TypeConvert             import ToFloat
from ORCA.utils.TypeConvert             import ToUnicode
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.vars.Helpers import Round
from ORCA.widgets.core.MultiLineButton  import cMultiLineButton

from ORCA.settings.setttingtypes.Base import SettingSpacer

__all__ = ['SettingNumericSlider']


class SettingNumericSlider(SettingNumeric):
    """ An setting item, which has a slider to input a numeric value """
    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        super().__init__(**RemoveNoClassArgs(kwargs,SettingNumeric))
        self.fMin:float                         = ToFloat(kwargs["min"])
        self.fMax:float                         = ToFloat(kwargs["max"])
        self.iRoundPos:int                      = int(kwargs["roundpos"])
        self.slider:Union[Slider:None]          = None
        self.textvalue:Union[TextInput,None]    = None

    def _create_popup(self, instance) -> None:
        """ create popup layout """
        oBtn:cMultiLineButton
        oContent:BoxLayout = BoxLayout(orientation='vertical', spacing='5dp')
        self.popup = popup = Popup(title=self.title,content=oContent, size_hint=(None, None), size=('400dp', '250dp'))

        # Create the slider used for numeric input
        self.slider = oSlider = Slider(min=self.fMin, max=self.fMax, value=float(self.value),size_hint_y=None, height='50dp')
        oSlider.bind(on_touch_move = self.OnSliderMoved)
        oSlider.bind(on_touch_up = self.OnSliderMoved)
        self.textvalue = TextInput(size_hint_y=None, height='30dp',multiline=False, )
        self.textvalue.bind(on_text_validate = self.On_Enter)
        self.textvalue.bind(focus=self.On_Focus)

        # construct the content, widget are used as a spacer
        oContent.add_widget(Widget())
        oContent.add_widget(oSlider)
        oContent.add_widget(Widget())
        oContent.add_widget(self.textvalue)
        oContent.add_widget(Widget())
        oContent.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        oBtnlayout:BoxLayout  = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        oBtn                  = cMultiLineButton(text=ReplaceVars('$lvar(5008)'), halign='center', valign='middle')
        oBtn.bind(on_release=self._validate)
        oBtnlayout.add_widget(oBtn)
        oBtn = cMultiLineButton(text=ReplaceVars('$lvar(5009)'), halign='center', valign='middle')
        oBtn.bind(on_release=self._dismiss)
        oBtnlayout.add_widget(oBtn)
        oContent.add_widget(oBtnlayout)

        self.textvalue.text=str(self.value)
        # all done, open the popup !
        popup.open()

    def _validate(self, instance) -> None:
        """ returns the value of the slider """
        self._dismiss()
        self.value = ToUnicode(Round(self.slider.value,self.iRoundPos))

    # noinspection PyUnusedLocal
    def OnSliderMoved(self,instance:Slider,touch) -> None:
        """ updates the text value, whne the slider is moved """
        self.textvalue.text=ToUnicode(Round(instance.value,self.iRoundPos))

    def On_Enter(self,instance:TextInput) -> None:
        """  when the user enters a value without slider """
        try:
            fValue=float(instance.text)
            if fValue<self.slider.min:
                fValue=self.slider.min
            if fValue>self.slider.max:
                fValue=self.slider.max
            fValue=Round(fValue,self.iRoundPos)
            self.slider.value=float(fValue)
            self.textvalue.text=ToUnicode(fValue)

        except Exception:
            pass

    # noinspection PyUnusedLocal
    def On_Focus(self,instance:TextInput, value:str) -> None:
        """ updates the slider, when the textfield gets the focus """
        self.On_Enter(self.textvalue)

