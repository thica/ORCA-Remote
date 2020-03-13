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

from typing import Union
from typing import List

from kivy.uix.scrollview                import ScrollView
from kivy.uix.gridlayout                import GridLayout
from kivy.uix.popup                     import Popup
from kivy.uix.togglebutton              import ToggleButton
from kivy.uix.textinput                 import TextInput
from kivy.uix.widget                    import Widget
from kivy.uix.settings                  import SettingOptions
from kivy.metrics                       import dp

from ORCA.utils.Path                    import cPath
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.vars.Actions import Var_GetArray
from ORCA.widgets.core.MultiLineButton  import cMultiLineButton

from ORCA.settings.setttingtypes.Base   import GetActionList
from ORCA.settings.setttingtypes.Base   import GetGestureList
from ORCA.settings.setttingtypes.Base   import GetLanguageList
from ORCA.settings.setttingtypes.Base   import GetPageList
from ORCA.settings.setttingtypes.Base   import GetSendActionList
from ORCA.settings.setttingtypes.Base   import SettingSpacer
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs

import ORCA.Globals as Globals

__all__ = ['SettingScrollOptions',
           'ScrollOptionsPopUp']

class ScrollOptionsPopUp:
    """ Core Scroll Popup """
    def __init__(self, **kwargs):
        self.bNoValueChange:bool                        = False
        self.bAllWaysOnChange:bool                      = False
        self.bAddInputField:bool                        = False
        self.bIsLanguageInput:bool                      = False
        self.bStopVarTrigger:bool                       = False
        self.bIsOpen:bool                               = False
        self.oButtonCancel:Union[cMultiLineButton,None] = None
        self.oTextInput:Union[TextInput,None]           = None
        self.oContent:Union[GridLayout,None]            = None
        self.popup:Union[Popup,None]                    = None
        self.value:str                                  = kwargs.get('value','')
        self.title:str                                  = kwargs.get('title','')
        self.options:List[str]                          = kwargs.get('options','')

        if len(self.options)>0:
            if self.options[0]=="$LANGUAGELIST":
                self.bIsLanguageInput=True

        uRet=kwargs.get('novaluechange')
        if uRet:
            self.bNoValueChange=(uRet=='1')
            self.uOrgValue=self.value

        self.bAllWaysOnChange=(kwargs.get('alwaysonchange',0)=="1")
        self.bAddInputField=(kwargs.get('allowtextinput',0)=="1")
        self.oButtonHeigth=dp(55)

        self.bStopVarTrigger = True
        self.value=self.UnhideLanguageVars(self.value)

        ''' Show text of language vars '''
        if self.value.startswith(u'$lvar(') and self.value.endswith(u')') and ":::" not in self.value:
            self.value="%s [[%s]]" % (ReplaceVars(self.value),self.value[self.value.find("(")+1:-1])

        if ":::" in self.value:
            aValues=self.value.split(":::")
            self.value=""
            for uValue in aValues:
                if uValue.startswith(u'$lvar(') and uValue.endswith(u')'):
                    self.value+="%s [[%s]]" % (ReplaceVars(uValue),uValue[uValue.find("(")+1:-1])+":::"
                else:
                    self.value+=uValue+":::"
            self.value=self.value[:-3]

        self.bStopVarTrigger = False
        Globals.oNotifications.RegisterNotification(uNotification="on_key",fNotifyFunction=self.ClosePopUpbyESC,uDescription= "Close Settings Popup",aValueLinks=[{"in":"key","out":"key"}])

    def CreatePopup(self, uValue, fktButttonSelect, fktTextInputSelect):

        """ create the popup """
        self.oContent:GridLayout           = GridLayout(cols=1, spacing='5dp')
        oScrollview:ScrollView             = ScrollView( do_scroll_x=False, bar_width='10dp',scroll_type=['bars','content'] )
        oScrollcontent:GridLayout          = GridLayout(cols=1,  spacing='5dp', size_hint=(None, None))
        oScrollcontent.bind(minimum_height = oScrollcontent.setter('height'))
        if Globals.uDeviceOrientation == u'landscape':
            self.popup = Popup(content=self.oContent, title=self.title, size_hint=(0.5, 0.9),  auto_dismiss=False)
        else:
            self.popup = Popup(content=self.oContent, title=self.title, size_hint=(0.9, 0.9),  auto_dismiss=False)

        self.popup.bind(on_dismiss=self.OnClose)
        self.popup.bind(on_open=self.OnOpen)

        #we need to open the popup first to get the metrics
        self.popup.open()
        #Add some space on top
        self.oContent.add_widget(Widget(size_hint_y=None, height=dp(2)))

        # add an inputfield if requested
        if self.bAddInputField:
            self.oTextInput = TextInput(text=uValue, size_hint_y=None, height='30dp',multiline=False, )
            self.oTextInput.bind(on_text_validate=fktTextInputSelect)
            self.oContent.add_widget(self.oTextInput)
            self.oContent.add_widget(SettingSpacer())

        # we test if we want to show some special list
        if len(self.options)>0:
            if self.options[0]=="$LANGUAGELIST":
                self.options=GetLanguageList()
                self.oButtonHeigth=dp(30)
            elif self.options[0]=="$GESTURESLIST":
                self.options=GetGestureList()
            elif self.options[0]=="$PAGELIST":
                self.options=GetPageList()
            elif self.options[0]=="$ACTIONLIST":
                self.options=GetActionList()
                self.oButtonHeigth=dp(30)
            elif self.options[0]=="$ACTIONLISTSEND":
                self.options=GetSendActionList()
                self.oButtonHeigth=dp(30)
            elif self.options[0].startswith("$DIRLIST["):
                uPath=self.options[0][9:-1]
                aFiles= cPath(uPath).GetFolderList()
                aRet=[]
                for uFile in aFiles:
                    aRet.append(uFile)
                aRet.sort()
                self.options=aRet
            elif self.options[0].startswith("$FILELIST["):
                uPath=self.options[0][10:-1]
                aFiles= cPath(uPath).GetFileList()
                aRet=[]
                for uFile in aFiles:
                    aRet.append(uFile)
                aRet.sort()
                self.options=aRet
            elif self.options[0].endswith("[]"):
                aRetTmp = Var_GetArray(uVarName = self.options[0] , iLevel = 1)
                aRet = [ReplaceVars(u"$var("+item+")") for item in aRetTmp]
                aRet.sort()
                self.options=aRet

        uid = "test"
        for option in self.options:
            state = 'down' if option == uValue else 'normal'
            btn = ToggleButton(text=option, state=state, group=uid, size=(self.popup.width, self.oButtonHeigth), size_hint=(None, None),text_size=(self.popup.width, self.oButtonHeigth), valign="middle",halign="center")
            btn.bind(on_release=fktButttonSelect)
            oScrollcontent.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        oScrollview.add_widget(oScrollcontent)
        self.oContent.add_widget(oScrollview)
        self.oContent.add_widget(SettingSpacer())
        self.oButtonCancel = cMultiLineButton(text=ReplaceVars('$lvar(5009)'), size=(self.popup.width, dp(50)),size_hint=(0.9, None), halign='center', valign='middle')
        self.oButtonCancel .bind(on_release=self.popup.dismiss)
        self.oContent.add_widget(self.oButtonCancel)

    # noinspection PyUnusedLocal
    def OnClose(self,oPupup:Popup) -> bool:
        self.bIsOpen = False
        return False

    # noinspection PyUnusedLocal
    def OnOpen(self,oPupup:Popup) -> None:
        self.bIsOpen = True
        return None


    def ClosePopUpbyESC(self,**kwargs):
        if kwargs["key"]=="ESC":
            if self.popup:
                    if self.bIsOpen:
                        self.popup.dismiss()
                        return {}
        return kwargs

    def CleanUpLanguageVars(self, uValue:str) -> str:
        """ Hides the added Language string (only the $var will left) """

        if self.bIsLanguageInput:
            if "[[" in uValue and uValue.endswith("]]") and not ":::" in uValue:
                uValue="$lvar(%s)" % (uValue[uValue.find("[[")+2:-2])
            if ":::" in uValue:
                aValues=uValue.split(":::")
                uValue=""
                for uSValue in aValues:
                    if "[[" in uSValue and uSValue.endswith("]]"):
                        uValue+="$lvar(%s)" % (uSValue[uSValue.find("[[")+2:-2])+":::"
                    else:
                        uValue+=uSValue+":::"
                uValue=uValue[:-3]

        return uValue

    # noinspection PyMethodMayBeStatic
    def UnhideLanguageVars(self, uValue:str) -> str:
        """ Show text of language vars """
        if uValue.startswith(u'$lvar(') and uValue.endswith(u')') and not ":::" in uValue:
            return "%s [[%s]]" % (ReplaceVars(uValue),uValue[uValue.find("(")+1:-1])
        return uValue

