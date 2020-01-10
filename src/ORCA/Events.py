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

from typing                             import List
from typing                             import Dict
from typing                             import Tuple
from typing                             import Union
from typing                             import Callable

import                                  logging
from functools                          import partial
from kivy.logger                        import Logger
from kivy.clock                         import Clock

from ORCA.Action                        import CreateActionForSimpleActionList
from ORCA.EventTimer                    import cAllTimer
from ORCA.ui.ProgressBar                import cProgressBar
from ORCA.Queue                         import GetActiveQueue
from ORCA.Queue                         import GetNewQueue
from ORCA.Queue                         import GetQueueLen
from ORCA.Queue                         import StopQueue
from ORCA.Queue                         import ResumeQueue
from ORCA.Queue                         import cQueue
from ORCA.actions.Base                  import cEventActionBase
from ORCA.actions.AppControl            import cEventActionsAppControl
from ORCA.actions.FlowControl           import cEventActionsFlowControl
from ORCA.actions.GuiControl            import cEventActionsGuiControl
from ORCA.actions.GuiInput              import cEventActionsGuiInput
from ORCA.actions.GuiStatusPictures     import cEventActionsGuiStatusPictures
from ORCA.actions.Internal              import cEventActionsInternal
from ORCA.actions.ScriptsAndInterfaces  import cEventActionsScriptsAndInterfaces
from ORCA.actions.Settings              import cEventActionsSettings
from ORCA.actions.VarControl            import cEventActionsVarControl
from ORCA.actions.WidgetControl         import cEventActionsWidgetControl
from ORCA.actions.Notifications         import cEventActionsNotifications

from ORCA.vars.Replace                  import ReplaceVars

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.Action            import cAction
    from ORCA.widgets.base.Base import cWidgetBase
else:
    from typing import TypeVar
    cAction = TypeVar("cAction")
    cWidgetBase = TypeVar("cWidgetBase")

__all__ = ['cEvents']

