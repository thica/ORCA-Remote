# -*- coding: utf-8 -*-
# remoteghost

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
from typing                                 import List
from typing                                 import Dict
from typing                                 import Tuple

import select
import socket
from threading                              import Thread
from kivy.logger                            import Logger
from ORCA.action.Action import cAction
from ORCA.interfaces.BaseInterface          import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings  import cBaseInterFaceSettings
from ORCA.utils.FileName                    import cFileName
from ORCA.utils.TypeConvert                 import ToBytes
from ORCA.utils.TypeConvert                 import ToUnicode
from ORCA.utils.wait.StartWait              import StartWait
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.actions.ReturnCode                import eReturnCode

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
      <name>Remoteghost Control for EventGhost</name>
      <description language='English'>Interface to send commands to EventGhost</description>
      <description language='German'>Interface um Kommandos an EventGhost zu senden</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/remoteghost</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/remoteghost.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


"""

You need to create / adjust the CODESET_xxxx.xml file to match Action string to Eventghost Commands
xxxx = Configuration Name

To emulate special-keys, you have to enclose a keyword in curly braces.
For example if you want to have a cursor-up-key you write **{Up}**. You
can combine multiple keywords with the plus sign to get key-combinations like
**{Shift+Ctrl+F1}** or **{Ctrl+V}**.

Some keys differentiate between the left or the right side of the keyboard
and can then be prefixed with an "L" or "R", like the Windows-Key:

**{Win}** or **{LWin}** or **{RWin}**

And here is the list of the remaining keywords EventGhost understands:

    | ** Follwoing Commands must have a 'key' eventtype **
    | **{Ctrl}** or **{Control}**
    | **{Shift}**
    | **{Alt}**
    | **{Return}** or **{Enter}**
    | **{Back}** or **{Backspace}**
    | **{Tab}** or **{Tabulator}**
    | **{Esc}** or **{Escape}**
    | **{Spc}** or **{Space}**
    | **{Up}**
    | **{Down}**
    | **{Left}**
    | **{Right}**
    | **{PgUp}** or **{PageUp}**
    | **{PgDown}** or **{PageDown}**
    | **{Home}**
    | **{End}**
    | **{Ins}** or **{Insert}**
    | **{Del}** or **{Delete}**
    | **{Pause}**
    | **{Capslock}**
    | **{Numlock}**
    | **{Scrolllock}**
    | **{F1}, {F2}, ... , {F24}**
    | **{Apps}** (This is the context-menu-key)
    |
    | These will emulate keys from the numpad:
    | **{Divide}**
    | **{Multiply}**
    | **{Subtract}**
    | **{Add}**
    | **{Decimal}**
    | **{Numpad0}, {Numpad1}, ... , {Numpad9}**
    | ** Follwoing Commands must have a 'mouse' eventtype **
    | **{MOUSE_LEFT_CLICK}**
    | **{MOUSE_RIGHT_CLICK}**
"""



