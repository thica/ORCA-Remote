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

from __future__                     import annotations
from typing                         import List
from typing                         import Dict
from typing                         import Tuple

import  mwclient
from kivy.logger                    import Logger
from ORCA.utils.LogError            import LogError
from ORCA.utils.TypeConvert         import EscapeUnicode
from ORCA.utils.Path                import cPath
from ORCA.utils.FileName            import cFileName
from ORCA.utils.LoadFile            import LoadFile
from ORCA.utils.Sleep               import fSleep

import ORCA.Globals as Globals

class cWikiTocEntry:
    """ class for a TOC Entry """
    def __init__(self):
        self.uTocTitle:str     = u''
        self.uTocReference:str = u''
    def AsListToc(self) -> str:
        return "* [[%s|%s]]" % (self.uTocReference,self.uTocTitle)
    def RemoveOrder(self) -> None:
        self.uTocTitle = self.uTocTitle[self.uTocTitle.index("=")+1:]

class cWikiPage:
    """ Class for a Wiki Page """
    def __init__(self):
        self.uContext:str           = u''
        self.uPage:str              = u''
        self.uContent:List[str]     = []
        self.uTOCTitle:str          = u''
        self.oPages:List[cWikiPage] = []
        self.uWikiApp:str           = ""
    def ParseFile(self,oFileName:cFileName,iStartLine:int=0) -> List[cWikiPage]:
        """ parses a single file """

        uContent:str
        aContent:List[str]
        uParts:List[str]
        uLine:str
        bFound:bool
        i:int=0

        if oFileName.string.endswith("__init__.py"):
            return self.oPages

        if iStartLine==0:
            Logger.debug("Reading File:"+oFileName.string)
        try:
            if oFileName.Exists():
                uContent=LoadFile(oFileName=oFileName)
                aContent=uContent.split("\n")
                bFound = False
                for  i,uLine in enumerate(aContent):
                    if i>iStartLine:
                        uLine=uLine.strip()
                        if uLine.startswith(u'WikiDoc:Doc'):
                            bFound = True
                        elif uLine.startswith(u'WikiDoc:End'):
                            self.oPages.append(self)
                            break
                        elif uLine.startswith("WikiDoc:Context:"):
                            uParts=uLine.split(":")
                            self.uContext=uParts[-1]
                        elif uLine.startswith("WikiDoc:Page:"):
                            uParts=uLine.split(":")
                            self.uPage=uParts[-1]
                            Logger.debug("Parsed Wikipage:"+self.uPage)
                        elif uLine.startswith("WikiDoc:TOCTitle:"):
                            uParts=uLine.split(":")
                            self.uTOCTitle=uParts[-1]
                        elif "'''" in uLine:
                            pass
                        elif '"""' in uLine:
                            pass
                        else:
                            if bFound:
                                self.uContent.append(uLine)
            else:
                LogError(uMsg=u'cWikiDoc:Cant find file:'+oFileName.string)

            if len(self.oPages)>0:
                oPage:cWikiPage = cWikiPage()
                oPages=oPage.ParseFile(oFileName,i)
                if len(oPages)>0:
                    self.oPages.extend(oPages)
            else:
                if iStartLine==0:
                    Logger.warning("No Wikidoc entry in file:"+oFileName.string)
            return self.oPages
        except Exception as e:
            LogError(uMsg=u'WikiDoc:Unexpected error reading file:',oException=e)
            return []

    def WriteDoc(self,uPath:cPath) -> None:
        """ writes the Wiki Doc File """

        oFileName:cFileName = cFileName(uPath) + (self.uPage+".mediawiki")
        # oFileName.Delete()
        f = open(oFileName.string, 'w')

        # _Header.md currently not working, so add it static
        if self.uWikiApp == "GITWIKI":
            f.write("[[https://github.com/thica/ORCA-Remote/blob/master/src/wikidoc/images/orca.png]]\r\n")

        for uLine in self.uContent:
            f.write(EscapeUnicode(uLine)+u"\n")
        f.close()

    def WriteWiki(self,oWiki:mwclient.Site) -> None:
        try:
            Logger.debug("Writing Page to Wiki:"+self.uPage)
            oPage = oWiki.Pages[self.uPage]
            uContent:str    = '\n'.join(self.uContent)
            oPage.save(uContent)
        except Exception as e:
            Logger.error("Error writing page:"+str(e))

    def ReplaceTocs(self,dTocs:Dict[str,List[cWikiTocEntry]]) -> None:
        """ replaces the Tocs Refs with the collected TOCs"""
        i:int
        uLine:str
        aParts:List[str]
        uContext:str
        uSortType:str
        aTocs:List[cWikiTocEntry]

        for i,uLine in enumerate(self.uContent):
            if uLine.startswith(u'WikiDoc:TOC:'):
                aParts=uLine.split(":")
                if len(aParts)==4:
                    uContext=aParts[-2]
                    uTocType=aParts[-1]
                    uSortType="unsorted"
                else:
                    uContext=aParts[-3]
                    uTocType=aParts[-2]
                    uSortType=aParts[-1]

                aTocs = dTocs.get(uContext)
                if aTocs:
                    if uSortType=="sorted":
                        aTocs=sorted(aTocs, key=lambda entry: entry.uTocTitle)
                    if uSortType=="ordered":
                        aTocs=sorted(aTocs, key=lambda entry: entry.uTocTitle)
                        for oTocEntry in aTocs:
                            oTocEntry.RemoveOrder()
                    if uTocType=="List":
                        for oTocEntry in aTocs:
                            self.uContent.insert(i,oTocEntry.AsListToc())
                            i+=1
                        self.uContent.remove(uLine)
                else:
                    LogError(uMsg=u'Wikidoc:unable to find TOCS for context:'+uContext)

    def AdjustToTargetWiki(self,oWikiDoc:cWikiDoc) -> None:
        iIndex:int
        iPos:int
        uFileName:str
        uLine:str
        uLink:str

        self.uWikiApp = oWikiDoc.uWikiApp
        if oWikiDoc.uWikiApp == "GITWIKI":
            iIndex = -1
            for uLine in self.uContent:
                # replace the git links to files in the git repo
                iIndex += 1
                iPos = uLine.find("[[File:")
                if iPos>=0:
                    uFileName = uLine[iPos+7:uLine.find("|",iPos+1)]
                    oFile = oWikiDoc.dImageFileListBase.get(uFileName)
                    if oFile is not None:
                        uLink = EscapeUnicode(oWikiDoc.uHost+oFile.unixstring[oFile.unixstring.rfind("/src/"):])
                        uLine = uLine[:iPos+2]+uLink+uLine[uLine.find("]]",iPos):]
                    else:
                        LogError(uMsg=u'Wikidoc:unable to find linked filename: [%s] [%s] [%s]' % (uFileName,uLine,self.uPage))
                # adjust syntaxhighlighting to GIT Wiki

                uLine = uLine.replace('<div style="overflow-x: auto;"><syntaxhighlight  lang="xml">', '<div style="overflow-x: auto;">\n```xml')
                uLine = uLine.replace('</syntaxhighlight></div>',"```\n</div>")
                # uLine = uLine.replace('<div style="overflow-x: auto;"><syntaxhighlight  lang="xml">', '----<div style="overflow-x: auto;"><code><nowiki>')
                # uLine = uLine.replace('</syntaxhighlight></div>',"</nowiki></code></div>\r\n----")

                if "syntaxhighlight" in uLine:
                    Logger.warning("Unsupported Syntax Highlight: [%s] [%s] " %(self.uPage,uLine))
                self.uContent[iIndex]=uLine


