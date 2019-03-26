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

import re
import select
import socket
import struct
import threading
from time                                   import sleep

from kivy.clock                             import Clock
from kivy.logger                            import Logger

from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.vars.QueryDict                    import QueryDict

'''
<root>
  <repositorymanager>
    <entry>
      <name>iTach Discover</name>
      <description language='English'>Discover iTach devices</description>
      <description language='German'>Erkennt sucht iTach Geräte über beacon</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_itach</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_itach.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/discover/discover_itach/script.pyc</file>
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
        def __init__(self,oScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aScriptIniSettings.fTimeOut                     = 30.0

    def __init__(self):
        cDiscoverScriptTemplate.__init__(self)
        self.fTimeOut             = 30
        self.uSubType             = u'iTach (Global Cache)'
        self.aiTachDevices        = {}
        self.oThread              = None
        self.iDiscoverCount       = 0
        self.iMaxDiscoverCount    = 3
        self.oDiscoverObject      = ciTachDiscover(self.aiTachDevices,self)
    def __del__(self):
        self.StopThread([])

    def DeInit(self,**kwargs):
        super(cScript, self).DeInit(**kwargs)
        self.StopThread([])

    def Init(self,uScriptName,oFnScript=None):
        """
        Init function for the script

        :param string uScriptName: The name of the script (to be passed to all scripts)
        :param cFileName oFnScript: The file of the script (to be passed to all scripts)
        """

        cDiscoverScriptTemplate.Init(self, uScriptName, oFnScript)
        self.oScriptConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.StartThread()

    def StartThread(self):
        if self.iDiscoverCount < self.iMaxDiscoverCount:
            self.iDiscoverCount = self.iDiscoverCount+1
            self.oThread =  FuncThread(self.oDiscoverObject.Run,self.fTimeOut)
            self.oThread.start()
            Clock.schedule_once(self.StopThread, int(self.fTimeOut))

    def StopThread(self,*largs):
        if self.oThread:
            self.oDiscoverObject.Close()

    def GetHeaderLabels(self):
        return ['$lvar(5029)','$lvar(5034)','$lvar(5031)','Revision']

    def ListDiscover(self):

        oSetting = self.GetSettingObjectForConfigName(uConfigName=self.uConfigName)

        if len(self.aiTachDevices)==0:
            sleep(oSetting.aScriptIniSettings.fTimeOut)

        for oDeviceKey in self.aiTachDevices:
            oDevice=self.aiTachDevices[oDeviceKey]
            self.AddLine([oDevice.uIP , oDevice.uUUID , oDevice.uModel ,oDevice.uRevision ],oDevice)

    def CreateDiscoverList_ShowDetails(self,instance):
        uText=  u"$lvar(5029): %s \n"\
                u"$lvar(5034): %s \n"\
                u"$lvar(5031): %s \n"\
                u"\n"\
                u"Revision: %s" % (instance.oDevice.uIP,instance.oDevice.uUUID,instance.oDevice.uModel,instance.oDevice.uRevision)

        ShowMessagePopUp(uMessage=uText)

    def Discover(self,**kwargs):

        uConfigName = self.uConfigName
        if "configname" in kwargs:
            uConfigName = kwargs['configname']

        oSetting = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut = oSetting.aScriptIniSettings.fTimeOut

        if "timeout" in kwargs:
            fTimeOut = ToFloat(kwargs['timeout'])

        self.fTimeOut = fTimeOut

        if self.oThread is None:
            self.StartThread()

        if not self.oThread.is_alive():
            self.StartThread()

        iCount=self.fTimeOut*100
        while len(self.aiTachDevices)==0 and iCount > 0 and self.oThread.is_alive():
            sleep(0.01)
            iCount=iCount-1

        self.StopThread()
        if len(self.aiTachDevices)==0:
            return {"Host":""}
        else:
            uKey=self.aiTachDevices.keys()[0]
            return {"Host":self.aiTachDevices[uKey].uIP}

    def OnPause(self,**kwargs):
        cDiscoverScriptTemplate.OnPause(self)
        if self.oThread is not None:
            self.oDiscoverObject.Close()
    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults):
        return {"TimeOut":{"type": "numericfloat", "order":0,  "title": "$lvar(6019)", "desc": "$lvar(6020)","key": "timeout", "default":"2.0"}}


class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args

    def run(self):
        self._target(*self._args)

class ciTachDiscover(object):

    def __init__(self,aDevices, cScriptClass):
        self.aDevices = aDevices
        self.cScript  = cScriptClass
        self.oSocket  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def Run(self,fTimeOut):

        self.bStopThreadEvent = False

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
            self.cScript.ShowError("iTach-Discover -3: Error occured",e)

        try:
            while not self.bStopThreadEvent:
                if self.oSocket is not None:
                    ready = select.select([self.oSocket], [], [],int(fTimeOut))
                    # the first element of the returned list is a list of readable sockets
                    if ready[0]:
                        data = self.oSocket.recv(1024)
                        match = p.match(data)
                        if match:
                            oiTachEntry=QueryDict()
                            oiTachEntry.uIP = match.group('IP')
                            oiTachEntry.uUUID       = match.group('UUID')
                            oiTachEntry.uModel      = match.group('Model')
                            oiTachEntry.uRevision   = match.group('Revision')
                            oiTachEntry.uPartNumber = match.group('PN')
                            oiTachEntry.uStatus     = match.group('Status')

                            if not oiTachEntry.uIP in self.aDevices:
                                self.aDevices[oiTachEntry.uIP]=oiTachEntry
                                Logger.info("iTach-Discover: iTach found! IP: %s, UUID:%s, Model:%s, Revision:%s, Part number:%s, Status:%s" % (oiTachEntry.uIP , oiTachEntry.uUUID , oiTachEntry.uModel , oiTachEntry.uRevision , oiTachEntry.uPartNumber ,  oiTachEntry.uStatus ))

        except socket.timeout:
            if len(self.aDevices)==0:
                Logger.debug("iTach-Discover: Could not find an iTach on the network")
        except Exception as e:
            self.cScript.ShowError("iTach-Discover: Error occured",e)
        finally:
            Logger.debug (u'iTach-Discover: Stop Discover Thread')
            self.oSocket.close()
            return
    def Close(self):
        self.bStopThreadEvent=True

