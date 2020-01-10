# -*- coding: utf-8 -*-
# elv_max

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

'''

 This code uses the (adjusted) maxcube module

 https://github.com/hackercowboy/python-maxcube-api
'''

from typing                         import TYPE_CHECKING
from typing                         import Union
from typing                         import List
from typing                         import Dict
from typing                         import Callable
from typing                         import Tuple

import sys
from kivy.logger                    import Logger

from ORCA.interfaces.BaseInterface  import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
from ORCA.vars.Replace              import ReplaceVars
from ORCA.utils.Path                import cPath
from ORCA.utils.FileName            import cFileName
from ORCA.vars.QueryDict            import QueryDict
from ORCA.utils.TypeConvert         import ToInt
from ORCA.utils.TypeConvert         import ToFloat
from ORCA.utils.TypeConvert         import ToDic
from ORCA.utils.TypeConvert         import ToList
from ORCA.vars.Actions              import Var_DelArray
from ORCA.Action                    import cAction
from ORCA.actions.ReturnCode        import eReturnCode

import ORCA.Globals as Globals

if TYPE_CHECKING:
    from interfaces.elv_max.maxcube.cube        import MaxCube
    from interfaces.elv_max.maxcube.connection  import MaxCubeConnection
    from interfaces.elv_max.maxcube.room        import MaxRoom
else:
    sys.path.append((cPath(Globals.oPathInterface + "/elv_max")).string)
    # noinspection PyUnresolvedReferences
    from maxcube.cube import MaxCube
    # noinspection PyUnresolvedReferences
    from maxcube.connection import MaxCubeConnection
    # noinspection PyUnresolvedReferences
    from maxcube.room import MaxRoom
