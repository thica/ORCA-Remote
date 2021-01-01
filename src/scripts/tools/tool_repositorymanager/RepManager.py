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

from __future__             import annotations
import os

from typing                 import Union
from typing                 import List
from typing                 import Dict

from xml.etree.ElementTree  import Element
from xml.etree.ElementTree  import SubElement

from kivy.logger            import Logger

from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.TypeConvert import EscapeUnicode
from ORCA.utils.Filesystem  import AdjustPathToOs


from ORCA.utils.FileName    import cFileName
from ORCA.utils.LogError    import LogError
from ORCA.vars.Replace      import ReplaceVars
from ORCA.vars.Access       import SetVar
from ORCA.vars.Actions      import Var_DelArray
from ORCA.utils.XML         import XMLPrettify
from ORCA.utils.Path        import cPath
from ORCA.download.RepManagerEntry import cRepManagerEntry

import ORCA.Globals as Globals

oRepositoryManager:Union[cRepositoryManager,None] = None

def RepositoryManager(oPathRepSource:cPath) -> None:
    """ starts RepositoryManager, we make it global to avoid wrong garbage collection """
    global oRepositoryManager
    oRepositoryManager=cRepositoryManager(oPathRepSource)
    oRepositoryManager.CollectAndUpload()

def CreateRepVarArray(uBaseLocalDir:str) -> None:
    global oRepositoryManager
    if oRepositoryManager:
        oRepositoryManager.CreateRepVarArray(uBaseLocalDir)

