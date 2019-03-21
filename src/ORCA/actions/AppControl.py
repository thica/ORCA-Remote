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

from kivy.logger            import Logger

from ORCA.actions.Base      import cEventActionBase
from ORCA.EventTimer        import cCustomTimer
from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.LogError    import LogError
from ORCA.utils.TypeConvert import ToFloat
from ORCA.utils.Zip         import cZipFile
from ORCA.utils.Zip         import cZipPath
from ORCA.utils.FileName    import cFileName
from ORCA.utils.Path        import cPath
from ORCA.vars.Access       import SetVar
from ORCA.vars.Dump         import DumpDefinitionVars
from ORCA.vars.Dump         import DumpVars
from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.TypeConvert import ToInt
from ORCA.utils.TypeConvert import ToList
from ORCA.Queue             import DumpQueue


import ORCA.Globals as Globals

__all__ = ['cEventActionsAppControl']

class cEventActionsAppControl(cEventActionBase):
    """ Actions for getting/writings settings """

    def ExecuteActionDump(self,oAction):
        self.doc_end_ = """
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
        uType           = ReplaceVars(oAction.dActionPars.get("type",""))
        uFilter         = ReplaceVars(oAction.dActionPars.get("filter",""))
        uDefinitionName = ReplaceVars(oAction.dActionPars.get("definitionname",""))

        self.oEvenDispatcher.bDoNext = True
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

        return -2

    def ExecuteActionSetReturnCode(self,oAction):
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
        self.oEvenDispatcher.LogAction(u'SetReturnCode',oAction)
        self.oEvenDispatcher.bDoNext = True
        uCode = oAction.dActionPars.get("code","0")
        return ToInt(uCode)

    def ExecuteActionNoAction(self,oAction):
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
        self.oEvenDispatcher.bDoNext = True
        self.oEvenDispatcher.LogAction(u'NoAction',oAction)
        return -2


    def ExecuteActionWaitForConnectivity(self,oAction):
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
        self.oEvenDispatcher.bDoNext = True
        self.oEvenDispatcher.LogAction(u'WaitForConnectivity',oAction)
        if not Globals.oWaitForConnectivity.bIsWaiting:
            Globals.oWaitForConnectivity.Wait()
        return -2

    def ExecuteActionDefineTimer(self,oAction):
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
        |-
        |definetimer
        |Timer Name (Mandantory)
        |Time Interval in seconds
        |on / off : on to enable/set a timer, off to remove the timer
        |Action to execute by the timer
        |}</div>

        If you want to change a timer, ou need to remove the timer and add it with the new settings
        WikiDoc:End
        """

        self.oEvenDispatcher.LogAction(u'DefineTimer',oAction)

        uTimerName     = ReplaceVars(oAction.dActionPars.get("timername",""))
        uInterval      = ReplaceVars(oAction.dActionPars.get("interval",""))
        uSwitch        = ReplaceVars(oAction.dActionPars.get("switch",""))
        uActionName    = ReplaceVars(oAction.dActionPars.get("actionname",""))

        self.oEvenDispatcher.bDoNext = True
        if uSwitch==u'on':
            if not self.oEvenDispatcher.oAllTimer.HasTimer(uTimerName):
                oCustomTimer=cCustomTimer( uTimerName, uActionName,ToFloat(uInterval))
                self.oEvenDispatcher.oAllTimer.AddTimer(uTimerName,oCustomTimer)
                oCustomTimer.StartTimer()
                return 0
            else:
                Logger.warning (u'Action: DefineTimer, timer already exist:',uTimerName)
                return 1

        if uSwitch==u'off':
            if self.oEvenDispatcher.oAllTimer.HasTimer(uTimerName):
                self.oEvenDispatcher.oAllTimer.DeleteTimer(uTimerName)
                return 0
            else:
                Logger.warning (u'Action: DefineTimer, timer does not exist:'+uTimerName)
                return 1

        uMsg=u'Action: DefineTimer, you need to on/off the timer:'+uTimerName
        Logger.warning (uMsg)
        ShowErrorPopUp(uTitle='Warning',uMessage=uMsg)
        return 1

    def ExecuteActionPlaySound(self,oAction):
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
        self.oEvenDispatcher.LogAction(u'PlaySound',oAction)
        uSoundName     = ReplaceVars(oAction.dActionPars.get("soundname",""))
        uVolume        = ReplaceVars(oAction.dActionPars.get("volume","100"))
        self.oEvenDispatcher.bDoNext = True
        Globals.oSound.PlaySound(uSoundName,uVolume)
        return -2

    def ExecuteActionRedirect(self,oAction):
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

        oFrom   = cFileName("").ImportFullPath(oAction.dActionPars.get("from",""))
        oTo     = cFileName("").ImportFullPath(oAction.dActionPars.get("to",""))

        self.oEvenDispatcher.LogAction(u'Redirect',oAction)
        self.oEvenDispatcher.bDoNext = True
        Globals.oTheScreen.oSkin.dSkinRedirects[oFrom.string]=oTo
        return -2

    def ExecuteActionModifyFile(self,oAction):

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ModifyFile
        WikiDoc:TOCTitle:modifyfile
        = modifyfile =
        Provides some common file operations like copy, rename, delete. All Operations can only be performed on files within the definition folder, so all pathes must be relative to the definition root folder. For copyfolder the abspath argument gives you access as a source for folder outside the definition folder
        This action will modify the error code (0=success, 1=failure)

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

        uFileName        = oAction.dActionPars.get("filename","")
        uDestFileName    = oAction.dActionPars.get("dstfilename","")
        uPath            = oAction.dActionPars.get("path","")
        uDestPath        = oAction.dActionPars.get("dstpath","")

        uDestVarName     = oAction.dActionPars.get("dstvarname","")
        uOperator        = ReplaceVars(oAction.dActionPars.get("operator",""))
        uAbsPath         = ReplaceVars(oAction.dActionPars.get("abspath",""))
        uRemovePath      = ReplaceVars(oAction.dActionPars.get("removepath",""))
        aSkipFiles       = ToList(ReplaceVars(oAction.dActionPars.get("skipfiles",'[]')))

        self.oEvenDispatcher.LogAction(u'ModifyFile',oAction)

        if uFileName.startswith('$var(DEFINITIONPATH'):
            oFileName = cFileName().ImportFullPath(uFileName)
        else:
            oFileName = cFileName(Globals.oDefinitionPathes.oPathDefinition)+uFileName

        if uPath.startswith('$var(DEFINITIONPATH'):
            oPath = cPath(uPath)
        else:
            oPath = cPath(Globals.oDefinitionPathes.oPathDefinition)+uPath

        oAbsPath=cPath(uAbsPath)

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
            return 1

        if ".." in oDestFileName.string:
            Logger.warning(u'Action: ModifyFile: Destination File must be inside definition folder:'+oDestFileName.string)
            return 1

        if ".." in oPath.string:
            Logger.warning(u'Action: ModifyFile: Path must be inside definition folder:'+oPath.string)
            return 1

        if ".." in oDestPath.string:
            Logger.warning(u'Action: ModifyFile: Destination Path must be inside definition folder:'+oDestPath.string)
            return 1

        if uOperator==u'copyfile':
            if oFileName.Copy(oDestFileName):
                return 0
            else:
                return 1
        elif uOperator==u'renamefile':
            if oFileName.Rename(oDestFileName):
                return 0
            else:
                return 1
        elif uOperator==u'deletefile':
            if oFileName.Delete():
                return 0
            else:
                return 1
        elif uOperator==u'existfile':
            if oFileName.Exists():
                SetVar(uVarName = uDestVarName, oVarValue = "TRUE")
            else:
                SetVar(uVarName = uDestVarName, oVarValue = "FALSE")
            return -2
        elif uOperator==u'copyfolder':
            if oAbsPath.IsEmpty():
                if oPath.Copy(oDestPath):
                    return 0
                else:
                    return 1
            else:
                if oAbsPath.Copy(oDestPath):
                    return 0
                else:
                    return 1
        elif uOperator==u'renamefolder':
            if oPath.Rename(oDestPath):
                return 0
            else:
                return 1
        elif uOperator==u'deletefolder':
            if oPath.Delete():
                return 0
            else:
                return 1
        elif uOperator==u'createfolder':
            if oPath.Create():
                return 0
            else:
                return 1
        elif uOperator==u'existfolder':
            if oPath.Exists():
                SetVar(uVarName = uDestVarName, oVarValue = "TRUE")
            else:
                SetVar(uVarName = uDestVarName, oVarValue=  "FALSE")
            return 0
        elif uOperator==u'zipfolder':
            oZipFolder    = cZipPath(ReplaceVars(oAction.dActionPars.get("path", "")))
            oDestFileName = cFileName('').ImportFullPath(ReplaceVars(oAction.dActionPars.get("dstfilename", "")))
            if oZipFolder.ZipFolder(oFnZipDest=oDestFileName,uRemovePath=uRemovePath,aSkipFiles=aSkipFiles):
                return 0
            else:
                return 1
        elif uOperator==u'zipfile':
            oZipFile    = cZipFile().ImportFullPath(ReplaceVars(oAction.dActionPars.get("filename", "")))
            oDestFileName = cFileName('').ImportFullPath(ReplaceVars(oAction.dActionPars.get("dstfilename", "")))
            if oZipFile.ZipFile(oZipDest=oDestFileName,uRemovePath=uRemovePath):
                return 0
            else:
                return 1
        else:
            LogError(u'Action: ModifyFile: Wrong modifier:'+uOperator )
            return 1
