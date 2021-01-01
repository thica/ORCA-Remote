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

from copy import copy
from kivy.logger                import Logger
from kivy.clock                 import Clock

from ORCA.vars.Replace          import ReplaceVars
from ORCA.vars.Access           import SetVar
from ORCA.ui.ShowErrorPopUp     import ShowErrorPopUp
from ORCA.utils.LogError        import LogError
from ORCA.actions.Base          import cEventActionBase
from ORCA.Queue                 import GetActiveQueue
from ORCA.Queue                 import cQueue
from ORCA.Queue                 import DumpQueue
from ORCA.Action                import cAction
from ORCA.ScreenPage            import cScreenPage
from ORCA.actions.ReturnCode    import eReturnCode


import ORCA.Globals as Globals

__all__ = ['cEventActionsFlowControl']

class cEventActionsFlowControl(cEventActionBase):
    """ Actions for ControlFlow (if, endif, goto, call) """
    def ExecuteActionGoto(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-Goto
        WikiDoc:TOCTitle:goto

        = goto =
        Jumps to an action within a multi line action / macro. You have to use the action name of the target as a jump target. You can jump only to actions within your multi line action / macro. If the label can't be found, an error message will popup.
        You also could use a short form, where the label is added directly to the string. eg. string="goto label_end"

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |goto
        |-
        |label
        |Action to jump to
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="goto exit" string="goto" label="End Function"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """

        uLabel:str = ReplaceVars(oAction.dActionPars.get("label",""))
        oTmpAction: cAction
        i:int = 0
        self.oEventDispatcher.LogAction(uTxt=u'Goto',oAction=oAction)

        oQueue:cQueue = GetActiveQueue()
        for oTmpAction in oQueue.aActionQueue:
            if oTmpAction.uActionName==uLabel:
                oQueue.iActionQueuePos=i-1
                return eReturnCode.Nothing
            i+=1
        uMsg:str = self.oEventDispatcher.CreateDebugLine(oAction=oAction,uTxt='Wrong Goto')+u"\nFileName:"+oAction.uFileName
        Logger.error (uMsg)
        ShowErrorPopUp(uTitle='Warning',uMessage=uMsg)
        return eReturnCode.Nothing

    def ExecuteActionIf(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-If
        WikiDoc:TOCTitle:if
        = if =

        Useful, if blocks of actions should be skipped/executed on a condition. Does only make sense, if you apply a condition. For each if, there must be an endif. "if" can be nested.
        You also could use a short form, where the condition is added directly to the string. eg. string="if red!=green"
        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |if
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="if we haven't showed it by now" string="if"  condition="'$var(SHOWINSTALLATIONHINT)'=='TRUE'"/>
        <action name="SET Showflag to False" string="setvar SHOWINSTALLATIONHINT=FALSE" />
        <action name="Save Status" string="modifyvar" varname="SHOWINSTALLATIONHINT"  operator="save"  parameter1="$var(DEFINITIONNAME)"/>
        <action name="show message" string="showquestion" title="$lvar(597)" message="$var(INSTALLATIONHINT)" actionyes="dummy" condition="'$var(INSTALLATIONHINT)'!=''"/>
        <action name="" string="endif" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        #This action will be called, if "IF" fails to goto the next end if
        self.oEventDispatcher.LogAction(uTxt=u'If',oAction=oAction,uAddText="skip actions")
        iLevel:int = -1
        oTmpAction:cAction
        oQueue:cQueue = GetActiveQueue()
        i:int = oQueue.iActionQueuePos
        iActionQueuePos:int = oQueue.iActionQueuePos

        for oTmpAction in oQueue.aActionQueue[iActionQueuePos:]:
            if oTmpAction.iActionId==Globals.oActions.oActionType.If:
                iLevel+=1

            if oTmpAction.iActionId==Globals.oActions.oActionType.EndIf:
                if iLevel==0:
                    oQueue.iActionQueuePos = i
                    self.oEventDispatcher.LogAction(uTxt=u'EndIf', oAction=oTmpAction)
                    return eReturnCode.Nothing
                iLevel-=1
            i+=1
        uMsg:str = self.oEventDispatcher.CreateDebugLine(oAction=oAction,uTxt='Wrong If')+u"\nFileName:"+oAction.uFileName
        DumpQueue()

        for oTmpAction in oQueue.aActionQueue[iActionQueuePos:]:
            uMsg+=u"\n"
            uMsg+=oTmpAction.uActionName + u' '+oTmpAction.uActionString

        Logger.error (uMsg)
        ShowErrorPopUp(uTitle='Warning',uMessage=uMsg)
        return eReturnCode.Nothing

    def ExecuteActionEndIf(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-EndIf
        WikiDoc:TOCTitle:endif
        = endif =

        Closes an if condition

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |endif
        |}</div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'EndIf',oAction=oAction)
        return eReturnCode.Nothing

    def ExecuteActionExitAction(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ExitAction
        WikiDoc:TOCTitle:exitaction
        = exitaction =

        Exit the current action

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |exitaction
        |}</div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'ExitAction',oAction=oAction)
        oQueue:cQueue = GetActiveQueue()
        oQueue.iActionQueuePos=len(oQueue.aActionQueue)+1
        return eReturnCode.Nothing


    def ExecuteActionCall(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-Call
        WikiDoc:TOCTitle:call
        = call =
        Calls a single/multi line action / macro like a function. You have to use the action name of the target as a function name. You can call only  multi line actions / macros, not single actions within a macro.
        This action will modify the error code, if it fails, otherwise it will not change the error code

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |call
        |-
        |actionname
        |multi line action / macro name to call
        The actionname could be the name of an action, or one of the following keywords
        * APPSTARTACTIONS
        * DEFINITIONSTARTACTIONS
        * PAGESTARTACTIONS
        * PAGESTOPACTIONS
        |-
        |pagename
        |Optional: Name of the page, for which Pagestart/stop Actions to call (only if actionname is PAGESTARTACTIONS/PAGESTOPACTIONS)
        |-
        |currentpagename
        |Optional: Name of the the current pagename: (only if actionname is PAGESTARTACTIONS/PAGESTOPACTIONS)
        |-
        |enforce
        |Optional: attribute to enforce page startaction or page stopactions (only if actionname is PAGESTARTACTIONS/PAGESTOPACTIONS). valid options are:
        * ENFORCESTARTACTIONS
        * ENFORCESTOPACTIONS
        |}</div>

        Actionpars:
        If the call is triggered directly by a widget click, each action parameter from the widget will create a variable with name ActionName+"_parameter_"+parameter name. This enables the called function to receive parameters


        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="Return to last page" string="call gotolastpage" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        #self.oEventDispatcher.bDoNext = False
        #self.oEventDispatcher.bDoNext = True

        self.oEventDispatcher.LogAction(uTxt=u'Call',oAction=oAction)

        uActionName:str      = ReplaceVars(oAction.dActionPars.get("actionname",""))
        uEnforce:str         = ReplaceVars(oAction.dActionPars.get("enforce",""))
        uPageName:str        = ReplaceVars(oAction.dActionPars.get("pagename",""))
        uCurrentPageName:str = ReplaceVars(oAction.dActionPars.get("currentpagename",""))
        bForceState:bool     = GetActiveQueue().bForceState
        uLastPageName:str
        oLastPage:cScreenPage

        aActions:List[cAction] = Globals.oActions.GetActionList(uActionName = ReplaceVars(uActionName), bNoCopy = False)

        if aActions is None:
            if uActionName=="APPSTARTACTIONS":
                aActions=Globals.oActions.GetPageStartActionList(uActionName = u'appstart', bNoCopy=True)
                if aActions is None:
                    return eReturnCode.Nothing
            elif uActionName=="DEFINITIONSTARTACTIONS":
                aActions=Globals.oActions.GetPageStartActionList(uActionName=u'definitionstart', bNoCopy=True)
                if aActions is None:
                    return eReturnCode.Nothing
            elif uActionName=="PAGESTARTACTIONS":
                # we want to prevent pagestart actions, if the old page was just a popup, or we enforce it
                uLastPageName=""
                oLastPage=Globals.oTheScreen.oScreenPages.GetLastPageReal()
                if oLastPage:
                    uLastPageName=oLastPage.uPageName
                if (not Globals.oTheScreen.IsPopup(uPageName=uLastPageName)) or ('ENFORCESTARTACTIONS' in uEnforce):
                    aActions=Globals.oTheScreen.ShowPageGetPageStartActions(uPageName=uPageName)
                    if aActions is not None:
                        uActionName=u"PageStartAction"
                        Logger.debug("Action: () Calling PageStartAction for page: {0}".format(uPageName))
                        oAction.oParentWidget=Globals.oTheScreen.oCurrentPage.oWidgetBackGround
                    else:
                        return eReturnCode.Nothing
                else:
                    self.oEventDispatcher.LogAction(uTxt=u'Skipping PageStartAction',oAction=oAction,uAddText=u' for: {0}'.format(uPageName))
                    return eReturnCode.Nothing
            elif uActionName=="PAGESTOPACTIONS":
                # we want to prevent pagestop actions, if the new page is just a popup  or we enforce it
                # Or we want to force it
                # noinspection PyRedundantParentheses
                if (not Globals.oTheScreen.IsPopup(uPageName=uCurrentPageName) or  ("ENFORCESTOPACTIONS" in uEnforce) ):
                    aActions=Globals.oTheScreen.ShowPageGetPageStopActions(uPageName="$var(CURRENTPAGE)")
                    if aActions is not None:
                        uActionName=u"PageStopAction"
                        self.oEventDispatcher.LogAction(uTxt=u'Calling PageStopAction',oAction=oAction,uAddText=u' for: {0}'.format(ReplaceVars("$var(CURRENTPAGE)")))
                        oAction.oParentWidget=Globals.oTheScreen.oCurrentPage.oWidgetBackGround
                    else:
                        return eReturnCode.Nothing
                else:
                    self.oEventDispatcher.LogAction(uTxt=u'Skipping PageStopAction',oAction=oAction,uAddText=u' for: {0}'.format(ReplaceVars("$var(CURRENTPAGE)")))
                    return eReturnCode.Nothing

        if aActions is not None:
            # oTmpFunction=copy(oFunction)
            oTmpFunction:List[cAction] = []
            for oTmp in aActions:
                oTmpFunction.append(copy(oTmp))

            if oAction.oParentWidget is not None:
                self.oEventDispatcher.CopyActionPars(dTarget=oTmpFunction[0].dActionPars,dSource=oAction.oParentWidget.dActionPars,uReplaceOption="donotreplacetarget")
                self.oEventDispatcher.CopyActionPars(dTarget=oAction.dActionPars,dSource=oAction.oParentWidget.dActionPars,uReplaceOption="donotreplacetarget")
            else:
                self.oEventDispatcher.CopyActionPars(dTarget=oTmpFunction[0].dActionPars,dSource=oAction.dActionPars,uReplaceOption="donotreplacetarget")

            #for aActionParKey in oTmpFunction[0].dActionPars:
                #SetVar(uActionName+"_parameter_"+aActionParKey,oTmpFunction[0].dActionPars[aActionParKey])
            for aActionParKey in oAction.dActionPars:
                if aActionParKey != "linefilename" and aActionParKey != "linefilenames" :
                    # SetVar(uVarName = uActionName+"_parameter_"+aActionParKey, oVarValue = oAction.dActionPars[aActionParKey])
                    SetVar(uVarName = uActionName+"_parameter_"+aActionParKey, oVarValue = ReplaceVars(oAction.dActionPars[aActionParKey]))

            self.oEventDispatcher.ExecuteActionsNewQueue(aActions=oTmpFunction,oParentWidget=oAction.oParentWidget,bForce=bForceState)
            return eReturnCode.Nothing
        uMsg:str=self.oEventDispatcher.CreateDebugLine(oAction=oAction,uTxt='Wrong Call')+u"\nFileName:"+oAction.uFileName
        Logger.error (uMsg)
        for uKey in sorted(Globals.oActions.dActionsCommands):
            LogError(uMsg=u'Action: Call: Available Name: [%s]' % uKey)
        DumpQueue()

        ShowErrorPopUp(uTitle='Warning',uMessage=uMsg)
        return eReturnCode.Error

    def ExecuteActionStopApp(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-StopApp
        WikiDoc:TOCTitle:stopapp
        = stopapp =
        Quits Orca Remote Application (without Question)

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |stopapp
        |}</div>

        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="Stop ORCA" string="stopapp" />
        </syntaxhighlight></div>
        WikiDoc:End

        """

        self.oEventDispatcher.LogAction(uTxt=u'StopApp',oAction=oAction)
        self.oEventDispatcher.oAllTimer.DeleteAllTimer()
        self.oEventDispatcher.StopQueue()
        Clock.schedule_once(self._ExecuteActionStopApp2)
        return eReturnCode.Nothing

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _ExecuteActionStopApp2(self,instance) -> eReturnCode:
        """ Internal """
        Globals.oApp.StopApp()
        return eReturnCode.Nothing

    def ExecuteActionWait(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-Wait
        WikiDoc:TOCTitle:wait
        = wait =
        Waits for a specific time. Helpful for synchronizing remote commands. This is a blocking action. The wait time has to be passed in milliseconds
        You also could use a short form, where the wait time is added directly to the string. eg. string="wait 500"

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |wait
        |-
        |time
        |Wait time in milliseconds
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="wait some time" string="wait" time="500" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'Wait',oAction=oAction)
        return eReturnCode.Nothing
