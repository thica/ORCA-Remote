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
from xml.etree.ElementTree  import ParseError
from xml.etree              import ElementInclude

from time                   import localtime

from kivy.logger            import Logger

from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.XML         import GetXMLTextAttribute
from ORCA.utils.XML         import GetXMLTextValue
from ORCA.utils.XML         import Orca_include
from ORCA.utils.XML         import Orca_FromString
from ORCA.utils.XML         import orca_et_loader
from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.LogError    import LogError
from ORCA.utils.CachedFile  import CachedFile

import ORCA.Globals as Globals

from ORCA.utils.FileName import cFileName

def find_first_not_of(uString,iStartPos,cChar):
    """ Python adoption of C function to find the first character which is diffrent fom the given one """
    i=iStartPos
    iLen=len(uString)
    while i<iLen:
        if not uString[i]==cChar:
            return i
        i=i+1
    return -1

class cLocalesEntry(object):
    """ Object which represents a locales entry """
    def __init__(self):
        self.uName              = u''
        self.uLocale            = u''
        self.uDateShort         = u''
        self.uDateLong          = u''
        self.uTimeSymbolAM      = u''
        self.uTimeSymbolPM      = u''
        self.uTimeFormat        = u''
        self.uTempUnit          = u''
        self.uSpeedUnit         = u''

    def ParseXMLLocales(self,oXMLLocales):
        """ reads the locales information from the xml (kodi file) """
        self.uName      = GetXMLTextAttribute(oXMLLocales,u'name',True,u'')
        self.uLocale    = GetXMLTextAttribute(oXMLLocales,u'locale',False,u'EN')
        self.uDateShort = GetXMLTextValue(oXMLLocales,u'dateshort',False,u'DD.MM.YYYY')
        self.uDateLong  = GetXMLTextValue(oXMLLocales,u'datelong',False,u'DDDD, D MMMM YYYY')
        self.uTimeFormat= GetXMLTextValue(oXMLLocales,u'time',False,u'H:mm:ss')
        oXMLTime=oXMLLocales.find('time')
        if oXMLTime is not None:
            self.uTimeSymbolAM=GetXMLTextAttribute(oXMLTime,u'symbolAM',False,u'')
            self.uTimeSymbolPM=GetXMLTextAttribute(oXMLTime,u'symbolPM',False,u'')

class cLocales(object):
    """ a representation of all loaded locales entries for a language"""
    def __init__(self):
        self.oLocalesEntries = {}
    def LoadXmlFile(self):
        """ reads all locales for a language """
        self.oLocalesEntries.clear()
        try:
            oET_Root = ElementTree(file=Globals.oFnLangInfo.string).getroot()
            oXMLRegions = oET_Root.find(u'regions')
            if oXMLRegions is not None:
                for oXMLRegion in oXMLRegions.findall(u'region'):
                    self.__ParseXMLLocales(oXMLRegion)
        except ParseError as e:
            uMsg=LogError(u'Language: Fatal Error:Load Locales XmlFile:',e)
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=uMsg, bAbort=True)

    def __ParseXMLLocales(self,oXMLLocale):
        """ reads a single locales entry and stores it in the locles list """
        oLocalesEntry=cLocalesEntry()
        oLocalesEntry.ParseXMLLocales(oXMLLocale)
        self.oLocalesEntries[oLocalesEntry.uName]=oLocalesEntry

