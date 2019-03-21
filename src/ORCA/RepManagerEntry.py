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

from xml.etree.ElementTree  import ElementTree
from xml.etree.ElementTree  import Element
from xml.etree.ElementTree  import fromstring

from kivy.logger            import Logger
from kivy.compat            import string_types

from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.FileName    import cFileName
from ORCA.utils.LoadFile    import LoadFile
from ORCA.utils.LogError    import LogError
from ORCA.Downloads         import cRepEntry

class cRepManagerEntry(object):
    """ Single entry of Repository entry """
    def __init__(self, oFileName):
        if isinstance(oFileName,string_types):
            self.oFnEntry = cFileName(u'').ImportFullPath(oFileName)
        else:
            self.oFnEntry = cFileName(oFileName)
        self.oRepEntry=cRepEntry()

    def ParseFromXML(self,oContent=None):
        """ Parses an xms string into object vars """
        try:
            if oContent is None:
                oET_Root = ElementTree(file=self.oFnEntry.string).getroot()
                Logger.debug('RepManager: Parsing File: [%s]' % self.oFnEntry.string)
            elif isinstance(oContent,Element):
                oET_Root = oContent
            else:
                oET_Root = ElementTree(fromstring(oContent))

            if not oET_Root is None:
                oNode=oET_Root.find('repositorymanager')
                if not oNode is None:
                    oNode=oNode.find('entry')
                    if not oNode is None:
                        self.oRepEntry.ParseFromXMLNode(oNode)
            return self.oRepEntry.uName!='Error'
        except Exception as e:
            uMsg=LogError('Invalid XML Syntax on file '+self.oFnEntry ,e)
            ShowErrorPopUp(uMessage=uMsg)
            return False

    def ParseFromSourceFile(self):
        """ Parses an xml file into object vars """
        uContent=LoadFile(self.oFnEntry)
        lPos=uContent.find('<root>')
        lPos2=uContent.find('</root>')
        if lPos==-1 or lPos2==-1:
            return False
        uContent=uContent[lPos:lPos2+7]
        return self.ParseFromXML(uContent)

