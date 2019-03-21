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

'''

 Parts of the code based on the project

 https://github.com/google/python-adb/

'''

import  imp

from kivy.clock             import Clock
from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
from ORCA.vars.Replace      import ReplaceVars
from ORCA.vars.Access       import SetVar
from ORCA.vars.Access       import GetVar
from ORCA.utils.FileName    import cFileName

'''
<root>
  <repositorymanager>
    <entry>
      <name>Android adb</name>
      <description language='English'>Interface control Android devices by adb (TCP/IP)</description>
      <description language='German'>Interface um Android Geräte per adb (TCP/IP) zu steuern</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
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
        <file>android_adb/interface.pyc</file>
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
            self.aInterFaceIniSettings.uPort                       = u"5555"
            self.aInterFaceIniSettings.uFNCodeset                  = u"CODESET_android_adb_DEFAULT.xml"
            self.aInterFaceIniSettings.fTimeOut                    = 2.0
            self.aInterFaceIniSettings.iTimeToClose                = -1
            self.aInterFaceIniSettings.uDiscoverScriptName         = u"discover_upnp"
            self.aInterFaceIniSettings.uParseResultOption          = u'store'
            self.aInterFaceIniSettings.fDISCOVER_UPNP_timeout      = 5.0
            self.aInterFaceIniSettings.uDISCOVER_UPNP_models       = u"[]"
            self.aInterFaceIniSettings.uDISCOVER_UPNP_servicetypes = "urn:dial-multiscreen-org:service:dial:1"
            self.aInterFaceIniSettings.uDISCOVER_UPNP_manufacturer = ""
            self.aInterFaceIniSettings.uDISCOVER_UPNP_prettyname   = ""

            # Load the helper
            oFn_Adb_Helper = cFileName(self.oInterFace.oPathMyCode) + u'adb_helper.py'
            oModule = imp.load_source('adb_helper' , oFn_Adb_Helper.string)
            self.oDevice = oModule.cADB_Helper()

        def ReadAction(self,oAction):
            cBaseInterFaceSettings.ReadAction(self,oAction)
            oAction.uParams      = oAction.dActionPars.get(u'params',u'')
        def Disconnect(self):
            if not self.bIsConnected:
                return cBaseInterFaceSettings.Disconnect(self)
            try:
                self.oDevice.Close()
                return cBaseInterFaceSettings.Disconnect(self)
            except Exception as e:
                self.ShowError(u'Cannot diconnect:'+self.aInterFaceIniSettings.uHost+':'+self.aInterFaceIniSettings.uPort,e)
                return cBaseInterFaceSettings.Disconnect(self)

        def Connect(self):

            bRet=True
            if not cBaseInterFaceSettings.Connect(self):
                return False

            if self.aInterFaceIniSettings.uHost=='':
                return False

            try:
                self.oDevice.Connect(uHost=self.aInterFaceIniSettings.uHost, uPort=self.aInterFaceIniSettings.uPort,fTimeOut=self.aInterFaceIniSettings.fTimeOut)
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
        self.aSettings              = {}
        self.oSetting               = None
        self.aDiscoverScriptsBlackList = ["iTach (Global Cache)","Keene Kira"]

    def Init(self,uInterFaceName,uInterFaceFile=u''):
        cBaseInterFace.Init(self,uInterFaceName,uInterFaceFile)
        self.oInterFaceConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oInterFaceConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oInterFaceConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oInterFaceConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oInterFaceConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self,**kwargs):
        cBaseInterFace.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        iTryCount=0
        iRet=1

        if oAction.dActionPars.get('commandname') == "send_string":
            uTmpVar  = GetVar(uVarName = 'inputstring')
            uTmpVar2 = uTmpVar
            uTmpVar  = uTmpVar.replace(" ","%s")
            SetVar(uVarName = 'inputstring',oVarValue = uTmpVar)

        uRetVar = ReplaceVars(uRetVar)
        oSetting.uRetVar=uRetVar

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        uParams = ReplaceVars(oAction.uParams)
        uParams = ReplaceVars(uParams,self.uInterFaceName+'/'+oSetting.uConfigName)

        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()
            if oSetting.bIsConnected:
                try:
                    self.ShowDebug("Sending adb command: %s:%s" % (oAction.uCmd,uParams))
                    oMethod = getattr(oSetting.oDevice.oADB_Commands, oAction.uCmd)
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
                    self.ShowError(u'can\'t Send Message',oSetting.uConfigName,e)
                    iRet=1
            else:
                oSetting.bIsConnected=False

        if oAction.dActionPars.get('commandname') =="send_string":
            SetVar(uVarName = 'inputstring', oVarValue = uTmpVar2)

        self.iLastRet=iRet

        if not bNoLogOut:
            if oSetting.aInterFaceIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aInterFaceIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aInterFaceIniSettings.iTimeToClose)
        return iRet













