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

import socket
import struct
import time
import rsa

from pyasn1.codec.der       import decoder
from pyasn1.type            import univ
from rsa                    import pkcs1
from kivy.logger            import Logger
from kivy.compat            import PY2

from ORCA.utils.Path        import cPath
from ORCA.utils.Platform    import OS_GetSystemUserPath
from ORCA.utils.TypeConvert import ToBytes

import ORCA.Globals as Globals

# Maximum amount of data in an ADB packet.
MAX_ADB_DATA = 4096
# ADB protocol version.
VERSION = 0x01000000

# AUTH constants for arg0.
AUTH_TOKEN          = 1
AUTH_SIGNATURE      = 2
AUTH_RSAPUBLICKEY   = 3

def MakeWireIDs(ids):
  id_to_wire = {
      cmd_id: sum(ord(c) << (i * 8) for i, c in enumerate(cmd_id))
      for cmd_id in ids
  }
  wire_to_id = {wire: cmd_id for cmd_id, wire in id_to_wire.items()}
  return id_to_wire, wire_to_id

def CalculateChecksum(data):
    # The checksum is just a sum of all the bytes. I swear.
    if not PY2:
        return sum(data) & 0xFFFFFFFF
    else:
        return sum(map(ord, data)) & 0xFFFFFFFF


class cIP_Connection(object):
    """ The pysical (TCP/IP) Connection to the target device """
    def __init__(self):
        self.oSocket        = None
        self.fTimeOut       = 1.0
        self.bIsConnected   = False
        self.uHost          = ""
        self.uPort          = ""

    def Connect(self, uHost, uPort ,fTimeOut):
        """
        Establishes a physcal TCP/IP Connection to the target device
        Exception and Error messages to be managed by calling class

        :param string uHost: The hostname or IP address of te target device
        :param string uPort: The port of the target device
        :param float fTimeOut: The timeout for the communication
        :return: True / False
        """

        self.oSocket     = None
        self.fTimeOut    = fTimeOut
        self.uHost       = uHost
        self.uPort       = uPort

        self.oSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.oSocket.setblocking(0)
        self.oSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.oSocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.oSocket.settimeout(fTimeOut)
        return self.ReConnect()

    def ReConnect(self):
        """
        Reconnects the pysical connection

        :return:
        """
        self.oSocket.connect((self.uHost, int(self.uPort)))
        self.bIsConnected = True
        return self.bIsConnected

    def WriteAll(self, uData):
        """
        Send data to the device

        :param string uData: The data to write
        :return: Unknown
        """

        if not PY2:
            uData = ToBytes(uData)

        return self.oSocket.sendall(uData)

    def ReadAll(self, iNumBytes):
        """
        Reads number of bytes from the stream

        :param integer iNumBytes: The number of bytes to read
        :return: The read data
        """
        return self.oSocket.recv(iNumBytes)

    def Close(self):
        """
        Closes the IP Connection

        :return: None
        """

        self.bIsConnected = False
        return self.oSocket.close()

    @property
    def IsConnected(self):
        """
        The logical connection status

        :return: The logical (not physical) connection status
        """
        return self.bIsConnected


