# -*- coding: utf-8 -*-
# telnet

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
from typing                                 import Optional
from typing                                 import Dict

from ORCA.interfaces.BaseInterface          import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings  import cBaseInterFaceSettings
from ORCA.utils.TypeConvert                 import ToInt
from ORCA.vars.Access                       import SetVar
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.action.Action import cAction
from ORCA.utils.FileName                    import cFileName
from ORCA.actions.ReturnCode                import eReturnCode
from ORCA.utils.Telnet                      import cTelnet


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass
else:
    from typing import TypeVar
    cBaseTrigger = TypeVar('cBaseTrigger')

'''
<root>
  <repositorymanager>
    <entry>
      <name>Telnet2</name>
      <description language='English'>Interface to send telnet commands (new)</description>
      <description language='German'>Interface um Telnet Kommandos zu senden (neu)</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/telnet2</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/telnet2.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>scripts</type>
          <name>UPNP Discover</name>
        </dependency>
      </dependencies>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):
        def __init__(self,oInterFace:cInterface):
            super().__init__(oInterFace)
            self.bStopThreadEvent:bool                    = False
            self.oTelnet:Optional[cTelnet]                = None
            self.uRetVar:str                              = ''
            self.uResponse:str                            = ''
            self.aIniSettings.fTimeOut                    = 2.0
            self.aIniSettings.iTimeToClose                = -1
            self.aIniSettings.uFNCodeset                  = 'Select'
            self.aIniSettings.uHost                       = 'discover'
            self.aIniSettings.uParseResultOption          = 'store'
            self.aIniSettings.uPort                       = '23'
            self.aIniSettings.uDiscoverScriptName         = 'discover_upnp'
            self.aIniSettings.fDISCOVER_UPNP_timeout      = 5.0
            self.aIniSettings.uDISCOVER_UPNP_manufacturer = ''
            self.aIniSettings.uDISCOVER_UPNP_models       = '[]'
            self.aIniSettings.uDISCOVER_UPNP_prettyname   = ''
            self.aIniSettings.uDISCOVER_UPNP_servicetypes = 'upnp:rootdevice'

        def ReadConfigFromIniFile(self,uConfigName:str) -> None:
            super().ReadConfigFromIniFile(uConfigName=uConfigName)
            self.aIniSettings.uResultEndString           = self.aIniSettings.uResultEndString.replace('[LF]','\n').replace('[CR]','\r')
            return

        def Connect(self) -> bool:

            if not super().Connect():
                return False

            try:
                self.ShowDebug(uMsg=f'Connecting to {self.aIniSettings.uHost}:{self.aIniSettings.uPort}')
                self.oTelnet = cTelnet(uHost=self.aIniSettings.uHost,iPort=ToInt(self.aIniSettings.uPort))
            except Exception as e:
                self.ShowError(uMsg=f'Cannot open telnet session: {+self.aIniSettings.uHost}',oException=e)
                self.bOnError=True
                return False
            self.ShowDebug(uMsg='Connected! (Virtual)')
            self.bIsConnected =True
            return True

        def Disconnect(self) -> bool:

            if not super().Disconnect():
                return False
            return True

    def __init__(self):
        cInterFaceSettings = self.cInterFaceSettings
        super().__init__()
        self.dSettings:Dict                             = {}
        self.oSetting:Optional[cInterFaceSettings]      = None
        self.uResponse                                  = ''
        self.iWaitMs:int                                = 2000

    def Init(self, uObjectName: str, oFnObject: Optional[cFileName] = None) -> None:
        super().Init(uObjectName=uObjectName, oFnObject=oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = 'enabled'
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = 'enabled'
        self.oObjectConfig.dDefaultSettings['User']['active']                        = 'enabled'
        self.oObjectConfig.dDefaultSettings['Password']['active']                    = 'enabled'
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = 'enabled'
        self.oObjectConfig.dDefaultSettings['ParseResult']['active']                 = 'enabled'
        self.oObjectConfig.dDefaultSettings['TokenizeString']['active']              = 'enabled'
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = 'enabled'
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = 'enabled'
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = 'enabled'
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = 'enabled'
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = 'enabled'

    def DeInit(self, **kwargs) -> None:
        super().DeInit(**kwargs)
        for uSettingName in self.dSettings:
            self.dSettings[uSettingName].DeInit()

    def GetConfigJSON(self) -> Dict:
        super().GetConfigJSON()
        return {'TerminalType':    {'active': 'enabled', 'order': 8, 'type': 'string', 'title': '$lvar(IFACE_TELNET2_3)', 'desc': '$lvar(IFACE_TELNET2_4)', 'section': '$var(ObjectConfigSection)', 'key': 'TerminalType',    'default':'' },
                'ResultEndString': {'active': 'enabled', 'order': 9, 'type': 'string', 'title': '$lvar(IFACE_TELNET2_1)', 'desc': '$lvar(IFACE_TELNET2_2)', 'section': '$var(ObjectConfigSection)', 'key': 'ResultEndString', 'default': '[LF]'},
                }

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        super().SendCommand(oAction=oAction,oSetting=oSetting,uRetVar=uRetVar,bNoLogOut=bNoLogOut)
        eRet:eReturnCode  = eReturnCode.Error
        uMsg:str
        byMsg:bytes

        if uRetVar!='':
            oAction.uGlobalDestVar=uRetVar

        oSetting.uRetVar=uRetVar

        uMsg=oAction.uCmd
        uMsg=ReplaceVars(uMsg,self.uObjectName+'/'+oSetting.uConfigName)
        uMsg=ReplaceVars(uMsg)

        oSetting.Connect()

        self.ShowInfo(uMsg=f'Setting Credentials: User:"{oSetting.aIniSettings.uUser}" Password: "{oSetting.aIniSettings.uPassword}"', uParConfigName=oSetting.uConfigName)
        if oAction.bWaitForResponse:
            oSetting.oTelnet.fWaitTimeForAfter=oSetting.aIniSettings.fTimeOut
        if oSetting.aIniSettings.uTerminalType:
            oSetting.oTelnet.SetArgs({'term':oSetting.aIniSettings.uTerminalType})
        oSetting.oTelnet.uTermStringForCredentials = oSetting.aIniSettings.uResultEndString.replace('\\n','\n').replace('\\r','\r')
        oSetting.oTelnet.uTermStringForCommands = oSetting.aIniSettings.uResultEndString.replace('\\n','\n').replace('\\r','\r')
        oSetting.oTelnet.SetCredentionals(uUser=oSetting.aIniSettings.uUser,uPassword=oSetting.aIniSettings.uPassword)

        #Logger.info ('Interface '+self.uObjectName+': Sending Command: '+sCommand + ' to '+oSetting.sHost+':'+oSetting.sPort)
        try:
            self.ShowInfo(uMsg=f'Sending Command: {uMsg} to {oSetting.aIniSettings.uHost}:{oSetting.aIniSettings.uPort}',uParConfigName=oSetting.uConfigName)
            uMsg=uMsg.replace('\\n','\n').replace('\\r','\r')
            oSetting.oTelnet.AddCommand(uCommand=uMsg)
            uResponse=oSetting.oTelnet.Send()

            if oAction is not None:
                uCmd,uRetVal=self.ParseResult(oAction,uResponse,oSetting)
                self.ShowDebug(uMsg='Parsed Responses:'+uRetVal)
                if not uRetVar=='' and not uRetVal=='':
                    SetVar(uVarName = uRetVar, oVarValue = uRetVal)
                # We do not need to wait for an response anymore

            eRet = eReturnCode.Success
        except Exception as e:
            self.ShowError(uMsg= 'can\'t Send Message',uParConfigName=oSetting.uConfigName,oException=e)
            eRet = eReturnCode.Error
            oSetting.Disconnect()
        self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet

