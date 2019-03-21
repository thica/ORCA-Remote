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

import  tokenize
import  token
from    io import StringIO
import  json

from    xml.etree.ElementTree   import ElementTree
from    xml.etree.ElementTree   import fromstring

from    kivy.logger             import Logger
from    kivy.compat             import string_types
from    ORCA.utils.LogError     import LogError
from    ORCA.utils.TypeConvert  import ToList
from    ORCA.utils.TypeConvert  import ToUnicode
from    ORCA.utils.XML          import GetXMLTextValue
from    ORCA.vars.Replace       import ReplaceVars
from    ORCA.vars.Access        import SetVar
from    ORCA.vars.Helpers       import UnSplit


class cResultParser(object):
    """ Object to parse results """
    def __init__(self):
        self.uDebugContext              = u''
        self.uContext                   = u''
        self.uGlobalDestVar             = u''
        self.uLocalDestVar              = u''
        self.uParseResultOption         = u''
        self.uGlobalParseResultOption   = u''
        self.uGlobalTokenizeString      = u''

    def Parse(self,uResponse,uGetVar,uParseResultOption,uGlobalDestVar,uLocalDestVar='',uTokenizeString=u''):
        """ The Main Parse Function """
        self.uGlobalDestVar         = uGlobalDestVar
        self.uLocalDestVar          = uLocalDestVar
        self.uGlobalTokenizeString  = uTokenizeString

        if uGetVar.startswith('ORCAMULTI'):
            uTmpGetVar        = ToList(uGetVar[9:])
            uTmpLocalDestVar  = ToList(uLocalDestVar)
            uTmpGlobalDestVar = ToList(uGlobalDestVar)
            uRet1=''
            uRet2=''
            for iIndex, uGetVar in enumerate(uTmpGetVar):
            #for iIndex in range(len(uTmpGetVar)):
            #    uGetVar = uTmpGetVar[iIndex]
                if iIndex < len(uTmpLocalDestVar):
                    self.uLocalDestVar = uTmpLocalDestVar[iIndex]
                if iIndex < len(uTmpGlobalDestVar):
                    self.uGlobalDestVar = uTmpGlobalDestVar[iIndex]
                uRet1,uRet2 = self.ParseSingle(uResponse,uGetVar,uParseResultOption,uTokenizeString)
                self.uLocalDestVar          = uLocalDestVar
                self.uGlobalTokenizeString  = uTokenizeString
            return uRet1,uRet2
        return self.ParseSingle(uResponse,uGetVar,uParseResultOption,uTokenizeString)

    def _SetVar(self,uValue,uDebugMessage,uAddName=u''):
        """ Sets the vars, which contains the parse results """
        if self.uLocalDestVar != u'':
            self.ShowDebug(u'Local: %s : [%s]=[%s]' % (uDebugMessage,self.uLocalDestVar+uAddName,uValue))
            SetVar(uVarName = self.uLocalDestVar+uAddName, oVarValue = uValue, uContext = self.uContext)
        if self.uGlobalDestVar != u'':
            if self.uGlobalDestVar.startswith("$var("):
                self.uGlobalDestVar=ReplaceVars(self.uGlobalDestVar)
            self.ShowDebug(u'Global: %s : [%s]=[%s]' %(uDebugMessage,self.uGlobalDestVar+uAddName,uValue))
            SetVar(uVarName = self.uGlobalDestVar+uAddName, oVarValue = uValue)
            SetVar(uVarName = "RESULT", oVarValue = uValue)
            SetVar(uVarName = "GLOBALDESTVAR", oVarValue = self.uGlobalDestVar+uAddName)

    def SetVar2(self, uValue, uLocalDestVar, uGlobalDestVar, uDebugMessage, uAddName=u''):
        """ As _SetVar, but with given var names """
        self.uGlobalDestVar         = uGlobalDestVar
        self.uLocalDestVar          = uLocalDestVar
        return self._SetVar(uValue=uValue,uDebugMessage=uDebugMessage,uAddName=uAddName)

    def ParseSingle(self,uResponse,uGetVar,uParseResultOption, uTokenizeString=u''):
        """ Parses a single result """

        if uParseResultOption == '':
            uParseResultOption = self.uGlobalParseResultOption

        if uParseResultOption == u'no' or uParseResultOption == u'':
            return u'',u''

        self.ShowDebug(u'Response: '+ToUnicode(uResponse))
        try:
            if uParseResultOption == u'store':
                return self._Parse_Store(uResponse,uGetVar)
            if uParseResultOption == u'json':
                return self._Parse_Json(uResponse,uGetVar)
            if uParseResultOption == u'tokenize':
                return self._Parse_Tokenize(uResponse,uGetVar,uTokenizeString)
            if uParseResultOption == u'xml':
                return self._Parse_XML(uResponse,uGetVar)
            if uParseResultOption == u'dict':
                return self._Parse_Dict(uResponse,uGetVar)
        except Exception as e:
            self.ShowError(u'can\'t Parse Result',oException=e)
            return u'',u''
        return u'',u''

    def _Parse_Store(self,uResponse,uGetVar):
        """ Just stores the result """
        uResponse = ToUnicode(uResponse)
        self._SetVar(uResponse,u'Storing Responses')
        return u'',uResponse

    def _Parse_Tokenize(self,uResponse,uGetVar,uParseResultTokenizeString):
        """ tokenizes the result """
        uCmd = u''
        if uResponse == '':
            self._SetVar(uResponse,u'_Parse_Tokenize: Storing Empty Response')
            return uGetVar,uResponse
        else:
            aLines = uResponse.splitlines()
            for uLine in aLines:
                if uParseResultTokenizeString == u'':
                    uParseResultTokenizeString=self.uGlobalTokenizeString
                #tResp=uResponse.split(uParseResultTokenizeString)
                tResp=uLine.split(uParseResultTokenizeString)
                if len(tResp) == 2:
                    uResponse   = tResp[1]
                    uCmd        = tResp[0]
                    self._SetVar(uResponse,u'Tokenized one result',uCmd)

                elif len(tResp)>2:
                    i = 1
                    while i < len(tResp):
                        uResponse   = tResp[1]
                        uCmd        = tResp[0]
                        self._SetVar(uResponse,u'Tokenized multi results',uCmd+"_"+ToUnicode(i))
                        i+= 1
                else:
                    self._SetVar(uResponse,u'No Tokens found, storing result')
        return uCmd,uResponse
    def ParseResult_JsonHeader(self,uResponse):
        """ Parses a json header """
        try:
            tJsonResponse = json.loads(uResponse)
            uID = u''
            uMethod = tJsonResponse.get(u'method')
            if uMethod is None:
                uMethod = u''
            uID=tJsonResponse.get(u'id')
            if uID is None:
                uID = u''
            return uMethod,uID
        except Exception as e:
            self.ShowError(u'Invalid JSON Response Header:'+uResponse,oException=e)
            return u'',u''

    def _Parse_Json(self,uOrgResponse,uGetVar):
        """ parses the result a json """
        uResponse     = ToUnicode(uOrgResponse)
        uResponse2    = ToUnicode(uOrgResponse)
        tJsonResponse = uResponse

        try:
            tJsonResponse = json.loads(uResponse)
        except Exception as e:
            #uResponse = uResponse.replace("'", "blalala")
            #uResponse = uResponse.replace('"', "'")
            #uResponse = uResponse.replace("blalala",'"')

            uResponse=fixLazyJsonWithComments(uResponse)

            try:
                tJsonResponse = json.loads(uResponse)
            except Exception as e:
                # uResponse     = uResponse.replace('u"', '"')
                # uResponse     = uResponse.replace('u"', "'")
                if "u'" in uResponse:
                    uResponse     = uResponse.replace("u'", '"')
                    uResponse     = uResponse.replace("'", '"')
                    tJsonResponse = json.loads(uResponse)

        lGetVars = uGetVar.split(',')
        uResult  = tJsonResponse
        iIndex   = 0
        UnSplit(lGetVars)
        if uGetVar == u'':
            return u'',u''
        for uVar in lGetVars:
            self.ShowDebug(u'Parsing Vartoken:' + uVar + " in:"+uResponse)
            iIndex=iIndex+1
            # we split [aa=bb,ccc}
            uVar = uVar.split(',')
            #and remove the brackets
            if len(uVar)>1:
                if uVar[0].startswith(u'['):
                    uVar[0] = uVar[0][1:]
                if uVar[1].endswith(u']'):
                    uVar[1] = uVar[1][:-1]
            #If we got a dict
            if isinstance(uResult,dict):
                self.ShowDebug(u'Parsing Result as Dict')
                # and should only receive one value, its simple, we do it
                if len(uVar) == 1:
                    uResult = uResult.get(uVar[0])
                # If we have to pull a specific value from a dict, than use the specific one (Not Testet: ToDo: Needs to reworked as soon as i got an example)
                else:
                    uResult = uResult.get(uVar[1])
            #If we got a list
            elif isinstance(uResult,list):
                self.ShowDebug(u'Parsing Result as List')
                #if we need nothing special, then use the first one
                if len(uVar) == 1:
                    if len(uResult) > 0:
                        uResult = uResult[0]
                        self.ShowDebug(u'Parsing Result as List, pulling first element:' + uResponse)
                else:
                    self.ShowDebug(u'Parsing Result as List: Pulling given Value')
                    #now it gets complicated
                    # Lets split the first part (xxx=yyy
                    lTmp=uVar[0].split('=')
                    if len(lTmp) == 2:
                        for oTmpResult in uResult:
                            if isinstance(oTmpResult,dict):
                                uFinalResult = u''
                                bFound       = False
                                for uKey, uValue in oTmpResult.items():
                                    if uKey == uVar[1]:
                                        uFinalResult = uValue
                                    if uKey == lTmp[0]:
                                        if uValue == lTmp[1]:
                                            bFound = True
                                if bFound:
                                    uResult = uFinalResult
                                    break
                        #sResult=sResult.get(lTmp[1])
                    else:
                        uResult = uResult[0]
            if iIndex == len(lGetVars):
                if isinstance(uResult, int) or isinstance(uResult, str) or isinstance(uResult, float):
                    uResult = ToUnicode(uResult)
                if isinstance(uResult, string_types):
                    self._SetVar(uResult,u'JSON:Storing Value')
                    return uVar,uResult
                else:
                    self.ShowError(u'Incomplete parse options')
                    self._SetVar(uResponse2,u'Storing incomplete Value')
                    return uVar,uResponse2
        return u'',u''
    def _Parse_Dict(self,uResponse,uGetVar):
        """ parses the result as dict """
        uResult = uResponse
        if isinstance(uResponse,dict):
            uResult = uResponse.get(uGetVar)
            if uResult is not None:
                uResult = ToUnicode(uResult)
                self._SetVar(uResult,u'Dictionary value')
                return uGetVar,uResult
        return u'',u''
    def _Parse_XML(self,uResponse,uGetVar):
        """ parses the result as xml """

        if uResponse == u'':
            return u'', u''


        lGetVars    = uGetVar.split(',')
        uResult     = uResponse
        iIndex      = 0
        UnSplit(lGetVars)

        if uGetVar == u'':
            return u'',u''
        oNode = ElementTree(fromstring(uResult))
        for uVar in lGetVars:
            self.ShowDebug(u'Parsing Vartoken:' + uVar + " in:"+uResponse)
            iIndex = iIndex+1
            if iIndex != len(lGetVars):
                oNode = oNode.find(uVar)
                if oNode is None:
                    self.ShowError(u'can\'t Find xml Value')
                    return u'',u''
            else:
                uResult = GetXMLTextValue(oNode,uVar,False,u'notfound')
                self._SetVar(uResult,u'Storing Value')
                return uVar,uResult
        return u'',u''

    def ShowDebug(self,uMsg):
        """ Creates a parser debug message """
        if self.uDebugContext != u'':
            uRet=self.uDebugContext + u': ' + uMsg
        else:
            uRet = uMsg

        Logger.debug (uRet)
        return uRet

    def ShowInfo(self,uMsg):
        """ Creates a parser info message """
        if self.uDebugContext != u'':
            uRet=self.uDebugContext + u': ' + uMsg
        else:
            uRet = uMsg
        Logger.info (uRet)
        return uRet

    def ShowError(self,uMsg, uParConfigName=None,oException=None):
        """ Creates a parser error message """
        iErrNo = 0

        if oException is not None:
            if hasattr(oException,'errno'):
                iErrNo = oException.errno
        if iErrNo is None:
            iErrNo = 12345
        uRet = LogError (self.uDebugContext+u': '+ uMsg + " (%d) " % (iErrNo),oException)
        return uRet

