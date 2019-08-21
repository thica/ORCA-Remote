# -*- coding: utf-8 -*-
#  Onkyo eiscp
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

from time                   import sleep
from threading              import Thread
from threading              import currentThread
from struct                 import pack, unpack
from xml.etree.ElementTree  import ElementTree, fromstring

import select
import socket
import binascii

from kivy.logger            import Logger
from kivy.clock             import Clock
from kivy.compat            import PY2
from kivy.network.urlrequest import UrlRequest

from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
from ORCA.interfaces.InterfaceResultParser import cInterFaceResultParser
from ORCA.vars.Replace      import ReplaceVars
from ORCA.vars.Access       import SetVar
from ORCA.vars.Actions      import Var_DelArray, Var_Int2Hex
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.TypeConvert import ToBytes

from ORCA.utils.wait.StartWait  import StartWait
from ORCA.utils.XML         import *
from ORCA.utils.FileName    import cFileName
from ORCA.utils.PyXSocket   import cPyXSocket

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Onkyo EISCP (LAN)</name>
      <description language='English'>Onkyo EISCP Interface (LAN/IP)</description>
      <description language='German'>Onkyo EISCP Interface (LAN/IP)</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/eiscp</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/eiscp.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>EISCP Discover</name>
        </dependency>
      </dependencies>
      <skipfiles>
        <file>eiscp/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    class cDeviceSettings(object):
        def __init__(self,oInterFace,oSetting):
            #We set some default values to assure that the some system vars has been set

            self.oInterFace           = oInterFace
            self.oSetting             = oSetting
            self.uVar_MacAdress       = u"000000000000"
            self.uVar_Brand           = u"Unknown"
            self.uVar_Category        = u"Unknown"
            self.uVar_DeviceName      = u"Unknown"
            self.uVar_Year            = u"Unknown"
            self.uVar_Destination     = u"Unknown"
            self.uVar_Model           = u"Unknown"
            self.uVar_ModelIconUrl    = u""
            self.uVar_FriendlyName    = u"Unknown"
            self.uVar_FirmwareVersion = u"Unknown"
            self.dVar_NetService      = {'1':{'id':'0e','name':'TuneIn Radio'}}
            self.dVar_Sources         = {'1':{'id':'10','name':'BD/DVD'}}
            self.dVar_ListeningModes  = {'1':{'code':'MUSIC','name':'Music'}}
            self.dVar_Presets         = {'1':{'id':'01','name':'Unknown'}}

            self.uVar_SWLFormat       = u"{:+03X}"
            self.uVar_CTLFormat       = u"{:+03X}"

            self.uVar_Bass_Min        = u""
            self.uVar_Bass_Max        = u""
            self.uVar_Treble_Min      = u""
            self.uVar_Treble_Max      = u""
            self.uVar_CenterLevel_Min = u""
            self.uVar_CenterLevel_Max = u""
            self.uVar_SubWooferLevel_Min = u""
            self.uVar_SubWooferLevel_Max = u""
            self.uVar_SWLMin          = u''
            self.uVar_SWLMax          = u''

            self.dCapability          = self.oInterFace.dDeviceCaps['TX-NR676E']

        def ParseXML(self,uXML, oAction):
            try:
                oXML = ElementTree(fromstring(uXML))
                oXML = oXML.find("device")

                self.uVar_MacAdress         = GetXMLTextValue       (oXML,"macaddress"      ,False,"Unknown")
                self.uVar_Brand             = GetXMLTextValue       (oXML,"brand"           ,False,"Unknown")
                self.uVar_Category          = GetXMLTextValue       (oXML,"category"        ,False,"Unknown")
                self.uVar_DeviceName        = GetXMLTextAttributeVar(oXML,"id"              ,False,"Unknown")
                self.uVar_Year              = GetXMLTextValue       (oXML,"year"            ,False,"Unknown")
                self.uVar_Destination       = GetXMLTextValue       (oXML,"destination"     ,False,"Unknown")
                self.uVar_Model             = GetXMLTextValue       (oXML,"model"           ,False,"Unknown")
                self.uVar_ModelIconUrl      = GetXMLTextValue       (oXML,"modeliconurl"    ,False,"")
                self.uVar_FriendlyName      = GetXMLTextValue       (oXML,"friendlyname"    ,False,"Unknown")
                self.uVar_FirmwareVersion   = GetXMLTextValue       (oXML,"firmwareversion" ,False,"Unknown")

                oXMLControlList             = oXML.find("controllist")
                if oXMLControlList is not None:
                    for oControlElement in oXMLControlList:
                        uID = GetXMLTextAttribute(oControlElement,'id',False,u'')
                        if uID == "Bass":
                            uZone = GetXMLTextAttribute(oControlElement, 'zone', False, u'')
                            if uZone == "1":
                                self.uVar_Bass_Min = GetXMLTextAttribute(oControlElement, 'min', False, u'-10')
                                self.uVar_Bass_Max = GetXMLTextAttribute(oControlElement, 'max', False, u'+10')
                        if uID == "Treble":
                            uZone = GetXMLTextAttribute(oControlElement, 'zone', False, u'')
                            if uZone == "1":
                                self.uVar_Treble_Min = GetXMLTextAttribute(oControlElement, 'min', False, u'-10')
                                self.uVar_Treble_Max = GetXMLTextAttribute(oControlElement, 'max', False, u'+10')
                        if uID == "Center Level":
                            uZone = GetXMLTextAttribute(oControlElement, 'zone', False, u'')
                            if uZone == "1":
                                self.uVar_CenterLevel_Min = GetXMLTextAttribute(oControlElement, 'min', False, u'-12')
                                self.uVar_CenterLevel_Max = GetXMLTextAttribute(oControlElement, 'max', False, u'+12')
                        if uID == "Subwoofer":
                            uZone = GetXMLTextAttribute(oControlElement, 'zone', False, u'')
                            if uZone == "1":
                                self.uVar_SubWooferLevel_Min = GetXMLTextAttribute(oControlElement, 'min', False, u'-15')
                                self.uVar_SubWooferLevel_Max = GetXMLTextAttribute(oControlElement, 'max', False, u'+12')

                oXMLNetServices = oXML.find("netservicelist")
                self.dVar_NetService.clear()
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_NetService_id[]')
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_NetService_name[]')
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_NetService_value[]')
                if oXMLNetServices is not None:
                    iPos=0
                    for oNetServiceElement in oXMLNetServices:
                        uID    = GetXMLTextAttribute(oNetServiceElement , 'id', False, u'')
                        uName  = GetXMLTextAttribute(oNetServiceElement , 'name', False, u'')
                        uValue = GetXMLTextAttribute(oNetServiceElement,  'value', False, u'')
                        if uID and uValue=="1":
                            iPos = iPos + 1
                            self.dVar_NetService[str(iPos)]={"id":uID,"name":uName}

                oXMLPresets = oXML.find("presetlist")
                # <preset id="01" band="0" freq="0" name="" />
                self.dVar_Presets.clear()
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_Presets_id[]')
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_Presets_name[]')
                if oXMLPresets is not None:
                    iPos=0
                    for oPresetElement in oXMLPresets:
                        uID    = GetXMLTextAttribute(oPresetElement, 'id', False, u'')
                        uName  = GetXMLTextAttribute(oPresetElement, 'name', False, u'')
                        if uID and uName!="":
                            iPos = iPos + 1
                            self.dVar_Presets[str(iPos)]={"id":uID,"name":uName}

                oXMLSources = oXML.find("selectorlist")
                self.dVar_Sources.clear()
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_Sources_id[]')
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_Sources_name[]')
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_Sources_value[]')
                if oXMLSources is not None:
                    iPos=0
                    for oSourceElement in oXMLSources:
                        uID    = GetXMLTextAttribute(oSourceElement, 'id', False, u'')
                        uName  = GetXMLTextAttribute(oSourceElement, 'name', False, u'')
                        uValue = GetXMLTextAttribute(oSourceElement, 'value', False, u'')
                        if uID and uValue=="1":
                            iPos = iPos + 1
                            self.dVar_Sources[str(iPos)]={"id":uID,"name":uName}

                oXMLControls = oXML.find("controllist")
                self.dVar_ListeningModes.clear()
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_ListeningModes_id[]')
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_ListeningModes_name[]')
                Var_DelArray(uVarName = oAction.uGlobalDestVar+u'_ListeningModes_code[]')
                if oXMLControls is not None:
                    iPos = 0
                    for oControlElement in oXMLControls:
                        uID = GetXMLTextAttribute(oControlElement, 'id', False, u'')
                        uValue = GetXMLTextAttribute(oControlElement, 'value', False, u'')
                        uCode = GetXMLTextAttribute(oControlElement, 'code', False, u'')
                        if uID.startswith(u"LMD ") and uValue == "1":
                            iPos = iPos + 1
                            self.dVar_ListeningModes[str(iPos)] = {"code": uCode, "name": uID[4:]}

                dCapability = self.oInterFace.dDeviceCaps.get(self.uVar_Model)
                if dCapability is not None:
                    self.uVar_SWLFormat=dCapability['SWLFORMAT']
                    self.uVar_SWLMin=dCapability['SWLMIN']
                    self.uVar_SWLMax=dCapability['SWLMAX']
                    self.uVar_CTLFormat=dCapability['CTLFORMAT']
                    self.uVar_SWLMin=dCapability['CTLMIN']
                    self.uVar_SWLMax=dCapability['CTLMAX']
                    self.dCapability = dCapability

                return True
            except Exception as e:
                self.oInterFace.ShowError(uMsg="Error parsing NRI (Device Information) response", oException=e)
                return False

        def WriteVars(self,uVarPrefix, oAction):

            if self.oSetting.oResultParser is None:
                self.oSetting.oResultParser = cInterFaceResultParser(self.oInterFace, self.oSetting.uConfigName)
                self.oSetting.oResultParser.uGlobalParseResultOption = self.oSetting.aIniSettings.uParseResultOption
                self.oSetting.oResultParser.uGlobalTokenizeString = self.oSetting.aIniSettings.uParseResultTokenizeString

            for uAttributName in self.__dict__:
                if uAttributName.startswith('uVar_'):
                    uValue= self.__dict__[uAttributName]
                    self.oSetting.oResultParser.SetVar2(uValue, oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Device Configuration', uAddName=u"_" + uAttributName[5:])
                if uAttributName.startswith("dVar_"):
                    dDict = self.__dict__[uAttributName]
                    for uKey in dDict:
                        for uSubKey in dDict[uKey]:
                            uValue = dDict[uKey][uSubKey]
                            self.oSetting.oResultParser.SetVar2(uValue, oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Device Configuration', uAddName=u"_" + uAttributName[5:] + "_" + uSubKey + "[" + uKey + "]")
            iIdx = 0
            if self.dCapability is not None:
                for uKey in self.dCapability['ListeningModes']:
                    self.oSetting.oResultParser.SetVar2(uKey, oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Listening Mode', uAddName=u"_ListeningMode_key[" + str(iIdx) + "]")
                    self.oSetting.oResultParser.SetVar2(self.oInterFace.dLMD_Text[uKey], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Listening Mode', uAddName=u"_ListeningMode_name[" + str(iIdx) + "]")
                    iIdx = iIdx +1

    class cInterFaceSettings(cBaseInterFaceSettings):
        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.oSocket            = None
            self.uMsg               = u''
            self.iBufferSize        = 2048

            self.bHeader            = b'ISCP'
            self.iHeaderSize        = 16
            self.iVersion           = 1
            self.bStopThreadEvent   = False
            self.uRetVar            = ''
            self.dResponseActions   = {}
            self.bBusy              = False

            self.aIniSettings.uHost                        = u"discover"
            self.aIniSettings.uPort                        = u"60128"
            self.aIniSettings.uFNCodeset                   = u"CODESET_eiscp_ONKYO_AVR.xml"
            self.aIniSettings.fTimeOut                     = 2.0
            self.aIniSettings.iTimeToClose                 = -1
            self.aIniSettings.uDiscoverScriptName          = u"discover_eiscp"
            self.aIniSettings.uParseResultOption           = u'store'
            self.aIniSettings.fDISCOVER_EISCP_timeout      = 2.0
            self.aIniSettings.uDISCOVER_EISCP_models       = []
            self.aIniSettings.uDISCOVER_UPNP_servicetypes  = "upnp:rootdevice"
            self.aIniSettings.uDISCOVER_UPNP_manufacturer  = "Onkyo & Pioneer Corporation"
            self.oThread                                   = None

        def Connect(self):

            if self.oResultParser is None:
                # Initiate Resultparser
                uCommand,uID=self.oInterFace.ParseResult(None,"",self)

            bRet=True
            if not cBaseInterFaceSettings.Connect(self):
                return False

            if (self.aIniSettings.uHost=="") or (self.aIniSettings.uPort==u""):
                self.ShowError(u'Cannot connect on empty host of port ')
                self.bOnError=True
                return False


            try:
                self.oSocket = cPyXSocket(socket.AF_INET, socket.SOCK_STREAM)
                self.oSocket.SetBlocking(0)
                self.oSocket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.oSocket.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.oSocket.settimeout(self.aIniSettings.fTimeOut)
                self.oSocket.connect((str(self.aIniSettings.uHost),int(self.aIniSettings.uPort)))
                if self.oThread:
                    self.bStopThreadEvent = True
                    self.oThread.join()
                    self.oThread = None

                self.oThread = Thread(target = self.Receive,)
                self.bStopThreadEvent = False
                self.oThread.oParent = self
                self.oThread.start()
            except socket.error as e:
                self.ShowError(u'Cannot open socket:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.oSocket.close()
                self.oSocket = None
            except Exception as e:
                self.ShowError(u'Cannot open socket#2:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.bOnError=True

            if self.oSocket is None:
                self.bOnError=True
                return False

            self.bIsConnected =True
            return self.bIsConnected

        def Disconnect(self):
            if not cBaseInterFaceSettings.Disconnect(self):
                return False

            if self.oThread:
                self.bStopThreadEvent = True
                self.oThread.join()
                self.oThread = None
            self.bOnError = False

        def CreateEISPHeader(self,uCmd):
            uMessage = u'!' + str(self.aIniSettings.iUnitType) + uCmd + '\x0a'
            iDataSize =  len(uMessage)
            return pack('!4sIIBxxx', self.bHeader, self.iHeaderSize, iDataSize, self.iVersion) + ToBytes(uMessage)

        def UnpackEISPResponse(self,sResponseIn):

            sResponse=""

            if len(sResponseIn)==0:
                return u'', ''

            try:
                bHeaderRet, iHeaderSize, iDataSize, iVersionRet = unpack('!4sIIBxxx', sResponseIn[0:self.iHeaderSize])
                if bHeaderRet != self.bHeader:
                    self.ShowDebug(u'Received packet not ISCP: '+ToUnicode(bHeaderRet))
                    return u'',''
                if iVersionRet != self.iVersion:
                    self.ShowDebug(u'ISCP version not supported: '+ToUnicode(iVersionRet))
                    return u'',''
                if len(sResponseIn)==16:
                    #sResponse= self.oSocket.recv(iDataSize)
                    sResponse=self.Helper_ReceiveAll(self.oSocket,iDataSize)
                else:
                    sResponse= sResponseIn[17:]
                if sResponse:
                    if PY2:
                        sMessage = sResponse.rstrip('\x1a\r\n')
                    else:
                        sMessage = sResponse.decode("utf-8").rstrip('\x1a\r\n')
                    iMessageSize = len(sMessage)
                    # parse message
                    sUnitType = sMessage[1]
                    uCommand = ToUnicode(sMessage[2:5])
                    sParameter = sMessage[5:iMessageSize]
                    return uCommand,sParameter
                else:
                    self.ShowDebug(u'Got empty response: '+ToUnicode(sResponseIn))
                    return "", ""
            except Exception as e:
                self.ShowError(u'Cannot parse response:'+sResponse+":"+sResponseIn,e)
                return u'',''

        def Helper_ReceiveAll(self, oSocket, iSize):
            # Helper function to recv n bytes or return None if EOF is hit
            # As windows is ignoring the select timeout we need to ignore the errors

            data = bytes()

            try:
                while len(data) < iSize:
                    packet = oSocket.recv(iSize - len(data))
                    if not packet:
                        self.ShowError("Can't get complete response 1")
                        return data
                    data += packet
                return data
            except Exception as e:
                self.ShowError(u"ReceiveAll:Can't receive response 2",e)
                return data

        def Receive(self):

            # Main Listening Thread to receice eiscp messages
            # self (the settings object) is not reliable passed , to we use it passed from the Thread object

            oThread = currentThread()
            oParent = oThread.oParent

            #Loop until closed by external flag
            try:
                while not oParent.bStopThreadEvent:
                    if oParent.oSocket is not None:

                        # on Windows, the timeout does not work, (known error)
                        # which means the the receiveall will run on error, so we need to skip the error message
                        aReadSocket, aWriteSocket, aExceptional = select.select([oParent.oSocket],[],[],0.1)

                        if len(aReadSocket) >0 and aReadSocket[0]:

                            i = 0
                            while self.bBusy:
                                sleep(0.01)
                                i = i + 1
                                if i > 200:
                                    oParent.ShowError("Busy Time Out")
                                    self.bBusy = False
                            self.bBusy = True

                            # if oParent.aIniSettings.iTimeToClose > 0:
                            #     Clock.unschedule(oParent.FktDisconnect)
                            #     Clock.schedule_once(oParent.FktDisconnect, oParent.aIniSettings.iTimeToClose)

                            sResponseHeader = oParent.Helper_ReceiveAll(aReadSocket[0], 16)
                            if len(sResponseHeader)>0:
                                # Get the Command and the payload
                                uCommand,sResponse=oParent.UnpackEISPResponse(sResponseHeader)

                                # print ("Receive:",uCommand,":",sResponse)

                                # This returns ASCII of sResponse, we will convert it one line later
                                # we might get a response without dedicated requesting it, so lets use an action
                                # from previous request to get the return vars

                                bHandleSpecialResponse = False
                                # Default is the last action (That is the command, where we MIGHT get the response from
                                oTmpAction = self.oAction
                                if uCommand == self.uMsg[:3]:
                                    # if we have a respose to the last action, lets store the action for future use
                                    # in case we got a response without requsting it
                                    # Not 100% logic, but shoud fit in 99.9 % of the cases
                                    if oParent.GetTrigger(uCommand) is None:
                                        oParent.dResponseActions[uCommand] = oTmpAction
                                        bHandleSpecialResponse = True

                                # Lets check , if we have an Trigger set for unrequested responses
                                oActionTrigger = oParent.GetTrigger(uCommand)
                                if oActionTrigger:
                                    oTmpAction=oActionTrigger
                                    bHandleSpecialResponse = True
                                elif bHandleSpecialResponse == False:
                                    # If we dont have an trigger and its not a response to the action
                                    # lets use the stored action, if we have it
                                    if uCommand in oParent.dResponseActions:
                                        oTmpAction = oParent.dResponseActions[uCommand]
                                        bHandleSpecialResponse = True

                                if bHandleSpecialResponse:
                                    if uCommand==u'NLS':
                                        # This might return an adjusted Response
                                        uCommand,sResponse=oParent.oInterFace.Handle_NLS(oTmpAction,sResponse,self)
                                uResponse=ToUnicode(sResponse)
                                if bHandleSpecialResponse:
                                    if uCommand == u'NRI':
                                        oParent.oInterFace.Handle_NRI(oTmpAction, sResponse, oParent)
                                    elif uCommand==u'NJA':
                                        uCommand,uResponse=oParent.oInterFace.Handle_NJA(oTmpAction,uResponse,oParent)
                                    elif uCommand==u'LMD':
                                        uResponse=oParent.oInterFace.ISCP_LMD_To_Text(uResponse)
                                    elif uCommand==u'IFA':
                                        oParent.oInterFace.Split_IFA(oTmpAction,uResponse,oParent)
                                    elif uCommand==u'IFV':
                                         oParent.oInterFace.Split_IFV(oTmpAction,uResponse,oParent)
                                    elif uCommand==u'MVL' or uCommand==u'CTL' or uCommand==u'SWL':
                                        if uResponse!=u'N/A':
                                            uResponse=str(int(uResponse, 16))
                                # If the returned Command is a response to the send message
                                if uCommand==oParent.uMsg[:3]:
                                    #uCmd,uRetVal=self.oInterFace.ParseResult(self.oAction,uResponse,self)
                                    uRetVal = u''
                                    if not oParent.uRetVar==u'':
                                        uTmp=oParent.oAction.uGlobalDestVar
                                        oParent.oAction.uGlobalDestVar=oParent.uRetVar
                                        uCmd,uRetVal=oParent.oInterFace.ParseResult(oParent.oAction,uResponse,oParent)
                                        oParent.oAction.uGlobalDestVar=uTmp
                                    if not oParent.uRetVar==u'' and not uRetVal==u'':
                                        SetVar(uVarName = self.uRetVar, oVarValue = uRetVal)

                                    # we got our response, all other responses are for somebody else
                                    #self.uMsg=''
                                # we have a notification issued by the device, so lets have a look, if we have a trigger code to it
                                oActionTrigger=oParent.GetTrigger(uCommand)

                                if oActionTrigger:
                                    oParent.ShowInfo(u'Calling Trigger for:' + uCommand)
                                    oParent.CallTrigger(oActionTrigger,uResponse)
                                else:
                                    if not uCommand==oParent.uMsg[:3]:
                                        if not uCommand==u'LTN':
                                            if not uCommand==u'':
                                                if not uCommand+ ':'+uResponse=="NST:p--":
                                                    oParent.ShowDebug(u'Discard message:'+uCommand+ ':'+uResponse+': Looking for ('+oParent.uMsg[:3]+')')
#                               self.uMsg=''
                                # We do not need to wait for an response anymore
                                StartWait(0)
                            self.bBusy = False


            except Exception as e:
                self.ShowError(u'Receive:Error Receiving Response:',e)
                self.bIsConnected = False
                self.bBusy = False
            try:
                if self.oSocket is not None:
                    self.ShowDebug(u'Closing socket in Thread')
                    self.oSocket.close()
                    self.oSocket = None
            except Exception as e:
                self.ShowError(u'Error closing socket in Thread',e)

    def __init__(self):
        cBaseInterFace.__init__(self)
        self.aSettings          = {}
        self.oSetting           = None
        self.uResponse          = u''
        self.iBufferSize        = 2048
        self.iWaitMs            = 2000
        self.uPictureType       = u'.bmp'
        self.uRetVar            = u''
        self.uPictureData       = u''
        self.iCursorPos         = 0
        self.iCntNLS            = 0
        self.dDeviceSettings    = {}
        self.dLMD_Text          = {}
        self.dDeviceCaps        = {}
        self.InitDeviceCaps()
        self.InitLVM()
        self.aDiscoverScriptsBlackList = ["iTach (Global Cache)","Keene Kira","ELVMAX"]

    def Init(self, uObjectName, oFnObject=None):
        cBaseInterFace.Init(self,uObjectName, oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self, **kwargs):
        cBaseInterFace.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def GetConfigJSON(self):
        return {"UnitType": {"active": "enabled", "order": 3, "type": "numeric", "title": "$lvar(IFACE_EISCP_1)", "desc": "$lvar(IFACE_EISCP_2)", "section": "$var(ObjectConfigSection)","key": "UnitType", "default":"1" }}

    def DoAction(self,oAction):
        uCmd=oAction.dActionPars.get("commandname",'')
        if uCmd=='favorite pgup' or uCmd=='favorite pgdn':
            self.NLSPage(oAction,uCmd)
        return cBaseInterFace.DoAction(self,oAction)

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        iTryCount       = 0
        iRet            = 1
        uMsg            = oAction.uCmd

        uTst=uMsg[:3]
        if uTst==u'MVL' and uMsg!=u'MVLUP' and uMsg!=u'MVLDOWN' and not uMsg.endswith("QSTN"):
            Var_Int2Hex(uVarName = self.uObjectName+'/'+oSetting.uConfigName+'volumetoset')
        if (uTst==u'CTL' or uTst==u'SWL') and not uMsg.endswith("QSTN"):
            uFormat='{:+03X}'
            uKey = oSetting.aIniSettings.uHost + oSetting.aIniSettings.uPort
            if uKey in self.dDeviceSettings:
                if uTst == u'CTL':
                    uFormat=self.dDeviceSettings[uKey].uVar_CTLFormat
                else:
                    uFormat = self.dDeviceSettings[uKey].uVar_SWLFormat
            Var_Int2Hex(uVarName = self.uObjectName + '/' + oSetting.uConfigName + 'volumetoset', uFormat = uFormat)

        uMsg            = ReplaceVars(uMsg,self.uObjectName+'/'+oSetting.uConfigName)
        uMsg            = ReplaceVars(uMsg)
        oSetting.uMsg   = uMsg
        oSetting.uRetVar= uRetVar

        if uTst == u"NRI":
            uKey = oSetting.aIniSettings.uHost + oSetting.aIniSettings.uPort
            if uKey in self.dDeviceSettings and False:
                self.dDeviceSettings[uKey].WriteVars(uVarPrefix=uRetVar, oAction=oAction)
                return 0
            else:
                self.dDeviceSettings[uKey] = self.cDeviceSettings(self, oSetting)
                # we write the defaults to var, in case we can't connect to the receiver
                self.dDeviceSettings[uKey].WriteVars(uVarPrefix=uRetVar, oAction=oAction)

        # oSetting.Disconnect()
        #Logger.info (u'Interface '+self.uObjectName+': Sending Command: '+sCommand + ' to '+oSetting.sHost+':'+oSetting.sPort)
        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()

            if oSetting.bIsConnected:
                try:
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar,self.uObjectName+'/'+oSetting.uConfigName)
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar)

                    self.ShowInfo (u'Sending Command: '+uMsg + ' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,oSetting.uConfigName)
                    bMsg=oSetting.CreateEISPHeader(uMsg)
                    if oAction.bWaitForResponse:
                        #All response comes to receiver thread, so we should hold the queue until vars are set
                        if uTst!='NRI':
                            StartWait(self.iWaitMs)
                        else:
                            StartWait(2000)
                    oSetting.oSocket.sendall(bMsg)
                    iRet=0
                    break
                except Exception as e:
                    self.ShowError(u'Can\'t Send Message',oSetting.uConfigName,e)
                    iRet=1
                    oSetting.Disconnect()
                    if not uRetVar==u'':
                        SetVar(uVarName = uRetVar, oVarValue = u"Error")
            else:
                if iTryCount==2:
                    self.ShowWarning(u'Nothing done,not connected! ->[%s]' % oAction.uActionName, oSetting.uConfigName)
                if uRetVar:
                    SetVar(uVarName = uRetVar, oVarValue = u"?")

        if oSetting.bIsConnected:
            if oSetting.aIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aIniSettings.iTimeToClose)
        return iRet

    def NLSPage(self,oAction,uCmd):

        oSetting=self.GetSettingObjectForConfigName(oAction.dActionPars.get(u'configname',u''))

        if uCmd=='favorite pgup':
            iSteps=self.iCursorPos-(self.iCntNLS+1)-1
            iSteps=(self.iCursorPos*-1)-1
        else:
            iSteps=(self.iCntNLS+1)-self.iCursorPos-1
            if iSteps==0:
                iSteps=1

        oSetting.SetContextVar("PAGESIZE"," " * abs(iSteps))
        Logger.debug('Cmd:'+uCmd+" count:"+str(self.iCntNLS)+" Pos:"+str(self.iCursorPos)+ " Steps:"+str(iSteps))

    def Split_IFA(self,oAction,uResponse,oSetting):
        # handles the return of Audio Information Request
        uTmp=oAction.uGlobalDestVar
        if not oSetting.uRetVar==u'':
            oAction.uGlobalDestVar=oSetting.uRetVar

        aResponses=uResponse.split(',')

        if len(aResponses)>1:
            oSetting.oResultParser.SetVar2(aResponses[0], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Input Selection', uAddName=u'_audio_input_selection')
            oSetting.oResultParser.SetVar2(aResponses[1], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Input Codec', uAddName=u'_audio_input_codec')
        if len(aResponses)>2:
            oSetting.oResultParser.SetVar2(aResponses[2], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Input Frequency', uAddName=u'_audio_input_frequency')
        if len(aResponses)>3:
            oSetting.oResultParser.SetVar2(aResponses[3], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Input Channels', uAddName=u'_audio_input_channels')
        if len(aResponses)>4:
            oSetting.oResultParser.SetVar2(aResponses[4], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Output Effect', uAddName=u'_audio_output_effect')
        if len(aResponses)>5:
            oSetting.oResultParser.SetVar2(aResponses[5], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Audio Output Channels', uAddName=u'_audio_output_channels')

        if uTmp!=u'':
            oSetting.uRetVar=uTmp

    def Handle_NRI(self,oAction,sResponse,oSetting):
        # Parses the Onkyo Device Information and writes them into vars
        uKey = oSetting.aIniSettings.uHost + oSetting.aIniSettings.uPort
        if uKey not in self.dDeviceSettings:
            self.dDeviceSettings[uKey] = self.cDeviceSettings(self, oSetting)

        self.dDeviceSettings[uKey].ParseXML(sResponse, oAction)
        self.dDeviceSettings[uKey].WriteVars(uVarPrefix=oAction.uGlobalDestVar, oAction=oAction)

    def Handle_NLS(self,oAction,sResponse,oSetting):
        # Handles the NET/USB List Info
        if len(sResponse)>2:
            if sResponse[0]=='C':
                iCurPos=sResponse[1]
                if iCurPos.isdigit():
                    self.iCursorPos=int(iCurPos)
                # if new page delete all old vars
                uTmpCmd = oAction.uCmd

                if sResponse[2]=='P':
                    for i in range(10):
                        oSetting.oResultParser.SetVar2(uValue=u'',uLocalDestVar=oAction.uLocalDestVar, uGlobalDestVar=oAction.uGlobalDestVar,uDebugMessage= u'NLS Value', uAddName=u"[" + ToUnicode(i) + u"]")
                    return u'NLS',u''
                return u'',u''


            if sResponse[0]==u'U' or sResponse[0]==u'A':
                uTmp=oAction.uGlobalDestVar
                iIndex=int(sResponse[1])

                #this is redundent, but sometimes the Receiver doesn't send a page clear
                if iIndex==0:
                    for i in range(10):
                        oSetting.oResultParser.SetVar2(uValue=u'', uLocalDestVar=oAction.uLocalDestVar, uGlobalDestVar=oAction.uGlobalDestVar, uDebugMessage=u'NLS Value', uAddName=u"[" + ToUnicode(i) + u"]")

                sText=sResponse[3:]
                uText=''
                if sResponse[0]=='A':
                    uText=ToUnicode(sText)
                if sResponse[0]=='U':
                    uText=ToUnicode(sText)
                oSetting.oResultParser.SetVar2(uValue=uText, uLocalDestVar=oAction.uLocalDestVar, uGlobalDestVar=oAction.uGlobalDestVar, uDebugMessage=u'NLS Value', uAddName=u"[" + ToUnicode(iIndex) + u"]")
                if uTmp!=u'':
                    oSetting.uRetVar=uTmp
                self.iCntNLS=iIndex
                self.uRetVar=uTmp
                return u'NLS',uText
        return u"NLS",ToUnicode(sResponse[3:])

    def Handle_NLT(self,oAction,sResponse,oSetting):
        # Handles the NET/USB List Info
        pass
        '''
        
        "xxuycccciiiillsraabbssnnn...nnn" 
        ('Receive:', u'NLT', ':', '1C22000000000001001C00')
        
        xx 1C scheint Amazon Muisc
        
        NET/USB List Title Info
        xx : Service Type
         00 : Music Server (DLNA), 01 : Favorite, 02 : vTuner, 03 : SiriusXM, 04 : Pandora, 05 : Rhapsody, 06 : Last.fm,
         07 : Napster, 08 : Slacker, 09 : Mediafly, 0A : Spotify, 0B : AUPEO!, 0C : radiko, 0D : e-onkyo,
         0E : TuneIn Radio, 0F : MP3tunes, 10 : Simfy, 11:Home Media, 12:Deezer, 13:iHeartRadio, 18:Airplay, 1A:onkyo music,
         1B:TIDAL, F0 : USB/USB(Front) F1 : USB(Rear), F2 : Internet Radio, F3 : NET, FF : None
        u : UI Type
         0 : List, 1 : Menu, 2 : Playback, 3 : Popup, 4 : Keyboard, "5" : Menu List
        y : Layer Info
         0 : NET TOP, 1 : Service Top,DLNA/USB/iPod Top, 2 : under 2nd Layer
        cccc : Current Cursor Position (HEX 4 letters)
        iiii : Number of List Items (HEX 4 letters)
        ll : Number of Layer(HEX 2 letters)
        s : Start Flag
         0 : Not First, 1 : First
        r : Reserved (1 leters, don't care)
        aa : Icon on Left of Title Bar
         00 : Internet Radio, 01 : Server, 02 : USB, 03 : iPod, 04 : DLNA, 05 : WiFi, 06 : Favorite
         10 : Account(Spotify), 11 : Album(Spotify), 12 : Playlist(Spotify), 13 : Playlist-C(Spotify)
         14 : Starred(Spotify), 15 : What's New(Spotify), 16 : Track(Spotify), 17 : Artist(Spotify)
         18 : Play(Spotify), 19 : Search(Spotify), 1A : Folder(Spotify)
         FF : None
        bb : Icon on Right of Title Bar
         00 : Muisc Server (DLNA), 01 : Favorite, 02 : vTuner, 03 : SiriusXM, 04 : Pandora, 05 : Rhapsody, 06 : Last.fm,
         07 : Napster, 08 : Slacker, 09 : Mediafly, 0A : Spotify, 0B : AUPEO!, 0C : radiko, 0D : e-onkyo,
         0E : TuneIn Radio, 0F : MP3tunes, 10 : Simfy, 11:Home Media, 12:Deezer, 13:iHeartRadio, 18:Airplay, 1A:onkyo music,
        1B:TIDAL, F0:USB/USB(Front), F1:USB(Rear),
         FF : None
        ss : Status Info
         00 : None, 01 : Connecting, 02 : Acquiring License, 03 : Buffering
         04 : Cannot Play, 05 : Searching, 06 : Profile update, 07 : Operation disabled
         08 : Server Start-up, 09 : Song rated as Favorite, 0A : Song banned from station,
         0B : Authentication Failed, 0C : Spotify Paused(max 1 device), 0D : Track Not Available, 0E : Cannot Skip
        nnn...nnn : Character of Title Bar (variable-length, 64 Unicode letters [UTF-8 encoded] max)
        
        '''


    def Handle_NJA(self,oAction,uResponse,oSetting):

        hex_chars = map(hex, map(ord, uResponse))

        if len(uResponse)>1:
            if uResponse[1]==u'0' or uResponse[1]==u'-':
                self.uPictureData=uResponse[2:]
                self.uPictureType = u".bmp"
                if uResponse[0]==u'1':
                    self.uPictureType=u'.jpg'
                if uResponse[0]==u'2':
                    self.uPictureType=u'.href'
            if uResponse[0]==u'n':
                #todo: delete old file picture if we get a no picture response
                Logger.debug("Onkyo Receiver has no picture to return")
                return "NJA",""

            if uResponse[1]==u'1':
                self.uPictureData+=uResponse[2:]
                return u"",u""
            if uResponse[1]==u'2' or uResponse[1]==u'-':
                if uResponse[1] == u'2':
                    self.uPictureData=uResponse[2:]

                try:
                    bHex = True

                    if self.uPictureType == u'.href':
                        self.uPictureData,self.uPictureType = self.GetPictureByUrl(self.uPictureData, oSetting)
                        bHex = False

                    if len(self.uPictureData)>0:
                        oFileName = cFileName(Globals.oPathTmp) + oAction.uGlobalDestVar + self.uPictureType

                        f = open(oFileName.string, 'wb')
                        if bHex:
                            f.write( binascii.a2b_hex(self.uPictureData))
                        else:
                            f.write(self.uPictureData)
                        f.close()
                        oSetting.oResultParser.SetVar2(oFileName.string, oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing MediaPicture')
                        SetVar(uVarName = u'NJAPIC', oVarValue = oFileName.string)
                        return u"NJA",oFileName.string
                    else:
                        self.ShowWarning(u'Skipping empty picture:', oSetting.uConfigName)
                        return u'', u''

                except Exception as e:
                    self.ShowError(u'Unexpected error writing file:',oSetting.uConfigName,e)

        return u'',u''

    def GetPictureByUrl(self, uUrl, oSetting):

        uPictureData = u''
        uPictureType = u''

        try:
            oReq = UrlRequest(uUrl)
            oReq.wait()
            uPictureData = oReq.result
            uHeader = oReq.resp_headers.get("content-type")
            if uHeader is None:
                iPos = uPictureData.lower().find("content-type:")
                iPosEnd = uPictureData.find("\n",iPos)
                if iPos>-1 and iPosEnd>-1:
                    uHeader = uPictureData[iPos:iPosEnd]
                    iPos = uPictureData.find("\n\n")
                    if iPos > -1:
                        uPictureData=uPictureData[iPos+2:]
            if uHeader:
                uPictureType = uHeader.split("/")[-1]
            else:
                self.ShowWarning("Invaid URL/Content Type when pulling picture from device:"+str(uHeader),oSetting.uConfigName)
                uPictureType = uUrl.split(".")[-1]

            uPictureType = "."+uPictureType

        except Exception as e:
            self.ShowError(u' Unexpected error reading picture by URL:', oSetting.uConfigName, e)

        return uPictureData,uPictureType

    def Split_IFV(self,oAction,uResponse,oSetting):
        # handles the return of Video Information Request
        uTmp=oAction.uGlobalDestVar
        if not oSetting.uRetVar==u'':
            oAction.uGlobalDestVar=oSetting.uRetVar

        aResponses=uResponse.split(',')
        if len(aResponses)>1:
            oSetting.oResultParser.SetVar2(aResponses[0], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Input Selection', uAddName=u"_video_input_selection")
            oSetting.oResultParser.SetVar2(aResponses[1], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Input Resolution', uAddName=u"_video_input_resolution")
        if len(aResponses)>2:
            oSetting.oResultParser.SetVar2(aResponses[2], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Input Color', uAddName=u"_video_input_color")
        if len(aResponses)>3:
            oSetting.oResultParser.SetVar2(aResponses[3], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Input Bits', uAddName=u"_video_input_bits")
        if len(aResponses)>4:
            oSetting.oResultParser.SetVar2(aResponses[4], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Selection', uAddName=u"_video_output_selection")
        if len(aResponses)>5:
            oSetting.oResultParser.SetVar2(aResponses[5], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Resolution', uAddName=u"_video_output_resolution")
        if len(aResponses)>6:
            oSetting.oResultParser.SetVar2(aResponses[6], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Color', uAddName=u"_video_output_color")
        if len(aResponses)>7:
            oSetting.oResultParser.SetVar2(aResponses[7], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Bits', uAddName=u"_video_output_bits")
        if len(aResponses)>8:
            oSetting.oResultParser.SetVar2(aResponses[8], oAction.uLocalDestVar, oAction.uGlobalDestVar, u'Storing Video Output Effect', uAddName=u"_video_output_bits")

        if uTmp!=u'':
            oSetting.uRetVar=uTmp

    def ISCP_LMD_To_Text(self,uLMD):

        uRet= self.dLMD_Text.get(uLMD)
        if uRet is None:
            uRet=u"unknown"
        return uRet

    def InitLVM(self):
        self.dLMD_Text= {'00': u'STEREO',
                         '01': u'DIRECT',
                         '02': u'SURROUND',
                         '03': u'FILM',
                         '04': u'THX',
                         '05': u'ACTION',
                         '06': u'MUSICAL',
                         '07': u'MONO MOVIE',
                         '08': u'ORCHESTRA',
                         '09': u'UNPLUGGED',
                         '0A': u'STUDIO-MIX',
                         '0B': u'TV LOGIC',
                         '0C': u'ALL CH STEREO',
                         '0D': u'THEATER-DIMENSIONAL',
                         '0E': u'ENHANCED',
                         '0F': u'MONO',
                         '11': u'PURE AUDIO',
                         '12': u'MULTIPLEX',
                         '13': u'FULL MONO',
                         '14': u'DOLBY VIRTUAL',
                         '15': u'DTS Surround Sensation',
                         '16': u'Audyssey DSX',
                         '1F': u'Whole House Mode',
                         '40': u'5.1ch Surround',
                         '41': u'DTS ES',
                         '42': u'THX Cinema',
                         '43': u'THX Surround EX',
                         '44': u'THX Music',
                         '45': u'THX Games',
                         '50': u'THX Cinema',
                         '51': u'THX MusicMode',
                         '52': u'THX Games Mode',
                         '80': u'PLII/PLIIx Movie',
                         '81': u'PLII/PLIIx Music',
                         '82': u'Neo:X Cinema',
                         '83': u'Neo:X Music',
                         '84': u'PLII/PLIIx THX Cinema',
                         '85': u'Neo:X THX Cinema',
                         '86': u'PLII/PLIIx Game',
                         '87': u'Neural Surr',
                         '88': u'Neural THX',
                         '89': u'PLII/PLIIx THX Games',
                         '8A': u'Neo:X THX Games',
                         '8B': u'PLII/PLIIx THX Music',
                         '8C': u'Neo:X THX Music',
                         '8D': u'Neural THX Cinema',
                         '8E': u'Neural THX Music',
                         '8F': u'Neural THX Games',
                         '90': u'PLIIz Height',
                         '91': u'Neo:6 Cinema DTS Surround Sensation',
                         '92': u'Neo:6 Music DTS Surround Sensation',
                         '93': u'Neural Digital Music',
                         '94': u'PLIIz Height + THX Cinema',
                         '95': u'PLIIz Height + THX Music',
                         '96': u'PLIIz Height + THX Games',
                         '97': u'PLIIz Height + THX U2/S2 Cinema',
                         '98': u'PLIIz Height + THX U2/S2 Music',
                         '99': u'PLIIz Height + THX U2/S2 Games',
                         '9A': u'Neo:X Game',
                         'A0': u'PLIIx/PLII Movie + Audyssey DSX',
                         'A1': u'PLIIx/PLII Music + Audyssey DSX',
                         'A2': u'PLIIx/PLII Game + Audyssey DSX',
                         'A3': u'Neo:6 Cinema + Audyssey DSX',
                         'A4': u'Neo:6 Music + Audyssey DSX',
                         'A5': u'Neural Surround + Audyssey DSX',
                         'A6': u'Neural Digital Music + Audyssey DSX',
                         'A7': u'Dolby EX + Audyssey DSX',
                         'FF': u'Auto Surround'}

    def InitDeviceCaps(self):

        self.dDeviceCaps = {    'DHC-40.1' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'DHC-40.2' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2","A3","A4"]},
                                'DHC-60.5' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'DHC-60.7' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'DHC-80.1' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'DHC-80.2' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'DHC-80.3' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'DHC-80.6' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","85","8A","8C","9A"]},
                                'DHC-9.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'DRX-2' :        { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{0:0>+X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","82","83"]},
                                'DRX-3' :        { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{0:0>+X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","82","83"]},
                                'DRX-4' :        { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-30","SWLMAX":"24","CTLFORMAT":"{0:0>+X}","CTLMIN":"-30","CTLMAX":"24","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'DRX-5' :        { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-30","SWLMAX":"24","CTLFORMAT":"{0:0>+X}","CTLMIN":"-30","CTLMAX":"24","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'DTC-7' :        { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0E","0F","80","81","82","83"]},
                                'DTC-9.4' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0E","0F","80","81","82","83"]},
                                'DTC-9.8' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'DTR-10.5' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0E","0F","11","12","13","14","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'DTR-20.1' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","41","80","81","82","83","86"]},
                                'DTR-20.2' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C"]},
                                'DTR-20.3' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C"]},
                                'DTR-20.4' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","41","80","81","82","83","86","90"]},
                                'DTR-20.7' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","80","82","83"]},
                                'DTR-30.1' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","41","80","81","82","83","86","90"]},
                                'DTR-30.2' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2","A3","A4"]},
                                'DTR-30.3' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'DTR-30.4' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'DTR-30.5' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","41","80","81","82","83","86","90"]},
                                'DTR-30.6' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","41","80","81","82","83","86","90"]},
                                'DTR-30.7' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","80","82","83"]},
                                'DTR-4.5' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0E","0F","13","40","80","81","86"]},
                                'DTR-4.6' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'DTR-4.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0F","13","40","41","80","81","82","83","86"]},
                                'DTR-40.1' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'DTR-40.2' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2","A3","A4"]},
                                'DTR-40.3' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'DTR-40.4' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'DTR-40.5' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'DTR-40.6' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96"]},
                                'DTR-40.7' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'DTR-5.2' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","08","09","0A","0B","0C"]},
                                'DTR-5.3' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","08","09","0A","0B","0C"]},
                                'DTR-5.5' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0E","0F","11","13","40","41","80","81","82","83","86"]},
                                'DTR-5.6' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'DTR-5.8' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0F","13","40","41","80","81","82","83","86","87"]},
                                'DTR-5.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0F","13","40","41","80","81","82","83","86"]},
                                'DTR-50.1' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'DTR-50.2' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2","A3","A4"]},
                                'DTR-50.3' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'DTR-50.4' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'DTR-50.5' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'DTR-50.6' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96"]},
                                'DTR-50.7' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'DTR-6.2' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","08","09","0A","0B","0C"]},
                                'DTR-6.3' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","08","09","0A","0B","0C","11"]},
                                'DTR-6.4' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F","11","80","81","82","83","84","85"]},
                                'DTR-6.5' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F","11","13","40","41","42","43","80","81","82","83","84","85","86"]},
                                'DTR-6.6' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'DTR-6.8' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'DTR-6.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C"]},
                                'DTR-60.5' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'DTR-60.6' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","85","8A","8C","9A"]},
                                'DTR-60.7' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'DTR-7.1' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","07","08","09","0A","0B","0C","0D","0E","0F"]},
                                'DTR-7.2' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F"]},
                                'DTR-7.3' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0E","0F","80","81","82","83"]},
                                'DTR-7.4' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F","11","80","81","82","83","84","85"]},
                                'DTR-7.6' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'DTR-7.7' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0F","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'DTR-7.8' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'DTR-7.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C"]},
                                'DTR-70.1' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'DTR-70.2' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'DTR-70.3' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'DTR-70.4' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'DTR-70.6' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","85","8A","8C","9A"]},
                                'DTR-8.2' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F"]},
                                'DTR-8.3' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0E","0F","80","81","82","83"]},
                                'DTR-8.4' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F","11","80","81","82","83","84","85"]},
                                'DTR-8.8' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'DTR-8.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'DTR-80.1' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'DTR-80.2' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'DTR-80.3' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'DTR-9.1' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","07","08","09","0A","0B","0C","0D","0E","0F"]},
                                'DTR-9.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'DTX-5.8' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0F","13","40","41","80","81","82","83","86","87"]},
                                'DTX-5.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0F","13","40","41","80","81","82","83","86"]},
                                'DTX-7' :        { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F","11","80","81","82","83","84","85"]},
                                'DTX-7.7' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0F","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'DTX-7.8' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'DTX-8.8' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'DTX-8.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'DTX-9.9' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'ETX-NA1000' :   { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0E","0F","11","12","13","14","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'HT-R693' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","41","80","81","82","83","86","90"]},
                                'HT-R993' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","85","8A","8C"]},
                                'HT-RC550' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","81","82","83","86"]},
                                'HT-RC560' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","41","80","81","82","83","86","90"]},
                                'HT-RC660' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","41","80","81","82","83","86","90"]},
                                'NR-365' :       { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","80","81","82","83","86"]},
                                'PR-SC5507' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","15","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","91","92","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'PR-SC5508' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'PR-SC5509' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'PR-SC5530' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","85","8A","8C","9A"]},
                                'PR-SC885' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'PR-SC886' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'RDC-7' :        { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","07","08","09","0A","0B","0C","0D","0E","0F"]},
                                'RDC-7.1' :      { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0E","0F","11","12","13","14","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'TX-DS787' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","07","08","09","0A","0B","0C","0D","0E","0F"]},
                                'TX-DS797' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F"]},
                                'TX-DS898' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F"]},
                                'TX-DS989' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","07","08","09","0A","0B","0C","0D","0E","0F"]},
                                'TX-NA900' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F","11"]},
                                'TX-NA905' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'TX-NA906' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'TX-NA906X' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'TX-NR1000' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0E","0F","11","12","13","14","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'TX-NR1007' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","15","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","91","92","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'TX-NR1008' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'TX-NR1009' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'TX-NR1010' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'TX-NR1030' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","85","8A","8C","9A"]},
                                'TX-NR3007' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","15","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","91","92","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'TX-NR3008' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'TX-NR3009' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'TX-NR3010' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'TX-NR3030' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","85","8A","8C","9A"]},
                                'TX-NR414' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","81","82","83","86"]},
                                'TX-NR5000' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0E","0F","11","12","13","14","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'TX-NR5007' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","15","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","91","92","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'TX-NR5008' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F","90","93","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'TX-NR5009' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'TX-NR5010' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'TX-NR509' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","41","80","81","82","83","86"]},
                                'TX-NR515' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","41","80","81","82","83","86","90"]},
                                'TX-NR515AE' :   { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","41","80","81","82","83","86","90"]},
                                'TX-NR525' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","81","82","83","86"]},
                                'TX-NR535' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","81","82","83","86"]},
                                'TX-NR545' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","82","83"]},
                                'TX-NR555' :     { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{0:0>+X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","82","83"]},
                                'TX-NR579' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","41","80","81","82","83","86","90"]},
                                'TX-NR609' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'TX-NR616' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'TX-NR616AE' :   { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'TX-NR626' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","41","80","81","82","83","86","90"]},
                                'TX-NR636' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","41","80","81","82","83","86","90"]},
                                'TX-NR646' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","80","82","83"]},
                                'TX-NR656' :     { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{0:0>+X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","82","83"]},
                                'TX-NR676E' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","82","83"]},
                                'TX-NR708' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2","A3","A4"]},
                                'TX-NR709' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'TX-NR717' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'TX-NR727' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'TX-NR737' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96"]},
                                'TX-NR747' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'TX-NR757' :     { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-30","SWLMAX":"24","CTLFORMAT":"{0:0>+X}","CTLMIN":"-30","CTLMAX":"24","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'TX-NR807' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","15","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","91","92","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'TX-NR808' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2","A3","A4"]},
                                'TX-NR809' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'TX-NR818' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'TX-NR818AE' :   { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'TX-NR828' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","A0","A1","A2"]},
                                'TX-NR838' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96"]},
                                'TX-NR900' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","07","08","09","0A","0B","0C","0D","0E","0F","80","81","82","83"]},
                                'TX-NR901' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F","11","80","81","82","83","84","85"]},
                                'TX-NR905' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'TX-NR906' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'TX-NR929' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","16","1F","23","25","26","2E","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","94","95","96","97","98","99","9A","A0","A1","A2","A7"]},
                                'TX-RZ610' :     { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{0:0>+X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","80","82","83"]},
                                'TX-RZ710' :     { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-30","SWLMAX":"24","CTLFORMAT":"{0:0>+X}","CTLMIN":"-30","CTLMAX":"24","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","13","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'TX-RZ800' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'TX-RZ810' :     { "SWLFORMAT":"{0:0>+X}","SWLMIN":"-30","SWLMAX":"24","CTLFORMAT":"{0:0>+X}","CTLMIN":"-30","CTLMAX":"24","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","1F","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'TX-RZ900' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","1F","23","25","26","2E","40","42","43","44","45","50","51","52","80","82","83","84","85","89","8A","8B","8C"]},
                                'TX-SA706' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C"]},
                                'TX-SA706X' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C"]},
                                'TX-SA805' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'TX-SA806' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C"]},
                                'TX-SA806X' :    { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'TX-SA875' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'TX-SA876' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]},
                                'TX-SR702' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0E","0F","11","13","40","41","42","43","80","81","82","83","84","85","86"]},
                                'TX-SR703' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'TX-SR705' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'TX-SR706' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C"]},
                                'TX-SR707' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","03","04","05","06","08","09","0A","0B","0C","0D","0E","0F","11","13","15","16","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C","90","91","92","94","95","96","97","98","99","A0","A1","A2","A3","A4","A7"]},
                                'TX-SR803' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'TX-SR804' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86"]},
                                'TX-SR805' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'TX-SR806' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","89","8A","8B","8C"]},
                                'TX-SR875' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","50","51","52","80","81","82","83","84","85","86","88","89","8A"]},
                                'TX-SR876' :     { "SWLFORMAT":"{:+03X}","SWLMIN":"-15","SWLMAX":"12","CTLFORMAT":"{:+03X}","CTLMIN":"-15","CTLMAX":"12","ListeningModes": ["00","01","02","04","07","08","09","0A","0B","0C","0D","0F","11","13","40","41","42","43","44","45","50","51","52","80","81","82","83","84","85","86","88","89","8A","8B","8C","8D","8E","8F"]}
                            }




    def GenerateXMLFile(self):
        pass
        '''
        from collections import OrderedDict


                for sCommands in COMMANDS:
            # print sCommands

            print "  <!--\n      Section:",sCommands+ "\n  -->"
            for sSubCommand in COMMANDS[sCommands]:
                # print sSubCommand
                # print COMMANDS[sCommands][sSubCommand]
                oItems=COMMANDS[sCommands][sSubCommand]
                print "  <!--\n      Category:"+oItems['description']+ "\n  -->"
                #for oItem in oItems:
                if True:
                    for sValue in oItems['values']:
                        oValue=oItems['values'][sValue]

                        if not oValue['name']==None:
                            if type(oValue['name']).__name__=="str":
                                sName=oValue['name']
                            else:
                                sName=oValue['name'][0]
                        else:
                            sName="!!!!!!!!!!!!!!!!!value!!!!!!!!!!!!!!!!"

                        if not type(sValue).__name__=="str":
                            sValue="Varrange from "+ str(sValue[0])+" to "+str(sValue[1])

                        sDescription=oValue['description']
                        if type(sDescription).__name__=="unicode":
                            sDescription=sDescription.encode("utf-8","replace")

                        print "  <action string="codeset" name=\""+sCommands+"."+COMMANDS[sCommands][sSubCommand]['name']+"."+sName+"\" desc=\""+sDescription +  "\"  cmd=\""+sSubCommand+sValue+"\" />"
            '''

'''
<?xml version="1.0" encoding="utf-8"?>
<response status="ok">
	<device id="TX-NR676E">
		<brand>ONKYO</brand>
		<category>AV Receiver</category>
		<year>2017</year>
		<model>TX-NR676E</model>
		<destination>xx</destination>
		<macaddress>0009B0E74DA8</macaddress>
		<modeliconurl>http://192.168.1.195/icon/OAVR_120.jpg</modeliconurl>
		<friendlyname></friendlyname>
		<firmwareversion>1040-4010-1020-0008-0000</firmwareversion>
		<ecosystemversion>100</ecosystemversion>
		<netservicelist count="12">
			<netservice id="0e" value="1" name="TuneIn Radio" account="Username" password="Password" zone="07" enable="07" />
			<netservice id="04" value="1" name="Pandora" account="Email" password="Password" zone="07" enable="07" />
			<netservice id="0a" value="1" name="Spotify" zone="07" enable="07" />
			<netservice id="12" value="1" name="Deezer" account="Email address" password="Password" zone="07" enable="07" />
			<netservice id="18" value="1" name="AirPlay" zone="07" enable="07" />
			<netservice id="1b" value="1" name="TIDAL" account="Username" password="Password" zone="07" enable="07" />
			<netservice id="00" value="1" name="Music Server" zone="07" enable="07" addqueue="1" sort="1" />
			<netservice id="f0" value="1" name="USB" zone="07" enable="07" addqueue="1" />
			<netservice id="41" value="1" name="FireConnect" zone="07" enable="07" />
			<netservice id="40" value="1" name="Chromecast built-in" zone="07" enable="01" />
			<netservice id="1d" value="1" name="Play Queue" zone="07" enable="07" />
			<netservice id="42" value="1" name="DTS Play-Fi" zone="07" enable="01" />
		</netservicelist>
		<zonelist count="4">
			<zone id="1" value="1" name="Main" volmax="82" volstep="1" src="1" dst="0" lrselect="0" />
			<zone id="2" value="1" name="Zone2" volmax="0" volstep="1" src="0" dst="0" lrselect="0" />
			<zone id="3" value="0" name="Zone3" volmax="0" volstep="0" src="0" dst="0" lrselect="0" />
			<zone id="4" value="0" name="Zone4" volmax="0" volstep="0" src="0" dst="0" lrselect="0" />
		</zonelist>
		<selectorlist count="14">
			<selector id="10" value="1" name="BD/DVD" zone="03" iconid="10" />
			<selector id="01" value="1" name="CBL/SAT" zone="03" iconid="01" />
			<selector id="02" value="1" name="GAME" zone="03" iconid="02" />
			<selector id="11" value="1" name="STRM BOX" zone="03" iconid="11" />
			<selector id="05" value="1" name="PC" zone="01" iconid="05" />
			<selector id="03" value="1" name="AUX" zone="03" iconid="03" />
			<selector id="25" value="1" name="AM" zone="03" iconid="25" />
			<selector id="24" value="1" name="FM" zone="03" iconid="24" />
			<selector id="23" value="1" name="CD" zone="03" iconid="47" />
			<selector id="12" value="1" name="TV" zone="03" iconid="12" />
			<selector id="22" value="1" name="PHONO" zone="03" iconid="22" />
			<selector id="2b" value="1" name="NET" zone="03" iconid="2b" />
			<selector id="2e" value="1" name="BLUETOOTH" zone="03" iconid="2e" />
			<selector id="80" value="1" name="Source" zone="02" />
		</selectorlist>
		<presetlist count="40">
			<preset id="01" band="0" freq="0" name="" />
			<preset id="02" band="0" freq="0" name="" />
			.......
			<preset id="1f" band="0" freq="0" name="" />
			<preset id="20" band="0" freq="0" name="" />
			<preset id="21" band="0" freq="0" name="" />
			<preset id="22" band="0" freq="0" name="" />
			<preset id="23" band="0" freq="0" name="" />
			<preset id="24" band="0" freq="0" name="" />
			<preset id="25" band="0" freq="0" name="" />
			<preset id="26" band="0" freq="0" name="" />
			<preset id="27" band="0" freq="0" name="" />
			<preset id="28" band="0" freq="0" name="" />
		</presetlist>
		<controllist count="61">
			<control id="Bass" value="1" zone="1" min="-10" max="10" step="1" />
			<control id="Treble" value="1" zone="1" min="-10" max="10" step="1" />
			<control id="Center Level" value="1" zone="1" min="-12" max="12" step="1" />
			<control id="Subwoofer Level" value="1" zone="1" min="-15" max="12" step="1" />
			<control id="Subwoofer1 Level" value="0" zone="1" min="-15" max="12" step="1" />
			<control id="Subwoofer2 Level" value="0" zone="1" min="-15" max="12" step="1" />
			<control id="Phase Matching Bass" value="0" />
			<control id="LMD Movie/TV" value="1" code="MOVIE" position="1" />
			<control id="LMD Music" value="1" code="MUSIC" position="2" />
			<control id="LMD Game" value="1" code="GAME" position="3" />
			<control id="LMD THX" value="0" code="04" position="4" />
			<control id="LMD Stereo" value="1" code="00" position="4" />
			<control id="LMD Direct" value="0" code="01" position="1" />
			<control id="LMD Pure Audio" value="0" code="11" position="2" />
			<control id="LMD Pure Direct" value="0" code="11" position="1" />
			<control id="LMD Auto/Direct" value="0" code="AUTO" position="2" />
			<control id="LMD Stereo G" value="0" code="STEREO" position="3" />
			<control id="LMD Surround" value="0" code="SURR" position="4" />
			<control id="TUNER Control" value="1" />
			<control id="TUNER Freq Control" value="0" />
			<control id="Info" value="1" />
			<control id="Cursor" value="1" />
			<control id="Home" value="0" code="HOME" position="2" />
			<control id="Setup" value="1" code="MENU" position="2" />
			<control id="Quick" value="1" code="QUICK" position="1" />
			<control id="Menu" value="0" code="MENU" position="1" />
			<control id="AMP Control(RI)" value="0" />
			<control id="CD Control(RI)" value="0" />
			<control id="CD Control" value="0" />
			<control id="BD Control(CEC)" value="1" />
			<control id="TV Control(CEC)" value="1" />
			<control id="NoPowerButton" value="0" />
			<control id="DownSample" value="0" />
			<control id="Dimmer" value="1" />
			<control id="time_hhmmss" value="1" />
			<control id="Zone2 Control(CEC)" value="0" />
			<control id="Sub Control(CEC)" value="0" />
			<control id="NoNetworkStandby" value="0" />
			<control id="NJAREQ" value="1" />
			<control id="Music Optimizer" value="1" />
			<control id="NoVideoInfo" value="0" />
			<control id="NoAudioInfo" value="0" />
			<control id="AV Adjust" value="0" />
			<control id="Audio Scalar" value="0" />
			<control id="Hi-Bit" value="0" />
			<control id="Upsampling" value="0" />
			<control id="Digital Filter" value="0" />
			<control id="DolbyAtmos" value="1" />
			<control id="DTS:X" value="1" />
			<control id="MCACC" value="0" />
			<control id="Dialog Enhance" value="0" />
			<control id="PQLS" value="0" />
			<control id="CD Control(NewRemote)" value="0" />
			<control id="NoVolume" value="0" />
			<control id="Auto Sound Retriever" value="0" />
			<control id="Lock Range Adjust" value="0" />
			<control id="P.BASS" value="0" />
			<control id="Tone Direct" value="0" />
			<control id="DetailedFileInfo" value="0" />
			<control id="NoDABPresetFunc" value="0" />
			<control id="S.BASS" value="0" />
		</controllist>
		<functionlist count="10">
			<function id="UsbUpdate" value="0" />
			<function id="NetUpdate" value="1" />
			<function id="WebSetup" value="1" />
			<function id="WifiSetup" value="1" />
			<function id="Nettune" value="0" />
			<function id="Initialize" value="0" />
			<function id="Battery" value="0" />
			<function id="AutoStandbySetting" value="0" />
			<function id="e-onkyo" value="0" />
			<function id="UsbDabDongle" value="1" />
		</functionlist>
		<tuners count="2">
			<tuner band="FM" min="87500" max="108000" step="50" />
			<tuner band="AM" min="522" max="1611" step="9" />
		</tuners>
	</device>
</response>

<?xml version="1.0" encoding="utf-8"?>
<response status="ok">
    <device id="HT-RC660">
        <brand>ONKYO</brand>
        <category>AV Receiver</category>
        <year>2014</year>
        <model>HT-RC660</model>
        <destination>xx</destination>
        <firmwareversion>2020-9110-200?-????-????</firmwareversion>
        <netservicelist count="16">
            <netservice id="0e" value="1" name="TuneIn" account="Username" password="Password" />
            <netservice id="04" value="1" name="Pandora" account="Email" password="Password" />
            <netservice id="05" value="0" name="Rhapsody" account="Username" password="Password" />
            <netservice id="03" value="0" name="SiriusXM Internet Radio" account="User Name" password="Password" />
            <netservice id="06" value="0" name="Last.fm Internet Radio" account="User Name" password="Password" />
            <netservice id="08" value="0" name="Slacker Personal Radio" account="Email" password="Password" />
            <netservice id="0a" value="1" name="Spotify" account="Username" password="Password" />
            <netservice id="0b" value="1" name="AUPEO! PERSONAL RADIO" account="User Name" password="Password" />
            <netservice id="0d" value="0" name="e-onkyo music" />
            <netservice id="0c" value="0" name="radiko.jp" />
            <netservice id="10" value="0" name="simfy" account="Username or email address." password="Password" />
            <netservice id="0f" value="0" name="MP3tunes" account="Email" password="Password" />
            <netservice id="12" value="1" name="Deezer" account="E-Mail-Adresse" password="Passwort" />
            <netservice id="01" value="1" name="My Favorites" />
            <netservice id="00" value="1" name="DLNA" />
            <netservice id="11" value="1" name="Home Media" account="User Name" password="Password" />
        </netservicelist>
        <zonelist count="4">
            <zone id="1" value="1" name="Main" volmax="80" volstep="1" />
            <zone id="2" value="1" name="Zone2" volmax="80" volstep="1" />
            <zone id="3" value="0" name="Zone3" volmax="0" volstep="1" />
            <zone id="4" value="0" name="Zone4" volmax="0" volstep="1" />
        </zonelist>
        <selectorlist count="26">
            <selector id="10" value="1" name="BD/DVD    " zone="03" iconid="10" />
            <selector id="01" value="1" name="CBL/SAT   " zone="03" iconid="01" />
            <selector id="00" value="1" name="STB/DVR   " zone="03" iconid="00" />
            <selector id="02" value="1" name="GAME      " zone="03" iconid="02" />
            <selector id="02" value="0" name="" zone="00" iconid="02" />
            <selector id="04" value="0" name="" zone="00" iconid="04" />
            <selector id="05" value="1" name="PC        " zone="03" iconid="05" />
            <selector id="03" value="1" name="AUX       " zone="01" iconid="03" />
            <selector id="26" value="0" name="" zone="00" iconid="26" />
            <selector id="25" value="1" name="AM" zone="03" iconid="25" />
            <selector id="24" value="1" name="FM" zone="03" iconid="24" />
            <selector id="23" value="1" name="TV/CD     " zone="03" iconid="23" />
            <selector id="22" value="1" name="PHONO     " zone="03" iconid="22" />
            <selector id="2b" value="1" name="NET" zone="03" iconid="2b" />
            <selector id="29" value="1" name="USB" zone="03" iconid="29" />
            <selector id="29" value="0" name="" zone="00" iconid="29" />
            <selector id="2a" value="0" name="" zone="00" iconid="2a" />
            <selector id="2c" value="0" name="" zone="00" iconid="2c" />
            <selector id="2e" value="1" name="BLUETOOTH" zone="03" iconid="2e" />
            <selector id="07" value="0" name="" zone="00" iconid="10" />
            <selector id="08" value="0" name="" zone="00" iconid="01" />
            <selector id="09" value="0" name="" zone="00" iconid="00" />
            <selector id="80" value="1" name="Source" zone="02" />
            <selector id="44" value="0" name="" zone="00" iconid="44" />
            <selector id="45" value="0" name="" zone="00" iconid="45" />
            <selector id="41" value="0" name="" zone="00" iconid="41" />
        </selectorlist>
        <presetlist count="40">
            <preset id="01" band="0" freq="0" name="" />
            <preset id="02" band="0" freq="0" name="" />
            <preset id="03" band="0" freq="0" name="" />
            <preset id="04" band="0" freq="0" name="" />
            <preset id="05" band="0" freq="0" name="" />
            <preset id="06" band="0" freq="0" name="" />
            <preset id="07" band="0" freq="0" name="" />
            <preset id="08" band="0" freq="0" name="" />
            <preset id="09" band="0" freq="0" name="" />
            <preset id="0a" band="0" freq="0" name="" />
            <preset id="0b" band="0" freq="0" name="" />
            .....
            <preset id="26" band="0" freq="0" name="" />
            <preset id="27" band="0" freq="0" name="" />
            <preset id="28" band="0" freq="0" name="" />
        </presetlist>
        <controllist count="32">
            <control id="Bass" value="1" zone="1" min="-10" max="10" step="2" />
            <control id="Treble" value="1" zone="1" min="-10" max="10" step="2" />
            <control id="Center Level" value="1" zone="1" min="-12" max="12" step="1" />
            <control id="Subwoofer Level" value="1" zone="1" min="-15" max="12" step="1" />
            <control id="Subwoofer1 Level" value="0" zone="1" min="-15" max="12" step="1" />
            <control id="Subwoofer2 Level" value="0" zone="1" min="-15" max="12" step="1" />
            <control id="Phase Matching Bass" value="1" />
            <control id="LMD Movie/TV" value="1" code="MOVIE" position="1" />
            <control id="LMD Music" value="1" code="MUSIC" position="2" />
            <control id="LMD Game" value="1" code="GAME" position="3" />
            <control id="LMD THX" value="0" code="04" position="4" />
            <control id="LMD Stereo" value="1" code="00" position="4" />
            <control id="LMD Direct" value="0" code="01" position="1" />
            <control id="LMD Pure Audio" value="0" code="11" position="2" />
            <control id="TUNER Control" value="1" />
            <control id="TUNER Freq Control" value="0" />
            <control id="Info" value="1" />
            <control id="NoVideoInfo" value="0" />
            <control id="NoAudioInfo" value="0" />
            <control id="Cursor" value="1" />
            <control id="Home" value="1" code="HOME" position="2" />
            <control id="Quick" value="1" code="QUICK" position="1" />
            <control id="Menu" value="0" code="MENU" position="1" />
            <control id="AMP Control(RI)" value="0" />
            <control id="CD Control(RI)" value="0" />
            <control id="CD Control" value="0" />
            <control id="BD Control(CEC)" value="1" />
            <control id="TV Control(CEC)" value="1" />
            <control id="NoPowerButton" value="0" />
            <control id="DownSample" value="0" />
            <control id="Dimmer" value="0" />
            <control id="time_hhmmss" value="1" />
        </controllist>
        <functionlist count="6">
            <function id="UsbUpdate" value="0" />
            <function id="NetUpdate" value="0" />
            <function id="WebSetup" value="1" />
            <function id="WifiSetup" value="1" />
            <function id="Nettune" value="0" />
            <function id="Initialize" value="0" />
        </functionlist>
    </device>
</response>'


'''
