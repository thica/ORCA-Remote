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

from typing import List
from typing import Dict
from typing import Union
from typing import Callable
from typing import Tuple
from typing import Any
from typing import Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.definition.Definition import cDefinition
else:
    from typing import TypeVar
    cDefinition = TypeVar("cDefinition")

from copy                            import copy
from xml.dom                         import minidom
from xml.etree                       import ElementInclude
from xml.etree.ElementTree           import fromstring
from xml.etree.ElementTree           import tostring
from xml.etree.ElementTree           import Element
from xml.etree.ElementTree           import TreeBuilder
from xml.etree.ElementTree           import Comment
from xml.etree.ElementTree           import XMLParser
from xml.etree.ElementTree           import ElementTree as ET

from kivy.logger                     import Logger

from ORCA.definition.DefinitionVars import cDefinitionVars
from ORCA.definition.DefinitionContext import SetDefinitionContext
from ORCA.definition.DefinitionContext import RestoreDefinitionContext
from ORCA.ui.ShowErrorPopUp          import ShowErrorPopUp
from ORCA.utils.CachedFile           import CachedFile
from ORCA.utils.CheckCondition       import CheckCondition
from ORCA.utils.GetSetDefinitionName import GetSetDefinitionName
from ORCA.utils.LogError             import LogError
from ORCA.utils.TypeConvert          import ToBool
from ORCA.utils.TypeConvert          import ToDic
from ORCA.utils.TypeConvert          import ToFloat
from ORCA.utils.TypeConvert          import ToInt
from ORCA.utils.TypeConvert          import ToUnicode
from ORCA.vars.Replace               import ReplaceDefVars
from ORCA.vars.Replace               import ReplaceVars
from ORCA.utils.FileName             import cFileName
from ORCA.utils.Path                 import cPath

import ORCA.Globals as Globals

bBlockInclude = False

__all__ = ['XMLPrettify',
           'orca_et_loader',
           'Orca_include',
           'Orca_FromString',
           'GetXMLTextValue',
           'GetXMLIntValue',
           'GetXMLIntValueVar',
           'GetXMLFloatValue',
           'GetXMLBoolValue',
           'GetXMLBoolValueVar',
           'GetXMLTextAttribute',
           'GetXMLTextAttributeVar',
           'GetXMLDicAttribute',
           'GetXMLIntAttribute',
           'GetXMLIntAttributeVar',
           'GetXMLFloatAttribute',
           'GetXMLFloatAttributeVar',
           'GetXMLBoolAttribute',
           'GetXMLBoolAttributeVar',
           'LoadXMLFile',
           'LoadXMLString',
           'WriteXMLFile',
           'SplitMax',
           'CommentedTreeBuilder'
          ]


'''
class CommentedTreeBuilder (XMLTreeBuilder ):
    def __init__ ( self, html = 0, target = None):
        super(CommentedTreeBuilder, self).__init__(html)
        #XMLTreeBuilder.__init__( self, html, target )
        self._parser.CommentHandler = self.handle_comment

    def handle_comment ( self, data ):
        self._target.start( Comment, {} )
        self._target.data( data )
        self._target.end( Comment )
'''
'''
class CommentedTreeBuilder (XMLTreeBuilder ):
    def __init__(self, **kwargs):
        kwargs["insert_comments"] = True
        super().__init__(**kwargs)
'''

class CommentedTreeBuilder(TreeBuilder):
    def comment(self, data) -> None:
        self.start(Comment, {})
        self.data(data)
        self.end(Comment)

def LoadXMLFile(*,oFile:cFileName, oParser:Optional[XMLParser]=None, bNoCache=False)-> Element:
    """
    Loads a simple XML file to an Elementree Node without any manipulating

    :rtype: xml.etree.ElementTree.Element
    :param cFileName oFile: xml file to load
    :param XMLParser oParser: Optional: Parser to use
    :param bool bNoCache: Optional: Do not use cached files
    :return: Element tree element
    """

    if oParser is None:
        if not bNoCache:
            return fromstring(CachedFile(oFileName=oFile))
        else:
            return ET().parse(source=oFile.string)
    else:
        return ET().parse(source=oFile.string, parser=oParser)

def LoadXMLString(*,uXML:str)-> Element:
    """
    Loads a simple XML string representation to an Elementree Node without any manipulating

    :rtype: xml.etree.ElementTree.Element
    :param str uXML: xml file to load
    :return: Element tree element
    """

    return fromstring(uXML)

def WriteXMLFile(*,oFile:cFileName,oElem:Element)-> bool:
    """
    Save an Element node to an xml file

    :param cFileName oFile: xml file to save
    :param Element oElem: XML Element to save
    :return: Element tree element
    """
    try:
        oET=ET(oElem)
        oET.write(oFile.string, encoding="UTF-8",xml_declaration=True)
        return True
    except Exception as e:
        LogError(uMsg='Can''t write XML File:'+oFile.string,oException=e)
        return False


