# -*- coding: utf-8 -*-
#

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


import socket
import select
from kivy.logger                            import Logger

from ORCA.Compat                            import PY2
from ORCA.scripts.BaseScriptSettings        import cBaseScriptSettings
from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
from ORCA.ui.ShowErrorPopUp                 import ShowMessagePopUp
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.vars.QueryDict                    import QueryDict

'''
<root>
  <repositorymanager>
    <entry>
      <name>ELV MAX Discover</name>
      <description language='English'>Discover ELV MAX cubes</description>
      <description language='German'>Erkennt bwz. sucht ELV MAX Cubes</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/discover/discover_elvmax</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/discover_elvmax.zip</sourcefile>
          <targetpath>scripts/discover</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/discover/discover_elvmax/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


class cScript(cDiscoverScriptTemplate):

    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-Discover-ELVMAX
    WikiDoc:TOCTitle:Discover ELVMAX
    = Script Discover ELVMAX =

    The ELV MAX discover script discovers ELV MAX cubes for heaing control.
    You can filter the discover result by passing the following parameters::
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |serial
    |Discover models only with a specific serial number (leave it blank to discover all)
    |-
    |timeout
    |Specifies the timout for discover
    |}</div>

    WikiDoc:End
    """

    class cScriptSettings(cBaseScriptSettings):
        def __init__(self,oScript):
            cBaseScriptSettings.__init__(self,oScript)
            self.aScriptIniSettings.fTimeOut                     = 5.0

    def __init__(self):
        cDiscoverScriptTemplate.__init__(self)
        self.uSubType        = u'ELVMAX'
        self.uSerial         = u''
        self.aResults        = []

    def Init(self,uScriptName,uScriptFile=u''):
        cDiscoverScriptTemplate.Init(self, uScriptName, uScriptFile)
        self.oScriptConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"

    def GetHeaderLabels(self):
        return ['$lvar(5029)','$lvar(SCRIPT_DISC_ELVMAX_1)','$lvar(5035)']

    def ListDiscover(self):

        dArgs = {}

        self.Discover(**dArgs)
        for aDevice in self.aResults:
            self.AddLine([aDevice.sFoundIP,aDevice.uFoundSerial,aDevice.uFoundHostName],aDevice)


    def CreateDiscoverList_ShowDetails(self,instance):
        uText=  u"$lvar(5029): %s \n" \
                u"$lvar(5035): %s \n" \
                u"$lvar(1063): %s \n" \
                u"$lvar(SCRIPT_DISC_ELVMAX_1): %s " % (instance.oDevice.sFoundIP,instance.oDevice.uFoundHostName,instance.oDevice.uFoundName,instance.oDevice.uFoundSerial)

        ShowMessagePopUp(uMessage=uText)


    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults):
        return  {"Serial Number":   {"type": "string",       "order":0,  "title": "$lvar(SCRIPT_DISC_ELVMAX_1)", "desc": "$lvar(SCRIPT_DISC_ELVMAX_1)", "key": "serialnumber",    "default":"" }
                }

    def Discover(self,**kwargs):

        oSendSocket    = None
        oReceiveSocket = None
        iPort          = 23272
        uSerial        = kwargs.get('serialnumber',"")
        uConfigName    = kwargs.get('configname',self.uConfigName)
        oSetting       = self.GetSettingObjectForConfigName(uConfigName=uConfigName)
        fTimeOut       = ToFloat(kwargs.get('timeout', oSetting.aScriptIniSettings.fTimeOut))
        del self.aResults[:]

        Logger.debug (u'Try to discover ELV MAX device:  %s ' % uSerial)

        try:
            oSendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            oSendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
            oSendSocket.settimeout(10)

            bData = bytearray("eQ3Max", "utf-8") + \
                    bytearray("*\0",    "utf-8") + \
                    bytearray('*' * 10, "utf-8") + \
                    bytearray('I',      "utf-8")

            oSendSocket.sendto(bData,("255.255.255.255",iPort))

            oReceiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oReceiveSocket.settimeout(fTimeOut)
            oReceiveSocket.bind(("0.0.0.0", iPort))

            # sData, tSenderAddr = oReceiveSocket.recvfrom(50)
            # oRet = self.GetDeviceDetails(sData, tSenderAddr)
            # if uSerial == "" or oRet.uSerial == uSerial:
            #     self.aResults.append(oRet)

            while True:
                # we do not wait too long
                ready = select.select([oReceiveSocket],[],[],fTimeOut)
                if ready[0]:
                    # Get a response
                    sData, tSenderAddr = oReceiveSocket.recvfrom(50)
                    oRet = self.GetDeviceDetails(sData, tSenderAddr)
                    if uSerial=="" or oRet.uSerial == uSerial:
                        self.aResults.append(oRet)
                else:
                    break

            if oSendSocket:
                oSendSocket.close()
            if oReceiveSocket:
                oReceiveSocket.close()

            if len(self.aResults)>0:
                return QueryDict([("Host", self.aResults[0].sFoundIP),("Hostname",self.aResults[0].uFoundHostName), ("Serial",self.aResults[0].uFoundSerial), ("Name",self.aResults[0].uFoundName)])

        except Exception as e:
            pass

        if oSendSocket:
            oSendSocket.close()
        if oReceiveSocket:
            oReceiveSocket.close()

        Logger.warning(u'No ELV MAX Cube found %s' % uSerial)
        return QueryDict([("Host", ""), ("Hostname", ""), ("Serial", ""), ("Name", "")])

    def GetDeviceDetails(self,sData,tSenderAddr):

        oRet                     = QueryDict()
        oRet.sFoundIP            = tSenderAddr[0]
        oRet.sData               = sData
        oRet.uFoundName          = sData[0:8].decode('utf-8')
        oRet.uFoundSerial        = sData[8:18].decode('utf-8')
        oRet.uFoundHostName      = socket.gethostbyaddr(oRet.sFoundIP)[0]
        oRet.uIPVersion          = u"IPv4"

        Logger.info(u'Bingo: Dicovered device %s:%s:%s at %s' % (oRet.uFoundName, oRet.uFoundHostName, oRet.uFoundSerial, oRet.sFoundIP))

        return oRet