class cLanguage(object):
    """ The representation of a language (strings, locales, formats) """
    def __init__(self):
        self.dIDToString                = {}
        self.oLocales                   = cLocales()
        self.aLoadedFiles               = []
        self.oFnLanguagePrimary         = None
        self.oFnLanguageEnglish         = None
        self.oFnLanguageFallBackPrimary = None
        self.oFnLanguageFallBackEngLish = None

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


    def Init(self):
        self.oFnLanguagePrimary              = cFileName(Globals.oPathLanguageRoot + Globals.uLanguage) + u'strings.xml'
        self.oFnLanguageEnglish              = cFileName(Globals.oPathLanguageRoot + u'English') + u'strings.xml'
        self.oFnLanguageFallBackPrimary      = cFileName(Globals.oPathAppReal + u'languages/'+ Globals.uLanguage) + u'strings.xml'
        self.oFnLanguageFallBackEngLish      = cFileName(Globals.oPathAppReal + u'languages/English') + u'strings.xml'


    def SetString(self,uID,uText):
        """ sets a string """
        self.dIDToString[uID]=uText

    def StringIDToString(self,uID):
        """ returns the language string to a given language id """
        uRet = self.dIDToString.get(uID)
        if uRet is not None:
            return uRet
        else:
            Logger.warning (u'Language: No Language String found:'+uID)
        return uID

    def __LoadXMLNode(self,oET_Root,uTarget):

        if oET_Root.find(ElementInclude.XINCLUDE_INCLUDE) is not None:
            Orca_include(oET_Root ,orca_et_loader)

        oET_Strings=oET_Root.find("strings")
        if oET_Strings is not None:
            self.__LoadXMLNode(oET_Strings,uTarget)

        for oXMLString in oET_Root.findall('string'):
            uText=oXMLString.text
            if uText is None:
                uText=u''
            uText  = ToUnicode(uText)
            sIndex = GetXMLTextAttribute(oXMLString,u'id',True,0)
            uTarget[sIndex]  = uText

    def _LoadXmlFile(self,oFnFile):
        """ Loads all strings for the language from a specific files"""
        if not oFnFile.Exists():
            Logger.debug (u'Language: String File does not exist:'+oFnFile.string)
            return
        if oFnFile.string in self.aLoadedFiles:
            Logger.debug (u'Language: Skip duplicate language file loading:'+oFnFile.string)
            return

        oDef = None
        try:
            sET_Data = CachedFile(oFnFile)
            if Globals.uDefinitionContext:
                oDef = Globals.oDefinitions.get(Globals.uDefinitionContext)
            oET_Root = Orca_FromString(sET_Data,oDef,oFnFile.string)
            self.__LoadXMLNode(oET_Root,self.dIDToString)
        except ParseError as e:
            uMsg=LogError(u'Language: Fatal Error:Load Language XmlFile (xml parse error):'+oFnFile.string,e)
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=uMsg, bAbort=True)
        except Exception as e:
            uMsg=LogError(u'Language: Fatal Error:Load Language XmlFile (2):'+oFnFile.string,e)
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=uMsg, bAbort=True)

    def Reset(self):
        """ clears all language strings """
        self.dIDToString.clear()
        del self.aLoadedFiles[:]

    def LoadXMLLanguageFont(self, oFnFile):
        iCountFonts = 0
        try:
            sET_Data = CachedFile(oFnFile)
            oET_Root = Orca_FromString(sET_Data,None,oFnFile.string)
            iCountFonts = Globals.oTheScreen.oFonts.ParseFontFromXMLNode(oET_Root)
            Globals.oTheScreen.oFonts.ParseIconsFromXMLNode(oET_Root)
        except Exception as e:
            uMsg=LogError(u'Language: Fatal Error:Load Fonts from XmlFile:'+oFnFile.string,e)
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=uMsg, bAbort=False)
        return iCountFonts

    def LoadXmlFile(self,uType,uContext=''):
        """ Loads all strings for the language from a specific type (App, definition, interface, script, ) """
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

            oFnFile = cFileName().ImportFullPath(Globals.oScripts.dScriptPathList[uContext].string+"/" + Globals.uScriptLanguageFallBackTail)

            self._LoadXmlFile(oFnFile)
            if not Globals.uLanguage==u'English':
                oFnFile = cFileName().ImportFullPath(Globals.oScripts.dScriptPathList[uContext].string + "/" + Globals.uScriptLanguageFileTail)
                self._LoadXmlFile(oFnFile)
        elif uType == "INTERFACE":
            oFnFile = cFileName().ImportFullPath(Globals.oFnInterfaceLanguageFallBack.string % uContext)
            self._LoadXmlFile(oFnFile)
            if not Globals.uLanguage==u'English':
                oFnFile = cFileName().ImportFullPath(Globals.oFnInterfaceLanguage.string % (uContext))
                self._LoadXmlFile(oFnFile)
        else:
            oFnFile=cFileName('').ImportFullPath(uType)
            if oFnFile.Exists():
                self._LoadXmlFile(oFnFile)

    # next two functions are ported from KODI

    def GetLocalizedTime(self, bWithSeconds):
        """ return a formated time to a locale """
        oLocales=self.oLocales.oLocalesEntries.get(Globals.uLocalesName)
        if oLocales is None:
            return u''
        uOut=u''
        uTimeFormat=oLocales.uTimeFormat
        oDateTime=localtime()
        uMeridiem=u''
        if oDateTime.tm_hour >11:
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
                while(pos>-1 and pos<len(uTimeFormat)) and uTimeFormat[pos+1]=='\'':
                    pos=uTimeFormat.find(cC,pos+1)
                uPart=u''
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
                iPartLength=0
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
                hour=oDateTime.tm_hour
                if cC=='h':
                    #recalc to 12 hour clock
                    if hour > 11:
                        hour = hour - (12 * (hour > 12))
                    else:
                        hour = hour + (12 * (hour < 1))
                #Format hour string with the length of the mask
                uStr=u''
                if iPartLength==1:
                    uStr=u'%d' % hour
                else:
                    uStr=u'%02d' % hour
                uOut+=uStr

            elif cC=='m': #parse minutes
                iPartLength=0
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
                minute=oDateTime.tm_min
                uStr=u''
                if iPartLength==1:
                    uStr=u'%d' % minute
                else:
                    uStr=u'%02d' % minute
                uOut+=uStr
            elif cC=='s': #parse seconds
                iPartLength=0
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
                    second=oDateTime.tm_sec
                    uStr=u''
                    if iPartLength==1:
                        uStr=u'%d' % second
                    else:
                        uStr=u'%02d' % second
                    uOut+=uStr
                else:
                    uOut = uOut[0:-1]
            elif cC=='x': # add meridiem symbol
                iPartLength=0
                pos=find_first_not_of(uTimeFormat,i+1,cC)
                if pos>-1:
                    #Get length of the minute mask, eg. mm
                    iPartLength=pos-i
                    i=pos-1
                else:
                    # mask ends at the end of the string, extract it
                    iPartLength=iLength-i
                    i=iLength
                uOut=uOut+uMeridiem
            else:
                uOut=uOut+cC
            i=i+1
        return uOut

    def GetLocalizedDate(self,bLongDate,bLongMonth, bLongDay):
        """ return a formated date to a locale """
        oLocales=self.oLocales.oLocalesEntries.get(Globals.uLocalesName)
        if oLocales is None:
            return u''
        uOut=u''
        if bLongDate:
            uDateFormat=oLocales.uDateLong
        else:
            uDateFormat=oLocales.uDateShort
        oDateTime=localtime()

        i =0
        iLength=len(uDateFormat)
        while i<iLength:
            cC=uDateFormat[i]
            if cC==u'\'':
                #To be able to display a "'" in the string,
                #find the last "'" that doesn't follow a "'"
                pos=uDateFormat.find(cC,i+1)
                while(pos>-1 and pos<len(uDateFormat)) and uDateFormat[pos+1]=='\'':
                    pos=uDateFormat.find(cC,pos+1)
                uPart=u''
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
                iPartLength=0
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
                uStr=u''
                day=oDateTime.tm_mday
                if iPartLength==1:   # single-digit number
                    uStr=u'%d' % day
                elif iPartLength==2:  # two-digit number
                    uStr=u'%02d' % day
                else:                 # day of week string
                    if bLongDay:
                        uStr='$lvar(%d)'%(oDateTime.tm_wday+11)
                    else:
                        uStr='$lvar(%d)'%(oDateTime.tm_wday+41)
                uOut+=uStr

            elif cC=='m' or cC=='M':  # parse months
                iPartLength=0
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
                uStr=u''
                month=oDateTime.tm_mon
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
                iPartLength=0
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
                uStr=u''
                year=oDateTime.tm_year
                if iPartLength==1:   # single-digit number
                    uStr=u'%d' % year
                elif iPartLength==2:  # two-digit number
                    uStr=u'%02d' % year
                else:                 # four digit
                    uStr=u'%04d' % year
                uOut+=uStr
            else:
                uOut=uOut+cC
            i=i+1
        return ReplaceVars(uOut)

