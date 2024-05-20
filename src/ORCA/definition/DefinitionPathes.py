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
from ORCA.Globals import Globals
from ORCA.utils.FileName   import cFileName
from ORCA.utils.Path       import cPath
from ORCA.vars.Access       import SetVar

__all__ = ['cDefinitionPathes']

class cDefinitionPathes:
    """ Class , which is a representation of all pathes of a definition """
    def __init__(self, *,uDefinitionName:str, uDefinitionPathName:str='') -> None:
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

        if uDefinitionPathName=='':
            self.oPathDefinition = Globals.oPathDefinitionRoot + uDefinitionName
        else:
            self.oPathDefinition = Globals.oPathDefinitionRoot + uDefinitionPathName

        self.oPathDefinitionAtlas:cPath                 = self.oPathDefinition + 'atlas'
        self.oFnDefinitionAtlas:cFileName               = cFileName(self.oPathDefinitionAtlas) + 'definition.atlas'
        self.oFnDefinitionLocalFont:cFileName           = cFileName(self.oPathDefinition + 'fonts') + 'fonts.xml'
        self.oFnDefinition:cFileName                    = cFileName(self.oPathDefinition) + 'definition.xml'
        self.oFnDefinitionCache:cFileName               = cFileName(self.oPathDefinition) + f'cache_{uAdd}.xml'
        self.oFnDefinitionIni:cFileName                 = cFileName(self.oPathDefinition) + 'definition.ini'
        self.oPathDefinitionInterfaceSettings:cPath     = self.oPathDefinition + 'interfacesettings'
        self.oPathDefinitionScriptSettings:cPath        = self.oPathDefinition + 'scriptsettings'
        self.oFnDefinitionLanguage:cFileName            = cFileName()
        self.oFnDefinitionLanguageFallBack:cFileName    = cFileName(self.oPathDefinition + 'languages/English')+ 'strings.xml'
        self.oPathDefinitionSkinElements:cPath          = self.oPathDefinition + 'elements'
        self.oPathTemplateSkinElements:cFileName        = cFileName()

        uCheck = 'skin_' + Globals.uSkinName
        oPathCheck = self.oPathDefinitionSkinElements + uCheck
        if oPathCheck.Exists():
            self.oPathDefinitionSkinElements = oPathCheck
            SetVar('SKINCONTEXT',uCheck)
        else:
            self.oPathDefinitionSkinElements = self.oPathDefinitionSkinElements + 'skin_default'
            SetVar('SKINCONTEXT', 'skin_default')

        self.LanguageChange()

        if uDefinitionName in Globals.oDefinitions:
            if 'definition_templatename_mediaplayer_wizard' in Globals.oDefinitions[uDefinitionName].oDefinitionVars:
                oPathCheck = Globals.oPathWizardTemplates +(Globals.oDefinitions[uDefinitionName].oDefinitionVars['definition_templatename_mediaplayer_wizard']+'/elements/' +uCheck)
                if oPathCheck.Exists():
                    self.oPathTemplateSkinElements = oPathCheck
                    SetVar('MEDIATEMPLATESKINCONTEXT',uCheck)
                else:
                    self.oPathDefinitionSkinElements = Globals.oPathWizardTemplates +(Globals.oDefinitions[uDefinitionName].oDefinitionVars['definition_templatename_mediaplayer_wizard']+'/elements/' + 'skin_default')
                    SetVar('MEDIATEMPLATESKINCONTEXT', 'skin_default')

    def LanguageChange(self) -> None:
        """
        changes the filename of the definition language file
        :return:
        """
        self.oFnDefinitionLanguage            = cFileName(self.oPathDefinition + ('languages/' + Globals.uLanguage)) + 'strings.xml'
        return None