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
from __future__ import annotations
from typing import Dict
from typing import List
from typing import Union
from xml.etree.ElementTree import Element

from copy                   import copy
from kivy.logger            import Logger
from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.TypeConvert import ToDic
from ORCA.utils.LogError    import LogError
from ORCA.vars.Helpers      import CopyDict


import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.widgets.base.Base import cWidgetBase
else:
    from typing import TypeVar
    cWidgetBase = TypeVar("cWidgetBase")


__all__ = ['cAction','GetActionID','CreateActionForSimpleActionList']

dSplitActions:Dict[str,Dict] =     {'if':           {'DstPars': ['condition'],          'SrcParsToken': ''},
                                    'showpage':     {'DstPars': ['pagename'],           'SrcParsToken': ''},
                                    'call':         {'DstPars': ['actionname'],         'SrcParsToken': ''},
                                    'setvar':       {'DstPars': ['varname','varvalue'], 'SrcParsToken': '='},
                                    'goto':         {'DstPars': ['label'],              'SrcParsToken': ''},
                                    'wait':         {'DstPars': ['time'],               'SrcParsToken': ''},
                                    'updatewidget': {'DstPars': ['widgetname'],         'SrcParsToken': ''},
                                    'blockgui':     {'DstPars': ['status'],             'SrcParsToken': ''},
                                    'sendcommand':  {'DstPars': ['commandname'],        'SrcParsToken': ''},
                                    }

def CreateActionForSimpleActionList(dAction:Dict) -> cAction:
    """ Creates a single action for the actionlist """
    return cAction(pars=dAction)

def GetActionID(uID:str) -> int:
    """ Returns the action to an ID """
    return Globals.oActions.oActionType.ActionToId.get(uID,Globals.oActions.oActionType.NoAction)


