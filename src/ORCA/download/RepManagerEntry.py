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

from typing import Union
from typing import cast

from xml.etree.ElementTree  import Element

from kivy.logger            import Logger

from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.FileName    import cFileName
from ORCA.utils.LogError    import LogError
from ORCA.utils.XML         import LoadXMLFile
from ORCA.utils.XML         import LoadXMLString
from ORCA.download.RepEntry import cRepEntry

class cRepManagerEntry:
    """ Single entry of Repository entry """
    def __init__(self, *,oFileName:Union[str,cFileName]):
        self.oFnEntry:cFileName  = cFileName(oFileName)
        self.oRepEntry:cRepEntry = cRepEntry()

    def ParseFromXML(self,*,vContent:Union[str,Element,None]=None) -> bool:
        """ Parses an xms string into object vars """
        oET_Root: Element
        oNode:Element
        try:
            if vContent is None:
                oET_Root = LoadXMLFile(oFile=self.oFnEntry)
                Logger.debug(f'RepManager: Parsing File: [{self.oFnEntry}]')
            elif isinstance(vContent,Element):
                oET_Root = cast(Element,vContent)
            else:
                oET_Root = LoadXMLString(uXML=cast(str,vContent))

            if not oET_Root is None:
                oNode=oET_Root.find('repositorymanager')
                if not oNode is None:
                    oNode=oNode.find('entry')
                    if not oNode is None:
                        self.oRepEntry.ParseFromXMLNode(oXMLEntry=oNode)
            return self.oRepEntry.uName!='Error'
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=f'Invalid XML Syntax on file {self.oFnEntry}' ,oException=e))
            return False

    def ParseFromSourceFile(self) -> bool:
        """ Parses an xml file into object vars """
        uContent:str=self.oFnEntry.Load()
        #iPos=uContent.find('<root>')
        #iPos2=uContent.find('</root>')
        iPos=uContent.find('<repositorymanager>')
        iPos2=uContent.find('</repositorymanager>')
        if iPos==-1 or iPos2==-1:
            return False
        #uContent=uContent[iPos:iPos2+7]
        uContent='<root>'+uContent[iPos:iPos2+21]+'</root>'

        return self.ParseFromXML(vContent=uContent)

