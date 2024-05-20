# -*- coding: utf-8 -*-
#

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

from typing                                 import Dict
from typing                                 import List
from typing                                 import Union

from ORCA.scripts.Scripts                   import cScriptSettingPlugin
from ORCA.scripttemplates.Template_Tools    import cToolsTemplate
from ORCA.scripts.BaseScript                import cBaseScript
from ORCA.utils.Path                        import cPath
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.Tar                         import cTarFile
from ORCA.utils.Platform                    import OS_GetSystemTmpPath
from ORCA.utils.Platform                    import OS_GetSystemUserPath
from ORCA.ui.ShowErrorPopUp                 import ShowErrorPopUp
from ORCA.Globals import Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>Create TV Logos Script (internal)</name>
      <description language='English'>Helper script to create TV Logos (internal)</description>
      <description language='German'>Hilfs - Skript zum Erstellen der TV Logos (internal)</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <skip>1</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/tools/tool_createtvlogos</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/tool_createtvlogos.zip</sourcefile>
          <targetpath>scripts/tools</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cScript(cToolsTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-CreateTvLogos
    WikiDoc:TOCTitle:Helper Script to create TV logos
    = Create TV Scripts =

    This is an internal helper script to create the TV Logos

    WikiDoc:End
    """

    def __init__(self):
        super().__init__()
        self.uSubType               = 'TVLOGOS'
        self.uSortOrder             = 'auto'
        self.uSettingSection        = 'tools'
        self.uSettingTitle          = 'Create TV Logos'
        self.uIniFileLocation:str   = 'none'

        self.dServices:Dict         = {}
        self.dLogos:Dict            = {}

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """
        super().Init(uObjectName= uObjectName, oFnObject=oFnScript)

    def RunScript(self, *args:List, **kwargs:Dict) -> Union[Dict,None]:
        """ Main Entry point, parses the cmd_type and calls the relevant functions """
        try:
            super().RunScript(*args, **kwargs)
            if kwargs.get('caller',None)=='settings':
                self.CreateLogoSources(**kwargs)
                return None
        except Exception as e:
            self.ShowError(uMsg='Can\'t run TV Helper script, invalid parameter',uParConfigName=self.uConfigName,oException=e)
        return {"ret":1}

    def Register(self, *args, **kwargs) -> None:
        super().Register(*args, **kwargs)
        Globals.oNotifications.RegisterNotification(uNotification='STARTSCRIPTCREATETVLOGOS', fNotifyFunction=self.CreateLogoSources,   uDescription="Script CreateTVLogos")

        oScriptSettingPlugin:cScriptSettingPlugin   = cScriptSettingPlugin()
        oScriptSettingPlugin.uScriptName            = self.uObjectName
        oScriptSettingPlugin.uSettingName           = 'ORCA'
        oScriptSettingPlugin.uSettingPage           = '$lvar(572)'
        oScriptSettingPlugin.uSettingTitle          = '$lvar(SCRIPT_TOOLS_CREATETVLOGOS_4)'
        oScriptSettingPlugin.aSettingJson           = ['{"type": "buttons","title": "$lvar(SCRIPT_TOOLS_CREATETVLOGOS_1)","desc": "$lvar(SCRIPT_TOOLS_CREATETVLOGOS_2)","section": "ORCA","key": "button_notification","buttons":[{"title":"$lvar(SCRIPT_TOOLS_CREATETVLOGOS_3)","id":"button_notification_STARTSCRIPTCREATETVLOGOS"}]}']
        Globals.oScripts.RegisterScriptInSetting(uScriptName=self.uObjectName,oScriptSettingPlugin=oScriptSettingPlugin)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def CreateLogoSources(self,**kwargs) -> None:
        aSourceIcons:List[str]
        dFolderTarget:Dict[str,str] = {}
        oFnDest:cFileName
        oFnSource:cFileName
        oFnTarFile:cFileName
        oPathDest:cPath
        oPathDestRef:cPath
        oPathDestSub:cPath
        uFileCore:str
        uFile:str
        uFnSource:str
        uPathSource:str
        uSubFolder:str
        oPathSources:cPath
        oPathSourcesDebug:cPath
        aFolder:List[str]
        aFiles:List[str]

        oPathSources = cPath('$var(RESOURCEPATH)/tvlogos-src')
        oPathSourcesDebug = cPath('c:/tvlogos-src')
        if oPathSourcesDebug.Exists():
            oPathSources=oPathSourcesDebug

        oPathSourcesDebug = OS_GetSystemUserPath() + 'tvlogos-src'
        if oPathSourcesDebug.Exists():
            oPathSources=oPathSourcesDebug

        aFiles = oPathSources.GetFileList(bSubDirs=False,bFullPath=True)
        if aFiles:
            oFnSource = cFileName(oPathSources)+'srp.index.txt'
            if not  oFnSource.Exists():
                ShowErrorPopUp(uMessage='srp.index.txt is missing in source folder!')
                return
            oPathSourcesDebug = OS_GetSystemTmpPath()+'tvlogos-src'
            oPathSourcesDebug.Delete()
            oPathSourcesDebug.Create()
            oFnSource.Copy(oNewFile=oPathSourcesDebug)
            for uFnXY in aFiles:
                if uFnXY.endswith('.tar.xz') and 'snp-full' in uFnXY and '190x102.' in uFnXY:
                    oTarFile = cTarFile().ImportFullPath(uFnFullName=uFnXY)
                    self.ShowDebug(uMsg=f'Untar: {oTarFile} to {oPathSourcesDebug}')
                    oTarFile.UnTar(oPath=oPathSourcesDebug)
            oPathSources = oPathSourcesDebug

        aFolder = oPathSources.GetFolderList(bFullPath=True)
        for uPathSource in aFolder:
            dFolderTarget.clear()
            uFileCore = uPathSource[uPathSource.rfind('102.')+4:uPathSource.find('_')]
            oPathDest = Globals.oPathTVLogos+uFileCore
            oPathDest.Create()

            self.ShowDebug(uMsg=f'Create Picons for: {oPathDest}')

            oFnSource = cFileName(oPathSources)+'srp.index.txt'

            if not  oFnSource.Exists():
                ShowErrorPopUp(uMessage='srp.index.txt is missing in source folder!')
                return

            oFnSource.Copy(oNewFile=oPathDest)

            oPathDest=oPathDest+'picons'
            oPathDest.Create()
            oPathDestRef=oPathDest+'references'
            oPathDestRef.Create()
            aSourceIcons = cPath(uPathSource).GetFileList(bFullPath=False,bSubDirs=False)
            for uFnSource in aSourceIcons:
                oFnSource = cFileName(cPath(uPathSource)) + uFnSource
                if uFnSource.startswith('1_'):
                    oFnSource.Copy(oNewFile=oPathDestRef)
                else:
                    uSubFolder=uFnSource.upper()[:2]
                    uSubFolder=uSubFolder.replace('.','')
                    if uSubFolder[0].isnumeric():
                        uSubFolder='0-9'
                    oPathDestSub=oPathDest+uSubFolder
                    if not uSubFolder in dFolderTarget:
                        dFolderTarget[uSubFolder] = uSubFolder
                        oPathDestSub.Create()
                    oFnSource.Copy(oNewFile=oPathDestSub)