class SettingScrollOptions(SettingOptions):
    """ Like the kivy options, but with scrollable layout """
    def __init__(self, **kwargs):
        self.bInitComplete=False
        self.oScrollOptionsPopup=ScrollOptionsPopUp(**kwargs)
        super(SettingScrollOptions, self).__init__(**RemoveNoClassArgs(dInArgs=kwargs,oObject=SettingOptions))
        self.bInitComplete=True

    def _create_popup(self, instance) -> None:
        self.oScrollOptionsPopup.CreatePopup(self.value,self._set_option,self.OnTextInput)
        self.popup=self.oScrollOptionsPopup.popup

    def on_value(self, instance, value) -> None:

        if self.oScrollOptionsPopup.bStopVarTrigger:
            return

        if not self.bInitComplete:
            ''' Show text of language vars '''
            self.value=self.oScrollOptionsPopup.UnhideLanguageVars(value)
            return

        value=self.oScrollOptionsPopup.CleanUpLanguageVars(value)

        if (not self.oScrollOptionsPopup.bAllWaysOnChange) and (not self.oScrollOptionsPopup.bNoValueChange):
            super(SettingScrollOptions, self).on_value(instance, value)
            return

        panel=self.panel

        if not isinstance(value, str):
            value = str(value)

        #if self.oScrollOptionsPopup.bAllWaysOnChange and (self.oScrollOptionsPopup.value==value):
        if self.oScrollOptionsPopup.bAllWaysOnChange:
            panel.settings.dispatch('on_config_change',panel.config, self.section, self.key, value)
            # panel.config._do_callbacks(self.section, self.key, value)

        if self.oScrollOptionsPopup.bNoValueChange:
            self.value=self.oScrollOptionsPopup.uOrgValue

    def OnTextInput(self, instance):
        """ called when we have a text input field, and the user made an input """
        instance.text=self.oScrollOptionsPopup.oTextInput.text.strip()
        self._set_option( instance)