'''
<root>
  <repositorymanager>
    <entry>
      <name>ELV MAX</name>
      <description language='English'>Interface control ELV MAX</description>
      <description language='German'>Interface um ALV MAX Geräte zu steuern</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
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
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):

        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.aIniSettings.uHost                       = u"discover"
            self.aIniSettings.uPort                       = u"62910"
            self.aIniSettings.uFNCodeset                  = u"CODESET_elv_max_DEFAULT.xml"
            self.aIniSettings.uParseResultOption          = u'dict'
            self.aIniSettings.iTimeToClose                = -1
            self.aIniSettings.uDiscoverScriptName         = u"discover_elvmax"
            self.aIniSettings.uDISCOVER_ELVMAX_serialnumber = ""
            self.oDevice:Union[MaxCube,None]                = None


        def Disconnect(self) -> bool:
            if not self.bIsConnected:
                return cBaseInterFaceSettings.Disconnect(self)
            try:
                if self.oDevice is not None:
                    self.oDevice.connection.disconnect()
                return cBaseInterFaceSettings.Disconnect(self)
            except Exception as e:
                self.ShowError(u'Cannot diconnect:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                return cBaseInterFaceSettings.Disconnect(self)

        def Connect(self) -> bool:

            if not cBaseInterFaceSettings.Connect(self):
                return False

            if self.aIniSettings.uHost=='':
                return False

            try:
                if self.oDevice is None:
                    # self.oDevice = Cube(address=self.aIniSettings.uHost, port=ToInt(self.aIniSettings.uPort))
                    self.oDevice = MaxCube(MaxCubeConnection(host=self.aIniSettings.uHost, port=ToInt(self.aIniSettings.uPort)))

                # self.oDevice.connect()
                self.oInterFace.oObjectConfig.WriteDefinitionConfigPar(uSectionName = self.uSection, uVarName= u'OldDiscoveredIP', uVarValue = self.aIniSettings.uHost)
                self.bIsConnected=True
                return self.bIsConnected
            except Exception as e:
                if hasattr(e,"errno"):
                    if e.errno==10051:
                        self.bOnError=True
                        self.ShowWarning(u'Cannot connect (No Network):'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort)
                        return False
                self.ShowError(u'Cannot connect:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.bOnError=True
                return False

    def __init__(self):
        cBaseInterFace.__init__(self)
        self.dSettings:Dict                                 = {}
        self.oSetting:Union[cBaseInterFaceSettings,None]    = None
        self.aDiscoverScriptsBlackList:List[str]            = ["iTach (Global Cache)","Keene Kira","UPNP","Enigma","EISCP (Onkyo)"]
        self.dInterfaceFunctions:Dict[str,Callable]         = {}
        self.RegisterInterfaceActions()


    def Init(self,uObjectName:str,oFnObject:Union[cFileName,None]=None) -> None:
        """ Initialisizes the Interface

        :param str uObjectName: unicode : Name of the interface
        :param cFileName oFnObject: The Filename of the interface
        """

        cBaseInterFace.Init(self,uObjectName,oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self, **kwargs) -> None:
        cBaseInterFace.DeInit(self,**kwargs)
        for uSettingName in self.dSettings:
            self.dSettings[uSettingName].DeInit()

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        iTryCount:int     = 0
        eRet:eReturnCode  = eReturnCode.Error

        uRetVar:str = ReplaceVars(uRetVar)
        oSetting.uRetVar=uRetVar

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        dCmd:Dict     = ToDic(oAction.uCmd)
        uCmd:str      = dCmd["method"]
        dParams:Dict  = dCmd["params"]

        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                try:
                    self.ShowDebug("Sending elv max command: %s" % uCmd)
                    oFunc:Callable  = self.dInterfaceFunctions.get(uCmd)
                    aResult:List    = []
                    if oFunc is not None:
                        aResult = oFunc(oSetting=oSetting,oAction=oAction, dParams=dParams)
                    else:
                        self.ShowError("Function not implemented: %s" % uCmd)

                    for dLine in aResult:
                        uGlobalDestVarSave:str      = oAction.uGlobalDestVar
                        uLocalDestVarSave:str       = oAction.uLocalDestVar

                        if oAction.uGetVar.startswith('ORCAMULTI'):
                            aTmpGlobalDestVar:List  = ToList(oAction.uGlobalDestVar)
                            aTmpLocalDestVar:List   = ToList(oAction.uLocalDestVar)
                            oAction.uGlobalDestVar  = "".join('"'+e+dLine.uVarSuffix+'",' for e in aTmpGlobalDestVar)[:-1]
                            oAction.uLocalDestVar   = "".join('"'+e+dLine.uVarSuffix+'",'  for e in aTmpLocalDestVar)[:-1]
                        else:
                            oAction.uGlobalDestVar  = oAction.uGlobalDestVar + dLine.uVarSuffix
                            oAction.uLocalDestVar   = oAction.uLocalDestVar + dLine.uVarSuffix

                        uCmd, uRetVal           = self.ParseResult(oAction, dLine.dValue, oSetting)
                        oAction.uGlobalDestVar  = uGlobalDestVarSave
                        oAction.uLocalDestVar   = uLocalDestVarSave

                    eRet = eReturnCode.Success
                    break
                except Exception as e:
                    self.ShowError(uMsg=u'can\'t Send Message',uParConfigName=oSetting.uConfigName,oException=e)
                    eRet = eReturnCode.Error
            else:
                oSetting.bIsConnected=False

        self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet

    def RegisterInterfaceActions(self) -> None:
        """
        Register all actions managed by the interface
        """

        aFuncs:List=dir(self)
        for uFuncName in aFuncs:
            if uFuncName.startswith('ELV_'):
                uName = uFuncName[4:]
                self.dInterfaceFunctions[uName] = getattr(self, uFuncName)

    def _GetRFAddress(self,oSetting:cInterFaceSettings,uRoom:str) -> Union[Tuple,None]:
        """
        Finds the rf_address for a room

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param str uRoom: the room name
        :return: The rf_address, or None if not found
        :rtype: collections.namedtuple
        """

        for oRoom in oSetting.oDevice.rooms:
            if oRoom.name == uRoom:
                return oRoom.rf_address
        oSetting.ShowError("Wrong Room Name given:"+uRoom)
        return None


    def _GetRoomForRfAddress(self, uRfAddress:str,oSetting:cInterFaceSettings) -> Union[MaxRoom,None]:
        """
        Internal Helper function to find the Room for a RF Address

        :param str uRfAddress: The RF Address to look for
        :param cInterface.cInterFaceSettings oSetting: The setting object
        :return: The room object or None if not found
        """
        for oRoom in oSetting.oDevice.rooms:
            if str(oRoom.rf_address)==uRfAddress:
                return oRoom
            for oDevice in oSetting.oDevice.devices_by_room(oRoom):
                if str(oDevice.rf_address)==uRfAddress:
                    return oRoom
        return None

    def _CreateSimpleResult(self,uResult:str) -> List[QueryDict]:
        """
        Helper Function to create a simple one line result

        :param uResult:
        :return: a dict key:result=Result
        :rtype: QueryDict
        """
        aRet:List               = []
        dLine:QueryDict         = QueryDict()
        dLine.uVarSuffix        = ""
        dLine.dValue            = {"result": uResult}
        aRet.append(dLine)
        return aRet

    def _ELV_getroomdevices(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict, bAddRoom:bool) -> List: #check
        """
        Internal Helper function to get a list of devices of a room

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :param boolean bAddRoom: Flag to include the room name as first element
        :return: list: A list of dicts: key:name=room name , rf_address= Rf Address of Room
        """

        aRet:List        = []
        i:int            = 0
        uRoom:str        = ReplaceVars(dParams["room"],self.uObjectName+u'/'+oSetting.uConfigName)

        aTmpDestVar:List = ToList(oAction.uGlobalDestVar)
        for uVarName in aTmpDestVar:
            Var_DelArray(uVarName=uVarName+u'[]')

        oRoom:MaxRoom
        dLine:QueryDict

        for oRoom in oSetting.oDevice.rooms:
            if oRoom.name == uRoom:
                if bAddRoom:
                    dLine                       = QueryDict()
                    dLine.uVarSuffix            = "[" + str(i) + "]"
                    uRfAddress:str              = str(oRoom.rf_address)
                    dLine.dValue                = {"name": oRoom.name, "rf_address": uRfAddress}
                    aRet.append(dLine)
                    i = i + 1

                for oDevice in oSetting.oDevice.devices_by_room(oRoom):
                    dLine                       = QueryDict()
                    dLine.uVarSuffix            = "[" + str(i) + "]"
                    uRfAddress                  = str(oDevice.rf_address)
                    dLine.dValue                = {"name": oDevice.name,"rf_address": uRfAddress}
                    aRet.append(dLine)
                    i = i + 1
                break
        return aRet

    def _ELV_set_mode(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict, bMode:bool) -> List[QueryDict]:
        """
        Internal Helper function to sets the mode of a room or device , depends on what is given in dParams

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, see calling function for valid options
        :param byte bMode: the mode
        :return: dict: key:result=Error or maxcube result
        """

        uRet:str                    = "Error"
        kwArgs:Dict                 = {}
        oRoom:Union[MaxRoom,None]   = None
        uRoom:str
        fTemperature:float           = 0.0
        fTemperature:str
        uRF_Address:str

        try:
            uRF_Address = dParams.get("rf_address")
            if uRF_Address:
                uRF_Address = ReplaceVars(uRF_Address, self.uObjectName + u'/' + oSetting.uConfigName)

            uRoom = dParams.get("room")
            if uRoom:
                uRoom = ReplaceVars(uRoom, self.uObjectName + u'/' + oSetting.uConfigName)

            if uRoom is None and uRF_Address is None:
                self.ShowError("set_mode:Invalid Parameter, not a room or rf_address given")
                return self._CreateSimpleResult(uRet)

            if uRF_Address is None:
                oRF_Address = self._GetRFAddress(oSetting,uRoom)
                oRoom       = self._GetRoomForRfAddress(str(oRF_Address), oSetting)

            if uRoom is None:
                oRoom = self._GetRoomForRfAddress(uRF_Address, oSetting)

            uTemperature= dParams.get("temperature")
            if uTemperature is not None:
                fTemperature = ToFloat(ReplaceVars(uTemperature,self.uObjectName+u'/'+oSetting.uConfigName))

            if oRoom:
                if uTemperature is not None:
                    oSetting.oDevice.set_mode(oRoom,oSetting.oDevice.ModeManual)
                    uRet = str(oSetting.oDevice.set_target_temperature(oRoom, fTemperature))
                else:
                    uRet = str(oSetting.oDevice.set_mode(oRoom, bMode))
            else:
                self.ShowError("set_mode:Invalid Parameter")

        except Exception as e:
            self.ShowError(uMsg="room_set_mode: Internal Error",uParConfigName=oSetting.uConfigName,oException=e)

        return self._CreateSimpleResult(uRet)



    ''' ##################################################################################  '''

    def ELV_clearcache(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Clears all caches, should be called after changes of mode and temperatures, performs a reconnect
        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter (unused)
        :return: dict: key:result=OK
        """


        oSetting.Disconnect()
        oSetting.oDevice =  None
        # fSleep(0.5)
        oSetting.Connect()

        return self._CreateSimpleResult("OK")

    def ELV_getrooms(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List:
        """
        Returns a list of rooms

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter (unused)
        :return: list: A list of dicts: key:name=room name , rf_address= Rf Address of Room
        """

        aRet:List  = []
        i:int      = 0
        oRoom:MaxRoom

        for oRoom in oSetting.oDevice.rooms:
            dLine:QueryDict                 = QueryDict()
            dLine.uVarSuffix                = "[" + str(i) + "]"
            dLine.dValue                    = {"name": oRoom.name, "rf_address": str(oRoom.rf_address)}
            aRet.append(dLine)
            i=i+1

        return aRet

    def ELV_getattribute(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Returns a attribut for a device or room

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address and attributename
        :return: dict: key:result=Error or result=attributevalue, attributevalue=n/a if attribute not found
        """

        oDevice:MaxCube

        uRF_Address:str                         = ReplaceVars(dParams["rf_address"],self.uObjectName+u'/'+oSetting.uConfigName)
        uAttribute:str                          = ReplaceVars(dParams["attributename"],self.uObjectName+u'/'+oSetting.uConfigName)

        try:
            oDevice = oSetting.oDevice.device_by_rf(uRF_Address)
            uRet:str = getattr(oDevice, uAttribute, "N/A")
            if uRet is None:
                uRet="N/A"
        except Exception as e:
            uRet = "N/A"

        if uRet=="N/A":
            Logger.error(uAttribute)

        return self._CreateSimpleResult(uRet)

    def ELV_getroomdevices(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Gets a list of room devices excluding the room name as first element

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or _ELV_getroomdevices result
        """

        return self._ELV_getroomdevices(oSetting=oSetting,oAction=oAction, dParams=dParams, bAddRoom=False)

    def ELV_getroomdevicesex(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Gets a list of room devices including the room name as first element

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or _ELV_getroomdevices result
        """
        return self._ELV_getroomdevices(oSetting=oSetting,oAction=oAction, dParams=dParams, bAddRoom=True)

    def ELV_room_set_mode_auto(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Sets a room to mode auto

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or maxcube result
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeAuto)

    def ELV_room_set_mode_boost(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Sets a room to mode boost

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or maxcude result
        """

        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeBoost)

    def ELV_room_set_mode_manual(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Sets a room to mode manual

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room and the temperature in Celsius
        :return: dict: key:result=Error or maxcube result
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeManual)

    def ELV_room_set_mode_vacation(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Sets a room to mode auto

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include room
        :return: dict: key:result=Error or maxcube result
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeVacation)

    def ELV_device_set_mode_auto(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Sets a device to mode auto mode

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address
        :return: dict: key:result=Error or maxcube result
        """
        return self._ELV_set_mode(oSetting, oAction, dParams, oSetting.oDevice.ModeAuto)

    def ELV_device_set_mode_boost(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Sets a device to mode boost

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address
        :return: dict: key:result=Error or maxcube result
        """
        return self._ELV_set_mode(oSetting, oAction, dParams, oSetting.oDevice.ModeBoost)

    def ELV_device_set_mode_manual(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Sets a device to mode manual

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address and the temperature in Celsius
        :return: dict: key:result=Error or maxcube result
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeManual)

    def ELV_device_set_mode_vacation(self,oSetting:cInterFaceSettings,oAction:cAction, dParams:Dict) -> List[QueryDict]:
        """
        Sets a device to mode manual

        :param cInterface.cInterFaceSettings oSetting: The setting object
        :param cAction oAction: The action object (unused)
        :param dict dParams: The parameter, needs to include rf_address
        :return: dict: key:result=Error or maxcube result
        """
        return self._ELV_set_mode(oSetting,oAction, dParams,oSetting.oDevice.ModeVacation)
