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

from typing                             import List
from typing                             import Union
from xml.etree.ElementTree              import Element
from xml.etree.ElementTree              import SubElement
from kivy.logger                        import Logger
from kivy.event                         import EventDispatcher
from ORCA.utils.LogError                import LogError
from ORCA.vars.Access                   import SetVar
from ORCA.utils.XML                     import GetXMLTextValue
from ORCA.utils.FileName                import cFileName
from ORCA.utils.Path                    import cPath
import ORCA.Globals as Globals

from ORCA.download.DownloadObject       import cDownLoadObject
from ORCA.download.RepEntry             import cRepEntry
from ORCA.download.LoadOnlineResource   import cLoadOnlineResource

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.Events import cEvents
    from ORCA.Action import cAction
else:
    from typing import TypeVar
    cEvents     = TypeVar("cEvents")
    cAction     = TypeVar("cAction")

# Helper class to hold all installed resources like definitions, , etc

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
        self.uRepType:str                       = u''
        self.uName:str                          = u''
        self.uDescription:str                   = u''
        self.aRepEntries:List[cRepEntry]        = []
        self.oPath:Union[cPath,None]            = None
        self.uUrl:str                           = u''
        self.uDest:str                          = u''
        self.aDownloads:List                    = []
        self.oDownloader:cLoadOnlineResource    = cLoadOnlineResource(oRepository=self)
        self.bCancel:bool                       = False
        self.uVersion:str                       = u''

    def Init(self):
        """ Inits the Objects """
        del self.aRepEntries[:]
        del self.aDownloads[:]

    def ParseFromXMLNode(self,*,oXMLNode:Element) -> None:
        """ Parses an xml string into object vars """
        oXMLEntries:Element

        try:
            self.uDescription   = GetXMLTextValue(oXMLNode=oXMLNode,uTag=u'description',bMandatory=True, vDefault=u'')
            self.uVersion       = GetXMLTextValue(oXMLNode=oXMLNode,uTag=u'version',    bMandatory=False,vDefault=u'unknown')
            self.uRepType       = GetXMLTextValue(oXMLNode=oXMLNode,uTag=u'type',       bMandatory=False,vDefault=u'unknown')
            oXMLEntries =  oXMLNode.find(u'entries')
            if not oXMLEntries is None:
                for oXMLEntry in oXMLEntries.findall(u'entry'):
                    oRepEntry:cRepEntry=cRepEntry()
                    oRepEntry.ParseFromXMLNode(oXMLEntry=oXMLEntry)
                    if not oRepEntry.bSkip:
                        oRepEntry.uRepType = self.uRepType
                        oRepEntry.uUrl = self.uUrl
                        if oRepEntry.iMinOrcaVersion<=Globals.iVersion:
                            self.aRepEntries.append(oRepEntry)
                        else:
                            Logger.warning("Skip dependency as it needs a newer ORCA Version, Minimum: %d, Orca: %d" %(oRepEntry.iMinOrcaVersion , Globals.iVersion))
        except Exception as e:
            LogError(uMsg=u'Can\'t parse repository:'+self.uUrl,oException=e)

    def WriteToXMLNode(self,*,uType:str) -> None:
        """ writes object vars to an xml node """

        oXMLRoot:Element
        oVal:Element

        oXMLRoot    = Element('repository')
        oVal        = SubElement(oXMLRoot,'version')
        oVal.text   = '1.00'
        oVal        = SubElement(oXMLRoot,'type')
        oVal.text   = uType
        oVal        = SubElement(oXMLRoot,'description')
        oVal.text   ='Orca genuine repository'

        oXMLEntries = SubElement(oXMLRoot,'entries')
        for oRepEntry in self.aRepEntries:
            oRepEntry.WriteToXMLNode(oXMLNode=oXMLEntries)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def LoadAllSubReps(self,*,uPath:str,aSubReps:List,bDoNotExecute:bool) -> List:
        """ Load all sub reposities (dependencies) """

        Logger.debug('Repository: Request to download reposity description: [%s]' % uPath)

        bDoRefresh=False

        if "setting" in Globals.oTheScreen.uCurrentPageName.lower():
            bDoRefresh=True

        oEvents:cEvents                 = Globals.oEvents
        oDownLoadObject:cDownLoadObject = cDownLoadObject()

        aActions:List[cAction] = oEvents.CreateSimpleActionList(aActions=[{'string':'setvar','varname':'DOWNLOADERROR','varvalue':'0'},
                                                                          {'string':'showprogressbar','title':'$lvar(5015)','message':uPath,'max':'100'}])
        for uSubRep in aSubReps:
            uRepType                            = uSubRep[1]
            uRepPrettyName                      = uSubRep[0]
            uUrl                                = '%s/%s/repository.xml' % (uPath,uRepType)
            oDownLoadObject.dPars['Url']        = uUrl
            oDownLoadObject.dPars['Type']       = uRepType
            oDownLoadObject.dPars['Dest']       = (cFileName(Globals.oPathTmp) + 'download.xml').string
            oDownLoadObject.dPars['Finalize']   = "REPOSITORY XML"
            oDownLoadObject.dPars['PrettyName'] = uRepPrettyName

            oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'showprogressbar','message':uUrl,'current':'0'},
                                                                         {'string':'loadresource','resourcereference':oDownLoadObject.ToString(),'condition':"$var(DOWNLOADERROR)==0"}])


        oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'showprogressbar'}])

        if bDoRefresh:
            oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'updatewidget','widgetname':'SettingsDownload'}])

        oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'string':'showquestion','title':'$lvar(595)','message':'$lvar(698)','actionyes':'dummy','condition':'$var(DOWNLOADERROR)==1'}])

        #Execute the Queue
        oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)

        return aActions

    # noinspection PyMethodMayBeStatic
    def CancelLoading(self):
        """ Set a flag when loading has been cancelled """
        SetVar(uVarName = "DOWNLOADERROR", oVarValue = "1")


oRepository:cRepository = cRepository()
