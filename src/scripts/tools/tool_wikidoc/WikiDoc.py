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

import  mwclient
from kivy.logger                    import Logger
from ORCA.utils.LogError            import LogError
from ORCA.utils.TypeConvert         import EscapeUnicode
from ORCA.utils.Path                import cPath
from ORCA.utils.FileName            import cFileName
from ORCA.utils.LoadFile            import LoadFile
from ORCA.utils.TypeConvert         import ToUnicode
from ORCA.utils.Sleep               import fSleep

import ORCA.Globals as Globals

class cWikiTocEntry(object):
    """ class for a TOC Entry """
    def __init__(self):
        self.uTocTitle     = u''
        self.uTocReference = u''
    def AsListToc(self):
        return "* [[%s|%s]]" % (self.uTocReference,self.uTocTitle)
    def RemoveOrder(self):
        self.uTocTitle = self.uTocTitle[self.uTocTitle.index("=")+1:]

class cWikiPage(object):
    """ Class for a Wiki Page """
    def __init__(self):
        self.uContext  = u''
        self.uPage     = u''
        self.uContent  = []
        self.uTOCTitle = u''
        self.oPages    = []
        self.uWikiApp  = ""
    def ParseFile(self,oFileName,iStartLine=0):
        """ parses a single file """

        i=0

        if oFileName.string.endswith("__init__.py"):
            return self.oPages

        if iStartLine==0:
            Logger.debug("Reading File:"+oFileName.string)
        try:
            if oFileName.Exists():
                uContent=ToUnicode(LoadFile(oFileName))
                aContent=uContent.split("\n")
                bFound = False
                for  i,uLine in enumerate(aContent):
                    if i>iStartLine:
                        uLine=uLine.strip()
                        if uLine.startswith(u'WikiDoc:Doc'):
                            bFound = True
                        elif uLine.startswith(u'WikiDoc:End'):
                            bFound = False
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
                LogError(u'cWikiDoc:Cant find file:'+oFileName.string)

            if len(self.oPages)>0:
                oPage=cWikiPage()
                oPages=oPage.ParseFile(oFileName,i)
                if len(oPages)>0:
                    self.oPages.extend(oPages)
            else:
                if iStartLine==0:
                    Logger.warning("No Wikidoc entry in file:"+oFileName.string)
            return self.oPages
        except Exception as e:
            LogError(u'WikiDoc:Unexpected error reading file:',e)
            return []

    def WriteDoc(self,uPath):
        """ writes the Wiki Doc File """

        oFileName=cFileName(uPath) + (self.uPage+".mediawiki")
        # oFileName.Delete()
        f = open(oFileName.string, 'w')

        # _Header.md currently not working, so add it static
        if self.uWikiApp == "GITWIKI":
            f.write("[[https://github.com/thica/ORCA-Remote/blob/master/src/wikidoc/images/orca.png]]\r\n")

        for uLine in self.uContent:
            f.write(EscapeUnicode(uLine)+u"\n")
        f.close()

    def WriteWiki(self,oWiki):
        try:
            Logger.debug("Writing Page to Wiki:"+self.uPage)
            oPage = oWiki.Pages[self.uPage]
            uContent='\n'.join(self.uContent)
            jRet=oPage.save(uContent)
        except Exception as e:
            Logger.error("Error writing page:"+str(e))

    def ReplaceTocs(self,dTocs):
        """ replaces the Tocs Refs with the collected TOCs"""
        for i,uLine in enumerate(self.uContent):
            if uLine.startswith(u'WikiDoc:TOC:'):
                uParts=uLine.split(":")
                if len(uParts)==4:
                    uContext=uParts[-2]
                    uTocType=uParts[-1]
                    uSortType="unsorted"
                else:
                    uContext=uParts[-3]
                    uTocType=uParts[-2]
                    uSortType=uParts[-1]

                aTocs=dTocs.get(uContext)
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
                    LogError(u'Wikidoc:unable to find TOCS for context:'+uContext)

    def AdjustToTargetWiki(self,oWikiDoc):
        self.uWikiApp = oWikiDoc.uWikiApp
        if oWikiDoc.uWikiApp == "GITWIKI":
            iIndex = -1
            for uLine in self.uContent:
                # replace the git links to files in the git repo
                iIndex = iIndex +1
                iPos = uLine.find("[[File:")
                if iPos>=0:
                    uFileName = uLine[iPos+7:uLine.find("|",iPos+1)]
                    oFile = oWikiDoc.dImageFileListBase.get(uFileName)
                    if oFile is not None:
                        uLink = EscapeUnicode(oWikiDoc.uHost+oFile.unixstring[oFile.unixstring.rfind("/src/"):])
                        uLine = uLine[:iPos+2]+uLink+uLine[uLine.find("]]",iPos):]
                    else:
                        LogError(u'Wikidoc:unable to find linked filename: [%s] [%s] [%s]' % (uFileName,uLine,self.uPage))
                # adjust syntaxhighlighting to GIT Wiki

                uLine = uLine.replace('<div style="overflow-x: auto;"><syntaxhighlight  lang="xml">', '<div style="overflow-x: auto;">\r\n```xml')
                uLine = uLine.replace('</syntaxhighlight></div>',"```\r\n</div>")
                # uLine = uLine.replace('<div style="overflow-x: auto;"><syntaxhighlight  lang="xml">', '----<div style="overflow-x: auto;"><code><nowiki>')
                # uLine = uLine.replace('</syntaxhighlight></div>',"</nowiki></code></div>\r\n----")

                if "syntaxhighlight" in uLine:
                    Logger.warning("Unsupported Syntax Highlight: [%s] [%s] " %(self.uPage,uLine))
                self.uContent[iIndex]=uLine


