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

from typing                                     import List
from typing                                     import Optional
from typing                                     import Tuple


from kivy.event                                 import EventDispatcher
from kivy.uix.settings                          import Settings as KivySettings
from kivy.logger                                import Logger
from kivy.clock                                 import Clock

from ORCA                                       import Globals as Globals
from ORCA.Action                                import cAction
from ORCA.download.DownloadObject               import cDownLoadObject
from ORCA.download.Repository                   import oRepository
from ORCA.settings.setttingtypes.Public         import RegisterSettingTypes
from ORCA.ui.ShowErrorPopUp                     import ShowErrorPopUp
from ORCA.ui.ShowErrorPopUp                     import ShowMessagePopUp
from ORCA.utils.ConfigHelpers                   import Config_GetDefault_Str
from ORCA.utils.FileName                        import cFileName
from ORCA.utils.LogError                        import LogError
from ORCA.utils.TypeConvert                     import ToDic
from ORCA.utils.wait.StopWait                   import StopWait
from ORCA.vars.Replace                          import ReplaceVars


__all__ = ['cDownLoad_Settings']

class cDownLoad_Settings(EventDispatcher):
    """ Reprensation of the settings tab """
    def __init__(self, *args, **kwargs):
        super(cDownLoad_Settings, self).__init__(*args, **kwargs)
        self.aSubReps:List[Tuple]                       = Globals.aRepNames
        self.oSetting:Optional[KivySettings]            = None
        # aQueue = queue of all repository items to load (just for reference, names only)
        self.aQueue:List[str]                           = []
        # aItemQueue = queue of all files to load (full json string)
        self.aItemQueue:List[str]                       = []
        self.uLast:str                                  = u''
        self.bForce:bool                                = False

    def LoadDirect(self,*,uDirect:str, bForce:bool) -> None:
        """ Directly loads a Resources """
        self.bForce  = bForce
        self.On_ConfigChange(None, None, '', 'button_add_resource', uDirect)

    def UpdateAllInstalledRepositories(self,*,bForce:bool) -> None:
        """ Update all installed repositories """

        del self.aQueue[:]
        del self.aItemQueue[:]
        self.bForce=bForce

        for oInstalledRepKey in Globals.dInstalledReps:
            Logger.debug("Schedule to update "+oInstalledRepKey)
            oInstalledRep=Globals.dInstalledReps[oInstalledRepKey]
            self.CreateDownloadQueueForRepositoryItem(uRepType=oInstalledRep.uType,uRepName=oInstalledRep.uName)
        self.DownloadDownloadQueue()

    def ConfigDownLoadSettings(self,*,oSetting:KivySettings) -> KivySettings:
        """  Creates the settings tab for download """
        self.oSetting               = oSetting
        self.bForce                 = False
        uSettingsJSONResources:str  = u'[{"type": "title","title": "$lvar(694)" },\n'
        iNumber:int                 = 0
        uURL:str
        uSubRep:str

        RegisterSettingTypes(oSetting)

        for uURL in Globals.aRepositories:
            if not uURL=='':
                uSettingsJSONResources+=u'{"type": "bool","title": "$lvar(695) %s","desc": "%s","section": "ORCA","key": "repository_state%s"},\n' % (str(iNumber),uURL,str(iNumber))
            iNumber+=1

        uSettingsJSONResources    +=u'{"type": "buttons","title": "$lvar(696)","desc": "$lvar(697)","section": "ORCA","key": "button_load_resources","buttons":[{"title":"$lvar(5016)","id":"button_load_resources"}]}]\n'

        aSubList2:List = sorted(oRepository.aRepEntries, key=lambda entry: entry.uName)

        for uSubRep in self.aSubReps:
            aSubList = [oEntry for oEntry in aSubList2 if oEntry.uRepType == uSubRep[1]]
            if len(aSubList)>0:
                uSettingsJSON   = u'['
                for oEntry in aSubList:
                    uDescription:str = ''
                    if len(oEntry.oDescriptions.dDescriptions)>0:
                        uDescription=oEntry.oDescriptions.dDescriptions.get(Globals.uLanguage)
                        if uDescription is None:
                            uDescription=oEntry.oDescriptions.dDescriptions.get('English')
                        if uDescription is None:
                            for uKey in oEntry.oDescriptions.dDescriptions:
                                uDescription=oEntry.oDescriptions.dDescriptions[uKey]
                                break
                    uSettingsJSON  +=   u'{"type": "buttons","title": "%s ","desc": "%s %s:%s","section": "ORCA","key": "button_add_resource","buttons":[{"title":"$lvar(5016)","id":"button:%s:%s"}]},' % (oEntry.uName,uDescription,'$lvar(673)',oEntry.uVersion,uSubRep[1] ,oEntry.uName)
                uSettingsJSON:str=uSettingsJSON[:-1]+ u']'
                oSetting.add_json_panel(ReplaceVars(uSubRep[0]),  None, data=ReplaceVars(uSettingsJSON))

        oSetting.add_json_panel("Resources", Globals.oOrcaConfigParser, data=ReplaceVars(uSettingsJSONResources))
        oSetting.bind(on_close         = self.On_SettingsClose)
        oSetting.bind(on_config_change = self.On_ConfigChange)

        return oSetting

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def On_SettingsClose(self,oSetting:KivySettings) -> bool:
        """ Called when the setting is called """
        Globals.oNotifications.SendNotification(uNotification='closesetting_download')
        oRepository.CancelLoading()
        Clock.schedule_once(Globals.oApp.fdo_config_change_load_definition,0.2)
        return True

    def LoadRepositoryDirectory(self,*,bDoNotExecute:bool) -> List[cAction]:
        """ Loads the directory of a repository """
        aActions:List[cAction] = []
        if len(oRepository.aRepEntries)==0:
            for i in range(Globals.iCntRepositories):
                uRepKey=u'repository_state'+str(i)
                uRepUrl=Globals.aRepositories[i]
                if not uRepUrl=='':
                    if Config_GetDefault_Str(oConfig=Globals.oOrcaConfigParser, uSection=u'ORCA', uOption=uRepKey, vDefaultValue='0')!= '0':
                        oRepository.Init()
                        aActions+= oRepository.LoadAllSubReps(uPath=ReplaceVars(uRepUrl),aSubReps=self.aSubReps, bDoNotExecute=bDoNotExecute)
        return aActions

    # noinspection PyUnusedLocal
    def On_ConfigChange(self,oSettings:Optional[KivySettings], oConfig, uSection:str, uKey:str, uValue:str) -> bool:
        """ Handles a change of a setting element """

        if uKey==u'button_load_resources':
            self.LoadRepositoryDirectory(bDoNotExecute=False)
        elif uKey=='button_add_resource':
            self.uLast=uValue
            uTmp,uRepType,uRepName=uValue.split(':')
            del self.aQueue[:]
            del self.aItemQueue[:]
            self.CreateDownloadQueueForRepositoryItem(uRepType=uRepType,uRepName=uRepName)
            self.DownloadDownloadQueue()

        elif uKey.startswith(u'repository_state'):
            pass
        else:
            ShowMessagePopUp(uMessage=u'$lvar(5011)')
        return True

    def DownloadDownloadQueue(self) -> None:
        """ starts to load the complete queue """

        uRep: str
        tRep: Tuple
        bDoRestart:bool = False
        bDoRefresh:bool = False

        if "setting" in Globals.oTheScreen.uCurrentPageName.lower():
            bDoRefresh=True

        oEvents=Globals.oEvents

        for uRep in self.aQueue:
            if uRep.startswith("definitions"):
                bDoRestart=True

        aActions:List[cAction]=oEvents.CreateSimpleActionList(aActions=[{'string':'setvar','varname':'DOWNLOADERROR','varvalue':'0'},
                                                                        {'string':'showprogressbar','title':'$lvar(5015)','message':'Load File','max':'100'}])

        for uItem in self.aItemQueue:
            uType:str=ToDic(uItem)['Type']
            uPrettyRepName:str='?'
            for tRep in Globals.aRepNames:
                if tRep[1]==uType:
                    uPrettyRepName=ReplaceVars(tRep[0])
                    break

            uName:str='%s: %s' % (uPrettyRepName,ToDic(uItem)['Name'])
            oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'showprogressbar','message':uName,'current':'0'},
                                                                         {'string':'loadresource','resourcereference':uItem,'condition':"$var(DOWNLOADERROR)==0"}])

        oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'showprogressbar'},
                                                                     {'string':'showquestion','title':'$lvar(595)','message':'$lvar(698)','actionyes':'dummy','condition':'$var(DOWNLOADERROR)==1'}])

        if bDoRefresh and not bDoRestart:
            oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'updatewidget','widgetname':'SettingsDownload'}])

        if bDoRestart:
            oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'restartafterdefinitiondownload','condition':'$var(DOWNLOADERROR)==0'}])

        #Execute the Queue
        StopWait()
        oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

    def CreateDownloadQueueForRepositoryItem(self,*,uRepType:str,uRepName:str) -> None:
        """ we need to prevent an endless recursion on dependencies, so we need to track, what we already have """

        oDownLoadObject:cDownLoadObject = cDownLoadObject()
        uRef:str                        = uRepType+uRepName

        if not uRef in self.aQueue:
            self.aQueue.append(uRef)
            aSubList:List = [oEntries for oEntries in oRepository.aRepEntries    if oEntries.uRepType == uRepType]
            aEntry:List   = [oEntries for oEntries in aSubList                   if oEntries.uName == uRepName]

            if len(aEntry)>0:
                oEntry=aEntry[0]

                iInstalledVersion:int = GetInstalledVersion(uType=uRepType,uName=uRepName)

                if (oEntry.iVersion > iInstalledVersion) or self.bForce:
                    for oSource in oEntry.aSources:
                        oDownLoadObject.dPars["Url"]     = oSource.uSourceFile
                        oDownLoadObject.dPars["Dest"]    = (cFileName(Globals.oPathTmp) + 'download.xml').string
                        oDownLoadObject.dPars["Target"]  = oSource.uTargetPath
                        oDownLoadObject.dPars["Type"]    = uRepType
                        oDownLoadObject.dPars["Name"]    = uRepName
                        oDownLoadObject.dPars["Version"] = oEntry.iVersion
                        oDownLoadObject.dPars["Finalize"]= "FILE ZIP"

                        uString:str = oDownLoadObject.ToString()
                        if uString not in self.aItemQueue:
                            self.aItemQueue.append(uString)

                    for oDependency in oEntry.aDependencies:
                        self.CreateDownloadQueueForRepositoryItem(uRepType=oDependency.uType,uRepName=oDependency.uName)
                else:
                    Logger.info('Skipping download of repository type:%s Resource:%s, Resource version [%d] not newer than installed version [%d]' % (uRepType,uRepName,oEntry.iVersion,iInstalledVersion))

            else:
                LogError(uMsg="can\'t find Resource in Resourcelist: [%s] %s" %( uRepType,uRepName))
                ShowErrorPopUp(uMessage="can\'t find Resource in Resourcelist: [%s] %s" %( uRepType,uRepName))

def GetInstalledVersion(*,uType:str,uName:str) -> int:
    """ Gets the installed version of a repository element """
    uKey:str    = '%s:%s'%(uType,uName)
    oRep        = Globals.dInstalledReps.get(uKey)
    iVersion:int
    if not oRep is None:
        iVersion=oRep.iVersion
    else:
        iVersion=0
    return iVersion

