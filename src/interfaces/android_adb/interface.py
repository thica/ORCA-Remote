# -*- coding: utf-8 -*-
# android_adb

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

from __future__                             import annotations
from typing                                 import TYPE_CHECKING
from typing                                 import Dict
from typing                                 import List
from typing                                 import Union
from ORCA.interfaces.BaseInterface          import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings  import cBaseInterFaceSettings
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.vars.Access                       import SetVar
from ORCA.vars.Access                       import GetVar
from ORCA.utils.FileName                    import cFileName
from ORCA.Action                            import cAction
from ORCA.actions.ReturnCode                import eReturnCode

import ORCA.Globals as Globals

'''

 Parts of the code based on the project

 https://github.com/google/python-adb/

'''


'''
<root>
  <repositorymanager>
    <entry>
      <name>Android adb</name>
      <description language='English'>Interface control Android devices by adb (TCP/IP)</description>
      <description language='German'>Interface um Android Geräte per adb (TCP/IP) zu steuern</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/android_adb</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/android_adb.zip</sourcefile>
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
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.aIniSettings.uHost                       = u"discover"
            self.aIniSettings.uPort                       = u"5555"
            self.aIniSettings.uFNCodeset                  = u"CODESET_android_adb_DEFAULT.xml"
            self.aIniSettings.fTimeOut                    = 2.0
            self.aIniSettings.iTimeToClose                = -1
            self.aIniSettings.uDiscoverScriptName         = u"discover_upnp"
            self.aIniSettings.uParseResultOption          = u'store'
            self.aIniSettings.fDISCOVER_UPNP_timeout      = 5.0
            self.aIniSettings.uDISCOVER_UPNP_models       = u"[]"
            self.aIniSettings.uDISCOVER_UPNP_servicetypes = "urn:dial-multiscreen-org:service:dial:1"
            self.aIniSettings.uDISCOVER_UPNP_manufacturer = ""
            self.aIniSettings.uDISCOVER_UPNP_prettyname   = ""

            # Load the helper
            if TYPE_CHECKING:
                from interfaces.android_adb.adb_helper import cADB_Helper
                self.oDevice = cADB_Helper()
            else:
                oFn_Adb_Helper = cFileName(self.oInterFace.oPathMyCode) + u'adb_helper.py'
                oModule = Globals.oModuleLoader.LoadModule(oFn_Adb_Helper,'adb_helper')
                self.oDevice = oModule.GetClass("cADB_Helper")()

        def ReadAction(self,oAction:cAction) -> None:
            cBaseInterFaceSettings.ReadAction(self,oAction)
            oAction.uParams      = oAction.dActionPars.get(u'params',u'')

        def Disconnect(self) -> bool:
            if not self.bIsConnected:
                return cBaseInterFaceSettings.Disconnect(self)
            try:
                self.oDevice.Close()
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
                self.oDevice.Connect(uHost=self.aIniSettings.uHost, uPort=self.aIniSettings.uPort,fTimeOut=self.aIniSettings.fTimeOut)
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
        cInterFaceSettings = self.cInterFaceSettings
        cBaseInterFace.__init__(self)
        self.dSettings:Dict                             = {}
        self.oSetting:Union[cInterFaceSettings,None]    = None
        self.aDiscoverScriptsBlackList:List[str]        = ["iTach (Global Cache)","Keene Kira","ELVMAX"]

    def Init(self, uObjectName:str, oFnObject:Union[cFileName,None]=None) -> None:
        """ Initialisizes the Interface

        :param str uObjectName: unicode : Name of the interface
        :param cFileName oFnObject: The Filename of the interface
        """

        cBaseInterFace.Init(self,uObjectName,oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self,**kwargs) -> None:
        cBaseInterFace.DeInit(self,**kwargs)
        for uSettingName in self.dSettings:
            self.dSettings[uSettingName].DeInit()

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        iTryCount:int    = 0
        eRet:eReturnCode = eReturnCode.Success
        uTmpVar2:str     = u""

        if oAction.dActionPars.get('commandname') == "send_string":
            uTmpVar:str  = GetVar(uVarName = 'inputstring')
            uTmpVar2:str = uTmpVar
            uTmpVar      = uTmpVar.replace(" ","%s")
            SetVar(uVarName = 'inputstring',oVarValue = uTmpVar)

        uRetVar:str = ReplaceVars(uRetVar)
        oSetting.uRetVar=uRetVar

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        # noinspection PyUnresolvedReferences
        uParams:str = ReplaceVars(oAction.uParams)
        uParams     = ReplaceVars(uParams,self.uObjectName+'/'+oSetting.uConfigName)

        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                try:
                    self.ShowDebug("Sending adb command: %s:%s" % (oAction.uCmd,uParams))
                    oMethod = getattr(oSetting.oDevice, oAction.uCmd)
                    oResult = oMethod(uParams)
                    uCmd,uRetVal=self.ParseResult(oAction,oResult,oSetting)
                    self.ShowDebug(u'Parsed Resonse:'+uRetVal)
                    if not uRetVar==u'':
                        uRetVal=uRetVal.replace("\n","")
                        uRetVal=uRetVal.replace("\r","")
                        SetVar(uVarName = uRetVar, oVarValue = uRetVal)

                    self.ShowDebug("Result:"+str( oResult))
                    break
                except Exception as e:
                    self.ShowError(uMsg=u'can\'t Send Message',uParConfigName=oSetting.uConfigName,oException=e)
                    eRet=eReturnCode.Error
            else:
                oSetting.bIsConnected=False

        if oAction.dActionPars.get('commandname') =="send_string":
            SetVar(uVarName = 'inputstring', oVarValue = uTmpVar2)

        self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet
