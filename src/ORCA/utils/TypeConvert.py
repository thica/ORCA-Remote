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

import ast
import json
import demjson

from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
from typing import Any
from typing import cast


from xml.etree.ElementTree  import Element
from xml.etree.ElementTree  import fromstring
from collections            import OrderedDict
from ORCA.utils.LogError    import LogError, LogErrorSmall

import html

__all__ = ['ToBool',
           'ToDic',
           'ToFloat',
           'ToFloat2',
           'ToHex',
           'ToHexFromString',
           'ToInt',
           'ToIntVersion',
           'ToList',
           'ToOrderedDic',
           'ToString',
           'ToStringVersion',
           'ToUnicode',
           'ToBytes',
           'UnEscapeUnicode',
           'EscapeUnicode',
           'DictToUnicode',
           'XMLToDic'
          ]

def ToHex(iInt:int,iLen:int=2)->str:
    """
    Converts as integer to a hex string

    :param iInt: Integer value to convert
    :param iLen: Optional: output len, default = 2
    :return: The Hex String
    """

    uTmp:str = "0"*iLen+hex(iInt)
    uTmp     = uTmp.replace('x', '0')
    uTmp     = uTmp[iLen*-1:]
    return uTmp

def ToBytes(uStr:str) -> bytes:
    """
    Converts as string to bytes

    :param uStr: input string
    :return: The bytes string
    """

    if isinstance(uStr, bytes):
        return cast(bytes,uStr)

    byRet:bytes = cast(bytes,uStr)
    try:
        byRet = bytes(uStr, 'utf-8')
    except Exception as e:
        LogError(uMsg=u'ToBytes: Convert error, using fallback', oException=e)

    return byRet

def ToHexFromString(uString:str) -> str:
    """
    Converts a string to a hex string
    :param uString: the string to convert to a hex string
    :return: A hex string representation of a string
    """
    return ":".join("{:02x}".format(ord(c)) for c in uString)

def DictToUnicode(vObj:Union[Dict,List,bool,str,None]) -> str:
    """
    Converts a dict to a string, without the u' prefix for unicode strings
    :return: The string represenation
    """
    try:

        if isinstance(vObj, dict):
            if len(vObj)==0:
                return "{}"

            uRet=u'{'
            for key, value in vObj.items():
                uRet=uRet+DictToUnicode(key)+": "+DictToUnicode(value)+","
            return uRet[:-1]+u'}'
        elif isinstance(vObj, list):
            if len(vObj)>0:
                uRet = "["
                for value in vObj:
                    uRet+=DictToUnicode(value)+","
                uRet =  uRet[:-1] +"]"
                return uRet
            return "[]"
        elif isinstance(vObj, bool):
            return ToUnicode(vObj).lower()
        elif isinstance(vObj, str):
            return '"'+vObj+'"'
        elif vObj is None:
            return '"none"'
        else:
            return ToUnicode(vObj)
    except Exception as e:
        LogError(uMsg=u'DictToUnicode: Dictionary Conver error, using fallback',oException=e)
        return ToUnicode(str(vObj))

def ToString(uObj:str) -> bytes:
    """
    Converts an unicode string into a string

    :param string uObj:
    :return: The converted string (not unicode)
    """
    return uObj.encode('ascii', 'xmlcharrefreplace')


def ToUnicode(Obj):
    """
    Converts an object into a unicode string

    :rtype: string
    :param Obj: any object to be converted
    :return: A nunicode string of Obj
    """

    if isinstance(Obj, dict):
        return DictToUnicode(Obj)

    if isinstance(Obj, str):
        return Obj

    try:
        if isinstance(Obj, bytes):
            return Obj.decode("utf-8")
        else:
            return str(Obj)
    except Exception as e:
        LogError(uMsg=u'Unicode Transfer Error',oException=e)
        print ('[',Obj,']')
        print (type(Obj))
        if isinstance(Obj, str):
            for cChar in Obj:
                print (ord(cChar)),
            print ('')

    return Obj

def ToOrderedDic(uString:str) -> OrderedDict:
    """
    converts a (unicode) string into a ordered dict

    :rtype: OrderedDict
    :param uString: The string representation of a dict
    :return: The ordered Dict
    """

    dDict = OrderedDict()
    aList:List[str]
    uPair:str
    uFinalstring:str
    aKeyValue:List
    uName:str
    uValue:str

    try:
        uFinalstring = uString.strip(' \n{}')
        aList = uFinalstring.split(",")
        for uPair in aList:
            if ":" in uPair:
                aKeyValue = uPair.split(":")
                uName=aKeyValue[0].strip(' \n\"')
                uValue=aKeyValue[1].strip(' \n\"')
                dDict[uName] = uValue
    except Exception as e:
        LogError(uMsg=u'ToOrderedDic: Dictionary Convert error',oException=e)
        LogError(uMsg=uString)

    return dDict


