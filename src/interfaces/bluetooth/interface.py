# -*- coding: utf-8 -*-
# BLUETOOTH

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
from ORCA.vars.Replace      import ReplaceVars
from ORCA.vars.Access import SetVar
from ORCA.utils.TypeConvert import ToUnicode

from ORCA.utils.Sleep       import fSleep
from ORCA.utils.LogError    import LogError
from ORCA.utils.wait.StartWait  import StartWait
from kivy.clock             import Clock

import select

try:
    from bluetooth import *
except:
    pass

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Bluetooth</name>
      <description language='English'>Sends commands to a bluetooth connected device</description>
      <description language='German'>Sendet Befehle an ein per Bluetooth angeschlossenes Gerät</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <skip>1</skip>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/bluetooth</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/bluetooth.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>bluetooth/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

'''
The app must have BLUETOOTH and BLUETOOTH_ADMIN permissions (well, i didn't
tested without BLUETOOTH_ADMIN, maybe it works.)

'''

'''

This does not work properly, just for collecting ideas

myBluetoothAdapter = BluetoothAdapter.getDefaultAdapter()
myIntentFilter = IntentFilter(BluetoothDevice.ACTION_FOUND)
myContext = PythonActivity.mActivity
myDiscoverer=BroadcastReceiver

class FloatLayoutApp(App):
        def __init__(self, **kwargs):
                super(FloatLayoutApp,self).__init__(**kwargs)

        def build(self, *args, **kwargs):
                print myBluetoothAdapter.getName()
                if myBluetoothAdapter.getName != None:
                        print "device is BT Capable"
                else:
                        print "device is not BT Capable"
                if myBluetoothAdapter.isEnabled()==True:
                        myContext.registerReceiver(myDiscoverer,myIntentFilter)

                if myBluetoothAdapter.isDiscovering()==False:
                        myBluetoothAdapter.startDiscovery()

                return FloatLayoutWidget()


'''

'''
pybluez advertise as a keyboard

from bluetooth import *

server_sock=BluetoothSocket(L2CAP)
server_sock.bind(("", 17))
server_sock.listen(1)

uuid = "1f16e7c0-b59b-11e3-95d2-0002a5d5c51b"

advertise_service( server_sock, "PyBluez TEST",
                   service_id = uuid,
                   service_classes = [ HID_CLASS ],
                   profiles = [ HID_PROFILE ])

print("Waiting for connection on L2CAP")

try:
    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    while True:
        data = client_sock.recv(1024)
        if len(data) == 0:
                break
        print("received [%s]" % data)
except IOError:
    pass
except KeyboardInterrupt:
    print "Stopping..."
    stop_advertising(server_sock)
    sys.exit()  

print("disconnected")

client_sock.close()
server_sock.close()
print("all done")


'''

#
class cInterface(cBaseInterFace):


    class cBluetoothSocket(object):
        def __init__(self):

            try:
                if Globals.uPlatform==u'android':
                    from jnius import autoclass
                    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
                    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
                    UUID = autoclass('java.util.UUID')
