# -*- coding: utf-8 -*-
# Orca Video

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
from typing                                 import List
from typing                                 import cast
from ORCA.action.Action import cAction
from ORCA.interfaces.BaseInterface          import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings  import cBaseInterFaceSettings
from ORCA.utils.FileName                    import cFileName
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.widgets.Video                     import cWidgetVideo
from ORCA.actions.ReturnCode                import eReturnCode
from ORCA.Globals import Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.interfaces.BaseTrigger import cBaseTrigger
else:
    from typing import TypeVar
    cBaseTrigger = TypeVar('cBaseTrigger')


'''
<root>
  <repositorymanager>
    <entry>
      <name>ORCA Video Control</name>
      <description language='English'>Interface to show videos and streams (experimental)</description>
      <description language='German'>Interface um Videos und Streams anzuzeigen (experimental)</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/orca_video</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/orca_video.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
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
            self.oWidgetPlayer:Optional[cWidgetVideo]      = None
            self.aIniSettings.uParseResultOption           = 'tokenize'
            self.aIniSettings.uParseResultTokenizeString   = ':'

        def ReadConfigFromIniFile(self,uConfigName:str) -> None:
            super().ReadConfigFromIniFile(uConfigName=uConfigName)
            self.aIniSettings.uParseResultOption           = 'tokenize'
            self.aIniSettings.uParseResultTokenizeString   = ':'
            self.aIniSettings.uStream                      = ReplaceVars(self.aIniSettings.uStream)
            self.aIniSettings.uFNCodeset                   = 'CODESET_orca_video_default.xml'
            return

        def Connect(self) -> bool:

            if not super().Connect():
                return False
            try:
                aWidgetPlayer = Globals.oTheScreen.FindWidgets(uPageName = self.oAction.oParentWidget.oParentScreenPage.uPageName, uWidgetName = self.aIniSettings.uWidgetName)
                if len(aWidgetPlayer)>0:
                    self.oWidgetPlayer= cast(cWidgetVideo,aWidgetPlayer[0])
                if self.oWidgetPlayer is not None:
                    self.bIsConnected =True
                    self.oWidgetPlayer.Connect(self)
                    return True
                else:
                    self.ShowError(uMsg='Can\'t find widget')
                    self.bOnError=True
                    return False

            except Exception as e:
                self.ShowError(uMsg='Can\'t find widget',oException=e)
                self.bOnError=True
                return False

        def Disconnect(self) -> bool:
            if not super().Disconnect():
                return False
            if self.oWidgetPlayer is not None:
                self.oWidgetPlayer.Connect(None)

            self.bOnError = False
            self.oWidgetPlayer=None
            return True

        def Receive(self,uResponse:str) -> None:
            uCommand:str
            uRetVal:str
            aActionTrigger:List[cBaseTrigger]

            try:
                uCommand,uRetVal=self.oInterFace.ParseResult(self.oAction,uResponse,self)
                self.ShowDebug(uMsg='Parsed Responses:'+uCommand+':'+uRetVal)

                aActionTrigger=self.GetTrigger(uCommand)
                if len(aActionTrigger) > 0:
                    for oActionTrigger in aActionTrigger:
                        self.CallTrigger(oActionTrigger,uResponse)
                else:
                    self.ShowDebug(uMsg='Discard message:'+uCommand +':'+uResponse )
            except Exception as e:
                self.ShowError(uMsg='Error Receiving Response',oException=e)

    def __init__(self):
        cInterFaceSettings = self.cInterFaceSettings
        super().__init__()
        self.dSettings:Dict                             = {}
        self.oSetting:Optional[cInterFaceSettings]      = None

    def Init(self, uObjectName: str, oFnObject: cFileName = None) -> None:
        super().Init(uObjectName=uObjectName, oFnObject=oFnObject)
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = 'enabled'
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = 'enabled'
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = 'enabled'

    def DeInit(self, **kwargs) -> None:
        super().DeInit(**kwargs)
        for uSettingName in self.dSettings:
            self.dSettings[uSettingName].DeInit()

    def GetConfigJSON(self) -> Dict:
        return {'WidgetName': {'active': 'enabled', 'order': 3, 'type': 'string', 'title': '$lvar(IFACE_OVIDEO_1)',  'desc': '$lvar(IFACE_OVIDEO_1)',  'section': '$var(ObjectConfigSection)','key': 'WidgetName',  'default':'select'   },
                'Stream':     {'active': 'enabled', 'order': 4, 'type': 'string', 'title': '$lvar(IFACE_OVIDEO_3)',  'desc': '$lvar(IFACE_OVIDEO_4)',  'section': '$var(ObjectConfigSection)','key': 'Stream',      'default':'rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov'  }
               }

    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        super().SendCommand(oAction=oAction,oSetting=oSetting,uRetVar=uRetVar,bNoLogOut=bNoLogOut)

        uCmd:str
        uCmd=ReplaceVars(oAction.uCmd)
        uCmd=ReplaceVars(uCmd,self.uObjectName+'/'+oSetting.uConfigName)

        self.ShowInfo(uMsg='Sending command: %s to %s (%s:%s)' % (uCmd,oSetting.aIniSettings.uWidgetName,oSetting.uConfigName,oSetting.aIniSettings.uStream))
        oSetting.Connect()

        eRet:eReturnCode=eReturnCode.Error
        if oSetting.bIsConnected:
            try:
                oSetting.oWidgetPlayer.StatusControl(uCmd,oSetting.aIniSettings.uStream)
                eRet = eReturnCode.Success
            except Exception as e:
                self.ShowError(uMsg='Can\'t send message',uParConfigName='',oException=e)
                eRet = eReturnCode.Error
        return eRet
