# -*- coding: utf-8 -*-
#

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


from typing                                 import Dict
from typing                                 import Union
from datetime                               import datetime
from datetime                               import timedelta

import hashlib


from ORCA.scripts.BaseScript                import cBaseScript
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.vars.Access                       import SetVar
from ORCA.utils.TypeConvert                 import ToInt
from ORCA.utils.FileName                    import cFileName

from ORCA.Globals import Globals



'''
<root>
  <repositorymanager>
    <entry>
      <name>Fritz Smarthome Helper Script</name>
      <description language='English'>Fritz Smarthome Helper Script</description>
      <description language='German'>Fritz Smarthome Hilfs - Skript</description>
      <author>Carsten Thielepape</author>
      <version>6.0.0</version>
      <minorcaversion>6.0.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/helper/helper_fritz_smarthome</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/helper_fritz_smarthome.zip</sourcefile>
          <targetpath>scripts/helper</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

class cScript(cBaseScript):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-helper_fritz_smarthome
    WikiDoc:TOCTitle:Helper Script Fritz Smarthome
    = Fritz Smarthome Helper =

    This is a helper script for Fritz Smarthome commends
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |cmd_type
    |The requested helper function: can be "calculate_password_hash"
    |-
    |resultvar
    |for "parse_services": The name of the var which holds the servielist to parse. Not the result itself
    |-
    |definitionalias
    |For assign_channels: The alias name of the TV Template definition
    |-
    |interface
    |For assign_channels, parse_services: The interface name for the Enigma2 Control
    |-
    |configname
    |For assign_channels, parse_services: The config name for the Enigma2 Control
    |-
    |force
    |For assign_channels: 0/1 Replace all (1) of only unconfigured channels (with name "discover")
    |-
    |retvar
    |for get_channelreference: The var name for the result (the reference)
    |-
    |channelnum
    |for get_channelreference: The channelnum to get the reference for
    |-
    |logopackfoldername
    |For assign_channels: the name of the folder (only the folder name, not the fullpath) in "recources" , below "tvlogos"
    |}</div>

    Remarks:
    "parse_services": Needs to done first, Reads all services for a specific Enigma box into the script
    "get_channelreference": Will return the channel reference for a channel number
    "assign_channels": Sets the TV Logos for the parsed channels

    WikiDoc:End
    """

    def __init__(self):
        super().__init__()
        self.uType:str                  = 'HELPERS'
        self.uIniFileLocation:str       = 'none'

    def Init(self, uObjectName: str, oFnObject: Union[cFileName, None] = None) -> None:
        """ Main Init, loads the Enigma Script"""
        super().Init(uObjectName= uObjectName,oFnObject=oFnObject)

    def RunScript(self, *args, **kwargs) -> Union[Dict,None]:
        """ Main Entry point, parses the cmd_type and calls the relevant functions """
        uCmdType:str
        try:
            if 'cmd_type' in kwargs:
                uCmdType = kwargs['cmd_type']
                if uCmdType == 'calculate_password_hash':
                    return self.CalculatePasswordHash(**kwargs)
                if uCmdType == 'addtime':
                    return self.AddTime(**kwargs)

            return None
        except Exception as e:
            self.ShowError(uMsg='Can\'t run Enigma Helper script, invalid parameter',uParConfigName=self.uConfigName,oException=e)
            return {"ret":1}

    def CalculatePasswordHash(self, **kwargs) -> Dict:
        """Calculate response for the challenge-response authentication
           To be called from a codeset in the codeset context  """

        uChallenge:str
        uPassword:str
        bToHash:bytes
        uHashed:str
        uDstVarName:str
        uInterfaceName:str
        uConfigName:str
        uResult:str

        try:
            uDstVarName     = kwargs['retvar']
            uInterfaceName  = ReplaceVars(kwargs['interface'])
            uConfigName     = ReplaceVars(kwargs['configname'])

            oInterFace      = Globals.oInterFaces.GetInterface(uInterfaceName)
            oSetting        = oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
            uChallenge      = oSetting.GetContextVar(uVarName=kwargs['challenge'])
            uPassword       = oSetting.GetContextVar(uVarName=kwargs['password'])

            bToHash         = (uChallenge + "-" + uPassword).encode("UTF-16LE")
            uHashed         = hashlib.md5(bToHash).hexdigest()
            uResult         = "{0}-{1}".format(uChallenge, uHashed)
            oSetting.SetContextVar(uVarName=uDstVarName, uVarValue=uResult)
            return {}
        except Exception as e:
            self.ShowError(uMsg='helper_fritz_smarthome: Error to calculate password hash', uParConfigName=self.uConfigName, oException=e)
        return {}

    def ParseResult(self, **kwargs) -> Dict:
        pass

    def AddTime(self, **kwargs) -> Dict:

        """Adds a time in seconds to the current time in seconds (started 1.1.1970
           To be called from a codeset in the codeset context  """

        uDstVarName:str
        iSecondsFromStart:int
        iAddSeconds:int
        iNewTime:int
        oDateFromStart:datetime

        try:
            uDstVarName     = kwargs['retvar']
            uInterfaceName  = ReplaceVars(kwargs['interface'])
            uConfigName     = ReplaceVars(kwargs['configname'])
            oInterFace      = Globals.oInterFaces.GetInterface(uInterfaceName)
            oSetting        = oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
            iAddSeconds     = ToInt(oSetting.GetContextVar(uVarName=kwargs['seconds']))

            oDateFromStart  = datetime.fromtimestamp(0) + timedelta(seconds=datetime.now().timestamp())
            iSecondsFromStart = int(oDateFromStart.timestamp())
            iNewTime          = iSecondsFromStart + iAddSeconds
            oSetting.SetContextVar(uVarName=uDstVarName, uVarValue=str(iNewTime ))
        except Exception as e:
            self.ShowError(uMsg='helper_fritz_smarthome: Error to calculate time', uParConfigName=self.uConfigName, oException=e)
        return {}

    def ParseBitmask(self, **kwargs) -> Dict:

        uDstVarName:str
        uBitMask:str
        uResult:str

        try:
            uDstVarName     = kwargs['retvar']
            uBitMask        = ReplaceVars(kwargs['bitmask'])

            SetVar(uVarName=uDstVarName ,  oVarValue=uResult)

        except Exception as e:
            self.ShowError(uMsg='helper_fritz_smarthome: Error to identify bitmask', uParConfigName=self.uConfigName, oException=e)
        return {}

'''
Bit 0: HAN-FUN Gerät
Bit 2: Licht/Lampe
Bit 4: Alarm-Sensor
Bit 5: AVM-Button
Bit 6: Heizkörperregler
AHA-HTTP-API 8/17 © AVM GmbH
Bit 7: Energie Messgerät
Bit 8: Temperatursensor
Bit 9: Schaltsteckdose
Bit 10: AVM DECT Repeater
Bit 11: Mikrofon
Bit 13: HAN-FUN-Unit
Bit 15: an-/ausschaltbares Gerät/Steckdose/Lampe/Aktor
Bit 16: Gerät mit einstellbarem Dimm-, Höhen- bzw. Niveau-Level
Bit 17: Lampe mit einstellbarer Farbe/Farbtemperatur
Bit 18: Rollladen(Blind) - hoch, runter, stop und level 0% bis 100 %1

'''