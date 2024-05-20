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

from typing                     import Dict
from typing                     import List
from copy                       import copy
from kivy.logger                import Logger

from ORCA.actions.Base          import cEventActionBase
from ORCA.vars.Replace          import ReplaceVars
from ORCA.utils.TypeConvert     import ToDic
from ORCA.action.Action import cAction
from ORCA.actions.ReturnCode    import eReturnCode
from ORCA.action.ActionType import eReplaceOption

from ORCA.Globals import Globals

__all__ = ['cEventActionsNotifications']

class cEventActionsNotifications(cEventActionBase):
    """ Actions for managing notification """

    def ExecuteActionSendNotification(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-SendNotification
        WikiDoc:TOCTitle:noaction

        = sendnotification =
        Will send an ORCA internal notification
        This action will not modify the error code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        ! align="left" | notification
        ! align="left" | actionpars
        |-
        |sendnotification
        |notification string to send
        |Optional: Actionpars to be submitted: Format "{'parname1':'varvalue1','parname2':'varvalue2'}"
        |}</div>
        WikiDoc:End
        """

        uNotification:str                   = ReplaceVars(oAction.dActionPars.get('notification',''))
        dActionPars:Dict                    = ToDic(ReplaceVars(oAction.dActionPars.get('actionpars','{}')))
        if not isinstance(dActionPars,dict):
            dActionPars = ToDic(oAction.dActionPars.get('actionpars', '{}'))
        self.oEventDispatcher.LogAction(uTxt='SendNotification',oAction=oAction)

        Globals.oNotifications.SendNotification(uNotification=uNotification,**dActionPars)
        return eReturnCode.Nothing


    def ExecuteActionRegisterNotification(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-RegisterNotification
        WikiDoc:TOCTitle:noaction

        = registernotification =
        Will register an ORCA internal notification
        This action will not modify the error code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        ! align="left" | notification
        ! align="left" | notifyaction
        ! align="left" | filterpagename
        |-
        |registernotification
        |notification string to register
        |action to be executed
        |Page filter on which the the action should be applied. This can be "ALL" execute it independent of the pagename (default). Can be "NOPOPUP" to execute it only on non popup pages, Can be "POPUP" to execute it on all popup pages. Can be "FIRSTPAGE" to execute it only the first shown definition page, Does not execute it multiple time
        |}</div>

        All further parameter will passed as actions pars to the action

        WikiDoc:End
        """

        uPageName:str = ReplaceVars(oAction.dActionPars.get('filterpagename', ''))
        self.oEventDispatcher.LogAction(uTxt='RegisterNotification',oAction=oAction)

        if uPageName == 'ALL':
            for uPageKey in Globals.oTheScreen.oScreenPages:
                oCopyAction:cAction = copy(oAction)
                oCopyAction.dActionPars['filterpagename'] = uPageKey
                self.ExecuteActionRegisterNotification_sub(oCopyAction)
        elif uPageName == 'NOPOPUP':
            for uPageKey in Globals.oTheScreen.oScreenPages:
                if not Globals.oTheScreen.oScreenPages[uPageKey].bIsPopUp:
                    oCopyAction:cAction = copy(oAction)
                    oCopyAction.dActionPars['filterpagename'] = uPageKey
                    self.ExecuteActionRegisterNotification_sub(oCopyAction)
        elif uPageName == 'POPUP':
            for uPageKey in Globals.oTheScreen.oScreenPages:
                if Globals.oTheScreen.oScreenPages[uPageKey].bIsPopUp:
                    oCopyAction:cAction = copy(oAction)
                    oCopyAction.dActionPars['filterpagename'] = uPageKey
                    self.ExecuteActionRegisterNotification_sub(oCopyAction)
        else:
            self.ExecuteActionRegisterNotification_sub(oAction)
        return eReturnCode.Nothing

    def ExecuteActionRegisterNotification_sub(self,oAction:cAction) -> eReturnCode:
        uNotification:str                   = ReplaceVars(oAction.dActionPars.get('notification',''))
        uActionName:str                     = ReplaceVars(oAction.dActionPars.get('notifyaction',''))

        uRegisterOption:str                 = oAction.dActionPars.get('registeroption','replace')
        uFilterPageName:str                 = oAction.dActionPars.get('filterpagename','')
        if uRegisterOption == 'append':
            Globals.oNotifications.RegisterNotification(uNotification=uNotification, fNotifyFunction=self.NotificationHandler, uDescription='Action:' + uActionName, bQuiet=True, **oAction.dActionPars)
        else:
            uKey:str = uNotification+'_'+uFilterPageName
            iHash:int = Globals.oNotifications.dFilterPageNames.get(uKey,0)
            if iHash != 0:
                Globals.oNotifications.UnRegisterNotification_ByHash(iHash=iHash)
            Globals.oNotifications.RegisterNotification(uNotification=uNotification, fNotifyFunction=self.NotificationHandler, uDescription='Action:' + uActionName, bQuiet=True, **oAction.dActionPars)
        return eReturnCode.Nothing

    # noinspection PyMethodMayBeStatic
    def NotificationHandler(self,**kwargs):
        uActionName:str     = kwargs['notifyaction']
        uFilterPageName:str = kwargs.get('filterpagename','')

        if uFilterPageName  == 'FIRSTPAGE':
            uFilterPageName=Globals.oTheScreen.uFirstPageName
        if uFilterPageName  == 'CURRENT':
            uFilterPageName=Globals.oTheScreen.uCurrentPageName
        if uActionName and ((uFilterPageName == Globals.oTheScreen.uCurrentPageName) or uFilterPageName=='' ):
            aActions:List[cAction]=Globals.oActions.GetActionList(uActionName = uActionName, bNoCopy = False)
            if aActions is not None:
                aTmpActions:List[cAction] = []
                for oAction in aActions:
                    Globals.oEvents.CopyActionPars(dTarget=oAction.dActionPars,dSource=kwargs,enReplaceOption=eReplaceOption.eDoNotCopyEmpty)
                    aTmpActions.append(oAction)
                Logger.debug('Notification: Execute Action for notification: %s, Action: %s' % (kwargs['notification'], uActionName))
                Globals.oEvents.ExecuteActions( aActions=aTmpActions,oParentWidget=None)
                return True
            else:
                Logger.warning ('Notification: Action handler not found: Notification: %s, Action: %s'%(kwargs['notification'],uActionName))
        else:
            pass
            # Logger.debug('Notification: Action not for this page:%s, Action: %s ' % (kwargs['notification'], uActionName))
