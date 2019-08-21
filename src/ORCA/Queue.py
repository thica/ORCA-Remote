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

import time
from copy                       import copy

from functools                  import partial
from threading                  import Lock

from kivy.logger                import Logger
from kivy.clock                 import Clock


from ORCA.ui.ShowErrorPopUp             import ShowErrorPopUp
from ORCA.utils.LogError                import LogError

from ORCA.utils.Sleep           import fSleep
from ORCA.utils.TypeConvert     import ToFloat
from ORCA.utils.wait.IsWaiting  import IsWaiting
from ORCA.vars.Replace          import ReplaceVars
from ORCA.Action                import GetActionID
from ORCA.Action                import cAction
from ORCA.vars.Access           import GetVar
from ORCA.utils.CheckCondition  import CheckCondition
from ORCA.utils.TypeConvert             import ToUnicode
from ORCA.vars.Access                   import SetVar


from ORCA import Globals as Globals

aActiveQueueStack   = []
aInActiveQueueStack = []
bStop               = False
oQueueLock          = Lock()



__all__ = ['cQueue',
           'GetActiveQueue',
           'ClearQueue',
           'DumpQueue',
           'GetQueueLen',
           'GetNewQueue',
           'StopQueue',
           'ResumeQueue'
           ]

def GetNewQueue():
    """
    Returns a queue object, either a new one or a re-initialized used one
    :return: cQueue
    """

    oQueueLock.acquire()
    if len(aInActiveQueueStack) > 0:
        oQueue = aInActiveQueueStack.pop()
    else:
        oQueue = cQueue()
    oQueue.Reset()
    oQueueLock.release()
    return oQueue

def GetQueueLen():
    """
    Returns the len of the current queue
    :return: int
    """
    return len(aActiveQueueStack)

def GetActiveQueue():
    """
    Returns the last (current) queue object
    :return: cQueue
    """
    if GetQueueLen()>0:
        return aActiveQueueStack[-1]
    else:
        return GetNewQueue(uQueueName="unknown")

def ClearQueue():
    """ terminates all queues """
    oQueueLock.acquire()
    for oQueue in reversed(aActiveQueueStack):
        oQueue.iActionQueuePos = len(oQueue.aActionQueue)
    oQueueLock.release()


def DumpQueue():
    """ dumps all queues """
    oQueueLock.acquire()
    iStackNum=0
    for oStack in aActiveQueueStack:
        iStackNum+=1
        Logger.debug (u'Action: ========= Start Queue (' +str(iStackNum)+')  ==========')
        oStack.Dump()
        Logger.debug (u'Action: ========= End Queue (' +str(iStackNum)+')  ==========')
    oQueueLock.release()


def StopQueue():
    global bStop
    bStop = True

def ResumeQueue():
    global bStop
    bStop = False