class cInterface(cBaseInterFace):

    class cInterFaceSettings(cBaseInterFaceSettings):
        def __init__(self,oInterFace:cInterface):
            super().__init__(oInterFace)
            self.aIniSettings.iTimeToClose          = -1
            self.aIniSettings.uParseResultOption    = 'store'
            self.bStopThreadEvent:bool              = False
            self.iBufferSize:int                    = 1024
            self.oSocket:Optional[socket.socket]    = None
            self.oThread:Optional[Thread]           = None
            self.uMsg:str                           = ''

        def ReadConfigFromIniFile(self,uConfigName:str) -> None:
            super().ReadConfigFromIniFile(uConfigName=uConfigName)
            self.aIniSettings.uParseResultOption = 'store'
            return

        def Connect(self) -> bool:
            if not super().Connect():
                return False

            try:
                for res in socket.getaddrinfo(self.aIniSettings.uHost, int(self.aIniSettings.uPort), socket.AF_UNSPEC, socket.SOCK_STREAM):
                    af, socktype, proto, canonname, sa = res
                    try:
                        self.oSocket = socket.socket(af, socktype, proto)
                        self.oSocket.settimeout(2.0)
                    except socket.error:
                        self.oSocket = None
                        continue
                    try:
                        self.oSocket.connect(sa)
                        self.oSocket.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    except socket.error:
                        self.oSocket.close()
                        self.oSocket = None
                        continue
                    break
                if not self.oSocket is None:
                    if self.oThread:
                        self.bStopThreadEvent = True
                        self.oThread.join()
                        self.oThread = None
                    self.bStopThreadEvent = False

                    self.oThread = Thread(target=self.Receive, )
                    self.oThread.start()

                if self.oSocket is None:
                    self.ShowError(uMsg='Cannot open socket'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort)
                    self.bOnError=True
                    return False
                self.bIsConnected =True
            except Exception as e:
                self.ShowError(uMsg='Cannot open socket #2'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,oException=e)
                self.bOnError=True
                return False

            self.ShowDebug(uMsg='Interface connected!')
            return True

        def Disconnect(self) -> bool:
            if not super().Disconnect():
                return False

            self.bStopThreadEvent=True
            if self.oThread:
                self.oThread.join()
                self.oThread = None
            self.bOnError = False
            return True

        def Receive(self) -> None:
            #Main Listening Thread to receice eiscp messages

            uResponses:str
            uResponse:str
            aResponses:List
            aActionTrigger:List[cBaseTrigger]

            #Loop until closed by external flag
            try:
                while not self.bStopThreadEvent:
                    if self.oSocket is not None:
                        ready:Tuple = select.select([self.oSocket], [], [],1.0)
                        # the first element of the returned list is a list of readable sockets
                        if ready[0]:
                            byResponses = self.oSocket.recv(self.iBufferSize)
                            # there could be more than one response, so we need to split them
                            uResponses  = ToUnicode(byResponses)
                            aResponses  = uResponses.split('[EOL]')
                            for uResponse in aResponses:
                                # Todo: find proper encoding
                                if not uResponse=='' and not uResponse=='ORCA.ORCA Connecting...':
                                    if True:
                                         # If the returned Command is a response to the send message
                                        if uResponse.startswith('RemoteGhost.'):
                                            self.ShowDebug(uMsg='Returned Message:'+uResponse)
                                            #todo: parse the command from return
                                            # We do not need to wait for an response anymore
                                            StartWait(0)
                                            # we got our response, all other responses are for somebody else
                                            self.uMsg=''
                                        else:
                                            # we have a notification issued by the device, so lets have a look, if we have a trigger assigned to it
                                            aActionTrigger=self.GetTrigger(uResponse)
                                            if len(aActionTrigger)>0:
                                                for oActionTrigger in aActionTrigger:
                                                    self.CallTrigger(oActionTrigger,uResponse)
                                            else:
                                                self.ShowDebug(uMsg='Discard message:'+uResponse)

            except Exception as e:
                self.ShowError(uMsg='Error Receiving Response:',oException=e)
                self.bIsConnected=False
            try:
                if not self.oSocket is None:
                    self.ShowDebug(uMsg='Closing socket in Thread')
                    self.oSocket.close()
            except Exception as e:
                self.ShowError(uMsg='Error closing socket in Thread',oException=e)


    def __init__(self):
        cInterFaceSettings=self.cInterFaceSettings
        super().__init__()
        self.dSettings:Dict                             = {}
        self.oSetting:Optional[cInterFaceSettings]      = None
        self.iWaitMs:int                                = 2000

    def Init(self, uObjectName: str, oFnObject: cFileName = None) -> None:
        super().Init(uObjectName=uObjectName, oFnObject=oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = 'enabled'
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = 'enabled'
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

    def GetConfigJSON(self) -> Dict:
        return {'Prefix': {'active': 'enabled', 'order': 3, 'type': 'string',         'title': '$lvar(IFACE_RGHOST_1)', 'desc': '$lvar(IFACE_RGHOST_2)', 'section': '$var(ObjectConfigSection)','key': 'Prefix',                  'default':'ORCA_'}}

    # noinspection PyUnresolvedReferences
    def SendCommand(self,oAction:cAction,oSetting:cInterFaceSettings,uRetVar:str,bNoLogOut:bool=False) -> eReturnCode:
        super().SendCommand(oAction=oAction,oSetting=oSetting,uRetVar=uRetVar,bNoLogOut=bNoLogOut)

        uCmd:str
        uPrefix:str      = ''
        iTryCount:int    = 0
        eRet:eReturnCode = eReturnCode.Error

        # call the function to pass string to eventghost
        if oAction.uType=='command':
            uPrefix= 'c'
        elif oAction.uType=='event':
            uPrefix='e'+oSetting.aIniSettings.uPreFix
        elif oAction.uType=='key':
            uPrefix= 'k'
        elif oAction.uType=='macro':
            uPrefix= 'a'
        elif oAction.uType=='mouse':
            uPrefix= 'm'
        else:
            Logger.warning ('Invalid type: '+oAction.uType)

        uCmd = ReplaceVars(oAction.uCmd)
        uCmd = ReplaceVars(uCmd,self.uObjectName+'/'+oSetting.uConfigName)
        if uCmd=='*':
            uCmd=oAction.dActionPars['commandname']

        self.ShowInfo(uMsg='Sending Command: '+uPrefix+uCmd + ' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,uParConfigName=oSetting.uConfigName)

        while iTryCount<self.iMaxTryCount:
            iTryCount+=1
            oSetting.Connect()
           # we need to verify if we are really connected, as the connection might have died
            # and .sendall will not return on error in this case
            #bIsConnected=oSetting.IsConnected()

            if oSetting.bIsConnected:
                uMsg=uPrefix+uCmd+'\n'
                try:
                    StartWait(self.iWaitMs)
                    oSetting.oSocket.sendall(ToBytes(uMsg))
                    eRet = eReturnCode.Success
                    break
                except Exception as e:
                    self.ShowError(uMsg='can\'t Send Message',uParConfigName=oSetting.uConfigName,oException=e)
                    oSetting.Disconnect()
                    eRet = eReturnCode.Error

        self.CloseSettingConnection(oSetting=oSetting, bNoLogOut=bNoLogOut)
        return eRet

