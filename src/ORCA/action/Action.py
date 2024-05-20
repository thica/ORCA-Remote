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
from __future__ import annotations
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from xml.etree.ElementTree import Element

from copy                   import copy
from kivy.logger            import Logger
from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.TypeConvert import ToDic
from ORCA.utils.LogError    import LogError
from ORCA.vars.Helpers      import CopyDict


from ORCA.Globals import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.widgets.base.Base import cWidgetBase
else:
    from typing import TypeVar
    cWidgetBase = TypeVar('cWidgetBase')


__all__ = ['cAction','GetActionID','CreateActionForSimpleActionList']

dSplitActions:Dict[str,Dict] =     {'if':           {'DstPars': ['condition'],          'SrcParsToken': ''},
                                    'showpage':     {'DstPars': ['pagename'],           'SrcParsToken': ''},
                                    'call':         {'DstPars': ['actionname'],         'SrcParsToken': ''},
                                    'setvar':       {'DstPars': ['varname','varvalue'], 'SrcParsToken': '='},
                                    'goto':         {'DstPars': ['label'],              'SrcParsToken': ''},
                                    'dump':         {'DstPars': ['type'],               'SrcParsToken': ''},
                                    'wait':         {'DstPars': ['time'],               'SrcParsToken': ''},
                                    'updatewidget': {'DstPars': ['widgetname'],         'SrcParsToken': ''},
                                    'blockgui':     {'DstPars': ['status'],             'SrcParsToken': ''},
                                    'sendcommand':  {'DstPars': ['commandname'],        'SrcParsToken': ''},
                                    'modifyvar':    {'DstPars': ['varname'],            'SrcParsToken': ''},
                                    }

def CreateActionForSimpleActionList(dAction:Dict) -> cAction:
    """ Creates a single action for the actionlist """
    return cAction(pars=dAction)

def GetActionID(uID:str) -> int:
    """ Returns the action to an ID """
    return Globals.oActions.oActionType.dActionToId.get(uID,Globals.oActions.oActionType.NoAction)

