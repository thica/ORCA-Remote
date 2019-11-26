# -*- coding: utf-8 -*-


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

from __future__ import annotations

from typing import Dict
from typing import List
from typing import Union
from typing import Callable


import re
import select
import socket
import struct
import threading
from time                                   import sleep

from kivy.clock                             import Clock
from kivy.logger                            import Logger
from kivy.uix.button                        import Button

from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.vars.QueryDict                    import QueryDict
from ORCA.utils.FileName                    import cFileName

'''
<root>
  <repositorymanager>
    <entry>
      <name>iTach Discover</name>
      <description language='English'>Discover iTach devices</description>
      <description language='German'>Erkennt sucht iTach Geräte über beacon</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_itach</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_itach.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cScript(cDiscoverScriptTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-Discover-iTach
    WikiDoc:TOCTitle:Discover Itach
    = Script Discover iTach =

    The iTach discover script discover iTach Infrared transmitter devices. Not reliable by now.

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |timeout
    |Specifies the timout for discover
    |}</div>

    WikiDoc:End
    """
    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript:cScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aIniSettings.fTimeOut = 30.0

    def __init__(self):
        cDiscoverScriptTemplate.__init__(self)
        self.fTimeOut:float             = 30
        self.uSubType:str               = u'iTach (Global Cache)'
        self.aiTachDevices:dict         = {}
        self.oThread                    = None
        self.iDiscoverCount:int         = 0
        self.iMaxDiscoverCount:int      = 3
        self.oDiscoverObject            = ciTachDiscover(self.aiTachDevices,self)
    def __del__(self):
        self.StopThread([])

    def DeInit(self,**kwargs) -> None:
        super(cScript, self).DeInit(**kwargs)
        self.StopThread([])

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """

        cDiscoverScriptTemplate.Init(self, uObjectName, oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.StartThread()

    def StartThread(self) -> None:
        if self.iDiscoverCount < self.iMaxDiscoverCount:
            self.iDiscoverCount = self.iDiscoverCount+1
            # noinspection PyTypeChecker
            self.oThread =  FuncThread(self.oDiscoverObject.Run,self.fTimeOut)
            self.oThread.start()
            Clock.schedule_once(self.StopThread, int(self.fTimeOut))

    # noinspection PyUnusedLocal
    def StopThread(self,*largs) -> None:
        if self.oThread:
            self.oDiscoverObject.Close()

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(5034)','$lvar(5031)','Revision']

    def ListDiscover(self) -> None:

        oSetting:cBaseScriptSettings = self.GetSettingObjectForConfigName(uConfigName=self.uConfigName)

        if len(self.aiTachDevices)==0:
            sleep(oSetting.aIniSettings.fTimeOut)

        for oDeviceKey in self.aiTachDevices:
            oDevice=self.aiTachDevices[oDeviceKey]
            self.AddLine([oDevice.uIP , oDevice.uUUID , oDevice.uModel ,oDevice.uRevision ],oDevice)

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:QueryDict = oButton.dDevice

        uText=  u"$lvar(5029): %s \n"\
                u"$lvar(5034): %s \n"\
                u"$lvar(5031): %s \n"\
                u"\n"\
                u"Revision: %s" % (dDevice.uIP,dDevice.uUUID,dDevice.uModel,dDevice.uRevision)

        ShowMessagePopUp(uMessage=uText)

    def Discover(self,**kwargs) -> Dict[str,str]:

        uConfigName:str = self.uConfigName
        if "configname" in kwargs:
            uConfigName = kwargs['configname']

        oSetting:cBaseScriptSettings = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut                     = oSetting.aIniSettings.fTimeOut

        if "timeout" in kwargs:
            fTimeOut = ToFloat(kwargs['timeout'])

        self.fTimeOut = fTimeOut

        if self.oThread is None:
            self.StartThread()

        if not self.oThread.is_alive():
            self.StartThread()

        iCount:int = self.fTimeOut*100
        while len(self.aiTachDevices)==0 and iCount > 0 and self.oThread.is_alive():
            sleep(0.01)
            iCount=iCount-1

        self.StopThread()
        if len(self.aiTachDevices)==0:
            return {"Host":""}
        else:
            uKey=self.aiTachDevices[0]
            return {"Host":self.aiTachDevices[uKey].uIP}

    def OnPause(self,**kwargs) -> None:
        cDiscoverScriptTemplate.OnPause(self)
        if self.oThread is not None:
            self.oDiscoverObject.Close()
    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return {"TimeOut":{"type": "numericfloat", "order":0,  "title": "$lvar(6019)", "desc": "$lvar(6020)","key": "timeout", "default":"2.0"}}


class FuncThread(threading.Thread):
    def __init__(self, target:Callable, *args:List):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args

    def run(self) -> None:
        self._target(*self._args)

class ciTachDiscover:

    def __init__(self,dDevices:Dict, cScriptClass:cScript):
        self.dDevices:Dict          = dDevices
        self.cScript:cScript        = cScriptClass
        self.oSocket:socket.socket  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bStopThreadEvent:bool  = False
    def Run(self,*args) -> None:

        self.bStopThreadEvent = False

        fTimeOut = args[0]

        Logger.debug (u'iTach Start Discover Thread')

        p = re.compile((r'AMXB<-UUID=GlobalCache_(?P<UUID>.{12}).+'
                        r'Model=iTach(?P<Model>.+?)>.+'
                        r'Revision=(?P<Revision>.+?)>.+'
                        r'Config-URL=http://(?P<IP>.+?)>.+'
                        r'PCB_PN=(?P<PN>.+?)>.+'
                        r'Status=(?P<Status>.+?)>'))

        try:
            self.oSocket.settimeout(fTimeOut)
            self.oSocket.bind(('', 9131))
            group = socket.inet_aton('239.255.250.250')
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.oSocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except Exception as e:
            self.cScript.ShowError("iTach-Discover -3: Error occured",oException= e)

        try:
            while not self.bStopThreadEvent:
                if self.oSocket is not None:
                    aReady:List = select.select([self.oSocket], [], [],int(fTimeOut))
                    # the first element of the returned list is a list of readable sockets
                    if aReady[0]:
                        byData:bytes = self.oSocket.recv(1024)
                        match = p.match(ToUnicode(byData))
                        if match:
                            diTachEntry=QueryDict()
                            diTachEntry.uIP         = match.group('IP')
                            diTachEntry.uUUID       = match.group('UUID')
                            diTachEntry.uModel      = match.group('Model')
                            diTachEntry.uRevision   = match.group('Revision')
                            diTachEntry.uPartNumber = match.group('PN')
                            diTachEntry.uStatus     = match.group('Status')

                            if not diTachEntry.uIP in self.dDevices:
                                self.dDevices[diTachEntry.uIP]=diTachEntry
                                Logger.info("iTach-Discover: iTach found! IP: %s, UUID:%s, Model:%s, Revision:%s, Part number:%s, Status:%s" % (diTachEntry.uIP , diTachEntry.uUUID , diTachEntry.uModel , diTachEntry.uRevision , diTachEntry.uPartNumber ,  diTachEntry.uStatus ))

        except socket.timeout:
            if len(self.dDevices)==0:
                Logger.debug("iTach-Discover: Could not find an iTach on the network")
        except Exception as e:
            self.cScript.ShowError("iTach-Discover: Error occured",oException=e)
        finally:
            Logger.debug (u'iTach-Discover: Stop Discover Thread')
            self.oSocket.close()
            return
    def Close(self):
        self.bStopThreadEvent=True

