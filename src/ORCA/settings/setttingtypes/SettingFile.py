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
from os.path                        import split

from kivy.uix.boxlayout             import BoxLayout
from kivy.uix.popup                 import Popup

from kivy.uix.screenmanager         import FadeTransition
from kivy.uix.settings              import SettingPath
from ORCA.utils.FileName            import cFileName
from ORCA.vars.Replace              import ReplaceVars
from ORCA.widgets.core.FileBrowser  import FileBrowser

import ORCA.Globals as Globals

__all__ = ['SettingFile']

class SettingFile(SettingPath):
    """ A setting item as file picker """
    def _create_popup(self, instance):
        """ create popup layout """
        uRoot:str
        uName:str
        oContent:BoxLayout = BoxLayout(orientation='vertical', spacing=5)
        self.popup = popup = Popup(title=self.title, content=oContent, size_hint=(0.95, 0.95))

        # create the filechooser
        uRoot, uName = split(self.value)
        uRoot = ReplaceVars(uRoot)
        self.textinput = textinput = FileBrowser(select_string     = ReplaceVars('$lvar(563)'),
                                                 cancel_string     = ReplaceVars('$lvar(5009)'),
                                                 libraries_string  = ReplaceVars('$lvar(5018)'),
                                                 favorites_string  = ReplaceVars('$lvar(5019)'),
                                                 computer_string   = ReplaceVars('$lvar(5020)'),
                                                 location_string   = ReplaceVars('$lvar(5021)'),
                                                 listview_string   = ReplaceVars('$lvar(5022)'),
                                                 iconview_string   = ReplaceVars('$lvar(5023)'),
                                                 path              = uRoot, dirselect=False,
                                                 transition        = FadeTransition(),
                                                 size_hint         = (1, 1),
                                                 favorites         = [(Globals.oPathRoot.string, 'ORCA')],
                                                 show_fileinput    = False,
                                                 show_filterinput  = False
                                                 )

        # construct the content
        oContent.add_widget(textinput)
        textinput.bind(on_success=self._validate,on_canceled=self._dismiss)

        # all done, open the popup !
        popup.open()

    def _validate(self, instance:FileBrowser):
        """ user selected something """
        uValue:str
        if len(instance.selection)==0:
            self._dismiss()
            return
        uValue=(cFileName().ImportFullPath(instance.selection[0])).string
        uValue=uValue.replace(Globals.oPathSkin.string,                           '$var(SKINPATH)')
        uValue=uValue.replace(Globals.oPathResources.string,                      '$var(RESOURCEPATH')
        uValue=uValue.replace(Globals.oDefinitionPathes.oPathDefinition.string,   '$var(DEFINITIONPATH)')
        uValue=uValue.replace(str(Globals.iVersion),                              '$var(REPVERSION)')
        uValue=uValue.replace('\\',"/")
        self.value=uValue
        super()._validate(instance)