class cWikiDoc(object):
    """ Class to create the ORCA Wiki Documentation """
    def __init__(self,**kwargs):
        self.dFileList          = {}
        self.aDocs              = []
        self.dTocs              = {}
        self.dImageFileList     = {}
        self.dImageFileListBase = {}
        self.oSourcePath        = cPath(Globals.oPathRoot) + "ORCA"

        self.uHost              = kwargs["Host"]
        self.uWikiPath          = kwargs["WikiPath"]
        self.uUser              = kwargs["User"]
        self.uPassword          = kwargs["Password"]
        self.oWikiTargetFolder  = cPath(kwargs["WikiTargetFolder"])
        self.uWikiApp           = kwargs["WikiApp"]

    def Run(self):
        """ Collects all Wiki Docs """
        self.CleanUp()
        #self.CollectFile(self.uSourcePath + "/widgets/wikidoc.txt")
        self.CollectFile(oFile  = cFileName(self.oSourcePath + "widgets") + "Base.py")
        self.CollectFiles(oPath = self.oSourcePath + "widgets")
        self.CollectFiles(oPath = self.oSourcePath + "actions")
        self.CollectFiles(oPath = Globals.oPathInterface, bSubDirs=True)
        self.CollectFiles(oPath = Globals.oPathScripts, bSubDirs=True)
        self.CollectFiles(oPath = Globals.oPathDefinitionRoot, bSubDirs=True)
        self.CollectFiles(oPath = Globals.oPathRoot + "wikidoc", bSubDirs=True)
        self.CollectImages(oPath= Globals.oPathRoot + "wikidoc/images", bSubDirs=True)
        self.CollectImages(oPath= Globals.oPathRoot + "definitions", bSubDirs=True)

        self.ParseFiles()
        self.ReplaceTocs()
        self.AdjustToTargetWiki()
        self.WriteDocs()
        if self.uWikiApp == "MEDIAWIKI":
            self.WriteWikiPages()

    def CollectImages(self,oPath,bSubDirs):
        """ adds all files in a folder to the list of images """
        aFiles  = oPath.GetFileList(bSubDirs=bSubDirs,bFullPath=True)
        tFilter = (".jpg",".jpeg",".bmp",".png")

        for uFile in aFiles:
            if "wikidoc" in uFile:
                if uFile.endswith(tFilter):
                    oFile=cFileName(u'').ImportFullPath(uFile)
                    self.dImageFileList[oFile.string] = oFile
                    self.dImageFileListBase[oFile.basename] = oFile

    def WriteWikiPages(self):
        """ Write all wiki entries to wikipedia """

        oSite     = None

        try:
            oSite = mwclient.Site(self.uHost,path= self.uWikiPath,force_login=True)
            oSite.login(self.uUser,self.uPassword)

            try:
                for uImageKey in self.dImageFileList:
                    oFnImage = self.dImageFileList[uImageKey]
                    Logger.debug("Uploading Image:" + oFnImage.string)
                    jRec=oSite.upload(open(oFnImage.string, 'rb'), filename=oFnImage.basename, description='')
                    # print (jRec["warnings"].keys()[0]," ",jRec["warnings"][jRec["warnings"].keys()[0]])
                    dWarnings = jRec.get("warnings")
                    if dWarnings is not None:
                        if "was-deleted" in dWarnings.keys()[0]:
                            Logger.error("You need Undelete File in Mediawiki:"+oFnImage.basename)
                        if "exists" in dWarnings.keys()[0]:
                            jRec = oSite.upload(open(oFnImage.string, 'rb'), filename=oFnImage.basename, description='', ignore=True)

            except Exception as e:
                Logger.error("Error writing image:" + str(e))

            for oPage in self.aDocs:
                if oPage.uPage:
                    oPage.WriteWiki(oSite)
                    fSleep(1.0)

        except Exception as e:
            Logger.error("Error writing page:"+str(e))



    def CleanUp(self):
        Globals.oPathTmp.Clear()

    def CollectFile(self,oFile):
        """ Adds a file to list of sources """
        self.dFileList[oFile.string]=oFile
    def CollectFiles(self,oPath, bSubDirs=False):
        """ adds all files in a folder to the list of sources """
        aFiles=oPath.GetFileList(bSubDirs=bSubDirs,bFullPath=True)
        for uFile in aFiles:
            oFile=cFileName(u'').ImportFullPath(uFile)
            if oFile.string.endswith(".py") or oFile.string.endswith(".txt"):
                self.dFileList[oFile.string]=oFile

    def ParseFiles(self):
        """ Parses all added files """
        for uFileKey in self.dFileList:
            self.ParseFile(self.dFileList[uFileKey])

    def ReplaceTocs(self):
        """ Replace all TOC references """
        for oPage in self.aDocs:
            oPage.ReplaceTocs(self.dTocs)

    def AdjustToTargetWiki(self):
        """ Adjust to target wiki (currently GIT wiki( """
        for oPage in self.aDocs:
            oPage.AdjustToTargetWiki(self)

        if self.uWikiApp=="GITWIKI":
            oWikiPath = Globals.oPathRoot + "wikidoc"
            aFiles = oWikiPath.GetFileList(bSubDirs=False,bFullPath=True)
            for uFile in aFiles:
                if uFile.endswith(".md"):
                    oSourceFileName = cFileName()
                    oSourceFileName.ImportFullPath(uFile)
                    oSourceFileName.Copy(self.oWikiTargetFolder)


    def WriteDocs(self):
        """ Write all wiki entries as txt file """
        for oPage in self.aDocs:
            oPage.WriteDoc(self.oWikiTargetFolder)

    def AddToc(self,oTocReference,uContext):
        """ adds a toc reference to the list of all Tocs """
        aTocs = self.dTocs.get(uContext)
        if aTocs is None:
            self.dTocs[uContext]=[]
        self.dTocs[uContext].append(oTocReference)

    def ParseFile(self,oFileName):
        """ Parses a single file """
        oPage=cWikiPage()
        oPages=oPage.ParseFile(oFileName)
        for oFoundPage in oPages:
            self.aDocs.append(oFoundPage)
            oToc=cWikiTocEntry()
            oToc.uTocReference=oFoundPage.uPage
            oToc.uTocTitle    =oFoundPage.uTOCTitle
            self.AddToc(oToc,oFoundPage.uContext)
            Logger.debug("Found Page: %s (%s)" % (oFoundPage.uPage,oFileName))




