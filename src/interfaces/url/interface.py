# -*- coding: utf-8 -*-
# url

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

from __future__                            import annotations
from typing                                import Dict
from typing                                import Tuple
from typing                                import Union

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
from ORCA.utils.FileName                   import cFileName
from ORCA.Action                           import cAction
from ORCA.actions.ReturnCode               import eReturnCode

'''
<root>
  <repositorymanager>
    <entry>
      <name>URL-Web</name>
      <description language='English'>Interface to send web based commands</description>
      <description language='German'>Interface um webbasierte Kommandos zu senden</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
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
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.bIgnoreTimeOut                           = False
            self.aIniSettings.uHost                       = u"discover"
            self.aIniSettings.uPort                       = u"80"
            self.aIniSettings.uFNCodeset                  = u"Select"
            self.aIniSettings.fTimeOut                    = 2.0
            self.aIniSettings.iTimeToClose                = -1
            self.aIniSettings.uDiscoverScriptName         = u"discover_upnp"
            self.aIniSettings.uParseResultOption          = u'no'
            self.aIniSettings.fDISCOVER_UPNP_timeout      = 2.0
            self.aIniSettings.uDISCOVER_UPNP_models       = u"[]"
            self.aIniSettings.uDISCOVER_UPNP_servicetypes = "urn:dial-multiscreen-org:service:dial:1,urn:schemas-upnp-org:service:AVTransport:1"
            self.aIniSettings.uDISCOVER_UPNP_manufacturer = ""
            self.aIniSettings.uDISCOVER_UPNP_prettyname   = ""

        def ReadAction(self,oAction:cAction) -> None:
            cBaseInterFaceSettings.ReadAction(self,oAction)
            oAction.uParams      = oAction.dActionPars.get(u'params',u'')
            oAction.uRequestType = oAction.dActionPars.get(u'requesttype',u'POST')
            oAction.uHeaders     = oAction.dActionPars.get(u'headers',u'{}')
            oAction.uProtocol    = oAction.dActionPars.get(u'protocol',u'http://')


        def OnError(self,request,error) -> None:
            if self.bIgnoreTimeOut:
                if str(error)=="timed out":
                    return
            if self.bIsConnected:
                self.ShowError(u'Error Receiving Response (Error)',error)
            self.oInterFace.bStopWait      = True
        def OnFailure(self,request,result) -> None:
            self.ShowError(u'Error Receiving Response (Failure)')
            self.oInterFace.bStopWait      = True
        def OnReceive(self,oRequest,oResult) -> None:
            self.ShowDebug(u'Received Response:'+ToUnicode(oResult))
            self.oInterFace.bStopWait      = True
        def Disconnect(self) -> bool:

            if not self.bIsConnected:
                return cBaseInterFaceSettings.Disconnect(self)
            try:
                tRet = self.ExecuteStandardAction('logoff')
                return cBaseInterFaceSettings.Disconnect(self)
            except Exception as e:
                self.ShowError(u'Cannot diconnect:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                return cBaseInterFaceSettings.Disconnect(self)

        def Connect(self) -> bool:

            if self.bInConnect:
                return True

            bRet=True
            if not cBaseInterFaceSettings.Connect(self):
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
                    self.ShowDebug(u'Auth. failed:'+self.oInterFace.uResponse )
                    self.ShowError(u'Cannot connect:' + self.aIniSettings.uHost + ':' + self.aIniSettings.uPort)

                return self.bIsConnected

            except Exception as e:
                self.ShowError(u'Cannot connect:'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.bOnError=True
                return False

    def __init__(self):
        cInterFaceSettings=self.cInterFaceSettings
        cBaseInterFace.__init__(self)
        self.dSettings:Dict                             = {}
        self.oSetting:Union[cInterFaceSettings,None]    = None
        self.uResponse:str                              = u''
        self.oReq                                       = None
        self.bStopWait:bool                             = False
        self.iWaitMs:int                               = 2000

    def Init(self, uObjectName: str, oFnObject: Union[cFileName,None] = None) -> None:
        cBaseInterFace.Init(self, uObjectName, oFnObject)

        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['User']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Password']['active']                    = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['ParseResult']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['TokenizeString']['active']              = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
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

        iTryCount:int    = 0
        eRet:eReturnCode = eReturnCode.Error

        oSetting.uRetVar=uRetVar

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                try:
                    iStatusCode, uRes = self.SendCommand_Helper(oAction,oSetting,self.uObjectName)
                    if iStatusCode == 200:
                        eRet = eReturnCode.Success
                        self.ShowDebug(u'Sending Command succeeded: : %d' % iStatusCode, oSetting.uConfigName)
                        break
                    elif iStatusCode == 0:
                        eRet = eReturnCode.Unknown
                        self.ShowWarning(u'Sending Command: Response should be 200, maybe error, maybe success: %d [%s]' % (iStatusCode,uRes),oSetting.uConfigName)
                        break
                    else:
                        eRet = eRet.Error
                        oSetting.bIsConnected=False
                        self.ShowError(u'Sending Command failed: %d [%s]' % (iStatusCode,ToUnicode(uRes)),oSetting.uConfigName)
                except Exception as e:
                    self.ShowError(uMsg=u'can\'t Send Message',uParConfigName=oSetting.uConfigName,oException=e)
                    eRet = eReturnCode.Error
            else:
                if iTryCount==2:
                    self.ShowWarning(u'Nothing done,not connected! ->[%s]' % oAction.uActionName, oSetting.uConfigName)
                oSetting.bIsConnected=False

        self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet

    def NewWait(self,delay:float) -> None:

        #Replacement of the buggy UrlRquest wait function

        while self.oReq.resp_status is None:
            self.oReq._dispatch_result(delay)
            sleep(delay)
            if self.bStopWait:
                self.bStopWait=False
                break

    # noinspection PyUnresolvedReferences
    def SendCommand_Helper(self,oAction:cAction,oSetting:cInterFaceSettings,uObjectName:str) -> Tuple[int,str]:

        iRet = None
        self.uResponse      = u''

        uUrlFull= oAction.uProtocol+oSetting.aIniSettings.uHost+":"+oSetting.aIniSettings.uPort+oAction.uCmd
        uUrlFull= ReplaceVars(uUrlFull,uObjectName+u'/'+oSetting.uConfigName)
        uUrlFull= ReplaceVars(uUrlFull)

        # oSetting.SetContextVar('Host',oSetting.aIniSettings.uHost)
        # oSetting.SetContextVar('Port',oSetting.aIniSettings.uPort)
        sAuth = u''

        #self.register_app('http://'+oAction.uHost,oSetting)
        #self.register_app(uUrlFull,oSetting)

        try:
            uData = oAction.uParams
            uData = ReplaceVars(uData,uObjectName+u'/'+oSetting.uConfigName)
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

            uData = ReplaceVars(uData,uObjectName+u'/'+oSetting.uConfigName)
            uData = ReplaceVars(uData)

            SetVar(uVarName = 'datalenght', oVarValue = ToUnicode(len(uData)), uContext =  uObjectName+u'/'+oSetting.uConfigName)

            if oAction.uActionName=='logon' or True:
                # base64 encode the username and password
                uTmp = ReplaceVars('%s:%s' % ('$cvar(CONTEXT_USER)','$cvar(CONTEXT_PASSWORD)'),uObjectName+u'/'+oSetting.uConfigName)
                bTmp  = ToBytes(uTmp)
                #bTmp  = base64.encodestring(bTmp)
                # noinspection PyUnresolvedReferences
                bTmp = base64.encodebytes(bTmp)
                uTmp  = bTmp.decode( 'utf-8')
                sAuth = uTmp.replace('\n', '')
                #sAuth = base64.encodestring(bTmp).replace('\n', '')
            #construct and send the header
            uHeader = oAction.uHeaders
            uHeader = ReplaceVars(uHeader,uObjectName+u'/'+oSetting.uConfigName)
            uHeader = ReplaceVars(uHeader)
            uHeader = ReplaceVars(uHeader,uObjectName+u'/'+oSetting.uConfigName)

            aHeader = ToDic(uHeader)
            for uKey in aHeader:
                if isinstance(aHeader[uKey],str):
                    aHeader[uKey]=UnEscapeUnicode(aHeader[uKey])

            if not sAuth == u'':
                aHeader['Authorization'] = "Basic %s" % sAuth

            self.ShowInfo(u'Sending Command [%s]: %s %s to %s' % (oAction.uActionName,uData,UnEscapeUnicode(uHeader),uUrlFull),oSetting.uConfigName)

            if not oAction.bWaitForResponse:
                oSetting.bIgnoreTimeOut=True
                fTimeOut=0.02
            else:
                oSetting.bIgnoreTimeOut=False
                fTimeOut=oSetting.aIniSettings.fTimeOut

            self.bStopWait = False
            self.oReq = UrlRequest(uUrlFull,method=oAction.uRequestType,req_body=uData, req_headers=aHeader,timeout=fTimeOut,on_error=oSetting.OnError,on_success=oSetting.OnReceive,debug=False)
            if oAction.bWaitForResponse:
                self.NewWait(0.05)
                if self.oReq.resp_status is not None:
                    self.ParseResult(oAction,self.oReq.result,oSetting)
                    iRet=self.oReq.resp_status
                    self.uResponse = self.oReq.result
                else:
                    if self.oReq._error is not None:
                        self.uResponse = str(self.oReq._error)
                        iRet=self.oReq._error.errno
                if iRet is None:
                    iRet=200
                if self.uResponse is None:
                    self.uResponse ="unknown"
                return iRet,self.uResponse
            else:
                return 200,''

        except Exception as e:
            self.ShowError(uMsg=u'can\'t Send Message #2' ,uParConfigName=oSetting.uConfigName,oException=e)

        return -1,''