class cADB_Connection(object):
    """ The logical (ADB) Connection to the target device
        All Communication will be managed by the cADB_Message class
    """

    def __init__(self,oADB_Message ):
        self.oADB_Message   = oADB_Message
        self.iLocal_id      = 0
        self.iRemote_id     = 0
        self.fTimeOut       = 1.0

    def SetConnectionParameter(self, iLocal_id, iRemote_id, fTimeOut):
        self.iLocal_id  = iLocal_id
        self.iRemote_id = iRemote_id
        self.fTimeOut   = fTimeOut

    def _Send(self, uCommand, arg0, arg1, uData=''):
        self.oADB_Message.SetCommand(uCommand, arg0, arg1, uData)
        self.oADB_Message.Send()

    def Write(self, uData):
        """Write a packet and expect an Ack."""
        self._Send('WRTE', arg0=self.iLocal_id, arg1=self.iRemote_id, uData=uData)
        # Expect an ack in response.
        uCmd, uOkay_data = self.ReadUntil('OKAY')
        if uCmd != 'OKAY':
            if uCmd == 'FAIL':
                raise Exception('cADB_Connection:write Command failed:'+ str(uOkay_data))
            raise Exception('cADB_Connection:write Expected an OKAY in response to a WRITE, got %s (%s)',uCmd, uOkay_data)
        return len(uData)

    def Okay(self):
        self._Send('OKAY', arg0=self.iLocal_id, arg1=self.iRemote_id)

    def ReadUntil(self, aExpected_cmds):
        """Read a packet, Ack any write packets."""

        uCmd, iRemote_id, iLocal_id, uData = self.oADB_Message.Read(aExpected_cmds, self.fTimeOut)
        if iLocal_id != 0 and self.iLocal_id != iLocal_id:
            raise Exception("cADB_Connection:ReadUntil We don't support multiple streams...")
        if iRemote_id != 0 and self.iRemote_id != iRemote_id:
            raise Exception('cADB_Connection:ReadUntil Incorrect remote id, expected %s got %s' % (self.iRemote_id, iRemote_id))
        # Ack write packets.
        if uCmd == 'WRTE':
            self.Okay()
        return uCmd, uData

    def ReadUntilClose(self):
        """Yield packets until a Close packet is received."""
        while True:
            uCmd, uData = self.ReadUntil(['CLSE', 'WRTE'])
            if uCmd == 'CLSE':
                self._Send('CLSE', arg0=self.iLocal_id, arg1=self.iRemote_id)
                break
            if uCmd != 'WRTE':
                if uCmd == 'FAIL':
                    raise Exception('cADB_Connection:ReadUntilClose Command failed (%s).' % uData)
                raise Exception('cADB_Connection:ReadUntilClose Expected a WRITE or a CLOSE, got %s (%s)',uCmd, uData)
            yield uData

    def Close(self):
        self._Send('CLSE', arg0=self.iLocal_id, arg1=self.iRemote_id)
        return
        uCmd, uData = self.ReadUntil('CLSE')
        if uCmd != 'CLSE':
            if uCmd == 'FAIL':
                raise Exception('cADB_Connection:Close Command failed. (%s))' %  uData)
            raise Exception('Expected a CLSE response, got %s (%s)',uCmd, uData)

class cADB_Commands(object):
    """ The set of exposed / implemented ADB Commands """

    def __init__(self):
        self.oIP_Connection  = cIP_Connection()
        self.oADB_Message    = cADB_Message(self.oIP_Connection)
        self.uDeviceState    = u''

    def ConnectDevice(self,uHost, uPort, fTimeOut=1.0, **kwargs):
        """
        Convenience function to get an adb device

        :param string uHost: The Host Name or IP Address
        :param string uPort: The Port use
        :param float fTimeOut: The timeout for the IP commands
        :param kwargs:
        :return: An cADB_Commands object
        """
        self.oIP_Connection.Connect(uHost = uHost,uPort = uPort,fTimeOut = fTimeOut)
        return self.Connect(**kwargs)

    def Connect(self,uIdentifier=None, **kwargs):
        """Connect to the device.

        Args:
          uIdentifier: Identifier of ORCA
          **kwargs: See protocol_handler.Connect for kwargs. Includes rsa_keys,
              and auth_timeout_ms.
        Returns:
          An instance of this class if the device connected successfully.
        """
        if not uIdentifier:
            uIdentifier = u"ORCA_"+Globals.uMACAddressDash
        self.uDeviceState = self.oADB_Message.Connect(uIdentifier=uIdentifier, **kwargs)
        # Remove banner and colons after device state (state::banner)
        self.uDeviceState = self.uDeviceState.split(':')[0]
        return self

    def Reboot(self, uDestination=''):
        """Reboot the device.
        Args:
        destination: Specify 'bootloader' for fastboot.
        """
        self.oADB_Message.Open('reboot:%s' % uDestination)

    def Shell(self, uCommand, fTimeOut=1.0):
        """Run command on the device, returning the output."""
        return self.oADB_Message.Command(uService='shell', uCommand=uCommand,fTimeOut=fTimeOut)

    def CloseWithConnection(self):
        self.oADB_Message.Close()