class cEvents:
    """ The core event objects which manages the queues and actions """
    def __init__(self):
        self.aEventActions:List[cEventActionBase] = [
                              cEventActionsFlowControl(self),
                              cEventActionsInternal(self),
                              cEventActionsGuiControl(self),
                              cEventActionsVarControl(self),
                              cEventActionsWidgetControl(self),
                              cEventActionsGuiInput(self),
                              cEventActionsGuiStatusPictures(self),
                              cEventActionsScriptsAndInterfaces(self),
                              cEventActionsSettings(self),
                              cEventActionsAppControl(self),
                              cEventActionsInternal(self),
                              cEventActionsNotifications(self)
                             ]

        self.dActionFunctions:Dict[str,Callable]     = {}
        self.aHiddenKeyWords:List[str]               = ['string','condition','name','taptype','interface','configname','conditionchecktype','conditionvar','conditionvalue','retvar','force','linefilename']
        self.aProgressBars:List[cProgressBar]        = []
        self.bDoNext:bool                            = False
        self.bForceState:bool                        = False
        self.oAllTimer:cAllTimer                     = cAllTimer()

        for oEventActions in self.aEventActions:
            self.RegisterEventActions(oEventActions)



    def RegisterEventActions(self,oEventActions:cEventActionBase) -> None:
        """ register all actions managed by the eventdispatcher """
        aFuncs=dir(oEventActions)
        for uFuncName in aFuncs:
            if uFuncName.startswith('ExecuteAction'):
                uName:str = uFuncName[13:]
                Globals.oActions.oActionType.RegisterAction(uName)
                self.dActionFunctions[Globals.oActions.oActionType.ActionToId[uName.lower()]] = getattr(oEventActions, uFuncName)

    def DeInit(self) -> None:
        """ stops all timer """
        self.oAllTimer.DeleteAllTimer()

    # noinspection PyMethodMayBeStatic
    def StopQueue(self) -> None:
        """ Stops the latest queue """
        StopQueue()

    def UnPauseQueue(self) -> None:
        """ restarts a queue by reactivating the timer """
        ResumeQueue()
        Clock.schedule_once(partial(GetActiveQueue().WorkOnQueue,self.bForceState),0)

    def ExecuteActionsNewQueue(self,aActions:List[cAction], oParentWidget:Union[cWidgetBase,None], bForce:bool=False) -> Union[bool,None]:
        """ Execute all actions in a new queue, new queue will atomatic appended to the queue stack"""
        oQueue:cQueue           = GetNewQueue()
        oQueue.bForceState      = bForce
        bRet:Union[bool,None]   = self._ExecuteActions(aActions=aActions,oParentWidget=oParentWidget)
        return bRet

    def ExecuteActions(self,aActions:List[cAction], oParentWidget:Union[cWidgetBase,None]) -> None:
        """ execute actions by either adding multiple actions to a new queue, or appending a single action to the existing queue """
        if len(aActions) > 1:
            self.ExecuteActionsNewQueue(aActions, oParentWidget)
        else:
            self._ExecuteActions(aActions, oParentWidget)

    # noinspection PyMethodMayBeStatic
    def _ExecuteActions(self,aActions:List[cAction], oParentWidget:cWidgetBase) -> Union[int,None]:
        """ This functions just adds the action commands to the queue and calls the scheduler at the end """

        oQueue:cQueue     = GetActiveQueue()
        bForceState:bool  = oQueue.bForceState
        oQueue.AddActions(aActions, oParentWidget)

        if not bForceState:
            Clock.schedule_once(partial(oQueue.WorkOnQueue,oQueue.bForceState), 0)
        else:
            return oQueue.WorkOnQueue(oQueue.bForceState)

    # noinspection PyMethodMayBeStatic
    def GetTargetInterfaceAndConfig(self,oAction:cAction) -> Tuple[str,str]:
        """
        Gets the interface and config for an sendcommand action
        If interfaces has not been set, we set the page defaults
        but we need to restore old values, as actions could be used from several pages  """

        uOrgInterFace:str  =   oAction.dActionPars.get(u'interface',u'')
        uOrgConfigName:str =   oAction.dActionPars.get(u'configname',u'')

        #Interface / config detection
        #Action Interfaces rules
        #then Widget Interface
        #then Anchor Interface
        #then Page Interface

        uToUseInterFace:str  = uOrgInterFace
        uToUseConfigName:str = uOrgConfigName

        if oAction.oParentWidget:
            if hasattr(oAction.oParentWidget,"uInterFace"):
                if uToUseInterFace==u'':
                    uToUseInterFace=oAction.oParentWidget.uInterFace
                if uToUseConfigName==u'':
                    uToUseConfigName=oAction.oParentWidget.uConfigName

            if uToUseInterFace==u'':
                uAnchorName:str=oAction.oParentWidget.uAnchorName
                while uAnchorName!=u'':
                    aTmpAnchor:List = oAction.oParentWidget.oParentScreenPage.dWidgets[uAnchorName]
                    if aTmpAnchor:
                        oTmpAnchor = aTmpAnchor[0]
                        if hasattr(oTmpAnchor,"uInterFace"):
                            uToUseInterFace=oTmpAnchor.uInterFace
                        uAnchorName=oTmpAnchor.uAnchorName
                    if uToUseInterFace!="":
                        break

            if uToUseInterFace==u'':
                uToUseInterFace=oAction.oParentWidget.oParentScreenPage.uDefaultInterface
            if uToUseConfigName==u'':
                uAnchorName=oAction.oParentWidget.uAnchorName
                while uAnchorName!=u'':
                    aTmpAnchors = oAction.oParentWidget.oParentScreenPage.dWidgets[uAnchorName]
                    if aTmpAnchors:
                        oTmpAnchor=aTmpAnchors[0]
                        if hasattr(oTmpAnchor, "uConfigName"):
                            uToUseConfigName=oTmpAnchor.uConfigName
                        uAnchorName=oTmpAnchor.uAnchorName
                    if uToUseConfigName!="":
                        break

            if uToUseConfigName==u'':
                uToUseConfigName=oAction.oParentWidget.oParentScreenPage.uDefaultConfigName

        uToUseConfigName = ReplaceVars(uToUseConfigName)
        uToUseInterFace  = ReplaceVars(uToUseInterFace)

        # We already should have loaded all interfaces at Definitionstart, but if this fails caused by heavy var tweaking, we ensure to load it here
        Globals.oInterFaces.LoadInterface(uToUseInterFace)

        return uToUseInterFace,uToUseConfigName


    def CopyActionPars(self, dSource:Dict, dTarget:Dict, uReplaceOption:str, bIgnoreHiddenWords=False) -> None:
        """
            Copies the action pars
            uReplaceOption
                "donotreplacetarget": Do not copy to target if target exists
                "donotcopyempty":     Do not copy empty sources to target
                "":                   copy all
        """

        if uReplaceOption=="donotreplacetarget":
            for uKey in dSource:
                if dTarget.get(uKey) is None:
                    if not uKey in self.aHiddenKeyWords or bIgnoreHiddenWords:
                        dTarget[uKey]=dSource[uKey]
        elif uReplaceOption=="donotcopyempty":
            for uKey in dSource:
                if not dSource.get(uKey,"") == "":
                    if not uKey in self.aHiddenKeyWords:
                        dTarget[uKey]=dSource[uKey]
        else:
            for uKey in dSource:
                if not uKey in self.aHiddenKeyWords:
                    dTarget[uKey]=dSource[uKey]


    def CreateDebugLine(self,oAction:cAction, uTxt:str) ->str:
        """ Creates a debugline for the logger """

        if uTxt:
            uTemp=u'Action QL%d: (%s) | %s | %s' % (GetQueueLen(),oAction.uActionName,uTxt,oAction.dActionPars.get('string',''))
        else:
            uTemp=u'Action QL%d: (%s) | %s'  % (GetQueueLen(),oAction.uActionName,oAction.dActionPars.get('string',''))

        for uKey in oAction.dActionPars:
            if not uKey in self.aHiddenKeyWords:
                uValue=oAction.dActionPars[uKey]
                if isinstance(uValue,str):
                    if '$var' in uValue or '$lvar' in uValue:
                        uValue=u'{0} [{1}]'.format(uValue , ReplaceVars(uValue))
                else:
                    uValue=u"[unknown object]"
                uTemp+=u'| %s:%s' % (uKey,uValue)
        return uTemp

    def LogAction(self,uTxt:str,oAction:cAction,uAddText:str='') -> None:
        """ Logs an action """

        if Logger.getEffectiveLevel()!=logging.DEBUG:
            return
        uTemp=self.CreateDebugLine(oAction,uTxt=uTxt)

        if uAddText:
            uTemp+=u"| "+uAddText
        try:
            from ORCA.utils.TypeConvert import ToUnicode
            Logger.debug (ToUnicode(uTemp))
        except Exception:
            try:
                Logger.debug(uTemp.encode("'UTF-8'",errors='replace'))
            except Exception as e:
                Logger.error ("Cant Create Debugline:"+str(e))

    def CreateSimpleActionList(self,aActions:List[Dict]) -> List[cAction]:
        """ Creates a simple action list from an array of action """
        aTmpActions  = []
        self.AddToSimpleActionList(aTmpActions,aActions)
        return aTmpActions

    # noinspection PyMethodMayBeStatic
    def AddToSimpleActionList(self,aActionList:List[cAction],aActions:List[Dict]) -> None:
        """ Adds a set actions to the action list """
        for dAction in aActions:
            aActionList.append(CreateActionForSimpleActionList(dAction))
