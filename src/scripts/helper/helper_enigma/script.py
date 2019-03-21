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

from xml.etree.ElementTree                  import fromstring

from ORCA.scripts.BaseScript                import cBaseScript
from ORCA.vars.Access                       import GetVar
from ORCA.vars.Access                       import SetVar
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.utils.TypeConvert                 import EscapeUnicode
from ORCA.utils.XML                         import GetXMLTextValue
from ORCA.utils.Path                        import cPath

import ORCA.Globals as Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>Enigma Helper Script</name>
      <description language='English'>Enigma Helper Script (for DVB Receiver)</description>
      <description language='German'>Enigma Hilfs - Skript (Für DVB Receiver)</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/helper/helper_enigma</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/helper_enigma.zip</sourcefile>
          <targetpath>scripts/helper</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/helper/helper_enigma/script.pyc</file>
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
    |For assign_channels: 0/1 Replace all (1) of only unconfigured channels (with name "discover"
    |-
    |retvar
    |for get_channelreference: The var name for the result (the reference)
    |-
    |channelnum
    |for get_channelreference: The channelnum to get the reference for
    |}</div>

    Remarks:
    "parse_services": Needs to done first, Reads all services for a specific Enigma box into the script
    "get_channelreference": Will return the channel reference for a channel number
    "assign_channels": Sets the TV Logos for the parsed channels

    WikiDoc:End
    """

    def __init__(self):
        cBaseScript.__init__(self)
        self.uType          = u'HELPERS'
        self.dServices      = {}
        self.dLogos         = {}

    def Init(self,uScriptName,uScriptFile=u''):
        """ Main Init, loads the Enigma Script"""
        cBaseScript.Init(self,uScriptName,uScriptFile)

    def RunScript(self, *args, **kwargs):
        """ Main Entry point, parses the cmd_type and calls the relevant functions """
        try:
            if 'cmd_type' in kwargs:
                uCmdType = kwargs['cmd_type']
                if uCmdType == u'parse_services':
                    return self.ParseServices(**kwargs)
                if uCmdType == u'get_channelreference':
                    return self.GetChannelReference(**kwargs)
                if uCmdType == u'assign_channels':
                    return self.AssignChannels(**kwargs)

        except Exception as e:
            self.ShowError("Can''t run Enigma Helper script, invalid parameter",e)
            return 1

    def AssignChannels(self, **kwargs):
        """
        Sets the TV Logos for the parsed channels

        :param kwargs: argument dic, need to have definitionalias, interface, configname, force
        """
        try:
            uAlias           = ReplaceVars(kwargs['definitionalias'])
            uInterfaceName   = ReplaceVars(kwargs['interface'])
            uConfigName      = ReplaceVars(kwargs['configname'])
            bForce           = ReplaceVars(kwargs['force'])!='0'
            oInterFace       = Globals.oInterFaces.dInterfaces.get(uInterfaceName)
            oSetting         = oInterFace.GetSettingObjectForConfigName(uConfigName)
            uContext         = oSetting.uContext
            uSection         = Globals.uDefinitionName

            dServices = self.dServices.get(uContext,{})
            aBouquets = dServices.get("Bouquets",[])
            for dBouquetDetail in aBouquets:
                iBouquetNumber = dBouquetDetail["BouquetNum"]
                if iBouquetNumber <5:
                    uBouquetName   = dBouquetDetail["Name"]
                    uVarName = uAlias + "_bouquet_name["+str(iBouquetNumber)+"]"
                    uVarValue = uBouquetName
                    Globals.oDefinitionConfigParser.set(uSection, uVarName, EscapeUnicode(uVarValue))
                    SetVar(uVarName=uVarName, oVarValue=uVarValue)
                    dChannels = dBouquetDetail.get("Channels",{})
                    for iBouquetChannelNum in dChannels:
                        if iBouquetChannelNum<30:
                            dChannel = dChannels[iBouquetChannelNum]
                            uVarName = uAlias+"%s[%d][%d]" % ("_tvlogo",iBouquetNumber,iBouquetChannelNum)
                            if Globals.oDefinitionConfigParser.get(uSection, uVarName) == "discover" or bForce:
                                uVarValue = self.FindChannelLogo(dChannel["ChannelName"])
                                Globals.oDefinitionConfigParser.set(uSection, uVarName, EscapeUnicode(uVarValue))
                                SetVar(uVarName=uVarName, oVarValue=uVarValue)
                                uVarName = uAlias+"%s[%d][%d]" % ("_tvchannel",iBouquetNumber,iBouquetChannelNum)
                                uVarValue = str(dChannel["ChannelNum"])
                                Globals.oDefinitionConfigParser.set(uSection, uVarName, uVarValue)
                                SetVar(uVarName=uVarName, oVarValue=uVarValue)

            Globals.oDefinitionConfigParser.write()

        except Exception as e:
            self.ShowError("Can''t assign channelnumbers", e)

    def GetChannelReference(self, **kwargs):
        """
        Will return the channel reference for a channel number

        :param kwargs: argument dic, need to have retvar, channelnum, interface, configname
        """

        uContext    = u''
        uChannelNum = u''

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
            self.ShowError("Can''t find channelreference:"+uChannelNum+" context:"+uContext, e)
            if not uContext in self.dServices:
                self.ShowError("Context not found, available context:")
                for uKey in self.dServices:
                    self.ShowError(uKey)
            else:
                self.ShowError("Channel not found, available channels:")
                for iChannelNum in self.dServices[uContext]["Channels"]:
                    self.ShowError(str(iChannelNum))


    def ParseServices(self, **kwargs):
        """
        Needs to done first, Reads all services for a specific Enigma box into the script

        :param kwargs: argument dic, need to have resultvar, interface, configname
        :return: 0
        """
        try:
            uResultVar          = kwargs['resultvar']
            # uDstVarName         = args['retvar']
            uInterfaceName      = ReplaceVars(kwargs['interface'])
            uConfigName         = ReplaceVars(kwargs['configname'])

            oInterFace = Globals.oInterFaces.dInterfaces.get(uInterfaceName)
            oSetting = oInterFace.GetSettingObjectForConfigName(uConfigName)
            uContext = oSetting.uContext

            self.ShowInfo("Parsing Services into "+uContext)

            if self.dServices.get(uContext) is not None:
                return 0

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

                            # print uContext,":",uChannelName,":",iChannelNum

                            # SetVar(uVarName=uDstVarName+"_channelservice["+str(iChannelNum)+"]",uContext=uContext,oVarValue=str(iChannelNum))
                        dBouquetDetails["Channels"]   = dBouquetChannels
                        dBouquetDetails["Name"]       = uBouquetName
                        dBouquetDetails["BouquetNum"] = iBouquetNum
                        aBouquets.append(dBouquetDetails)

                self.dServices[uContext] = {}
                self.dServices[uContext]["Bouquets"]=aBouquets
                self.dServices[uContext]["Channels"]=dChannels
                return 1
            else:
                self.ShowError("No Services Data in Source Var:"+uResultVar)
        except Exception as e:
            self.ShowError("Can''t parse services, invalid xml", e)
        return 0

    def FindChannelLogo(self,uChannelName):
        """
        Finds a channel Logo in the list of all logo files

        :rtype: string
        :param string uChannelName: The name of the chanell to look for
        :return: The logo file name (full pazh), or "text:Channelname" if logo file can't be found
        """
        self.CollectAllChannelLogos()
        iPos = uChannelName.find("/")
        if iPos>0:
            uChannelName=uChannelName[:iPos]

        uFnLogo = self.FindChannelLogo_sub(uChannelName=uChannelName)
        if uFnLogo == u"" or uFnLogo is None:
            uFnLogo = u"text:"+uChannelName
        return uFnLogo

    def FindChannelLogo_sub(self,uChannelName):
        """
        Helper function to just find a channel logo file, or nobe if not find

        :rtype: string
        :param string uChannelName: The name of the chanell to look for
        :return: The logo file name (full pazh), or "text:Channelname" if logo file can't be found
        """
        uCheck = uChannelName+".png"
        uCheck = self.NormalizeName(uCheck)
        uFnLogo = self.dLogos.get(uCheck)
        if uFnLogo is None:
            uFnLogo = self.dLogos.get(self.NormalizeName(uCheck, True))
        if uFnLogo:
            uFnLogo = uFnLogo.replace(Globals.oPathResources.string, '$var(RESOURCEPATH)')
        return uFnLogo

    def CollectAllChannelLogos(self):
        """
        Collect all chanel logos in a dict (if not already done)
        """
        if len(self.dLogos)==0:
            self.CollectAllChannelLogos_sub(oPath=cPath("$var(RESOURCEPATH)/tvlogos"))

    def CollectAllChannelLogos_sub(self,oPath):
        """
        Helper function to recursive get all files in a folder tree
        :param cPath oPath: The start folder in the folder tree
        """
        self.GetFolderFiles(oPath)
        aFolder = oPath.GetFolderList(bFullPath=True)
        for uFolder in aFolder:
            self.CollectAllChannelLogos_sub(cPath(uFolder))

    def GetFolderFiles(self,oPath):
        """
        Helper function to get all files in a folder (not folder)

        :param cPath oPath: The folder to collect the files
        """
        aFileList=oPath.GetFileList(bFullPath=True,bSubDirs=True)
        for uFile in aFileList:
            self.dLogos[self.NormalizeName(os.path.basename(uFile))]=uFile
            self.dLogos[self.NormalizeName(os.path.basename(uFile),True)] = uFile

    def NormalizeName(self, uFnPicture, bRemoveHD = False):
        """
        Helper function to increase the match rate of icon names to channle names by removing blanks and special characters

        :rtype: string
        :param string uFnPicture: the core picture name
        :param bool bRemoveHD: Remove the 'HD', 'UHD' tags as well
        :return: normalized file name
        """
        if bRemoveHD:
            uFnPicture=uFnPicture.lower().replace("uhd","").replace("hd","")
        return uFnPicture.lower().replace(" ", "").replace("/","").replace("\\","")
