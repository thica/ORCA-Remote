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

import urllib
import json
import sys

from xml.etree.ElementTree      import ElementTree
from xml.etree.ElementTree      import Element
from xml.etree.ElementTree      import SubElement

from kivy.logger                import Logger
from kivy.event                 import EventDispatcher
from kivy.network.urlrequest    import UrlRequest
from kivy.clock                 import Clock
from kivy.compat                import PY2

from ORCA.settings.setttingtypes.Public import RegisterSettingTypes
from ORCA.ui.ProgressBar        import cProgressBar
from ORCA.ui.ShowErrorPopUp     import ShowMessagePopUp, ShowErrorPopUp
from ORCA.utils.ConfigHelpers   import Config_GetDefault_Str
from ORCA.utils.Filesystem      import AdjustPathToOs
from ORCA.utils.Zip             import cZipFile
from ORCA.utils.LogError        import LogError
from ORCA.utils.wait.StartWait  import StartWait
from ORCA.utils.wait.StopWait   import StopWait
from ORCA.vars.Replace          import ReplaceVars
from ORCA.vars.Access           import SetVar
from ORCA.utils.TypeConvert     import ToDic
from ORCA.utils.TypeConvert     import ToInt
from ORCA.utils.TypeConvert     import ToIntVersion
from ORCA.utils.TypeConvert     import ToUnicode
from ORCA.utils.XML             import GetXMLBoolValue
from ORCA.utils.XML             import GetXMLTextAttribute
from ORCA.utils.XML             import GetXMLTextValue
from ORCA.utils.FileName        import cFileName
from ORCA.utils.Path            import cPath
import ORCA.Globals as Globals

this = sys.modules[__name__]

this.oGlobalProgressBar=None

# Helper class to hold all installed resources like definitions, , etc

class cDownLoadObject(object):
    """ Representation of a single object to download"""
    def __init__(self):
        self.aPars = {  "Url"     :"",
                        "Dest"    :"",
                        "Target"  :"",
                        "Type"    :"",
                        "Name"    :"",
                        "Version" :"",
                        "Finalize":""  }

    def ToString(self):
        """ Dumps the pars of the object """
        return json.dumps(self.aPars)
    def FromString(self,uPars):
        """ loads the parameters from a json string """
        self.aPars=json.loads(uPars)


def CreateProgressBar(uTitle,uMessage,lMax):
    """ Creates a Progressbar """
    if this.oGlobalProgressBar is None:
        this.oGlobalProgressBar=cProgressBar()
        this.oGlobalProgressBar.Show(uTitle,uMessage,lMax)
    else:
        this.oGlobalProgressBar.ReInit(uTitle,uMessage,lMax)
    return this.oGlobalProgressBar

def RemoveProgressBar():
    """ Removes an active progressbar """

    if not this.oGlobalProgressBar is None:
        this.oGlobalProgressBar.ClosePopup()
        this.oGlobalProgressBar=None

class cInstalledReps(object):
    """ A class representing an installed repository"""
    def __init__(self):
        self.uType    = ''
        self.uName    = ''
        self.iVersion = 0
    def __str__(self):
        return self.uType

# class to load a web based resource by url (not ftp)

