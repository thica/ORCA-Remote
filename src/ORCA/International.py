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

from typing import Dict
from typing import List
from typing import Optional

from xml.etree.ElementTree  import Element
from xml.etree.ElementTree  import ParseError
from xml.etree              import ElementInclude

from time                   import localtime
from time                   import struct_time

from kivy.logger            import Logger

from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.XML         import GetXMLTextAttribute
from ORCA.utils.XML         import GetXMLTextValue
from ORCA.utils.XML         import Orca_include
from ORCA.utils.XML         import Orca_FromString
from ORCA.utils.XML         import orca_et_loader
from ORCA.utils.XML         import LoadXMLFile

from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.LogError    import LogError
from ORCA.utils.CachedFile  import CachedFile

import ORCA.Globals as Globals

from ORCA.utils.FileName import cFileName

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.definition.Definition import cDefinition
else:
    from typing import TypeVar
    cDefinition = TypeVar("cDefinition")

def find_first_not_of(uString:str,iStartPos:int,cChar:str) -> int:
    """ Python adoption of C function to find the first character which is diffrent fom the given one """
    i:int    = iStartPos
    iLen:int =len(uString)
    while i<iLen:
        if not uString[i]==cChar:
            return i
        i += 1
    return -1

class cLocalesEntry:
    """ Object which represents a locales entry """
    def __init__(self):
        self.uName:str              = u''
        self.uLocale:str            = u''
        self.uDateShort:str         = u''
        self.uDateLong:str          = u''
        self.uTimeSymbolAM:str      = u''
        self.uTimeSymbolPM:str      = u''
        self.uTimeFormat:str        = u''
        self.uTempUnit:str          = u''
        self.uSpeedUnit:str         = u''

    def ParseXMLLocales(self,oXMLLocales:Element) -> None:
        """ reads the locales information from the xml (kodi file) """
        self.uName       = GetXMLTextAttribute(oXMLNode=oXMLLocales,uTag=u'name',  bMandatory=True, vDefault=u'')
        self.uLocale     = GetXMLTextAttribute(oXMLNode=oXMLLocales,uTag=u'locale',bMandatory=False,vDefault=u'EN')
        self.uDateShort  = GetXMLTextValue(oXMLNode=oXMLLocales,uTag=u'dateshort', bMandatory=False,vDefault=u'DD.MM.YYYY')
        self.uDateLong   = GetXMLTextValue(oXMLNode=oXMLLocales,uTag=u'datelong',  bMandatory=False,vDefault=u'DDDD, D MMMM YYYY')
        self.uTimeFormat = GetXMLTextValue(oXMLNode=oXMLLocales,uTag=u'time',      bMandatory=False,vDefault=u'H:mm:ss')
        oXMLTime:Element = oXMLLocales.find('time')
        if oXMLTime is not None:
            self.uTimeSymbolAM=GetXMLTextAttribute(oXMLNode=oXMLTime,uTag=u'symbolAM',bMandatory=False,vDefault=u'')
            self.uTimeSymbolPM=GetXMLTextAttribute(oXMLNode=oXMLTime,uTag=u'symbolPM',bMandatory=False,vDefault=u'')

class cLocales:
    """ a representation of all loaded locales entries for a language"""
    def __init__(self):
        self.oLocalesEntries:Dict[str,cLocalesEntry] = {}
    def LoadXmlFile(self) -> None:
        """ reads all locales for a language """
        self.oLocalesEntries.clear()
        try:
            oET_Root:Element    = LoadXMLFile(oFile=Globals.oFnLangInfo)
            oXMLRegions:Element = oET_Root.find(u'regions')
            if oXMLRegions is not None:
                for oXMLRegion in oXMLRegions.findall(u'region'):
                    self.__ParseXMLLocales(oXMLRegion)
        except ParseError as e:
            uMsg:str=LogError(uMsg=u'Language: Fatal Error:Load Locales XmlFile:',oException=e)
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=uMsg, bAbort=True)

    def __ParseXMLLocales(self,oXMLLocale:Element) -> None:
        """ reads a single locales entry and stores it in the locles list """
        oLocalesEntry:cLocalesEntry = cLocalesEntry()
        oLocalesEntry.ParseXMLLocales(oXMLLocale)
        self.oLocalesEntries[oLocalesEntry.uName]=oLocalesEntry

