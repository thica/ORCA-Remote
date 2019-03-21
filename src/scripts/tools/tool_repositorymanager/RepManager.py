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

import os

from xml.etree.ElementTree  import Element
from xml.etree.ElementTree  import SubElement

from kivy.logger            import Logger
from kivy.network.urlrequest import UrlRequest
from kivy.compat            import PY2


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
from ORCA.RepManagerEntry   import cRepManagerEntry

import ORCA.Globals as Globals

oRepositoryManager = None

def RepositoryManager(oPathRepSource):
    """ starts RepositoryManager, we make it global to avoid wrong garbage collecteio """
    global oRepositoryManager
    oRepositoryManager=cRepositoryManager(oPathRepSource)
    oRepositoryManager.CollectAndUpload()

def CreateRepVarArray(uBaseLocalDir):
    global oRepositoryManager
    if oRepositoryManager:
        oRepositoryManager.CreateRepVarArray(uBaseLocalDir)

class cRepositoryManager(object):
    """ The Main repository manager class, which uploads all reps to the cloud """
    def __init__(self,oPathRepSource):
        super(cRepositoryManager, self).__init__()
        self.aFiles                           = []
        self.oRepManagerEntries               = []
        self.aZipFiles                        = []
        self.oPathRepSource                   = oPathRepSource

    def CollectAndUpload(self):
        """ Collects all Reps and uploads them """
        try:
            oPath= Globals.oPathTmp + "RepManager"
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
            uMsg=LogError('Critical failure on Repository Manager ...' ,e)
            ShowErrorPopUp(uMessage=uMsg)

    def GetOthers(self):
        """ Gets all others reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        self.aFiles=(self.oPathRepSource + 'repositories/orca-remote/repositories/others').GetFileList(bSubDirs = False, bFullPath = True)
        for uFn in self.aFiles:
            oRepManagerEntry=cRepManagerEntry(uFn)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.oRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Resource not ready for Repository Manager, skipped: '+uFn)
        self.SaveRepositoryXML('others','Various ORCA resources')

    def GetFonts(self):
        """ Gets all others reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        aFontsFolders = Globals.oPathFonts.GetFolderList(bFullPath=True)
        for uFontFolder in aFontsFolders:
            oFnFontDefinition = cFileName(cPath(uFontFolder)) + "fonts.xml"
            oRepManagerEntry = cRepManagerEntry(oFnFontDefinition)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.oRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Font not ready for Repository Manager, skipped: '+oFnFontDefinition)
        self.SaveRepositoryXML('fonts','Font Resources')


    #todo: change getCodesets, getskinns, getdefinitions, getinterfaces to uRepSourcePath

    def GetCodesets(self):
        """ Gets all codeset reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        self.aFiles=Globals.oPathCodesets.GetFileList(bSubDirs = True, bFullPath = True)
        for uFn in self.aFiles:
            if uFn.lower().endswith('.xml'):
                oRepManagerEntry=cRepManagerEntry(uFn)
                if oRepManagerEntry.ParseFromXML():
                    if not oRepManagerEntry.oRepEntry.bSkip:
                        self.oRepManagerEntries.append(oRepManagerEntry)
                else:
                    Logger.warning('Codeset not ready for Repository Manager, skipped: '+uFn)
        self.SaveRepositoryXML('codesets','Orca Genuine Codesets')

    def GetSounds(self):
        """ Gets all sounds reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        for uSound in Globals.oSound.aSoundsList:
            oFnSound=cFileName(Globals.oPathSoundsRoot + uSound) +"sounds.xml"
            oRepManagerEntry=cRepManagerEntry(oFnSound)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.oRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Soundset not ready for Repository Manager, skipped: '+oFnSound)
        self.SaveRepositoryXML('sounds','Orca Genuine Sounds')

    def GetDefinitions(self):
        """ Gets all definition reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        for uDefinitionName in Globals.aDefinitionList:
            oFnFile=cFileName().ImportFullPath('%s/definitions/%s/definition.xml' % (Globals.oPathRoot.string, uDefinitionName))
            oRepManagerEntry=cRepManagerEntry(oFnFile)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.oRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Definition not ready for Repository Manager, skipped: '+oFnFile)
        self.SaveRepositoryXML('definitions','Orca Genuine Definitions')

    def GetLanguages(self):
        """ Gets all Language reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        for uLanguage in Globals.aLanguageList:
            oFn=cFileName().ImportFullPath('%s/languages/%s/strings.xml' % (Globals.oPathRoot.string, uLanguage))
            oRepManagerEntry=cRepManagerEntry(oFn)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.oRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Language not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('languages','Orca Genuine Language Files')

    def GetInterfaces(self):
        """ Gets all interface reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        for uInterFaceName in Globals.oInterFaces.oInterfaceList:
            oFn=cFileName().ImportFullPath('%s/interfaces/%s/interface.py' % (Globals.oPathRoot.string, uInterFaceName))
            oRepManagerEntry=cRepManagerEntry(oFn)
            if oRepManagerEntry.ParseFromSourceFile():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.oRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Interface not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('interfaces','Orca Genuine Interfaces')

    def GetScripts(self):
        """ Gets all scripts reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        for uScriptName in Globals.oScripts.dScriptPathList:
            oFn=cFileName(Globals.oScripts.dScriptPathList[uScriptName])+'script.py'
            oRepManagerEntry=cRepManagerEntry(oFn)
            if oRepManagerEntry.ParseFromSourceFile():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.oRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Script not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('scripts','Orca Genuine Scripts')

    def GetSkins(self):
        """ Gets all skins reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        for uSkinName in Globals.aSkinList:
            oFn=cFileName().ImportFullPath('%s/skins/%s/skin.xml' % (Globals.oPathRoot.string, uSkinName))
            oRepManagerEntry=cRepManagerEntry(oFn)
            if oRepManagerEntry.ParseFromXML():
                if not oRepManagerEntry.oRepEntry.bSkip:
                    self.oRepManagerEntries.append(oRepManagerEntry)
            else:
                Logger.warning('Skin not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('skins','Orca Genuine Skins')

    def GetWizardTemplates(self):
        """ Gets all wizard reps """
        del self.aFiles[:]
        del self.oRepManagerEntries[:]
        aDirs=(Globals.oPathRoot + u'wizard templates').GetFolderList()
        for uDirName in aDirs:
            aDirsSub=(Globals.oPathRoot + (u'wizard templates/' + uDirName)).GetFolderList()
            for uDirsSub in aDirsSub:
                oFn=cFileName(Globals.oPathRoot + (u'wizard templates/' + uDirName + "/" + uDirsSub)) +  (uDirsSub + ".xml")
                oRepManagerEntry=cRepManagerEntry(oFn)
                if oRepManagerEntry.ParseFromXML():
                    if not oRepManagerEntry.oRepEntry.bSkip:
                        self.oRepManagerEntries.append(oRepManagerEntry)
                else:
                    Logger.warning('Wizard Template not ready for Repository Manager, skipped: '+oFn)
        self.SaveRepositoryXML('wizard templates','Wizard Templates')

    def SaveRepositoryXML(self,uType,uDescription):
        """ Saves the main repository directory xml """
        oPath= Globals.oPathTmp + "RepManager"
        oPath.Create()
        oPath=oPath+"repositories"
        oPath.Create()
        oPath=oPath+uType
        oPath.Create()
        oFnXml=cFileName(oPath) +'repository.xml'

        oXMLRoot    = Element('repository')
        oVal        = SubElement(oXMLRoot,'version')
        oVal.text   = '1.00'
        oVal        = SubElement(oXMLRoot,'type')
        oVal.text   = uType
        oVal        = SubElement(oXMLRoot,'description')
        oVal.text   = uDescription

        oXMLEntries = SubElement(oXMLRoot,'entries')

        for oEntry in self.oRepManagerEntries:
            Logger.debug ('Saving Repository-Entry [%s]' % oEntry.oFnEntry.string)

            oEntry.oRepEntry.WriteToXMLNode(oXMLEntries)
            for oSource in oEntry.oRepEntry.aSources:
                bZipParentDir= cPath.CheckIsDir(oSource.uLocal)
                # Create according Zip
                if bZipParentDir:
                    uUpper1=os.path.split(os.path.abspath(oSource.uSourceFile))[0]
                    uUpper2=os.path.split(os.path.abspath(uUpper1))[0]
                    uUpper=uUpper1[len(uUpper2)+1:]
                    uUpper=os.path.basename(oSource.uLocal)
                    uUpper=os.path.basename(oSource.uSourceFile)
                    uFinalPath=uType
                    oDest= cFileName().ImportFullPath('%s/RepManager/repositories/%s/%s' % (Globals.oPathTmp.string, uFinalPath, uUpper))
                    uUpper1=os.path.split(os.path.abspath(oSource.uLocal))[0]
                    uRoot = '%s/%s/' % (Globals.oPathRoot.string, uType)
                    uRoot = AdjustPathToOs(ReplaceVars(uUpper1)+'/')
                    self.aZipFiles.append({'filename':oSource.uLocal,'dstfilename':oDest.string, 'removepath':uRoot, 'skipfiles':ToUnicode(oEntry.oRepEntry.aSkipFileNames)})
                else:
                    uDest = AdjustPathToOs('%s/RepManager/repositories/%s/%s.zip' % (Globals.oPathTmp.string, uType, os.path.splitext(os.path.basename(oSource.uLocal))[0]))
                    uRoot = AdjustPathToOs(Globals.oPathRoot.string + "/" + oSource.uTargetPath)
                    self.aZipFiles.append({'filename':oSource.uLocal,'dstfilename':uDest, 'removepath':uRoot})

        oFSFile = open(oFnXml.string, 'w')
        uContent=XMLPrettify(oXMLRoot)
        uContent=ReplaceVars(uContent)
        if PY2:
            oFSFile.write(uContent.encode('utf8'))
        else:
            oFSFile.write(EscapeUnicode(uContent))
        oFSFile.close()

    def CreateRepository(self):
        self.CreateZipVarArray()
        SetVar(uVarName="REPMAN_BASELOCALDIR", oVarValue=(Globals.oPathTmp + "RepManager").string)
        Globals.oTheScreen.AddActionToQueue([{'string': 'call Create Repository'}])
        return

    def CreateZipVarArray(self):
        SetVar(uVarName="REPMAN_ZIPCNTFILES",  oVarValue= str(len(self.aZipFiles)))
        Var_DelArray("REPMAN_ZIPSOUREFILENAMES[]")
        Var_DelArray("REPMAN_ZIPDESTFILENAMES[]")
        Var_DelArray("REPMAN_ZIPREMOVEPATH[]")
        Var_DelArray("REPMAN_ZIPSKIPFILES[]")
        Var_DelArray("REPMAN_ZIPTYPE[]")

        i=0
        for dZipFile in self.aZipFiles:
            uIndex = str(i) + "]"
            SetVar(uVarName="REPMAN_ZIPSOURCEFILENAMES[" + uIndex ,oVarValue=dZipFile['filename'])
            SetVar(uVarName="REPMAN_ZIPDESTFILENAMES[" + uIndex ,oVarValue=dZipFile['dstfilename'])
            SetVar(uVarName="REPMAN_ZIPREMOVEPATH[" + uIndex ,oVarValue=dZipFile['removepath'])
            uSkipFiles = dZipFile.get('skipfiles',None)
            if uSkipFiles is not None:
                SetVar(uVarName="REPMAN_ZIPSKIPFILES[" + uIndex, oVarValue=dZipFile['skipfiles'])
                SetVar(uVarName="REPMAN_ZIPTYPE[" + uIndex,oVarValue= "folder")
            else:
                SetVar(uVarName="REPMAN_ZIPTYPE[" + uIndex,oVarValue= "file")

            i=i+1

    def CreateRepVarArray(self,uBaseLocalDir):
        aLocalFiles = cPath(uBaseLocalDir).GetFileList(bSubDirs=True, bFullPath=True)
        SetVar(uVarName="REPMAN_LOCALBASENAME", oVarValue=uBaseLocalDir)
        SetVar(uVarName="REPMAN_CNTFILES",      oVarValue= str(len(aLocalFiles)))
        Var_DelArray("REPMAN_LOCALFILENAMES[]")

        i=0
        for uLocalFile in aLocalFiles:
            uIndex = str(i) + "]"
            SetVar(uVarName="REPMAN_LOCALFILENAMES[" + uIndex ,oVarValue=uLocalFile)
            i=i+1


def GetYoutubeRTSP(uID):
    """ unused stuff """
    video_id = "_iuukyjCz74"
    gdata = "http://gdata.youtube.com/feeds/api/videos/"
    oWeb         = UrlRequest(gdata+video_id,on_success=YTOnSuccess)
    return oWeb

def YTOnSuccess(request,result):
    """ unused stuff """
    u1="rtsp:"+result.split('rtsp:')[1].split('.3gp')[0] + ".3gp"
    return u1


