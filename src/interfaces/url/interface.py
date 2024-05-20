# -*- coding: utf-8 -*-
# url

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

from __future__                            import annotations
from typing                                import Dict
from typing                                import Tuple
from typing                                import Optional

import urllib
import base64
from time                                  import sleep
from kivy.network.urlrequest               import UrlRequest
from ORCA.interfaces.BaseInterface         import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
from ORCA.vars.Replace                     import ReplaceVars
from ORCA.vars.Access                      import SetVar
from ORCA.utils.TypeConvert                import UnEscapeUnicode
from ORCA.utils.TypeConvert                import ToUnicode
from ORCA.utils.TypeConvert                import ToDic
from ORCA.utils.TypeConvert                import ToBytes
from ORCA.utils.TypeConvert                import ToInt
from ORCA.utils.FileName                   import cFileName
from ORCA.action.Action import cAction
from ORCA.actions.ReturnCode               import eReturnCode

'''
<root>
  <repositorymanager>
    <entry>
      <name>URL-Web</name>
      <description language='English'>Interface to send web based commands</description>
      <description language='German'>Interface um webbasierte Kommandos zu senden</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/url</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/url.zip</sourcefile>
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


# noinspection PyProtectedMember
class cInterface(cBaseInterFace):

    # noinspection PyUnusedLocal
    class cInterFaceSettings(cBaseInterFaceSettings):

        def __init__(self,oInterFace:cInterface):
            super().__init__(oInterFace)
            self.bIgnoreTimeOut                           = False
            self.aIniSettings.uHost                       = 'discover'
            self.aIniSettings.uPort                       = '80'
            self.aIniSettings.uFNCodeset                  = 'Select'
            self.aIniSettings.fTimeOut                    = 2.0
            self.aIniSettings.iTimeToClose                = -1
            self.aIniSettings.uDiscoverScriptName         = 'discover_upnp'
            self.aIniSettings.uParseResultOption          = 'no'
            self.aIniSettings.fDISCOVER_UPNP_timeout      = 2.0
            self.aIniSettings.uDISCOVER_UPNP_models       = '[]'
            self.aIniSettings.uDISCOVER_UPNP_servicetypes = 'urn:dial-multiscreen-org:service:dial:1,urn:schemas-upnp-org:service:AVTransport:1'
            self.aIniSettings.uDISCOVER_UPNP_manufacturer = ''
            self.aIniSettings.uDISCOVER_UPNP_prettyname   = ''

        def ReadAction(self,oAction:cAction) -> None:
            super().ReadAction(oAction)
            oAction.uParams       = oAction.dActionPars.get('params','')
            oAction.uRequestType  = oAction.dActionPars.get('requesttype','POST')
            oAction.uHeaders      = oAction.dActionPars.get('headers','{}')
            oAction.uProtocol     = oAction.dActionPars.get('protocol','http://')
            oAction.iCodeOK       = ToInt(oAction.dActionPars.get('codeok','200'))

        def OnError(self,request,error) -> None:
            if self.bIgnoreTimeOut:
                if str(error)=='timed out':
                    return
            if self.bIsConnected:
                self.ShowError(uMsg='Error Receiving Response (Error)',oException=error)
            self.oInterFace.bStopWait      = True
        def OnFailure(self,request,result) -> None:
            self.ShowError(uMsg='Error Receiving Response (Failure)')
            self.oInterFace.bStopWait      = True
        def OnReceive(self,oRequest,oResult) -> None:
            self.ShowDebug(uMsg='Received Response:'+ToUnicode(oResult))
            self.oInterFace.bStopWait      = True
        def Disconnect(self) -> bool:

            if not self.bIsConnected:
                return super().Disconnect()
            try:
                tRet = self.ExecuteStandardAction(uActionName='logoff')
                return super().Disconnect()
            except Exception as e:
                self.ShowError(uMsg='Cannot diconnect:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,oException=e)
                return super().Disconnect()

        def Connect(self) -> bool:

            if self.bInConnect:
                return True

            bRet=True
            if not super().Connect():
                return False
            try:
                self.bInConnect   = True
                self.bIsConnected = True
                tRet= self.ExecuteStandardAction('logon')
                self.bInConnect = False
                if type(tRet)==tuple:
                    # noinspection PyUnresolvedReferences
                    iStatusCode, uRes = tRet[0],tRet[1]
                elif type(tRet)==int:
                    iStatusCode=tRet
                else:
                    iStatusCode=0

                # self.bIsConnected = (iStatusCode == 200)
                self.bIsConnected = (iStatusCode == 0)
                if not self.bIsConnected:
                    self.ShowDebug(uMsg='Auth. failed:'+self.oInterFace.uResponse )
                    self.ShowError(uMsg='Cannot connect:' + self.aIniSettings.uHost + ':' + self.aIniSettings.uPort)

                return self.bIsConnected

            except Exception as e:
                self.ShowError(uMsg='Can\'t connect:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,oException=e)
                self.bOnError=True
                return False

    def __init__(self):
        cInterFaceSettings=self.cInterFaceSettings
        super().__init__()
        self.dSettings:Dict                             = {}
        self.oSetting:Optional[cInterFaceSettings]      = None
        self.uResponse:str                              = ''
        self.oReq                                       = None
        self.bStopWait:bool                             = False
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

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        super().SendCommand(oAction=oAction,oSetting=oSetting,uRetVar=uRetVar,bNoLogOut=bNoLogOut)

        iTryCount:int    = 0
        eRet:eReturnCode = eReturnCode.Error

        oSetting.uRetVar=uRetVar

        if uRetVar!='':
            oAction.uGlobalDestVar=uRetVar

        while iTryCount<self.iMaxTryCount:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                try:
                    iStatusCode, uRes = self.SendCommand_Helper(oAction,oSetting,self.uObjectName)
                    if iStatusCode == oAction.iCodeOK:
                        eRet = eReturnCode.Success
                        self.ShowDebug(uMsg=f'Sending Command succeeded: : {iStatusCode:d}', uParConfigName=oSetting.uConfigName)
                        break
                    elif iStatusCode == 0:
                        eRet = eReturnCode.Unknown
                        self.ShowWarning(uMsg=f'Sending Command: Response should be {oAction.iCodeOK:d}, maybe error, maybe success: {iStatusCode:d} [{uRes}]', uParConfigName=oSetting.uConfigName)
                        break
                    else:
                        eRet = eRet.Error
                        oSetting.bIsConnected=False
                        self.ShowError(uMsg=f'Sending Command failed: {iStatusCode:d} [{ToUnicode(uRes)}]', uParConfigName=oSetting.uConfigName)
                except Exception as e:
                    self.ShowError(uMsg='Can\'t send message',uParConfigName=oSetting.uConfigName,oException=e)
                    eRet = eReturnCode.Error
            else:
                if iTryCount==self.iMaxTryCount:
                    self.ShowWarning(uMsg=f'Nothing done,not connected! ->[{oAction.uActionName}]', uParConfigName=oSetting.uConfigName)
                oSetting.bIsConnected=False

        self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet

    def NewWait(self,delay:float) -> None:

        #Replacement of the buggy UrlRequest wait function

        while self.oReq.resp_status is None:
            self.oReq._dispatch_result(delay)
            sleep(delay)
            if self.bStopWait:
                self.bStopWait=False
                break

    # noinspection PyUnresolvedReferences
    def SendCommand_Helper(self,oAction:cAction,oSetting:cInterFaceSettings,uObjectName:str) -> Tuple[int,str]:

        iRet = None
        self.uResponse      = ''

        uUrlFull= oAction.uProtocol+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort+oAction.uCmd
        uUrlFull= ReplaceVars(uUrlFull,uObjectName+'/'+oSetting.uConfigName)
        uUrlFull= ReplaceVars(uUrlFull)

        oSetting.SetContextVar(uVarName='Host',uVarValue=oSetting.aIniSettings.uHost)
        oSetting.SetContextVar(uVarName='Port',uVarValue=oSetting.aIniSettings.uPort)
        oSetting.SetContextVar(uVarName='User',uVarValue=oSetting.aIniSettings.uUser)
        oSetting.SetContextVar(uVarName='Password',uVarValue=oSetting.aIniSettings.uPassword)

        sAuth = ''

        #self.register_app('http://'+oAction.uHost,oSetting)
        #self.register_app(uUrlFull,oSetting)

        try:
            uData = oAction.uParams
            uData = ReplaceVars(uData,uObjectName+'/'+oSetting.uConfigName)
            uData = ReplaceVars(uData)

            # we do nothing special on soap actions
            if oAction.uType=='soap':
                pass

            # we do nothing special on plain string actions
            if oAction.uType=='string':
                pass

            if oAction.uType=='none':
                return -1,""

            if oAction.uType=='encode':
                uData = urllib.parse.urlencode(uData)

            uData = ReplaceVars(uData,uObjectName+'/'+oSetting.uConfigName)
            uData = ReplaceVars(uData)

            SetVar(uVarName = 'datalenght', oVarValue = ToUnicode(len(uData)), uContext =  uObjectName+'/'+oSetting.uConfigName)

            if oAction.uActionName=='logon' or True:
                # base64 encode the username and password
                uTmp = ReplaceVars(f'{"$cvar(CONTEXT_USER)"}:{"$cvar(CONTEXT_PASSWORD)"}', uObjectName + '/' + oSetting.uConfigName)
                bTmp  = ToBytes(uTmp)
                #bTmp  = base64.encodestring(bTmp)
                # noinspection PyUnresolvedReferences
                bTmp = base64.encodebytes(bTmp)
                uTmp  = bTmp.decode( 'utf-8')
                sAuth = uTmp.replace('\n', '')
                #sAuth = base64.encodestring(bTmp).replace('\n', '')

            #construct and send the header
            uHeader = oAction.uHeaders
            uHeader = ReplaceVars(uHeader,uObjectName+'/'+oSetting.uConfigName)
            uHeader = ReplaceVars(uHeader)
            uHeader = ReplaceVars(uHeader,uObjectName+'/'+oSetting.uConfigName)

            aHeader = ToDic(uHeader)
            for uKey in aHeader:
                if isinstance(aHeader[uKey],str):
                    aHeader[uKey]=UnEscapeUnicode(aHeader[uKey])

            if not sAuth == '':
                aHeader['Authorization'] = 'Basic %s' % sAuth

            self.ShowInfo(uMsg=f'Sending Command [{oAction.uActionName}]: {uData} {UnEscapeUnicode(uHeader)} to {uUrlFull}', uParConfigName=oSetting.uConfigName)

            if not oAction.bWaitForResponse:
                oSetting.bIgnoreTimeOut=True
                fTimeOut=0.02
            else:
                oSetting.bIgnoreTimeOut=False
                fTimeOut=oSetting.aIniSettings.fTimeOut

            #todo: remove
            fTimeOut=30.0

            self.bStopWait = False
            self.oReq = UrlRequest(uUrlFull,method=oAction.uRequestType,req_body=uData, req_headers=aHeader,timeout=fTimeOut,on_error=oSetting.OnError,on_success=oSetting.OnReceive,debug=True)
            if oAction.bWaitForResponse:
                self.NewWait(0.05)
                if self.oReq.resp_status is not None:
                    self.ParseResult(oAction,self.oReq.result,oSetting)
                    iRet=self.oReq.resp_status
                    self.uResponse = self.oReq.result
                else:
                    if self.oReq._error is not None:
                        self.uResponse = ToUnicode(self.oReq._error)
                        if hasattr(self.oReq,'_error'):
                            iRet=self.oReq._error.errno
                        else:
                            iRet=0
                if iRet is None:
                    iRet=200
                if self.uResponse is None:
                    self.uResponse ="unknown"
                return iRet,self.uResponse
            else:
                return 200,''

        except Exception as e:
            self.ShowError(uMsg='Can\'t send message #2' ,uParConfigName=oSetting.uConfigName,oException=e)

        return -1,''