def XMLPrettify(*,oElem:Element)-> str:
    """
    Return a pretty-printed XML string for the Element

    :param  xml.etree.ElementTree.Element oElem: Element to prettyfy
    :return: A string representation of the elementree node
    """

    iNum:int
    uRough_string:str           = tostring(oElem, 'utf-8')
    oReparsed:minidom.Document  = minidom.parseString(uRough_string)
    uFinal:str                  = oReparsed.toprettyxml(indent="    ")
    uFinal                      = uFinal.replace(">\n",">")
    uFinal                      = uFinal.replace("\n\n","")
    for iNum in range(10):
        uFinal = uFinal.replace("\n"+" "*iNum+"\n", "\n")
    return uFinal

# noinspection PyDefaultArgument,PyUnusedLocal
def orca_et_loader(uFile:str, uParse:str, uEncoding:str="xml",oReplacementVars:cDefinitionVars=cDefinitionVars()) -> Union[List[str],Element,None]:
    """Custom Loader for ElementTree Include to add definition path to includes
        and to make make bulk include using placeholder possible
    """
    if uFile.endswith('*'):
        aRet:List[str]   = []
        oFn:cFileName    = cFileName("").ImportFullPath(uFnFullName=uFile)
        oDir:cPath       = oFn.oPath
        uPattern:str     = oFn.string[len(oDir.string):]
        uPattern         = uPattern[1:-1]
        aFiles:List[str] = oDir.GetFileList()

        for uFile in aFiles:
            if uFile.startswith(uPattern):
                oFnLoad:cFileName      = cFileName(oDir) + uFile
                oFnLoadFileRedirect:Union[cFileName,None]  = Globals.oTheScreen.oSkin.dSkinRedirects.get(oFnLoad.string)
                if oFnLoadFileRedirect is not None:
                    oFnLoad = oFnLoadFileRedirect
                Logger.debug (u'XML: Bulk-Loading XML Include:' + oFnLoad)
                #uRaw= ElementInclude.default_loader(uLoadFile, "text", encoding)
                uRaw:str  = CachedFile(oFileName=oFnLoad)
                uRaw2:str = ReplaceDefVars(uRaw,oReplacementVars)
                aRet.append(fromstring(uRaw2))
        if len(aRet)==0:
            return None
        else:
            return aRet
    else:
        oFn:cFileName = cFileName("").ImportFullPath(uFnFullName=uFile)
        if oFn.Exists():
            Logger.debug (u'XML: Loading XML Include:'+oFn.string)
            #uRaw= ElementInclude.default_loader(uFile2, "text", encoding)
            uRaw:str  = CachedFile(oFileName=oFn)
            uRaw2:str = ReplaceDefVars(uRaw,oReplacementVars)
            oRet  = fromstring(uRaw2)
        else:
            Logger.debug (u'XML: Skipping XML Include (File not found):'+oFn.string)
            oRet=None
        return oRet

def Orca_FromString(*,uET_Data:str, oDef:cDefinition, uFileName:str="Unknown") -> Union[Element,None]:
    """  reads xml from a string and sets the definition context vars
    :param str uET_Data: The string representinga xml
    :param cDefinition oDef: The definition, wehere the xml belomgs to
    :param uFileName: The original filename (for debugging support)
    :return:
    """
    try:
        if oDef is None:
            return fromstring(uET_Data)
        else:
            oET_Root:Element = fromstring(ReplaceDefVars(uET_Data,oDef.oDefinitionVars))

        oET_Root.set('definitioncontext',oDef.uName)
        oET_Root.set('definitionalias', oDef.uAlias)
        oET_Root.set('replacementvars',oDef.oDefinitionVars)

        for e in oET_Root:
            e.set('definitioncontext',oDef.uName)
            e.set('definitionalias',oDef.uAlias)
            e.set('replacementvars',oDef.oDefinitionVars)
            e.set('linefilename',uFileName)
        return oET_Root
    except Exception as e:
        LogError(uMsg='FromString:Invalid XML:'+uFileName,oException=e)
        LogError(uMsg=ReplaceDefVars(uET_Data,oDef.oDefinitionVars))
    return None

def Orca_include(oElem, pLoader: Callable,uFileName:str = "Unknown Filename")-> None:
    """  heavily customized loader for includes in xml files"""
    uAlias = oElem.get('definitionalias')
    oDef = None
    if uAlias is not None:
        oDef = Globals.oDefinitions[uAlias]

    Orca_includesub(oElem, pLoader,Globals.uDefinitionContext,oDef,uFileName)
    RestoreDefinitionContext()