def fixLazyJsonWithComments (in_text):
    """ Same as fixLazyJson but removing comments as well """

    result = []
    tokengen = tokenize.generate_tokens(StringIO(in_text).readline)

    sline_comment = False
    mline_comment = False
    last_token = ''

    for tokid, tokval, _, _, _ in tokengen:
        # ignore single line and multi line comments
        if sline_comment:
            if (tokid == token.NEWLINE) or (tokid == tokenize.NL):
                sline_comment = False
            continue

        # ignore multi line comments
        if mline_comment:
            if (last_token == '*') and (tokval == '/'):
                mline_comment = False
                last_token = tokval
            continue

        # fix unquoted strings
        if tokid == token.NAME:
            if tokval not in ['true', 'false', 'null', '-Infinity', 'Infinity', 'NaN']:
                tokid = token.STRING
                tokval = u'"%s"' % tokval

        # fix single-quoted strings
        elif tokid == token.STRING:
            if tokval.startswith ("'"):
                tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')

        # remove invalid commas
        elif tokid == token.OP and (tokval == '}' or tokval == ']'):
            if len(result) > 0 and result[-1][1] == ',':
                result.pop()

        # detect single-line comments
        elif tokval == "//":
            sline_comment = True
            continue

        # detect multiline comments
        elif last_token == '/' and tokval == '*':
            result.pop() # remove previous token
            mline_comment = True
            continue

        result.append((tokid, tokval))
        last_token = tokval

    return tokenize.untokenize(result)

def FindNameSpace(uVar):
    """ Helper function for xml to find the namespace """
    uNS   = ''
    uRet  = uVar
    iPos  = uVar.find('}')
    if iPos != -1:
        uNS  = uVar[:iPos+1]
        uRet = uVar[iPos+1:]
    else:
        iPos = uVar.find(':')
        if iPos != -1:
            uNS  = uVar[:iPos+1]
            uRet = uVar[iPos+1:]
    return uNS,uRet

def RemoveNameSpaceFromVar(uVar):
    """ Helper function for xml to remove the namespace """
    uRet = uVar
    iPos = uVar.find('}')
    if iPos != -1:
        uRet = uVar[iPos+1:]
    else:
        iPos = uVar.find(':')
        if iPos !=-1:
            uRet = uVar[iPos+1:]
    return uRet

def RemoveNameSpaceFromXml(doc, ns):
    """ Remove namespace in the passed document in place. """
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]
        for oChild in elem._children:
            RemoveNameSpaceFromXml(oChild, ns)
