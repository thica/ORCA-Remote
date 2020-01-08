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

from typing import List
from typing import Dict
from typing import Union
from typing import Any

from kivy.logger                import Logger
from ORCA.ui.ShowErrorPopUp     import ShowErrorPopUp
from ORCA.utils.FileName        import cFileName
from ORCA.utils.Path            import cPath
from ORCA.utils.LogError        import LogError
from ORCA.vars.Access           import SetVar
from ORCA.scripts.BaseScript    import cBaseScript

import ORCA.Globals as Globals

__all__ = ['cScriptSettingPlugin', 'cScripts']


class cScriptSettingPlugin:
    def __init__(self):
        self.uScriptName:str    = u""
        self.uSettingName:str   = u""
        self.uSettingPage:str   = u""
        self.uSettingTitle:str  = u''
        self.aSettingJson:List = []

class cScripts:
    """ container for all scripts """
    def __init__(self):
        self.aScriptNameList:List[str]                              = [] # list of all names of all scripts
        self.aScriptNameListWithConfig:List[str]                    = [] # list of all names of all scripts, which have configs
        self.dScriptPathList:Dict[str:cFileName]                    = {} # dict of all script pathes of all scripts
        self.dScripts:Dict[str,cBaseScript]                         = {} # dict of all scripts
        self.dModules:Dict[str,Any]                                 = {} # dict of all python modules for all scripts
        self.dScriptSettingPlugins:Dict[str,cScriptSettingPlugin]   = {} # dict of all settings to pulled into the various setting pages (optional)
    def Init(self) -> None:
        """ dummy """
        pass
    def DeInit(self) -> None:
        """ deinits all scripts """
        for oScriptName in self.dScripts:
            self.dScripts[oScriptName].DeInit()

    def RegisterScriptInSetting(self,uScriptName:str,oScriptSettingPlugin:cScriptSettingPlugin) -> None:
        """ Registers a plugin for the Orca Settings"""

        self.dScriptSettingPlugins[uScriptName]=oScriptSettingPlugin

    def LoadScriptList(self,oPath:cPath=None) -> None:
        """ loads a list of all scripts """

        uScriptNameFolder:str
        uScriptName:str
        oFolderPath:cPath
        oPathScriptSkinElements:cPath

        if oPath is None:
            oPath = Globals.oPathScripts

        if oPath == Globals.oPathScripts:
            Logger.debug (u'Scripts: Loading Script List')

        aScriptNameList:List[str] = oPath.GetFolderList()
        for uScriptNameFolder in aScriptNameList:
            oFolderPath=cPath(oPath)+uScriptNameFolder
            if (cFileName(oFolderPath)+"script.py").Exists():
                self.aScriptNameList.append(uScriptNameFolder)
                self.dScriptPathList[uScriptNameFolder]=oFolderPath
            else:
                self.LoadScriptList(oPath=oFolderPath)

        if oPath == Globals.oPathScripts:
            self.aScriptNameList.sort(key = lambda x: x)

            for uScriptName in self.aScriptNameList:
                SetVar(uVarName="SCRIPTPATH[%s]" % uScriptName,oVarValue=self.dScriptPathList[uScriptName].string)
                oPathScriptSkinElements = self.dScriptPathList[uScriptName]+"elements"
                oPathCheck = oPathScriptSkinElements + ("skin_" + Globals.uSkinName)
                if oPathCheck.Exists():
                    oPathScriptSkinElements = oPathCheck
                else:
                    oPathScriptSkinElements = oPathScriptSkinElements + "skin_default"

                SetVar(uVarName="SCRIPTPATHSKINELEMENTS[%s]" % uScriptName, oVarValue=oPathScriptSkinElements.string)

    def LoadScripts(self) -> None:
        """ Loads all scripts """

        uScriptName:str

        for uScriptName in self.aScriptNameList:
            self.LoadScript(uScriptName)

    def LoadScript(self,uScriptName:str):
        """
        Loads a script (if not already loaded)

        :rtype: module
        :param str uScriptName: Name of the script to load
        :return: The loaded (or cached) script
        """

        if uScriptName in self.dScripts:
            return self.dModules.get(uScriptName)

        if uScriptName=="":
            return None

        Logger.info (u'Scripts: Loading Script: '+uScriptName)

        oFnScriptPy:cFileName     = cFileName(self.dScriptPathList[uScriptName]) + u'script.py'
        oFnScript:cFileName       = cFileName(oFnScriptPy)

        if not oFnScript.Exists():
            return None

        try:
            oModule=Globals.oModuleLoader.LoadModule(oFnScript,'cScript'+"_"+uScriptName)
            self.dModules[uScriptName] = oModule
            oScript:cBaseScript = oModule.GetClass('cScript')()
            oScript.Init(uScriptName, oFnScript)
            self.dScripts[uScriptName] = oScript
            if oScript.uIniFileLocation != "none":
                self.aScriptNameListWithConfig.append(uScriptName)
            return oModule
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'Scripts: Fatal Error Loading Script: '+uScriptName+ u' :',oException=e))
            return None

    def OnPause(self) -> None:
        """ pauses a script """
        for oScriptName in self.dScripts:
            self.dScripts[oScriptName].OnPause()

    def OnResume(self) -> None:
        """ resumes a script """
        uScriptName:str
        for uScriptName in self.dScripts:
            self.dScripts[uScriptName].OnResume()

    def GetScriptListForScriptType(self, uType:str) -> List[str]:
        """ gets a list a scripts for a specific script type """
        uScriptName:str
        aResult:List[str]=[]
        #Load all Scripts
        for uScriptName in self.aScriptNameList:
            self.LoadScript(uScriptName)

        for uScriptName in self.aScriptNameList:
            if uScriptName in self.dScripts:
                if self.dScripts[uScriptName].uType==uType:
                    aResult.append(uScriptName)
        self._SortScripts(aResult)
        return aResult

    def _SortScripts(self,aScriptList):
        """ Sorts the Scriptlist """
        u:int
        iIndex:int
        iIndex2:int
        uSortOrder:str
        tElements:List[str]
        bFound:bool
        uSortOrder:str
        uScriptName:str

        if len(aScriptList)>1:
            for u in range(3): #do it three times
                for iIndex in range(len(aScriptList)):
                    uSortOrder = self.dScripts[aScriptList[iIndex]].uSortOrder
                    if uSortOrder == "first":
                        aScriptList[0],aScriptList[iIndex] = aScriptList[iIndex],aScriptList[0]
                    elif uSortOrder == "last":
                        aScriptList[-1], aScriptList[iIndex] = aScriptList[iIndex], aScriptList[-1]
                    elif uSortOrder == "auto":
                        pass
                    else:
                        aElements = uSortOrder.split(":")
                        if len(aElements)==2:
                            uSortOrder  = aElements[0]
                            uScriptName = aElements[1]
                            bFound      = False
                            iIndex2     = -1
                            for iIndex2 in range(len(aScriptList)):
                                if self.dScripts[aScriptList[iIndex2]].uObjectName == uScriptName:
                                    bFound = True
                                    break
                            if bFound:
                                if uSortOrder == "before":
                                    if iIndex2 > 0:
                                        aScriptList[iIndex2-1], aScriptList[iIndex] = aScriptList[iIndex], aScriptList[iIndex2-1]
                                    else:
                                        aScriptList[0], aScriptList[1] = aScriptList[1], aScriptList[0]
                                        aScriptList[0], aScriptList[iIndex] = aScriptList[iIndex], aScriptList[0]
                                if uSortOrder == "after":
                                    if iIndex2 < len(aScriptList):
                                        aScriptList[iIndex2+1], aScriptList[iIndex] = aScriptList[iIndex], aScriptList[iIndex2+1]
                                    else:
                                        aScriptList[-1], aScriptList[-2] = aScriptList[-2], aScriptList[-1]
                                        aScriptList[-1], aScriptList[iIndex] = aScriptList[iIndex], aScriptList[-1]

    def RunScript(self,uScriptName:str,*args, **kwargs) -> Union[Dict,None]:
        """ runs a script """
        oScript:cBaseScript = self.LoadScript(uScriptName)
        if oScript:
            return self.dScripts[uScriptName].RunScript(*args,**kwargs)
        LogError (uMsg=u'Script '+uScriptName+u': not found')
        return {}

    def RegisterScriptGroup(self, uName:str):
        uScriptName:str
        aScripts:List[str] = self.GetScriptListForScriptType(uName)
        for uScriptName in aScripts:
            self.RunScript(uScriptName,**{"caller":"appstart"})
