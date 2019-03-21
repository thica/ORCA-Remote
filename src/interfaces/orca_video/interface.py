# -*- coding: utf-8 -*-
# Orca Video

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

from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
from ORCA.vars.Replace          import ReplaceVars
import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>ORCA Video Control</name>
      <description language='English'>Interface to show videos and streams (experimental)</description>
      <description language='German'>Interface um Videos und Streams anzuzeigen (experimental)</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/orca_video</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/orca_video.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>orca_video/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):
        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.oWidgetPlayer    = None
            self.aInterFaceIniSettings.uParseResultOption           = u'tokenize'
            self.aInterFaceIniSettings.uParseResultTokenizeString   = u':'

        def ReadConfigFromIniFile(self,uConfigName):
            cBaseInterFaceSettings.ReadConfigFromIniFile(self,uConfigName)
            self.aInterFaceIniSettings.uParseResultOption           = u'tokenize'
            self.aInterFaceIniSettings.uParseResultTokenizeString   = u':'
            self.aInterFaceIniSettings.uStream                      = ReplaceVars(self.aInterFaceIniSettings.uStream)
            self.aInterFaceIniSettings.uFNCodeset                   = u"CODESET_orca_video_default.xml"

            return

        def Connect(self):

            if not cBaseInterFaceSettings.Connect(self):
                return False
            try:
                aWidgetPlayer = Globals.oTheScreen.FindWidgets(uPageName = self.oAction.oParentWidget.oParentScreenPage.uPageName, uWidgetName = self.aInterFaceIniSettings.uWidgetName)
                if len(aWidgetPlayer)>0:
                    self.oWidgetPlayer= aWidgetPlayer[0]
                if self.oWidgetPlayer is not None:
                    self.bIsConnected =True
                    self.oWidgetPlayer.Connect(self)
                    return True
                else:
                    self.ShowError(u'Cannot Find Widget')
                    self.bOnError=True
                    return False

            except Exception as e:
                self.ShowError(u'Cannot Find Widget',e)
                self.bOnError=True
                return False

        def Disconnect(self):
            if not cBaseInterFaceSettings.Disconnect(self):
                return False
            if self.oWidgetPlayer is not None:
                self.oWidgetPlayer.Connect(None)

            self.bOnError = False
            self.oWidgetPlayer=None

        def Receive(self,uResponse):
            try:
                uCommand,uRetVal=self.oInterFace.ParseResult(self.oAction,uResponse,self)
                self.ShowDebug(u'Parsed Responses:'+uCommand+u':'+uRetVal)

                oActionTrigger=self.GetTrigger(uCommand)
                if oActionTrigger is not None:
                    self.CallTrigger(oActionTrigger,uResponse)
                else:
                    self.ShowDebug(u'Discard message:'+uCommand +':'+uResponse )
            except Exception as e:
                self.ShowError(u'Error Receiving Response',e)

    def __init__(self):
        cBaseInterFace.__init__(self)
        self.aSettings   = {}
        self.oSetting = None

    def Init(self, uInterFaceName, oFnInterFace=None):
        cBaseInterFace.Init(self, uInterFaceName, oFnInterFace)
        self.oInterFaceConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oInterFaceConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"

    def DeInit(self, **kwargs):
        cBaseInterFace.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def GetConfigJSON(self):
        return {"WidgetName": {"active": "enabled", "order": 3, "type": "string", "title": "$lvar(IFACE_OVIDEO_1)",  "desc": "$lvar(IFACE_OVIDEO_1)",  "section": "$var(InterfaceConfigSection)","key": "WidgetName",  "default":"select"   },
                "Stream":     {"active": "enabled", "order": 4, "type": "string", "title": "$lvar(IFACE_OVIDEO_3)",  "desc": "$lvar(IFACE_OVIDEO_4)",  "section": "$var(InterfaceConfigSection)","key": "Stream",      "default":"rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov"  }
               }

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        uCmd=ReplaceVars(oAction.uCmd)
        uCmd=ReplaceVars(uCmd,self.uInterFaceName+'/'+oSetting.uConfigName)

        self.ShowInfo(u'Sending Command: %s to %s (%s:%s)' % (uCmd,oSetting.aInterFaceIniSettings.uWidgetName,oSetting.uConfigName,oSetting.aInterFaceIniSettings.uStream))
        oSetting.Connect()

        iRet=1
        if oSetting.bIsConnected:
            try:
                iRet,sValue=oSetting.oWidgetPlayer.StatusControl(uCmd,oSetting.aInterFaceIniSettings.uStream)
                iRet=0
            except Exception as e:
                self.ShowError(u'can\'t Send Message',u'',e)
                iRet=1
        return iRet