class cRepositoryManager:
    """ The Main repository manager class, which uploads all reps to the cloud """
    def __init__(self,oPathRepSource) -> None:
        super(cRepositoryManager, self).__init__()
        self.aFiles:List[str]                           = []
        self.aRepManagerEntries:List[cRepManagerEntry]  = []
        self.aZipFiles:List[Dict]                       = []
        self.oPathRepSource:cPath                       = oPathRepSource

    def CollectAndUpload(self) -> None:
        """ Collects all Reps and uploads them """
        try:
            oPath:cPath = Globals.oPathTmp + "RepManager"
            oPath.Delete()

            self.GetOthers()
            self.GetCodesets()
            self.GetDefinitions()
            self.GetSkins()
            self.GetInterfaces()
            self.GetLanguages()
            self.GetSounds()
            self.GetScripts()
            self.GetWizardTemplates()
            self.GetFonts()
            self.CreateRepository()
        except Exception as e:
            uMsg=LogError(uMsg='Critical failure on Repository Manager ...' ,oException=e)
            ShowErrorPopUp(uMessage=uMsg)

    def GetOthers(self) -> None:
        """ Gets all others reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        self.aFiles=(self.oPathRepSource + 'repositories/orca-remote/repositories/others').GetFileList(bSubDirs = False, bFullPath = True)
        for uFn in self.aFiles:
            oRepManagerEntry:cRepManagerEntry = cRepManagerEntry(oFileName=uFn)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.aRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Resource not ready for Repository Manager, skipped: '+uFn)
        self.SaveRepositoryXML('others','Various ORCA resources')

    def GetFonts(self) -> None:
        """ Gets all others reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        aFontsFolders:List[str] = Globals.oPathFonts.GetFolderList(bFullPath=True)
        for uFontFolder in aFontsFolders:
            oFnFontDefinition:cFileName = cFileName(cPath(uFontFolder)) + "fonts.xml"
            oRepManagerEntry:cRepManagerEntry = cRepManagerEntry(oFileName=oFnFontDefinition)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.aRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Font not ready for Repository Manager, skipped: '+oFnFontDefinition)
        self.SaveRepositoryXML('fonts','Font Resources')

    def GetCodesets(self) -> None:
        """ Gets all codeset reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        self.aFiles=Globals.oPathCodesets.GetFileList(bSubDirs = True, bFullPath = True)
        for uFn in self.aFiles:
            if uFn.lower().endswith('.xml'):
                oRepManagerEntry:cRepManagerEntry=cRepManagerEntry(oFileName=uFn)
                if oRepManagerEntry.ParseFromXML():
                    if not oRepManagerEntry.oRepEntry.bSkip:
                        self.aRepManagerEntries.append(oRepManagerEntry)
                else:
                    Logger.warning('Codeset not ready for Repository Manager, skipped: '+uFn)
        self.SaveRepositoryXML('codesets','Orca Genuine Codesets')

    def GetSounds(self) -> None:
        """ Gets all sounds reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        for uSound in Globals.oSound.aSoundsList:
            oFnSound:cFileName = cFileName(Globals.oPathSoundsRoot + uSound) +"sounds.xml"
            oRepManagerEntry:cRepManagerEntry = cRepManagerEntry(oFileName=oFnSound)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.aRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Soundset not ready for Repository Manager, skipped: '+oFnSound)
        self.SaveRepositoryXML('sounds','Orca Genuine Sounds')

    def GetDefinitions(self) -> None:
        """ Gets all definition reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        for uDefinitionName in Globals.aDefinitionList:
            oFnFile:cFileName=cFileName().ImportFullPath(uFnFullName='%s/definitions/%s/definition.xml' % (Globals.oPathRoot.string, uDefinitionName))
            oRepManagerEntry:cRepManagerEntry=cRepManagerEntry(oFileName=oFnFile)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.aRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Definition not ready for Repository Manager, skipped: '+oFnFile)
        self.SaveRepositoryXML('definitions','Orca Genuine Definitions')

    def GetLanguages(self) -> None:
        """ Gets all Language reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        for uLanguage in Globals.aLanguageList:
            oFn:cFileName=cFileName().ImportFullPath(uFnFullName='%s/languages/%s/strings.xml' % (Globals.oPathRoot.string, uLanguage))
            oRepManagerEntry:cRepManagerEntry=cRepManagerEntry(oFileName=oFn)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.aRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Language not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('languages','Orca Genuine Language Files')

    def GetInterfaces(self) -> None:
        """ Gets all interface reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        for uInterFaceName in Globals.oInterFaces.aObjectNameList:
            oFn:cFileName=cFileName().ImportFullPath(uFnFullName='%s/interfaces/%s/interface.py' % (Globals.oPathRoot.string, uInterFaceName))
            oRepManagerEntry:cRepManagerEntry=cRepManagerEntry(oFileName=oFn)
            if oRepManagerEntry.ParseFromSourceFile():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.aRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Interface not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('interfaces','Orca Genuine Interfaces')

    def GetScripts(self) -> None:
        """ Gets all scripts reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        for uScriptName in Globals.oScripts.dScriptPathList:
            oFn:cFileName=cFileName(Globals.oScripts.dScriptPathList[uScriptName])+'script.py'
            oRepManagerEntry:cRepManagerEntry=cRepManagerEntry(oFileName=oFn)
            if oRepManagerEntry.ParseFromSourceFile():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.aRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Script not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('scripts','Orca Genuine Scripts')

    def GetSkins(self) -> None:
        """ Gets all skins reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        for uSkinName in Globals.aSkinList:
            oFn:cFileName=cFileName().ImportFullPath(uFnFullName='%s/skins/%s/skin.xml' % (Globals.oPathRoot.string, uSkinName))
            oRepManagerEntry:cRepManagerEntry=cRepManagerEntry(oFileName=oFn)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.aRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Skin not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('skins','Orca Genuine Skins')

    def GetWizardTemplates(self) -> None:
        """ Gets all wizard reps """
        del self.aFiles[:]
        del self.aRepManagerEntries[:]
        aDirs:List[str]=(Globals.oPathRoot + u'wizard templates').GetFolderList()
        for uDirName in aDirs:
            aDirsSub:List[str]=(Globals.oPathRoot + (u'wizard templates/' + uDirName)).GetFolderList()
            for uDirsSub in aDirsSub:
                oFn:cFileName=cFileName(Globals.oPathRoot + (u'wizard templates/' + uDirName + "/" + uDirsSub)) +  (uDirsSub + ".xml")
                oRepManagerEntry:cRepManagerEntry=cRepManagerEntry(oFileName=oFn)
                if oRepManagerEntry.ParseFromXML():
                    if not oRepManagerEntry.oRepEntry.bSkip:
                        self.aRepManagerEntries.append(oRepManagerEntry)
                else:
                    Logger.warning('Wizard Template not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('wizard templates','Wizard Templates')

    def SaveRepositoryXML(self,uType:str,uDescription:str) -> None:
        """ Saves the main repository directory xml """

        oVal:Element
        uContent:str
        uRoot:str

        oPath:cPath= Globals.oPathTmp + "RepManager"
        oPath.Create()
        oPath=oPath+"repositories"
        oPath.Create()
        oPath=oPath+uType
        oPath.Create()
        oFnXml:cFileName=cFileName(oPath) +'repository.xml'

        oXMLRoot:Element    = Element('repository')
        oVal                = SubElement(oXMLRoot,'version')
        oVal.text           = '1.00'
        oVal                = SubElement(oXMLRoot,'type')
        oVal.text           = uType
        oVal                = SubElement(oXMLRoot,'description')
        oVal.text           = uDescription

        oXMLEntries:Element = SubElement(oXMLRoot,'entries')

        for oEntry in self.aRepManagerEntries:
            Logger.debug ('Saving Repository-Entry [%s]' % oEntry.oFnEntry.string)

            oEntry.oRepEntry.WriteToXMLNode(oXMLNode=oXMLEntries)
            for oSource in oEntry.oRepEntry.aSources:
                bZipParentDir:bool = cPath.CheckIsDir(uCheckName=oSource.uLocal)
                # Create according Zip
                if bZipParentDir:
                    uUpper:str          = os.path.basename(oSource.uSourceFile)
                    uFinalPath:str      = uType
                    oDest:cFileName     = cFileName().ImportFullPath(uFnFullName='%s/RepManager/repositories/%s/%s' % (Globals.oPathTmp.string, uFinalPath, uUpper))
                    uUpper1:str         = os.path.split(os.path.abspath(oSource.uLocal))[0]
                    uRoot           = AdjustPathToOs(uPath=ReplaceVars(uUpper1)+'/')
                    self.aZipFiles.append({'filename':oSource.uLocal,'dstfilename':oDest.string, 'removepath':uRoot, 'skipfiles':ToUnicode(oEntry.oRepEntry.aSkipFileNames)})
                else:
                    uDest:str = AdjustPathToOs(uPath='%s/RepManager/repositories/%s/%s.zip' % (Globals.oPathTmp.string, uType, os.path.splitext(os.path.basename(oSource.uLocal))[0]))
                    uRoot = AdjustPathToOs(uPath=Globals.oPathRoot.string + "/" + oSource.uTargetPath)
                    self.aZipFiles.append({'filename':oSource.uLocal,'dstfilename':uDest, 'removepath':uRoot})

        oFSFile     = open(oFnXml.string, 'w')
        uContent    = XMLPrettify(oElem=oXMLRoot)
        uContent    = ReplaceVars(uContent)
        oFSFile.write(EscapeUnicode(uContent))
        oFSFile.close()

    def CreateRepository(self) -> None:
        self.CreateZipVarArray()
        SetVar(uVarName="REPMAN_BASELOCALDIR", oVarValue=(Globals.oPathTmp + "RepManager").string)
        Globals.oTheScreen.AddActionToQueue(aActions=[{'string': 'call Create Repository'}])
        return

    def CreateZipVarArray(self) -> None:
        SetVar(uVarName="REPMAN_ZIPCNTFILES",  oVarValue= str(len(self.aZipFiles)))
        Var_DelArray("REPMAN_ZIPSOUREFILENAMES[]")
        Var_DelArray("REPMAN_ZIPDESTFILENAMES[]")
        Var_DelArray("REPMAN_ZIPREMOVEPATH[]")
        Var_DelArray("REPMAN_ZIPSKIPFILES[]")
        Var_DelArray("REPMAN_ZIPTYPE[]")

        i:int=0
        for dZipFile in self.aZipFiles:
            uIndex:str = str(i) + "]"
            SetVar(uVarName="REPMAN_ZIPSOURCEFILENAMES[" + uIndex ,oVarValue=dZipFile['filename'])
            SetVar(uVarName="REPMAN_ZIPDESTFILENAMES[" + uIndex ,oVarValue=dZipFile['dstfilename'])
            SetVar(uVarName="REPMAN_ZIPREMOVEPATH[" + uIndex ,oVarValue=dZipFile['removepath'])
            uSkipFiles:str = dZipFile.get('skipfiles',None)
            if uSkipFiles is not None:
                SetVar(uVarName="REPMAN_ZIPSKIPFILES[" + uIndex, oVarValue=dZipFile['skipfiles'])
                SetVar(uVarName="REPMAN_ZIPTYPE[" + uIndex,oVarValue= "folder")
            else:
                SetVar(uVarName="REPMAN_ZIPTYPE[" + uIndex,oVarValue= "file")

            i += 1

    # noinspection PyMethodMayBeStatic
    def CreateRepVarArray(self,uBaseLocalDir:str) -> None:
        aLocalFiles:List[str] = cPath(uBaseLocalDir).GetFileList(bSubDirs=True, bFullPath=True)
        SetVar(uVarName="REPMAN_LOCALBASENAME", oVarValue=uBaseLocalDir)
        SetVar(uVarName="REPMAN_CNTFILES",      oVarValue= str(len(aLocalFiles)))
        Var_DelArray("REPMAN_LOCALFILENAMES[]")

        i:int=0
        for uLocalFile in aLocalFiles:
            uIndex:str = str(i) + "]"
            SetVar(uVarName="REPMAN_LOCALFILENAMES[" + uIndex ,oVarValue=uLocalFile)
            i += 1