class cADB_Message(object):
    """ Compiles the Message and sends it to the device using the cConnection Class

    Protocol Notes

    local_id/remote_id:
        Turns out the documentation is host/device ambidextrous, so local_id is the
        id for 'the sender' and remote_id is for 'the recipient'. So since we're
        only on the host, we'll re-document with host_id and device_id:

        OPEN(host_id, 0, 'shell:XXX')
        READY/OKAY(device_id, host_id, '')
        WRITE(0, host_id, 'data')
        CLOSE(device_id, host_id, '')
    """


    def __init__(self, oIP_Connection):

        self.oIP_Connection      = oIP_Connection
        self.dCommands, self.dConstants = MakeWireIDs(['SYNC', 'CNXN', 'AUTH', 'OPEN', 'OKAY', 'CLSE', 'WRTE'])
        self.uFormat             = '<6I'            # An ADB message is 6 words in little-endian.
        self.iCommand            = 0
        self.iMagic              = 0
        self.arg0                = u''
        self.arg1                = u''
        self.uData               = u''
        self.oADB_Connection     = cADB_Connection(self)

    def SetCommand(self, uCommand = None, arg0 = None, arg1 = None, uData = ''):
        self.iCommand  = self.dCommands[uCommand]
        self.iMagic    = self.iCommand ^ 0xFFFFFFFF
        self.arg0      = arg0
        self.arg1      = arg1
        self.uData     = uData

    @property
    def checksum(self):
        return CalculateChecksum(self.uData)

    def Pack(self):
        """Returns this message in an over-the-wire format."""
        return struct.pack(self.uFormat, self.iCommand, self.arg0, self.arg1,len(self.uData), self.checksum, self.iMagic)

    def Unpack(self, uMessage):
        try:
            iCmd, arg0, arg1, iData_length, iData_checksum, iUnused_magic = struct.unpack(self.uFormat, uMessage)
        except struct.error:
            raise Exception('cADB_Message:Unpack Unable to unpack ADB command.')
        return iCmd, arg0, arg1, iData_length, iData_checksum

    def Send(self):
        """
        Sends the message to to the device
        """
        self.oIP_Connection.WriteAll(self.Pack())
        self.oIP_Connection.WriteAll(self.uData)

    def Read(self, aExpected_cmds, fTimeOut=1.0):
        """Receive a response from the device."""
        iStart = time.time()
        while True:
            uMsg = self.oIP_Connection.ReadAll(24)
            iCmd, arg0, arg1, iData_length, iData_checksum = self.Unpack(uMsg)
            uCommand = self.dConstants.get(iCmd)
            if not uCommand:
                raise Exception('cADB_Message:Read Unknown command: %x' % iCmd, iCmd, (arg0, arg1))
            if uCommand in aExpected_cmds:
                break
            else:
                # we read AND discard the wrong message
                Logger.debug("Discarding unexpected message:"+uCommand)
                if iData_length > 0:
                    self.ReadRestOfData(iData_length)

            if time.time() - iStart > (fTimeOut/1000):
                raise Exception('cADB_Message:Read Never got one of the expected responses (%s)' % aExpected_cmds,iCmd, (fTimeOut))

        if iData_length > 0:
            uData = self.ReadRestOfData(iData_length)

            iActual_checksum = CalculateChecksum(uData)
            if iActual_checksum != iData_checksum:
                raise Exception('cADB_Message:Read Received checksum %s != %s', (iActual_checksum, iData_checksum))
        else:
            uData = ''
        return uCommand, arg0, arg1, uData

    def ReadRestOfData(self,iData_length):
        if PY2:
            uData = ''
            while iData_length > 0:
                uTemp = self.oIP_Connection.ReadAll(iData_length)
                uData += uTemp
                iData_length -= len(uTemp)
            return uData
        else:
            bData = b''
            while iData_length > 0:
                bTemp = self.oIP_Connection.ReadAll(iData_length)
                bData += bTemp
                iData_length -= len(bTemp)
            return bData


    def Connect(self,  uIdentifier='notadb', aRsa_keys=None, fTimeOut=0.1):
        """Establish a new connection to the device.

        Args:
          uIdentifier: A string to send as a host identifier.
          aRsa_keys: List of AuthSigner subclass instances to be used for
              authentication. The device can either accept one of these via the Sign
              method, or we will send the result of GetPublicKey from the first one
              if the device doesn't accept any of them.
          fTimeOut: Timeout to wait for when sending a new public key. This
              is only relevant when we send a new public key. The device shows a
              dialog and this timeout is how long to wait for that dialog. If used
              in automation, this should be low to catch such a case as a failure
              quickly; while in interactive settings it should be high to allow
              users to accept the dialog. We default to automation here, so it's low
              by default.

        Returns:
          The device's reported banner. Always starts with the state (device,
              recovery, or sideload), sometimes includes information after a : with
              various product information.

        """

        if aRsa_keys is None:
            aRsa_keys = []

        self.SetCommand(uCommand='CNXN', arg0=VERSION, arg1=MAX_ADB_DATA,uData='host::%s\0' % uIdentifier)
        self.Send()
        uCmd, arg0, arg1, uIdentifier = self.Read(['CNXN', 'AUTH'])
        if uCmd == 'AUTH':
            if len(aRsa_keys)==0:
                raise Exception('cADB_Message:Connect Device authentication required, no keys available.')
            # Loop through our keys, signing the last 'banner' or token.
            for rsa_key in aRsa_keys:
                if arg0 != AUTH_TOKEN:
                    raise Exception('cADB_Message:Connect Unknown AUTH response: %s %s %s' % (arg0, arg1, uIdentifier))

                signed_token = rsa_key.Sign(uIdentifier)
                self.SetCommand(uCommand='AUTH', arg0=AUTH_SIGNATURE, arg1=0, uData=signed_token)
                self.Send()
                uCmd, arg0, unused_arg1, uIdentifier = self.Read(['CNXN', 'AUTH'])
                if uCmd == 'CNXN':
                    return uIdentifier

            # None of the keys worked, so send a public key.
            self.SetCommand(uCommand='AUTH', arg0=AUTH_RSAPUBLICKEY, arg1=0,uData=aRsa_keys[0].GetPublicKey() + '\0')
            self.Send()
            try:
                uCmd, arg0, unused_arg1, uIdentifier = self.Read(['CNXN'], fTimeOut=fTimeOut)
            except Exception as e:
                # todo: ReImplement
                #if e.usb_error.value == -7:  # Timeout.
                #    raise Exception('cADB_Message:Connect Accept auth key on device, then retry.')
                raise
            # This didn't time-out, so we got a CNXN response.
            return uIdentifier
        return uIdentifier

    def Open(self, uDestination, fTimeOut=1.0):
        """Opens a new connection to the device via an OPEN message.

        Not the same as the posix 'open' or any other google3 Open methods.

        Args:
          uDestination: The service:command string.
          fTimeOut: Timeout in seconds

        Returns:
          The local connection id.
        """
        iLocal_id = 1
        self.SetCommand(uCommand='OPEN', arg0=iLocal_id, arg1=0,uData=uDestination + '\0')
        self.Send()
        uCmd, iRemote_id, iTheir_local_id, _ = self.Read(['CLSE', 'OKAY'])
        if iLocal_id != iTheir_local_id:
            raise Exception('cADB_Message:Open Expected the local_id to be %s, got %s' % (iLocal_id, iTheir_local_id))
        if uCmd == 'CLSE':
            # Device doesn't support this service
            Logger.error("Device doesn't support this service")
            return None
        if uCmd != 'OKAY':
            raise Exception('cADB_Message:Close Expected a ready response, got %s' % uCmd,uCmd, (iRemote_id, iTheir_local_id))
        self.oADB_Connection.SetConnectionParameter(iLocal_id, iRemote_id, fTimeOut)
        return True

    def Command(self, uService, uCommand='', fTimeOut=1.0):
        """One complete set of packets for a single command.

        Sends service:command in a new connection, reading the data for the
        response. All the data is held in memory, large responses will be slow and
        can fill up memory.

        Args:
          uService: The service on the device to talk to.
          uCommand: The command to send to the service.
          fTimeOut: Timeout , in seconds.

        Returns:
          The response from the service.
        """
        return ''.join(self.StreamingCommand(uService, uCommand, fTimeOut))

    def StreamingCommand(self, uService, uCommand='', fTimeOut=1.0):
        """One complete set of USB packets for a single command.

        Sends service:command in a new connection, reading the data for the
        response. All the data is held in memory, large responses will be slow and
        can fill up memory.

        Args:
          uService: The service on the device to talk to.
          uCommand: The command to send to the service.
          fTimeOut: Timeout , in seconds.

        Yields:
          The responses from the service.
        """
        if self.Open(uDestination='%s:%s' % (uService, uCommand),fTimeOut=fTimeOut):
            for uData in self.oADB_Connection.ReadUntilClose():
                yield uData

    def Close(self):
        self.oADB_Connection.Close()
        # self.oIP_Connection.Close()



