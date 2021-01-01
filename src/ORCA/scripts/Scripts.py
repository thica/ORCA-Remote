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

from typing                     import List
from typing                     import Dict
from typing                     import Union
from typing                     import Optional
from typing                     import cast
from dataclasses                import dataclass
from dataclasses                import field
from kivy.logger                import Logger
from ORCA.ui.ShowErrorPopUp     import ShowErrorPopUp
from ORCA.utils.FileName        import cFileName
from ORCA.utils.Path            import cPath
from ORCA.utils.LogError        import LogError
from ORCA.vars.Access           import SetVar
from ORCA.scripts.BaseScript    import cBaseScript
from ORCA.BaseObject            import cBaseObjects

import ORCA.Globals as Globals

__all__ = ['cScriptSettingPlugin', 'cScripts']

@dataclass
class cScriptSettingPlugin:
     uScriptName:str    = u""
     uSettingName:str   = u""
     uSettingPage:str   = u""
     uSettingTitle:str  = u""
     aSettingJson:List  = field(default_factory=list)

class cScripts(cBaseObjects):
    """ container for all scripts """
    def __init__(self):
        cBaseObjects.__init__(self,uType="SCRIPTS",uPrefix="SCRIPTS")
        self.aObjectNameListWithConfig:List[str]                    = [] # list of all names of all scripts, which have configs
        self.dScriptPathList:Dict[str,cPath]                        = {} # dict of all script paths of all scripts
        self.dScriptSettingPlugins:Dict[str,cScriptSettingPlugin]   = {} # dict of all settings to pulled into the various setting pages (optional)

    def RegisterScriptInSetting(self,uScriptName:str,oScriptSettingPlugin:cScriptSettingPlugin) -> None:
        """ Registers a plugin for the Orca Settings"""
        self.dScriptSettingPlugins[uScriptName]=oScriptSettingPlugin

    def LoadScriptList(self,*,oPath:Optional[cPath]=None)->None:
        """ loads a list of all scripts """

        aObjectNameList:List[str]
        oFolderPath:cPath
        oPathScriptSkinElements:cPath
        oRealPath:cPath
        uScriptName:str
        uScriptNameFolder:str

        if oPath is None:
            oRealPath = Globals.oPathScripts
        else:
            oRealPath = cast(cPath,oPath)

        if oRealPath == Globals.oPathScripts:
            Logger.debug (u'Scripts: Loading Script List')

        aObjectNameList = oRealPath.GetFolderList()
        for uScriptNameFolder in aObjectNameList:
            oFolderPath=cPath(oRealPath)+uScriptNameFolder
            if (cFileName(oFolderPath)+"script.py").Exists():
                self.aObjectNameList.append(uScriptNameFolder)
                self.dScriptPathList[uScriptNameFolder]=oFolderPath
            else:
                self.LoadScriptList(oPath=oFolderPath)

        if oRealPath == Globals.oPathScripts:
            self.aObjectNameList.sort(key = lambda x: x)
            for uScriptName in self.aObjectNameList:
                SetVar(uVarName="SCRIPTPATH[%s]" % uScriptName,oVarValue=self.dScriptPathList[uScriptName].string)
                oPathScriptSkinElements = self.dScriptPathList[uScriptName]+"elements"
                oPathCheck              = oPathScriptSkinElements + ("skin_" + Globals.uSkinName)
                if oPathCheck.Exists():
                    oPathScriptSkinElements = oPathCheck
                else:
                    oPathScriptSkinElements = oPathScriptSkinElements + "skin_default"
                SetVar(uVarName="SCRIPTPATHSKINELEMENTS[%s]" % uScriptName, oVarValue=oPathScriptSkinElements.string)

    def LoadScripts(self) -> None:
        """ Loads all scripts """

        uScriptName:str

        for uScriptName in self.aObjectNameList:
            self.LoadScript(uScriptName=uScriptName)

    def LoadScript(self,uScriptName:str) ->Optional[cBaseScript]:
        """
        Loads a script (if not already loaded)

        :rtype: module
        :param str uScriptName: Name of the script to load
        :return: The loaded (or cached) script
        """

        if uScriptName in self.dObjects:
            return self.dModules.get(uScriptName)

        if uScriptName=="":
            return None

        Logger.info (u'Scripts: Loading Script: '+uScriptName)

        oFnScriptPy:cFileName     = cFileName(self.dScriptPathList[uScriptName]) + u'script.py'
        oFnScript:cFileName       = cFileName(oFnScriptPy)

        if not oFnScript.Exists():
            return None

        try:
            oModule                     = Globals.oModuleLoader.LoadModule(oFnModule=oFnScript,uModuleName='cScript'+"_"+uScriptName)
            self.dModules[uScriptName]  = oModule
            oScript:cBaseScript         = oModule.GetClass('cScript')()
            oScript.Init(uScriptName, oFnScript)
            self.dObjects[uScriptName]  = oScript
            if oScript.uIniFileLocation != "none":
                self.aObjectNameListWithConfig.append(uScriptName)
            return oModule
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'Scripts: Fatal Error Loading Script: '+uScriptName+ u' :',oException=e))
            return None

    def GetScript(self,uScriptName:str) -> cBaseScript:
        """
        Returns an cBaseScript class

        :param str uScriptName: The name of the Script
        :return: The script class (cBaseScript)
        """
        return self.dObjects.get(uScriptName)

    def GetScriptListForScriptType(self, uType:str) -> List[str]:
        """ gets a list a scripts for a specific script type """
        uScriptName:str
        aResult:List[str]=[]
        #Load all Scripts
        for uScriptName in self.aObjectNameList:
            self.LoadScript(uScriptName)

        for uScriptName in self.aObjectNameList:
            if uScriptName in self.dObjects:
                if self.dObjects[uScriptName].uType==uType:
                    aResult.append(uScriptName)
        self._SortScripts(aResult)
        return aResult

    def _SortScripts(self,aScriptList:List[str]):
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
                    uSortOrder = self.dObjects[aScriptList[iIndex]].uSortOrder
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
                                if self.dObjects[aScriptList[iIndex2]].uObjectName == uScriptName:
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
            return self.GetScript(uScriptName).RunScript(*args,**kwargs)
        LogError (uMsg=u'Script '+uScriptName+u': not found')
        return {}

    def RegisterScriptGroup(self,*,uName:str)-> None:
        uScriptName:str
        aScripts:List[str] = self.GetScriptListForScriptType(uName)
        for uScriptName in aScripts:
            self.RunScript(uScriptName,**{"caller":"appstart"})
        return None
