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
from typing                            import Dict
from enum                              import Enum
from enum                              import auto

__all__ = ['eWidgetType','dWidgetTypeToId']

class eWidgetType(Enum):
    """
    Helper Class to enumerate through widget names
    """
    ERROR           = auto()
    NoWidget        = auto()
    BackGround      = auto()
    TextField       = auto()
    Button          = auto()
    Picture         = auto()
    Anchor          = auto()
    TextInput       = auto()
    Knob            = auto()
    FileViewer      = auto()
    Slider          = auto()
    Rectangle       = auto()
    Circle          = auto()
    Video           = auto()
    DropDown        = auto()
    ColorPicker     = auto()
    Settings        = auto()
    Switch          = auto()
    SkipWidget      = auto()
    FileBrowser     = auto()
    ScrollContainer = auto()
    Border          = auto()

    def __str__(self):
        return str(self.value)

dWidgetTypeToId:Dict[str,eWidgetType] = {}
for uName, eValue in eWidgetType.__members__.items():
    dWidgetTypeToId[uName.upper()] = eValue