class cLanguage:
    """ The representation of a language (strings, locales, formats) """
    def __init__(self):
        self.dIDToString:Dict[str,str]                          = {}
        self.oLocales:cLocales                                  = cLocales()
        self.aLoadedFiles:List[str]                             = []
        self.oFnLanguagePrimary:Optional[cFileName]             = None
        self.oFnLanguageEnglish:Optional[cFileName]             = None
        self.oFnLanguageFallBackPrimary:Optional[cFileName]     = None
        self.oFnLanguageFallBackEngLish:Optional[cFileName]     = None

        # add some basic strings, even before we load the language files (for messages)
        self.SetString("5000", "Continue")
        self.SetString("5001", "Yes")
        self.SetString("5002", "No")
        self.SetString("5003", "Question")
        self.SetString("5004", "Quit ORCA?")
        self.SetString("5005", "Quit ORCA!")
        self.SetString("5006", "Info")
        self.SetString("5008", "OK")
        self.SetString("5009", "Cancel")
        self.SetString("5010", "Message")
        self.SetString("452",  "OK")


    def Init(self) -> None:
        self.oFnLanguagePrimary              = cFileName(Globals.oPathLanguageRoot + Globals.uLanguage) + u'strings.xml'
        self.oFnLanguageEnglish              = cFileName(Globals.oPathLanguageRoot + u'English') + u'strings.xml'
        self.oFnLanguageFallBackPrimary      = cFileName(Globals.oPathAppReal + u'languages/'+ Globals.uLanguage) + u'strings.xml'
        self.oFnLanguageFallBackEngLish      = cFileName(Globals.oPathAppReal + u'languages/English') + u'strings.xml'


    def SetString(self,uID:str,uText:str) -> None:
        """ sets a string """
        self.dIDToString[uID]=uText

    def StringIDToString(self,uID:str) -> str:
        """ returns the language string to a given language id """
        uRet:str = self.dIDToString.get(uID)
        if uRet is not None:
            return uRet
        else:
            Logger.warning (u'Language: No Language String found:'+uID)
        return uID

    def __LoadXMLNode(self,oET_Root:Element,dTarget:Dict[str,str]) -> None:

        uText: str
        sIndex: str

        if oET_Root.find(ElementInclude.XINCLUDE_INCLUDE) is not None:
            Orca_include(oET_Root ,orca_et_loader)

        oET_Strings:Element=oET_Root.find("strings")
        if oET_Strings is not None:
            self.__LoadXMLNode(oET_Strings,dTarget)

        for oXMLString in oET_Root.findall('string'):
            uText = oXMLString.text
            if uText is None:
                uText=u''
            uText  = ToUnicode(uText)
            sIndex = GetXMLTextAttribute(oXMLNode=oXMLString,uTag=u'id',bMandatory=True,vDefault=u"0")
            dTarget[sIndex]  = uText

    def _LoadXmlFile(self,oFnFile:cFileName) -> None:
        """ Loads all strings for the language from a specific files"""
        if not oFnFile.Exists():
            Logger.debug (u'Language: String File does not exist:'+oFnFile.string)
            return
        if oFnFile.string in self.aLoadedFiles:
            Logger.debug (u'Language: Skip duplicate language file loading:'+oFnFile.string)
            return

        oDef:Optional[cDefinition]=None

        try:
            uET_Data:str = CachedFile(oFileName=oFnFile)
            if Globals.uDefinitionContext:
                oDef = Globals.oDefinitions.get(Globals.uDefinitionContext)
            oET_Root = Orca_FromString(uET_Data=uET_Data,oDef=oDef,uFileName=oFnFile.string)
            self.__LoadXMLNode(oET_Root,self.dIDToString)
        except ParseError as e:
            uMsg:str=LogError(uMsg=u'Language: Fatal Error:Load Language XmlFile (xml parse error):'+oFnFile.string,oException=e)
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=uMsg, bAbort=True)
        except Exception as e:
            uMsg:str=LogError(uMsg=u'Language: Fatal Error:Load Language XmlFile (2):'+oFnFile.string,oException=e)
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=uMsg, bAbort=True)

    def Reset(self) -> None:
        """ clears all language strings """
        self.dIDToString.clear()
        del self.aLoadedFiles[:]

    # noinspection PyMethodMayBeStatic
    def LoadXMLLanguageFont(self, oFnFile:cFileName) -> int:
        iCountFonts:int = 0
        try:
            uET_Data            = CachedFile(oFileName=oFnFile)
            oET_Root:Element    = Orca_FromString(uET_Data=uET_Data,oDef=None,uFileName=oFnFile.string)
            iCountFonts         = Globals.oTheScreen.oFonts.ParseFontFromXMLNode(oXMLNode=oET_Root)
            Globals.oTheScreen.oFonts.ParseIconsFromXMLNode(oXMLNode=oET_Root)
        except Exception as e:
            uMsg:str=LogError(uMsg=u'Language: Fatal Error:Load Fonts from XmlFile:'+oFnFile.string,oException=e)
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=uMsg, bAbort=False)
        return iCountFonts

    def LoadXmlFile(self,uType:str,uContext:str='') -> None:
        """ Loads all strings for the language from a specific type (App, definition, interface, script, ) """
        iCountFonts:int
        oFnFile:cFileName

        if uType=="APP":
            if not self.oFnLanguageEnglish.Exists():
                iCountFonts = self.LoadXMLLanguageFont(self.oFnLanguageFallBackPrimary)
                self._LoadXmlFile(self.oFnLanguageFallBackEngLish)
                if Globals.uLanguage != u'English' and iCountFonts == 0:
                    self._LoadXmlFile(self.oFnLanguageFallBackPrimary)
            else:
                self._LoadXmlFile(self.oFnLanguageEnglish)
                if Globals.uLanguage!=u'English':
                    self._LoadXmlFile(self.oFnLanguagePrimary)
                self.oLocales.LoadXmlFile()
                self.LoadXMLLanguageFont(self.oFnLanguagePrimary)
        elif uType == "DEFINITION":
            self._LoadXmlFile(Globals.oDefinitionPathes.oFnDefinitionLanguageFallBack)
            if not Globals.uLanguage==u'English':
                self._LoadXmlFile(Globals.oDefinitionPathes.oFnDefinitionLanguage)
        elif uType == "SCRIPT":
            oFnFile = cFileName().ImportFullPath(uFnFullName=Globals.oScripts.dScriptPathList[uContext].string+"/" + Globals.uScriptLanguageFallBackTail)
            self._LoadXmlFile(oFnFile)
            if not Globals.uLanguage==u'English':
                oFnFile = cFileName().ImportFullPath(uFnFullName=Globals.oScripts.dScriptPathList[uContext].string + "/" + Globals.uScriptLanguageFileTail)
                self._LoadXmlFile(oFnFile)
        elif uType == "INTERFACE":
            oFnFile = cFileName().ImportFullPath(uFnFullName=Globals.oFnInterfaceLanguageFallBack.string % uContext)
            self._LoadXmlFile(oFnFile)
            if not Globals.uLanguage==u'English':
                oFnFile = cFileName().ImportFullPath(uFnFullName=Globals.oFnInterfaceLanguage.string % uContext)
                self._LoadXmlFile(oFnFile)
        else:
            oFnFile=cFileName('').ImportFullPath(uFnFullName=uType)
            if oFnFile.Exists():
                self._LoadXmlFile(oFnFile)

    # next two functions are ported from KODI

    def GetLocalizedTime(self, bWithSeconds:bool, oTime:struct_time=None) -> str:
        """ return a formated time to a locale """
        oLocales:cLocalesEntry = self.oLocales.oLocalesEntries.get(Globals.uLocalesName)
        uOut:str
        uTimeFormat:str
        uMeridiem:str
        uPart:str
        iPartLength:int
        uStr:str

        if oLocales is None:
            return u''
        uOut=u''
        uTimeFormat=oLocales.uTimeFormat
        if oTime is None:
            oTime=localtime()
        if oTime.tm_hour >11:
            uMeridiem=oLocales.uTimeSymbolPM
        else:
            uMeridiem=oLocales.uTimeSymbolAM
        i =0
        iLength=len(uTimeFormat)
        while i<iLength:
            cC=uTimeFormat[i]
            if cC==u'\'':
                #To be able to display a "'" in the string,
                #find the last "'" that doesn't follow a "'"

                pos=uTimeFormat.find(cC,i+1)
                # noinspection PyChainedComparisons
                while(pos>-1 and pos<len(uTimeFormat)) and uTimeFormat[pos+1]=='\'':
                    pos=uTimeFormat.find(cC,pos+1)
                if pos>-1:
                    #Extract string between ' '
                    uPart=uTimeFormat[i+1: pos-i-1]
                    i=pos
                else:
                    uPart=uTimeFormat[i+1: len(uTimeFormat)-i-1]
                    i=iLength
                uPart=uPart.replace("''", "'")
                uOut+=uPart
            elif cC=='h' or cC=='H':  # parse hour (H='24 hour clock')
                pos=find_first_not_of(uTimeFormat,i+1,cC)
                 #pos=uTimeFormat.find_first_not_of(cC,i+1)
                if pos>-1:
                    #Get length of the hour mask, eg. HH
                    iPartLength=pos-i
                    i=pos-1
                else:
                    #mask ends at the end of the string, extract it
                    iPartLength=iLength-i
                    i=iLength
                hour=oTime.tm_hour
                if cC=='h':
                    #recalc to 12 hour clock
                    if hour > 11:
                        hour = hour - (12 * (hour > 12))
                    else:
                        hour = hour + (12 * (hour < 1))
                #Format hour string with the length of the mask
                if iPartLength==1:
                    uStr=u'%d' % hour
                else:
                    uStr=u'%02d' % hour
                uOut+=uStr

            elif cC=='m': #parse minutes
                pos=find_first_not_of(uTimeFormat,i+1,cC)
                #pos=uTimeFormat.find_first_not_of(cC,i+1);
                if pos>-1:
                    #Get length of the minute mask, eg. mm
                    iPartLength=pos-i
                    i=pos-1
                else:
                    # mask ends at the end of the string, extract it
                    iPartLength=iLength-i
                    i=iLength
                #Format minute string with the length of the mask
                minute=oTime.tm_min
                if iPartLength==1:
                    uStr=u'%d' % minute
                else:
                    uStr=u'%02d' % minute
                uOut+=uStr
            elif cC=='s': #parse seconds
                pos=find_first_not_of(uTimeFormat,i+1,cC)
                if pos>-1:
                    #Get length of the minute mask, eg. mm
                    iPartLength=pos-i
                    i=pos-1
                else:
                    # mask ends at the end of the string, extract it
                    iPartLength=iLength-i
                    i=iLength
                #Format minute string with the length of the mask
                if bWithSeconds:
                    second=oTime.tm_sec
                    if iPartLength==1:
                        uStr=u'%d' % second
                    else:
                        uStr=u'%02d' % second
                    uOut+=uStr
                else:
                    uOut = uOut[0:-1]
            elif cC=='x': # add meridiem symbol

                pos=find_first_not_of(uTimeFormat,i+1,cC)
                if pos>-1:
                    #Get length of the minute mask, eg. mm
                    # iPartLength=pos-i
                    i=pos-1
                else:
                    # mask ends at the end of the string, extract it
                    #iPartLength=iLength-i
                    i=iLength
                uOut += uMeridiem
            else:
                uOut += cC
            i += 1
        return uOut

    def GetLocalizedDate(self,bLongDate:bool,bLongMonth:bool, bLongDay:bool, oTime:struct_time=None) -> str:
        """ return a formated date to a locale """

        uPart:str
        iPartLength:int
        uStr:str
        uOut:str

        oLocales:cLocalesEntry=self.oLocales.oLocalesEntries.get(Globals.uLocalesName)
        if oLocales is None:
            return u''
        uOut=u''
        if bLongDate:
            uDateFormat=oLocales.uDateLong
        else:
            uDateFormat=oLocales.uDateShort
        if oTime is None:
            oTime=localtime()

        i =0
        iLength=len(uDateFormat)
        while i<iLength:
            cC=uDateFormat[i]
            if cC==u'\'':
                #To be able to display a "'" in the string,
                #find the last "'" that doesn't follow a "'"
                pos=uDateFormat.find(cC,i+1)
                # noinspection PyChainedComparisons
                while(pos>-1 and pos<len(uDateFormat)) and uDateFormat[pos+1]=='\'':
                    pos=uDateFormat.find(cC,pos+1)
                if pos>-1:
                    #Extract string between ' '
                    uPart=uDateFormat[i+1: pos-i-1]
                    i=pos
                else:
                    uPart=uDateFormat[i+1: len(uDateFormat)-i-1]
                    i=iLength
                uPart=uPart.replace("''", "'")
                uOut+=uPart

            elif cC=='d' or cC=='D':  # parse days
                pos=find_first_not_of(uDateFormat,i+1,cC)
                if pos>-1:
                    #Get length of the hour mask, eg. HH
                    iPartLength=pos-i
                    i=pos-1
                else:
                    #mask ends at the end of the string, extract it
                    iPartLength=iLength-i
                    i=iLength
                #Format day string with the length of the mask
                day=oTime.tm_mday
                if iPartLength==1:   # single-digit number
                    uStr=u'%d' % day
                elif iPartLength==2:  # two-digit number
                    uStr=u'%02d' % day
                else:                 # day of week string
                    if bLongDay:
                        uStr='$lvar(%d)'%(oTime.tm_wday+11)
                    else:
                        uStr='$lvar(%d)'%(oTime.tm_wday+41)
                uOut+=uStr

            elif cC=='m' or cC=='M':  # parse months
                pos=find_first_not_of(uDateFormat,i+1,cC)
                if pos>-1:
                    #Get length of the hour mask, eg. HH
                    iPartLength=pos-i
                    i=pos-1
                else:
                    #mask ends at the end of the string, extract it
                    iPartLength=iLength-i
                    i=iLength
                #Format month string with the length of the mask
                month=oTime.tm_mon
                if iPartLength==1:   # single-digit number
                    uStr=u'%d' % month
                elif iPartLength==2:  # two-digit number
                    uStr=u'%02d' % month
                else:                 # day of week string
                    if bLongMonth:
                        uStr='$lvar(%d)'%(month+20)
                    else:
                        uStr='$lvar(%d)'%(month+50)
                uOut+=uStr
            elif cC=='y' or cC=='Y':  # parse months
                pos=find_first_not_of(uDateFormat,i+1,cC)
                if pos>-1:
                    #Get length of the hour mask, eg. HH
                    iPartLength=pos-i
                    i=pos-1
                else:
                    #mask ends at the end of the string, extract it
                    iPartLength=iLength-i
                    i=iLength
                #Format month string with the length of the mask
                year=oTime.tm_year
                if iPartLength==1:   # single-digit number
                    uStr=u'%d' % year
                elif iPartLength==2:  # two-digit number
                    uStr=u'%02d' % year
                else:                 # four digit
                    uStr=u'%04d' % year
                uOut+=uStr
            else:
                uOut += cC
            i += 1
        return ReplaceVars(uOut)

