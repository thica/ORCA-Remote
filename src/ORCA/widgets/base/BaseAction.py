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

from ORCA.Globals import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.screen.ScreenPage import cScreenPage
    from ORCA.action.Action import cAction
else:
    from typing import TypeVar
    cScreenPage   = TypeVar('cScreenPage')
    cAction       = TypeVar('cAction')

__all__ = ['cWidgetBaseAction']


class cWidgetBaseAction(cWidgetBaseBase):
    # Base Class for all ORCA widgets with Action / Touch capabilities

    # noinspection PyUnresolvedReferences
    def __init__(self,**kwargs):

        super().__init__(**kwargs)

        self.aWidgetActions:List[Dict]                  = []
        self.dActionPars:Dict[str,str]                  = {} # Actionpars will be passed to Actions within command set, existing pars will be replaced!
        self.uActionName:str                            = ''
        self.uActionNameDoubleTap:str                   = ''
        self.uActionNameDownOnly:str                    = ''
        self.uActionNameLongTap:str                     = ''
        self.uActionNameUpOnly:str                      = ''
        self.uTapType:str                               = ''

    # noinspection PyUnresolvedReferences
    def ParseXMLBaseNode (self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:

        try:
            self.uActionName          = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='action',           bMandatory=False,vDefault='')
            self.uActionNameDoubleTap = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='actiondoubletap',  bMandatory=False,vDefault='')
            self.uActionNameLongTap   = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='actionlongtap',    bMandatory=False,vDefault='')
            self.uActionNameDownOnly  = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='actiondownonly',   bMandatory=False,vDefault='')
            self.uActionNameUpOnly    = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='actionuponly',     bMandatory=False,vDefault='')
            uActionPars:str           = GetXMLTextAttribute(oXMLNode=oXMLNode,uTag='actionpars',       bMandatory=False,vDefault='{}')
            if uActionPars.startswith('$var('):
                uActionPars=ReplaceVars(uActionPars)

            self.dActionPars=ToDic(uActionPars)

            if self.uActionName.startswith('SendCommand '):
                if len(self.dActionPars)==0:
                    self.dActionPars={'commandname':self.uActionName[12:]}
                    self.uActionName='Send'

            if not self.uInterFace=='':
                Globals.oInterFaces.dUsedInterfaces[self.uInterFace]=True

            return super().ParseXMLBaseNode (oXMLNode,oParentScreenPage, uAnchor)

        except Exception as e:
            LogError(uMsg='Error parsing widget from element (Action):['+self.uName+']',oException=e)
            return False

    def On_Button_Up(self,instance:Widget) -> None:

        if self.bIsEnabled:
            if hasattr(instance,'uTapType'):
                self.uTapType = instance.uTapType
            else:
                self.uTapType = 'up'

            self.OnButtonClicked()
            return

    def On_Button_Down(self,instance:Widget) -> None:

        if self.bIsEnabled:
            Globals.oSound.PlaySound(SoundName=Globals.oSound.eSounds.click)
            OS_Vibrate()

            if hasattr(instance,'uTapType'):
                self.uTapType = instance.uTapType
            else:
                self.uTapType = 'down'

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

        if uActionNameDoubleTap != '' and self.uTapType == 'double_up':
            aUseActionName.append(uActionNameDoubleTap)
        elif uActionNameLongTap != '' and self.uTapType == 'long_up':
            aUseActionName.append(uActionNameLongTap)
        elif uActionNameDown    != '' and self.uTapType == 'down':
            aUseActionName.append(uActionNameDown)
        elif uActionNameUp      != '' and self.uTapType == 'up':
            aUseActionName.append(uActionNameUp)
        elif uActionName!='' and  self.uTapType== 'repeat_down' and uActionNameLongTap == '':
            aUseActionName.append(uActionName)
        elif uActionName!='' and self.uTapType== 'up':
            aUseActionName.append(uActionName)

        # this a response optimisation, If we do have just one standard action
        # then we convert it to a down only action

        if (self.eWidgetType == eWidgetType.Button or self.eWidgetType == eWidgetType.Picture) and False:
            if self.uTapType == 'down':
                if self.uActionName != '':
                    if self.uActionNameDoubleTap == '':
                        if self.uActionNameLongTap == '':
                            if self.uActionNameDownOnly == '':
                                if self.uActionNameUpOnly == '':
                                    aUseActionName.append(uActionName)

            if self.uTapType == 'up' and False:
                if self.uActionName != '':
                    if self.uActionNameDoubleTap == '':
                        if self.uActionNameLongTap == '':
                            if self.uActionNameDownOnly == '':
                                if self.uActionNameUpOnly == '':
                                    return

        # if we have a doubletap but no doubletap action, then execute two single taps
        if len(aUseActionName) == 0 and self.uTapType == 'double_up' and False:
            aUseActionName.append(uActionName)
            aUseActionName.append(uActionName)

        aActions:List[cAction]=[]
        for uUseActionName in aUseActionName:
            aActionsTest:List[cAction] = Globals.oActions.GetActionList(uActionName = uUseActionName, bNoCopy = True)
            if aActionsTest:
                Globals.oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'call'}])
                aActions[-1].dActionPars=self.dActionPars
                aActions[-1].dActionPars['actionname']=uUseActionName
                Logger.debug (f'WidgetBaseAction: [{self.uTapType}] Action queued for Object [{self.uName}] [{uUseActionName}]')
            else:
                Globals.oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':uUseActionName}])
                aActions[-1].dActionPars=self.dActionPars
        if len(aActions)>0:
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=self,uQueueName="Button_clicked")
        return

    def On_Gesture(self,instance:Widget) -> None:

        if Globals.oTheScreen.GuiIsBlocked():
            return

        if self.bIsEnabled:
            if hasattr(instance,'aActions'):
                self.aWidgetActions=instance.aActions
                if self.aWidgetActions is not None:
                    Globals.oEvents.ExecuteActions( aActions=self.aWidgetActions,oParentWidget=self)

