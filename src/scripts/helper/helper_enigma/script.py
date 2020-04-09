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


from typing                                 import Dict
from typing                                 import List
from typing                                 import Union
from typing                                 import cast


from time                                   import struct_time
from datetime                               import datetime
from datetime                               import timezone
import urllib
from xml.etree.ElementTree                  import Element

from ORCA.scripts.BaseScript                import cBaseScript
from ORCA.vars.Access                       import GetVar
from ORCA.vars.Access                       import SetVar
from ORCA.vars.Actions                      import Var_DelArray
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.utils.TypeConvert                 import EscapeUnicode
from ORCA.utils.TypeConvert                 import ToInt
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.XML                         import GetXMLTextValue
from ORCA.utils.XML                         import LoadXMLString

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.interfaces.BaseInterface import cBaseInterFace
    from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
else:
    from typing import TypeVar
    cBaseInterFace          = TypeVar("cBaseInterFace")
    cBaseInterFaceSettings  = TypeVar("cBaseInterFaceSettings")

typeReference       = Dict[str,str]
typeReferences      = Dict[str,typeReference]

typeSingleChannel   = Dict[str,Union[int,str]]
typeChannels        = Dict[int,typeSingleChannel]
typeMoviedetails    = Dict[str,str]
typeMovies          = Dict[str,typeMoviedetails]
typeMovieList       = Dict[str,typeMovies]

typeBouquetChannels = Dict[int,typeSingleChannel]
typeBouquetDetails  = Dict[str,Union[typeBouquetChannels,int,str]]
typeBouquetsList    = List[typeBouquetDetails]


typeServiceList    = Dict[str,Union[typeReferences,typeBouquetsList,Dict]]
typeServices       = Dict[str,typeServiceList]



'''
<root>
  <repositorymanager>
    <entry>
      <name>Enigma Helper Script</name>
      <description language='English'>Enigma Helper Script (for DVB Receiver)</description>
      <description language='German'>Enigma Hilfs - Skript (Für DVB Receiver)</description>
      <author>Carsten Thielepape</author>
      <version>5.0.1</version>
      <minorcaversion>5.0.1</minorcaversion>
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
        super().__init__()
        self.uType:str                  = u'HELPERS'
        self.uIniFileLocation:str       = u'none'
        self.dServices                  = {}
        self.dMovies:typeMovieList      = {}

    def Init(self, uObjectName: str, oFnObject: Union[cFileName, None] = None) -> None:
        """ Main Init, loads the Enigma Script"""
        super().Init(uObjectName= uObjectName,oFnObject=oFnObject)

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
                    self.GetChannelReference(**kwargs)
                    return None
                if uCmdType == u'assign_channels':
                    self.AssignChannels(**kwargs)
                    return None
            return None
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
            oSetting:cBaseInterFaceSettings = oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
            uContext:str                    = oSetting.uContext
            uSection:str                    = Globals.uDefinitionName

            iMaxBouquets:int                = 9
            iMaxChannelsPerBouquets:int     = 27

            iBouquetNumber:int
            uBouquetName:str
            dBouquetDetail:Dict
            uVarName:str
            uVarValue:str
            dChannels:Dict[int,Dict]

            dServices:Dict[str,Union[Dict,List]] = self.dServices.get(uContext,{})
            aBouquets:typeBouquetsList = dServices.get("Bouquets",[])

            if uLogoPackFolderName==u'':
                uLogoPackFolderName=self.GetLogoPack()

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
                                uVarValue = self.FindChannelLogo(uChannelName=dChannel["ChannelName"],uReference=dChannel["Reference"],uLogoPackFolderName=uLogoPackFolderName)
                                Globals.oDefinitionConfigParser.set(uSection, uVarName, EscapeUnicode(uVarValue))
                                SetVar(uVarName=uVarName, oVarValue=uVarValue)
                                uVarName = uAlias+"%s[%d][%d]" % ("_tvchannel",iBouquetNumber,iBouquetChannelNum)
                                uVarValue = str(dChannel["ChannelNum"])
                                Globals.oDefinitionConfigParser.set(uSection, uVarName, uVarValue)
                                SetVar(uVarName=uVarName, oVarValue=uVarValue)
            Globals.oDefinitionConfigParser.write()
            return None

        except Exception as e:
            self.ShowError(uMsg="Can''t assign channel numbers", uParConfigName=self.uConfigName,oException=e)
            return None

    def GetLogoPack(self) -> str:
        """
        Finds the first installed tv-logo pack
        :return: The first installed logo pack name
        """

        if Globals.aLogoPackFolderNames:
            return Globals.aLogoPackFolderNames[0]
        else:
            self.ShowError(uMsg="Script TV-Logos: No TV Logos available")
            return ""


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
            oSetting        = oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
            uContext        = oSetting.uContext
            uChannelNum     = ReplaceVars(uOrgIn=uChannelNum,uContext=uContext)
            uReference      = self.dServices[uContext]["Channels"][int(uChannelNum)]["Reference"]
            SetVar(uVarName=uDstVarName , uContext=uContext, oVarValue=uReference)
            return None
        except Exception as e:
            self.ShowError(uMsg="Can''t find channelreference:"+uChannelNum+" context:"+uContext, uParConfigName=self.uConfigName, oException=e)
            if not uContext in self.dServices:
                self.ShowError(uMsg="Context not found, available context:")
                for uKey in self.dServices:
                    self.ShowError(uMsg=uKey)
            else:
                self.ShowError(uMsg="Channel not found, available channels:")
                for iChannelNum in self.dServices[uContext]["Channels"]:
                    self.ShowError(uMsg=str(iChannelNum))
            return None

    def ParseServices(self, **kwargs) -> Dict:
        """
        Needs to done first, Reads all services for a specific Enigma box into the script

        :param kwargs: argument dic, need to have resultvar, interface, configname
        :return: Dict ret: 0 or 1 : 1=success
        """
        try:
            uResultVar:str                  = kwargs['resultvar']
            uInterfaceName:str              = ReplaceVars(kwargs['interface'])
            uConfigName:str                 = ReplaceVars(kwargs['configname'])

            oInterFace:cBaseInterFace       = Globals.oInterFaces.dInterfaces.get(uInterfaceName)
            oSetting:cBaseInterFaceSettings = oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
            uContext:str                    = oSetting.uContext
            oXmlBouquet:Element

            self.ShowInfo(uMsg="Parsing Services into "+uContext)

            if self.dServices.get(uContext) is not None:
                return {"ret":1}

            uXmlContent:str = GetVar(uResultVar)
            uXmlContent = EscapeUnicode(uXmlContent)

            iBouquetNum:int = 0  # Order Number of the Channel
            iBouquetChannelNum:int
            uBouquetName:str
            iChannelNum:int = 0  # Absolute Channel num, through all Bouquets
            uReference:str
            uChannelName:str
            oXmlServices:Element

            if uXmlContent:
                # oET_Root = fromstring(uXmlContent)
                # oXmlBouquets = oET_Root.find("e2bouquet")
                oXmlBouquets:Element                = LoadXMLString(uXML=uXmlContent)
                dChannels:typeChannels              = {} # Bouquet independent list of all channels
                aBouquets:typeBouquetsList          = [] # List of all bouquets as dBouquetDetails
                for oXmlBouquet in oXmlBouquets:
                    if oXmlBouquet.tag=='e2bouquet': # we might get services as well
                        dBouquetDetails:typeBouquetDetails     = {}    # Element to decribe a single bouquet (number , name, containing channels)
                        dBouquetChannels:typeBouquetChannels   = {}    # Dict of all channels in a single bouquet, index is Bouquechannelnum
                        iBouquetChannelNum = 0
                        uBouquetName = GetXMLTextValue(oXMLNode=oXmlBouquet,uTag="e2servicename",bMandatory=False,vDefault="NoName"+str(iBouquetNum))
                        iBouquetNum+=1
                        oXmlServices = cast(Element,oXmlBouquet.find("e2servicelist"))
                        for oXmlServiceDetails in oXmlServices:
                            dSingleChannel:typeSingleChannel  = {}   # details of a channel
                            iChannelNum             += 1   # absolute channel num within all bouquets
                            iBouquetChannelNum      += 1   # relative channel num in bouquet
                            uReference   = GetXMLTextValue(oXMLNode=oXmlServiceDetails, uTag="e2servicereference" , bMandatory=True,  vDefault="NoName")
                            uChannelName = GetXMLTextValue(oXMLNode=oXmlServiceDetails, uTag="e2servicename",       bMandatory=False, vDefault="NoName"+str(iChannelNum))
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
                self.ShowError(uMsg="No Services Data in Source Var:"+uResultVar)
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
            uResultVar:str                  = kwargs['resultvar']
            uInterfaceName:str              = ReplaceVars(kwargs['interface'])
            uConfigName:str                 = ReplaceVars(kwargs['configname'])
            uReturnVar:str                  = kwargs['retvar']

            oInterFace:cBaseInterFace       = Globals.oInterFaces.dInterfaces.get(uInterfaceName)
            oSetting:cBaseInterFaceSettings = oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
            uContext:str                    = oSetting.uContext
            uXmlContent:str
            iMovieNum:int
            uMovieReference:str

            self.ShowInfo(uMsg="Parsing movies into "+uContext)

            # cache disabled
            # if self.dMovies.get(uContext) is not None:
            #     return {"ret":1}

            uXmlContent = GetVar(uResultVar)
            uXmlContent = EscapeUnicode(uXmlContent)

            iMovieNum = 0  # Order Number of the Channel
            if uXmlContent:
                oXmlMovies:Element       = LoadXMLString(uXML=uXmlContent)
                self.dMovies[uContext]   = {}
                dMovies:typeMovies       = {}

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
                        dMovieDetails:typeMoviedetails  = {}  # Element to describe a single movie (number , name, containing channels)
                        iMovieNum                       += 1   # absolute channel num within all bouquets
                        uMovieReference                 = GetXMLTextValue(oXMLNode=oXmlMovie, uTag="e2servicereference", bMandatory=True, vDefault="N/A")
                        dMovieDetails["reference"]      = uMovieReference
                        # noinspection Mypy
                        dMovieDetails["url_reference"]  = urllib.parse.quote(uMovieReference)
                        dMovieDetails["title"]          = GetXMLTextValue(oXMLNode=oXmlMovie, uTag="e2title", bMandatory=False, vDefault="No Title")
                        dMovieDetails["description"]    = GetXMLTextValue(oXMLNode=oXmlMovie, uTag="e2description", bMandatory=False, vDefault="")
                        dMovieDetails["descriptionex"]  = GetXMLTextValue(oXMLNode=oXmlMovie, uTag="e2descriptionextended", bMandatory=False, vDefault="")
                        dMovieDetails["servicename"]    = GetXMLTextValue(oXMLNode=oXmlMovie, uTag="e2servicename", bMandatory=False, vDefault="")
                        dMovieDetails["time"]           = GetXMLTextValue(oXMLNode=oXmlMovie, uTag="e2time", bMandatory=False, vDefault="")
                        dMovieDetails["length"]         = GetXMLTextValue(oXMLNode=oXmlMovie, uTag="e2length", bMandatory=False, vDefault="0:00")
                        dMovieDetails["filename"]       = GetXMLTextValue(oXMLNode=oXmlMovie, uTag="e2filename", bMandatory=False, vDefault="")
                        # noinspection Mypy
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
                            self.ShowDebug(uMsg="Got MovieDetail:"+uTag+":"+dMovieDetails[uKey])

                        dMovies[uMovieReference]    = dMovieDetails

                self.dMovies[uContext] = dMovies
                return {"ret":1}
            else:
                self.ShowError(uMsg="No Movies Data in Source Var:"+uResultVar)
        except Exception as e:
            self.ShowError(uMsg="Can''t parse movies, invalid xml", uParConfigName=self.uConfigName, oException=e)
        return {"ret":0}

    def FindChannelLogo(self,*,uChannelName:str, uReference:str, uLogoPackFolderName:str) -> str:
        """
        Finds a channel Logo in the list of all logo files

        :param str uChannelName: The name of the channel to look for
        :param str uReference: The SAT Reference
        :param str uLogoPackFolderName: the name of the folder (only the folder name, not the fullpath) in "recources" , below "tvlogos"
        :return: The logo file name (full path), or "text:Channelname" if logo file can't be found
        """

        dRet:Dict

        if uLogoPackFolderName==u'':
            uLogoPackFolderName=self.GetLogoPack()

        kwargs = {"cmd_type": "get_tvlogofile","channelname":uChannelName,"reference":uReference,"logopackfoldername":uLogoPackFolderName }
        dRet=Globals.oScripts.RunScript("helper_gettvlogo",**kwargs)
        return dRet.get("filename","")


'''
<e2movie>
    <e2servicereference>
    1:0:0:0:0:0:0:0:0:0:/media/hdd/movie/20191101 1711 - Sky Cinema Spooky Halloween HD - Die Legende der Wächter.ts
    </e2servicereference>
    <e2title>Die Legende der Wächter</e2title>
    <e2description>Fantasyfilm</e2description>
    <e2descriptionextended>
    Atemberaubend animiertes Fantasyabenteuer für die ganze Familie nach den Kinderbüchern von Kathryn Lasky.
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


