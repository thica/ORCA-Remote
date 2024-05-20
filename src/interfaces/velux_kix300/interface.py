# -*- coding: utf-8 -*-
# android_adb

"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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


from __future__                             import annotations
from typing                                 import TYPE_CHECKING
from typing                                 import Dict
from typing                                 import List
from typing                                 import Optional

import sys

from ORCA.utils.Path                        import cPath
from ORCA.interfaces.BaseInterface          import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings  import cBaseInterFaceSettings
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.vars.Access                       import SetVar
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.TypeConvert                 import ToDic
from ORCA.action.Action import cAction
from ORCA.actions.ReturnCode                import eReturnCode
from ORCA.Globals import Globals

if TYPE_CHECKING:
    from interfaces.velux_kix300.veluxtinyapi import cVelux
else:
    sys.path.append(str(cPath(Globals.oPathInterface + "/velux_kix300")))
    from veluxtinyapi.veluxtinyapi import cVelux


'''
<root>
  <repositorymanager>
    <entry>
      <name>Velux KIX300</name>
      <description language='English'>Interface control Velux KIX300</description>
      <description language='German'>Interface um das Velux KIX300 zu steuern</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/velux_kix300</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/velux_kix300.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
      </dependencies>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

'''
Overall, this could have been done with the url module as well, but the veluxtinyapin is there, which makes it simpler
'''

class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):

        def __init__(self,oInterFace:cInterface):
            super().__init__(oInterFace)
            self.aIniSettings.uHost                       = 'https://app.velux-active.com'
            self.aIniSettings.uPort                       = ''
            self.aIniSettings.uUser                       = ''
            self.aIniSettings.uFNCodeset                  = 'CODESET_velux_kix300.xml'
            self.aIniSettings.fTimeOut                    = 2.0
            self.aIniSettings.iTimeToClose                = -1
            self.aIniSettings.iRetryCount                 = 1
            self.aIniSettings.uParseResultOption          = 'store'

            # Load the helper
            self.oDevice = cVelux()

        def ReadAction(self,oAction:cAction) -> None:
            super().ReadAction(oAction)
            oAction.uParams      = oAction.dActionPars.get('params','')

        def Disconnect(self) -> bool:
            if not self.bIsConnected:
                return super().Disconnect()

        def Connect(self) -> bool:

            if not super().Connect():
                return False

            self.oDevice.uHost = self.aIniSettings.uHost

            try:
                self.bInConnect = True
                self.bIsConnected = True
                eRet:eReturnCode = self.ExecuteStandardAction('logon')
                self.bInConnect = False
                self.bIsConnected = (eRet == eReturnCode.Success)
                if not self.bIsConnected:
                    self.ShowError(uMsg=f'Cant\'t connect: {self.oDevice.uHost}')
                return self.bIsConnected

            except Exception as e:
                self.ShowError(uMsg=f'Cant\'t connect: {self.oDevice.uHost}', oException=e)
                self.bOnError = True
                return False

    def __init__(self):
        cInterFaceSettings = self.cInterFaceSettings
        super().__init__()
        self.dSettings:Dict                             = {}
        self.oSetting:Optional[cInterFaceSettings]      = None

    def Init(self, uObjectName:str, oFnObject:Optional[cFileName]=None) -> None:
        """ Initializes the Interface

        :param str uObjectName: unicode : Name of the interface
        :param cFileName oFnObject: The Filename of the interface
        """

        super().Init(uObjectName=uObjectName,oFnObject=oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = 'enabled'
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = 'disabled'
        self.oObjectConfig.dDefaultSettings['User']['active']                        = 'enabled'
        self.oObjectConfig.dDefaultSettings['Password']['active']                    = 'enabled'
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = 'enabled'
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = 'disabled'
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = 'disabled'
        self.oObjectConfig.dDefaultSettings['RetryCount']['active']                  = 'enabled'
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = 'enabled'
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = 'enabled'
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = 'disabled'

    def DeInit(self,**kwargs) -> None:
        super().DeInit(**kwargs)
        for uSettingName in self.dSettings:
            self.dSettings[uSettingName].DeInit()

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        super().SendCommand(oAction=oAction,oSetting=oSetting,uRetVar=uRetVar,bNoLogOut=bNoLogOut)

        iTryCount:int    = 0
        eRet:eReturnCode = eReturnCode.Success
        uTmpVar2:str     = ''
        oResult          = ''

        oSetting.SetContextVar(uVarName='User',uVarValue=oSetting.aIniSettings.uUser)
        oSetting.SetContextVar(uVarName='Password',uVarValue=oSetting.aIniSettings.uPassword)
        uRetVar          = ReplaceVars(uRetVar)
        oSetting.uRetVar = uRetVar

        uCmd: str = ReplaceVars(oAction.uCmd)
        uCmd = ReplaceVars(uCmd, self.uObjectName + '/' + oSetting.uConfigName)

        dCmd: Dict    = ToDic(uCmd)
        uCmd:str      = dCmd['method']
        dParams:Dict  = dCmd.get('params',{})

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        while iTryCount<oSetting.aIniSettings.iRetryCount:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                try:
                    self.ShowDebug(uMsg=f'Sending Velux command: {uCmd}:{dParams}')
                    if uCmd == 'logon':
                        oResult=oSetting.oDevice.Logon(uUserName=oSetting.aIniSettings.uUser,uPassword=oSetting.aIniSettings.uPassword)
                        if oResult==True:
                            eRet: eReturnCode = eReturnCode.Success
                        else:
                            eRet: eReturnCode = eReturnCode.Error
                    elif uCmd == 'gethome':
                        oResult=oSetting.oDevice.GetHomes()
                        if oResult==True:
                            eRet: eReturnCode = eReturnCode.Success
                            oResult = []
                            for oHome in oSetting.oDevice.dHomes.values():
                                oResult.append(oHome.dResponse)
                        else:
                            eRet: eReturnCode = eReturnCode.Error
                    elif uCmd == 'getroomdevices':
                        try:
                            uHomeName:str=dParams.get('home','')
                            uRoomName:str=dParams.get('room', '')
                            dModules = oSetting.oDevice.dHomes[uHomeName.lower()].dRooms[uRoomName.lower()].dModules
                            aResult:List = []
                            for uName in dModules:
                                aResult.append(uName)
                            oResult=ToUnicode(aResult)
                        except Exception as e:
                            self.ShowError(uMsg=f'can\'t get Modules for {uHomeName} / {uRoomName}', uParConfigName=oSetting.uConfigName,oException=e)
                            eRet: eReturnCode = eReturnCode.Error
                    elif uCmd == 'getdevicestate':
                        try:
                            uHomeName:str=dParams.get('home','')
                            uRoomName:str=dParams.get('room', '')
                            uModuleName:str=dParams.get('device', '')
                            oResult=oSetting.oDevice.GetState(uHomeName=uHomeName, uRoomName=uRoomName, uModuleName=uModuleName)
                            oResult=ToUnicode(oResult)
                        except Exception as e:
                            self.ShowError(uMsg=f'can\'t get status for {uHomeName} / {uRoomName} / {uModuleName}', uParConfigName=oSetting.uConfigName,oException=e)
                            eRet: eReturnCode = eReturnCode.Error
                    elif uCmd == 'setdevicestate':
                        try:
                            uHomeName:str=dParams.get('home','')
                            uRoomName:str=dParams.get('room', '')
                            uModuleName:str=dParams.get('device', '')
                            uPosition: str = dParams.get('position', '')
                            oResult=oSetting.oDevice.SetState(uHomeName=uHomeName, uRoomName=uRoomName, uModuleName=uModuleName, uState=uPosition)
                        except Exception as e:
                            self.ShowError(uMsg=f'can\'t set status for {uHomeName} / {uRoomName} / {uModuleName}', uParConfigName=oSetting.uConfigName,oException=e)
                            eRet: eReturnCode = eReturnCode.Error

                    else:
                        self.ShowError(uMsg=f'Unknown Command {uCmd}', uParConfigName=oSetting.uConfigName, oException=e)
                        oResult = []
                        eRet: eReturnCode = eReturnCode.Error
                        break


                    uCmd,uRetVal=self.ParseResult(oAction,oResult,oSetting)
                    self.ShowDebug(uMsg='Parsed Response:'+ToUnicode(uRetVal))
                    if not uRetVar=='':
                        SetVar(uVarName = uRetVar, oVarValue = uRetVal)

                    self.ShowDebug(uMsg='Result:'+str( oResult))
                    break
                except Exception as e:
                    self.ShowError(uMsg='can\'t Send Message',uParConfigName=oSetting.uConfigName,oException=e)
                    eRet=eReturnCode.Error
            else:
                oSetting.bIsConnected=False

        # self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet
