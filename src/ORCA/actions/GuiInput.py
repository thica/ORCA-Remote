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

from ORCA.Action                import cAction
from ORCA.actions.Base          import cEventActionBase
from ORCA.ui.InputKeyboard      import ShowKeyBoard
from ORCA.ui.ProgressBar        import cProgressBar
from ORCA.ui.RaiseQuestion      import ShowQuestionPopUp
from ORCA.utils.LogError        import LogError
from ORCA.utils.wait.StartWait  import StartWait
from ORCA.utils.wait.StopWait   import StopWait
from ORCA.vars.Replace          import ReplaceVars
from ORCA.utils.TypeConvert     import ToLong

import ORCA.Globals as Globals
__all__ = ['cEventActionsGuiInput']

class cEventActionsGuiInput(cEventActionBase):
    """ Actions Gui Input (inputfields, MessageBoxes, ProgressBars) """
    def __init__(self, oEventDispatcher):
        super(cEventActionsGuiInput, self).__init__(oEventDispatcher)
        self.oQuestionAction  = None
        self.oInputKeyboard   = None

    def ExecuteActionShowProgressBar(self,oAction):

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ShowProgressBar
        WikiDoc:TOCTitle:showprogressbar
        = showprogressbar =
        Shows a progressar popup, updates the progressbar value & bar or closes a progressbar popup
        * If title and message are given, it creates a new progressbar.
        * If title is not given, but current is given, it updates the progressbar
        * If title, message and currrent are not not given, the progressbar is closed

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |showprogressbar
        |-
        |title
        |Title of the progressbar-popup
        |-
        |message
        |Message for the progress bar popup
        |-
        |current
        |Current value of the progress bar. Default is 0
        |-
        |max
        |Maximum value of the progress bar (Minimum is always 0)
        |}</div>

        If title is empty, message is empty and current is 0, the the progressbar will be closed
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="Show the popup" string="showprogressbar" title="My Title" message="My Message" max="100" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(u'ShowProgressBar',oAction)

        uTitle   = ReplaceVars(oAction.dActionPars.get("title",""))
        uMessage = ReplaceVars(oAction.dActionPars.get("message",""))
        uCurrent = ReplaceVars(oAction.dActionPars.get("current",""))
        lCurrent = ToLong(uCurrent)
        uMax     = ReplaceVars(oAction.dActionPars.get("max",""))
        lMax     = ToLong(uMax)
        self.oEventDispatcher.bDoNext = False

        if uTitle!=u'' and  lMax!=0:
            oProgressBar=cProgressBar()
            oProgressBar.Show(uTitle,uMessage,lMax)
            self.oEventDispatcher.aProgressBars.append(oProgressBar)
            return 0

        if len(self.oEventDispatcher.aProgressBars)==0:
            LogError(u'Action: Showprogressbar Failed, no active progressar')
            return 1

        oProgressBar=self.oEventDispatcher.aProgressBars[-1]

        if uTitle==u'' and  uCurrent!='':
            oProgressBar.Update(lCurrent,uMessage)
            return 0

        if uTitle==u'' and uMessage==u'' and lCurrent==0:
            oProgressBar.ClosePopup()
            self.oEventDispatcher.aProgressBars.pop()
            return 0

        LogError(u'Action: Showprogressbar Failed, wrong parameter combination')

        return 1

    def ExecuteActionShowInputField(self,oAction):
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ShowInputField
        WikiDoc:TOCTitle:showinputfield
        = showinputfield =
        This action opens a seperate page where the user can input text using the default keyboard. This could be the system software keyboard, an Orca software keyboard or a hardware keyboard. You can specify this in the settings dialog. The result of the input (the string entered) will be stored in a given variable name for usage in other functions.
        It is recommended to used the "TEXTINPUT" widget for user input, instead of calling this action directly

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |showinputfield
        |-
        |varname
        |destination varname for the input
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="Opens a input popup" string="showinputfield" varname="myinput" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.bDoNext = False
        self.oEventDispatcher.LogAction(u'ShowInputField: DestVar:',oAction)
        uVarName    = oAction.dActionPars.get("varname","")
        self.oInputKeyboard=ShowKeyBoard(uVarName,None)
        return -2

    def ExecuteActionShowQuestion(self,oAction):
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ShowQuestion
        WikiDoc:TOCTitle:showquestion
        = showquestion =
        This action open a separate page where the user can answer a question. Can be used to show a popup message as well

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |showquestion
        |-
        |title
        |Title of the question-popup
        |-
        |message
        |Message for the question bar popup (normally the question)
        |-
        |actionyes
        |Name of the action to called, if the user presses the Yes button
        |-
        |actionno
        |Name of the action to called, if the user presses the No button
        |-
        |dontstopqueue
        |Doesn't stop the queue (if set to any value). As standard, the queue will be stopped until the answer to the question has been given.
        |-
        |close
        |Closes the question popup. Use it only, when you used the dontstopqueue flag
        |}</div>

        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="My Qustion" string="showquestion" title="Mytitle" message="MyMessage" actionyes="myYesAction" actionno="myNoAction"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(u'ShowQuestion',oAction)

        oAction.uTitle     = ReplaceVars(oAction.dActionPars.get("title",""))
        oAction.uMessage   = ReplaceVars(oAction.dActionPars.get("message",""))
        oAction.uActionYes = ReplaceVars(oAction.dActionPars.get("actionyes",""))
        oAction.uActionNo  = ReplaceVars(oAction.dActionPars.get("actionno",""))
        uClose             = ReplaceVars(oAction.dActionPars.get("close",""))
        uDontStopQueue     = ReplaceVars(oAction.dActionPars.get("dontstopqueue",""))
        self.oEventDispatcher.bDoNext = False

        if uClose:
            if self.oQuestionAction:
                StopWait()
                self.oQuestionAction.oQuestionPopup.ClosePopup()
                return -2
        if uDontStopQueue=="":
            StartWait()
        self.oQuestionAction=oAction
        if oAction.uActionYes=='' and oAction.uActionNo=='':
            self.oQuestionAction.oQuestionPopup=ShowQuestionPopUp(uTitle=oAction.uTitle,uMessage=oAction.uMessage,uSound=u'message')
        elif oAction.uActionNo=='':
            self.oQuestionAction.oQuestionPopup=ShowQuestionPopUp(uTitle=oAction.uTitle,uMessage = oAction.uMessage,fktYes = self.__fktExecuteActionShowQuestionOption1,uStringYes= '$lvar(5000)',uSound= u'message')
        else:
            self.oQuestionAction.oQuestionPopup=ShowQuestionPopUp(uTitle=oAction.uTitle,uMessage = oAction.uMessage,fktYes = self.__fktExecuteActionShowQuestionOption1, fktNo = self.__fktExecuteActionShowQuestionOption2, uStringYes='$lvar(5001)',uStringNo='$lvar(5002)',uSound= u'message')
        self.oQuestionAction.oQuestionPopup.bPreventCloseOnEscKey=True
        return -2

    def __fktExecuteActionShowQuestionOption1(self, *largs):
        StopWait()
        if self.oQuestionAction.uActionYes!="" and self.oQuestionAction.uActionYes!=u'dummy':
            self.__fktExecuteActionShowQuestionOption(self.oQuestionAction.uActionYes)

    def __fktExecuteActionShowQuestionOption2(self, *largs):
        StopWait()
        if self.oQuestionAction.uActionNo!="" and self.oQuestionAction.uActionNo!=u'dummy':
            self.__fktExecuteActionShowQuestionOption(self.oQuestionAction.uActionNo)

    def __fktExecuteActionShowQuestionOption(self,uActionName):
        if not uActionName==u'':
            aActions = Globals.oEvents.CreateSimpleActionList([{'name': 'ShowQuestionTask', 'string': 'call', 'actionname': uActionName}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions, oParentWidget=None)
