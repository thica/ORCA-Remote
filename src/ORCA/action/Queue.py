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
from __future__                 import annotations

import time
from typing                     import List
from typing                     import Union
from copy                       import copy
from functools                  import partial
from threading                  import Lock
from kivy.logger                import Logger
from kivy.clock                 import Clock

from ORCA.ui.ShowErrorPopUp     import ShowErrorPopUp
from ORCA.utils.LogError        import LogError

from ORCA.utils.Sleep           import fSleep
from ORCA.utils.TypeConvert     import ToFloat
from ORCA.utils.wait.IsWaiting  import IsWaiting
from ORCA.vars.Replace          import ReplaceVars
from ORCA.action.Action import GetActionID
from ORCA.action.Action import cAction
from ORCA.action.ActionType import eReplaceOption
from ORCA.vars.Access           import GetVar
from ORCA.utils.CheckCondition  import CheckCondition
from ORCA.utils.TypeConvert     import ToUnicode
from ORCA.vars.Access           import SetVar
from ORCA.actions.ReturnCode    import eReturnCode

from ORCA.Globals               import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.widgets.base.Base import cWidgetBase
else:
    from typing import TypeVar
    cWidgetBase     = TypeVar('cWidgetBase')

aActiveQueueStack:List[cQueue]   = []
aInActiveQueueStack:List[cQueue] = []
bStop:bool                       = False
oQueueLock                       = Lock()

__all__ = ['cQueue',
           'GetActiveQueue',
           'ClearQueue',
           'DumpQueue',
           'GetQueueLen',
           'GetNewQueue',
           'StopQueue',
           'ResumeQueue'
           ]

def GetNewQueue() -> cQueue:
    """
    Returns a queue object, either a new one or a re-initialized used one
    :return: cQueue
    """

    oQueue:cQueue
    oQueueLock.acquire()
    if len(aInActiveQueueStack) > 0:
        oQueue = aInActiveQueueStack.pop()
    else:
        oQueue = cQueue()
    oQueue.Reset()
    oQueueLock.release()
    return oQueue

def GetQueueLen() -> int:
    """
    Returns the len of the current queue
    :return: int
    """
    return len(aActiveQueueStack)

def GetActiveQueue() -> cQueue:
    """
    Returns the last (current) queue object
    :return: cQueue
    """
    if GetQueueLen()>0:
        return aActiveQueueStack[-1]
    else:
        return GetNewQueue()

def ClearQueue() -> None:
    """ terminates all queues """
    oQueueLock.acquire()
    for oQueue in reversed(aActiveQueueStack):
        oQueue.iActionQueuePos = len(oQueue.aActionQueue)
    oQueueLock.release()


def DumpQueue() -> None:
    """ dumps all queues """
    oQueueLock.acquire()
    iStackNum:int=0
    for oStack in aActiveQueueStack:
        iStackNum+=1
        Logger.debug (f'Action: ========= Start Queue ({iStackNum:d})  ==========')
        oStack.Dump()
        Logger.debug (f'Action: ========= End Queue ({iStackNum:d})  ==========')
    oQueueLock.release()


def StopQueue() -> None:
    """
    Stops the queue (set it on pause)
    :return: None
    """
    global bStop
    bStop = True

def ResumeQueue() -> None:
    """
    Restarts the queue
    :return: None
    """
    global bStop
    bStop = False

