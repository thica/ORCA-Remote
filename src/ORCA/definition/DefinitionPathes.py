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
import ORCA.Globals as Globals
from ORCA.utils.FileName   import cFileName
from ORCA.utils.Path       import cPath
from ORCA.vars.Access       import SetVar

__all__ = ['cDefinitionPathes']

class cDefinitionPathes:
    """ Class , which is a representation of all pathes of a definition """
    def __init__(self, uDefinitionName:str, uDefinitionPathName:str=u"") -> None:
        uAdd:str
        self.oPathDefinition:cPath
        self.oPathDefinitionSkinElements:cPath
        oPathCheck:cPath
        uCheck:str

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

        self.oPathDefinitionAtlas:cPath                 = self.oPathDefinition + 'atlas'
        self.oFnDefinitionAtlas:cFileName               = cFileName(self.oPathDefinitionAtlas) + u'definition.atlas'
        self.oFnDefinitionLocalFont:cFileName           = cFileName(self.oPathDefinition + u'fonts') + 'fonts.xml'
        self.oFnDefinition:cFileName                    = cFileName(self.oPathDefinition) + u'definition.xml'
        self.oFnDefinitionCache:cFileName               = cFileName(self.oPathDefinition) + (u'cache_' + uAdd + '.xml')
        self.oFnDefinitionIni:cFileName                 = cFileName(self.oPathDefinition) + u'definition.ini'
        self.oPathDefinitionInterfaceSettings:cPath     = self.oPathDefinition + u'interfacesettings'
        self.oPathDefinitionScriptSettings:cPath        = self.oPathDefinition + u'scriptsettings'
        self.oFnDefinitionLanguage:cFileName            = cFileName()
        self.oFnDefinitionLanguageFallBack:cFileName    = cFileName(self.oPathDefinition + u'languages/English')+ "strings.xml"
        self.oPathDefinitionSkinElements:cPath          = self.oPathDefinition + u'elements'
        self.oPathTemplateSkinElements:cFileName        = cFileName()

        uCheck = "skin_" + Globals.uSkinName
        oPathCheck = self.oPathDefinitionSkinElements + uCheck
        if oPathCheck.Exists():
            self.oPathDefinitionSkinElements = oPathCheck
            SetVar("SKINCONTEXT",uCheck)
        else:
            self.oPathDefinitionSkinElements = self.oPathDefinitionSkinElements + "skin_default"
            SetVar("SKINCONTEXT", "skin_default")

        self.LanguageChange()

        if uDefinitionName in Globals.oDefinitions.dDefinitionList_Dict:
            if "definition_templatename_mediaplayer_wizard" in Globals.oDefinitions.dDefinitionList_Dict[uDefinitionName].oDefinitionVars:
                oPathCheck = Globals.oPathWizardTemplates +(Globals.oDefinitions.dDefinitionList_Dict[uDefinitionName].oDefinitionVars["definition_templatename_mediaplayer_wizard"]+"/elements/" +uCheck)
                if oPathCheck.Exists():
                    self.oPathTemplateSkinElements = oPathCheck
                    SetVar("MEDIATEMPLATESKINCONTEXT",uCheck)
                else:
                    self.oPathDefinitionSkinElements = Globals.oPathWizardTemplates +(Globals.oDefinitions.dDefinitionList_Dict[uDefinitionName].oDefinitionVars["definition_templatename_mediaplayer_wizard"]+"/elements/" + "skin_default")
                    SetVar("MEDIATEMPLATESKINCONTEXT", "skin_default")


    def LanguageChange(self) -> None:
        self.oFnDefinitionLanguage            = cFileName(self.oPathDefinition + (u'languages/' + Globals.uLanguage)) + u'strings.xml'
