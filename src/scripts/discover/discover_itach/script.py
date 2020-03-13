# -*- coding: utf-8 -*-


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

from __future__ import annotations

from typing import Dict
from typing import List
from typing import Union

import re
import select
import socket
import struct
import threading
from time                                   import sleep

from kivy.clock                             import Clock
from kivy.uix.button                        import Button

from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.vars.QueryDict                    import TypedQueryDict
from ORCA.utils.FileName                    import cFileName

import ORCA.Globals as Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>iTach Discover</name>
      <description language='English'>Discover iTach devices</description>
      <description language='German'>Erkennt sucht iTach Geräte über beacon</description>
      <author>Carsten Thielepape</author>
      <version>5.0.0</version>
      <minorcaversion>5.0.0</minorcaversion>
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
            super().__init__(oScript)
            self.aIniSettings.fTimeOut = 30.0

    def __init__(self):
        super().__init__()
        self.fTimeOut:float                         = 30
        self.uSubType:str                           = u'iTach (Global Cache)'
        self.aResults:List[TypedQueryDict]          = []
        self.aThreads:List[cThread_Discover_iTach]  = []
        self.iDiscoverCount:int                     = 0
        self.iMaxDiscoverCount:int                   = 3
        self.uIPVersion                             = u'IPv4Only'
        self.dReq:TypedQueryDict                    = TypedQueryDict()

    def __del__(self):
        self.StopThread([])

    def DeInit(self,**kwargs) -> None:
        super().DeInit(**kwargs)
        self.StopThread([])

    def Init(self,uObjectName:str,oFnScript:Union[cFileName,None]=None) -> None:
        """
        Init function for the script

        :param str uObjectName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """

        # iTach just send beacons to the network, so we start listening immediately

        super().Init(uObjectName=uObjectName, oFnObject=oFnScript)
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.StartThread()

    def StartThread(self) -> None:
        if self.iDiscoverCount < self.iMaxDiscoverCount:
            self.iDiscoverCount += 1
            if self.uIPVersion == "IPv4Only" or self.uIPVersion == "All" or (self.uIPVersion == "Auto" and Globals.uIPAddressV6 == ""):
                self.ShowInfo(uMsg="Start Discover Thread V4")
                oThread = cThread_Discover_iTach(dReq=self.dReq,uIPVersion=self.uIPVersion, fTimeOut=self.fTimeOut, oCaller=self)
                self.aThreads.append(oThread)
                self.aThreads[-1].start()
            Clock.schedule_once(self.StopThread, int(self.fTimeOut)*4)

    # noinspection PyUnusedLocal
    def StopThread(self,*largs) -> None:
        for oThread in self.aThreads:
            oThread.Close()

    def GetHeaderLabels(self) -> List[str]:
        return ['$lvar(5029)','$lvar(5034)','$lvar(5031)','Revision']

    def ListDiscover(self) -> None:

        oSetting:cBaseScriptSettings = self.GetSettingObjectForConfigName(uConfigName=self.uConfigName)

        if len(self.aResults)==0:
            sleep(oSetting.aIniSettings.fTimeOut)

        for dDevice in self.aResults:
            self.AddLine([dDevice.uIP , dDevice.uUUID , dDevice.uModel ,dDevice.uRevision ],dDevice)

    def CreateDiscoverList_ShowDetails(self,oButton:Button) -> None:

        dDevice:TypedQueryDict = oButton.dDevice

        uText=  u"$lvar(5029): %s \n"\
                u"$lvar(5034): %s \n"\
                u"$lvar(5031): %s \n"\
                u"\n"\
                u"Revision: %s" % (dDevice.uIP,dDevice.uUUID,dDevice.uModel,dDevice.uRevision)

        ShowMessagePopUp(uMessage=uText)

    def Discover(self,**kwargs) -> Dict[str,str]:


        uConfigName:str                 = kwargs.get('configname',self.uConfigName)
        oSetting:cBaseScriptSettings    = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        self.fTimeOut:float             = ToFloat(kwargs.get('timeout',oSetting.aIniSettings.fTimeOut))
        self.dReq.uModels               = kwargs.get('models',"")
        self.uIPVersion:str             = kwargs.get('ipversion',"IPv4Only")

        self.ShowDebug(uMsg=u'Try to discover iTach device')

        try:
            oThread:cThread_Discover_iTach
            if len(self.aThreads) == 0:
                self.StartThread()

            if not self.aThreads[0].is_alive():
                self.StartThread()

            for oT in self.aThreads:
                oT.join()

            if len(self.aResults)>0:
                return {"Host":self.aResults[0].uFoundIP}

            if len(self.aResults)>0:
                return {'Model': self.aResults[0].uFoundModel, 'Host': self.aResults[0].uFoundIP,'Port': self.aResults[0].uFoundPort, 'Category': self.aResults[0].uFoundCategory, 'Exception': None}
            else:
                self.ShowWarning(uMsg='No iTach device found')
        except Exception as e:
            self.ShowError(uMsg=u'No iTach device found, possible timeout',oException=e)

        return {"Host":""}


    def OnPause(self,**kwargs) -> None:
        cDiscoverScriptTemplate.OnPause(self)
        self.StopThread()

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults:Dict) -> Dict[str,Dict]:
        return {"TimeOut":{"type": "numericfloat", "order":0,  "title": "$lvar(6019)", "desc": "$lvar(6020)","key": "timeout", "default":"2.0"}}