def ToDic(uString:str) -> Dict:
    """
    converts a (unicode) string into a dict

    :rtype: dict
    :param uString: The string representation of a dict
    :return: The dict
    """

    dRet:Dict
    uString2:str

    if isinstance(uString, dict):
        return cast(Dict,uString)

    if uString==u'':
        return {}

    try:
        if uString.startswith(u'{'):
            try:
                return json.loads(uString)
            except Exception:
                pass

        try:
            return demjson.decode(uString)
        except Exception:
            pass

        try:
            if "\\" in uString:
                uString2 = uString.replace("\\","***BaCkSlAsH***")
                dRet     = ast.literal_eval(uString2)
                DictUnescaceBackslash(dRet)
                return dRet
            else:
                return ast.literal_eval(uString)
        except Exception:
            pass

        uString = uString.replace("\'", "\"")

        if uString.startswith(u'{'):
            try:
                return json.loads(uString)
            except Exception:
                pass

        try:
            return ast.literal_eval(uString)
        except Exception:
            pass

        LogError(uMsg=u'ToDic: can\'t convert string to dic:'+uString)
        return {}

    except Exception as e:
        LogErrorSmall(uMsg=u'ToDic: Dictionary Convert error',oException=e)
        LogErrorSmall(uMsg=uString)
    return {}

def DictUnescaceBackslash(oDict:Dict) -> None:
    """
    Unescapes previous escapes backslashes in dict strings
    :param dict oDict:
    """

    uKey:str
    vValue:Any
    vElem:Any

    try:
        for uKey, vValue in oDict.items():
            if isinstance(vValue, dict):
                DictUnescaceBackslash(vValue)
            elif isinstance(vValue, str):
                oDict[uKey]=oDict[uKey].replace("***BaCkSlAsH***","\\")
            elif isinstance(vValue, list):
                for vElem in vValue:
                    DictUnescaceBackslash(vElem)
    except Exception as e:
        LogError(uMsg=u'DictUnescaceBackslash',oException=e)


def ToList(uString:str) -> List:
    """
    converts a (unicode) string into a list
    Standard format should be "['par1','par2']"

    :param uString: A string representation of a list
    :return: The list
    """

    aRet:List
    uItem:str

    if isinstance(uString, list):
        return uString

    if uString=="" or uString=="[]" or uString=="u[]":
        return []

    try:
        return ast.literal_eval(uString)
    except:
        pass

    try:
        if uString.startswith("["):
            return ast.literal_eval(uString[1:-1])
    except:
        pass

    if not "," in uString:
        if uString.startswith("["):
            return [uString[1:-1]]
        else:
            return [uString]

    try:
        aRet = []
        for uItem in uString.split(","):
            aRet.append(uItem)
        return aRet

    except Exception as e:
        LogError(uMsg=u'ToList: List Convert error',oException=e)
        LogError(uMsg=uString)
        uRet= [uString]
    return uRet


def ToInt(vValue:Union[str,float]) -> int:
    """
    converts a (unicode) string into an integer
    (0) in case of an error

    :rtype: int
    :param string|float vValue: The string representation of an integer number
    :return: The integer value
    """
    try:
        return int(vValue)
    except Exception:
        return 0

def ToBool(vValue:Union[str,bool]) -> bool:
    """
    converts a (unicode) string into a bool

    :rtype: bool
    :param  vValue: The string  representation of a boolean value , can be (0/1) or True/False (case independent)
    :return: The boolean value
    """

    if isinstance(vValue,bool):
        return vValue

    uString=ToUnicode(vValue)
    return uString.lower() in ['true', '1']


def ToFloat(uString:str) -> float:
    """
    converts a (unicode) string into a float number
    (0.0) in case of an error

    :rtype: float
    :param uString: The string representation of a float number
    :return: The float value
    """

    try:
        return float(uString)
    except Exception:
        return 0.0

def ToFloat2(uValue:str) -> Tuple[float,bool]:
    """
    converts a (unicode) string into a float number and returns, if conversion was successful
    (0.0) in case of an error

    :rtype: tuple(float, bool)
    :param string uValue: The string representation of a float number
    :return: A tuple of the float value and a boolean value
    """

    ''' converts a (unicode) string into a float and returns, if coversion was sucessfull '''
    try:
        return float(uValue),True
    except Exception:
        return 0.0,False