class cLoadOnlineResource(EventDispatcher):
    """ Class for loading a single online resource """
    def __init__(self, *args, **kwargs):
        super(cLoadOnlineResource, self).__init__(*args, **kwargs)
        self.register_event_type('on_download_finished')

        self.bIsLoading      = False
        self.oRef            = None
        self.uDest           = ""
        self.uTarget         = ""
        self.uType           = ""
        self.uName           = ""
        self.uVersion        = ""
        self.oWeb            = None
        self.oProgressBar    = None
        self.bFinished       = False
        self.bOnError        = False
        self.bIsLoading      = True
        self.bFirstMessage   = True
        self.uUrl            = ''

    def LoadSingleFile(self, sRef,oProgressBar):
        """
        Loads a single resource by web
        dispatches on_download_finished when finished
        """

        self.oRef            = cDownLoadObject()
        self.oRef.FromString(sRef)

        uUrl                 = self.oRef.aPars["Url"]
        self.uDest           = self.oRef.aPars["Dest"]
        self.uTarget         = self.oRef.aPars["Target"]
        self.uType           = self.oRef.aPars["Type"]
        self.uName           = self.oRef.aPars["Name"]
        self.uVersion        = self.oRef.aPars["Version"]

        self.oWeb            = None
        self.oProgressBar    = oProgressBar
        self.bFinished       = False
        self.bOnError        = False
        self.bIsLoading      = True
        self.bFirstMessage   = True

        StartWait()

        try:
            Logger.debug("LoadOnlineResource: Downloading [%s] to [%s]" % (uUrl,self.uDest))
            if PY2:
               self.uUrl  = urllib.quote(uUrl,safe="%/:=&?~#+!$,;'@()*[]")
            else:
                self.uUrl = urllib.parse.quote(uUrl, safe="%/:=&?~#+!$,;'@()*[]")

            #self.uUrl         = urllib.quote(uUrl,safe="%:=&?~#+!$,;'@()*[]")
            self.oWeb         = UrlRequest(self.uUrl,on_success=self.OnSuccess,on_failure=self.OnFailure,on_error=self.OnError,on_progress=self.OnProgress, decode=False,file_path=self.uDest, debug=False)

            return True
        except Exception as e:
            LogError(u'can\'t load online resource: %s to %s' % (self.uUrl,self.uDest),e)
            self.bFinished  = True
            self.bOnError   = True
            self.bIsLoading = False
            StopWait()
            SetVar(uVarName = "DOWNLOADERROR", oVarValue = "1")
            self.dispatch('on_download_finished')
            return False

    def OnError(self,request,result):
        """ Handle an FTP error event """
        self.OnFailure(request,result)
    def OnFailure(self,request,result):
        """ Handle an FTP Failure event """
        self.bFinished = True
        self.bOnError  = True
        cFileName('').ImportFullPath(self.uDest).Delete()
        LogError(u'can\'t load online resource: %s to %s [%s]' % (self.uUrl,self.uDest,result))
        self.OnSuccess(None,None)
        self.bIsLoading=False
        SetVar(uVarName = "DOWNLOADERROR", oVarValue = "1")
        StopWait()
        return
    def OnProgress(self,request,lCurrentSize,lTotalSize):
        """ Updates the progressbar  """
        if not self.oProgressBar is None:
            if self.bFirstMessage:
                self.bFirstMessage=False
                self.oProgressBar.SetMax(lTotalSize)

            if self.oProgressBar.bCancel:
                self.bFinished = True
                self.bOnError  = True
                cFileName('').ImportFullPath(self.uDest).Delete()
                self.OnSuccess(None,None)
                return

            self.oProgressBar.Update(lCurrentSize)

    def OnSuccess(self,request,result):
        """ Handles when the download of a single file finishes  """
        self.bIsLoading=False
        self.dispatch('on_download_finished')
        self.bFinished = True

        oFileName = cFileName().ImportFullPath(self.uDest)
        if not oFileName.Exists():
            Logger.error("Target File not found:" + oFileName.string)
            self.bOnError = True

        if not self.bOnError:
            self.Finish()
        StopWait()

    def on_download_finished(self):
        """ blank function for dispatcher """
        pass

    def Finish(self):
        """ Finishs loading """
        if self.oRef.aPars["Finalize"]=="REPOSITORY XML":
            try:
                oET_Root = ElementTree(file=self.uDest).getroot()
                if not oET_Root is None:
                    oRepository.ParseFromXMLNode(oET_Root)
            except Exception as e:
                LogError(u'can\'t parse repository:'+self.uUrl,e)
                return True
        if self.oRef.aPars["Finalize"]=="FILE ZIP":
            try:
                if not self.bOnError:
                    if self.uTarget.startswith('.' or '..' in self.uTarget):
                        LogError('All destination pathes must be inside the ORCA directory, absolute pathes are not allowed!:'+self.uTarget)
                    else:
                        oZipFile = cZipFile('').ImportFullPath(self.uDest)
                        if oZipFile.IsZipFile():
                            if not Globals.bProtected:
                                oZipFile.Unzip(cPath('$var(APPLICATIONPATH)/'+self.uTarget))
                            else:
                                LogError("Protected: Nothing will be unzipped")
                        else:
                            if oZipFile.Exists():
                                Logger.error("Failed to unzip:"+oZipFile.string)
                            else:
                                Logger.error("Failed to download zip:" + oZipFile.string)
                                #todo: handle unzipped files
                    oZipFile.Delete()
                Logger.debug('LoadOnlineResource: Finished download Resource  [%s][%s]' % (self.uType,self.uName))
                RegisterDownLoad(self.uType,self.uName,ToInt(self.uVersion))
            except Exception as e:
                LogError(u'can\'t unpack resources:'+self.uUrl,e)

