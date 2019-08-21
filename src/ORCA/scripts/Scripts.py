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

import  imp
from kivy.logger            import Logger

from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.FileName    import cFileName
from ORCA.utils.Path        import cPath
from ORCA.utils.LogError    import LogError
from ORCA.vars.Access       import SetVar

import ORCA.Globals as Globals

__all__ = ['cScriptSettingPlugin', 'cScripts']


class cScriptSettingPlugin(object):
    def __init__(self):
        self.uScriptName   = u""
        self.uSettingName  = u""
        self.uSettingPage  = u""
        self.uSettingTitle = u''
        self.aSettingJson  = []

class cScripts(object):
    """ container for all scripts """
    def __init__(self):
        self.aScriptNameList            = [] # list of all names of all scripts
        self.aScriptNameListWithConfig  = [] # list of all names of all scripts, which have configs
        self.dScriptPathList            = {} # dict of all script pathes of all scripts
        self.dScripts                   = {} # dict of all scripts
        self.dModules                   = {} # dict of all python modules for all scripts
        self.dScriptSettingPlugins      = {} # dict of all settings to pulled into the various setting pages (optional)
    def Init(self):
        """ dummy """
        pass
    def DeInit(self):
        """ deinits all scripts """
        for oScriptName in self.dScripts:
            self.dScripts[oScriptName].DeInit()

    def RegisterScriptInSetting(self,uScriptName,oScriptSettingPlugin):
        """ Registers a plugin for the Orca Settings"""

        self.dScriptSettingPlugins[uScriptName]=oScriptSettingPlugin

    def LoadScriptList(self,oPath=None):
        """ loads a list of all scripts """


        if oPath is None:
            oPath = Globals.oPathScripts

        if oPath == Globals.oPathScripts:
            Logger.debug (u'Scripts: Loading Script List')


        aScriptNameList = oPath.GetFolderList()
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

    def LoadScripts(self):
        """ Loads all scripts """

        for uScriptName in self.aScriptNameList:
            self.LoadScript(uScriptName)

    def LoadScript(self,uScriptName):
        """
        Loads a script (if not already loaded)

        :rtype: module
        :param string uScriptName: Name of the script to load
        :return: The loaded (or cached) scipt
        """

        if uScriptName in self.dScripts:
            return self.dModules.get(uScriptName)

        if uScriptName=="":
            return None

        Logger.info (u'Scripts: Loading Script: '+uScriptName)

        oFnScriptPy     = cFileName(self.dScriptPathList[uScriptName]) + u'script.py'
        oFnScript       = cFileName(oFnScriptPy)

        if not oFnScript.Exists():
            return None

        try:
            oModule = imp.load_source('cScript'+"_"+uScriptName, oFnScript.string)
            self.dModules[uScriptName]=oModule
            oScript = oModule.cScript()
            oScript.Init(uScriptName, oFnScript)
            self.dScripts[uScriptName]=oScript
            if oScript.uIniFileLocation != "none":
                self.aScriptNameListWithConfig.append(uScriptName)
            return oModule
        except Exception as e:
            uMsg=LogError(u'Scripts: Fatal Error Loading Script: '+uScriptName+ u' :',e)
            ShowErrorPopUp(uMessage=uMsg)
            return None

    def OnPause(self):
        """ pauses a script """
        for oScriptName in self.dScripts:
            self.dScripts[oScriptName].OnPause()

    def OnResume(self):
        """ resumes a script """
        for oScriptName in self.dScripts:
            self.dScripts[oScriptName].OnResume()

    def GetScriptListForScriptType(self, uType):
        """ gets a list a scripts for a specific script type """
        aResult=[]
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
                        tElements = uSortOrder.split(":")
                        if len(tElements)==2:
                            uSortOrder  = tElements[0]
                            uScriptName = tElements[1]
                            bFound      = False
                            iIndex2     = -1
                            for iIndex2 in range(len(aScriptList)):
                                if self.dScripts[aScriptList[iIndex2]].uScriptName == uScriptName:
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

    def RunScript(self,uScriptName,*args, **kwargs):
        """ runs a script """
        oScript=self.LoadScript(uScriptName)
        if oScript:
            return self.dScripts[uScriptName].RunScript(*args,**kwargs)
        LogError (u'Script '+uScriptName+u': not found')
        return u''

    def RegisterScriptGroup(self, uName):
        aScripts = self.GetScriptListForScriptType(uName)
        for uScriptName in aScripts:
            self.RunScript(uScriptName,**{"caller":"appstart"})
