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


from copy                            import copy
from xml.dom                         import minidom
from xml.etree                       import ElementInclude
from xml.etree.ElementTree           import fromstring
from xml.etree.ElementTree           import tostring

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
           'SplitMax'
          ]

def LoadXMLFile(oFile):
    """
    Loads a simple XML file to an Elementree Node without any manipulating

    :rtype: xml.etree.ElementTree.Element
    :param cFileName oFile: xml file to load
    :return: Element tree element
    """

    uRaw=CachedFile(oFile)
    return fromstring(uRaw)

def XMLPrettify(oElem):
    """
    Return a pretty-printed XML string for the Element

    :rtype: string
    :param  xml.etree.ElementTree.Element oElem: Element to prettyfy
    :return: A string representation of the elementree node
    """

    uRough_string = tostring(oElem, 'utf-8')
    uReparsed = minidom.parseString(uRough_string)
    uFinal=uReparsed.toprettyxml(indent="    ")
    uFinal=uFinal.replace(">\n",">")
    uFinal=uFinal.replace("\n\n","")
    uFinal=uFinal.replace("\n \n","\n")
    uFinal=uFinal.replace("\n  \n","\n")
    uFinal=uFinal.replace("\n   \n","\n")
    uFinal=uFinal.replace("\n    \n","\n")
    uFinal=uFinal.replace("\n     \n","\n")
    uFinal=uFinal.replace("\n      \n","\n")
    uFinal=uFinal.replace("\n       \n","\n")
    uFinal=uFinal.replace("\n        \n","\n")
    uFinal=uFinal.replace("\n         \n","\n")
    return uFinal

def orca_et_loader(uFile, parse, encoding=None,oReplacementVars=cDefinitionVars()):
    """Custom Loader for ElementTree Include to add definition path to includes
        and to make make bulk include using placeholder possible
    """
    if uFile.endswith('*'):
        uRet=[]
        oFn        = cFileName("").ImportFullPath(uFile)
        oDir       = oFn.oPath
        uPattern   = (oFn.string)[len(oDir.string):]
        uPattern   = uPattern[1:-1]
        aFiles     = oDir.GetFileList()
        for uFile in aFiles:
            if uFile.startswith(uPattern):
                oFnLoad = cFileName(oDir) + uFile
                oFnLoadFileRedirect = Globals.oTheScreen.oSkin.dSkinRedirects.get(oFnLoad.string)
                if oFnLoadFileRedirect is not None:
                    oFnLoad = oFnLoadFileRedirect
                Logger.debug (u'XML: Bulk-Loading XML Include:' + oFnLoad)
                #uRaw= ElementInclude.default_loader(uLoadFile, "text", encoding)
                uRaw  = CachedFile(oFnLoad)
                uRaw2 = ReplaceDefVars(uRaw,oReplacementVars)
                uRet.append(fromstring(uRaw2))
        if len(uRet)==0:
            return None
        else:
            return uRet
    else:
        oFn = cFileName("").ImportFullPath(uFile)
        if oFn.Exists():
            Logger.debug (u'XML: Loading XML Include:'+oFn.string)
            #uRaw= ElementInclude.default_loader(uFile2, "text", encoding)
            uRaw  = CachedFile(oFn)
            uRaw2 = ReplaceDefVars(uRaw,oReplacementVars)
            bRet  = fromstring(uRaw2)
        else:
            Logger.debug (u'XML: Skipping XML Include (File not found):'+oFn.string)
            bRet=None
        return bRet

def Orca_FromString(sET_Data, oDef, sFileName="Unknown"):
    """  reads xml from a string and sets the definition context vars """
    try:
        if oDef is None:
            return fromstring(sET_Data)
        else:
            oET_Root = fromstring(ReplaceDefVars(sET_Data,oDef.oDefinitionVars))

        oET_Root.set('definitioncontext',oDef.uName)
        oET_Root.set('definitionalias', oDef.uAlias)
        oET_Root.set('replacementvars',oDef.oDefinitionVars)

        for e in oET_Root:
            e.set('definitioncontext',oDef.uName)
            e.set('definitionalias',oDef.uAlias)
            e.set('replacementvars',oDef.oDefinitionVars)
            e.set('linefilename',sFileName)
        return oET_Root
    except Exception as e:
        LogError('FromString:Invalid XML:'+sFileName,e)
        LogError(ReplaceDefVars(sET_Data,oDef.oDefinitionVars))
    return None

