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

from kivy.uix.screenmanager import FadeTransition
from kivy.logger            import Logger

from ORCA.widgets.core.FileBrowser      import FileBrowser
from ORCA.widgets.Base                  import cWidgetBase
from ORCA.vars.Replace                  import ReplaceVars
from ORCA.vars.Access                   import SetVar
from ORCA.vars.Access                   import GetVar
from ORCA.utils.XML                     import GetXMLBoolAttribute
from ORCA.utils.XML                     import GetXMLTextAttribute
from ORCA.utils.LogError                import LogError
from ORCA.ui.ShowErrorPopUp             import ShowErrorPopUp
from ORCA.utils.Path                    import cPath

import ORCA.Globals as Globals

__all__ = ['cWidgetFileBrowser']

class cWidgetFileBrowser(cWidgetBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-FILEBROWSER
    WikiDoc:TOCTitle:FileBrowser
    = FILEBROWSER =

    The button widget lets the user select a file or folder

    The following attributes are additional attributes to common widget attributes
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "FILEBROWSER". Capital letters!
    |-
    |filebrowserfile
    |The startpath / folder which is select first
    |-
    |actioncancel
    |The action, which is called, when the user presses the cancel button
    |-
    |dirselect
    |Boolean flag, (0/1), if the user can select a folder instead of a file
    |}</div>


    Below you see an example for a filebrowser widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="FileBrowser" type="FILEBROWSER"  dirselect="1" action="Fkt Import_Export" actioncancel="gotosettingspage"/>
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self, **kwargs):
        super(cWidgetFileBrowser, self).__init__(**kwargs)
        self.oPathStart = cPath()
        self.uActionNameCancel = ""
        self.bDirSelect = False

    def InitWidgetFromXml(self,oXMLNode,oParentScreenPage, uAnchor):
        """ Reads further Widget attributes from a xml node """
        self.oPathStart             = cPath(GetVar(uVarName = "filebrowserfile"))
        self.uActionNameCancel      = GetXMLTextAttribute(oXMLNode,u'actioncancel',False,u'')
        self.bDirSelect             = GetXMLBoolAttribute(oXMLNode,u'dirselect',False,False)
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Create(self,oParent):
        """ creates the Widget """
        self.AddArg('select_string',    ReplaceVars('$lvar(563)'))
        self.AddArg('cancel_string',    ReplaceVars('$lvar(5009)'))
        self.AddArg('libraries_string', ReplaceVars('$lvar(5018)'))
        self.AddArg('favorites_string', ReplaceVars('$lvar(5019)'))
        self.AddArg('computer_string',  ReplaceVars('$lvar(5020)'))
        self.AddArg('location_string',  ReplaceVars('$lvar(5021)'))
        self.AddArg('listview_string',  ReplaceVars('$lvar(5022)'))
        self.AddArg('iconview_string',  ReplaceVars('$lvar(5023)'))
        self.AddArg('transition ',      FadeTransition())
        self.AddArg('size_hint',        (1, 1))
        self.AddArg('favorites',        [(Globals.oPathRoot.string, 'ORCA')])
        self.AddArg('show_fileinput',   False)
        self.AddArg('show_filterinput', False)
        self.AddArg('dirselect',        self.bDirSelect)

        if not self.oPathStart.IsEmpty():
            self.AddArg('path',         self.oPathStart.string)

        if self.CreateBase(Parent=oParent, Class=FileBrowser):
            self.oParent.add_widget(self.oObject)
            self.oObject.bind(on_success=self.On_Success,on_canceled=self.On_Canceled)
            return True
        return False


    def On_Success(self, instance):
        """ called , when a user makes a selection """
        if len(instance.selection)!=0:
            oItem = cPath(instance.selection[0])
            if self.bDirSelect and not oItem.IsDir():
                return

            SetVar(uVarName = "filebrowserfile", oVarValue = oItem.string)
            self.On_Button_Up(instance)
            return

    def On_Canceled(self, instance):
        """ called, when the user cancelles """
        if self.uActionNameCancel!=u'':
            aActions=Globals.oActions.GetActionList(uActionName = self.uActionNameCancel, bNoCopy = False)
            if aActions:
                Globals.oEvents.ExecuteActions( aActions=aActions,oParentWidget=self)
                Logger.debug (u'TheScreen: Single Tap Action queued for Object %s [%s]' %(self.uName,self.uActionNameCancel))
            else:
                uMsg=LogError(u'TheScreen: Action Not Found:' + self.uActionNameCancel)
                ShowErrorPopUp(uTitle='Fatal Error', uMessage=uMsg, bAbort=True)

