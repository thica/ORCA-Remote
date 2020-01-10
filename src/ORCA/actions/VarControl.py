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

from kivy.logger                import Logger
from typing                     import List
from typing                     import Dict
from typing                     import Union

from ORCA.Cookies               import Var_Load
from ORCA.Cookies               import Var_Save
from ORCA.actions.Base          import cEventActionBase
from ORCA.utils.LogError        import LogError
from ORCA.utils.TypeConvert     import ToFloat2
from ORCA.utils.TypeConvert     import ToInt
from ORCA.vars.Access           import DelVar
from ORCA.vars.Access           import GetVar
from ORCA.vars.Access           import SetVar
from ORCA.vars.Access           import ExistVar
from ORCA.vars.Actions          import Var_Concatenate
from ORCA.vars.Actions          import Var_Decrease
from ORCA.vars.Actions          import Var_DelArray
from ORCA.vars.Actions          import Var_Divide
from ORCA.vars.Actions          import Var_Find
from ORCA.vars.Actions          import Var_Format
from ORCA.vars.Actions          import Var_FromVar
from ORCA.vars.Actions          import Var_GetArray
from ORCA.vars.Actions          import Var_Hex2Int
from ORCA.vars.Actions          import Var_HexStringToString
from ORCA.vars.Actions          import Var_Increase
from ORCA.vars.Actions          import Var_Invert
from ORCA.vars.Actions          import Var_Len
from ORCA.vars.Actions          import Var_LoadFile
from ORCA.vars.Actions          import Var_LowerCase
from ORCA.vars.Actions          import Var_Multiply
from ORCA.vars.Actions          import Var_Part
from ORCA.vars.Actions          import Var_Power
from ORCA.vars.Actions          import Var_Round
from ORCA.vars.Actions          import Var_StringToHexString
from ORCA.vars.Actions          import Var_ToVar
from ORCA.vars.Actions          import Var_Trim
from ORCA.vars.Actions          import Var_UpperCase
from ORCA.vars.Helpers          import Find_nth_Character
from ORCA.vars.Links            import DelVarLink
from ORCA.vars.Links            import SetVarLink
from ORCA.vars.Links            import VarHasLinks
from ORCA.vars.Replace          import ReplaceVars
from ORCA.Action                import cAction
from ORCA.definition.Definition import cDefinition
from ORCA.actions.ReturnCode    import eReturnCode

import ORCA.Globals as Globals

__all__ = ['cEventActionsVarControl']