def Orca_include(elem, loader,uFileName = "Unknown Filename"):
    """  heavyly customized loader for includes in xml files"""
    uAlias = elem.get('definitionalias')
    oDef = None
    if uAlias is not None:
        oDef = Globals.oDefinitions.dDefinitionList_Dict[uAlias]

    Orca_includesub(elem, loader,Globals.uDefinitionContext,oDef,uFileName)
    RestoreDefinitionContext()

def Orca_includesub(elem, loader,uOrgDefinitionContext, oDef, uFileName="Unknown Filename"):
    """ sub function for the include loader """
    global bBlockInclude

    elemens=[]
    oReplacementVars=cDefinitionVars()
    aSaveReplacementVars = []
    for e in elem:
        elemens.append(e)

    if oDef:
        oReplacementVars=oDef.oDefinitionVars

    i=0
    for e in elemens:
        e.set('definitioncontext',uOrgDefinitionContext)
        if oDef:
            e.set('definitionalias',oDef.uAlias)
        e.set('linefilename',uFileName)

        if e.tag=='startskip':
            if CheckCondition(e):
                bBlockInclude = True

        if e.tag=='stopskip':
            bBlockInclude = False

        if e.tag == ElementInclude.XINCLUDE_INCLUDE:

            if CheckCondition(e) and not bBlockInclude:

                # process xinclude directive
                href = e.get("href")
                parse = e.get("parse", "xml")
                if parse == "xml":
                    uNewDefinitionContext = u''
                    if "DEFINITIONPATH[" in href:
                        uNewDefinitionContext,href=GetSetDefinitionName( href)

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
                        aSaveReplacementVars=oReplacementVars
                        oReplacementVars=oTmpReplacementVars
                        oReplacementVars.update(aIncludeReplacementVars)
                        if oDef:
                            oDef.oDefinitionVars=oTmpReplacementVars

                    oFnHRefRedirect = Globals.oTheScreen.oSkin.dSkinRedirects.get(cFileName(u'').ImportFullPath(ReplaceVars(href)))
                    if oFnHRefRedirect is not None:
                        oFnHRef = oFnHRefRedirect.string
                    oFnHRef=cFileName(u'').ImportFullPath(ReplaceVars(href))
                    nodes = loader(oFnHRef.string, parse,None,oReplacementVars)

                    if nodes is not None:
                        if  uNewDefinitionContext==u'':
                            nodes = Orca_includesub(nodes, loader,uOrgDefinitionContext,oDef,oFnHRef.string)
                        else:
                            nodes = Orca_includesub(nodes, loader,uNewDefinitionContext,oDef,oFnHRef.string)

                    if oTmpReplacementVars is not None:
                        oReplacementVars=aSaveReplacementVars
                        if oDef:
                            oDef.oDefinitionVars=aSaveReplacementVars

                    if uNewDefinitionContext!=u'':
                        SetDefinitionContext(uOrgDefinitionContext)

                    if isinstance(nodes,list):
                        bFirst=True
                        for node in nodes:
                            node = copy(node)
                            if e.tail:
                                node.tail = (node.tail or "") + e.tail
                            if bFirst:
                                elem[i] = node
                                bFirst=False
                            else:
                                elem.insert(i,node)
                                i = i + 1
                    elif nodes is None:
                        del elem[i]
                        i=i-1
                    else:
                        nodes = copy(nodes)
                        if e.tail:
                            nodes.tail = (nodes.tail or "") + e.tail
                        elem[i] = nodes
        else:
            Orca_includesub(e, loader,uOrgDefinitionContext,oDef,uFileName)
        i = i + 1
    return elem

def GetXMLTextValueTest(oXMLNode,uTag,bMandantory,uDefault):
    """ Returns a string from a xml value """
    try:
        if uTag:
            uRet = ToUnicode(oXMLNode.find(uTag).text)
        else:
            uRet = ToUnicode(oXMLNode.text)
        if uRet==u"None":
            uRet=u''
        return uRet

    except Exception as e:
        if bMandantory:
            uMsg=LogError(u'XML Error: Attribut [' + uTag + '] missing:'+tostring(oXMLNode))
            ShowErrorPopUp(uMessage=uMsg,bAbort=True)
        return uDefault

def GetXMLTextValue(oXMLNode,uTag,bMandantory,uDefault):
    """ Returns a string from a xml value """

    if oXMLNode is None:
        return uDefault

    if uTag:
        oObj=oXMLNode.find(uTag)
    else:
        oObj=oXMLNode
    if oObj is None:
        if bMandantory:
            uMsg=LogError(u'XML Error: Attribut [' + uTag + '] missing:'+tostring(oXMLNode))
            ShowErrorPopUp(uMessage=uMsg,bAbort=True)
        return uDefault
    uTmp=oObj.text
    if uTmp is None:
        uTmp=u''
    return ToUnicode(uTmp)