#                if Globals.uPlatform==u'win':
#                    from bluetooth import *

            except Exception as e:
                LogError(u'Can''t initialize bluetooth interface',e)
                raise

        def connect(self,uDeviceName):
            self.uDeviceName=uDeviceName
            try:
                if Globals.uPlatform==u'android':
                    aPaired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
                    self.oSocket = None
                    for uDevice in aPaired_devices:
                        if uDevice.getName() == uDeviceName:
                            self.oSocket = uDevice.createRfcommSocketToServiceRecord(UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                            self.Recv_Stream = oSocket.getInputStream()
                            self.Send_Stream = oSocket.getOutputStream()
                            self.oSocket.connect()
                            return True
                    LogError(u'Bluetooth device not found',None)
                    return False
                elif Globals.uPlatform==u'win':

                    nearby_devices = discover_devices()
                    for bdaddr in nearby_devices:
                        print (lookup_name( bdaddr ))
                        if uDeviceName == lookup_name( bdaddr ):
                            target_address = bdaddr
                            break


                    #service_matches = find_service(name=uDeviceName)
                    service_matches = find_service()

                    if len(service_matches) == 0:
                        first_match = service_matches[0]
                        self.aInterFaceIniSettings.uPort = first_match["port"]
                        self.aInterFaceIniSettings.uHost = first_match["host"]

                        self.oSocket=BluetoothSocket( RFCOMM )
                        self.oSocket.connect((self.aInterFaceIniSettings.uHost, self.aInterFaceIniSettings.uPort))
                        return True
                    LogError(u'Bluetooth device not found',None)
                    return False

                return False
            except Exception as e:
                LogError(u'Error while bluetooth connect',e)
                return False

        def close(self):
            try:
                if Globals.uPlatform==u'android' or Globals.uPlatform==u'win':
                    oSocket.close()
                    return True
            except Exception as e:
                Logger.error("Closing bluetooth connection for device %s failed" % (self.uDeviceName))
                return False

        def send_all(self,uCommand):
            try:
                if Globals.uPlatform==u'android':
                    aCmd=[ord(b) if ord(b) <= 127 else ord(b)-256 for b in uCommand]
                    self.Send_Stream.write('{}\n'.format(aCmd))
                    self.Send_Stream.flush()
                elif Globals.uPlatform==u'win':
                    sock.send(uCommand)
                return True
            except Exception as e:
                Logger.error("Sending data via bluetooth for device %s failed" % (self.uDeviceName))
                return False


        def recv(self,fTimeOut):
            pass

    class cInterFaceSettings(cBaseInterFaceSettings):
        def __init__(self,oInterFace):
            cBaseInterFaceSettings.__init__(self,oInterFace)
            self.oSocket           = None
            self.uRetVar           = u''
            self.iBufferSize       = 30240
            self.bStopThreadEvent  = False
            self.uID               = u"5"

        def Connect(self):

            if not cBaseInterFaceSettings.Connect(self):
                return False

            self.ShowDebug(u'Interface trying to connect...')

            msg=None

            try:
                try:
                    self.oSocket = self.oInterFace.cBluetoothSocket()
                    self.oSocket.connect(self.aInterFaceIniSettings.uHost)
                except Exception as msg:
                    self.oSocket.close()
                    self.oSocket = None
                if self.oSocket is None:
                    self.ShowError(u'Interface not connected: Cannot open socket:'+self.aInterFaceIniSettings.uHost+':'+self.aInterFaceIniSettings.uPort,msg)
                    self.bOnError=True
                    return
                self.bIsConnected =True
            except Exception as e:
                self.ShowError(u'Interface not connected: Cannot open socket #2:'+self.aInterFaceIniSettings.uHost.uHost+':'+self.aInterFaceIniSettings.uPort,e)
                self.bOnError=True
                return

            self.ShowDebug(u'Interface connected!')

        def Disconnect(self):
            fSleep(0.05,True)
            self.bStopThreadEvent=True
            if not cBaseInterFaceSettings.Disconnect(self):
                self.ShowDebug(u'Interface Disconnect #1: Connection is already closed, no further actions')
                return False
            self.ShowDebug(u'Interface Disconnect #2:Closing Connection')

            #force close of socket, even if in thrad it will be close again
            try:
                self.oSocket.close()
            except Exception as e:
                pass
            self.bOnError = False

        def Receive(self):
            #Main Listening Thread to receive json messages

            #Loop until closed by external flag
            try:
                while not self.bStopThreadEvent:
                    if self.oSocket is not None:
                        ready = select.select([self.oSocket], [], [],1.0)
                        # the first element of the returned list is a list of readable sockets
                        if ready[0]:
                            self.bHandled=False
                            sResponses = self.oSocket.recv(self.iBufferSize)
                            uResponses = ToUnicode(sResponses)
                            # there could be more than one response, so we need to split them
                            # unfortunately, there is no end char in a json respone
                            aResponses=uResponses.split('}{')
                            if not len(aResponses)==1:
                                i=0
                                while i<len(aResponses):
                                    if i==0:
                                        aResponses[i]+='}'
                                    else:
                                        aResponses[i]=u'{'+aResponses[i]
                                    i+=1
                            uID=0
                            for uResponse in aResponses:
                                if not uResponse==u'':
                                    if '"result":"pong"' in uResponse:
                                        pass
                                    else:

                                        # Get the Command and the payload
                                        # If the returned Command is a response to the send message
                                        uCommand,uID=self.oInterFace.ParseResult_JsonHeader(uResponse)
                                        if uID==self.uID:

                                            uCmd,uRetVal=self.oInterFace.ParseResult(self.oAction,uResponse,self)

                                            self.ShowDebug(u'Parsed Respones:'+uRetVal)

                                            if not self.uRetVar==u'' and not uRetVal==u'':
                                                SetVar(uVarName = self.uRetVar, oVarValue = uRetVal)
                                            # We do not need to wait for an response anymore
                                            StartWait(0)
                                            self.bHandled=True


                                        if not self.bHandled:
                                            # we have a notification issued by the device, so lets have a look, if we have a trigger assigned to it
                                            oActionTrigger=self.GetTrigger(uCommand)
                                            if oActionTrigger is not None:
                                                self.CallTrigger(oActionTrigger,uResponse)
                                            else:
                                                self.ShowDebug(u'Discard message:'+uCommand +':'+uResponse)
                            #print "LEAVE PARSE"
                            fSleep(0.01)

            except Exception as e:
                if self.bIsConnected:
                    self.ShowError(u'Error Receiving Response:',e)
                self.bIsConnected=False
            try:
                if self.oSocket is not None:
                    self.ShowDebug(u'Closing socket in Thread')
                    self.oSocket.close()
            except Exception as e:
                self.ShowError(u'Error closing socket in Thread',e)

    def __init__(self):
        cBaseInterFace.__init__(self)
        self.aSettings      = {}
        self.oSetting       = None
        self.uResponse      = u''
        self.iBufferSize    = 30240
        self.tJsonResponse  = None
        self.iWaitMs        = 1000

    def DeInit(self, **kwargs):
        cBaseInterFace.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        if uRetVar!="":
            oAction.uGlobalDestVar=uRetVar

        iTryCount=0
        iRet=1
        #Logger.info ('Interface '+self.sInterFaceName+': Sending Command: '+sCommand + ' to '+oSetting.sHost+':'+oSetting.sPort)
        while iTryCount<2:
            iTryCount+=1
            oSetting.Connect()
            # we need to verify if we are really connected, as the connection might have died
            # and .sendall will not return on error in this case

            if oSetting.bIsConnected:
                uMsg=oAction.uCmd
                try:

                    uMsg=ReplaceVars(uMsg,self.uInterFaceName+'/'+oSetting.uConfigName)
                    uMsg=ReplaceVars(uMsg)
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar,self.uInterFaceName+'/'+oSetting.uConfigName)
                    oAction.uGetVar         = ReplaceVars(oAction.uGetVar)

                    uMsg=uMsg[:-1]+",\"id\":\"" +oSetting.uID+"\"}"
                    oSetting.uMsg=uMsg
                    oSetting.uRetVar=uRetVar
                    oSetting.uRetVar=uRetVar
                    self.ShowInfo (u'Sending Command: '+uMsg + ' to '+oSetting.aInterFaceIniSettings.uHost+':'+oSetting.aInterFaceIniSettings.uPort,oSetting.uConfigName)
                    #All response comes to receiver thread, so we should hold the queue until vars are set
                    if oSetting.oAction.bWaitForResponse:
                        StartWait(self.iWaitMs)
                    oSetting.oSocket.sendall(uMsg)
                    fSleep(0.01)
                    iRet=0
                    break
                except Exception as e:
                    self.ShowError(u'Can\'t send message',oSetting.uConfigName,e)
                    iRet=1
                    oSetting.Disconnect()
                    oSetting.bOnError=True
                    if not uRetVar==u'':
                        SetVar(uVarName = uRetVar, oVarValue = u"Error")
            else:
                if not uRetVar==u'':
                    SetVar(uVarName = uRetVar,oVarValue = u"Error")

        if oSetting.bIsConnected:
            if oSetting.aInterFaceIniSettings.iTimeToClose==0:
                oSetting.Disconnect()
            elif oSetting.aInterFaceIniSettings.iTimeToClose!=-1:
                Clock.unschedule(oSetting.FktDisconnect)
                Clock.schedule_once(oSetting.FktDisconnect, oSetting.aInterFaceIniSettings.iTimeToClose)
        return iRet