class cRepSource(object):
    """
    sub class which is an representation of the source part the repository xml tree
    loads and writes the xml node
    """

    def __init__(self):
        self.uSourceFile          = u''
        self.uTargetPath          = u''
        self.uLocal               = u''
    def ParseFromXMLNode(self,oXMLNode):
        """ Parses an xms string into object vars """
        self.uSourceFile = GetXMLTextValue(oXMLNode,u'sourcefile',True,u'')
        self.uTargetPath = GetXMLTextValue(oXMLNode,u'targetpath',True,u'')
        self.uLocal      = AdjustPathToOs(ReplaceVars(GetXMLTextValue(oXMLNode,u'local',False,u'')))
    def WriteToXMLNode(self,oXMLNode):
        """ writes object vars to an xml node """
        oXMLSource = SubElement(oXMLNode,'source')
        oVal       = SubElement(oXMLSource,'sourcefile')

        oFnUrl     = cFileName('').ImportFullPath(self.uSourceFile)
        oVal.text  = oFnUrl.urlstring
        oVal       = SubElement(oXMLSource,'targetpath')
        oVal.text  = self.uTargetPath
        # we do not write local by purpose

class cRepDependency(object):
    """
    sub class which is an representation of the dependency part the repository xml tree
    loads and writes the xml node
    """
    def __init__(self):
        self.uType           = u''
        self.uName           = u''
    def ParseFromXMLNode(self,oXMLNode):
        """ Parses an xms string into object vars """
        self.uType = GetXMLTextValue(oXMLNode,u'type',True,u'')
        self.uName = GetXMLTextValue(oXMLNode,u'name',True,u'')
    def WriteToXMLNode(self,oXMLNode):
        """ writes object vars to an xml node """
        oXMLSource = SubElement(oXMLNode,'dependency')
        oVal      = SubElement(oXMLSource,'type')
        oVal.text = self.uType
        oVal      = SubElement(oXMLSource,'name')
        oVal.text = self.uName

class cRepSkipFile(object):
    """
    sub class which is an representation of the skip files part the repository xml tree
    loads and writes the xml node
    """
    def __init__(self):
        self.uFile = u''
    def ParseFromXMLNode(self,oXMLNode):
        """ Parses an xms string into object vars """
        self.uFile = AdjustPathToOs(oXMLNode.text)
    def WriteToXMLNode(self,oXMLNode):
        """ writes object vars to an xml node """
        oVal = SubElement(oXMLNode,'file')
        oVal.text=self.uFile


class cRepDescription(object):
    """
    sub class which is an representation of the descriptions part the repository xml tree for the different languages
    loads and writes the xml node
    """
    def __init__(self):
        self.aDescriptions={'English':''}

    def ParseFromXMLNode(self,oXMLEntry):
        """ Parses an xms string into object vars """
        oXMLDescriptions=oXMLEntry.findall('description')
        for oXMLDescription in oXMLDescriptions:
            uLanguage=GetXMLTextAttribute(oXMLDescription,'language',False,'English')
            self.aDescriptions[uLanguage]=GetXMLTextValue(oXMLDescription,'',False,'')

    def WriteToXMLNode(self,oXMLNode):
        """ writes object vars to an xml node """
        for uKey in self.aDescriptions:
            oVal = SubElement(oXMLNode,'description')
            oVal.text = self.aDescriptions[uKey]
            oVal.set('language', uKey)

