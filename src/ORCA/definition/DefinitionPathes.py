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
import ORCA.Globals as Globals
from ORCA.utils.FileName   import cFileName
from ORCA.vars.Access      import SetVar

__all__ = ['cDefinitionPathes']

class cDefinitionPathes(object):
    """ Class , which is a representation of all pathes of a definition """
    def __init__(self, uDefinitionName, uDefinitionPathName=u""):
        if Globals.uDeviceOrientation == 'landscape':
            uAdd = 'l'
        else:
            uAdd = 'p'
        if Globals.fScreenSize<5.1:
            uAdd += 's'
        else:
            uAdd += 'l'

        if uDefinitionPathName==u"":
            self.oPathDefinition = Globals.oPathDefinitionRoot + uDefinitionName
        else:
            self.oPathDefinition = Globals.oPathDefinitionRoot + uDefinitionPathName

        self.oPathDefinitionAtlas               = self.oPathDefinition + 'atlas'
        self.oFnDefinitionAtlas                 = cFileName(self.oPathDefinitionAtlas) + u'definition.atlas'
        self.oFnDefinitionLocalFont             = cFileName(self.oPathDefinition + u'fonts') + 'fonts.xml'
        self.oFnDefinition                      = cFileName(self.oPathDefinition) + u'definition.xml'
        self.oFnDefinitionCache                 = cFileName(self.oPathDefinition) + (u'cache_' + uAdd + '.xml')
        self.oFnDefinitionIni                   = cFileName(self.oPathDefinition) + u'definition.ini'
        self.oPathDefinitionInterfaceSettings   = self.oPathDefinition + u'interfacesettings'
        self.oPathDefinitionScriptSettings      = self.oPathDefinition + u'scriptsettings'
        self.oFnDefinitionLanguage              = None
        self.oFnDefinitionLanguageFallBack      = cFileName(self.oPathDefinition + u'languages/English')+ "strings.xml"
        self.oPathDefinitionSkinElements        = self.oPathDefinition + u'elements'
        oPathCheck = self.oPathDefinitionSkinElements + ("skin_" + Globals.uSkinName)
        if oPathCheck.Exists():
            self.oPathDefinitionSkinElements = oPathCheck
        else:
            self.oPathDefinitionSkinElements = self.oPathDefinitionSkinElements + "skin_default"

        self.LanguageChange()

    def LanguageChange(self):
        self.oFnDefinitionLanguage            = cFileName(self.oPathDefinition + (u'languages/' + Globals.uLanguage)) + u'strings.xml'