class cQueue:
    """ represents a single queue object """
    def __init__(self)->None:
        self.aActionQueue:List[cAction] = []
        self.bForceState:bool           = False
        self.iActionQueuePos:int        = 0
        self.bDoNow:bool                = False
        self.uName:str                  = ''

    def Reset(self) -> None:
        """ Resets the Queue """
        self.iActionQueuePos   = 0
        del self.aActionQueue[:]
        self.bForceState       = False
        aActiveQueueStack.append(self)
        self.bDoNow            = False

    # noinspection PyUnusedLocal
    def WorkOnQueue(self,bForce:bool,*largs) -> Union[eReturnCode,None]:
        """ runs the queue, until finished """

        oAction:cAction
        self.bForceState            = bForce
        eRet:eReturnCode            = eReturnCode.Nothing
        eRetReal:eReturnCode

        # We need to ensure, that only actions in the last queue will be executed
        # All other Queues are still scheduled, so just skip them
        if not self == aActiveQueueStack[-1]:
            return None
        if IsWaiting() and not self.bForceState:
            Clock.schedule_once(partial(self.WorkOnQueue,bForce))
            return None

        if Globals.oTheScreen.bIntransition and not self.bForceState:
            Clock.schedule_once(partial(self.WorkOnQueue,bForce))
            return None

        fNextFrame:float = 0.0
        #fNextFrame=0.0001
        fStart = time.time()

        while True:
            if self.iActionQueuePos < len(self.aActionQueue):
                oAction=self.aActionQueue[self.iActionQueuePos]
                Globals.oEvents.bDoNext = True
                eRetReal= self.WorkOnQueueDoAction(oAction=oAction)
                if eRetReal!=eReturnCode.Nothing:
                    eRet=eRetReal
                self.iActionQueuePos += 1
                if not self == aActiveQueueStack[-1]:
                    #Logger.debug ('Not own queue')
                    return eRet
                if oAction.iActionId==Globals.oActions.oActionType.Wait:
                    fWait=ToFloat(ReplaceVars(oAction.dActionPars.get('time','1')))
                    Globals.oEvents.LogAction(uTxt='Wait',oAction=oAction)
                    Globals.oEvents.bDoNext = False
                    fSleep (fSeconds=fWait/1000) # Todo: Check division
                    Globals.oEvents.LogAction(uTxt='Wait2',oAction=oAction)

                #We will execute some basic Actions like Var manipulation immediately, to make it faster
                #If we wait, then prevent fast execution
                if IsWaiting():
                    Globals.oEvents.bDoNext=False

                # to ensure, that we get screen updates and detect touches, even on long queues
                if time.time() - fStart > 0.2:
                    Globals.oEvents.bDoNext = False
                    fStart = time.time()

                #If we do not force working the queue and nothing to accelerate, the next execution is not next frame (to ensure screen updates)
                if not self.bForceState and not Globals.oEvents.bDoNext:
                    if not bStop:
                        if Globals.bOnSleep:
                            fNextFrame=0.5 # if we are on sleep , we switch to timed minimum queue activity
                        Clock.schedule_once(partial(self.WorkOnQueue,False),fNextFrame)
                    return eRet
            else:
                del self.aActionQueue[:]
                self.iActionQueuePos=0
                if not len(aActiveQueueStack)==1:
                    aInActiveQueueStack.append(aActiveQueueStack.pop())
                    if not self.bForceState:
                        if not bStop:
                            Clock.schedule_once(partial(GetActiveQueue().WorkOnQueue,bForce),fNextFrame)
                return eRet

    def AddActions(self,*,aActions:List[cAction], oParentWidget:cWidgetBase) -> None:
        """ This functions just adds the action commands to the queue """

        oTmpAction:cAction
        oAction:cAction
        iActionId:int

        for oTmpAction in aActions:
            oAction = copy(oTmpAction)
            oAction.oParentWidget = oParentWidget

            iActionId=oAction.iActionId

            ''' this enables to any function to call without call statement from an macro, as long as the action exists'''
            if iActionId==Globals.oActions.oActionType.NoAction:
                if oAction.uActionString.lower()!='noaction':
                    oAction.iActionId=-1
                    aTmpActions = Globals.oActions.GetActionList(uActionName = oAction.uActionString, bNoCopy = True)
                    if aTmpActions is not None:
                        iActionId=aTmpActions[0].iActionId

            if iActionId == Globals.oActions.oActionType.SendCommand:
                self.__InsertToQueue(oAction=cAction(actionname='enabletransmitterpicture'))
            if iActionId == Globals.oActions.oActionType.ShowPage:
                self.__InsertToQueue(oAction=cAction(actionname='PAGESTOPACTIONS', actionstring='call'))

            self.__InsertToQueue(oAction=oAction)

            if iActionId == Globals.oActions.oActionType.ShowPage:
                oTmpAction = copy(oTmpAction)
                uPagenameToCall = oAction.dActionPars.get('pagename','')
                if uPagenameToCall == '':
                    if oAction.oParentWidget is not None:
                        if hasattr(oAction.oParentWidget,'dActionPars'):
                            uPagenameToCall = oAction.oParentWidget.dActionPars.get('pagename','')
                oTmpAction.dActionPars['string'] = 'call'
                oTmpAction.dActionPars['actionname'] = 'PAGESTARTACTIONS'
                oTmpAction.dActionPars['pagename'] = uPagenameToCall
                oTmpAction.dActionPars['currentpagename'] = GetVar(uVarName = 'CURRENTPAGE')
                oTmpAction.iActionId = GetActionID(oTmpAction.dActionPars['string'])
                self.__InsertToQueue(oAction=oTmpAction)
            if iActionId == Globals.oActions.oActionType.SendCommand:
                self.__InsertToQueue(oAction=cAction(actionname='disabletransmitterpicture'))

    def __InsertToQueue(self,*,oAction:cAction) -> None:
        """ insert an action to the latest queue """
        if not oAction.bForce:
            self.aActionQueue.append(oAction)
        else:
            self.WorkOnQueueDoAction(oAction=oAction)
        return

    def WorkOnQueueDoAction(self,*,oAction:cAction) -> Union[eReturnCode,int]:
        """ Executes a single action in a queue (including condition verifying)"""

        eRet:eReturnCode = eReturnCode.Success
        bCheckSuccess:bool = CheckCondition(oPar=oAction)

        if oAction.iActionId==Globals.oActions.oActionType.If:
            # we do the If statement only in case of the condition fails
            if bCheckSuccess:
                Globals.oEvents.LogAction(uTxt='if',oAction=oAction, uAddText='executing actions')
            # we need to run the if command in any way to skip the actions
            bCheckSuccess=not bCheckSuccess

        if bCheckSuccess:
            #We set / replace Action Command Pars by Definition/Button pars
            eRet=self.ExecuteAction(oAction=oAction)
            if eRet!=eReturnCode.Nothing:
                SetVar(uVarName = 'LASTERRORCODE', oVarValue = ToUnicode(eRet))
                if eRet!=eReturnCode.Success:
                    Logger.debug('Action returned LASTERRORCODE '+ ToUnicode(eRet))
        return eRet

    # noinspection PyMethodMayBeStatic
    def ExecuteAction(self,*,oAction:cAction) -> Union[int,eReturnCode]:
        """ Executes a single action in a queue (excluding condition verifying)"""

        eRet: Union[int, eReturnCode]

        try:
            oAction.uActionString=ReplaceVars(oAction.uActionString)
            oFunction=Globals.oEvents.dActionFunctions.get(oAction.iActionId)
            if oFunction:
                eRet = oFunction(oAction)
                return eRet
            else:
                ''' this enables to use standardactions / actions without call, but assigning parameters like interface and configname '''

                aActions:List[cAction]=Globals.oActions.GetActionList(uActionName = oAction.uActionString, bNoCopy = True)
                if aActions:
                    if len(aActions)>1:
                        Logger.error(f'you can\'t use multiline actions as short cut, use call instead (Action:{oAction.uActionString})')

                    oFunction=Globals.oEvents.dActionFunctions.get(aActions[0].iActionId)
                    if oFunction:
                        oAction.uActionString=ReplaceVars(aActions[0].uActionString)
                        Globals.oEvents.CopyActionPars(dTarget=oAction.dActionPars,dSource=aActions[0].dActionPars,enReplaceOption=eReplaceOption.eDoNotReplaceTarget)
                        if not oAction.uRetVar:
                            oAction.uRetVar=aActions[0].uRetVar
                        eRet = oFunction(oAction)
                        return eRet
                Logger.error('ExecuteAction: Action not Found:'+oAction.uActionName+':'+oAction.uActionString)
                # Globals.oActions.Dump('')
                return eReturnCode.Error
        except Exception as e:
            uMsg=LogError(uMsg='Error executing Action:'+Globals.oEvents.CreateDebugLine(oAction=oAction, uTxt=''),oException=e)
            ShowErrorPopUp(uMessage=uMsg)
            return eReturnCode.Error

    def Dump(self) -> None:
        """ dumps the queue """

        i:int
        oAction:cAction

        Logger.debug ('Action: ********* Start Dump  *********')
        Logger.debug (f'Action: QuePos: {self.iActionQueuePos:d}')
        for i,oAction in enumerate(self.aActionQueue):
            Logger.debug (Globals.oEvents.CreateDebugLine(oAction=oAction, uTxt=str(i)))
        Logger.debug ('Action: ********* End Dump  *********')