def Orca_includesub(oElem:Element, pLoader: Callable,uOrgDefinitionContext: str, oDef:cDefinition, uFileName:str="Unknown Filename") -> Element:
    """ sub function for the include loader """
    global bBlockInclude

    aElemens:List[Element]                = []
    oReplacementVars:cDefinitionVars      = cDefinitionVars()
    oSaveReplacementVars:cDefinitionVars  = cDefinitionVars()

    for e in oElem:
        aElemens.append(e)

    if oDef:
        oReplacementVars=oDef.oDefinitionVars

    i:int = 0
    for e in aElemens:
        e.set('definitioncontext',uOrgDefinitionContext)
        if oDef:
            e.set('definitionalias',oDef.uAlias)
        e.set('linefilename',uFileName)

        if e.tag=='startskip':
            if CheckCondition(oPar=e):
                bBlockInclude = True

        if e.tag=='stopskip':
            bBlockInclude = False

        if e.tag == ElementInclude.XINCLUDE_INCLUDE:

            if CheckCondition(oPar=e) and not bBlockInclude:

                # process xinclude directive
                uHref:str  = e.get("href")
                uParse:str = e.get("parse", "xml")
                if uParse == "xml":
                    uNewDefinitionContext = u''
                    if "DEFINITIONPATH[" in uHref:
                        uNewDefinitionContext,uHref=GetSetDefinitionName(uText=uHref)

                    oTmpReplacementVars=e.get("definitionvars")
                    if oTmpReplacementVars is None:
                        oTmpReplacementVars=oReplacementVars

                    aIncludeReplacementVars = e.get("includedefinitionvars")
                    if aIncludeReplacementVars is None:
                        aIncludeReplacementVars=cDefinitionVars()
                    else:
                        aIncludeReplacementVars=ToDic(aIncludeReplacementVars)

                    #
                    aIncludeReplacementVars=aIncludeReplacementVars.copy()

                    if oTmpReplacementVars is not None:
                        oTmpReplacementVars=oTmpReplacementVars.copy()
                        #oTmpReplacementVars=ToDic(oTmpReplacementVars)
                        oSaveReplacementVars=oReplacementVars
                        oReplacementVars=oTmpReplacementVars
                        oReplacementVars.update(aIncludeReplacementVars)
                        if oDef:
                            oDef.oDefinitionVars=oTmpReplacementVars

                    oFnHRefRedirect = Globals.oTheScreen.oSkin.dSkinRedirects.get(cFileName(u'').ImportFullPath(uFnFullName=ReplaceVars(uHref)).string)
                    if oFnHRefRedirect is not None:
                        oFnHRef = oFnHRefRedirect
                    else:
                        oFnHRef=cFileName(u'').ImportFullPath(uFnFullName=ReplaceVars(uHref))
                    oNodes:Element = pLoader(oFnHRef.string, uParse,None,oReplacementVars)

                    if oNodes is not None:
                        if  uNewDefinitionContext==u'':
                            oNodes = Orca_includesub(oNodes, pLoader,uOrgDefinitionContext,oDef,oFnHRef.string)
                        else:
                            oNodes = Orca_includesub(oNodes, pLoader,uNewDefinitionContext,oDef,oFnHRef.string)

                    if oTmpReplacementVars is not None:
                        oReplacementVars=oSaveReplacementVars
                        if oDef:
                            oDef.oDefinitionVars=oSaveReplacementVars

                    if uNewDefinitionContext!=u'':
                        SetDefinitionContext(uDefinitionName=uOrgDefinitionContext)

                    if isinstance(oNodes,list):
                        bFirst:bool = True
                        for oNode in oNodes:
                            oNode = copy(oNode)
                            if e.tail:
                                oNode.tail = (oNode.tail or "") + e.tail
                            if bFirst:
                                oElem[i] = oNode
                                bFirst=False
                            else:
                                oElem.insert(i,oNode)
                                i += 1
                    elif oNodes is None:
                        del oElem[i]
                        i -= 1
                    else:
                        oNodes = copy(oNodes)
                        if e.tail:
                            oNodes.tail = (oNodes.tail or "") + e.tail
                        oElem[i] = oNodes
        else:
            Orca_includesub(e, pLoader,uOrgDefinitionContext,oDef,uFileName)
        i += 1
    return oElem

