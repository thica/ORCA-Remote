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

from __future__                        import annotations #todo: remove in Python 4.0

from typing                            import Dict
from typing                            import List

from xml.etree.ElementTree             import Element

from kivy.logger                       import Logger
from kivy.uix.widget                   import Widget

from ORCA.utils.LogError               import LogError
from ORCA.utils.Platform               import OS_Vibrate
from ORCA.utils.TypeConvert            import ToDic
from ORCA.utils.XML                    import GetXMLTextAttribute
from ORCA.vars.Replace                 import ReplaceVars
from ORCA.widgets.helper.WidgetType    import eWidgetType
from ORCA.widgets.base.BaseBase        import cWidgetBaseBase

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
    from ORCA.Action                import cAction
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")
    cAction       = TypeVar("cAction")

__all__ = ['cWidgetBaseAction']


class cWidgetBaseAction(cWidgetBaseBase):
    # Base Class for all ORCA widgets with Action / Touch capabilities

    # noinspection PyUnresolvedReferences
    def __init__(self,**kwargs):

        super().__init__(**kwargs)

        self.aWidgetActions:List[Dict]                  = []
        self.dActionPars:Dict[str,str]                  = {} # Actionpars will be passed to Actions within command set, existing pars will be replaced!
        self.uActionName:str                            = u''
        self.uActionNameDoubleTap:str                   = u''
        self.uActionNameDownOnly:str                    = u''
        self.uActionNameLongTap:str                     = u''
        self.uActionNameUpOnly:str                      = u''
        self.uTapType:str                               = u''
        self.uConfigName:str                            = u''
        self.uInterFace:str                             = u''

    # noinspection PyUnresolvedReferences
    def ParseXMLBaseNode (self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:

        try:
            self.uActionName          = GetXMLTextAttribute(oXMLNode,u'action',False,u'')
            self.uActionNameDoubleTap = GetXMLTextAttribute(oXMLNode,u'actiondoubletap',False,u'')
            self.uActionNameLongTap   = GetXMLTextAttribute(oXMLNode,u'actionlongtap',False,u'')
            self.uActionNameDownOnly  = GetXMLTextAttribute(oXMLNode,u'actiondownonly',False,u'')
            self.uActionNameUpOnly    = GetXMLTextAttribute(oXMLNode,u'actionuponly',False,u'')
            self.uInterFace           = GetXMLTextAttribute(oXMLNode,u'interface',False,u'')
            self.uConfigName          = GetXMLTextAttribute(oXMLNode,u'configname',False,u'')
            uActionPars:str           = GetXMLTextAttribute(oXMLNode,u'actionpars',False,u'{}')
            if uActionPars.startswith("$var("):
                uActionPars=ReplaceVars(uActionPars)

            self.dActionPars=ToDic(uActionPars)

            if self.uActionName.startswith("SendCommand "):
                if len(self.dActionPars)==0:
                    self.dActionPars={"commandname":self.uActionName[12:]}
                    self.uActionName="Send"

            if not self.uInterFace==u'':
                Globals.oInterFaces.dUsedInterfaces[self.uInterFace]=True

            return super().ParseXMLBaseNode (oXMLNode,oParentScreenPage, uAnchor)

        except Exception as e:
            LogError(uMsg=u'Error parsing widget from element (Action):['+self.uName+"",oException=e)
            return False

    def On_Button_Up(self,instance:Widget) -> None:

        if self.bIsEnabled:
            if hasattr(instance,'uTapType'):
                self.uTapType = instance.uTapType
            else:
                self.uTapType = u"up"

            Logger.debug (u'WidgetBaseAction:On_Button_Up: Tap detected: %s:%s' %( self.uName, self.uTapType))

            self.OnButtonClicked()
            return

    def On_Button_Down(self,instance:Widget) -> None:

        if self.bIsEnabled:
            Globals.oSound.PlaySound(u'click')
            OS_Vibrate()

            if hasattr(instance,'uTapType'):
                self.uTapType = instance.uTapType
            else:
                self.uTapType = u"down"
            Logger.debug (u'WidgetBaseAction:On_Button_Down: Tap detected: %s:%s' %( self.uName, self.uTapType))

            self.OnButtonClicked()
            return

    def OnButtonClicked(self) -> None:

        if Globals.oTheScreen.GuiIsBlocked():
            return

        uActionName:str          = ReplaceVars(self.uActionName)
        uActionNameDoubleTap:str = ReplaceVars(self.uActionNameDoubleTap)
        uActionNameUp:str        = ReplaceVars(self.uActionNameUpOnly)
        uActionNameDown:str      = ReplaceVars(self.uActionNameDownOnly)
        uActionNameLongTap:str   = ReplaceVars(self.uActionNameLongTap)
        aUseActionName:List[str] = []

        if uActionNameDoubleTap != u'' and self.uTapType == u'double_up':
            aUseActionName.append(uActionNameDoubleTap)
        elif uActionNameLongTap != u'' and self.uTapType == u'long_up':
            aUseActionName.append(uActionNameLongTap)
        elif uActionNameDown    != u'' and self.uTapType == u"down":
            aUseActionName.append(uActionNameDown)
        elif uActionNameUp      != u'' and self.uTapType == u"up":
            aUseActionName.append(uActionNameUp)
        elif uActionName!=u'' and  self.uTapType== u'repeat_down' and uActionNameLongTap == u'':
            aUseActionName.append(uActionName)
        elif uActionName!=u'' and self.uTapType== u"up":
            aUseActionName.append(uActionName)

        # this a response optimisation, If we do have just one standard action
        # the we convert it to a down only action

        if self.eWidgetType == eWidgetType.Button or self.eWidgetType == eWidgetType.Picture:
            if self.uTapType == u"down":
                if self.uActionName != u"":
                    if self.uActionNameDoubleTap == u"":
                        if self.uActionNameLongTap == u"":
                            if self.uActionNameDownOnly == u"":
                                if self.uActionNameUpOnly == u"":
                                    aUseActionName.append(uActionName)

            if self.uTapType == u"up":
                if self.uActionName != u"":
                    if self.uActionNameDoubleTap == u"":
                        if self.uActionNameLongTap == u"":
                            if self.uActionNameDownOnly == u"":
                                if self.uActionNameUpOnly == u"":
                                    return

        # if we have a doubletap but no doubletap action, then execute two single taps
        if len(aUseActionName) == 0 and self.uTapType == u'double_up':
            aUseActionName.append(uActionName)
            aUseActionName.append(uActionName)

        aActions:List[cAction]=[]
        for uUseActionName in aUseActionName:
            aActionsTest:List[cAction] = Globals.oActions.GetActionList(uActionName = uUseActionName, bNoCopy = True)
            if aActionsTest:
                Globals.oEvents.AddToSimpleActionList(aActions,[{'string':'call'}])
                aActions[-1].dActionPars=self.dActionPars
                aActions[-1].dActionPars['actionname']=uUseActionName
                Logger.debug (u'WidgetBaseAction: [%s] Action queued for Object [%s] [%s]' % (self.uTapType,self.uName,uUseActionName))
            else:
                Globals.oEvents.AddToSimpleActionList(aActions,[{'string':uUseActionName}])
                aActions[-1].dActionPars=self.dActionPars
        if len(aActions)>0:
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=self)
        return

    def On_Gesture(self,instance:Widget) -> None:

        if Globals.oTheScreen.GuiIsBlocked():
            return

        if self.bIsEnabled:
            if hasattr(instance,'aActions'):
                self.aWidgetActions=instance.aActions
                if self.aWidgetActions is not None:
                    Globals.oEvents.ExecuteActions( aActions=self.aWidgetActions,oParentWidget=self)