class cRepEntry(object):
    """
    sub class which is an representation of the repositories entry part the repository xml tree
    loads and writes the xml node
    """
    def __init__(self):
        self.aDependencies          = []
        self.aSkipFileNames         = []
        self.aSkipFiles             = []
        self.aSources               = []
        self.bSkip                  = False
        self.iMinOrcaVersion        = 0
        self.iVersion               = 0
        self.oDescriptions          = cRepDescription()
        self.uAuthor                = u''
        self.uDescription           = u''
        self.uMinOrcaVersion        = u''
        self.uName                  = u'Error'
        self.oPath                  = None
        self.uRepType               = u''
        self.uUrl                   = u''
        self.uVersion               = u''

    def __repr__(self):
        return repr(self.uName)

    def ParseFromXMLNode(self,oXMLEntry):
        """ Parses an xms string into object vars """
        self.uName          = GetXMLTextValue(oXMLEntry,u'name',True,u'Error')
        self.uAuthor        = GetXMLTextValue(oXMLEntry,u'author',False,u'unknown')
        self.uVersion       = GetXMLTextValue(oXMLEntry,u'version',False,u'0')
        self.uMinOrcaVersion= GetXMLTextValue(oXMLEntry,u'minorcaversion',False,u'1.1.0')
        self.bSkip          = GetXMLBoolValue(oXMLEntry,u'skip',False,False)
        self.iVersion       = ToIntVersion(self.uVersion)
        self.iMinOrcaVersion= ToIntVersion(self.uMinOrcaVersion)
        self.oDescriptions.ParseFromXMLNode(oXMLEntry)

        oXMLSources = oXMLEntry.find(u'sources')
        if not oXMLSources is None:
            for oXMLSource in oXMLSources.findall(u'source'):
                oSource=cRepSource()
                oSource.ParseFromXMLNode(oXMLSource)
                self.aSources.append(oSource)

        oXMLDependencies = oXMLEntry.find(u'dependencies')
        if not oXMLDependencies is None:
            for oXMLDependency in oXMLDependencies.findall(u'dependency'):
                oRepDependency=cRepDependency()
                oRepDependency.ParseFromXMLNode(oXMLDependency)
                self.aDependencies.append(oRepDependency)

        oXMLSkipFiles = oXMLEntry.find(u'skipfiles')
        if not oXMLSkipFiles is None:
            oRepSkipFile=cRepSkipFile()
            for oXMLSkipFile in oXMLSkipFiles.findall(u'file'):
                oRepSkipFile.ParseFromXMLNode(oXMLSkipFile)
                oRepSkipFile.uFile=ReplaceVars(oRepSkipFile.uFile)
                self.aSkipFiles.append(oRepSkipFile)
                self.aSkipFileNames.append(oRepSkipFile.uFile)

    def WriteToXMLNode(self,oXMLNode):
        """ writes object vars to an xml node """
        oXMLEntry   = SubElement(oXMLNode,'entry')
        oVal        = SubElement(oXMLEntry,'name')
        oVal.text   = self.uName
        self.oDescriptions.WriteToXMLNode(oXMLEntry)
        oVal        = SubElement(oXMLEntry,'author')
        oVal.text   = self.uAuthor
        oVal        = SubElement(oXMLEntry,'version')
        oVal.text   = self.uVersion
        oVal        = SubElement(oXMLEntry,'minorcaversion')
        oVal.text   = self.uMinOrcaVersion

        oXMLSources = SubElement(oXMLEntry,'sources')
        for oSource in self.aSources:
            oSource.WriteToXMLNode(oXMLSources)
        oXMLDependencies = SubElement(oXMLEntry,'dependencies')
        for oDependency in self.aDependencies:
            oDependency.WriteToXMLNode(oXMLDependencies)
        #we do not write skipfiles by purpose