def GetXMLTextValue(*,oXMLNode:Element,uTag:str,bMandatory:bool,vDefault:Any) -> str:
    """ Returns a string from a xml value """

    if oXMLNode is None:
        return vDefault

    oObj: Element

    if uTag:
        oObj=oXMLNode.find(uTag)
    else:
        oObj=oXMLNode
    if oObj is None:
        if bMandatory:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'XML Error: Attribut [' + uTag + '] missing:'+tostring(oXMLNode)),bAbort=True)
        return vDefault
    uTmp=oObj.text
    if uTmp is None:
        uTmp=u''
    return uTmp

def GetXMLIntValue(*,oXMLNode:Element,uTag:str,bMandatory:bool,iDefault:int) -> int:
    """ Returns an integer from a xml value """
    return ToInt(GetXMLTextValue(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=iDefault))

def GetXMLFloatValue(*,oXMLNode:Element,uTag:str,bMandatory:bool,fDefault:float) -> float:
    """ Returns a float from a xml value """
    return ToInt(GetXMLTextValue(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=fDefault))

def GetXMLIntValueVar(*,oXMLNode:Element,uTag:str,bMandatory:bool,iDefault:int) -> int:
    """ Returns an int from a xml value (given as var)"""
    return ToInt(ReplaceVars(GetXMLTextValue(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=ToUnicode(iDefault))))

def GetXMLBoolValue(*,oXMLNode:Element,uTag:str,bMandatory:bool,bDefault:bool) -> bool:
    """ Returns a bool from a xml value """
    return ToBool(GetXMLTextValue(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=bDefault))

def GetXMLBoolValueVar(*,oXMLNode:Element,uTag:str,bMandatory:bool,bDefault:bool) -> bool:
    """ Returns a bool from a xml value (given as var)"""
    return ToBool(ReplaceVars(GetXMLTextValue(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=ToUnicode(bDefault))))

def GetXMLTextAttribute(*,oXMLNode:Element,uTag:str,bMandatory:bool,vDefault:Any) -> str:
    """ Returns a string from a xml attribute"""
    if oXMLNode is None:
        return vDefault
    oObj:str=oXMLNode.get(uTag)
    if oObj is None:
        if bMandatory:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'XML Error: Attribut [' + uTag + '] missing'),bAbort=True)
        return vDefault
    # oObj=ToUnicode(oObj)
    return oObj

def GetXMLTextAttributeVar(*,oXMLNode:Element,uTag:str,bMandatory:bool,uDefault:str) -> str:
    """ Returns a string from a xml attribute (given as var)"""
    return ReplaceVars(GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=uDefault))

def GetXMLDicAttribute(*,oXMLNode:Element,uTag:str,bMandatory:bool,dDefault:Dict) -> Dict:
    """ Returns a dict from a xml attribute """
    return ToDic(GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=dDefault))

#def GetXMLDicAttributeVar(oXMLNode,uTag,bMandatory,aDefault):
#    return ToDic(ReplaceVars(GetXMLTextAttribute(oXMLNode,uTag,bMandatory,aDefault)))

def GetXMLIntAttribute(*,oXMLNode:Element,uTag:str,bMandatory:bool,iDefault:int) -> int:
    """ Returns an integer from a xml attribute """
    return ToInt(GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=iDefault))

def GetXMLIntAttributeVar(*,oXMLNode:Element,uTag:str,bMandatory:bool,iDefault:int) -> int:
    """ Returns an integer from a xml attribute (given as var)"""
    return ToInt(ReplaceVars(GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=ToUnicode(iDefault))))

def GetXMLFloatAttribute(*,oXMLNode:Element,uTag:str,bMandatory:bool,fDefault:float) -> float:
    """ Returns an float from a xml attribute """
    return ToFloat(GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=fDefault))

def GetXMLFloatAttributeVar(*,oXMLNode:Element,uTag:str,bMandatory:bool,fDefault:float) -> float:
    """ Returns an float from a xml attribute (given as var)"""
    return ToFloat(ReplaceVars(GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=ToUnicode(fDefault))))

def GetXMLBoolAttribute(*,oXMLNode:Element,uTag:str,bMandatory:bool,bDefault:bool) -> bool:
    """ Returns an bool from a xml attribute """
    return ToBool(GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=bDefault))

def GetXMLBoolAttributeVar(*,oXMLNode:Element,uTag:str,bMandatory:bool,bDefault:bool) -> bool:
    """ Returns an bool from a xml attribute (given as var) """
    return ToBool(ReplaceVars(GetXMLTextAttribute(oXMLNode=oXMLNode,uTag=uTag,bMandatory=bMandatory,vDefault=ToUnicode(bDefault))))

def SplitMax(uPar:str) -> Tuple[float,float]:
    """splits an xml value in the format aa:bb into a tuple
       returns a tuple for aa as well """

    tRet=uPar.split(u":")
    if len(tRet)>1:
        return float(tRet[0]), float(tRet[1])
    else:
        return float(uPar),0.0
