# -*- coding: utf-8 -*-

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
from ORCA.utils.Sleep               import fSleep

from ORCA.Globals import Globals

class cWikiTocEntry:
    """ class for a TOC Entry """
    def __init__(self):
        self.uTocTitle:str     = ''
        self.uTocReference:str = ''
    def AsListToc(self) -> str:
        return '* [[%s|%s]]' % (self.uTocReference,self.uTocTitle)
    def RemoveOrder(self) -> None:
        self.uTocTitle = self.uTocTitle[self.uTocTitle.index('=')+1:]

class cRstPage:
    """ Class for a Wiki Page """
    def __init__(self):
        self.uContext:str           = ''
        self.uPage:str              = ''
        self.uContent:List[str]     = []
        self.uTOCTitle:str          = ''
        self.oPages:List[cRstPage] = []
        self.uWikiApp:str           = ''
    def ParseFile(self,oFileName:cFileName,iStartLine:int=0) -> List[cRstPage]:
        """ parses a single file """

        uContent:str
        aContent:List[str]
        uParts:List[str]
        uLine:str
        bFound:bool
        i:int=0
        iCol:int =0
        bCodeBlock:bool = False
        bFirst:bool=True
        bTable:bool=False
        bHeader:bool=False
        aHeader:List[List[str]] = []
        aHeaderLen:List[int] = []

        if str(oFileName).endswith('__init__.py'):
            return self.oPages

        if iStartLine==0:
            Logger.debug(f'Reading File: {oFileName}')
        try:
            if oFileName.Exists():
                uContent=oFileName.Load()
                aContent=uContent.split('\n')
                bFound = False
                for  i,uLine in enumerate(aContent):
                    if i>iStartLine:
                        uLine=uLine.strip()
                        if uLine.startswith('WikiDoc:Doc'):
                            bFound = True
                            self.uContent.append('.. '+uLine)
                            self.uContent.append('')
                        elif uLine.startswith('WikiDoc:End'):
                            self.uContent.append('.. '+uLine)
                            self.uContent.append('')
                            self.oPages.append(self)
                            break
                        elif "'''" in uLine:
                            pass
                        elif '"""' in uLine:
                            pass
                        else:
                            if bFound:
                                if uLine.startswith('WikiDoc:Context:'):
                                    self.uContent[0] = self.uContent[0] + " " + uLine.split(":", 1)[-1]
                                    self.uContext = uLine.split(":")[-1]
                                    continue
                                elif uLine.startswith('WikiDoc:Page:'):
                                    self.uContent[0] = self.uContent[0] + " " + uLine.split(":", 1)[-1]
                                    uParts = uLine.split(':')
                                    self.uPage = uParts[-1]
                                    Logger.debug('Parsed Rstpage:' + self.uPage)
                                    continue
                                elif uLine.startswith('WikiDoc:TOCTitle:'):
                                    self.uContent[0] = self.uContent[0] + ' ' + uLine.split(':', 1)[-1]
                                    uParts = uLine.split(':')
                                    self.uTOCTitle = uParts[-1]
                                    continue
                                elif uLine.startswith('<div') and 'xml' in uLine:
                                    self.uContent.append('')
                                    self.uContent.append('.. code-block:: XML')
                                    self.uContent.append('    :linenos:')
                                    self.uContent.append('')
                                    bCodeBlock=True
                                    continue
                                elif uLine.endswith('</div>') and not uLine.startswith('|}'):
                                    bCodeBlock=False
                                    continue
                                elif uLine.startswith('<div') and not 'xml' in uLine:
                                    continue
                                elif uLine.startswith('{|'):
                                    bTable=True
                                    bHeader=True
                                    del aHeader[:]
                                    aHeader.append([])
                                    continue
                                elif uLine.startswith("!") and bHeader:
                                    aHeader[0].append(uLine.split("|",1)[-1].strip())
                                    continue
                                elif uLine.startswith("|-") and bHeader:
                                    aHeader.append([])
                                    iCol=0
                                    bHeader=False
                                    continue
                                elif uLine.startswith("|-") and not bHeader:
                                    iCol=0
                                    aHeader.append([])
                                    continue
                                elif uLine.startswith('|}') and bTable:
                                    bTable=False

                                    iRow:int=0
                                    iCol:int=0
                                    for iRow in range(len(aHeader)):
                                        for iCol in range(len(aHeader[iRow])):
                                            if aHeader[iRow][iCol].startswith("*"):
                                                aHeader[iRow][iCol]=" -"+aHeader[iRow][iCol][1:]


                                    iIndex:int=0
                                    aHeaderLen =[0] * len(aHeader[0])
                                    for aSub in aHeader:
                                        iIndex=0
                                        for aSubSub in aSub:
                                            aHeaderLen[iIndex] = max([len(aSubSub),aHeaderLen[iIndex]])
                                            iIndex=iIndex+1
                                    uTrim=''
                                    for uLen in aHeaderLen:
                                        uTrim=uTrim+'='*uLen+' '
                                    self.uContent.append('')
                                    self.uContent.append(uTrim.strip())

                                    uLine=''
                                    iIndex:int=0
                                    for uTmp in aHeader[0]:
                                        uLine=uLine+uTmp.center(aHeaderLen[iIndex])+' '
                                    self.uContent.append(uLine[:-1])

                                    uTrim = ''
                                    for uLen in aHeaderLen:
                                        uTrim = uTrim + '-' * uLen + ' '
                                    self.uContent.append(uTrim.strip())

                                    iIndex:int=0
                                    for aLine in aHeader[1:]:
                                        uLine = ''
                                        uTmp:str
                                        for uTmp in aLine:
                                            uLine=uLine+ uTmp.ljust(aHeaderLen[iIndex])+" "
                                        self.uContent.append(uLine[:-1])

                                    uTrim=''
                                    for uLen in aHeaderLen:
                                        uTrim=uTrim+'='*uLen+' '


                                    self.uContent.append(uTrim)
                                    continue
                                elif uLine.startswith("|") and bTable:
                                    aHeader[-1].append(uLine.split("|",1)[-1].strip())
                                    iCol=iCol+1
                                    continue
                                elif uLine.startswith('=') and uLine.endswith('='):
                                    uLine=uLine[2:-2].strip()
                                    self.uContent.append(uLine)
                                    self.uContent.append('='*len(uLine))
                                    self.uContent.append('')
                                    continue
                                if bTable:
                                    aHeader.append([])
                                    while len(aHeader[-1]) < iCol:
                                        aHeader[-1].append('')
                                    aHeader[-1][iCol-1]=uLine
                                    continue

                                else:
                                    uIndent=''
                                    if bCodeBlock:
                                        uIndent=' '*4
                                    if bFirst:
                                        bFirst=False
                                        uIndent=''

                                    self.uContent.append(uIndent+uLine)
            else:
                LogError(uMsg=f'cWikiDoc:Cant find file: {oFileName}')

            if len(self.oPages)>0:
                oPage:cRstPage = cRstPage()
                oPages=oPage.ParseFile(oFileName,i)
                if len(oPages)>0:
                    self.oPages.extend(oPages)
            else:
                if iStartLine==0:
                    Logger.warning(f'No Wikidoc entry in file: {oFileName}')
            return self.oPages
        except Exception as e:
            LogError(uMsg='WikiDoc:Unexpected error reading file:',oException=e)
            return []

    def WriteDoc(self,uPath:cPath) -> None:
        """ writes the Wiki Doc File """

        oFileName:cFileName = cFileName(uPath) + (self.uPage+'.rst')
        # oFileName.Delete()
        f = open(str(oFileName), 'w')

        # _Header.md currently not working, so add it static
        if self.uWikiApp == 'GITWIKI':
            f.write('[[https://github.com/thica/ORCA-Remote/blob/master/src/wikidoc/images/orca.png]]\r\n')

        for uLine in self.uContent:
            f.write(EscapeUnicode(uLine)+'\n')
        f.close()


    def ReplaceTocs(self,dTocs:Dict[str,List[cWikiTocEntry]]) -> None:
        """ replaces the Tocs Refs with the collected TOCs"""
        i:int
        uLine:str
        aParts:List[str]
        uContext:str
        uSortType:str
        aTocs:List[cWikiTocEntry]

        for i,uLine in enumerate(self.uContent):
            if uLine.startswith('WikiDoc:TOC:'):
                aParts=uLine.split(':')
                if len(aParts)==4:
                    uContext=aParts[-2]
                    uTocType=aParts[-1]
                    uSortType='unsorted'
                else:
                    uContext=aParts[-3]
                    uTocType=aParts[-2]
                    uSortType=aParts[-1]

                aTocs = dTocs.get(uContext)
                if aTocs:
                    if uSortType=='sorted':
                        aTocs=sorted(aTocs, key=lambda entry: entry.uTocTitle)
                    if uSortType=='ordered':
                        aTocs=sorted(aTocs, key=lambda entry: entry.uTocTitle)
                        for oTocEntry in aTocs:
                            oTocEntry.RemoveOrder()
                    if uTocType=='List':
                        for oTocEntry in aTocs:
                            self.uContent.insert(i,oTocEntry.AsListToc())
                            i+=1
                        self.uContent.remove(uLine)
                else:
                    LogError(uMsg='Wikidoc:unable to find TOCS for context:'+uContext)

    def AdjustToTargetWiki(self,oWikiDoc:cWikiDoc) -> None:
        iIndex:int
        iPos:int
        uFileName:str
        uLine:str
        uLink:str

        self.uWikiApp = oWikiDoc.uWikiApp
        if oWikiDoc.uWikiApp == 'GITWIKI':
            iIndex = -1
            for uLine in self.uContent:
                # replace the git links to files in the git repo
                iIndex += 1
                iPos = uLine.find('[[File:')
                if iPos>=0:
                    uFileName = uLine[iPos+7:uLine.find('|',iPos+1)]
                    oFile = oWikiDoc.dImageFileListBase.get(uFileName)
                    if oFile is not None:
                        uLink = EscapeUnicode(oWikiDoc.uHost+oFile.unixstring[oFile.unixstring.rfind('/src/'):])
                        uLine = uLine[:iPos+2]+uLink+uLine[uLine.find(']]',iPos):]
                    else:
                        LogError(uMsg='Wikidoc:unable to find linked filename: [%s] [%s] [%s]' % (uFileName,uLine,self.uPage))
                # adjust syntaxhighlighting to GIT Wiki

                uLine = uLine.replace('<div style="overflow-x: auto;"><syntaxhighlight  lang="xml">', '<div style="overflow-x: auto;">\n```xml')
                uLine = uLine.replace('</syntaxhighlight></div>',"```\n</div>")
                # uLine = uLine.replace('<div style="overflow-x: auto;"><syntaxhighlight  lang="xml">', '----<div style="overflow-x: auto;"><code><nowiki>')
                # uLine = uLine.replace('</syntaxhighlight></div>',"</nowiki></code></div>\r\n----")

                if "syntaxhighlight" in uLine:
                    Logger.warning('Unsupported Syntax Highlight: [%s] [%s] ' %(self.uPage,uLine))
                self.uContent[iIndex]=uLine


