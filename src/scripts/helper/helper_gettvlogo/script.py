# -*- coding: utf-8 -*-
#

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


import os
from typing                                 import Dict
from typing                                 import List
from typing                                 import Union
from typing                                 import Optional

from kivy                                   import Logger

from ORCA.scripts.BaseScript                import cBaseScript
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.Path                        import cPath
from ORCA.utils.TypeConvert                 import ToBool

import ORCA.Globals as Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>TV Logos Helper Script</name>
      <description language='English'>Helper Scripts to find TV Logos</description>
      <description language='German'>Hilfs Skript um TV-Logos zu finden</description>
      <author>Carsten Thielepape</author>
      <version>5.0.0</version>
      <minorcaversion>5.0.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/helper/helper_gettvlogo</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/helper_gettvlogo.zip</sourcefile>
          <targetpath>scripts/helper</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

typeReference       = Dict[str,str]
typeReferences      = Dict[str,typeReference]


class cLogoItem:
    """
    Helper class to represent a logo item
    """
    def __init__(self,*,uLogoKey:str,uFnLogo:str):
        self.uLogoKey:str      = uLogoKey
        self.uFnLogo:str       = uFnLogo

class cLogosForFolder(Dict[str,cLogoItem]):
    """
    Helper class to represent a dictionary of logo items
    """
    pass

