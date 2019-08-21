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

from copy                   import copy
from kivy.compat            import string_types
from kivy.logger            import Logger

from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.LogError    import LogError
from ORCA.vars.Helpers      import CopyDict

import ORCA.Globals as Globals

__all__ = ['cAction','cActionType','GetActionID','CreateActionForSimpleActionList']

dSplitActions = {   'if':           {'DstPars': ['condition'],          'SrcParsToken': ''},
                    'showpage':     {'DstPars': ['pagename'],           'SrcParsToken': ''},
                    'call':         {'DstPars': ['actionname'],         'SrcParsToken': ''},
                    'setvar':       {'DstPars': ['varname','varvalue'], 'SrcParsToken': '='},
                    'goto':         {'DstPars': ['label'],              'SrcParsToken': ''},
                    'wait':         {'DstPars': ['time'],               'SrcParsToken': ''},
                    'updatewidget': {'DstPars': ['widgetname'],         'SrcParsToken': ''},
                    }

def CreateActionForSimpleActionList(dAction):
    """ Creates a single action for the actionlist """
    return cAction(pars=dAction)

def GetActionID(uID):
    """ Returns the action to an ID """
    return Globals.oActions.oActionType.ActionToId.get(uID,Globals.oActions.oActionType.NoAction)

class cActionType(object):
    """ Representation of an action type object """

    def __init__(self):
        self.iValue = 0
        self.ActionToId = {}

    def RegisterAction(self,uActionName):
        setattr(self, uActionName, self.iValue)
        self.ActionToId[uActionName.lower()] = self.iValue
        self.iValue+=1


class cAction(object):
    """ The Action Representation """

    def __init__(self,**kwargs):
        self.bForce             = False
        self.dActionPars        = {}
        self.dCommandParameter  = {}  # just internal for interfaces
        self.iActionId          = 0
        self.oParentWidget      = None
        self.uActionName        = u''
        self.uActionString      = u''
        self.uActionTapType     = u'both'  # could be both, single, double
        self.uFileName          = u''
        self.uRetVar            = u''
        self.uFunctionContext   = u''

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


    def __copy__(self):
        oRes=cAction()
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

    def ParseAction(self,oSource,oParentWidget=None):
        try:
            ''' parses an action from a given element , could be a dict or a XML node'''
            if isinstance(oSource, string_types):
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


            self.uActionString      =  self.dActionPars.get(u'string',u'noaction')
            self.SplitAction(self.uActionString)

            ''' Parses an action from a Source object '''
            self.oParentWidget      =  oParentWidget
            self.uActionName        =  self.dActionPars.get(u'name',u'noname')

            self.uActionString      =  self.dActionPars.get(u'string',u'noaction')
            self.iActionId          =  GetActionID(self.uActionString)
            self.uActionTapType     =  self.dActionPars.get(u'taptype',u'both')

            uConfigName = u''
            uInterFace  = u''

            if self.oParentWidget:
                uInterFace         =  self.dActionPars.get(u'interface',oParentWidget.oParentScreenPage.uDefaultInterface)
                uConfigName        =  self.dActionPars.get(u'configname',oParentWidget.oParentScreenPage.iDefaultConfigName)

            uInterFace         =  self.dActionPars.get(u'interface',uInterFace)

            if uInterFace:
                Globals.oInterFaces.dUsedInterfaces[uInterFace]=True

            self.uRetVar            =  self.dActionPars.get(u'retvar',u'')
            self.bForce             =  self.dActionPars.get(u'force',False)
        except Exception as e:
            LogError("Cant parse Action" , e)

    def SplitAction(self,uActionString):

        try:
            dRet = {}
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
            LogError("Wrong Parameter for Action given:"+uActionString, e)

    def Dump(self,iIndent):
        """ Dumps a specific action """

        uOut = " " * iIndent
        if self.uActionName:
            uOut+= self.uActionName+": "
        for uAttributName in self.__dict__:
            oValue= self.__dict__[uAttributName]
            if isinstance(oValue,string_types):
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