class cWikiDoc:
    """ Class to create the ORCA Wiki Documentation """
    def __init__(self,**kwargs):
        self.dFileList:Dict[str,cFileName]          = {}
        self.aDocs:List[cWikiPage]                  = []
        self.dTocs:Dict[str,List[cWikiTocEntry]]    = {}
        self.dImageFileList:Dict[str,cFileName]     = {}
        self.dImageFileListBase:Dict[str,cFileName] = {}
        self.oSourcePath:cPath                      = cPath(Globals.oPathRoot) + "ORCA"

        self.uHost:str                              = kwargs["Host"]
        self.uWikiPath:str                          = kwargs["WikiPath"]
        self.uUser:str                              = kwargs["User"]
        self.uPassword:str                          = kwargs["Password"]
        self.oWikiTargetFolder:cPath                = cPath(kwargs["WikiTargetFolder"])
        self.uWikiApp:str                           = kwargs["WikiApp"]

    def Run(self) -> None:
        """ Collects all Wiki Docs """
        self.CleanUp()
        #self.CollectFile(self.uSourcePath + "/widgets/wikidoc.txt")
        self.CollectFile(oFile  = cFileName(self.oSourcePath + "widgets") + "Base.py")
        self.CollectFiles(oPath = self.oSourcePath + "widgets")
        self.CollectFiles(oPath = self.oSourcePath + "actions")
        self.CollectFiles(oPath = Globals.oPathCodesets, bSubDirs=True)
        self.CollectFiles(oPath = Globals.oPathInterface, bSubDirs=True)
        self.CollectFiles(oPath = Globals.oPathScripts, bSubDirs=True)
        self.CollectFiles(oPath = Globals.oPathDefinitionRoot, bSubDirs=True)
        self.CollectFiles(oPath = Globals.oPathWizardTemplates, bSubDirs=True)
        self.CollectFiles(oPath = Globals.oPathRoot + "wikidoc", bSubDirs=True)

        self.CollectImages(oPath= Globals.oPathRoot + "wikidoc/images", bSubDirs=True)
        self.CollectImages(oPath= Globals.oPathDefinitionRoot, bSubDirs=True)
        self.CollectImages(oPath= Globals.oPathWizardTemplates, bSubDirs=True)

        self.ParseFiles()
        self.ReplaceTocs()
        self.AdjustToTargetWiki()
        self.WriteDocs()
        if self.uWikiApp == "MEDIAWIKI":
            self.WriteWikiPages()

    def CollectImages(self,oPath:cPath,bSubDirs:bool) -> None:
        """ adds all files in a folder to the list of images """
        aFiles:List[str] = oPath.GetFileList(bSubDirs=bSubDirs,bFullPath=True)
        tFilter:Tuple = (".jpg",".jpeg",".bmp",".png")

        for uFile in aFiles:
            if "wikidoc" in uFile:
                if uFile.endswith(tFilter):
                    oFile:cFileName = cFileName(u'').ImportFullPath(uFnFullName=uFile)
                    self.dImageFileList[oFile.string]       = oFile
                    self.dImageFileListBase[oFile.basename] = oFile

    def WriteWikiPages(self) -> None:
        """ Write all wiki entries to wikipedia """

        oSite:mwclient.Site
        uImageKey:str
        oPage:cWikiPage

        try:
            oSite = mwclient.Site(self.uHost,path= self.uWikiPath,force_login=True)
            oSite.login(self.uUser,self.uPassword)

            try:
                for uImageKey in self.dImageFileList:
                    oFnImage:cFileName = self.dImageFileList[uImageKey]
                    Logger.debug("Uploading Image:" + oFnImage.string)
                    # noinspection PyTypeChecker
                    jRec:Dict=oSite.upload(file=open(oFnImage.string, 'rb'), filename=oFnImage.basename, description='')
                    # print (jRec["warnings"].keys()[0]," ",jRec["warnings"][jRec["warnings"].keys()[0]])
                    dWarnings:Dict = jRec.get("warnings")
                    if dWarnings is not None:
                        if "was-deleted" in dWarnings.keys():
                            Logger.error("You need Undelete File in Mediawiki:"+oFnImage.basename)
                        if "exists" in dWarnings.keys():
                            # noinspection PyTypeChecker
                            oSite.upload(file=open(oFnImage.string, 'rb'), filename=oFnImage.basename, description='', ignore=True)

            except Exception as e:
                Logger.error("Error writing image:" + str(e))


            for oPage in self.aDocs:
                if oPage.uPage:
                    oPage.WriteWiki(oSite)
                    fSleep(fSeconds=1.0)

        except Exception as e:
            Logger.error("Error writing page:"+str(e))

    # noinspection PyMethodMayBeStatic
    def CleanUp(self) -> None:
        Globals.oPathTmp.Clear()

    def CollectFile(self,oFile:cFileName) -> None:
        """ Adds a file to list of sources """
        self.dFileList[oFile.string]=oFile
    def CollectFiles(self,oPath, bSubDirs=False):
        """ adds all files in a folder to the list of sources """
        aFiles=oPath.GetFileList(bSubDirs=bSubDirs,bFullPath=True)
        for uFile in aFiles:
            oFile=cFileName(u'').ImportFullPath(uFnFullName=uFile)
            if oFile.string.endswith(".py") or oFile.string.endswith(".txt"):
                self.dFileList[oFile.string]=oFile

    def ParseFiles(self) -> None:
        """ Parses all added files """
        for uFileKey in self.dFileList:
            self.ParseFile(self.dFileList[uFileKey])

    def ReplaceTocs(self) -> None:
        """ Replace all TOC references """
        oPage:cWikiPage
        for oPage in self.aDocs:
            oPage.ReplaceTocs(self.dTocs)

    def AdjustToTargetWiki(self) -> None:
        """ Adjust to target wiki (currently GIT wiki) """
        oPage:cWikiPage
        for oPage in self.aDocs:
            oPage.AdjustToTargetWiki(self)

        if self.uWikiApp=="GITWIKI":
            oWikiPath:cPath = Globals.oPathRoot + "wikidoc"
            aFiles:List[str] = oWikiPath.GetFileList(bSubDirs=False,bFullPath=True)
            for uFile in aFiles:
                if uFile.endswith(".md"):
                    oSourceFileName:cFileName = cFileName()
                    oSourceFileName.ImportFullPath(uFnFullName=uFile)
                    oSourceFileName.Copy(oNewFile=self.oWikiTargetFolder)


    def WriteDocs(self) -> None:
        """ Write all wiki entries as txt file """
        oPage:cWikiPage
        for oPage in self.aDocs:
            oPage.WriteDoc(self.oWikiTargetFolder)

    def AddToc(self,oTocReference:cWikiTocEntry,uContext:str) -> None:
        """ adds a toc reference to the list of all Tocs """
        aTocs:List[cWikiTocEntry] = self.dTocs.get(uContext)
        if aTocs is None:
            self.dTocs[uContext]=[]
        self.dTocs[uContext].append(oTocReference)

    def ParseFile(self,oFileName:cFileName) -> None:
        """ Parses a single file """
        oPage:cWikiPage=cWikiPage()
        aPages:List[cWikiPage]=oPage.ParseFile(oFileName)
        for oFoundPage in aPages:
            self.aDocs.append(oFoundPage)
            oToc:cWikiTocEntry=cWikiTocEntry()
            oToc.uTocReference=oFoundPage.uPage
            oToc.uTocTitle    =oFoundPage.uTOCTitle
            self.AddToc(oToc,oFoundPage.uContext)
            Logger.debug("Found Page: %s (%s)" % (oFoundPage.uPage,oFileName))




