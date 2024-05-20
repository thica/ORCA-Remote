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
from typing import Tuple
from typing import List
from typing import Dict
from typing import Any

import  tokenize
import  token
from    io import StringIO
import  json

from    kivy.logger             import Logger
from    ORCA.utils.LogError     import LogError
from    ORCA.utils.TypeConvert  import ToList
from    ORCA.utils.TypeConvert  import ToUnicode
from    ORCA.utils.TypeConvert  import ToDic
from    ORCA.utils.TypeConvert  import XMLToDic
from    ORCA.utils.ParseDict    import ParseDictKeyTree
from    ORCA.utils.ParseDict    import ParseDictAny
from    ORCA.utils.ParseDict    import ParseDictAll
from    ORCA.vars.Replace       import ReplaceVars
from    ORCA.vars.Access        import SetVar

class cResultParser:
    """ Object to parse results
    ParseFlags:

    L = we parse a list of getvars
    U = Undefined we Parse the first Value
    E = We parse and extend the complete dict/xml


    """
    def __init__(self):
        self.uDebugContext:str              = ''
        self.uContext:str                   = ''
        self.uGlobalDestVar:str             = ''
        self.uLocalDestVar:str              = ''
        self.uParseResultOption:str         = ''
        self.uGlobalParseResultOption:str   = ''
        self.uGlobalTokenizeString:str      = ''

    def Parse(self,*,uResponse:str,uGetVar:str,uParseResultOption:str,uGlobalDestVar:str,uLocalDestVar:str='',uTokenizeString:str='',uParseResultFlags:str='')->Tuple[str,str]:
        """ The Main Parse Function """
        self.uGlobalDestVar         = uGlobalDestVar
        self.uLocalDestVar          = uLocalDestVar
        self.uGlobalTokenizeString  = uTokenizeString

        if 'L' in uParseResultFlags:
            aTmpGetVar:List        = ToList(uGetVar)
            aTmpLocalDestVar:List  = ToList(uLocalDestVar)
            aTmpGlobalDestVar:List = ToList(uGlobalDestVar)
            uRet1:str=''
            uRet2:str=''
            for iIndex, uGetVar in enumerate(aTmpGetVar):
                if iIndex < len(aTmpLocalDestVar):
                    self.uLocalDestVar = aTmpLocalDestVar[iIndex]
                if iIndex < len(aTmpGlobalDestVar):
                    self.uGlobalDestVar = aTmpGlobalDestVar[iIndex]
                uRet1,uRet2 = self.ParseSingle(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)
                self.uLocalDestVar          = uLocalDestVar
                self.uGlobalTokenizeString  = uTokenizeString
            return uRet1,uRet2
        return self.ParseSingle(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    def _SetVar(self,uValue:str,uDebugMessage:str,uAddName:str='')->None:
        """ Sets the vars, which contains the parse results """
        if self.uLocalDestVar != '':
            self.ShowDebug(f'Local:  {uDebugMessage} : [{self.uLocalDestVar + uAddName}]=[{uValue}]')
            SetVar(uVarName = self.uLocalDestVar+uAddName, oVarValue = uValue, uContext = self.uContext)
        if self.uGlobalDestVar != '':
            if self.uGlobalDestVar.startswith('$var('):
                self.uGlobalDestVar=ReplaceVars(self.uGlobalDestVar)
            self.ShowDebug(f'Global: {uDebugMessage} : [{self.uGlobalDestVar + uAddName}]=[{uValue}]')
            SetVar(uVarName = self.uGlobalDestVar+uAddName, oVarValue = uValue)
            SetVar(uVarName = 'RESULT', oVarValue = uValue)
            SetVar(uVarName = 'GLOBALDESTVAR', oVarValue = self.uGlobalDestVar+uAddName)

    def SetVar2(self, uValue:str, uLocalDestVar:str, uGlobalDestVar:str, uDebugMessage:str, uAddName:str='')->None:
        """ As _SetVar, but with given var names """
        self.uGlobalDestVar         = uGlobalDestVar
        self.uLocalDestVar          = uLocalDestVar
        return self._SetVar(uValue=uValue,uDebugMessage=uDebugMessage,uAddName=uAddName)

    def ParseSingle(self,*,uResponse:str,uGetVar:str,uParseResultOption:str, uTokenizeString:str='', uParseResultFlags='')->Tuple[str,str]:
        """ Parses a single result """

        tRetDefault:Tuple = '',''

        if uParseResultOption == '':
            uParseResultOption = self.uGlobalParseResultOption

        self.ShowDebug('Response: '+ToUnicode(uResponse))

        if uParseResultOption == 'no' or uParseResultOption == '':
            return tRetDefault

        if uParseResultOption != 'store' and uParseResultOption != 'tokenize' and uGetVar=='' and not 'E' in uParseResultFlags and uParseResultOption!="list":
            return tRetDefault

        try:
            match uParseResultOption:
                case 'store':       return self._Parse_Store(uResponse)
                case 'tokenize':    return self._Parse_Tokenize(uResponse,uGetVar,uTokenizeString)
                case 'xml':         return self._Parse_XML(uResponse,uGetVar,uParseResultFlags)
                case 'dict':        return self._Parse_Dict(uResponse,uGetVar,uParseResultFlags)
                case 'list':        return self._Parse_List(uResponse)
                case 'json':
                    if uGetVar or "E" in uParseResultFlags:
                        return self._Parse_Json(uResponse,uGetVar,uParseResultFlags)
                case _:              pass
        except Exception as e:
            self.ShowError('Can\'t parse result',oException=e)
            return tRetDefault
        return tRetDefault

    def _Parse_Store(self,uResponse:str) ->Tuple:
        """ Just stores the result """
        uResponse = ToUnicode(uResponse)
        self._SetVar(uResponse,'Storing Responses')
        return '',uResponse

    def _Parse_Tokenize(self,uResponse:str,uGetVar:str,uParseResultTokenizeString:str)->Tuple:
        """ tokenizes the result """
        uCmd:str = ''
        if uResponse == '':
            self._SetVar(uResponse,'_Parse_Tokenize: Storing Empty Response')
            return uGetVar,uResponse
        else:
            aLines:List = uResponse.splitlines()
            for uLine in aLines:
                if uParseResultTokenizeString == '':
                    uParseResultTokenizeString=self.uGlobalTokenizeString
                tResp:Tuple[str]=uLine.split(uParseResultTokenizeString)
                if len(tResp) == 2:
                    uResponse:str   = tResp[1]
                    uCmd:str        = tResp[0]
                    self._SetVar(uResponse,'Tokenized one result',uCmd)
                elif len(tResp)>2:
                    i:int = 1
                    while i < len(tResp):
                        uResponse:str   = tResp[1]
                        uCmd:str        = tResp[0]
                        self._SetVar(uResponse,'Tokenized multi results',uCmd+"_"+ToUnicode(i))
                        i+= 1
                else:
                    self._SetVar(uResponse,'No Tokens found, storing result')
        return uCmd,uResponse

    def _Parse_Json(self,uResponse:str,uGetVar:str,uParseResultFlags:str)->Tuple:
        """ parses the result a json """
        uResponse:str       = ToUnicode(uResponse)
        tJsonResponse:Dict  = {}

        try:
            tJsonResponse = json.loads(uResponse)
        except:
            uResponse=fixLazyJsonWithComments(uResponse)
            try:
                tJsonResponse = json.loads(uResponse)
            except Exception:
                if 'u\'' in uResponse:
                    uResponse     = uResponse.replace('u\'', '\'')
                    uResponse     = uResponse.replace('"', '\'')
                    tJsonResponse = json.loads(uResponse)
        return self._Parse_Dict(uResponse=tJsonResponse,uGetVar=uGetVar,uParseResultFlags=uParseResultFlags)

    def _Parse_Dict(self,uResponse:Any,uGetVar:str,uParseResultFlags:str)->Tuple:
        """ parses the result as dict """
        uResult:str = ''
        aResult:List
        if not isinstance(uResponse,dict):
            uResponse = ToDic(uResponse)
        if isinstance(uResponse,dict):
            if 'U' in uParseResultFlags:
                aResult = ParseDictAny(vObj=uResponse,uSearchKey=uGetVar)
            else:
                if 'E' in uParseResultFlags:
                    dResult=ParseDictAll(vObj=uResponse,uPrefix='')
                    uLocalDestVar  = self.uLocalDestVar
                    uGlobalDestVar = self.uGlobalDestVar
                    for uFoundKey, uValue in dResult.items():
                        if uLocalDestVar:
                            self.uLocalDestVar = uLocalDestVar + '%s' % uFoundKey
                        if uGlobalDestVar:
                            self.uGlobalDestVar = uGlobalDestVar + '%s' % uFoundKey
                        self._SetVar(uValue, 'Dictionary value')
                    self.uLocalDestVar  = uLocalDestVar
                    self.uGlobalDestVar = uGlobalDestVar
                    aResult=[]
                else:
                    aResult = ParseDictKeyTree(vObj=uResponse, aKeys=ToList(uGetVar))

            if aResult:
                if not "A" in uParseResultFlags:
                    uResult = ToUnicode(aResult[0])
                    self._SetVar(uResult,'Dictionary value')
                else:
                    iIndex = 0
                    uLocalDestVar  = self.uLocalDestVar
                    uGlobalDestVar = self.uGlobalDestVar
                    for uResult in aResult:
                        if uLocalDestVar:
                            self.uLocalDestVar = uLocalDestVar + '[%d]' % iIndex
                        if uGlobalDestVar:
                            self.uGlobalDestVar = uGlobalDestVar + '[%d]' % iIndex
                        self._SetVar(uResult, 'Dictionary value')
                        iIndex += 1
                    self.uLocalDestVar  = uLocalDestVar
                    self.uGlobalDestVar = uGlobalDestVar
            else:
                self._SetVar(uResult, 'Dictionary value')
            return uGetVar,uResult
        else:
            self.ShowDebug('Warning: can\'t parse none dict as dict:' + ToUnicode(uResponse))
        return '',''

    def _Parse_XML(self,uResponse:str,uGetVar:str,uParseResultFlags:str)->Tuple:
        """ parses the result as xml """

        if uResponse == '':
            return '', ''

        dResponse = XMLToDic(uResponse)
        return self._Parse_Dict(uResponse=dResponse,uGetVar=uGetVar,uParseResultFlags=uParseResultFlags)


    def _Parse_List(self,uResponse:Any)->Tuple:
        """ parses the result as list """
        aResult:List = ToList(uResponse)
        uResult=ToUnicode(uResponse)
        if len(aResult)==0:
            return '', uResult
        i=0

        uLocalDestVar = self.uLocalDestVar
        uGlobalDestVar = self.uGlobalDestVar
        for uValue in aResult:
            if uLocalDestVar:
                self.uLocalDestVar = f"{uLocalDestVar}[{i}]"
            if uGlobalDestVar:
                self.uGlobalDestVar = f"{uGlobalDestVar}[{i}]"
            self._SetVar(uValue, 'List value')
            i+=1
        self.uLocalDestVar = uLocalDestVar
        self.uGlobalDestVar = uGlobalDestVar
        return '', uResult

    def ShowDebug(self,uMsg:str) ->str:
        """ Creates a parser debug message """
        if self.uDebugContext != '':
            uRet=self.uDebugContext + ': ' + uMsg
        else:
            uRet = uMsg

        Logger.debug (uRet)
        return uRet

    def ShowInfo(self,uMsg:str) ->str:
        """ Creates a parser info message """
        if self.uDebugContext != '':
            uRet=self.uDebugContext + ': ' + uMsg
        else:
            uRet = uMsg
        Logger.info (uRet)
        return uRet

    def ShowError(self,uMsg:str, oException:Any=None)-> str:
        """ Creates a parser error message """
        iErrNo:int = 0

        if oException is not None:
            if hasattr(oException,'errno'):
                iErrNo = oException.errno
        if iErrNo is None:
            iErrNo = 12345
        uRet = LogError (uMsg=self.uDebugContext +': ' + uMsg + ' (%d) ' % iErrNo, oException=oException)
        return uRet

def fixLazyJsonWithComments (in_text):
    """ Same as fixLazyJson but removing comments as well """

    result = []
    tokengen = tokenize.generate_tokens(StringIO(in_text).readline)

    sline_comment = False
    mline_comment = False
    last_token    = ''

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
                tokval = '"%s"' % tokval

        # fix single-quoted strings
        elif tokid == token.STRING:
            if tokval.startswith ("'"):
                tokval = '"%s"' % tokval[1:-1].replace ('"', '\\"')

        # remove invalid commas
        elif tokid == token.OP and (tokval == '}' or tokval == ']'):
            if len(result) > 0 and result[-1][1] == ',':
                result.pop()

        # detect single-line comments
        elif tokval == '//':
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

def FindNameSpace(uVar:str)-> Tuple:
    """ Helper function for xml to find the namespace """
    uNS:str   = ''
    uRet:str  = uVar
    iPos:int  = uVar.find('}')
    if iPos != -1:
        uNS  = uVar[:iPos+1]
        uRet = uVar[iPos+1:]
    else:
        iPos = uVar.find(':')
        if iPos != -1:
            uNS  = uVar[:iPos+1]
            uRet = uVar[iPos+1:]
    return uNS,uRet

def RemoveNameSpaceFromVar(uVar:str)-> str:
    """ Helper function for xml to remove the namespace """
    uRet:str = uVar
    iPos:int = uVar.find('}')
    if iPos != -1:
        uRet = uVar[iPos+1:]
    else:
        iPos = uVar.find(':')
        if iPos !=-1:
            uRet = uVar[iPos+1:]
    return uRet

def RemoveNameSpaceFromXml(doc, ns)-> None:
    """ Remove namespace in the passed document in place. """
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]
        # noinspection PyProtectedMember
        for oChild in elem._children:
            RemoveNameSpaceFromXml(oChild, ns)
