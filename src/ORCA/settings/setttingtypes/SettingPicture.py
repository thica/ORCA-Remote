# -*- coding: utf-8 -*-
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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


from kivy.logger                        import Logger
from kivy.uix.floatlayout               import FloatLayout
from kivy.uix.image                     import Image

from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs
from ORCA.utils.Atlas                   import ToAtlas
from ORCA.utils.TypeConvert             import ToUnicode
from ORCA.settings.setttingtypes.SettingFile import SettingFile
from ORCA.utils.TypeConvert         import UnEscapeUnicode
from ORCA.utils.TypeConvert         import EscapeUnicode
from ORCA.utils.FileName import cFileName


from ORCA.Globals import Globals

__all__ = ['SettingPicture']

class SettingPicture(SettingFile):
    """ let the user select a picture from a folder """
    def __init__(self, **kwargs):

        self.oLayout:FloatLayout = FloatLayout(size_hint=(1, 1))
        super(SettingPicture, self).__init__(**RemoveNoClassArgs(dInArgs=kwargs,oObject=SettingFile))
        oFnPic:cFileName = cFileName()

        try:
            oFnPic              = cFileName().ImportFullPath(uFnFullName=self.value)
            self.oPic:Image     = Image(source=UnEscapeUnicode(ToAtlas(oFileName=oFnPic)),size_hint=(1, 1), pos_hint={'x':0.0, 'y':0.0})
            oFnBack:cFileName   = cFileName(Globals.oPathResources + 'pics') + 'imagepicker_background.png'
            self.oBack:Image    = Image(source=ToAtlas(oFileName=oFnBack),size_hint=(1, 1), pos_hint={'x':0.0, 'y':0.0})
            self.oLayout.add_widget(self.oBack)
            self.oLayout.add_widget(self.oPic)
            self.add_widget(self.oLayout)
            self.content.children[1].text=''
        except Exception as e:
            uMsg=f'Settings: Picture: can\'t load image file: {ToUnicode(e)} File: {oFnPic}'
            Logger.error (uMsg)

    def set_value(self, section, key, value):
        value=EscapeUnicode(value)
        return super().set_value(section, key, value)


    def _validate(self, instance) -> None:
        """ displays the folder """

        SettingFile._validate(self,instance)
        self.oPic.source=ToAtlas(oFileName=cFileName(self.value))
        self.content.children[1].text=''