# python-rsa lib hashes all messages it signs. ADB does it already, we just
# need to slap a signature on top of already hashed message. Introduce "fake"
# hashing algo for this.

class _Accum(object):
    def __init__(self):
        self._buf = ''
    def update(self, msg):
        self._buf += msg
    def digest(self):
        return self._buf

pkcs1.HASH_METHODS['SHA-1-PREHASHED'] = _Accum
pkcs1.HASH_ASN1['SHA-1-PREHASHED'] = pkcs1.HASH_ASN1['SHA-1']

def _load_rsa_private_key(pem):
    """PEM encoded PKCS#8 private key -> rsa.PrivateKey."""
    # ADB uses private RSA keys in pkcs#8 format. 'rsa' library doesn't support
    # them natively. Do some ASN unwrapping to extract naked RSA key
    # (in der-encoded form). See https://www.ietf.org/rfc/rfc2313.txt.
    # Also http://superuser.com/a/606266.
    try:
        der = rsa.pem.load_pem(pem, 'PRIVATE KEY')
        keyinfo, _ = decoder.decode(der)
        if keyinfo[1][0] != univ.ObjectIdentifier('1.2.840.113549.1.1.1'):  # pragma: no cover
            raise Exception('Not a DER-encoded OpenSSL private RSA key')
        private_key_der = keyinfo[2].asOctets()
    except IndexError:  # pragma: no cover
        raise Exception('Not a DER-encoded OpenSSL private RSA key')
    return rsa.PrivateKey.load_pkcs1(private_key_der, format='DER')


