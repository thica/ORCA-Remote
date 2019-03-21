# -*- coding: utf-8 -*-
# elv_max

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

'''

 This code uses the (adjusted) maxcube module

 https://github.com/hackercowboy/python-maxcube-api
'''


import sys
from kivy.clock             import Clock
from kivy.logger            import Logger

from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.Path        import cPath
from ORCA.utils.Sleep       import fSleep
from ORCA.vars.QueryDict    import QueryDict
from ORCA.utils.TypeConvert import ToInt
from ORCA.utils.TypeConvert import ToFloat
from ORCA.utils.TypeConvert import ToDic
from ORCA.utils.TypeConvert import ToList
from ORCA.vars.Actions      import Var_DelArray
import ORCA.Globals as Globals

sys.path.append((cPath(Globals.oPathInterface + "/elv_max")).string)

from maxcube.cube import MaxCube
from maxcube.connection import MaxCubeConnection

'''
<root>
  <repositorymanager>
    <entry>
      <name>ELV MAX</name>
      <description language='English'>Interface control ELV MAX</description>
      <description language='German'>Interface um ALV MAX Geräte zu steuern</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/elv_max</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/elv_max.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>ELV MAX Discover</name>
        </dependency>
      </dependencies>
      <skipfiles>
        <file>elv_max/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):

        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.aInterFaceIniSettings.uHost                       = u"discover"
            self.aInterFaceIniSettings.uPort                       = u"62910"
            self.aInterFaceIniSettings.uFNCodeset                  = u"CODESET_elv_max_DEFAULT.xml"
            self.aInterFaceIniSettings.uParseResultOption          = u'dict'
            self.aInterFaceIniSettings.iTimeToClose                = -1
            self.aInterFaceIniSettings.uDiscoverScriptName         = u"discover_elvmax"
            self.aInterFaceIniSettings.uDISCOVER_ELVMAX_serialnumber = ""
            self.oDevice                                           = None
            self.dDevices                                          = {}

        def Disconnect(self):
            if not self.bIsConnected:
                return cBaseInterFaceSettings.Disconnect(self)
            try:
                if self.oDevice is not None:
                    self.oDevice.connection.disconnect()
                return cBaseInterFaceSettings.Disconnect(self)
            except Exception as e:
                self.ShowError(u'Cannot diconnect:'+self.aInterFaceIniSettings.uHost+':'+self.aInterFaceIniSettings.uPort,e)
                return cBaseInterFaceSettings.Disconnect(self)

        def Connect(self):

            if not cBaseInterFaceSettings.Connect(self):
                return False

            if self.aInterFaceIniSettings.uHost=='':
                return False

            try:
                if self.oDevice is None:
                    # self.oDevice = Cube(address=self.aInterFaceIniSettings.uHost, port=ToInt(self.aInterFaceIniSettings.uPort))
                    self.oDevice = MaxCube(MaxCubeConnection(host=self.aInterFaceIniSettings.uHost, port=ToInt(self.aInterFaceIniSettings.uPort)))

                # self.oDevice.connect()
                self.oInterFace.oInterFaceConfig.WriteDefinitionConfigPar(uSectionName = self.uSection, uVarName= u'OldDiscoveredIP', uVarValue = self.aInterFaceIniSettings.uHost)
                self.bIsConnected=True
                return self.bIsConnected
            except Exception as e:
                if hasattr(e,"errno"):
                    if e.errno==10051:
                        self.bOnError=True
                        self.ShowWarning(u'Cannot connect (No Network):'+self.aInterFaceIniSettings.uHost+':'+self.aInterFaceIniSettings.uPort)
                        return False
                self.ShowError(u'Cannot connect:'+self.aInterFaceIniSettings.uHost+':'+self.aInterFaceIniSettings.uPort,e)
                self.bOnError=True
                return False

    def __init__(self):
        cBaseInterFace.__init__(self)
        self.aSettings                  = {}
        self.oSetting                   = None
        self.aDiscoverScriptsBlackList  = ["iTach (Global Cache)","Keene Kira","UPNP","Enigma","EISCP (Onkyo)"]
        self.dInterfaceFunctions        = {}
        self.RegisterInterfaceActions()


    def Init(self,uInterFaceName,uInterFaceFile=u''):
        cBaseInterFace.Init(self,uInterFaceName,uInterFaceFile)
        self.oInterFaceConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oInterFaceConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oInterFaceConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oInterFaceConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self, **kwargs):
        cBaseInterFace.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        iTryCount=0
        iRet=1

        uRetVar = ReplaceVars(uRetVar)
        oSetting.uRetVar=uRetVar

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        dCmd     = ToDic(oAction.uCmd)
        uCmd     = dCmd["method"]
        dParams  = dCmd["params"]

        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                try:
                    self.ShowDebug("Sending elv max command: %s" % uCmd)
                    oFunc = self.dInterfaceFunctions.get(uCmd)
                    aResult = []
                    if oFunc is not None:
                        aResult = oFunc(oSetting=oSetting,oAction=oAction, dParams=dParams)
                    else:
                        self.ShowError("Function not implemented: %s" % uCmd)


                    for dLine in aResult:

                        uGlobalDestVarSave      = oAction.uGlobalDestVar
                        uLocalDestVarSave       = oAction.uLocalDestVar

                        if oAction.uGetVar.startswith('ORCAMULTI'):
                            aTmpGlobalDestVar  = ToList(oAction.uGlobalDestVar)
                            aTmpLocalDestVar = ToList(oAction.uLocalDestVar)
                            oAction.uGlobalDestVar = "".join('"'+e+dLine.uVarSuffix+'",' for e in aTmpGlobalDestVar)[:-1]
                            oAction.uLocalDestVar = "".join('"'+e+dLine.uVarSuffix+'",'  for e in aTmpLocalDestVar)[:-1]
                        else:
                            oAction.uGlobalDestVar  = oAction.uGlobalDestVar + dLine.uVarSuffix
                            oAction.uLocalDestVar   = oAction.uLocalDestVar + dLine.uVarSuffix

                        uCmd, uRetVal           = self.ParseResult(oAction, dLine.dValue, oSetting)
                        oAction.uGlobalDestVar  = uGlobalDestVarSave
                        oAction.uLocalDestVar   = uLocalDestVarSave

                    break
                except Exception as e:
                    self.ShowError(u'can\'t Send Message',oSetting.uConfigName,e)
                    iRet=1
            else:
                oSetting.bIsConnected=False

        self.iLastRet=iRet

        if not bNoLogOut:
            if oSetting.aInterFaceIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aInterFaceIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aInterFaceIniSettings.iTimeToClose)
        return iRet

    def RegisterInterfaceActions(self):
        """
        Register all actions managed by the interface
        """

        aFuncs=dir(self)
        for uFuncName in aFuncs:
            if uFuncName.startswith('ELV_'):
                uName = uFuncName[4:]
                self.dInterfaceFunctions[uName] = getattr(self, uFuncName)

    def _GetRFAddress(self,oSetting,uRoom):
        """
        Finds the rf_address for a room

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param string uRoom: the room name
        :return: The rf_address, or None if not found
        :rtype: collections.namedtuple
        """

        for oRoom in oSetting.oDevice.rooms:
            if oRoom.name == uRoom:
                return oRoom.rf_address
        oSetting.ShowError("Wrong Room Name given:"+uRoom)
        return None


    def _GetRoomForRfAddress(self, uRfAddress,oSetting):
        """
        Internal Helper function to find the Room for a RF Address

        :param string uRfAddress: The RF Address to look for
        :param cInterface.cInterFaceSettings oSetting: The setting object
        :return: The room object or None if not found
        :rtype: collections.namedtuple
        """
        for oRoom in oSetting.oDevice.rooms:
            if str(oRoom.rf_address)==uRfAddress:
                return oRoom
            for oDevice in oSetting.oDevice.devices_by_room(oRoom):
                if str(oDevice.rf_address)==uRfAddress:
                    return oRoom
        return None


    def _CreateSimpleResult(self,uResult):
        """
        Helper Function to create a simple one line result

        :param uResult:
        :return: a dict key:result=Result
        :rtype: QueryDict
        """
        aRet                    = []
        dLine                   = QueryDict()
        dLine.uVarSuffix        = ""
        dLine.dValue            = {"result": uResult}
        aRet.append(dLine)
        return aRet


    def _ELV_getroomdevices(self,oSetting,oAction, dParams, bAddRoom): #check
        """
        Internal Helper function to get a list of devices of a room

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :param boolean bAddRoom: Flag to include the room name as first element
        :return: list: A list of dicts: key:name=room name , rf_address= Rf Address of Room
        :rtype: list
        """

        aRet        = []
        i           = 0
        uRoom       = ReplaceVars(dParams["room"],self.uInterFaceName+u'/'+oSetting.uConfigName)

        aTmpDestVar = ToList(oAction.uGlobalDestVar)
        for uVarName in aTmpDestVar:
            Var_DelArray(uVarName=uVarName+u'[]')

        for oRoom in oSetting.oDevice.rooms:
            if oRoom.name == uRoom:
                if bAddRoom:
                    dLine                       = QueryDict()
                    dLine.uVarSuffix            = "[" + str(i) + "]"
                    dLine.dValue                = {}
                    uRfAddress                  = str(oRoom.rf_address)
                    dLine.dValue                = {"name": oRoom.name, "rf_address": uRfAddress}
                    aRet.append(dLine)
                    i = i + 1

                for oDevice in oSetting.oDevice.devices_by_room(oRoom):
                    dLine                       = QueryDict()
                    dLine.uVarSuffix            = "[" + str(i) + "]"
                    uRfAddress                  = str(oDevice.rf_address)
                    dLine.dValue                = {}
                    dLine.dValue["name"]        = oDevice.name
                    dLine.dValue["rf_address"]  = str(uRfAddress)
                    aRet.append(dLine)
                    i = i + 1
                break
        return aRet

    def _ELV_set_mode(self,oSetting,oAction, dParams, bMode):
        """
        Internal Helper function to sets the mode of a room or device , depends on what is given in dParams

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, see calling function for valid options
        :param byte bMode: the mode
        :return: dict: key:result=Error or maxcube result
        :rtype: QueryDict
        """

        uRet   = "Error"
        kwArgs = {}

        try:
            uRF_Address = dParams.get("rf_address")
            if uRF_Address:
                uRF_Address = ReplaceVars(uRF_Address, self.uInterFaceName + u'/' + oSetting.uConfigName)

            uRoom = dParams.get("room")
            if uRoom:
                uRoom = ReplaceVars(uRoom, self.uInterFaceName + u'/' + oSetting.uConfigName)

            if uRoom is None and uRF_Address is None:
                self.ShowError("set_mode:Invalid Parameter, not a room or rf_address given")
                return uRet

            if uRF_Address is None:
                oRF_Address = self._GetRFAddress(oSetting,uRoom)
                oRoom       = self._GetRoomForRfAddress(str(oRF_Address), oSetting)

            if uRoom is None:
                oRoom = self._GetRoomForRfAddress(uRF_Address, oSetting)


            uTemperature= dParams.get("temperature")
            if uTemperature is not None:
                fTemperature = ToFloat(ReplaceVars(uTemperature,self.uInterFaceName+u'/'+oSetting.uConfigName))

            if oRoom:
                if uTemperature is not None:
                    oSetting.oDevice.set_mode(oRoom,oSetting.oDevice.ModeManual)
                    uRet = str(oSetting.oDevice.set_target_temperature(oRoom, fTemperature))
                else:
                    uRet = str(oSetting.oDevice.set_mode(oRoom, bMode))
            else:
                self.ShowError("set_mode:Invalid Parameter")

        except Exception as e:
            self.ShowError("room_set_mode: Internal Error",oSetting.uConfigName,e)

        return self._CreateSimpleResult(uRet)



    ''' ##################################################################################  '''

    def ELV_clearcache(self,oSetting,oAction, dParams):
        """
        Clears all caches, should be called after changes of mode and temperatures, performs a reconnect
        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter (unused)
        :return: dict: key:result=OK
        :rtype: QueryDict
        """


        oSetting.Disconnect()
        oSetting.oDevice =  None
        # fSleep(0.5)
        oSetting.Connect()

        return self._CreateSimpleResult("OK")

    def ELV_getrooms(self,oSetting,oAction, dParams): #check
        """
        Returns a list of rooms

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter (unused)
        :return: list: A list of dicts: key:name=room name , rf_address= Rf Address of Room
        :rtype: list
        """

        aRet  = []
        i     = 0

        for oRoom in oSetting.oDevice.rooms:
            dLine                           = QueryDict()
            dLine.uVarSuffix                = "[" + str(i) + "]"
            dLine.dValue                    = {"name": oRoom.name, "rf_address": str(oRoom.rf_address)}
            aRet.append(dLine)
            i=i+1

        return aRet

    def ELV_getattribute(self,oSetting,oAction, dParams):
        """
        Returns a attribut for a device or room

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address and attributename
        :return: dict: key:result=Error or result=attributevalue, attributevalue=n/a if attribute not found
        :rtype: QueryDict
        """

        uRF_Address                         = ReplaceVars(dParams["rf_address"],self.uInterFaceName+u'/'+oSetting.uConfigName)
        uAttribute                          = ReplaceVars(dParams["attributename"],self.uInterFaceName+u'/'+oSetting.uConfigName)


        try:
            oDevice = oSetting.oDevice.device_by_rf(uRF_Address)
            uRet = getattr(oDevice, uAttribute, "N/A")
            if uRet==None:
                uRet="N/A"
        except Exception as e:
            uRet = "N/A"

        if uRet=="N/A":
            Logger.error(uAttribute)

        return self._CreateSimpleResult(uRet)

    def ELV_getroomdevices(self,oSetting,oAction, dParams):
        """
        Gets a list of room devices excluding the room name as first element

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or _ELV_getroomdevices result
        :rtype: QueryDict
        """

        return self._ELV_getroomdevices(oSetting=oSetting,oAction=oAction, dParams=dParams, bAddRoom=False)

    def ELV_getroomdevicesex(self,oSetting,oAction, dParams):
        """
        Gets a list of room devices including the room name as first element

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or _ELV_getroomdevices result
        :rtype: QueryDict
        """
        return self._ELV_getroomdevices(oSetting=oSetting,oAction=oAction, dParams=dParams, bAddRoom=True)

    def ELV_room_set_mode_auto(self,oSetting,oAction, dParams):
        """
        Sets a room to mode auto

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or maxcube result
        :rtype: QueryDict
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeAuto)

    def ELV_room_set_mode_boost(self,oSetting,oAction, dParams):
        """
        Sets a room to mode boost

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or maxcude result
        :rtype: QueryDict
        """

        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeBoost)

    def ELV_room_set_mode_manual(self,oSetting,oAction, dParams):
        """
        Sets a room to mode manual

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room and the temperature in Celsius
        :return: dict: key:result=Error or maxcube result
        :rtype: QueryDict
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeManual)

    def ELV_room_set_mode_vacation(self,oSetting,oAction, dParams):
        """
        Sets a room to mode auto

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or maxcube result
        :rtype: QueryDict
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeVacation)

    def ELV_device_set_mode_auto(self, oSetting, oAction, dParams):
        """
        Sets a device to mode auto mode

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address
        :return: dict: key:result=Error or maxcube result
        :rtype: QueryDict
        """
        return self._ELV_set_mode(oSetting, oAction, dParams, oSetting.oDevice.ModeAuto)

    def ELV_device_set_mode_boost(self, oSetting, oAction, dParams):
        """
        Sets a device to mode boost

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address
        :return: dict: key:result=Error or maxcube result
        :rtype: QueryDict
        """
        return self._ELV_set_mode(oSetting, oAction, dParams, oSetting.oDevice.ModeBoost)

    def ELV_device_set_mode_manual(self,oSetting,oAction, dParams):
        """
        Sets a device to mode manual

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address and the temperature in Celsius
        :return: dict: key:result=Error or maxcube result
        :rtype: QueryDict
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeManual)

    def ELV_device_set_mode_vacation(self,oSetting,oAction, dParams):
        """
        Sets a device to mode manual

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address
        :return: dict: key:result=Error or maxcube result
        :rtype: QueryDict
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeVacation)