class cRepository(EventDispatcher):
    """
    sub class which is an representation of a repostitory
    parses all entries of an repository
    loads and writes the xml node
    collects and holds all different rep types (definititions, codesets,..)
    all tasks for rep downloads are queued
    """
    def __init__(self, *args, **kwargs):
        super(cRepository, self).__init__(*args, **kwargs)
        self.uRepType               = u''
        self.uName                  = u''
        self.uDescription           = u''
        self.aRepEntries            = []
        self.oPath                  = None
        self.uUrl                   = u''
        self.uDest                  = u''
        self.aDownloads             = []
        self.oDownloader            = cLoadOnlineResource()
        self.bCancel                = False
        self.aRepEntries            = []
        self.aDownloads             = []
        self.uVersion               = ''

    def Init(self):
        """ Inits the Objects """
        del self.aRepEntries[:]
        del self.aDownloads[:]

    def ParseFromXMLNode(self,oXMLNode):
        """ Parses an xms string into object vars """
        try:
            self.uDescription   = GetXMLTextValue(oXMLNode,u'description',True,u'')
            self.uVersion       = GetXMLTextValue(oXMLNode,u'version',False,u'unknown')
            self.uRepType       = GetXMLTextValue(oXMLNode,u'type',False,u'unknown')
            oXMLEntries =  oXMLNode.find(u'entries')
            if not oXMLEntries is None:
                for oXMLEntry in oXMLEntries.findall(u'entry'):
                    oRepEntry=cRepEntry()
                    oRepEntry.ParseFromXMLNode(oXMLEntry)
                    if not oRepEntry.bSkip:
                        oRepEntry.uRepType = self.uRepType
                        oRepEntry.uUrl = self.uUrl
                        if oRepEntry.iMinOrcaVersion<=Globals.iVersion:
                            self.aRepEntries.append(oRepEntry)
                        else:
                            Logger.warning("Skip dependency as it needs a newer ORCA Version, Minimum: %d, Orca: %d" %(oRepEntry.iMinOrcaVersion , Globals.iVersion))
        except Exception as e:
            LogError(u'Can\'t parse repository:'+self.uUrl,e)

    def WriteToXMLNode(self,uType):
        """ writes object vars to an xml node """
        oXMLRoot    = Element('repository')
        oVal        = SubElement(oXMLRoot,'version')
        oVal.text   = '1.00'
        oVal        = SubElement(oXMLRoot,'type')
        oVal.text   = uType
        oVal        = SubElement(oXMLRoot,'description')
        oVal.text   ='Orca genuine repository'

        oXMLEntries = SubElement(oXMLRoot,'entries')
        for oRepEntry in self.aRepEntries:
            oRepEntry.WriteToXMLNode(oXMLEntries)

    def LoadAllSubReps(self,uPath,aSubReps,bDoNotExecute):
        """ Load all sub reposities (dependencies) """

        Logger.debug('Repository: Request to download reposity description: [%s]' %(uPath))

        bDoRefresh=False

        if "setting" in Globals.oTheScreen.uCurrentPageName.lower():
            bDoRefresh=True

        oEvents=Globals.oEvents
        oDownLoadObject=cDownLoadObject()

        aActions=oEvents.CreateSimpleActionList([{'string':'setvar','varname':'DOWNLOADERROR','varvalue':'0'},
                                                 {'string':'showprogressbar','title':'$lvar(5015)','message':uPath,'max':'100'}])
        for uSubRep in aSubReps:
            uRepType                            = uSubRep[1]
            uRepPrettyName                      = uSubRep[0]
            uUrl                                = '%s/%s/repository.xml' % (uPath,uRepType)
            oDownLoadObject.aPars['Url']        = uUrl
            oDownLoadObject.aPars['Type']       = uRepType
            oDownLoadObject.aPars['Dest']       = (cFileName(Globals.oPathTmp) + 'download.xml').string
            oDownLoadObject.aPars['Finalize']   = "REPOSITORY XML"
            oDownLoadObject.aPars['PrettyName'] = uRepPrettyName

            oEvents.AddToSimpleActionList(aActions,[{'string':'showprogressbar','message':uUrl,'current':'0'},
                                                    {'string':'loadresource','resourcereference':oDownLoadObject.ToString(),'condition':"$var(DOWNLOADERROR)==0"}])


        oEvents.AddToSimpleActionList(aActions,[{'string':'showprogressbar'}])

        if bDoRefresh:
            oEvents.AddToSimpleActionList(aActions,[{'string':'updatewidget','widgetname':'SettingsDownload'}])

        oEvents.AddToSimpleActionList(aActions,[{'string':'showquestion','title':'$lvar(595)','message':'$lvar(698)','actionyes':'dummy','condition':'$var(DOWNLOADERROR)==1'}])

        #Execute the Queue
        oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

        return aActions

    def CancelLoading(self):
        """ Set a flag when loading has been cancelled """
        SetVar(uVarName = "DOWNLOADERROR", oVarValue = "1")