class PythonRSASigner(object):
    """Implements adb_protocol.AuthSigner using http://stuvel.eu/rsa."""
    @classmethod
    def FromRSAKeyPath(cls, rsa_key_path):
        with open(rsa_key_path + '.pub') as f:
            pub = f.read()
        with open(rsa_key_path) as f:
            priv = f.read()
        return cls(pub, priv)

    def __init__(self, pub=None, priv=None):
        self.priv_key = _load_rsa_private_key(priv)
        self.pub_key = pub

    def Sign(self, data):
        return rsa.sign(data, self.priv_key, 'SHA-1-PREHASHED')

    def GetPublicKey(self):
        return self.pub_key


class cADB_Helper(object):

    def __init__(self):
        self.aGlobalRSA_KEYS = []
        self.oADB_Commands = cADB_Commands()
        self.Load_RSA_KEYS()
    def Connect(self,uHost, uPort ,fTimeOut):
        return self.oADB_Commands.ConnectDevice(uHost=uHost, uPort=uPort,fTimeOut=fTimeOut,aRsa_keys=self.aGlobalRSA_KEYS)
    def Close(self):
        self.oADB_Commands.CloseWithConnection()

    def Load_RSA_KEYS(self):

        aKeyPathes = []

        #default adb key path
        aKeyPathes.append(cPath(OS_GetSystemUserPath()+'.android/adbkey'))

        #default Android Path
        if Globals.uPlatform==u'android':
            aKeyPathes.append(cPath(OS_GetSystemUserPath()+'misc/adb/adb_keys/adbkey'))

        #Download path
        aKeyPathes.append(Globals.oPathUserDownload+"/adbkey")

        for oPath in aKeyPathes:
            if oPath.Exists():
                try:
                    self.aGlobalRSA_KEYS.append(PythonRSASigner.FromRSAKeyPath(oPath.string))
                    Logger.info("RSA Keyfiles loaded from "+oPath)
                except Exception as e:
                    Logger.error("Error Loading RSA Keys from "+oPath.string+" "+str(e))
            else:
                Logger.debug("No RSA Keyfiles at "+oPath)


