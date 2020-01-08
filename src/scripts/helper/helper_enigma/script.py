# -*- coding: utf-8 -*-
#

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


import os
from typing                                 import Dict
from typing                                 import List
from typing                                 import Union

from xml.etree.ElementTree                  import fromstring
from time                                   import struct_time
from datetime                               import datetime
from datetime                               import timezone

import urllib

from kivy                                   import Logger

from ORCA.scripts.BaseScript                import cBaseScript
from ORCA.vars.Access                       import GetVar
from ORCA.vars.Access                       import SetVar
from ORCA.vars.Actions                      import Var_DelArray
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.utils.TypeConvert                 import EscapeUnicode
from ORCA.utils.TypeConvert                 import ToInt
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.XML                         import GetXMLTextValue
from ORCA.utils.Path                        import cPath

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.interfaces.BaseInterface import cBaseInterFace
    from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
else:
    from typing import TypeVar
    cBaseInterFace          = TypeVar("cBaseInterFace")
    cBaseInterFaceSettings  = TypeVar("cBaseInterFaceSettings")



'''
<root>
  <repositorymanager>
    <entry>
      <name>Enigma Helper Script</name>
      <description language='English'>Enigma Helper Script (for DVB Receiver)</description>
      <description language='German'>Enigma Hilfs - Skript (Für DVB Receiver)</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/helper/helper_enigma</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/helper_enigma.zip</sourcefile>
          <targetpath>scripts/helper</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cScript(cBaseScript):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-helper_enigma
    WikiDoc:TOCTitle:Helper Script Autoconfig Enigma channels
    = ENIGMA Helper =

    This is a helper script for Enigma commands
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |cmd_type
    |The requested helper function: can be "parse_services","get_channelreference" or "assign_channels"
    |-
    |resultvar
    |for "parse_services": The name of the var which holds the servielist to parse. Not the result itself
    |-
    |definitionalias
    |For assign_channels: The alias name of the TV Template definition
    |-
    |interface
    |For assign_channels, parse_services: The interface name for the Enigma2 Control
    |-
    |configname
    |For assign_channels, parse_services: The config name for the Enigma2 Control
    |-
    |force
    |For assign_channels: 0/1 Replace all (1) of only unconfigured channels (with name "discover")
    |-
    |retvar
    |for get_channelreference: The var name for the result (the reference)
    |-
    |channelnum
    |for get_channelreference: The channelnum to get the reference for
    |-
    |logopackfoldername
    |For assign_channels: the name of the folder (only the folder name, not the fullpath) in "recources" , below "tvlogos"
    |}</div>

    Remarks:
    "parse_services": Needs to done first, Reads all services for a specific Enigma box into the script
    "get_channelreference": Will return the channel reference for a channel number
    "assign_channels": Sets the TV Logos for the parsed channels

    WikiDoc:End
    """

    def __init__(self):
        cBaseScript.__init__(self)
        self.uType                                   = u'HELPERS'
        self.uIniFileLocation                        = u'none'

        self.dServices:Dict[str,Union[Dict,List]]   = {}
        self.dMovies:Dict[str,Dict[Dict[Dict]]]     = {}

        self.dLogos:Dict[str,Dict[str,str]]         = {}
        self.dReferences:Dict[str,Dict[str,str]]    = {}

    def Init(self, uObjectName: str, oFnObject: Union[cFileName, None] = None) -> None:
        """ Main Init, loads the Enigma Script"""
        cBaseScript.Init(self,uObjectName,oFnObject)

    def RunScript(self, *args, **kwargs) -> Union[Dict,None]:
        """ Main Entry point, parses the cmd_type and calls the relevant functions """
        uCmdType:str
        try:
            if 'cmd_type' in kwargs:
                uCmdType = kwargs['cmd_type']
                if uCmdType == u'parse_services':
                    return self.ParseServices(**kwargs)
                if uCmdType == u'parse_movielist':
                    return self.ParseMovieList(**kwargs)
                if uCmdType == u'get_channelreference':
                    return self.GetChannelReference(**kwargs)
                if uCmdType == u'assign_channels':
                    return self.AssignChannels(**kwargs)

        except Exception as e:
            self.ShowError(uMsg="Can''t run Enigma Helper script, invalid parameter",uParConfigName=self.uConfigName,oException=e)
            return {"ret":1}

    def AssignChannels(self, **kwargs) -> None:
        """
        Sets the TV Logos for the parsed channels

        :param kwargs: argument dic, need to have definitionalias, interface, configname, force
        """
        try:
            uAlias:str                      = ReplaceVars(kwargs['definitionalias'])
            uInterfaceName:str              = ReplaceVars(kwargs['interface'])
            uConfigName:str                 = ReplaceVars(kwargs['configname'])
            uLogoPackFolderName             = ReplaceVars(kwargs['logopackfoldername'])
            bForce:bool                     = ReplaceVars(kwargs['force'])!='0'
            oInterFace:cBaseInterFace       = Globals.oInterFaces.dInterfaces.get(uInterfaceName)
            oSetting:cBaseInterFaceSettings = oInterFace.GetSettingObjectForConfigName(uConfigName)
            uContext:str                    = oSetting.uContext
            uSection:str                    = Globals.uDefinitionName

            iMaxBouquets:int                = 6
            iMaxChannelsPerBouquets:int     = 27

            iBouquetNumber:int
            uBouquetName:str
            dBouquetDetail:Dict
            uBouquetName:str
            uVarName:str
            uVarValue:str
            dChannels:Dict[int]

            dServices:Dict[str] = self.dServices.get(uContext,{})
            aBouquets:List[Dict] = dServices.get("Bouquets",[])

            if uLogoPackFolderName==u'':
                uLogoPackFolderName=self.GetLogoPack()

            self.CollectAllChannelLogos(uLogoPackFolderName)

            for dBouquetDetail in aBouquets:
                iBouquetNumber = dBouquetDetail["BouquetNum"]
                if iBouquetNumber <=iMaxBouquets:
                    uBouquetName   = dBouquetDetail["Name"]
                    uVarName = uAlias + "_bouquet_name["+str(iBouquetNumber)+"]"
                    uVarValue = uBouquetName
                    Globals.oDefinitionConfigParser.set(uSection, uVarName, EscapeUnicode(uVarValue))
                    SetVar(uVarName=uVarName, oVarValue=uVarValue)
                    dChannels = dBouquetDetail.get("Channels",{})
                    for iBouquetChannelNum in dChannels:
                        if iBouquetChannelNum<=iMaxChannelsPerBouquets:
                            dChannel = dChannels[iBouquetChannelNum]
                            uVarName = uAlias+"%s[%d][%d]" % ("_tvlogo",iBouquetNumber,iBouquetChannelNum)
                            if Globals.oDefinitionConfigParser.get(uSection, uVarName) == "discover" or bForce:
                                uVarValue = self.FindChannelLogo(dChannel["ChannelName"],dChannel["Reference"],uLogoPackFolderName)
                                Globals.oDefinitionConfigParser.set(uSection, uVarName, EscapeUnicode(uVarValue))
                                SetVar(uVarName=uVarName, oVarValue=uVarValue)
                                uVarName = uAlias+"%s[%d][%d]" % ("_tvchannel",iBouquetNumber,iBouquetChannelNum)
                                uVarValue = str(dChannel["ChannelNum"])
                                Globals.oDefinitionConfigParser.set(uSection, uVarName, uVarValue)
                                SetVar(uVarName=uVarName, oVarValue=uVarValue)
            Globals.oDefinitionConfigParser.write()

        except Exception as e:
            self.ShowError(uMsg="Can''t assign channelnumbers", uParConfigName=self.uConfigName,oException=e)

    def GetChannelReference(self, **kwargs) -> None:
        """
        Will return the channel reference for a channel number

        :param kwargs: argument dic, need to have retvar, channelnum, interface, configname
        """

        uContext:str    = u''
        uChannelNum:str = u''
        uDstVarName:str
        uInterfaceName:str
        uConfigName:str
        uReference:str

        try:
            uDstVarName     = kwargs['retvar']
            uChannelNum     = kwargs['channelnum']
            uInterfaceName  = ReplaceVars(kwargs['interface'])
            uConfigName     = ReplaceVars(kwargs['configname'])

            oInterFace      = Globals.oInterFaces.dInterfaces.get(uInterfaceName)
            oSetting        = oInterFace.GetSettingObjectForConfigName(uConfigName)
            uContext        = oSetting.uContext
            uChannelNum     = ReplaceVars(uOrgIn=uChannelNum,uContext=uContext)
            uReference      = self.dServices[uContext]["Channels"][int(uChannelNum)]["Reference"]
            SetVar(uVarName=uDstVarName , uContext=uContext, oVarValue=uReference)
        except Exception as e:
            self.ShowError(uMsg="Can''t find channelreference:"+uChannelNum+" context:"+uContext, uParConfigName=self.uConfigName, oException=e)
            if not uContext in self.dServices:
                self.ShowError("Context not found, available context:")
                for uKey in self.dServices:
                    self.ShowError(uKey)
            else:
                self.ShowError("Channel not found, available channels:")
                for iChannelNum in self.dServices[uContext]["Channels"]:
                    self.ShowError(str(iChannelNum))


    def ParseServices(self, **kwargs) -> Dict:
        """
        Needs to done first, Reads all services for a specific Enigma box into the script

        :param kwargs: argument dic, need to have resultvar, interface, configname
        :return: Dict ret: 0 or 1 : 1=success
        """
        try:
            uResultVar          = kwargs['resultvar']
            uInterfaceName      = ReplaceVars(kwargs['interface'])
            uConfigName         = ReplaceVars(kwargs['configname'])

            oInterFace = Globals.oInterFaces.dInterfaces.get(uInterfaceName)
            oSetting = oInterFace.GetSettingObjectForConfigName(uConfigName)
            uContext = oSetting.uContext

            self.ShowInfo("Parsing Services into "+uContext)

            if self.dServices.get(uContext) is not None:
                return {"ret":1}

            uXmlContent = GetVar(uResultVar)
            uXmlContent = EscapeUnicode(uXmlContent)

            iBouquetNum = 0  # Order Number of the Channel
            iChannelNum = 0  # Absolute Channel num, through all Bouquets
            if uXmlContent:
                # oET_Root = fromstring(uXmlContent)
                # oXmlBouquets = oET_Root.find("e2bouquet")
                oXmlBouquets = fromstring(uXmlContent)
                dChannels        = {} # Bouquet independent list of all channels
                aBouquets        = [] # List of all bouquets as dBouquetDetails
                for oXmlBouquet in oXmlBouquets:
                    if oXmlBouquet.tag=='e2bouquet': # we might get services as well
                        dBouquetDetails    = {}  # Element to decribe a single bouquet (number , name, containing channels)
                        dBouquetChannels   = {}    # Dict of all channels in a single bouquet, index is Bouquechannelnum
                        iBouquetChannelNum = 0
                        uBouquetName = GetXMLTextValue(oXmlBouquet,"e2servicename",False,"NoName"+str(iBouquetNum))
                        iBouquetNum+=1
                        oXmlServices = oXmlBouquet.find("e2servicelist")
                        for oXmlServiceDetails in oXmlServices:
                            dSingleChannel          = {}   # details of a channel
                            iChannelNum             += 1   # absolute channel num within all bouquets
                            iBouquetChannelNum      += 1   # relative channel num in bouquet
                            uReference   = GetXMLTextValue(oXmlServiceDetails, "e2servicereference" , True, "NoName")
                            uChannelName = GetXMLTextValue(oXmlServiceDetails, "e2servicename", False, "NoName"+str(iChannelNum))
                            dSingleChannel["ChannelName"]        = uChannelName
                            dSingleChannel["Reference"]          = uReference
                            dSingleChannel["ChannelNum"]         = iChannelNum
                            dSingleChannel["BouquetChannelNum"]  = iBouquetChannelNum
                            dBouquetChannels[iBouquetChannelNum] = dSingleChannel
                            dChannels[iChannelNum]               = dSingleChannel
                            # SetVar(uVarName=uDstVarName+"_channelservice["+str(iChannelNum)+"]",uContext=uContext,oVarValue=str(iChannelNum))
                        dBouquetDetails["Channels"]   = dBouquetChannels
                        dBouquetDetails["Name"]       = uBouquetName
                        dBouquetDetails["BouquetNum"] = iBouquetNum
                        aBouquets.append(dBouquetDetails)

                self.dServices[uContext] = {}
                self.dServices[uContext]["Bouquets"]=aBouquets
                self.dServices[uContext]["Channels"]=dChannels
                return {"ret":1}
            else:
                self.ShowError("No Services Data in Source Var:"+uResultVar)
        except Exception as e:
            self.ShowError(uMsg="Can''t parse services, invalid xml", uParConfigName=self.uConfigName, oException=e)
        return {"ret":0}

    # noinspection PyUnresolvedReferences
    def ParseMovieList(self, **kwargs) -> Dict:
        """
        Parses all movies

        :param kwargs: argument dic, need to have resultvar, interface, configname
        :return: Dict ret: 0 or 1 : 1=success
        """
        try:
            uResultVar          = kwargs['resultvar']
            uInterfaceName      = ReplaceVars(kwargs['interface'])
            uConfigName         = ReplaceVars(kwargs['configname'])
            uReturnVar          = kwargs['retvar']

            oInterFace = Globals.oInterFaces.dInterfaces.get(uInterfaceName)
            oSetting = oInterFace.GetSettingObjectForConfigName(uConfigName)
            uContext = oSetting.uContext

            self.ShowInfo("Parsing movies into "+uContext)

            # cache disabled
            # if self.dMovies.get(uContext) is not None:
            #     return {"ret":1}

            uXmlContent = GetVar(uResultVar)
            uXmlContent = EscapeUnicode(uXmlContent)

            iMovieNum = 0  # Order Number of the Channel
            if uXmlContent:
                oXmlMovies               = fromstring(uXmlContent)
                self.dServices[uContext] = {}
                dMovies                  = {}

                Var_DelArray("%s_%s[]" % (uReturnVar,'reference'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'title'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'description'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'descriptionex'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'servicename'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'url_reference'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'time'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'date'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'date_time'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'length'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'filename'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'url_filename'))
                Var_DelArray("%s_%s[]" % (uReturnVar,'index'))

                for oXmlMovie in oXmlMovies:
                    if oXmlMovie.tag=='e2movie': # we might get services as well
                        dMovieDetails                   = {}  # Element to decribe a single movie (number , name, containing channels)
                        iMovieNum                       += 1   # absolute channel num within all bouquets
                        uMovieReference                 = GetXMLTextValue(oXmlMovie, "e2servicereference", True, "N/A")
                        dMovieDetails["reference"]      = uMovieReference
                        dMovieDetails["url_reference"]  = urllib.parse.quote(uMovieReference)
                        dMovieDetails["title"]          = GetXMLTextValue(oXmlMovie, "e2title", False, "No Title")
                        dMovieDetails["description"]    = GetXMLTextValue(oXmlMovie, "e2description", False, "")
                        dMovieDetails["descriptionex"]  = GetXMLTextValue(oXmlMovie, "e2descriptionextended", False, "")
                        dMovieDetails["servicename"]    = GetXMLTextValue(oXmlMovie, "e2servicename", False, "")
                        dMovieDetails["time"]           = GetXMLTextValue(oXmlMovie, "e2time", False, "")
                        dMovieDetails["length"]         = GetXMLTextValue(oXmlMovie, "e2length", False, "0:00")
                        dMovieDetails["filename"]       = GetXMLTextValue(oXmlMovie, "e2filename", False, "")
                        dMovieDetails["url_filename"]   = urllib.parse.quote(dMovieDetails["filename"])
                        dMovieDetails["index"]          = ("000"+str(iMovieNum))[-3]

                        iTime:int                       = ToInt(dMovieDetails["time"])
                        oTime:struct_time               = datetime.fromtimestamp(iTime, timezone.utc).timetuple()
                        sTime:str                       = Globals.oLanguage.GetLocalizedTime(bWithSeconds=False, oTime=oTime)
                        sDate:str                       = Globals.oLanguage.GetLocalizedDate(bLongDate=False,bLongDay=False,bLongMonth=False, oTime=oTime)

                        dMovieDetails["time"]           = sTime
                        dMovieDetails["date"]           = sDate
                        dMovieDetails["date_time"]      = sDate+" "+sTime


                        for uKey in dMovieDetails:
                            uTag = "%s_%s[%s]" % (uReturnVar,uKey,iMovieNum)
                            SetVar(uTag,dMovieDetails[uKey] )
                            self.ShowDebug("Got MovieDetail:"+uTag+":"+dMovieDetails[uKey])

                        dMovies[uMovieReference]    = dMovieDetails

                self.dServices[uContext] = dMovies
                return {"ret":1}
            else:
                self.ShowError("No Movies Data in Source Var:"+uResultVar)
        except Exception as e:
            self.ShowError(uMsg="Can''t parse movies, invalid xml", uParConfigName=self.uConfigName, oException=e)
        return {"ret":0}

    def GetLogoPack(self) -> str:
        """
        Finds the first installed tv-logo pack
        :return: The first installed logo pack name
        """

        if Globals.aLogoPackFolderNames:
            return Globals.aLogoPackFolderNames[0]
        else:
            self.ShowError("Script helper_enigma: No TV Logos available")
            return ""

    def FindChannelLogo(self,uChannelName:str, uReference:str, uLogoPackFolderName:str) -> str:
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

    def FindChannelLogo_sub(self,uChannelName:str, uReference:str, uLogoPackFolderName:str) -> str:
        """
        Helper function to just find a channel logo file, or none if not found

        :param str uChannelName: The name of the channel to look for
        :param str uReference: The SAT Reference
        :param str uLogoPackFolderName: the name of the folder (only the folder name, not the fullpath) in "recources" , below "tvlogos"
        :return: The logo file name (full pazh), or "text:Channelname" if logo file can't be found
        """

        if uReference:
            dReferences:Dict[str,str] = self.dReferences.get(uLogoPackFolderName)
            if dReferences is not None:
                uFnLogo = dReferences.get(self.NormalizeReference(uReference))
                if uFnLogo is not None:
                    uFnLogo = self.NormalizeName(uFnLogo.replace("\n",""))+".png"
                    uFnLogo = self.dLogos[uLogoPackFolderName].get(uFnLogo)
                    if uFnLogo is not None:
                        return uFnLogo.replace(Globals.oPathResources.string, '$var(RESOURCEPATH)')

            uFnLogo = self.dLogos[uLogoPackFolderName].get(self.NormalizeReference(uReference))
            if uFnLogo is not None:
                return uFnLogo.replace(Globals.oPathResources.string, '$var(RESOURCEPATH)')

        dPackLogos:Dict[str,str] = self.dLogos.get(uLogoPackFolderName)

        uFnLogo = dPackLogos.get(self.NormalizeName(uChannelName+".png", False))
        if uFnLogo is None:
            uFnLogo = dPackLogos.get(self.NormalizeName(uChannelName+".png", True))
        if uFnLogo:
            uFnLogo = uFnLogo.replace(Globals.oPathResources.string, '$var(RESOURCEPATH)')
        return uFnLogo

    def CollectAllChannelLogos(self,uLogoPackFolderName:str) -> None:
        """
        Collect all channel logos in a dict (if not already done)
        """
        if not uLogoPackFolderName in self.dLogos:
            self.dLogos[uLogoPackFolderName] = {}
            self.CollectAllChannelLogos_sub(oPath=Globals.oPathTVLogos,uLogoPackFolderName=uLogoPackFolderName)

    def CollectAllChannelLogos_sub(self,oPath,uLogoPackFolderName:str,bFirst=True) -> None:
        """
        Helper function to recursive get all files in a folder tree
        :param cPath oPath: The start folder in the folder tree
        :param bool bFirst: Falg, is this been called first time on recursion
        :param str uLogoPackFolderName: the name of the folder (only the folder name, not the fullpath) in "recources" , below "tvlogos"
        """

        oFinalPath:cPath
        aFolders:List[str]

        if bFirst:
            oFinalPath = oPath+uLogoPackFolderName
            self.LoadRefences(oPath=oFinalPath,uLogoPackFolderName=uLogoPackFolderName)
        else:
            oFinalPath = oPath

        self.GetFolderFiles(oPath=oFinalPath,uLogoPackFolderName=uLogoPackFolderName)
        aFolder = oFinalPath.GetFolderList(bFullPath=True)
        for uFolder in aFolder:
            self.CollectAllChannelLogos_sub(cPath(uFolder),uLogoPackFolderName,False)


    def LoadRefences(self,oPath:cPath,uLogoPackFolderName:str) -> None:

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
                uReference= self.NormalizeReference(uReference)
                self.dReferences[uLogoPackFolderName][uReference] = uFileName.split("-")[0]

    def GetFolderFiles(self,oPath:cPath,uLogoPackFolderName:str) -> None:
        """
        Helper function to get all files in a folder (not folder)

        :param cPath oPath: The folder to collect the files
        :param str uLogoPackFolderName: The TV Logo Pack Folder name
        """
        aFileList:List[str]      = oPath.GetFileList(bFullPath=True,bSubDirs=False)
        uBaseName:str

        for uFile in aFileList:
            uBaseName = os.path.basename(uFile)
            uFileBaseNameStandard = self.NormalizeName(uBaseName)
            self.dLogos[uLogoPackFolderName][uFileBaseNameStandard] = uFile
            # if the filename is a refenece, normalize it and add it
            if uBaseName.count("_")>3:
                self.dLogos[uLogoPackFolderName][self.NormalizeReference(uFileBaseNameStandard)] = uFile


    # noinspection PyMethodMayBeStatic
    def NormalizeName(self, uFnPicture:str, bRemoveHD:bool = False) -> str:
        """
        Helper function to increase the match rate of icon names to channle names by removing blanks and special characters

        :param str uFnPicture: the core picture name
        :param bool bRemoveHD: Remove the 'HD', 'UHD' tags as well
        :return: normalized file name
        """

        uFnPicture = uFnPicture.lower().replace(" ", "").replace("/","").replace("\\","").replace("+","plus").replace("-","").replace("_","")

        if bRemoveHD:
            uFnPicture = uFnPicture.replace("uhd.",".").replace("sd.",".").replace("hd.",".")
        return remove_umlaut(uFnPicture)

    # noinspection PyMethodMayBeStatic
    def NormalizeReference(self, uReference:str) -> str:
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

def remove_umlaut(string:str) -> str:
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


