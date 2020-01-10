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
from typing                         import Union
from copy                           import copy
from kivy.logger                    import Logger

from ORCA.actions.Base              import cEventActionBase
from ORCA.utils.EventResultParser   import cEventScriptResultParser
from ORCA.utils.LogError            import LogError
from ORCA.utils.TypeConvert         import DictToUnicode
from ORCA.utils.TypeConvert         import ToBool
from ORCA.utils.TypeConvert         import ToDic
from ORCA.utils.TypeConvert         import ToUnicode
from ORCA.vars.Replace              import ReplaceVars
from ORCA.vars.Access               import SetVar
from ORCA.Action                    import cAction
from ORCA.interfaces.BaseInterface  import cBaseInterFace
from ORCA.actions.ReturnCode        import eReturnCode

import ORCA.Globals as Globals

__all__ = ['cEventActionsScriptsAndInterfaces']

class cEventActionsScriptsAndInterfaces(cEventActionBase):
    """ Actions for for Scripts and Interfaces (sendcommand, runscript,...)) """

    def __init__(self, oEventDispatcher):
        # to pass sendcommand actionpars to codeset actionpars
        self.dActionPars:Dict={}
        super(cEventActionsScriptsAndInterfaces, self).__init__(oEventDispatcher)

    def ExecuteActionRegisterScriptGroup(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-RegisterScriptGroup
        WikiDoc:TOCTitle:registerscriptgroup
        = registerscriptgroup =
        Registers a group of scripts.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |registerscriptgroup
        |-
        |groupname
        |Name of the group to register (SYSTEM, TOOLS, KEYHANDLER)
        |-
        |}</div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(u'RegisterScriptGroup:',oAction)
        uGroupName:str = oAction.dActionPars.get("groupname","")
        Globals.oScripts.RegisterScriptGroup(uGroupName)
        return eReturnCode.Nothing

    def ExecuteActionRunScript(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-RunScript
        WikiDoc:TOCTitle:runscript
        = runscript =
        Runs a script. Script results will be parsed by the resultparser.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |runscript
        |-
        |scriptname
        |Name of the script to run (without path)
        |-
        |commandparameter
        |Parameters to pass to the script, format (json): '{"arg":"value",...}'
        |-
        |getvar
        |Variable name to parse form result
        |-
        |gdestvar
        |Variable name to parse form result
        |-
        |ldestvar
        |Local destination var for parsed result
        |-
        |parseoption
        |Option, how to parse the result (eg store, split,tokenize...)
        |-
        |parsetoken
        |tokenize token to use
        |}</div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(u'RunScript:',oAction)

        uScriptName:str             = oAction.dActionPars.get("scriptname","")
        dParameters:Dict            = ToDic(ReplaceVars(oAction.dActionPars.get("commandparameter","{}")))
        Globals.oEvents.CopyActionPars(dTarget=dParameters, dSource=oAction.dActionPars, uReplaceOption="donotreplacetarget", bIgnoreHiddenWords=True)

        if isinstance(dParameters,dict):
            dParameters["oAction"]  = oAction
            dParameters["caller"]   = "action"

            dResponse:Union[Dict,None] = Globals.oScripts.RunScript(uScriptName,**dParameters)
            if dResponse:
                oResultParser = cEventScriptResultParser(oAction)
                oResultParser.ParseResult(ToUnicode(dResponse), ToUnicode(oAction.dActionPars))
        else:
            Logger.warning("Can't run script, parameter error:"+str(dParameters))
        return eReturnCode.Nothing

    def ExecuteActionAddTrigger(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-AddTrigger
        WikiDoc:TOCTitle:addtrigger
        = addtrigger =
        Registers / Deregisters a trigger to an interface. If the interface supports triggers and support the registered trigger, the action assigned to the trigger, will get called. Do not forget to deregister the trigger, if your action will interact with screen elements on a specific page.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |addtrigger
        |-
        |triggername
        |Name of the interfacetrigger to bind
        |-
        |actionname
        |Action to be called, when interfacetrigger happens
        |-
        |retvar
        |Destination variable to return to
        |-
        |getvar
        |Variable to parse: Variable, which get parsed from the trigger result. This could be an codeset code as well. In this case, it needs to start with 'codesetcode:'
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="addtrigger" triggername ="Application.OnVolumeChanged" actionname="trigger_on_kodivolume" getvar="codesetcode:On_Volume_Changed" interface="kodi" configname="main" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        uInterFace:str
        uConfigName:str

        uAction:str  = ReplaceVars(oAction.dActionPars.get("actionname",""))
        uRetVar:str  = ReplaceVars(oAction.dActionPars.get("retvar",""))
        uInterFace, uConfigName = self.oEventDispatcher.GetTargetInterfaceAndConfig(oAction)

        if uAction!=u'' or uRetVar!=u'':
            self.oEventDispatcher.LogAction(u'Add Trigger',oAction,u' Interface:{0} Config:{1}'.format(uInterFace,uConfigName))
        else:
            self.oEventDispatcher.LogAction(u'Del Trigger',oAction,u' Interface:{0} Config:{1}'.format(uInterFace,uConfigName))

        oInterface:cBaseInterFace = Globals.oInterFaces.dInterfaces.get(uInterFace)
        if oInterface:
            if not oInterface.bIsInit:
                oInterface.Init(uInterFace)
            oInterface.AddTrigger(oAction)
            return eReturnCode.Success
        else:
            LogError(uMsg=u'Action: Addtrigger: Interface not found:'+uInterFace)
            return eReturnCode.Error

    def ExecuteActionSendCommand(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-SendCommand
        WikiDoc:TOCTitle:sendcommand
        = sendcommand =
        The core action. This sends a command to an interface. The command parameter are passed to the interface, refer to the interface documentation, which parameters are used.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |sendcommand
        |-
        |commandname
        |Name of the command to send to the interface
        |-
        |commandparameter
        |additional parameter to pass to interface/codeset
        |-
        |interface
        |Interface to use. If not given, it will be used as gven in the following order: widget, anchor, page
        |-
        |configname
        |Configuration to use
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="Send Set Volume Sub" string="sendcommand setvolumesub" commandparameter='{"volumetoset":"$var(volumetoset)"}'/>
        </syntaxhighlight></div>
        WikiDoc:End
        """
        uInterFace:str  = u''
        uConfigName:str = u''

        vCommandParameter:Union[str,Dict] = oAction.dActionPars.get("commandparameter","{}")
        if isinstance(vCommandParameter, str):
            oAction.dCommandParameter  = ToDic(ReplaceVars(vCommandParameter))
        if isinstance(vCommandParameter, dict):
            oAction.dCommandParameter  = ToDic(ReplaceVars(DictToUnicode(vCommandParameter)))

        uCommandName:str               = ReplaceVars(oAction.dActionPars.get("commandname",""))

        try:
            uInterFace, uConfigName = self.oEventDispatcher.GetTargetInterfaceAndConfig(oAction)

            oInterface:cBaseInterFace = Globals.oInterFaces.dInterfaces.get(uInterFace)
            if oInterface:
                if not oInterface.bIsInit:
                    oInterface.Init(uInterFace)
                oTmpAction:cAction = copy(oAction)
                oTmpAction.uActionString=ReplaceVars(oTmpAction.uActionString)
                oTmpAction.dActionPars[u'configname']=uConfigName
                Logger.debug (u'Action: Send Command: [%s] Interface: %s Config: %s' % (uCommandName, uInterFace,uConfigName))
                eRet:eReturnCode = oInterface.DoAction(oTmpAction)
                SetVar(uVarName = u'INTERFACEERRORCODE_'+uInterFace+u'_'+uConfigName, oVarValue = ToUnicode(eRet))
                return eRet
            else:
                if uInterFace!="":
                    SetVar(uVarName = u'INTERFACEERRORCODE_'+uInterFace+u'_'+uConfigName, oVarValue = u'1')
                    LogError(uMsg=u'Action: Send Command failed #1: [%s] Interface: %s Config: %s : Interface not found!' % (uCommandName, uInterFace,uConfigName))
                else:
                    LogError(uMsg=u'Action: Send Command failed #2: [%s]:  No Interface given!' % uCommandName)
                return eReturnCode.Error
        except Exception as e:
            SetVar(uVarName = u'INTERFACEERRORCODE_'+uInterFace+u'_'+uConfigName, oVarValue = u"1")
            LogError(uMsg=u'Action: Send Command failed #2: [%s] Interface: %s Config: %s' % (uCommandName, uInterFace,uConfigName),oException=e)
            return eReturnCode.Error

    # noinspection PyMethodMayBeStatic
    def ExecuteActionDiscover(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-Discover
        WikiDoc:TOCTitle:discover
        = discover =
        Discovers either a device for a configuration / Interface or discovers all. The host name must be "discover" and the device must not have been discovered previously.
        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |discover
        |-
        |interface
        |The name of the interface to discover. Leave empty to discover all
        |-
        |config
        |The name of the config to discover. Only valid if you apply the interface name
        |-
        |gui
        |If set to '1', amessage is shown and the DISCOVERFAILED variable will be set to TRUE or FALSE. In this case the LASTERRORCODE is invalid.
         If gui set to 0, a silent discover is performed and the LASTERRORCoDE is set to '0' if successfull or '1' if failed.

        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action string="discover" />
        </syntaxhighlight></div>
        WikiDoc:End
        """
        uInterFace:str  = ReplaceVars(oAction.dActionPars.get(u'interface',''))
        uConfigName:str = ReplaceVars(oAction.dActionPars.get(u'configname',''))
        bGui:bool        = ToBool(ReplaceVars(oAction.dActionPars.get(u'gui','0')))
        Logger.debug(u'Action: discover: Interface: %s Config: %s' % (uInterFace, uConfigName))
        return Globals.oInterFaces.DiscoverAll(uInterFaceName = uInterFace, uConfigName = uConfigName, bGui = bGui)

    # noinspection PyMethodMayBeStatic
    def ExecuteActionCodeset(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-Codeset
        WikiDoc:TOCTitle:codeset
        = codeset =
        A helper action for interfaces. If an interface supports codesets, then all codeset actions will be executed by this action. The name is mandantory
        Not for public use!
        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |codeset
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action string="codeset" name='left' waitforresponse='0' cmd='Shell' params="input keyevent 21" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        uInterFace:str  = u""
        uConfigName:str = u""

        try:
            uInterFace  = oAction.dActionPars.get(u'interface')
            uConfigName = oAction.dActionPars.get(u'configname')
            oInterface:cBaseInterFace = Globals.oInterFaces.dInterfaces.get(uInterFace)
            if oInterface:
                Logger.debug (u'Action: codeset: [%s] Interface: %s Config: %s' % (oAction.uActionName, uInterFace,uConfigName))
                oSetting = oInterface.GetSettingObjectForConfigName(uConfigName)
                bNoLogOut=ToBool(oAction.dActionPars.get('nologout','0'))

                for uKey in oAction.dActionPars:
                    oSetting.SetContextVar("codesetvar_"+uKey,oAction.dActionPars[uKey])

                eRet:eReturnCode = oInterface.SendCommand(oAction,oSetting,oAction.uRetVar,bNoLogOut)
                SetVar(uVarName  = u'INTERFACEERRORCODE_'+uInterFace+u'_'+uConfigName, oVarValue = ToUnicode(eRet))
                return eRet
        except Exception as e:
            SetVar(uVarName = u'INTERFACEERRORCODE_'+uInterFace+u'_'+uConfigName, oVarValue = u"1")
            LogError(uMsg=u'Action: codeset failed #2: [%s] Interface: %s Config: %s' % (oAction.uActionName, uInterFace,uConfigName),oException=e)
            return eReturnCode.Error