class cRstDoc:
    """ Class to create the ORCA Wiki Documentation """
    def __init__(self,**kwargs):
        self.dFileList:Dict[str,cFileName]          = {}
        self.aDocs:List[cRstPage]                  = []
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

    def CollectImages(self,oPath:cPath,bSubDirs:bool) -> None:
        """ adds all files in a folder to the list of images """
        aFiles:List[str] = oPath.GetFileList(bSubDirs=bSubDirs,bFullPath=True)
        tFilter:Tuple = ('.jpg','.jpeg','.bmp','.png')

        for uFile in aFiles:
            if 'wikidoc' in uFile:
                if uFile.endswith(tFilter):
                    oFile:cFileName = cFileName(uFile)
                    self.dImageFileList[str(oFile)]       = oFile
                    self.dImageFileListBase[oFile.basename] = oFile


    # noinspection PyMethodMayBeStatic
    def CleanUp(self) -> None:
        Globals.oPathTmp.Clear()

    def CollectFile(self,oFile:cFileName) -> None:
        """ Adds a file to list of sources """
        self.dFileList[str(oFile)]=oFile
    def CollectFiles(self,oPath, bSubDirs=False):
        """ adds all files in a folder to the list of sources """
        aFiles=oPath.GetFileList(bSubDirs=bSubDirs,bFullPath=True)
        for uFile in aFiles:
            oFile=cFileName(uFile)
            if str(oFile).endswith('.py') or str(oFile).endswith('.txt'):
                self.dFileList[str(oFile)]=oFile

    def ParseFiles(self) -> None:
        """ Parses all added files """
        for uFileKey in self.dFileList:
            self.ParseFile(self.dFileList[uFileKey])

    def ReplaceTocs(self) -> None:
        """ Replace all TOC references """
        oPage:cRstPage
        for oPage in self.aDocs:
            oPage.ReplaceTocs(self.dTocs)

    def AdjustToTargetWiki(self) -> None:
        """ Adjust to target wiki (currently GIT wiki) """
        oPage:cRstPage
        for oPage in self.aDocs:
            oPage.AdjustToTargetWiki(self)

        if self.uWikiApp=='GITWIKI':
            oWikiPath:cPath = Globals.oPathRoot + 'wikidoc'
            aFiles:List[str] = oWikiPath.GetFileList(bSubDirs=False,bFullPath=True)
            for uFile in aFiles:
                if uFile.endswith('.md'):
                    oSourceFileName:cFileName = cFileName()
                    oSourceFileName.ImportFullPath(uFnFullName=uFile)
                    oSourceFileName.Copy(oNewFile=self.oWikiTargetFolder)


    def WriteDocs(self) -> None:
        """ Write all wiki entries as txt file """
        oPage:cRstPage
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
        oPage:cRstPage=cRstPage()
        aPages:List[cRstPage]=oPage.ParseFile(oFileName)
        for oFoundPage in aPages:
            self.aDocs.append(oFoundPage)
            oToc:cWikiTocEntry=cWikiTocEntry()
            oToc.uTocReference=oFoundPage.uPage
            oToc.uTocTitle    =oFoundPage.uTOCTitle
            self.AddToc(oToc,oFoundPage.uContext)
            Logger.debug('Found Page: %s (%s)' % (oFoundPage.uPage,oFileName))




