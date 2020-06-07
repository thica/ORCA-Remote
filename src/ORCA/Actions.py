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

from typing                         import Dict
from typing                         import List
from typing                         import Optional
from typing                         import Union

from copy                           import copy
from xml.etree.ElementTree          import Element

from kivy.logger                    import  Logger

from ORCA.ActionType                import cActionType
from ORCA.Action                    import cAction
from ORCA.utils.FileName            import cFileName
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import LoadXMLFile

import ORCA.Globals as Globals


class cActions:
    """ The Actions Representation """
    def __init__(self):
        self.dActionsCommands:Dict       = {}
        self.dActionsPageStart:Dict      = {}
        self.dActionsPageStop:Dict       = {}
        self.oActionType:cActionType     = cActionType()
        self.iIndent:int                 = 0

    def InitVars(self) -> None:
        """ (re) Initialisises all Actions (also after a definition change) """
        self.dActionsCommands.clear()
        self.dActionsPageStart.clear()
        self.dActionsPageStop.clear()

    def LoadActionsAppStart(self) -> None:
        """ Loads the appstart Actions """
        Logger.debug (u'Load AppStart Actions XmlFile')
        oET_Root:Element

        oFnActionFile:cFileName = cFileName(Globals.oFnActionEarlyAppStart)

        if not oFnActionFile.Exists():
            if (len(Globals.aDefinitionList)== 0) and (not Globals.bProtected):
                oFnActionFile=Globals.oFnActionFreshInstall

        try:
            oET_Root = LoadXMLFile(oFile=oFnActionFile)
            self.LoadActionsSub(oET_Root=oET_Root ,uSegmentTag=u'appstartactions',uListTag=u'appstartaction',dTargetDic=self.dActionsPageStart,uFileName=str(oFnActionFile))
            # just in case we have some sub commands (mainly in the fall back actions command set)
            self.LoadActionsSub(oET_Root=oET_Root ,uSegmentTag=u'actions',uListTag= u'action',dTargetDic= self.dActionsCommands,uFileName=str(oFnActionFile))

        except Exception as e:
            ShowErrorPopUp(uTitle="LoadActionsAppStart: Fatal Error",uMessage=u'TheScreen: Fatal Error:Load Appstart Action XmlFile (%s)' % str(oFnActionFile),bAbort=True,oException=e)

        aActions:List[cAction] = self.dActionsPageStart.get(u'earlyappstart')
        if aActions:
            Logger.debug (u'TheScreen: Calling Early Application StartActions')
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

    # noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
    def __ParseXMLActions(self,*,oXMLNode:Element, aActions:List[cAction],uFunctionName:str) -> None:
        bFound:bool = False
        oXMLAction:List[Element]
        for oXMLAction in oXMLNode.findall('action'):
            aActions.append(cAction(pars=oXMLAction,functionname=uFunctionName))
            bFound = True
        # If we got no child actions, then we use the Command Tag as a single action
        if not bFound:
            aActions.append(cAction(pars=oXMLNode,functionname=uFunctionName))

    def LoadActionsSub(self,*,oET_Root:Element,uSegmentTag:Optional[str], uListTag:str,dTargetDic:Dict,uFileName:Union[str,cFileName]=u'') -> None:
        """
            replaceoptions
            * appendtoexisting
            * replaceexisting = replace current action
            * renameexisting = rename original actions if exist
            * renamemeifexist = rename this action
        """

        oET_SegmentsStart:Element

        try:

            if uSegmentTag:
                oET_SegmentsStart  = oET_Root.find(uSegmentTag)
            else:
                oET_SegmentsStart  = oET_Root

            if oET_SegmentsStart is not None:
                for oET_Includes in oET_SegmentsStart:
                    if oET_Includes.tag==u'includes':
                        self.LoadActionsSub(oET_Root=oET_Includes,uSegmentTag=None, uListTag=uListTag,dTargetDic=dTargetDic,uFileName=uFileName)
                    elif oET_Includes.tag==uListTag:
                        uName           = GetXMLTextAttribute(oXMLNode=oET_Includes,uTag='name',            bMandatory=True, vDefault=u'')
                        uReplaceOption  = GetXMLTextAttribute(oXMLNode=oET_Includes,uTag='replaceoption',   bMandatory=False,vDefault=u'appendtoexisting')
                        uNewname        = GetXMLTextAttribute(oXMLNode=oET_Includes,uTag='newname',         bMandatory=False,vDefault=u'')
                        aActions        = []
                        bOldExist       = True
                        aActionsOrg     = dTargetDic.get(uName)
                        if aActionsOrg is None:
                            aActionsOrg=[]
                            bOldExist       = False

                        if uReplaceOption=='appendtoexisting':
                            aActions = aActionsOrg

                        if uReplaceOption=='renameexisting' and bOldExist:
                            dTargetDic[uNewname] = aActionsOrg

                        if uReplaceOption=='renamemeifexist' and bOldExist:
                            uName=uNewname

                        self.__ParseXMLActions(oXMLNode=oET_Includes,aActions=aActions,uFunctionName=uName)
                        dTargetDic[uName]=aActions

        except Exception as e:
            ShowErrorPopUp(uTitle="LoadActionsSub: Fatal Error",uMessage=u'TheScreen: Fatal Error:Load Action XmlFile:',bAbort=True,oException=e)

    def Dump(self,*,uFilter:str) -> None:
        """ Dumps all Actions """

        uActionName:str
        aActions:List[cAction]

        for uActionName in sorted(self.dActionsCommands):
            if uFilter == u"" or uFilter in uActionName:
                aActions=self.dActionsCommands[uActionName]
                self.DumpActions_Sub(uActionName=uActionName,aActions=aActions)

        for uActionName in sorted(self.dActionsPageStart):
            if uFilter == u"" or uFilter in uActionName:
                aActions=self.dActionsPageStart[uActionName]
                self.DumpActions_Sub(uActionName=uActionName,aActions=aActions)

        for uActionName in sorted(self.dActionsPageStop):
            if uFilter == u"" or uFilter in uActionName:
                aActions=self.dActionsPageStop[uActionName]
                self.DumpActions_Sub(uActionName=uActionName,aActions=aActions)

    def DumpActions_Sub(self,*,uActionName:str,aActions:List[cAction]) -> None:
        """ Little helper for dumping actions """

        if len(aActions)==1 and uActionName==aActions[0].uActionName:
            aActions[0].Dump(iIndent=0)
        else:
            Logger.debug("Action:"+uActionName)
            for oAction in aActions:
                # noinspection PyUnresolvedReferences
                if oAction.iActionId==Globals.oActions.oActionType.EndIf:
                    self.iIndent-=2
                oAction.Dump(iIndent=4+self.iIndent)
                # noinspection PyUnresolvedReferences
                if oAction.iActionId==Globals.oActions.oActionType.If:
                    self.iIndent+=2

    def SetActionList(self, uActionName:str, aActions:List[cAction]) -> None:
        """ Adds an Actionlist to the global list of Actions """
        self.dActionsCommands[uActionName] = aActions


    def GetActionList(self, *,uActionName, bNoCopy:bool) -> List[cAction]:
        """ Returns a (copy of an) action (list)  """

        if bNoCopy:
            return self.dActionsCommands.get(uActionName)
        else:
            return self._CopyActonList(dActionList=self.dActionsCommands,uActionName=uActionName)

    def GetPageStartActionList(self,*, uActionName, bNoCopy) -> List[cAction]:
        """ Returns a (copy of an) action (list)  """

        if bNoCopy:
            return self.dActionsPageStart.get(uActionName)
        else:
            return self._CopyActonList(dActionList=self.dActionsPageStart,uActionName=uActionName)

    def GetPageStopActionList(self,*, uActionName, bNoCopy) -> List[cAction]:
        """ Returns a (copy of an) action (list)  """
        if bNoCopy:
            return self.dActionsPageStop.get(uActionName)
        else:
            return self._CopyActonList(dActionList=self.dActionsPageStop,uActionName=uActionName)

    @staticmethod
    def _CopyActonList(*,dActionList:Dict, uActionName:str) -> Optional[List[cAction]]:
        """ Creates a copy of an action list  """
        aList:List[cAction] = dActionList.get(uActionName)
        if aList is None:
            return None
        aRet = []
        for oElem in aList:
            aRet.append(copy(oElem))
        return  aRet
