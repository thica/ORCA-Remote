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

from typing                       import List
from typing                       import Optional
from xml.etree.ElementTree        import Element
from xml.etree.ElementTree        import SubElement
from ORCA.vars.Replace            import ReplaceVars
from ORCA.utils.XML               import GetXMLTextValue
from ORCA.utils.XML               import GetXMLBoolValue
from ORCA.utils.Path              import cPath
from ORCA.utils.TypeConvert       import ToIntVersion
from ORCA.download.RepDependency  import cRepDependency
from ORCA.download.RepSkipFile    import cRepSkipFile
from ORCA.download.RepDescription import cRepDescription
from ORCA.download.RepSource      import cRepSource


__all__ = ['cRepEntry']

class cRepEntry:
    """
    sub class which is an representation of the repositories entry part the repository xml tree
    loads and writes the xml node
    """
    def __init__(self):
        self.aDependencies:List[cRepDependency]     = []
        self.aSkipFileNames:List[str]               = []
        self.aSkipFiles:List[cRepSkipFile]          = []
        self.aSources:List[cRepSource]              = []
        self.bSkip:bool                             = False
        self.iMinOrcaVersion:int                    = 0
        self.iVersion:int                           = 0
        self.oDescriptions:cRepDescription          = cRepDescription()
        self.uAuthor:str                            = u''
        self.uDescription:str                       = u''
        self.uMinOrcaVersion:str                    = u''
        self.uName:str                              = u'Error'
        self.oPath:Optional[cPath]                  = None
        self.uRepType:str                           = u''
        self.uUrl:str                               = u''
        self.uVersion:str                           = u''

    def __repr__(self) -> str:
        return repr(self.uName)

    def ParseFromXMLNode(self,*,oXMLEntry:Element) -> None:
        """ Parses an xms string into object vars """

        oXMLSources:Element
        oXMLDependencies:Element
        oXMLSkipFiles:Element

        self.uName          = GetXMLTextValue(oXMLNode=oXMLEntry,uTag=u'name',          bMandatory=True, vDefault=u'Error')
        self.uAuthor        = GetXMLTextValue(oXMLNode=oXMLEntry,uTag=u'author',        bMandatory=False,vDefault=u'unknown')
        self.uVersion       = GetXMLTextValue(oXMLNode=oXMLEntry,uTag=u'version',       bMandatory=False,vDefault=u'0')
        self.uMinOrcaVersion= GetXMLTextValue(oXMLNode=oXMLEntry,uTag=u'minorcaversion',bMandatory=False,vDefault=u'1.1.0')
        self.bSkip          = GetXMLBoolValue(oXMLNode=oXMLEntry,uTag=u'skip',          bMandatory=False,bDefault=False)
        self.iVersion       = ToIntVersion(self.uVersion)
        self.iMinOrcaVersion= ToIntVersion(self.uMinOrcaVersion)
        self.oDescriptions.ParseFromXMLNode(oXMLEntry=oXMLEntry)

        oXMLSources = oXMLEntry.find(u'sources')
        if not oXMLSources is None:
            for oXMLSource in oXMLSources.findall(u'source'):
                oSource:cRepSource = cRepSource()
                oSource.ParseFromXMLNode(oXMLNode=oXMLSource)
                self.aSources.append(oSource)

        oXMLDependencies = oXMLEntry.find(u'dependencies')
        if not oXMLDependencies is None:
            for oXMLDependency in oXMLDependencies.findall(u'dependency'):
                oRepDependency:cRepDependency=cRepDependency()
                oRepDependency.ParseFromXMLNode(oXMLNode=oXMLDependency)
                self.aDependencies.append(oRepDependency)

        oXMLSkipFiles = oXMLEntry.find(u'skipfiles')
        if not oXMLSkipFiles is None:
            oRepSkipFile:cRepSkipFile = cRepSkipFile()
            for oXMLSkipFile in oXMLSkipFiles.findall(u'file'):
                oRepSkipFile.ParseFromXMLNode(oXMLNode=oXMLSkipFile)
                oRepSkipFile.uFile=ReplaceVars(oRepSkipFile.uFile)
                self.aSkipFiles.append(oRepSkipFile)
                self.aSkipFileNames.append(oRepSkipFile.uFile)

    def WriteToXMLNode(self,*,oXMLNode:Element) -> None:
        """ writes object vars to an xml node """

        oXMLEntry:Element
        oVal:Element
        oXMLSources:Element
        oXMLDependencies:Element

        oXMLEntry   = SubElement(oXMLNode,'entry')
        oVal        = SubElement(oXMLEntry,'name')
        oVal.text   = self.uName
        self.oDescriptions.WriteToXMLNode(oXMLNode=oXMLEntry)
        oVal        = SubElement(oXMLEntry,'author')
        oVal.text   = self.uAuthor
        oVal        = SubElement(oXMLEntry,'version')
        oVal.text   = self.uVersion
        oVal        = SubElement(oXMLEntry,'minorcaversion')
        oVal.text   = self.uMinOrcaVersion

        oXMLSources = SubElement(oXMLEntry,'sources')
        for oSource in self.aSources:
            oSource.WriteToXMLNode(oXMLNode=oXMLSources)
        oXMLDependencies = SubElement(oXMLEntry,'dependencies')
        for oDependency in self.aDependencies:
            oDependency.WriteToXMLNode(oXMLNode=oXMLDependencies)
        #we do not write skipfiles by purpose

