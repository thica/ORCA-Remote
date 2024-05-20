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
from typing     import Dict
from enum       import Enum
from enum       import auto


__all__ = ['cActionType','eReplaceOption']


class cActionType:
    """ Representation of an action type object
        The types will be created at runtime, the list below is just for the linter
    """
    Call:int
    EndIf:int
    Goto:int
    If:int
    StopApp:int
    Wait:int
    CheckOnSleep:int
    CheckPermissions:int
    CheckToRotate:int
    CreatePages:int
    DownLoadDefinition:int
    ExecuteFTPCommand:int
    GetUsedDefinitions:int
    InitInterfaceSettings:int
    LoadDefinition:int
    LoadDefinitionActions:int
    LoadDefinitionFonts:int
    LoadDefinitionGestures:int
    LoadDefinitionLanguages:int
    LoadDefinitionParameter:int
    LoadDefinitionSettings:int
    LoadLanguages:int
    LoadRepositoryContent:int
    LoadResource:int
    LoadSkin:int
    LoadSounds:int
    ParseDefinitionXML:int
    RegisterFonts:int
    RegisterInterfaces:int
    RepositoryUpdate:int
    RestartAfterDefinitionDownload:int
    RestartAfterRepositoryUpdate:int
    ResumeInterfaces:int
    ResumeOnSleep:int
    ResumeScripts:int
    ShowSplashText:int
    SleepInterfaces:int
    SleepScripts:int
    SetPageEffect:int
    ShowPage:int
    AddVarLink:int
    ForIn:int
    ModifyVar:int
    SetDefinitionVar:int
    SetVar:int
    AddGesture:int
    GetWidgetAttribute:int
    LoadElement:int
    SetWidgetAttribute:int
    UpdateWidget:int
    ShowInputField:int
    ShowProgressBar:int
    ShowQuestion:int
    DisableTransmitterPicture:int
    DisableWaitPicture:int
    EnableTransmitterPicture:int
    EnableWaitPicture:int
    SetTransmitterPicture:int
    SetWaitPicture:int
    AddTrigger:int
    Codeset:int
    Discover:int
    RegisterScriptGroup:int
    RunScript:int
    SendCommand:int
    GetInterfaceSetting:int
    GetSaveOrcaSetting:int
    RemoveDefinitionSetting:int
    SaveInterfaceSetting:int
    DefineTimer:int
    Dump:int
    ModifyFile:int
    NoAction:int
    PlaySound:int
    Redirect:int
    SetReturnCode:int
    WaitForConnectivity:int
    RegisterNotification:int
    RegisterNotification_sub:int
    SendNotification:int

    def __init__(self)->None:
        self.iValue:int                 = 0
        self.dActionToId:Dict[str,int]  = {}

    def RegisterAction(self,*,uActionName:str) -> None:
        """
        Registers an Action
        :param str uActionName: The name of the Action
        :return: None
        """
        setattr(self, uActionName, self.iValue)
        self.dActionToId[uActionName.lower()] = self.iValue
        self.iValue+=1

class eReplaceOption(Enum):
    """
    Helper Class to abstract action copy options
    """

    eDoNotReplaceTarget = auto()
    eDoNotCopyEmpty     = auto()
    eAppendToExisting   = auto()
    eRenameExisting     = auto()
    eRenameMeIfExist    = auto()
    eError              = auto()

    def __str__(self):
        return str(self.value)

    @classmethod
    def FromString(cls,*,uReplaceOption:str) -> eReplaceOption:
        """
        Converts a Replaceeoption string into a Replaceoption enum
        :param uReplaceOption: string, which represents an action replaceoption
        :return: A eReplaceOption enum
        """

        match uReplaceOption:
            case 'donotreplacetarget':  return cls.eDoNotReplaceTarget
            case 'donotcopyempty':      return cls.eDoNotCopyEmpty
            case 'appendtoexisting':    return cls.eAppendToExisting
            case 'renameexisting':      return cls.eRenameExisting
            case 'renamemeifexist':     return cls.eRenameMeIfExist
            case _:                     return cls.eError



