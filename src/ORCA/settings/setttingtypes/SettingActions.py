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

from typing import List
from typing import Union

from xml.etree.ElementTree import Element

from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
import ORCA.Globals as Globals
from ORCA.settings.setttingtypes.SettingScrollOptionsWithOptions import SettingScrollOptionsWithOptions
from ORCA.settings.setttingtypes.SettingScrollOptions   import ScrollOptionsPopUp
from ORCA.utils.XML                                     import LoadXMLFile
from ORCA.utils.XML                                     import Orca_include
from ORCA.utils.XML                                     import orca_et_loader
from ORCA.utils.XML                                     import GetXMLTextAttribute
from ORCA.utils.LogError                                import LogError
from ORCA.utils.FileName                                import cFileName
from ORCA.vars.Replace                                  import ReplaceVars



__all__ = ['SettingActions']

class SettingActions(SettingScrollOptionsWithOptions):
    """ A setting class to select actions from the action list or from a codeset """
    def __init__(self, **kwargs):
        self.aCodesetCmds:List[str]                             = []
        self.oActionPopup:Union[Popup,None]                     = None
        self.oCodeSetActionsScrollOptionsPopup:Union[Popup,None]=None
        kwargs["options"] = [ReplaceVars("$lvar(742)"),ReplaceVars("$lvar(743)"),ReplaceVars("$lvar(744)")]
        kwargs["suboptions"] = [["$ACTIONLISTSEND"], ["$ACTIONLIST"], ["$FILELIST[%s]" % Globals.oPathCodesets.string]]
        super().__init__(**kwargs)

    def _set_suboption(self, instance:Widget) -> None:
        """ called, when the second option is selected """
        if instance.text.startswith('CODESET_'):
            self.subpopup.dismiss()
            self.popup.dismiss()
            self._ReadCodeset(instance.text)
            self._ShowCodesetCodesPopup(instance.text)
        else:
            self.value = instance.text
            self.subpopup.dismiss()
            self.popup.dismiss()

    def _set_suboptioncodesetaction(self, instance:Widget) -> None:
        """ called, when a codesetcode is selected """
        self.value = "SendCommand "+instance.text
        self.oActionPopup.dismiss()

    def _ReadCodeset(self,uFN:str) -> None:

        oXMLCode:Element
        uCmd:str
        del self.aCodesetCmds[:]
        try:
            oXMLCodeset:Element = LoadXMLFile(oFile=cFileName(Globals.oPathCodesets) + uFN)
            Orca_include(oXMLCodeset,orca_et_loader)
            if oXMLCodeset is not None:
                # First read imported codesets
                oXMLImports:Element = oXMLCodeset.find('imports')
                if oXMLImports is not None:
                    oXMLImportCodesets:Element=oXMLImports.find('codeset')
                    if oXMLImportCodesets is not None:
                        for oXMLCode in oXMLImportCodesets.findall('code'):
                            uCmd=GetXMLTextAttribute(oXMLNode=oXMLCode,uTag='action',bMandatory=False,vDefault='')
                            if uCmd:
                                self.aCodesetCmds.append(uCmd)

                for oXMLCode in oXMLCodeset.findall('code'):
                    uCmd=GetXMLTextAttribute(oXMLNode=oXMLCode,uTag='action',bMandatory=False,vDefault='')
                    if uCmd:
                        self.aCodesetCmds.append(uCmd)

        except Exception as e:
            LogError(uMsg='Error Reading Codeset',oException=e)

    def _ShowCodesetCodesPopup(self,uFN:str) -> None:
        kwargs={'title':uFN,'options':sorted(self.aCodesetCmds)}
        self.oCodeSetActionsScrollOptionsPopup=ScrollOptionsPopUp(**kwargs)
        self.oCodeSetActionsScrollOptionsPopup.CreatePopup(self.value,self._set_suboptioncodesetaction,None)
        self.oActionPopup=self.oCodeSetActionsScrollOptionsPopup.popup

