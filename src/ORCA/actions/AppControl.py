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
from typing                 import List

from kivy.logger            import Logger

from ORCA.Action            import cAction
from ORCA.actions.Base      import cEventActionBase
from ORCA.EventTimer        import cCustomTimer
from ORCA.Queue             import DumpQueue
from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.FileName    import cFileName
from ORCA.utils.LogError    import LogError
from ORCA.utils.Path        import cPath
from ORCA.utils.TypeConvert import ToBool
from ORCA.utils.TypeConvert import ToFloat
from ORCA.utils.TypeConvert import ToInt
from ORCA.utils.TypeConvert import ToList
from ORCA.utils.Zip         import cZipFile
from ORCA.utils.Zip         import cZipPath
from ORCA.vars.Access       import SetVar
from ORCA.vars.Dump         import DumpDefinitionVars
from ORCA.vars.Dump         import DumpVars
from ORCA.vars.Replace      import ReplaceVars
from ORCA.actions.ReturnCode import eReturnCode

import ORCA.Globals as Globals

__all__ = ['cEventActionsAppControl']

class cEventActionsAppControl(cEventActionBase):
    """ Actions for getting/writings settings """

    # noinspection PyMethodMayBeStatic
    def ExecuteActionDump(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-Dump
        WikiDoc:TOCTitle:dump

        = dump =
        Dumps various information to the logfile. Useful for debugging.
        This action will not modify the error code
        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |dump
        |-
        |type
        |type of information to dump. Could be one of the following keywords
        * pages: Dumps all pagenames
        * queue: Dumps the current queue
        * vars: Dumps all vars
        * actions: Dumps all actions
        * definitionvars: Dumps all defitions vars
        |-
        |filter
        |Filter to apply, just showing elements which CONTAIN the filter token (not for type = queue)
        |-
        |definitionname
        |For type= definitionvars: The definitionvars of the definition with the given name will be dumped. If empty, all definition vars from all definitions will be dumped
        |}</div>
        WikiDoc:End
        """
        uType:str           = ReplaceVars(oAction.dActionPars.get("type",""))
        uFilter:str         = ReplaceVars(oAction.dActionPars.get("filter",""))
        uDefinitionName:str = ReplaceVars(oAction.dActionPars.get("definitionname",""))

        if uType=="pages":
            Globals.oTheScreen.DumpPages(uFilter)
        elif uType=="queue":
            DumpQueue()
        elif uType=="vars":
            DumpVars(uFilter = uFilter)
        elif uType=="actions":
            Globals.oActions.Dump(uFilter)
        elif uType=="definitionvars":
            if uDefinitionName:
                oDef=Globals.oDefinitions.get(uDefinitionName)
                if oDef is not None:
                    DumpDefinitionVars(dArray = oDef.oDefinitionVars, uFilter = uFilter)
            else:
                for oDef in Globals.oDefinitions:
                    Logger.debug("Definition Name: %s / %s / %s" %(oDef.uName, oDef.uAlias, oDef.uDefPublicTitle))
                    DumpDefinitionVars(dArray = oDef.oDefinitionVars, uFilter = uFilter)

        return eReturnCode.Nothing

    def ExecuteActionSetReturnCode(self,oAction:cAction) -> int:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-SetReturnCode
        WikiDoc:TOCTitle:setreturncode

        = setreturncode =
        Set a specific return code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        |-
        |setreturncode
        |-
        |code
        |Error code to set
        |}</div>
        WikiDoc:End
        """
        self.oEventDispatcher.LogAction(u'SetReturnCode',oAction)
        uCode:str = oAction.dActionPars.get("code","0")
        return ToInt(uCode)

    def ExecuteActionBlockGui(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-BlockGui
        WikiDoc:TOCTitle:blockgui

        = blockgui =
        Blocks screen elements to react on touches. Helpful to ensure, that actions are finished and not interrupted by users touching screen elements
        This action will not modify the error code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        |-
        |blockgui
        |-
        |status
        |0 or 1: 1=block the gui, 0 = unblock the gui
        |}</div>
        WikiDoc:End
        """
        self.oEventDispatcher.LogAction(u'BlockGui',oAction)
        Globals.oTheScreen.BlockGui(ToBool(ReplaceVars(oAction.dActionPars.get("status", "0"))))
        return eReturnCode.Nothing

    def ExecuteActionResumeApp(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ResumeApp
        WikiDoc:TOCTitle:resumeapp

        = resumeapp =
        This helper function enable to resume the app, in case thhis event is not fired or is missed by the sstem
        This action will not modify the error code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        |-
        |resumeapp
        |}</div>
        WikiDoc:End
        """
        self.oEventDispatcher.LogAction(u'ResumeApp',oAction)
        Globals.oApp.on_resume()
        return eReturnCode.Nothing

    def ExecuteActionNoAction(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-NoAction
        WikiDoc:TOCTitle:noaction

        = noaction =
        Doesn't do anything. Helpful for jump labels. This is the default action, if no actionstring is defined
        This action will not modify the error code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        |-
        |noaction
        |}</div>
        WikiDoc:End
        """
        self.oEventDispatcher.LogAction(u'NoAction',oAction)
        return eReturnCode.Nothing


    def ExecuteActionWaitForConnectivity(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-WaitForConnectivity
        WikiDoc:TOCTitle:waitforconnectivity
        = waitforconnectivity =
        Shows an dialog to wait, until network connectivity  is etablished. This will be called on android as part of the standard actions, on resume
        This action will not modify the error code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        |-
        |waitforconnectivity
        |}</div>
        WikiDoc:End
        """
        self.oEventDispatcher.LogAction(u'WaitForConnectivity',oAction)
        if not Globals.oWaitForConnectivity.bIsWaiting:
            Globals.oWaitForConnectivity.Wait()
        return eReturnCode.Nothing

    def ExecuteActionDefineTimer(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-DefineTimer
        WikiDoc:TOCTitle:definetimer
        = definetimer =
        Sets or removes a timer for actions. With a timer, can can perfom actions in intervals. A predefined timer is a timer to update clock widgets.
        This action will modify the error code (0=success, 1=failure)

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        ! align="left" | timername
        ! align="left" | interval
        ! align="left" | switch
        ! align="left" | actionname
        ! align="left" | doonpause
        |-
        |definetimer
        |Timer Name (Mandantory)
        |Time Interval in seconds
        |on / off : on to enable/set a timer, off to remove the timer
        |Action to execute by the timer
        |Execute the timer, even if the device is on sleep
        |}</div>

        If you want to change a timer, ou need to remove the timer and add it with the new settings
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(u'DefineTimer',oAction)

        uTimerName:str     = ReplaceVars(oAction.dActionPars.get("timername",""))
        uInterval:str      = ReplaceVars(oAction.dActionPars.get("interval",""))
        uSwitch:str        = ReplaceVars(oAction.dActionPars.get("switch",""))
        uActionName:str    = ReplaceVars(oAction.dActionPars.get("actionname",""))
        bDoOnPause:bool    = ToBool(ReplaceVars(oAction.dActionPars.get("doonpause","0")))

        if uSwitch==u'on':
            if not self.oEventDispatcher.oAllTimer.HasTimer(uTimerName):
                oCustomTimer:cCustomTimer = cCustomTimer(uTimerName=uTimerName,uActionName=uActionName,fTimerIntervall=ToFloat(uInterval),bDoOnPause=bDoOnPause)
                self.oEventDispatcher.oAllTimer.AddTimer(uTimerName,oCustomTimer)
                oCustomTimer.StartTimer()
                return eReturnCode.Success
            else:
                Logger.warning (u'Action: DefineTimer, timer already exist:'+uTimerName)
                return eReturnCode.Error

        if uSwitch==u'off':
            if self.oEventDispatcher.oAllTimer.HasTimer(uTimerName):
                self.oEventDispatcher.oAllTimer.DeleteTimer(uTimerName)
                return eReturnCode.Success
            else:
                Logger.warning (u'Action: DefineTimer, timer does not exist:'+uTimerName)
                return eReturnCode.Error

        uMsg:str = u'Action: DefineTimer, you need to on/off the timer:'+uTimerName
        Logger.warning (uMsg)
        ShowErrorPopUp(uTitle='Warning',uMessage=uMsg)
        return eReturnCode.Error

    def ExecuteActionPlaySound(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-PlaySound
        WikiDoc:TOCTitle:playsound
        = playsound =
        Plays a given system sound
        This action will not modify the error code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        ! align="left" | soundname
        ! align="left" | volume
        |-
        |playsound
        |sound name (defined by the sound-repository), could be a sound file as well
        |Sound volume. This is the relative sound to the user defined sound volume (0 to 100).
        |}</div>

        The following standards sounds should be available

        * startup
        * shutdown
        * error
        * message
        * question
        * notification
        * ring
        * success
        * click
        WikiDoc:End
        """
        self.oEventDispatcher.LogAction(u'PlaySound',oAction)
        uSoundName:str     = ReplaceVars(oAction.dActionPars.get("soundname",""))
        uVolume:str        = ReplaceVars(oAction.dActionPars.get("volume","100"))
        Globals.oSound.PlaySound(uSoundName,uVolume)
        return eReturnCode.Nothing

    def ExecuteActionRedirect(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-Redirect
        WikiDoc:TOCTitle: redirect
        = redirect =
        Redirects a xml file to load to a new xml file. Purpose of this action is, to replace elements (standard / Skin / definition) by a customized element
        This action will not modify the error code

        <div style="overflow:auto; ">
        {| border=1 class="wikitable"
        ! align="left" | string
        ! align="left" | from
        ! align="left" | to
        |-
        |redirect
        |Full path and filename to the xml file which should be replaced
        |Full path and filename to the replacement file
        |}</div>
        WikiDoc:End
        """

        oFrom:cFileName   = cFileName("").ImportFullPath(oAction.dActionPars.get("from",""))
        oTo:cFileName     = cFileName("").ImportFullPath(oAction.dActionPars.get("to",""))

        self.oEventDispatcher.LogAction(u'Redirect',oAction)
        Globals.oTheScreen.oSkin.dSkinRedirects[oFrom.string]=oTo
        return eReturnCode.Nothing

    def ExecuteActionModifyFile(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ModifyFile
        WikiDoc:TOCTitle:modifyfile
        = modifyfile =
        Provides some common file operations like copy, rename, delete. All Operations can only be performed on files within the definition folder, so all pathes must be relative to the definition root folder. For copyfolder the abspath argument gives you access as a source for folder outside the definition folder
        This action will modify the error code (0=success, 1=failure), existfile will not modify the error coee

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |modifyfile
        |-
        |filename
        |Relative path to file name
        |-
        |path
        |Relative path
        |-
        |abspath
        |Absolute path to source folder (copyfolder only)
        |-
        |dstfilename
        |For copy,rename and zip... the destination file name
        |-
        |dstpath
        |For copy,rename... the destination path name
        |-
        |dstvarname
        |for exist the destination var for the result
        |-
        |removepath
        |for zip: the path to remove from the zip directory
        |-
        |skipfiles
        |for zipfolder: filenames to exclude from the zip file (list)
        |-
        |Operator
        |Operator for the command. Use one of the following keywords
        * "copyfile"
        * "copyfolder"
        * "renamefile"
        * "renamefolder"
        * "deletefile"
        * "createfolder"
        * "deletefolder"
        * "existfile"
        * "existfolder"
        * "zipfile"
        * "zipfolder"

        |}</div>

        exist returns "TRUE" or "FALSE"

        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="modifyfile" filename="definition.ini" operator="copy" dstfilename="definition.old"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """

        uFileName:str        = oAction.dActionPars.get("filename","")
        uDestFileName:str    = oAction.dActionPars.get("dstfilename","")
        uPath:str            = oAction.dActionPars.get("path","")
        uDestPath:str        = oAction.dActionPars.get("dstpath","")

        uDestVarName:str     = oAction.dActionPars.get("dstvarname","")
        uOperator:str        = ReplaceVars(oAction.dActionPars.get("operator",""))
        uAbsPath:str         = ReplaceVars(oAction.dActionPars.get("abspath",""))
        uRemovePath:str      = ReplaceVars(oAction.dActionPars.get("removepath",""))
        aSkipFiles:List      = ToList(ReplaceVars(oAction.dActionPars.get("skipfiles",'[]')))
        aSkipFiles.append("*.ini")
        aSkipFiles.append("*.pyc")

        self.oEventDispatcher.LogAction(u'ModifyFile',oAction)

        if uFileName.startswith('$var(DEFINITIONPATH'):
            oFileName = cFileName().ImportFullPath(uFileName)
        else:
            oFileName = cFileName(Globals.oDefinitionPathes.oPathDefinition)+uFileName

        if uPath.startswith('$var(DEFINITIONPATH'):
            oPath:cPath = cPath(uPath)
        else:
            oPath:cPath = cPath(Globals.oDefinitionPathes.oPathDefinition)+uPath

        oAbsPath:cPath = cPath(uAbsPath)

        if uDestFileName.startswith('$var(DEFINITIONPATH'):
            oDestFileName = cFileName().ImportFullPath(uDestFileName)
        else:
            oDestFileName = cFileName(Globals.oDefinitionPathes.oPathDefinition) + uDestFileName

        if uDestPath.startswith('$var(DEFINITIONPATH'):
            oDestPath = cPath(uDestPath)
        else:
            oDestPath = cPath(Globals.oDefinitionPathes.oPathDefinition) + uDestPath

        if ".." in oFileName.string:
            Logger.warning(u'Action: ModifyFile: File must be inside definition folder:'+oFileName.string)
            return eReturnCode.Error

        if ".." in oDestFileName.string:
            Logger.warning(u'Action: ModifyFile: Destination File must be inside definition folder:'+oDestFileName.string)
            return eReturnCode.Error

        if ".." in oPath.string:
            Logger.warning(u'Action: ModifyFile: Path must be inside definition folder:'+oPath.string)
            return eReturnCode.Error

        if ".." in oDestPath.string:
            Logger.warning(u'Action: ModifyFile: Destination Path must be inside definition folder:'+oDestPath.string)
            return eReturnCode.Error

        if uOperator==u'copyfile':
            if oFileName.Copy(oDestFileName):
                return eReturnCode.Success
            else:
                return eReturnCode.Error
        elif uOperator==u'renamefile':
            if oFileName.Rename(oDestFileName):
                return eReturnCode.Success
            else:
                return eReturnCode.Error
        elif uOperator==u'deletefile':
            if oFileName.Delete():
                return eReturnCode.Success
            else:
                return eReturnCode.Error
        elif uOperator==u'existfile':
            if oFileName.Exists():
                SetVar(uVarName = uDestVarName, oVarValue = "TRUE")
            else:
                SetVar(uVarName = uDestVarName, oVarValue = "FALSE")
            return eReturnCode.Nothing
        elif uOperator==u'copyfolder':
            if oAbsPath.IsEmpty():
                if oPath.Copy(oDestPath):
                    return eReturnCode.Success
                else:
                    return eReturnCode.Error
            else:
                if oAbsPath.Copy(oDestPath):
                    return eReturnCode.Success
                else:
                    return eReturnCode.Error
        elif uOperator==u'renamefolder':
            if oPath.Rename(oDestPath):
                return eReturnCode.Success
            else:
                return eReturnCode.Error
        elif uOperator==u'deletefolder':
            if oPath.Delete():
                return eReturnCode.Success
            else:
                return eReturnCode.Error
        elif uOperator==u'createfolder':
            if oPath.Create():
                return eReturnCode.Success
            else:
                return eReturnCode.Error
        elif uOperator==u'existfolder':
            if oPath.Exists():
                SetVar(uVarName = uDestVarName, oVarValue = "TRUE")
            else:
                SetVar(uVarName = uDestVarName, oVarValue=  "FALSE")
            return eReturnCode.Success
        elif uOperator==u'zipfolder':
            oZipFolder:cZipPath     = cZipPath(ReplaceVars(oAction.dActionPars.get("path", "")))
            oDestFileName:cFileName = cFileName('').ImportFullPath(ReplaceVars(oAction.dActionPars.get("dstfilename", "")))
            if oZipFolder.ZipFolder(oFnZipDest=oDestFileName,uRemovePath=uRemovePath,aSkipFiles=aSkipFiles):
                return eReturnCode.Success
            else:
                return eReturnCode.Error
        elif uOperator==u'zipfile':
            oZipFile:cZipFile       = cZipFile().ImportFullPath(ReplaceVars(oAction.dActionPars.get("filename", "")))
            oDestFileName:cFileName = cFileName('').ImportFullPath(ReplaceVars(oAction.dActionPars.get("dstfilename", "")))
            if oZipFile.ZipFile(oZipDest=oDestFileName,uRemovePath=uRemovePath):
                return eReturnCode.Success
            else:
                return eReturnCode.Error
        else:
            LogError(uMsg=u'Action: ModifyFile: Wrong modifier:'+uOperator )
            return eReturnCode.Error