class cAction:
    """ The Action Representation """

    def __init__(self,**kwargs):
        self.bForce:bool                        = False
        self.dActionPars:Dict                   = {}
        self.dCommandParameter:Dict             = {}  # just internal for interfaces
        self.iActionId:int                      = 0
        self.oParentWidget:Optional[cWidgetBase]= None
        self.uActionName:str                    = ''
        self.uActionString:str                  = ''
        self.uActionTapType:str                 = 'both'  # could be both, single, double
        self.uFileName:str                      = ''
        self.uRetVar:str                        = ''
        self.uCmd:str                           = ''
        self.bWaitForResponse:bool              = False  # Used for Codeset Actions

        # for resultparser
        self.uParseResultOption:str             = ''
        self.uParseResultTokenizeString:str     = ''
        self.uParseResultFlags:str              = ''
        self.uGetVar:str                        = ''
        self.uGlobalDestVar:str                 = ''
        self.uLocalDestVar:str                  = ''
        self.iCodeOK:int                        = 0  # used by some interfaces
        self.uFunctionContext:str

        if 'actionname' in kwargs:
            self.iActionId             = GetActionID(kwargs['actionname'])
            self.dActionPars['string'] = kwargs['actionname']
            self.uActionString         = kwargs['actionname']
        if 'actionstring' in kwargs:
            self.dActionPars['string'] = kwargs['actionstring']
            self.uActionString         = kwargs['actionstring']

        self.oParentWidget    = kwargs.get('parentwidget',None)
        self.uFunctionContext = kwargs.get('functionname', '')

        if 'pars' in kwargs:
            self.ParseAction(vSource=kwargs['pars'],oParentWidget=self.oParentWidget)


    def __copy__(self) -> cAction:
        oRes:cAction            = cAction()
        oRes.__dict__           = self.__dict__.copy()

        oRes.dActionPars        = CopyDict(self.dActionPars)
        oRes.dCommandParameter  = CopyDict(self.dCommandParameter)

        oRes.bForce             = self.bForce
        oRes.iActionId          = self.iActionId
        oRes.oParentWidget      = self.oParentWidget
        oRes.uActionName        = self.uActionName
        oRes.uActionString      = self.uActionString
        oRes.uActionTapType     = self.uActionTapType
        oRes.uFileName          = self.uFileName
        oRes.uRetVar            = self.uRetVar
        oRes.uFunctionContext   = self.uFunctionContext

        return oRes

    def ParseAction(self,*,vSource:Union[str,Dict,Element],oParentWidget:Optional[cWidgetBase]=None) -> None:
        """
        Parses the action parameter in the action
        :param vSource: The sources for the values, could be a string, a dict or a xml element
        :param oParentWidget: The parent widget for the action
        :return: None
        """
        try:
            ''' parses an action from a given element , could be a dict or a XML node'''
            if isinstance(vSource, str):
                Logger.error('Invalid Action Parameter:'+vSource)
                self.uActionString      =  'noaction'
                self.iActionId          =  GetActionID(self.uActionString)
                return

            if isinstance(vSource, dict):
                self.dActionPars=vSource
            else:
                self.dActionPars=copy(vSource.attrib)

            if self.uFunctionContext:
                for uKey in self.dActionPars:
                    self.dActionPars[uKey]=self.dActionPars[uKey].replace('$par(',f'$var({self.uFunctionContext}_parameter_')

            if 'commandparameter' in self.dActionPars:
                self.dActionPars['commandparameter']= ToDic(self.dActionPars.get('commandparameter'))

            self.uActionString      =  self.dActionPars.get('string','noaction')
            self.SplitAction(uActionString=self.uActionString)

            ''' Parses an action from a Source object '''
            self.oParentWidget      =  oParentWidget
            self.uActionName        =  self.dActionPars.get('name','noname')

            self.uActionString      =  self.dActionPars.get('string','noaction')
            self.iActionId          =  GetActionID(self.uActionString)
            self.uActionTapType     =  self.dActionPars.get('taptype','both')

            # uConfigName:str = ''
            uInterFace:str  = ''

            if self.oParentWidget:
                uInterFace         =  self.dActionPars.get('interface',oParentWidget.oParentScreenPage.uDefaultInterface)

            uInterFace         =  self.dActionPars.get('interface',uInterFace)

            if uInterFace:
                Globals.oInterFaces.dUsedInterfaces[uInterFace]=True


            if self.uActionName =="gethomes":
                i=1

            self.uRetVar            =  self.dActionPars.get('retvar','')
            self.bForce             =  self.dActionPars.get('force',False)
        except Exception as e:
            LogError(uMsg='Can\'t parse Action' , oException=e)

    def SplitAction(self,*,uActionString:str) -> None:
        """
        Helper function to split an action string into the parameter
        :param uActionString: The string representing the action
        """
        i:int
        iPos:int
        uString:str
        uParameter:str
        dSplitAction:Dict
        aParameter:List
        uVarName:str
        aSeps:List[str]=['/','*','+','-','fromwar','trim']
        uSep:str

        try:
            iPos = uActionString.find(' ')
            if iPos>0:
                uString    = uActionString[:iPos]
                uParameter = uActionString[iPos+1:]
                dSplitAction = dSplitActions.get(uString)
                if dSplitAction is not None:
                    if dSplitAction['SrcParsToken']=='':
                        self.dActionPars[dSplitAction['DstPars'][0]] = uParameter
                    else:
                        aParameter=uParameter.split('=')
                        for i in range(len(dSplitAction['DstPars'])):
                            self.dActionPars[dSplitAction['DstPars'][i]] = aParameter[i]
                    if uString=="modifyvar":
                        uVarName=self.dActionPars.get('varname')
                        if uVarName:
                            for uSep in aSeps:
                                aParameter=uVarName.split(uSep)
                                if len(aParameter) >1:
                                    if uSep=='/':
                                        self.dActionPars['varname']=aParameter[0]
                                        self.dActionPars['operator']='divide'
                                        self.dActionPars['parameter1']=aParameter[1]
                                        break
                                    if uSep=='*':
                                        self.dActionPars['varname']=aParameter[0]
                                        self.dActionPars['operator']='multiply'
                                        self.dActionPars['parameter1']=aParameter[1]
                                        break
                                    if uSep=="+":
                                        self.dActionPars['varname']=aParameter[0]
                                        self.dActionPars['operator']='increase'
                                        self.dActionPars['parameter1']=aParameter[1]
                                        aParameter = aParameter[1].split(" ")
                                        if len(aParameter)>1:
                                            self.dActionPars['parameter1']=aParameter[0]
                                            self.dActionPars['parameter2']=aParameter[1]
                                        break
                                    if uSep=="-":
                                        self.dActionPars['varname']=aParameter[0]
                                        self.dActionPars['operator']='decrease'
                                        self.dActionPars['parameter1']=aParameter[1]
                                        aParameter = aParameter[1].split(" ")
                                        if len(aParameter)>1:
                                            self.dActionPars['parameter1']=aParameter[0]
                                            self.dActionPars['parameter2']=aParameter[1]
                                        break
                                    if uSep=="fromvar":
                                        self.dActionPars['varname']=aParameter[0]
                                        self.dActionPars['operator']='fromvar'
                                        break
                                    if uSep=="trim":
                                        self.dActionPars['varname']=aParameter[0]
                                        self.dActionPars['operator']='trim'
                                        break

                    self.uActionString = uString
                    self.dActionPars['string'] = uString
        except Exception as e:
            LogError(uMsg = 'Wrong Parameter for Action given:'+uActionString, oException = e)

    def Dump(self,*,iIndent:int) -> None:
        """ Dumps a specific action """

        uOut:str
        uKey:str
        uAttributeName:str

        uOut = ' ' * iIndent
        if self.uActionName:
            uOut+= self.uActionName+': '
        for uAttributeName in self.__dict__:
            oValue= self.__dict__[uAttributeName]
            if isinstance(oValue,str):
                if not '$var' in oValue:
                    uOut+=f'"{uAttributeName}"="{oValue}" , '
                else:
                    uOut+=f'"{uAttributeName}"="{oValue}" [{ReplaceVars(oValue)}] , '

            elif isinstance(oValue,dict):
                uOut=uOut+uAttributeName+':{'
                for uKey in oValue:
                    if uKey!= 'name':
                        uValue=oValue[uKey]
                        if not '$var' in uValue:
                            uOut+=f'"{uKey}"="{uValue}" , '
                        else:
                            uOut+=f'"{uKey}"="{uValue}" [{ReplaceVars(uValue)}] , '

                uOut+='} '

        Logger.debug(uOut)


