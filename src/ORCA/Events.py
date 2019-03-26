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

import                      logging
from functools              import partial
from copy                   import copy

from kivy.logger            import Logger
from kivy.clock             import Clock
from kivy.compat            import string_types


from ORCA.Action                        import CreateActionForSimpleActionList
from ORCA.Action                        import GetActionID
from ORCA.EventTimer                    import cAllTimer
from ORCA.Queue                         import GetActiveQueue
from ORCA.Queue                         import GetNewQueue
from ORCA.Queue                         import GetQueueLen
from ORCA.Queue                         import StopQueue
from ORCA.Queue                         import ResumeQueue
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

from ORCA.ui.ShowErrorPopUp             import ShowErrorPopUp
from ORCA.utils.CheckCondition          import CheckCondition
from ORCA.utils.LogError                import LogError
from ORCA.utils.TypeConvert             import ToUnicode
from ORCA.vars.Access                   import GetVar
from ORCA.vars.Access                   import SetVar
from ORCA.vars.Replace                  import ReplaceVars

import ORCA.Globals as Globals

__all__ = ['cEvents']

class cEvents(object):
    """ The core event objects which manages the queues and actions """
    def __init__(self):
        self.aEventActions = [cEventActionsFlowControl(self),
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

        self.dActionFunctions      = {}
        self.aHiddenKeyWords       = ['string','condition','name','taptype','interface','configname','conditionchecktype','conditionvar','conditionvalue','retvar','force','linefilename']
        self.aProgressBars         = []
        self.bDoNext               = False
        self.bForceState           = False
        self.oAllTimer             = cAllTimer()

        for oEventActions in self.aEventActions:
            self.RegisterEventActions(oEventActions)

    def RegisterEventActions(self,oEventActions):
        """ register all actions managed by the eventdispatcher """
        aFuncs=dir(oEventActions)
        for uFuncName in aFuncs:
            if uFuncName.startswith('ExecuteAction'):
                uName = uFuncName[13:]
                Globals.oActions.oActionType.RegisterAction(uName)
                self.dActionFunctions[Globals.oActions.oActionType.ActionToId[uName.lower()]] = getattr(oEventActions, uFuncName)

    def DeInit(self):
        """ stops all timer """
        self.oAllTimer.DeleteAllTimer()

    def StopQueue(self):
        """ Stops the latest queue """
        StopQueue()

    def UnPauseQueue(self):
        """ restarts a queue by reactivating the timer """
        ResumeQueue()
        Clock.schedule_once(partial(GetActiveQueue().WorkOnQueue,self.bForceState),0)


    def ExecuteActionsNewQueue(self,aActions, oParentWidget, bForce=False):
        """ Execute all actions in a new queue, new queue will atomatic appended to the queue stack"""
        oQueue = GetNewQueue()
        oQueue.bForceState = bForce
        bRet = self._ExecuteActions(aActions=aActions,oParentWidget=oParentWidget)
        return bRet

    def ExecuteActions(self,aActions, oParentWidget):
        """ execute actions by either adding multiple actions to a new queue, or appending a single action to the existing queue """
        if len(aActions) > 1:
            self.ExecuteActionsNewQueue(aActions, oParentWidget)
        else:
            self._ExecuteActions(aActions, oParentWidget)

    def _ExecuteActions(self,aActions, oParentWidget):
        """ This functions just adds the action commands to the queue and calls the scheduler at the end """

        oQueue = GetActiveQueue()

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
                oTmpAction = copy(aTmpAction)
                oTmpAction.dActionPars['string']='enabletransmitterpicture'
                oTmpAction.iActionId = GetActionID(oTmpAction.dActionPars['string'])
                self.__InsertToQueue(oTmpAction, oQueue)
            if iActionId == Globals.oActions.oActionType.ShowPage:
                oTmpAction = copy(aTmpAction)
                oTmpAction.dActionPars['string'] = 'call'
                oTmpAction.dActionPars['actionname'] = 'PAGESTOPACTIONS'
                oTmpAction.iActionId = GetActionID(oTmpAction.dActionPars['string'])
                self.__InsertToQueue(oTmpAction, oQueue)

            self.__InsertToQueue(oAction, oQueue)

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
                self.__InsertToQueue(oTmpAction, oQueue)
            if iActionId == Globals.oActions.oActionType.SendCommand:
                oTmpAction = copy(aTmpAction)
                oTmpAction.dActionPars['string'] = 'disabletransmitterpicture'
                oTmpAction.iActionId = GetActionID(oTmpAction.dActionPars['string'])
                self.__InsertToQueue(oTmpAction, oQueue)

        oQueue = GetActiveQueue()
        if not oQueue.bForceState:
            Clock.schedule_once(partial(oQueue.WorkOnQueue,oQueue.bForceState), 0)
        else:
            return oQueue.WorkOnQueue(oQueue.bForceState)

    def __InsertToQueue(self,oAction, oQueue):
        """ insert an action to the latest queue """
        if not oAction.bForce:
            oQueue.aActionQueue.append(copy(oAction))
        else:
            self.WorkOnQueueDoAction(oAction)
        return

    def ForceWorkQueue(self):
        """ explicit starts a queue """
        GetActiveQueue().WorkOnQueue(True,None)



    def GetTargetInterfaceAndConfig(self,oAction):
        """
        Gets the interface and config for an sendcommand action
        If interfaces has not been set, we set the page defaults
        but we need to restore old values, as actions could be used from several pages  """

        uOrgInterFace  =   oAction.dActionPars.get(u'interface',u'')
        uOrgConfigName =   oAction.dActionPars.get(u'configname',u'')

        #Interface / config detection
        #Action Interfaces rules
        #then Widget Interface
        #then Anchor Interface
        #then Page Interface

        uToUseInterFace  = uOrgInterFace
        uToUseConfigName = uOrgConfigName

        if oAction.oParentWidget:
            if uToUseInterFace==u'':
                uToUseInterFace=oAction.oParentWidget.uInterFace
            if uToUseConfigName==u'':
                uToUseConfigName=oAction.oParentWidget.uConfigName

            if uToUseInterFace==u'':
                uAnchorName=oAction.oParentWidget.uAnchorName
                while uAnchorName!=u'':
                    oTmpAnchor=oAction.oParentWidget.oParentScreenPage.dWidgets.get(uAnchorName)
                    if oTmpAnchor:
                        uToUseInterFace=oTmpAnchor.uInterFace
                        uAnchorName=oTmpAnchor.uInterFace
                    if uToUseInterFace!="":
                        break

            if uToUseInterFace==u'':
                uToUseInterFace=oAction.oParentWidget.oParentScreenPage.uDefaultInterface
            if uToUseConfigName==u'':
                uAnchorName=oAction.oParentWidget.uAnchorName
                while uAnchorName!=u'':
                    # oTmpAnchor=oAction.oParentWidget.oParentScreenPage.dWidgets.get(oAction.oParentWidget.uAnchorName)
                    oTmpAnchor = oAction.oParentWidget.oParentScreenPage.dWidgets.get(uAnchorName)
                    if oTmpAnchor:
                        uToUseConfigName=oTmpAnchor.uConfigName
                        uAnchorName=oTmpAnchor.uInterFace
                    if uToUseConfigName!="":
                        break

            if uToUseConfigName==u'':
                uToUseConfigName=oAction.oParentWidget.oParentScreenPage.uDefaultConfigName

        uToUseConfigName = ReplaceVars(uToUseConfigName)
        uToUseInterFace  = ReplaceVars(uToUseInterFace)

        # We already should have loaded all interfaces at Definitionstart, but if this fails caused by heavy var tweaking, we ensure to load it here
        Globals.oInterFaces.LoadInterface(uToUseInterFace)

        return uToUseInterFace,uToUseConfigName

    def WorkOnQueueDoAction(self,oAction):
        """ Executes a single action in a queue (including condition verifying)"""

        iRet=0
        bCheckSuccess=CheckCondition(oAction)

        if oAction.iActionId==Globals.oActions.oActionType.If:
            # we do the If statement only in case of the condition fails
            if bCheckSuccess:
                self.LogAction("if",oAction, "executing actions")
            # we need to run the if command in any way to skip the actions
            bCheckSuccess=not bCheckSuccess

        if bCheckSuccess:
            #We set / replace Action Command Pars by Definition/Button pars
            #if oAction.oParentWidget:
            #    self.CopyActionPars(dTarget=oAction.dActionPars,dSource=oAction.oParentWidget.dActionPars,uReplaceOption="donotcopyempty")

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
            oFunction=self.dActionFunctions.get(oAction.iActionId)
            if oFunction:
                return oFunction(oAction)
            else:
                ''' this enables to use standardactions / actions without call, but assigning parameters like interface and configname '''

                aActions=Globals.oActions.GetActionList(uActionName = oAction.uActionString, bNoCopy = True)
                if aActions:
                    if len(aActions)>1:
                        Logger.error("you can''t use multiline actions as short cut, use call instead")

                    oFunction=self.dActionFunctions.get(aActions[0].iActionId)
                    if oFunction:
                        oAction.uActionString=ReplaceVars(aActions[0].uActionString)
                        self.CopyActionPars(dTarget=oAction.dActionPars,dSource=aActions[0].dActionPars,uReplaceOption="donotreplacetarget")
                        if not oAction.uRetVar:
                            oAction.uRetVar=aActions[0].uRetVar
                        return oFunction(oAction)
                Logger.error("ExecuteAction: Action not Found:"+oAction.uActionName+':'+oAction.uActionString)
                return 0
        except Exception as e:
            uMsg=LogError('Error executing Action:'+self.CreateDebugLine(oAction=oAction, uTxt=''),e)
            ShowErrorPopUp(uMessage=uMsg)
            return False

        return False

    def CopyActionPars(self, dSource, dTarget, uReplaceOption, bIgnoreHiddenWords=False):
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

    def CreateDebugLine(self,oAction, uTxt):
        """ Creates a debugline for the logger """

        if uTxt:
            uTemp=u'Action QL%d: (%s) | %s | %s' % (GetQueueLen(),oAction.uActionName,uTxt,oAction.dActionPars.get('string',''))
        else:
            uTemp=u'Action QL%d: (%s) | %s'  % (GetQueueLen(),oAction.uActionName,oAction.dActionPars.get('string',''))

        for uKey in oAction.dActionPars:
            if not uKey in self.aHiddenKeyWords:
                uValue=oAction.dActionPars[uKey]
                if isinstance(uValue,string_types):
                    if '$var' in uValue or '$lvar' in uValue:
                        uValue=u'{0} [{1}]'.format(uValue , ReplaceVars(uValue))
                else:
                    uValue=u"[unknown object]"
                uTemp+=u'| %s:%s' % (uKey,uValue)
        return ToUnicode(uTemp)

    def LogAction(self,uTxt,oAction,uAddText=''):
        """ Logs an action """

        if Logger.getEffectiveLevel()!=logging.DEBUG:
            return
        uTemp=self.CreateDebugLine(oAction,uTxt=uTxt)

        if uAddText:
            uTemp+=u"| "+uAddText
        try:
            Logger.debug (uTemp)
        except:
            Logger.error ("Cant Create Debugline")

    def CreateSimpleActionList(self,aActions):
        """ Creates a simple action list from an array of action """
        aTmpActions  = []
        self.AddToSimpleActionList(aTmpActions,aActions)
        return aTmpActions

    def AddToSimpleActionList(self,aActionList,aActions):
        """ Adds a set actions to the action list """
        for aAction in aActions:
            aActionList.append(CreateActionForSimpleActionList(aAction))