class cQueue(object):
    """ represents a single queue object """
    def __init__(self):
        self.aActionQueue      = []
        self.bForceState       = False
        self.iActionQueuePos   = 0
        self.bDoNow            = False

    def Reset(self):
        """ Resets the Queue """
        self.iActionQueuePos   = 0
        del self.aActionQueue[:]
        self.bForceState       = False
        aActiveQueueStack.append(self)
        self.bDoNow            = False

    def WorkOnQueue(self,bForce,*largs):
        """ runs the queue, until finished """

        self.bForceState = bForce
        iRet             = -2

        # We need to ensure, that only actions in the last queue will be executed
        # All other Queues are still scheduled, so just skip them
        if not self == aActiveQueueStack[-1]:
            return
        if IsWaiting() and not self.bForceState:
            Clock.schedule_once(partial(self.WorkOnQueue,bForce))
            return

        if Globals.oTheScreen.bIntransition and not self.bForceState:
            Clock.schedule_once(partial(self.WorkOnQueue,bForce))
            return

        fNextFrame=0.0
        #fNextFrame=0.0001
        fStart = time.time()

        while True:
            if self.iActionQueuePos < len(self.aActionQueue):

                oAction=self.aActionQueue[self.iActionQueuePos]
                Globals.oEvents.bDoNext = True
                iRetReal= self.WorkOnQueueDoAction(oAction)
                if iRetReal!=-2:
                    iRet=iRetReal
                self.iActionQueuePos=self.iActionQueuePos+1
                if not self == aActiveQueueStack[-1]:
                    #Logger.debug ("Not own queue")
                    return iRet
                if oAction.iActionId==Globals.oActions.oActionType.Wait:
                    '''
                    fWait=ToFloat(ReplaceVars(oAction.dActionPars.get('time','1')))
                    Globals.oEvents.LogAction(u'Wait',oAction)
                    if not self.bForceState:
                        fNextFrame = fWait/1000.0
                        Globals.oEvents.bDoNext = False
                    else:
                        fSleep (fWait/1000.0)
                    '''
                    fWait=ToFloat(ReplaceVars(oAction.dActionPars.get('time','1')))
                    Globals.oEvents.LogAction(u'Wait',oAction)
                    Globals.oEvents.bDoNext = False
                    fSleep (fWait/1000)
                    Globals.oEvents.LogAction(u'Wait2',oAction)

                #We will execute some basic Actions like Var manipulation immediatly, to make it faster
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
                        fStart = time.time()
                        Clock.schedule_once(partial(self.WorkOnQueue,False),fNextFrame)
                    return iRet
            else:
                del self.aActionQueue[:]
                self.iActionQueuePos=0
                if not len(aActiveQueueStack)==1:
                    aInActiveQueueStack.append(aActiveQueueStack.pop())
                    if not self.bForceState:
                        if not bStop:
                            Clock.schedule_once(partial(GetActiveQueue().WorkOnQueue,bForce),fNextFrame)
                return iRet
        return iRet

    def AddActions(self,aActions, oParentWidget):
        """ This functions just adds the action commands to the queue """

        for aTmpAction in aActions:
            oAction = copy(aTmpAction)
            oAction.oParentWidget = oParentWidget

            iActionId=oAction.iActionId

            ''' this enables to any function to call without call statement from an macro, as long as the action exists'''
            if iActionId==Globals.oActions.oActionType.NoAction:
                if oAction.uActionString.lower()!="noaction":
                    oAction.iActionId=-1
                    aTmpActions = Globals.oActions.GetActionList(uActionName = oAction.uActionString, bNoCopy = True)
                    if aTmpActions is not None:
                        iActionId=aTmpActions[0].iActionId

            if iActionId == Globals.oActions.oActionType.SendCommand:
                self.__InsertToQueue(cAction(actionname='enabletransmitterpicture'))
            if iActionId == Globals.oActions.oActionType.ShowPage:
                self.__InsertToQueue(cAction(actionname='PAGESTOPACTIONS', actionstring="call"))

            self.__InsertToQueue(oAction)

            if iActionId == Globals.oActions.oActionType.ShowPage:
                oTmpAction = copy(aTmpAction)
                uPagenameToCall = oAction.dActionPars.get('pagename','')
                if uPagenameToCall == "":
                    if oAction.oParentWidget is not None:
                        uPagenameToCall = oAction.oParentWidget.dActionPars.get('pagename','')
                oTmpAction.dActionPars['string'] = 'call'
                oTmpAction.dActionPars['actionname'] = 'PAGESTARTACTIONS'
                oTmpAction.dActionPars['pagename'] = uPagenameToCall
                oTmpAction.dActionPars['currentpagename'] = GetVar(uVarName = 'CURRENTPAGE')
                #oTmpAction.dActionPars['currentpagename'] = GetVar('LASTPAGE')
                oTmpAction.iActionId = GetActionID(oTmpAction.dActionPars['string'])
                self.__InsertToQueue(oTmpAction)
            if iActionId == Globals.oActions.oActionType.SendCommand:
                self.__InsertToQueue(cAction(actionname='disabletransmitterpicture'))

    def __InsertToQueue(self,oAction):
        """ insert an action to the latest queue """
        if not oAction.bForce:
            self.aActionQueue.append(oAction)
        else:
            self.WorkOnQueueDoAction(oAction)
        return

    def WorkOnQueueDoAction(self,oAction):
        """ Executes a single action in a queue (including condition verifying)"""

        iRet=0
        bCheckSuccess=CheckCondition(oAction)

        if oAction.iActionId==Globals.oActions.oActionType.If:
            # we do the If statement only in case of the condition fails
            if bCheckSuccess:
                Globals.oEvents.LogAction("if",oAction, "executing actions")
            # we need to run the if command in any way to skip the actions
            bCheckSuccess=not bCheckSuccess

        if bCheckSuccess:
            #We set / replace Action Command Pars by Definition/Button pars
            iRet=self.ExecuteAction(oAction)
            if iRet != -2:
                SetVar(uVarName = u'LASTERRORCODE', oVarValue = ToUnicode(iRet))
                if iRet != 0:
                    Logger.debug("Action returned LASTERRORCODE "+ ToUnicode(iRet))
        return iRet


    def ExecuteAction(self,oAction):
        """ Executes a single action in a queue (excluding condition verifying)"""

        try:
            oAction.uActionString=ReplaceVars(oAction.uActionString)
            oFunction=Globals.oEvents.dActionFunctions.get(oAction.iActionId)
            if oFunction:
                return oFunction(oAction)
            else:
                ''' this enables to use standardactions / actions without call, but assigning parameters like interface and configname '''

                aActions=Globals.oActions.GetActionList(uActionName = oAction.uActionString, bNoCopy = True)
                if aActions:
                    if len(aActions)>1:
                        Logger.error("you can''t use multiline actions as short cut, use call instead")

                    oFunction=Globals.oEvents.dActionFunctions.get(aActions[0].iActionId)
                    if oFunction:
                        oAction.uActionString=ReplaceVars(aActions[0].uActionString)
                        Globals.oEvents.CopyActionPars(dTarget=oAction.dActionPars,dSource=aActions[0].dActionPars,uReplaceOption="donotreplacetarget")
                        if not oAction.uRetVar:
                            oAction.uRetVar=aActions[0].uRetVar
                        return oFunction(oAction)
                Logger.error("ExecuteAction: Action not Found:"+oAction.uActionName+':'+oAction.uActionString)
                return 0
        except Exception as e:
            uMsg=LogError('Error executing Action:'+Globals.oEvents.CreateDebugLine(oAction=oAction, uTxt=''),e)
            ShowErrorPopUp(uMessage=uMsg)
            return False



    def Dump(self):
        """ dumps the queue """
        Logger.debug (u'Action: ********* Start Dump  *********')
        Logger.debug (u'Action: QuePos: %d' % self.iActionQueuePos)
        for i,oAction in enumerate(self.aActionQueue):
            Logger.debug (Globals.oEvents.CreateDebugLine(oAction=oAction, uTxt=str(i)))
        Logger.debug (u'Action: ********* End Dump  *********')