def GetXMLIntValue(oXMLNode,uTag,bMandantory,iDefault):
    """ Returns an integer from a xml value """
    return ToInt(GetXMLTextValue(oXMLNode,uTag,bMandantory,iDefault))

def GetXMLFloatValue(oXMLNode,uTag,bMandantory,fDefault):
    """ Returns a float from a xml value """
    return ToInt(GetXMLTextValue(oXMLNode,uTag,bMandantory,fDefault))

def GetXMLIntValueVar(oXMLNode,uTag,bMandantory,iDefault):
    """ Returns an int from a xml value (given as var)"""
    return ToFloat(ReplaceVars(GetXMLTextValue(oXMLNode,uTag,bMandantory,ToUnicode(iDefault))))

def GetXMLBoolValue(oXMLNode,uTag,bMandantory,bDefault):
    """ Returns a bool from a xml value """
    return ToBool(GetXMLTextValue(oXMLNode,uTag,bMandantory,bDefault))

def GetXMLBoolValueVar(oXMLNode,uTag,bMandantory,bDefault):
    """ Returns a bool from a xml value (given as var)"""
    return ToBool(ReplaceVars(GetXMLTextValue(oXMLNode,uTag,bMandantory,ToUnicode(bDefault))))

def GetXMLTextAttribute(oXMLNode,uTag,bMandantory,uDefault):
    """ Returns a string from a xml attribute"""
    if oXMLNode is None:
        return uDefault
    oObj=oXMLNode.get(uTag)
    if oObj is None:
        if bMandantory:
            uMsg=LogError(u'XML Error: Attribut [' + uTag + '] missing')
            ShowErrorPopUp(uMessage=uMsg,bAbort=True)
        return uDefault
    oObj=ToUnicode(oObj)
    return oObj

def GetXMLTextAttributeVar(oXMLNode,uTag,bMandantory,uDefault):
    """ Returns a string from a xml attribute (given as var)"""
    return ReplaceVars(GetXMLTextAttribute(oXMLNode,uTag,bMandantory,uDefault))

def GetXMLDicAttribute(oXMLNode,uTag,bMandantory,aDefault):
    """ Returns a dict from a xml attribute """
    return ToDic(GetXMLTextAttribute(oXMLNode,uTag,bMandantory,aDefault))

#def GetXMLDicAttributeVar(oXMLNode,uTag,bMandantory,aDefault):
#    return ToDic(ReplaceVars(GetXMLTextAttribute(oXMLNode,uTag,bMandantory,aDefault)))

def GetXMLIntAttribute(oXMLNode,uTag,bMandantory,iDefault):
    """ Returns an integer from a xml attribute """
    return ToInt(GetXMLTextAttribute(oXMLNode,uTag,bMandantory,iDefault))

def GetXMLIntAttributeVar(oXMLNode,uTag,bMandantory,iDefault):
    """ Returns an integer from a xml attribute (given as var)"""
    return ToInt(ReplaceVars(GetXMLTextAttribute(oXMLNode,uTag,bMandantory,ToUnicode(iDefault))))

def GetXMLFloatAttribute(oXMLNode,uTag,bMandantory,fDefault):
    """ Returns an float from a xml attribute """
    return ToFloat(GetXMLTextAttribute(oXMLNode,uTag,bMandantory,fDefault))

def GetXMLFloatAttributeVar(oXMLNode,uTag,bMandantory,fDefault):
    """ Returns an float from a xml attribute (given as var)"""
    return ToFloat(ReplaceVars(GetXMLTextAttribute(oXMLNode,uTag,bMandantory,ToUnicode(fDefault))))

def GetXMLBoolAttribute(oXMLNode,uTag,bMandantory,bDefault):
    """ Returns an bool from a xml attribute """
    return ToBool(GetXMLTextAttribute(oXMLNode,uTag,bMandantory,bDefault))

def GetXMLBoolAttributeVar(oXMLNode,uTag,bMandantory,bDefault):
    """ Returns an bool from a xml attribute (given as var) """
    return ToBool(ReplaceVars(GetXMLTextAttribute(oXMLNode,uTag,bMandantory,ToUnicode(bDefault))))

def SplitMax(uPar):
    """splits an xml value in the format aa:bb into a tuple
       returns a tuple for aa as well """

    tRet=uPar.split(u":")
    if len(tRet)>1:
        return float(tRet[0]), float(tRet[1])
    else:
        return(float(uPar),0)



