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


import os.path as op

from adb import adb_commands
# from adb import sign_cryptography

from kivy.logger            import Logger
from kivy.compat            import PY2

from ORCA.utils.Path        import cPath
from ORCA.utils.Platform    import OS_GetSystemUserPath


import ORCA.Globals as Globals


class cADB_Helper(object):

    def __init__(self):
        self.aGlobalRSA_KEYS = []
        self.Load_RSA_KEYS()

        # KitKat+ devices require authentication
        # Connect to the device
        self.oADB_Commands = adb_commands.AdbCommands()

    def Connect(self,uHost, uPort ,fTimeOut):
        # device.ConnectDevice(rsa_keys=[signer])
        # signer = sign_cryptography.CryptographySigner(op.expanduser('~/.android/adbkey'))


        '''

        Args:
          port_path: The filename of usb port to use.
          serial: The serial number of the device to use.
          default_timeout_ms: The default timeout in milliseconds to use.
          kwargs: handle: Device handle to use (instance of common.TcpHandle or common.UsbHandle)
                  banner: Connection banner to pass to the remote device
                  rsa_keys: List of AuthSigner subclass instances to be used for
                      authentication. The device can either accept one of these via the Sign
                      method, or we will send the result of GetPublicKey from the first one
                      if the device doesn't accept any of them.
                  auth_timeout_ms: Timeout to wait for when sending a new public key. This
                      is only relevant when we send a new public key. The device shows a
                      dialog and this timeout is how long to wait for that dialog. If used
                      in automation, this should be low to catch such a case as a failure
                      quickly; while in interactive settings it should be high to allow
                      users to accept the dialog. We default to automation here, so it's low
                      by default.
        '''

        try:
            self.oADB_Commands.ConnectDevice(serial=uHost+":"+uPort,auth_timeout_ms=fTimeOut*1000)
            return True
        except Exception as e:
            print (e)
            return False


        # return self.oADB_Commands.ConnectDevice(uHost=uHost, uPort=uPort,fTimeOut=fTimeOut,aRsa_keys=self.aGlobalRSA_KEYS)
    def Close(self):
        self.oADB_Commands.close()

    def Load_RSA_KEYS(self):

        # default adb key path
        aKeyPathes = [cPath(OS_GetSystemUserPath() + '.android/adbkey')]

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