'''

28 –>  “KEYCODE_CLEAR”
55 –>  “KEYCODE_COMMA”
56 –>  “KEYCODE_PERIOD”
61 –>  “KEYCODE_TAB”
62 –>  “KEYCODE_SPACE”
63 –>  “KEYCODE_SYM”
64 –>  “KEYCODE_EXPLORER”
65 –>  “KEYCODE_ENVELOPE”

67 –>  “KEYCODE_DEL”
68 –>  “KEYCODE_GRAVE”

70 –>  “KEYCODE_EQUALS”
71 –>  “KEYCODE_LEFT_BRACKET”
72 –>  “KEYCODE_RIGHT_BRACKET”
73 –>  “KEYCODE_BACKSLASH”
74 –>  “KEYCODE_SEMICOLON”
75 –>  “KEYCODE_APOSTROPHE”
76 –>  “KEYCODE_SLASH”
77 –>  “KEYCODE_AT”
78 –>  “KEYCODE_NUM”
79 –>  “KEYCODE_HEADSETHOOK”
80 –>  “KEYCODE_FOCUS”

83 –>  “KEYCODE_NOTIFICATION”
84 –>  “KEYCODE_SEARCH” - 




public static final int KEYCODE_STB_INPUT
Added in API level 11
Key code constant: Set-top-box input key. On TV remotes, switches the input mode on an external Set-top-box.
Constant Value: 180 (0x000000b4)

public static final int KEYCODE_STB_POWER
Added in API level 11
Key code constant: Set-top-box power key. On TV remotes, toggles the power on an external Set-top-box.
Constant Value: 179 (0x000000b3)

public static final int KEYCODE_SWITCH_CHARSET
Added in API level 9
Key code constant: Switch Charset modifier key. Used to switch character sets (Kanji, Katakana).
Constant Value: 95 (0x0000005f)

public static final int KEYCODE_SYM
Added in API level 1
Key code constant: Symbol modifier key. Used to enter alternate symbols.
Constant Value: 63 (0x0000003f)
public static final int KEYCODE_SYSRQ
Added in API level 11

Key code constant: System Request / Print Screen key.
Constant Value: 120 (0x00000078)
public static final int KEYCODE_T
Added in API level 1



public static final int KEYCODE_TV_AUDIO_DESCRIPTION
Added in API level 21


Key code constant: Contents menu key. Goes to the title list. Corresponds to Contents Menu (0x0B) of CEC User Control Code
Constant Value: 256 (0x00000100)
public static final int KEYCODE_TV_DATA_SERVICE
Added in API level 21

Key code constant: TV data service key. Displays data services like weather, sports.
Constant Value: 230 (0x000000e6)
public static final int KEYCODE_TV_INPUT
Added in API level 11

Key code constant: TV input key. On TV remotes, switches the input on a television screen.
Constant Value: 178 (0x000000b2)
public static final int KEYCODE_TV_INPUT_COMPONENT_1
Added in API level 21

Key code constant: Component #1 key. Switches to component video input #1.
Constant Value: 249 (0x000000f9)
public static final int KEYCODE_TV_INPUT_COMPONENT_2
Added in API level 21

Key code constant: Component #2 key. Switches to component video input #2.
Constant Value: 250 (0x000000fa)
public static final int KEYCODE_TV_INPUT_COMPOSITE_1
Added in API level 21

Key code constant: Composite #1 key. Switches to composite video input #1.
Constant Value: 247 (0x000000f7)
public static final int KEYCODE_TV_INPUT_COMPOSITE_2
Added in API level 21

Key code constant: Composite #2 key. Switches to composite video input #2.
Constant Value: 248 (0x000000f8)
public static final int KEYCODE_TV_INPUT_HDMI_1
Added in API level 21

Key code constant: HDMI #1 key. Switches to HDMI input #1.
Constant Value: 243 (0x000000f3)
public static final int KEYCODE_TV_INPUT_HDMI_2
Added in API level 21

Key code constant: HDMI #2 key. Switches to HDMI input #2.
Constant Value: 244 (0x000000f4)
public static final int KEYCODE_TV_INPUT_HDMI_3
Added in API level 21

Key code constant: HDMI #3 key. Switches to HDMI input #3.
Constant Value: 245 (0x000000f5)
public static final int KEYCODE_TV_INPUT_HDMI_4
Added in API level 21

Key code constant: HDMI #4 key. Switches to HDMI input #4.
Constant Value: 246 (0x000000f6)
public static final int KEYCODE_TV_INPUT_VGA_1
Added in API level 21

Key code constant: VGA #1 key. Switches to VGA (analog RGB) input #1.
Constant Value: 251 (0x000000fb)
public static final int KEYCODE_TV_MEDIA_CONTEXT_MENU
Added in API level 21

Key code constant: Media context menu key. Goes to the context menu of media contents. Corresponds to Media Context-sensitive Menu (0x11) of CEC User Control Code.
Constant Value: 257 (0x00000101)
public static final int KEYCODE_TV_NETWORK
Added in API level 21

Key code constant: Toggle Network key. Toggles selecting broacast services.
Constant Value: 241 (0x000000f1)
public static final int KEYCODE_TV_NUMBER_ENTRY
Added in API level 21

Key code constant: Number entry key. Initiates to enter multi-digit channel nubmber when each digit key is assigned for selecting separate channel. Corresponds to Number Entry Mode (0x1D) of CEC User Control Code.
Constant Value: 234 (0x000000ea)
public static final int KEYCODE_TV_POWER
Added in API level 11

Key code constant: TV power key. On TV remotes, toggles the power on a television screen.
Constant Value: 177 (0x000000b1)
public static final int KEYCODE_TV_RADIO_SERVICE
Added in API level 21

Key code constant: Radio key. Toggles TV service / Radio service.
Constant Value: 232 (0x000000e8)
public static final int KEYCODE_TV_SATELLITE
Added in API level 21

Key code constant: Satellite key. Switches to digital satellite broadcast service.
Constant Value: 237 (0x000000ed)
public static final int KEYCODE_TV_SATELLITE_BS
Added in API level 21

Key code constant: BS key. Switches to BS digital satellite broadcasting service available in Japan.
Constant Value: 238 (0x000000ee)
public static final int KEYCODE_TV_SATELLITE_CS
Added in API level 21

Key code constant: CS key. Switches to CS digital satellite broadcasting service available in Japan.
Constant Value: 239 (0x000000ef)
public static final int KEYCODE_TV_SATELLITE_SERVICE
Added in API level 21

Key code constant: BS/CS key. Toggles between BS and CS digital satellite services.
Constant Value: 240 (0x000000f0)
public static final int KEYCODE_TV_TELETEXT
Added in API level 21

Key code constant: Teletext key. Displays Teletext service.
Constant Value: 233 (0x000000e9)
public static final int KEYCODE_TV_TERRESTRIAL_ANALOG
Added in API level 21

Key code constant: Analog Terrestrial key. Switches to analog terrestrial broadcast service.
Constant Value: 235 (0x000000eb)
public static final int KEYCODE_TV_TERRESTRIAL_DIGITAL
Added in API level 21

Key code constant: Digital Terrestrial key. Switches to digital terrestrial broadcast service.
Constant Value: 236 (0x000000ec)
public static final int KEYCODE_TV_TIMER_PROGRAMMING
Added in API level 21

Key code constant: Timer programming key. Goes to the timer recording menu. Corresponds to Timer Programming (0x54) of CEC User Control Code.
Constant Value: 258 (0x00000102)
public static final int KEYCODE_TV_ZOOM_MODE
Added in API level 21

Key code constant: Zoom mode key. Changes Zoom mode (Normal, Full, Zoom, Wide-zoom, etc.)
Constant Value: 255 (0x000000ff)
public static final int KEYCODE_U
Added in API level 1

Key code constant: 'U' key.
Constant Value: 49 (0x00000031)
public static final int KEYCODE_UNKNOWN
Added in API level 1

Key code constant: Unknown key code.
Constant Value: 0 (0x00000000)
public static final int KEYCODE_V
Added in API level 1

Key code constant: 'V' key.
Constant Value: 50 (0x00000032)
public static final int KEYCODE_VOICE_ASSIST
Added in API level 21

Key code constant: Voice Assist key. Launches the global voice assist activity. Not delivered to applications.
Constant Value: 231 (0x000000e7)
public static final int KEYCODE_VOLUME_DOWN
Added in API level 1

Key code constant: Volume Down key. Adjusts the speaker volume down.
Constant Value: 25 (0x00000019)
public static final int KEYCODE_VOLUME_MUTE
Added in API level 11

Key code constant: Volume Mute key. Mutes the speaker, unlike KEYCODE_MUTE. This key should normally be implemented as a toggle such that the first press mutes the speaker and the second press restores the original volume.
Constant Value: 164 (0x000000a4)
public static final int KEYCODE_VOLUME_UP
Added in API level 1



public static final int KEYCODE_WINDOW
Added in API level 11

Key code constant: Window key. On TV remotes, toggles picture-in-picture mode or other windowing functions.
Constant Value: 171 (0x000000ab)
public static final int KEYCODE_X
Added in API level 1


Key code constant: Zoom in key.
Constant Value: 168 (0x000000a8)
public static final int KEYCODE_ZOOM_OUT
Added in API level 11

Key code constant: Zoom out key.
Constant Value: 169 (0x000000a9)



'''