class cScript(cBaseScript):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-helper_tvlogos
    WikiDoc:TOCTitle:Helper Script TV-Logos
    = TV-Logos Helper =

    This is a helper script for Enigma commands
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |cmd_type
    |The requested helper function: can be "get_tvlogofile","normalize_reference" or "normalize_channelname"
    |-
    |reference
    |for "normalize_reference": The reference string to be normalized, for "get_tvlogofile" the reference to find
    |-
    |channelname
    |for "normalize_channelname": The channelname string to be normalized, for "get_tvlogofile" the name to find
    |-
    |removehd
    |for "normalize_channelname": boolean flag if HD, UHD / SD flags should be removed
    |-
    |logopackfoldername
    |For "get_tvlogofile": the name of the folder (only the folder name, not the fullpath) in "recources" , below "tvlogos"
    |}</div>

    Remarks:
    "get_tvlogofile": Return a logo filename for the give reference or channelname
    "get_channelreference": Will return the channel reference for a channel number
    "assign_channels": Sets the TV Logos for the parsed channels

    WikiDoc:End
    """

    def __init__(self):
        super().__init__()
        self.uType:str                  = u'HELPERS'
        self.uIniFileLocation:str       = u'none'
        self.dLogoPackFolder:Dict[str,cLogosForFolder] =  {}
        self.dReferences:typeReferences = {}

    def Init(self, uObjectName: str, oFnObject: Union[cFileName, None] = None) -> None:
        """ Main Init, loads the Enigma Script"""
        super().Init(uObjectName= uObjectName, oFnObject=oFnObject)

    def RunScript(self, *args, **kwargs) -> Union[Dict,None]:
        """ Main Entry point, parses the cmd_type and calls the relevant functions """
        uCmdType:str
        try:
            if 'cmd_type' in kwargs:
                uCmdType = kwargs['cmd_type']
                if uCmdType == u'get_tvlogofile':
                    return self.GetTVLogoFile(**kwargs)
                elif uCmdType == u'normalize_reference':
                    return self.NormalizeReference(**kwargs)
                elif uCmdType == u'normalize_channelname':
                    return self.GetTVLogoFile(**kwargs)
            return None
        except Exception as e:
            self.ShowError(uMsg="Can''t run Get TV-Logos Helper script, invalid parameter",uParConfigName=self.uConfigName,oException=e)
            return {"ret":1}

    def GetTVLogoFile(self, **kwargs) -> Dict:
        """
        Sets the TV Logos for the parsed channels

        :param kwargs: argument dic, need to have definitionalias, interface, configname, force
        """
        try:
            uLogoPackFolderName:str         = ReplaceVars(kwargs['logopackfoldername'])
            uReference:str                  = ReplaceVars(kwargs['reference'])
            uChannelName:str                = ReplaceVars(kwargs['channelname'])
            uFnChannel:str

            self.CollectAllChannelLogos(uLogoPackFolderName=uLogoPackFolderName)
            uFnChannel=self.FindChannelLogo(uLogoPackFolderName=uLogoPackFolderName,uChannelName=uChannelName,uReference=uReference)

            return {"ret":0,"filename":uFnChannel}

        except Exception as e:
            self.ShowError(uMsg="Can''t find TV Logos", uParConfigName="",oException=e)
            return {"ret":1,"filename":""}

    def FindChannelLogo(self,*,uChannelName:str, uReference:str, uLogoPackFolderName:str) -> str:
        """
        Finds a channel Logo in the list of all logo files

        :param str uChannelName: The name of the channel to look for
        :param str uReference: The SAT Reference
        :param str uLogoPackFolderName: the name of the folder (only the folder name, not the fullpath) in "recources" , below "tvlogos"
        :return: The logo file name (full path), or "text:Channelname" if logo file can't be found
        """
        iPos = uChannelName.find("/")
        if iPos>0:
            uChannelName=uChannelName[:iPos]

        uFnLogo = self.FindChannelLogo_sub(uChannelName=uChannelName,uReference=uReference,uLogoPackFolderName=uLogoPackFolderName)
        if uFnLogo == u"" or uFnLogo is None:
            uFnLogo = u"text:"+uChannelName
            Logger.warning("Can't find logo [%s] [%s] in [%s]:" % ( uChannelName,uReference,uLogoPackFolderName))
        return uFnLogo

    def FindChannelLogo_sub(self,*,uChannelName:str, uReference:str, uLogoPackFolderName:str) -> str:
        """
        Helper function to just find a channel logo file, or none if not found

        :param str uChannelName: The name of the channel to look for
        :param str uReference: The SAT Reference
        :param str uLogoPackFolderName: the name of the folder (only the folder name, not the fullpath) in "recources" , below "tvlogos"
        :return: The logo file name (full path), or "" if logo file can't be found
        """

        uFnLogo:str

        if uReference:
            uFnLogo = self.FindLogoByReference(uLogoPackFolderName=uLogoPackFolderName,uReference=uReference)
            if uFnLogo:
                return uFnLogo

        return self.FindLogoByChannelName(uLogoPackFolderName=uLogoPackFolderName,uChannelName=uChannelName)

    def CollectAllChannelLogos(self,*,uLogoPackFolderName:str) -> None:
        """
        Collect all channel logos in a dict (if not already done)
        """
        if not uLogoPackFolderName in self.dLogoPackFolder:
            self.dLogoPackFolder[uLogoPackFolderName] = cLogosForFolder()
            self.CollectAllChannelLogos_sub(oPath=Globals.oPathTVLogos,uLogoPackFolderName=uLogoPackFolderName, bFirst=True)

    def CollectAllChannelLogos_sub(self,*,oPath,uLogoPackFolderName:str,bFirst=True) -> None:
        """
        Helper function to recursive get all files in a folder tree
        :param cPath oPath: The start folder in the folder tree
        :param bool bFirst: Flag, is this been called first time on recursion
        :param str uLogoPackFolderName: the name of the folder (only the folder name, not the full path) in "resources" , below "tvlogos"
        """

        oFinalPath:cPath
        aFolders:List[str]
        uFolder:str

        if bFirst:
            oFinalPath = oPath+uLogoPackFolderName
            self.LoadReferences(oPath=oFinalPath,uLogoPackFolderName=uLogoPackFolderName)
        else:
            oFinalPath = oPath

        self.GetFolderFiles(oPath=oFinalPath,uLogoPackFolderName=uLogoPackFolderName)

        aFolder = oFinalPath.GetFolderList(bFullPath=True)
        for uFolder in aFolder:
            self.CollectAllChannelLogos_sub(oPath=cPath(uFolder),uLogoPackFolderName=uLogoPackFolderName,bFirst=False)


    def GetFolderFiles(self,*,oPath:cPath,uLogoPackFolderName:str) -> None:
        """
        Helper function to get all files in a folder (not folder)

        :param cPath oPath: The folder to collect the files
        :param str uLogoPackFolderName: The TV Logo Pack Folder name
        """
        aFileList:List[str]             = oPath.GetFileList(bFullPath=True,bSubDirs=False)
        dLogosForFolder:cLogosForFolder = cLogosForFolder()
        uBaseName:str
        uFnLogo:str

        for uFnLogo in aFileList:
            uBaseName                               = os.path.basename(uFnLogo)
            uFileBaseNameStandard                   = NormalizeName(uName=uBaseName)
            oLogoItem = cLogoItem(uLogoKey=uFileBaseNameStandard,uFnLogo=uFnLogo)
            dLogosForFolder[oLogoItem.uLogoKey]    = oLogoItem
            # if the filename is a reference, normalize it and add it
            if uBaseName.count("_")>3:
                oLogoItem = cLogoItem(uLogoKey=NormalizeReference(uReference=uFileBaseNameStandard),uFnLogo=uFnLogo)
                dLogosForFolder[oLogoItem.uLogoKey]    = oLogoItem

        self.dLogoPackFolder[uLogoPackFolderName].update(dLogosForFolder)


    def FindLogoByReference(self,*,uLogoPackFolderName:str, uReference:str) -> str:
        """
        Finds a channel logo by a give channel reference
        :param uLogoPackFolderName: The name of the folder
        :param uReference: The reference string
        :return: A filename for the channel reference
        """

        uFnLogo:Optional[str]
        oLogoItem:Optional[cLogoItem]
        dReferences:Dict[str,str] = self.dReferences.get(uLogoPackFolderName)
        if dReferences is not None:
            uFnLogo = dReferences.get(NormalizeReference(uReference=uReference))
            if uFnLogo is not None:
                uFnReference:str = NormalizeName(uName=uFnLogo.replace("\n",""))+".png"
                oLogosForFolder:Optional[cLogosForFolder] = self.dLogoPackFolder.get(uLogoPackFolderName)
                if oLogosForFolder is not None:
                    oLogoItem = oLogosForFolder.get(uFnReference)
                    if oLogoItem is None:
                        oLogoItem = oLogosForFolder.get(NormalizeReference(uReference=uReference))
                    if oLogoItem is not None:
                        return oLogoItem.uFnLogo.replace(Globals.oPathResources.string, '$var(RESOURCEPATH)')
        return ""

    def FindLogoByChannelName(self,*,uLogoPackFolderName:str, uChannelName:str) -> str:
        """
        Finds a logo by channel name
        :param uLogoPackFolderName: the logo pack name to use
        :param uChannelName: The name of of the channel to check for
        :return: the logo file name of the channel logo
        """
        oLogoItem:Optional[cLogoItem] = None
        oLogosForFolder:Optional[cLogosForFolder] = self.dLogoPackFolder.get(uLogoPackFolderName)

        if oLogosForFolder is not None:
            oLogoItem = oLogosForFolder.get(NormalizeName(uName=uChannelName+".png",bRemoveHD=False))
            if oLogoItem is None:
                oLogoItem = oLogosForFolder.get(NormalizeName(uName=uChannelName+".png", bRemoveHD=True))
        if oLogoItem:
            return oLogoItem.uFnLogo.replace(Globals.oPathResources.string, '$var(RESOURCEPATH)')
        return ""

    def NormalizeChannelName(self, **kwargs) -> Dict:
        """
        Sets the TV Logos for the parsed channels

        :param kwargs: argument dic, need to have definitionalias, interface, configname, force
        """
        try:
            uChannelName:str                  = ReplaceVars(kwargs['channelname'])
            bRemoveHD:bool                    = ToBool(ReplaceVars(kwargs['removehd']))
            return {"ret":1,"channelname":NormalizeName(uName=uChannelName,bRemoveHD=bRemoveHD)}
        except Exception as e:
            self.ShowError(uMsg="Can''t run NormalizeChannelName, invalid parameter",uParConfigName=self.uConfigName,oException=e)
            return {"ret":1}

    def NormalizeReference(self, **kwargs) -> Dict:
        """
        Sets the TV Logos for the parsed channels

        :param kwargs: argument dic, need to have definitionalias, interface, configname, force
        """
        try:
            uReference:str                  = ReplaceVars(kwargs['reference'])
            return {"ret":1,"reference":NormalizeReference(uReference=uReference)}
        except Exception as e:
            self.ShowError(uMsg="Can''t run NormalizeReference, invalid parameter",uParConfigName=self.uConfigName,oException=e)
            return {"ret":1}

    def LoadReferences(self,*,oPath:cPath,uLogoPackFolderName:str) -> None:
        """
        Loads References from a file. A reference file matches a logo file name to a SAT/DVB:C service id, the file name is fixed "srp.index.txt"
        :param oPath: the path to the icon root foolder
        :param uLogoPackFolderName: the logo pack folder name
        :return:
        """
        aLines:List[str]
        uLine:str
        uReference:str
        uFileName:str

        if uLogoPackFolderName in self.dReferences:
            return

        self.dReferences[uLogoPackFolderName] = {}

        oFnReferences = cFileName(oPath) + "srp.index.txt"
        if oFnReferences.Exists():
            oFile = open(oFnReferences.string,"r")
            aLines = oFile.readlines()
            oFile.close()
            for uLine in aLines:
                uReference,uFileName=uLine.split("=")
                uReference= NormalizeReference(uReference=uReference)
                self.dReferences[uLogoPackFolderName][uReference] = uFileName.split("-")[0]

def NormalizeReference(*,uReference:str) -> str:
    """
    Helper function to increase the match rate of icon names to channel names by removing blanks and special characters

    :param str uReference: the core reference
    :return: normalized reference
    """

    if ":" in uReference:
        aParts = uReference.split(":")
        uReference = aParts[3]+aParts[4]+aParts[5]+aParts[6]
    uReference=uReference.replace("_","")
    # uReference = uReference.replace("0", "")
    return uReference

def NormalizeName(*,uName:str, bRemoveHD:bool = False) -> str:
    """
    Helper function to increase the match rate of icon names to channel names by removing blanks and special characters

    :param str uName: the name to normalize
    :param bool bRemoveHD: Remove the 'HD', 'UHD' tags as well
    :return: normalized file name
    """

    uName = uName.lower().replace(" ", "").replace("/","").replace("\\","").replace("+","plus").replace("-","").replace("_","")

    if bRemoveHD:
        uName = uName.replace("uhd.",".").replace("sd.",".").replace("hd.",".")
    return remove_umlaut(string=uName)


def remove_umlaut(*,string:str) -> str:
    """
    Removes umlauts from strings and replaces them with the letter+e convention
    :param string: string to remove umlauts from
    :return: unumlauted string
    """
    string = string.replace(u"ü", u'ue')
    string = string.replace(u"Ü", u'Ue')
    string = string.replace(u"ä", u'ae')
    string = string.replace(u"Ä", u'Ae')
    string = string.replace(u"ö", u'oe')
    string = string.replace(u"Ö", u'Oe')
    string = string.replace(u"ß", u'ss')

    return string

'''
<e2movie>
    <e2servicereference>
    1:0:0:0:0:0:0:0:0:0:/media/hdd/movie/20191101 1711 - Sky Cinema Spooky Halloween HD - Die Legende der Wächter.ts
    </e2servicereference>
    <e2title>Die Legende der Wächter</e2title>
    <e2description>Fantasyfilm</e2description>
    <e2descriptionextended>
    Atemberaubend animiertes Fantasyabenteuer für die ganze Familie nach den Kinderbüchern von Kathryn Lasky. - Als die jungen Schleiereulen Sören und Kludd von ihrem Heimatbaum stürzen, werden die Brüder von mysteriösen Eulen gerettet. Doch die Retter entpuppen sich als die diabolischen "Reinsten", die mit Hilfe eines Sklavenheeres ein despotisches Regime errichten wollen. Sören gelingt mit der kleinen Gylfie die Flucht. Gemeinsam suchen sie die legendären Wächter von Ga'Hoole, die schon einmal die "Reinsten" vertrieben haben sollen. 89 Min. AUS/USA 2010. Von Zack Snyder. Ab 6 Jahren
    </e2descriptionextended>
    <e2servicename>Sky Cinema Spooky Halloween HD</e2servicename>
    <e2time>1572624682</e2time>
    <e2length>21:09</e2length>
    <e2tags/>
    <e2filename>
    /media/hdd/movie/20191101 1711 - Sky Cinema Spooky Halloween HD - Die Legende der Wächter.ts
    </e2filename>
    <e2filesize>1397197200</e2filesize>
</e2movie>
'''