class cAction:
    """ The Action Representation """

    def __init__(self,**kwargs):
        self.bForce:bool                        = False
        self.dActionPars:Dict                   = {}
        self.dCommandParameter:Dict             = {}  # just internal for interfaces
        self.iActionId:int                      = 0
        self.oParentWidget:Union[cWidgetBase,None]   = None
        self.uActionName:str                    = u''
        self.uActionString:str                  = u''
        self.uActionTapType:str                 = u'both'  # could be both, single, double
        self.uFileName:str                      = u''
        self.uRetVar:str                        = u''
        self.uCmd:str                           = u''
        self.bWaitForResponse:bool              = False  # Used for Codeset Actions

        # for resultparser
        self.uParseResultOption:str             = u''
        self.uParseResultTokenizeString:str     = u''
        self.uGetVar:str                        = u''
        self.uGlobalDestVar:str                 = u''
        self.uLocalDestVar:str                  = u''
        self.uFunctionContext:str

        if "actionname" in kwargs:
            self.iActionId             = GetActionID(kwargs["actionname"])
            self.dActionPars['string'] = kwargs["actionname"]
            self.uActionString         = kwargs["actionname"]
        if "actionstring" in kwargs:
            self.dActionPars['string'] = kwargs["actionstring"]
            self.uActionString         = kwargs["actionstring"]

        self.oParentWidget    = kwargs.get("parentwidget",None)
        self.uFunctionContext = kwargs.get("functionname", "")

        if "pars" in kwargs:
            self.ParseAction(oSource=kwargs["pars"],oParentWidget=self.oParentWidget)


    def __copy__(self) -> cAction:
        oRes:cAction            = cAction()
        oRes.__dict__           = self.__dict__.copy()
        # oRes.dActionPars        = dict(self.dActionPars)
        # oRes.dCommandParameter  = dict(self.dCommandParameter)

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

    def ParseAction(self,oSource:Union[str,Dict,Element],oParentWidget:Union[cWidgetBase,None]=None) -> None:
        try:
            ''' parses an action from a given element , could be a dict or a XML node'''
            if isinstance(oSource, str):
                Logger.error("Invalid Action Parameter:"+oSource)
                self.uActionString      =  'noaction'
                self.iActionId          =  GetActionID(self.uActionString)
                return

            if isinstance(oSource, dict):
                self.dActionPars=oSource
            else:
                self.dActionPars=copy(oSource.attrib)

            if self.uFunctionContext:
                for uKey in self.dActionPars:
                    self.dActionPars[uKey]=self.dActionPars[uKey].replace("$par(","$var("+self.uFunctionContext+"_parameter_")

            if "commandparameter" in self.dActionPars:
                self.dActionPars["commandparameter"]= ToDic(self.dActionPars.get("commandparameter"))

            self.uActionString      =  self.dActionPars.get(u'string',u'noaction')
            self.SplitAction(self.uActionString)

            ''' Parses an action from a Source object '''
            self.oParentWidget      =  oParentWidget
            self.uActionName        =  self.dActionPars.get(u'name',u'noname')

            self.uActionString      =  self.dActionPars.get(u'string',u'noaction')
            self.iActionId          =  GetActionID(self.uActionString)
            self.uActionTapType     =  self.dActionPars.get(u'taptype',u'both')

            # uConfigName:str = u''
            uInterFace:str  = u''

            if self.oParentWidget:
                uInterFace         =  self.dActionPars.get(u'interface',oParentWidget.oParentScreenPage.uDefaultInterface)
                # uConfigName        =  self.dActionPars.get(u'configname',oParentWidget.oParentScreenPage.iDefaultConfigName)

            uInterFace         =  self.dActionPars.get(u'interface',uInterFace)

            if uInterFace:
                Globals.oInterFaces.dUsedInterfaces[uInterFace]=True

            self.uRetVar            =  self.dActionPars.get(u'retvar',u'')
            self.bForce             =  self.dActionPars.get(u'force',False)
        except Exception as e:
            LogError(uMsg="Cant parse Action" , oException=e)

    def SplitAction(self,uActionString:str) -> None:

        i:int
        iPos:int
        uString:str
        uParameter:str
        dSplitAction:Dict
        aParameter:List

        try:
            iPos = uActionString.find(" ")
            if iPos>0:
                uString    = uActionString[:iPos]
                uParameter = uActionString[iPos+1:]
                dSplitAction = dSplitActions.get(uString)
                if dSplitAction is not None:
                    if dSplitAction['SrcParsToken']==u'':
                        self.dActionPars[dSplitAction['DstPars'][0]] = uParameter
                    else:
                        aParameter=uParameter.split(u"=")
                        for i in range(len(dSplitAction['DstPars'])):
                            self.dActionPars[dSplitAction['DstPars'][i]] = aParameter[i]
                    self.uActionString = uString
                    self.dActionPars['string'] = uString
        except Exception as e:
            LogError(uMsg = "Wrong Parameter for Action given:"+uActionString, oException = e)

    def Dump(self,iIndent:int) -> None:
        """ Dumps a specific action """

        uOut:str
        uKey:str
        uAttributName:str

        uOut = u" " * iIndent
        if self.uActionName:
            uOut+= self.uActionName+": "
        for uAttributName in self.__dict__:
            oValue= self.__dict__[uAttributName]
            if isinstance(oValue,str):
                if not "$var" in oValue:
                    uOut+="'%s'='%s' , " % (uAttributName,oValue)
                else:
                    uOut+="'%s'='%s [%s]' , " % (uAttributName,oValue,ReplaceVars(oValue))

            elif isinstance(oValue,dict):
                uOut=uOut+uAttributName+":{"
                for uKey in oValue:
                    if uKey!= "name":
                        uValue=oValue[uKey]
                        if not "$var" in uValue:
                            uOut+="'%s'='%s' , " % (uKey,uValue)
                        else:
                            uOut+="'%s'='%s [%s]' , " % (uKey,uValue,ReplaceVars(uValue))

                uOut+="} "

        Logger.debug(uOut)