def ToStringVersion(iVersion:int) -> str:
    """
    converts an integer representation of a version to a version string

    :rtype: string
    :param int iVersion:
    :return: A string representation of the version
    """

    sVersion1:str
    sVersion2:str
    sVersion3:str

    sVersion1 = str((int(iVersion / 1000000)))
    sVersion2 = str(int ((iVersion % 1000000) / 1000))
    sVersion3 = str(int ((iVersion % 1000)))
    return "%s.%s.%s" % (sVersion1,sVersion2,sVersion3)

def ToIntVersion(uVersion:str) -> int:
    """
    converts a version string into a integer version number
    maxium 2 dots (3 section are allowed
    maxium 3 digits per section allowed
    eg 1.1.10

    :rtype: int
    :param str uVersion: The string representation of a version
    :return: The integer representation of a version
    """

    aParts:List=uVersion.split('.')
    aResult:List=[0,0,0]
    i:int=0
    uSection:str
    uNumber:int

    for uSection in aParts:
        uNumber=ToInt(uSection)
        aResult[i]=uNumber
        i+=1

    return aResult[0]*1000000 +aResult[1]*1000 + aResult[2]

def UnEscapeUnicode(uObj:str) -> str:
    """
    Converts unicode escapes (html escapes) into unicode values

    :rtype: str
    :param uObj: The unicode string to unescape unicode (html) escapes
    :return: Unescaped unicode value
    """

    return html.unescape(uObj)


def EscapeUnicode(uObj:str) -> str:
    """
    Escapes unicode character (non ASCII) to html escapes

    :rtype: str
    :param str uObj: The unicode string to escape unicode  values
    :return: Escaped unicode value (should be ASCII conform)
    """

    return ToUnicode(uObj.encode('ascii', 'xmlcharrefreplace'))


def XMLToDic(vElement:Union[Element,str]) -> Dict:
    """
    converts a xml structure into a dic

    :param vElement: An Elementree Node to convert, or a string representing a xml structure
    :return: The converted Dictionary
    """

    oElement:Element

    try:
        if isinstance(vElement,str):
            oElement = fromstring(cast(str,vElement))
        else:
            oElement = cast(Element,vElement)

        return cXMLToDic(oElement).getDict()
    except Exception as e:
        LogError(uMsg=u'XMLToDic: XML Convert error',oException=e)
        LogError(uMsg=str(vElement))
        return {}


class cXMLToDic(dict):
    """
    Converts a Elementree xml node into a dictionary
    """

    def __init__(self, oParentElement: Element):
        super().__init__()
        self.XML_Attributes:Element = oParentElement
        self.addAttributes(self.XML_Attributes,self)
        oChild:Element
        for oChild in list(oParentElement):
            oChild.text = oChild.text if (oChild.text is not None) else ' '
            if len(oChild) == 0:
                self.update(self._addToDict(uKey= oChild.tag, oValue = oChild.text.strip(), dDict = self))
                self.addAttributes(oChild,self)
            else:
                dInnerChild = cXMLToDic(oParentElement=oChild)
                self.update(self._addToDict(uKey=dInnerChild.XML_Attributes.tag, oValue=dInnerChild, dDict=self))

    def getDict(self)->Dict:
        """
        Return the attributes as a dict
        """
        return {self.XML_Attributes.tag: self}

    # noinspection PyMethodMayBeStatic
    def addAttributes(self,oNode: Element,dDict:Dict):
        """
        Adds the xml attributes into the Dict tree
        :param oNode: The xml node to parse the attributes
        :param dDict: The target dict to store the attributes
        """
        for uAttribute in oNode.attrib:
            uValue = oNode.get(uAttribute, default="")
            if uValue:
                if not "attributes" in dDict:
                    dDict["attributes"] = {}
                dDict["attributes"][uAttribute]=uValue
                for iIndex in range(1000):
                    sTag = uAttribute+"[%s]" % iIndex
                    if not sTag in dDict["attributes"]:
                        dDict["attributes"][sTag] = uValue
                        if iIndex>0:
                            del dDict["attributes"][uAttribute]
                        break

    class _addToDict(dict):
        def __init__(self, uKey: str, oValue, dDict: Dict):
            super().__init__()
            if not uKey in dDict:
                self.update({uKey: oValue})
            else:
                identical = dDict[uKey] if type(dDict[uKey]) == list else [dDict[uKey]]
                self.update({uKey: identical + [oValue]})