def GetInstalledVersion(uType,uName):
    """ Gets the installed version of a repository element """
    uKey='%s:%s'%(uType,uName)
    oRep=Globals.dInstalledReps.get(uKey)
    if not oRep is None:
        iVersion=oRep.iVersion
    else:
        iVersion=0
    return iVersion

class cDownLoad_Settings(EventDispatcher):
    """ Reprensation of the settings tab """
    def __init__(self, *args, **kwargs):
        super(cDownLoad_Settings, self).__init__(*args, **kwargs)
        self.aSubReps                                   = Globals.aRepNames
        self.oSetting                                   = None
        # aQueue = queue of all repository items to load (just for reference, names only)
        self.aQueue                                     = []
        # aItemQueue = queue of all files to load (full json string)
        self.aItemQueue                                 = []
        self.oOnlineResourceQueueManager                = None
        self.aUpdateQueue                               = []
        self.uLast                                      = u''
        self.bForce                                     = False

    def LoadDirect(self,uDirect, bForce):
        """ Directly loads a Resources """
        self.bForce  = bForce
        self.On_ConfigChange(None, None, '', 'button_add_resource', uDirect)

    def UpdateAllInstalledRepositories(self,bForce):
        """ Update all installed repositories """

        del self.aQueue[:]
        del self.aItemQueue[:]
        self.bForce=bForce

        for oInstalledRepKey in Globals.dInstalledReps:
            Logger.debug("Schedule to update "+oInstalledRepKey)
            oInstalledRep=Globals.dInstalledReps[oInstalledRepKey]
            self.CreateDownloadQueueForRepositoryItem(oInstalledRep.uType,oInstalledRep.uName)
        self.DownloadDownloadQueue()

    def ConfigDownLoadSettings(self,oSetting):
        """  Creates the settings tab for download """
        self.oSetting = oSetting
        self.bForce   = False
        RegisterSettingTypes(oSetting)
        uSettingsJSONResources     =u'[{"type": "title","title": "$lvar(694)" },\n'

        iNumber=0
        for uURL in Globals.aRepositories:
            if not uURL=='':
                uSettingsJSONResources+=u'{"type": "bool","title": "$lvar(695) %s","desc": "%s","section": "ORCA","key": "repository_state%s"},\n' % (str(iNumber),uURL,str(iNumber))
            iNumber+=1

        uSettingsJSONResources    +=u'{"type": "buttons","title": "$lvar(696)","desc": "$lvar(697)","section": "ORCA","key": "button_load_resources","buttons":[{"title":"$lvar(5016)","id":"button_load_resources"}]}]\n'

        aSubList2=sorted(oRepository.aRepEntries, key=lambda entry: entry.uName)

        for uSubRep in self.aSubReps:
            aSubList = [oEntry for oEntry in aSubList2 if oEntry.uRepType == uSubRep[1]]
            if len(aSubList)>0:
                uSettingsJSON   = u'['
                for oEntry in aSubList:
                    uDescription=''
                    if len(oEntry.oDescriptions.aDescriptions)>0:
                        uDescription=oEntry.oDescriptions.aDescriptions.get(Globals.uLanguage)
                        if uDescription is None:
                            uDescription=oEntry.oDescriptions.aDescriptions.get('English')
                        if uDescription is None:
                            for uKey in oEntry.oDescriptions.aDescriptions:
                                uDescription=oEntry.oDescriptions.aDescriptions[uKey]
                                break
                    uSettingsJSON  +=   u'{"type": "buttons","title": "%s ","desc": "%s %s:%s","section": "ORCA","key": "button_add_resource","buttons":[{"title":"$lvar(5016)","id":"button:%s:%s"}]},' % (oEntry.uName,uDescription,'$lvar(673)',oEntry.uVersion,uSubRep[1] ,oEntry.uName)
                uSettingsJSON=uSettingsJSON[:-1]+ u']'
                oSetting.add_json_panel(ReplaceVars(uSubRep[0]),  None, data=ReplaceVars(uSettingsJSON))

        oSetting.add_json_panel("Resources", Globals.oOrcaConfigParser, data=ReplaceVars(uSettingsJSONResources))

        oSetting.bind(on_close         = self.On_SettingsClose)
        oSetting.bind(on_config_change = self.On_ConfigChange)

        return oSetting

    def On_SettingsClose(self,instance):
        """ Called when the setting is called """
        Globals.oNotifications.SendNotification('closesetting_download')
        oRepository.CancelLoading()
        Clock.schedule_once(Globals.oApp.fdo_config_change_load_definition,0.2)
        return True

    def LoadRepositoryDirectory(self, bDoNotExecute):
        """ Loads the directory of a repository """
        aActions= []
        if len(oRepository.aRepEntries)==0:
            for i in range(Globals.iCntRepositories):
                uRepKey=u'repository_state'+str(i)
                uRepUrl=Globals.aRepositories[i]
                if not uRepUrl=='':
                    if Config_GetDefault_Str(Globals.oOrcaConfigParser, u'ORCA', uRepKey, '0')!= '0':
                        oRepository.Init()
                        aActions+= oRepository.LoadAllSubReps(ReplaceVars(uRepUrl),self.aSubReps, bDoNotExecute)
        return aActions

    def On_ConfigChange(self,oSettings, oConfig, uSection, uKey, uValue):
        """ Handles a change of a setting element """

        if uKey==u'button_load_resources':
            self.LoadRepositoryDirectory(bDoNotExecute=False)
        elif uKey=='button_add_resource':
            self.uLast=uValue
            uTmp,uRepType,uRepName=uValue.split(':')
            del self.aQueue[:]
            del self.aItemQueue[:]
            self.CreateDownloadQueueForRepositoryItem(uRepType,uRepName)
            self.DownloadDownloadQueue()

        elif uKey.startswith(u'repository_state'):
            pass
        else:
            ShowMessagePopUp(uMessage=u'$lvar(5011)')
        return True

    def DownloadDownloadQueue(self):
        """ starts to load the complete queue """

        bDoRestart=False
        bDoRefresh=False

        if "setting" in Globals.oTheScreen.uCurrentPageName.lower():
            bDoRefresh=True

        oEvents=Globals.oEvents

        for uRep in self.aQueue:
            if uRep.startswith("definitions"):
                bDoRestart=True

        aActions=oEvents.CreateSimpleActionList([{'string':'setvar','varname':'DOWNLOADERROR','varvalue':'0'},
                                                 {'string':'showprogressbar','title':'$lvar(5015)','message':'Load File','max':'100'}])


        for uItem in self.aItemQueue:
            uType=ToDic(uItem)['Type']
            uPrettyRepName='?'
            for uRep in Globals.aRepNames:
                if uRep[1]==uType:
                    uPrettyRepName=ReplaceVars(uRep[0])
                    break

            uName='%s: %s' % (uPrettyRepName,ToDic(uItem)['Name'])
            oEvents.AddToSimpleActionList(aActions,[{'string':'showprogressbar','message':uName,'current':'0'},
                                                    {'string':'loadresource','resourcereference':uItem,'condition':"$var(DOWNLOADERROR)==0"}])

        oEvents.AddToSimpleActionList(aActions,[{'string':'showprogressbar'},
                                                {'string':'showquestion','title':'$lvar(595)','message':'$lvar(698)','actionyes':'dummy','condition':'$var(DOWNLOADERROR)==1'}])

        if bDoRefresh and not bDoRestart:
            oEvents.AddToSimpleActionList(aActions,[{'string':'updatewidget','widgetname':'SettingsDownload'}])

        if bDoRestart:
            oEvents.AddToSimpleActionList(aActions,[{'string':'restartafterdefinitiondownload','condition':'$var(DOWNLOADERROR)==0'}])

        #Execute the Queue
        StopWait()
        oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

    def CreateDownloadQueueForRepositoryItem(self,uRepType,uRepName):
        """ we need to prevent an endless recursion on dependencies, so we need to track, what we allready have """

        oDownLoadObject=cDownLoadObject()
        uRef=uRepType+uRepName

        if not uRef in self.aQueue:
            self.aQueue.append(uRef)
            aSubList = [oEntries for oEntries in oRepository.aRepEntries    if oEntries.uRepType == uRepType]
            aEntry = [oEntries for oEntries in aSubList                   if oEntries.uName == uRepName]

            if len(aEntry)>0:
                oEntry=aEntry[0]

                iInstalledVersion=GetInstalledVersion(uRepType,uRepName)

                if (oEntry.iVersion > iInstalledVersion) or self.bForce:
                    for oSource in oEntry.aSources:
                        oDownLoadObject.aPars["Url"]     = oSource.uSourceFile
                        oDownLoadObject.aPars["Dest"]    = (cFileName(Globals.oPathTmp) + 'download.xml').string
                        oDownLoadObject.aPars["Target"]  = oSource.uTargetPath
                        oDownLoadObject.aPars["Type"]    = uRepType
                        oDownLoadObject.aPars["Name"]    = uRepName
                        oDownLoadObject.aPars["Version"] = oEntry.iVersion
                        oDownLoadObject.aPars["Finalize"]= "FILE ZIP"

                        uString = oDownLoadObject.ToString()
                        if uString not in self.aItemQueue:
                            self.aItemQueue.append(uString)

                    for oDependency in oEntry.aDependencies:
                        self.CreateDownloadQueueForRepositoryItem(oDependency.uType,oDependency.uName)
                else:
                    Logger.info('Skipping download of repository type:%s Resource:%s, Resource version [%d] not newer than installed version [%d]' % (uRepType,uRepName,oEntry.iVersion,iInstalledVersion))

            else:
                LogError("can\'t find Resource in Resourcelist: [%s] %s" %( uRepType,uRepName))
                ShowErrorPopUp(uMessage="can\'t find Resource in Resourcelist: [%s] %s" %( uRepType,uRepName))

def RegisterDownLoad(uType,uName,iVersion):
    """ Registers a repository """

    if not uName=='':
        oConfig                = Globals.oOrcaConfigParser
        oInstalledRep          = cInstalledReps()
        oInstalledRep.uType    = uType
        oInstalledRep.uName    = uName
        oInstalledRep.iVersion = iVersion
        uKey                   ='%s:%s'%(oInstalledRep.uType,oInstalledRep.uName)
        Globals.dInstalledReps[uKey]=oInstalledRep

        i=0
        for oInstalledRepKey in Globals.dInstalledReps:
            oInstalledRep=Globals.dInstalledReps[oInstalledRepKey]
            uKey=u'installedrep%i_type' % (i)
            oConfig.set(u'ORCA', uKey, oInstalledRep.uType)
            uKey=u'installedrep%i_name' % (i)
            oConfig.set(u'ORCA', uKey, oInstalledRep.uName)
            uKey=u'installedrep%i_version' % (i)
            oConfig.set(u'ORCA', uKey, ToUnicode(oInstalledRep.iVersion))

            i+=1
        oConfig.write()



oRepository = cRepository()