class cEventActionsVarControl(cEventActionBase):
    """ Actions for manipulating vars """

    def ExecuteActionSetVar(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-SetVar
        WikiDoc:TOCTitle:setvar
        = setvar =
        Simple: sets a variable name to a given value. The value can be either a constant or value of another variable

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |setvar
        |-
        |varname
        |Variable name to change its value
        |-
        |varvalue
        |Value to set
        |-
        |varcontext
        |Optinal:Context of the variable. Makes a variable local to the context
        |}</div>

        You can use the short form as well:
        "setvar varname=varvalue"

        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="setvar" varname="POWERSTATUS_kodi" varvalue="OFF" />
        <action name="" string="setvar POWERSTATUS_kodi=OFF" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(u'SetVar',oAction)
        uVarName:str    = ReplaceVars(oAction.dActionPars.get("varname",""))
        uVarValue:str   = ReplaceVars(oAction.dActionPars.get("varvalue",""))
        uVarContext:str = ReplaceVars(oAction.dActionPars.get("varcontext",""))
        SetVar(uVarName = uVarName, oVarValue = uVarValue, uContext = uVarContext)
        self.oEventDispatcher.bDoNext = not VarHasLinks(uVarName=uVarName)
        return eReturnCode.Nothing

    def ExecuteActionSetDefinitionVar(self,oAction:cAction) -> eReturnCode:

        """
        setdefinitionvar:
            sets a definition variable with a value
            Parameter:
            varname:  variable to use
            varvalue: value to set
            definitionname: Name of the definition
        """

        uVarName:str       = ReplaceVars(oAction.dActionPars.get("varname",""))
        uVarValue:str      = ReplaceVars(oAction.dActionPars.get("varvalue",""))
        uDefinitionName:str= ReplaceVars(oAction.dActionPars.get("definitionname",""))
        oDef:cDefinition

        self.oEventDispatcher.LogAction(u'SetDefinitionVar',oAction)
        if uDefinitionName=="":
            oDef=Globals.oDefinitions[0]
        else:
            oDef=Globals.oDefinitions[uDefinitionName]
        if oDef:
            if uVarValue!=u'':
                oDef.oDefinitionVars[uVarName]=uVarValue
            else:
                if uVarName in oDef.oDefinitionVars:
                    del oDef.oDefinitionVars[uVarName]
            return eReturnCode.Nothing
        else:
            LogError(uMsg=u'Action: SetDefinitionVar: Can''t find Definition:'+uDefinitionName )
        return eReturnCode.Error

    def ExecuteActionModifyVar(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ModifyVar
        WikiDoc:TOCTitle:modifyvar
        = modifyvar =
        Modifies an existing variable. This is an inplace modification, so the given variable will be changed: a=fkt(a). If you need something like a=fkt(b), you need to copy the variable using setvar prior using this functions.
        "Increase" and "decrease" works on  numeric variables only. "Invert" works on numeric (0/1) or on string variables (True/False).
        "Lowercase","Uppercase","Trim" works on string variables
        "Concatenate" , "Getpart", "Format" works on all variable types
        "Getlen" and "Find" are the only sub action, that will not modify the var, it will return the result in a different var
        "Load" and "Save" are options to create persistant variables. You can sav a variable value and reload the value at the next application start.
        Some note on "Getpart", which is to extract a part of string from a string. It follows python rules (eg.: string[start:end]) where start or end could be empty
        Fromvar converts a variable name into its variable value

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |modifyvar
        |-
        |varname
        |Variable to use/modify
        |-
        |parameter1
        |First parameter for operator
        |-
        |parameter2
        |Second parameter for operator
        |-
        |Operator
        |Operator for the command. Use one of the following keywords
        * "increase"
        * "decrease"
        * "multiply"
        * "divide"
        * "invert"
        * "lowercase"
        * "uppercase"
        * "trim"
        * "concatenate"
        * "getpart"
        * "format"
        * "getlen"
        * "find"
        * "power"
        * "save"
        * "load"
        * "delete"
        * "round"
        * "fromvar"
        * "hex2int"
        * "hexstringtostring"
        * "stringtohexstring"
        * "loadfile"
        * "tovar"
        * "addtoarray"
        * "removefromarray"
        * "exists"
        |}</div>

        Remarks on some operators

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Operator
        ! align="left" | Parameter1
        ! align="left" | Parameter2
        |-
        |increase
        |The delta value (like a=a+x)
        |Optional: The upper limit
        |-
        |decrease
        |The delta value (like a=a-x)
        |Optional: The lower limit
        |-
        |multiply
        |The Multiplier (like a=a*x)
        |
        |-
        |devide
        |The Devidor (like a=a/x)
        |
        |-
        |power
        |The power (like a=a^x)
        |
        |-
        |concatenate
        |The string / stringvar to add (like a=a+"mystring")
        |
        |-
        |getpart
        |The start position
        |The end position
        |-
        |fromvar (gets the variable content from a variable name given in a variable)
        |The context of the var
        |
        |-
        |delete either deletes a single var or an array if the var name ends with []
        |
        |
        |-
        |tovar (assigns a variable name to a new variable without variable replacement)
        |newvarname: the new var name, where the var name should be assigned to
        |
        |-
        |format
        |The format string, following the python string.format syntax
        e.g.: "(int)FFFF00{0:0>2x}"
        |
        |-
        |round
        |The rounding position (eg 0=round to int)
        |
        |-
        |getlen
        |the destination var for the length
        |
        |-
        |save
        |A prefix for the cookie name
        |
        |-
        |load
        |A prefix for the cookie name
        |The default value, if no save value is available
        |-
        |loadfile
        |The filename, from which the content should be loaded into the var
        |The default value, if no save value is available
        |-
        |addtoarray
        |The var value to be added
        |Boolean, if 1, than only add, if value is not already in array
        |-
        |removefromarray
        |The var value to be removed
        |
        |-
        |exist
        |The var name to return, if the var exists (0/1)
        |
        |}</div>

        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="modifyvar" varname="DIMVALUE" operator="divide" parameter1="6.25"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """


        uVarName:str       = ReplaceVars(oAction.dActionPars.get("varname",""))
        uParameter1:str    = oAction.dActionPars.get("parameter1","")
        uParameter2:str    = oAction.dActionPars.get("parameter2","")
        uOperator:str      = ReplaceVars(oAction.dActionPars.get("operator",""))
        bNoVarDetails:bool = False
        iLevel: int
        aVars: List[str]

        if uOperator==u'increase':
            Var_Increase(uVarName = uVarName,uStep = ReplaceVars(uParameter1), uMax = ReplaceVars(uParameter2))
        elif uOperator==u'decrease':
            Var_Decrease(uVarName = uVarName,uStep = ReplaceVars(uParameter1), uMin = ReplaceVars(uParameter2))
        elif uOperator==u'multiply':
            Var_Multiply(uVarName = uVarName, uFactor = ReplaceVars(uParameter1))
        elif uOperator==u'divide':
            Var_Divide(uVarName = uVarName, uDivisor =  ReplaceVars(uParameter1))
        elif uOperator==u'power':
            Var_Power(uVarName = uVarName, uPower = ReplaceVars(uParameter1))
        elif uOperator==u'invert':
            Var_Invert(uVarName = uVarName)
        elif uOperator==u'delete':
            if uVarName.endswith(u'[]'):
                Var_DelArray(uVarName = uVarName)
            else:
                DelVar(uVarName = uVarName)
        elif uOperator==u'round':
            Var_Round(uVarName = uVarName, uPos = uParameter1)
        elif uOperator==u'lowercase':
            Var_LowerCase(uVarName = uVarName)
        elif uOperator==u'uppercase':
            Var_UpperCase(uVarName = uVarName)
        elif uOperator==u'trim':
            Var_Trim(uVarName = uVarName)
        elif uOperator==u'fromvar':
            uOldVar=GetVar(uVarName = uVarName)
            Var_FromVar(uVarName = uVarName, uContext=ReplaceVars(uParameter1))
            Logger.debug(u'FromVar: '+uVarName+"="+GetVar(uVarName = uVarName)+ u" ["+uOldVar+u"]")
        elif uOperator==u'tovar':
            uVarName       = oAction.dActionPars.get("varname","")
            Var_ToVar(uVarName = uVarName, uNewVarName = uParameter1)
            Logger.debug(u'ToVar: '+uVarName+"="+uParameter1)
        elif uOperator==u'concatenate':
            Var_Concatenate(uVarName = uVarName,uAddVar = ReplaceVars(uParameter1))
        elif uOperator==u'getpart':
            Var_Part(uVarName = uVarName,uStart = uParameter1, uEnd = uParameter2)
        elif uOperator==u'getlen':
            Var_Len(uVarName = uVarName,uDestVar = uParameter1)
        elif uOperator==u'find':
            Var_Find(uVarName = uVarName,uFindVar = uParameter1, uDestVar = uParameter2)
        elif uOperator==u'format':
            Var_Format(uVarName = uVarName,uFormat = uParameter1)
        elif uOperator==u'hex2int':
            Var_Hex2Int(uVarName = uVarName)
        elif uOperator==u'hexstringtostring':
            Var_HexStringToString(uVarName = uVarName)
        elif uOperator == u'stringtohexstring':
            Var_StringToHexString(uVarName = uVarName)
        elif uOperator==u'load':
            Var_Load(uVarName, ReplaceVars(uParameter1),ReplaceVars(uParameter2))
        elif uOperator==u'save':
            Var_Save(uVarName,ReplaceVars(uParameter1))
        elif uOperator==u'addtoarray':
            iLevel = uVarName.count('[')

            aVars = sorted(Var_GetArray(uVarName = uVarName, iLevel = iLevel))
            uValue:str      = ReplaceVars(uParameter1)
            if uParameter2=="1":
                for uTmp in aVars:
                    if GetVar(uVarName = uTmp)==uValue:
                        return eReturnCode.Nothing

            uMax:str = "1"
            if len(aVars):
                uLast = aVars[-1]
                uMax   = uLast[uLast.rfind("[")+1:][:-1]
                if ToFloat2(uMax):
                    uMax=str(ToInt(uMax)+1)
                else:
                    Logger.warning(u'addtoarray:'+uVarName+" Array contains non numeric indices")

            uNewVarName:str=uVarName[:-2]+"["+uMax+"]"
            SetVar(uVarName = uNewVarName, oVarValue = uValue)
            Logger.debug(u'addtoarray:'+uNewVarName+"="+uValue)
        elif uOperator==u'removefromarray':
            iLevel = uVarName.count('[')
            aVars  = sorted(Var_GetArray(uVarName = uVarName,iLevel = iLevel))
            uValue = ReplaceVars(uParameter1)
            for uTmp in aVars:
                if GetVar(uVarName = uTmp)==uValue:
                    DelVar(uVarName = uTmp)

        elif uOperator==u'loadfile':
            Var_LoadFile(uVarName = uVarName,uFileName = ReplaceVars(uParameter1))
            bNoVarDetails = True
        elif uOperator==u'exists':
            if ExistVar(uVarName):
                SetVar(uParameter1,"1")
            else:
                SetVar(uParameter1, "0")
            bNoVarDetails = True
        else:
            LogError(uMsg=u'Action: ModifyVar: Wrong modifier:'+uOperator )
            return eReturnCode.Error
        if bNoVarDetails:
            self.oEventDispatcher.LogAction(u'ModifyVar',oAction)
        else:
            self.oEventDispatcher.LogAction(u'ModifyVar',oAction,"Result:"+GetVar(uVarName = uVarName))

        return eReturnCode.Nothing

    def ExecuteActionAddVarLink(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-AddVarLink
        WikiDoc:TOCTitle:addvarlink
        = addvarlink =
        Defines an action to execute, if a specific variable will be changed

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |addvarlink
        |-
        |varname
        |Name of the variable where the trigger should be added
        |-
        |linktype
        |linktype: type of the trigger
        can be
        * 'widget': adds an "updatewidget" trigger
        * 'call": adds a "call" trigger
        * 'action': adds an action trigger
        |-
        |widgetname
        |Name of the widget to update, if linktype = 'widget'
        |-
        |actionname
        |Name of the function to call, if linktype = 'call'
        |-
        |parameters
        |Action Parameter in the format [{"parameter":"value",......},{....}] , if linktype = 'action'
        |-
        |delete
        |deletes the varlink if set to anything not empty
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="addvarlink" varname="ENDLESSKNOB_direction" linktype="widget" widgetname="Knob Endless Textdirection" />
        <action name="" string="addvarlink" varname="$dvar(definition_alias_mediaplayer_template)_CMD_NUMBERPADBUTTON[11]"  linktype="action" parameters='{"string":"setwidgetattribut","widgetname":"Button Number +@Page_Device_$dvar(definition_alias_mediaplayer_template)","attributename":"action","attributevalue":"$var($dvar(definition_alias_mediaplayer_template)_CMD_NUMBERPADBUTTON[11])"}' />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(u'AddVarLink',oAction)

        uLinkType:str      = oAction.dActionPars.get("linktype","")
        uVarName:str       = ReplaceVars(oAction.dActionPars.get("varname",""))
        uDelete:str        = ReplaceVars(oAction.dActionPars.get("delete",""))

        uCmd:Union[List[Dict],str] = ""
        if uLinkType=='widget':
            uWidgetName:str    = ReplaceVars(oAction.dActionPars.get("widgetname",""))
            #uCmd           = '{"string":"updatewidget","widgetname":"%s"}' % (uWidgetName)
            uCmd:List[Dict] = [{"name":"Check if widget exists on current page (varlink)","string":"getwidgetattribute","widgetname":uWidgetName,"attributename":"exists","retvar":"TMPWIDGETEXISTS"},
                               {"name":"Update If Exists (varlink)"                      ,"string":"updatewidget", "widgetname":uWidgetName,"condition":"$var(TMPWIDGETEXISTS)==1"}
                              ]
        elif uLinkType=='call':
            uActionName:str     = ReplaceVars(oAction.dActionPars.get("actionname",""))
            uCmd:str            = '{"string":"call %s"}' % uActionName
        elif uLinkType=='action':
            uCmd:str            = ReplaceVars(oAction.dActionPars.get("parameters",""))

        if not uCmd:
            return eReturnCode.Error

        if not uDelete:
            SetVarLink(uVarName=uVarName,oActions=uCmd)
        else:
            DelVarLink(uVarName=uVarName,oActions=uCmd)
        return eReturnCode.Nothing

    def ExecuteActionForIn(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ForIn
        WikiDoc:TOCTitle:forin

        = ForIn =
        Loops through an array of custom vars

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |forin
        |-
        |varname
        |Variable name to loop through (without brackets)
        |-
        |level
        |the bracket level to use (from left), 1 = leftmost
        |-
        |actionname
        |multi line action / macro name to call for each var
        |-
        |breakvar
        |Break Var to exit the loop, set to 1 to exit the forin loop
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="loop through vars" string="forin" varname="myarray[]"  level="1" actionname="fkt dosomething"/>
        </syntaxhighlight></div>

        Given, you have the following var array

        myarray[1] = "Apple"
        myarray[2] = "Orange"
        myarray[3] = "Cherry"

        This will create the following pars for the first iteration

        Varname:
        $par(forin_value)    = "Apple"
        $par(forin_var)      = "myarray[1]"
        $par(forin_varcore)  = "myarray"
        $par(forin_index)    = "1"

        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="loop through vars" string="forin" varname="myarray[1]_subelement[]" dstvarname="elementname" level="2" actionname="fkt dosomething"/>
        </syntaxhighlight></div>

        Given, you have the following var array

        myarray[1]_sublement[1] = "Green Apple"
        myarray[1]_sublement[2] = "Red Apple"
        myarray[1]_sublement[3] = "Yellow Apple"
        myarray[2]_sublement[1] = "Green Orange"
        myarray[2]_sublement[2] = "Orange Orange"
        myarray[3]_sublement[1] = "Small Cherry"

        This will create the following subvars for the second iteration. Note, it will iterate only through the Apples, not through the oranges

        Varname:
        $par(forin_value)    = "Red Apple"
        $par(forin_var)      = "myarray[1]_sublement[2]"
        $par(forin_varcore)  = "myarray[1]_sublement"
        $par(forin_index)    = "2"

        WikiDoc:End
        """
        self.oEventDispatcher.LogAction(u'ForIn',oAction)

        uVarName:str    = ReplaceVars(oAction.dActionPars.get("varname",""))
        iLevel:int      = ToInt(oAction.dActionPars.get("level","1"))
        uActionName:str = ReplaceVars(oAction.dActionPars.get("actionname",""))
        uBreakVar:str   = ReplaceVars(oAction.dActionPars.get("breakvar",""))
        aActions:List[cAction] = []

        aVars:List[str] = sorted(Var_GetArray(uVarName = uVarName,iLevel = iLevel))

        SetVar(uVarName = uBreakVar, oVarValue = "0")

        uVar:str
        uVarCore:str
        uVarIndex:str
        iPosStart:int
        iPosEnd:int

        for uVar in aVars:
            uVarCore  = u""
            uVarIndex = u""
            iPosStart = Find_nth_Character(uVar,"[",iLevel)
            iPosEnd   = Find_nth_Character(uVar,"]",iLevel)
            if iPosEnd>iPosStart:
                uVarCore  = uVar[:iPosStart]
                uVarIndex = uVar[iPosStart+1:iPosEnd]

            if uBreakVar == u'':
                self.oEventDispatcher.AddToSimpleActionList(aActions,[{'name':'Call ForIn Action',
                                                                       'string':'call','actionname':uActionName,
                                                                       "forin_value":GetVar(uVarName = uVar),
                                                                       "forin_var":uVar,
                                                                       "forin_varcore":uVarCore,
                                                                       "forin_index":uVarIndex,}])
            else:
                self.oEventDispatcher.AddToSimpleActionList(aActions,[{'name':'Call ForIn Action',
                                                                       'string':'call','actionname':uActionName,
                                                                       "forin_value":GetVar(uVarName = uVar),
                                                                       "forin_var":uVar,
                                                                       "forin_varcore":uVarCore,
                                                                       "forin_index":uVarIndex,
                                                                       "condition":"$var("+uBreakVar+")==0"}])


        self.oEventDispatcher.ExecuteActionsNewQueue(aActions,None)
        return eReturnCode.Nothing