class cThread_Discover_iTach(threading.Thread):
    oWaitLock = threading.Lock()

    def __init__(self, dReq:TypedQueryDict,uIPVersion:str, fTimeOut:float,oCaller:cScript):
        threading.Thread.__init__(self)
        self.uIPVersion:str         = uIPVersion
        self.oCaller:cScript        = oCaller
        self.fTimeOut:float         = fTimeOut
        self.dReq:TypedQueryDict    = dReq
        self.oSocket:socket.socket  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bStopThreadEvent:bool  = False

    def run(self) -> None:

        self.bStopThreadEvent = False
        self.oCaller.ShowDebug(uMsg=u'iTach Start Discover Thread')

        p = re.compile((r'AMXB<-UUID=GlobalCache_(?P<UUID>.{12}).+'
                        r'Model=iTach(?P<Model>.+?)>.+'
                        r'Revision=(?P<Revision>.+?)>.+'
                        r'Config-URL=http://(?P<IP>.+?)>.+'
                        r'PCB_PN=(?P<PN>.+?)>.+'
                        r'Status=(?P<Status>.+?)>'))

        try:
            self.oSocket.settimeout(self.fTimeOut)
            self.oSocket.bind(('', 9131))
            group = socket.inet_aton('239.255.250.250')
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.oSocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except Exception as e:
            self.oCaller.ShowError(uMsg=" -3: Error occured",oException= e)

        try:
            while not self.bStopThreadEvent:
                if self.oSocket is not None:
                    aReady:List = select.select([self.oSocket], [], [],int(self.fTimeOut))
                    # the first element of the returned list is a list of readable sockets
                    if aReady[0]:
                        byData:bytes = self.oSocket.recv(1024)
                        match = p.match(ToUnicode(byData))
                        if match:
                            diTachEntry             = TypedQueryDict()
                            diTachEntry.uIP         = match.group('IP')
                            diTachEntry.uUUID       = match.group('UUID')
                            diTachEntry.uModel      = match.group('Model')
                            diTachEntry.uRevision   = match.group('Revision')
                            diTachEntry.uPartNumber = match.group('PN')
                            diTachEntry.uStatus     = match.group('Status')
                            cThread_Discover_iTach.oWaitLock.acquire()
                            self.oCaller.aResults.append(diTachEntry)
                            cThread_Discover_iTach.oWaitLock.release()
                            self.oCaller.ShowInfo(uMsg="iTach-Discover: iTach found! IP: %s, UUID:%s, Model:%s, Revision:%s, Part number:%s, Status:%s" % (diTachEntry.uIP , diTachEntry.uUUID , diTachEntry.uModel , diTachEntry.uRevision , diTachEntry.uPartNumber ,  diTachEntry.uStatus ))
        except Exception as e:
            self.oCaller.ShowError(uMsg="Error occured",oException=e)
        finally:
            if len(self.oCaller.aResults)==0:
                self.oCaller.ShowDebug (uMsg=u'Stop Discover Thread, nothing found')
            else:
                self.oCaller.ShowDebug (uMsg=u'Stop Discover Thread, device(s) found')
            self.oSocket.close()
            return
    def Close(self):
        self.bStopThreadEvent=True

