# -*- coding: utf-8 -*-
# remoteghost

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

import select
import socket
from threading              import Thread

from kivy.clock                     import Clock
from kivy.logger                    import Logger

from ORCA.Compat                    import PY2
from ORCA.interfaces.BaseInterface  import cBaseInterFace
from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
from ORCA.utils.TypeConvert         import ToUnicode
from ORCA.utils.TypeConvert         import ToBytes
from ORCA.utils.wait.StartWait      import StartWait
from ORCA.vars.Replace              import ReplaceVars

'''
<root>
  <repositorymanager>
    <entry>
      <name>Remoteghost Control for EventGhost</name>
      <description language='English'>Interface to send commands to EventGhost</description>
      <description language='German'>Interface um Kommandos an EventGhost zu senden</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/remoteghost</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/remoteghost.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>remoteghost/interface.pyc</file>
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
        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.aIniSettings.iTimeToClose          = -1
            self.aIniSettings.uParseResultOption    = u'store'
            self.bStopThreadEvent                   = False
            self.iBufferSize                        = 1024
            self.oSocket                            = None
            self.oThread                            = None
            self.uMsg                               = u''

        def ReadConfigFromIniFile(self,uConfigName):
            cBaseInterFaceSettings.ReadConfigFromIniFile(self,uConfigName)
            self.aIniSettings.uParseResultOption = u'store'
            return

        def Connect(self):
            if not cBaseInterFaceSettings.Connect(self):
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
                    self.ShowError(u'Cannot open socket'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort)
                    self.bOnError=True
                    return
                self.bIsConnected =True
            except Exception as e:
                self.ShowError(u'Cannot open socket #2'+self.aIniSettings.uHost+':'+self.aIniSettings.uPort,e)
                self.bOnError=True
                return

            self.ShowDebug(u'Interface connected!')

        def Disconnect(self):
            if not cBaseInterFaceSettings.Disconnect(self):
                return False

            self.bStopThreadEvent=True
            if self.oThread:
                self.oThread.join()
                self.oThread = None
            self.bOnError = False

        def Receive(self):
            #Main Listening Thread to receice eiscp messages

            #Loop until closed by external flag
            try:
                while not self.bStopThreadEvent:
                    if self.oSocket is not None:
                        ready = select.select([self.oSocket], [], [],1.0)
                        # the first element of the returned list is a list of readable sockets
                        if ready[0]:
                            sResponses = self.oSocket.recv(self.iBufferSize)
                            # there could be more than one response, so we need to split them
                            uResponses = ToUnicode(sResponses)
                            aResponses=uResponses.split("[EOL]")
                            for uResponse in aResponses:
                                # Todo: find proper encoding
                                if not uResponse==u'' and not uResponse==u'ORCA.ORCA Connecting...':
                                    if True:
                                         # If the returned Command is a response to the send message
                                        if uResponse.startswith(u'RemoteGhost.'):
                                            self.ShowDebug(u'Returned Message:'+uResponse)
                                            #todo: parse the command from return
                                            # We do not need to wait for an response anymore
                                            StartWait(0)
                                            # we got our response, all other responses are for somebody else
                                            self.uMsg=u''
                                        else:
                                            # we have a notification issued by the device, so lets have a look, if we have a trigger assigned to it
                                            oActionTrigger=self.GetTrigger(uResponse)
                                            if oActionTrigger is not None:
                                                self.CallTrigger(oActionTrigger,uResponse)
                                            else:
                                                self.ShowDebug(u'Discard message:'+uResponse)

            except Exception as e:
                self.ShowError(u'Error Receiving Response:',e)
                self.bIsConnected=False
            try:
                if not self.oSocket is None:
                    self.ShowDebug(u'Closing socket in Thread')
                    self.oSocket.close()
            except Exception as e:
                self.ShowError(u'Error closing socket in Thread',e)


    def __init__(self):
        cBaseInterFace.__init__(self)
        self.aSettings      = {}
        self.oSetting       = None
        self.iWaitMs        = 2000

    def Init(self, uObjectName, oFnObject=None):
        cBaseInterFace.Init(self,uObjectName, oFnObject)
        self.oObjectConfig.dDefaultSettings['Host']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['Port']['active']                        = "enabled"
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"
        self.oObjectConfig.dDefaultSettings['ParseResult']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['TokenizeString']['active']              = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeOut']['active']                     = "enabled"
        self.oObjectConfig.dDefaultSettings['TimeToClose']['active']                 = "enabled"
        self.oObjectConfig.dDefaultSettings['DisableInterFaceOnError']['active']     = "enabled"
        self.oObjectConfig.dDefaultSettings['DisconnectInterFaceOnSleep']['active']  = "enabled"
        self.oObjectConfig.dDefaultSettings['DiscoverSettingButton']['active']       = "enabled"

    def DeInit(self, **kwargs):
        cBaseInterFace.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def GetConfigJSON(self):
        return {"Prefix": {"active": "enabled", "order": 3, "type": "string",         "title": "$lvar(IFACE_RGHOST_1)", "desc": "$lvar(IFACE_RGHOST_2)", "section": "$var(ObjectConfigSection)","key": "Prefix",                  "default":"ORCA_"}}

    def SendCommand(self,oAction,oSetting, uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        uCmd=oAction.uCmd
        uPrefix = u''

        if uCmd==u'*':
            uCmd=oAction.dActionPars['commandname']

        # call the function to pass string to eventghost
        if oAction.uType==u'command':
            uPrefix= u'c'
        elif oAction.uType==u'event':
            uPrefix=u'e'+oSetting.aIniSettings.uPreFix
        elif oAction.uType==u'key':
            uPrefix= u'k'
        elif oAction.uType==u'macro':
            uPrefix= u'a'
        elif oAction.uType==u'mouse':
            uPrefix= u'm'
        else:
            Logger.warning (u'Invalid type: '+oAction.uType)

        iTryCount=0
        iRet=1

        uCmd=ReplaceVars(oAction.uCmd)
        uCmd=ReplaceVars(uCmd,self.uObjectName+'/'+oSetting.uConfigName)

        self.ShowInfo(u'Sending Command: '+uPrefix+uCmd + u' to '+oSetting.aIniSettings.uHost+':'+oSetting.aIniSettings.uPort,oSetting.uConfigName)

        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()
           # we need to verify if we are really connected, as the connection might have died
            # and .sendall will not return on error in this case
            #bIsConnected=oSetting.IsConnected()

            if oSetting.bIsConnected:
                uMsg=uPrefix+uCmd+u'\n'
                try:
                    StartWait(self.iWaitMs)
                    if PY2:
                        oSetting.oSocket.sendall(uMsg)
                    else:
                        oSetting.oSocket.sendall(ToBytes(uMsg))
                    iRet=0
                    break
                except Exception as e:
                    self.ShowError(u'can\'t Send Message',oSetting.uConfigName,e)
                    oSetting.Disconnect()
                    iRet=1

        if oSetting.bIsConnected:
            if oSetting.aIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aIniSettings.iTimeToClose)
        return iRet

