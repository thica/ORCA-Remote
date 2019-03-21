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

from copy                           import copy

from kivy.logger                    import  Logger

from ORCA.Action                    import cAction
from ORCA.Action                    import cActionType
from ORCA.utils.FileName            import cFileName
from ORCA.utils.LogError            import LogError
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import LoadXMLFile

import ORCA.Globals as Globals

class cActions(object):
    """ The Actions Representation """
    def __init__(self):
        self.dActionsCommands       = {}
        self.dActionsPageStart      = {}
        self.dActionsPageStop       = {}
        self.oActionType            = cActionType()
        self.iIndent                = 0
    def InitVars(self):
        """ (re) Initialisises all Actions (also after a definition change) """
        self.dActionsCommands.clear()
        self.dActionsPageStart.clear()
        self.dActionsPageStop.clear()

    def LoadActionsAppStart(self):
        """ Loads the appstart Actions """
        Logger.debug (u'Load AppStart Actions XmlFile')

        oFnActionFile = cFileName(Globals.oFnActionEarlyAppStart)

        if not oFnActionFile.Exists():
            if (len(Globals.aDefinitionList)== 0) and (not Globals.bProtected):
                oFnActionFile=Globals.oFnActionFreshInstall

        try:
            oET_Root = LoadXMLFile(oFnActionFile)
            self.LoadActionsSub(oET_Root ,u'appstartactions',u'appstartaction',self.dActionsPageStart,oFnActionFile.string)
            # just in case we have some sub commands (mainly in the fall back actions command set)
            self.LoadActionsSub(oET_Root ,u'actions',u'action',self.dActionsCommands,oFnActionFile.string)

        except Exception as e:
            uMsg=LogError(u'TheScreen: Fatal Error:Load Appstart Action XmlFile (%s)' % (oFnActionFile.string),e)
            ShowErrorPopUp(uTitle="Fatal Error",uMessage=uMsg,bAbort=True)

        aActions=self.dActionsPageStart.get(u'earlyappstart')
        if aActions:
            Logger.debug (u'TheScreen: Calling Early Application StartActions')
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        oET_Root=None

    def __ParseXMLActions(self, oXMLNode, aActions):
        for oXMLAction in oXMLNode.findall('action'):
            oTmpAction=cAction()
            oTmpAction.ParseAction(oXMLAction,None)
            aActions.append(oTmpAction)
        # If we got no child actions, then we use the Command Tag as a single action
        if len(aActions)==0:
            oTmpAction=cAction()
            oTmpAction.ParseAction(oXMLNode,None)
            aActions.append(oTmpAction)

    def LoadActionsSub(self,oET_Root,uSegmentTag, uListTag,aTargetDic,uFileName=u''):
        """
            replaceoptions
            * appendtoexisting
            * replaceexisting = replace current action
            * renameexisting = rename original actions if exist
            * renamemeifexist = rename this action
        """

        try:

            if uSegmentTag:
                oET_SegmentsStart  = oET_Root.find(uSegmentTag)
            else:
                oET_SegmentsStart  = oET_Root

            if oET_SegmentsStart is not None:
                for oET_Includes in oET_SegmentsStart:
                    if oET_Includes.tag==u'includes':
                        self.LoadActionsSub(oET_Includes,None, uListTag,aTargetDic,uFileName)
                    elif oET_Includes.tag==uListTag:
                        uName=GetXMLTextAttribute(oET_Includes,'name',True,u'')
                        uReplaceOption = GetXMLTextAttribute(oET_Includes,'replaceoption',False,u'appendtoexisting')

                        uNewname       = GetXMLTextAttribute(oET_Includes,'newname',False,u'')
                        aActions        = []
                        bOldExist       = True
                        aActionsOrg     = aTargetDic.get(uName)
                        if aActionsOrg is None:
                            aActionsOrg=[]
                            bOldExist       = False

                        if uReplaceOption=='appendtoexisting':
                            aActions = aActionsOrg

                        if uReplaceOption=='renameexisting' and bOldExist:
                            aTargetDic[uNewname] = aActionsOrg

                        if uReplaceOption=='renamemeifexist' and bOldExist:
                            uName=uNewname

                        self.__ParseXMLActions(oET_Includes,aActions)
                        aTargetDic[uName]=aActions

        except Exception as e:
            uMsg=LogError(u'TheScreen: Fatal Error:Load Action XmlFile:',e)
            ShowErrorPopUp(uTitle="Fatal Error",uMessage=uMsg,bAbort=True)

    def Dump(self,uFilter):
        """ Dumps all Actions """

        for uActionName in sorted(self.dActionsCommands):
            if uFilter == u"" or uFilter in uActionName:
                aActions=self.dActionsCommands[uActionName]
                self.DumpActions_Sub(uActionName,aActions)

        for uActionName in sorted(self.dActionsPageStart):
            if uFilter == u"" or uFilter in uActionName:
                aActions=self.dActionsPageStart[uActionName]
                self.DumpActions_Sub(uActionName,aActions)

        for uActionName in sorted(self.dActionsPageStop):
            if uFilter == u"" or uFilter in uActionName:
                aActions=self.dActionsPageStop[uActionName]
                self.DumpActions_Sub(uActionName,aActions)

    def DumpActions_Sub(self,uActionName,aActions):
        """ Little helper for dumping actions """

        if len(aActions)==1 and uActionName==aActions[0].uActionName:
            aActions[0].Dump(0)
        else:
            Logger.debug("Action:"+uActionName)
            for oAction in aActions:
                if oAction.iActionId==Globals.oActions.oActionType.EndIf:
                    self.iIndent-=2
                oAction.Dump(4+self.iIndent)
                if oAction.iActionId==Globals.oActions.oActionType.If:
                    self.iIndent+=2

    def SetActionList(self, uActionName, aActions):
        ''' Adds an Actionlist to the global list of Actions '''
        self.dActionsCommands[uActionName] = aActions


    def GetActionList(self, uActionName, bNoCopy):
        ''' Returns a (copy of an) action (list)  '''

        if bNoCopy:
            return self.dActionsCommands.get(uActionName)
        else:
            return self._CopyActonList(self.dActionsCommands,uActionName)

    def GetPageStartActionList(self, uActionName, bNoCopy):
        ''' Returns a (copy of an) action (list)  '''

        if bNoCopy:
            return self.dActionsPageStart.get(uActionName)
        else:
            return self._CopyActonList(self.dActionsPageStart,uActionName)

    def GetPageStopActionList(self, uActionName, bNoCopy):
        ''' Returns a (copy of an) action (list)  '''
        if bNoCopy:
            return self.dActionsPageStop.get(uActionName)
        else:
            return self._CopyActonList(self.dActionsPageStop,uActionName)

    def _CopyActonList(self,dActionList,uActionName):
        ''' Creates a copy of an action list  '''
        aList = dActionList.get(uActionName)
        if aList is None:
            return None
        aRet = []
        for oElem in aList:
            aRet.append(copy(oElem))
        return  aRet
