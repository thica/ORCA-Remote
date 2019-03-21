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
from functools                  import partial

from kivy.logger                import Logger
from kivy.clock                 import Clock

from ORCA.utils.Sleep           import fSleep
from ORCA.utils.TypeConvert     import ToFloat
from ORCA.utils.wait.IsWaiting  import IsWaiting
from ORCA.vars.Replace          import ReplaceVars

from ORCA import Globals as Globals

aActiveQueueStack   = []
aInActiveQueueStack = []
bStop               = False

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
    if len(aInActiveQueueStack) > 0:
        oQueue = aInActiveQueueStack.pop()
        oQueue.Reset()
    else:
        oQueue = cQueue()

    return oQueue

def GetQueueLen():
    return len(aActiveQueueStack)

def GetActiveQueue():
    return aActiveQueueStack[-1]

def ClearQueue():
    """ terminates all queues """
    for oQueue in reversed(aActiveQueueStack):
        oQueue.iActionQueuePos = len(oQueue.aActionQueue)

def DumpQueue():
    """ dumps all queues """
    iStackNum=0
    for oStack in aActiveQueueStack:
        iStackNum+=1
        Logger.debug (u'Action: ========= Start Queue (' +str(iStackNum)+')  ==========')
        oStack.Dump()
        Logger.debug (u'Action: ========= End Queue (' +str(iStackNum)+')  ==========')

def StopQueue():
    bStop = True

def ResumeQueue():
    bStop = False


class cQueue(object):
    """ represents a single queue object """
    def __init__(self):
        self.aActionQueue      = []
        self.bForceState       = False
        self.iActionQueuePos   = 0
        self.bDoNow            = False
        self.Reset()

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
        iRet=-2

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

        #fNextFrame=0.0
        fNextFrame=0.0001
        while True:
            if self.iActionQueuePos < len(self.aActionQueue):
                oAction=self.aActionQueue[self.iActionQueuePos]
                Globals.oEvents.bDoNext = True
                iRetReal= Globals.oEvents.WorkOnQueueDoAction(oAction)
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

                #If we do not force working the queue and nothing to accelerate, the next execution is not next frame (to ensure screen updates)
                if not self.bForceState and not Globals.oEvents.bDoNext:
                    if not bStop:
                        if Globals.bOnSleep:
                            fNextFrame=0.5 # if we are on sleep , we switch to timed minimum queue activity
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
    def Dump(self):
        """ dumps the queue """
        Logger.debug (u'Action: ********* Start Dump  *********')
        Logger.debug (u'Action: QuePos: %d' % self.iActionQueuePos)
        for i,oAction in enumerate(self.aActionQueue):
            Logger.debug (Globals.oEvents.CreateDebugLine(oAction=oAction, uTxt=str(i)))
        Logger.debug (u'Action: ********* End Dump  *********')
