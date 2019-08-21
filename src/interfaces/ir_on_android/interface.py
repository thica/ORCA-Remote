# -*- coding: utf-8 -*-
# Infrared on Android devices using build in transmitter

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

from kivy.logger                import Logger
from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.vars.Replace          import ReplaceVars
from ORCA.utils.TypeConvert     import ToInt
import ORCA.Globals as Globals

try:
    # noinspection PyUnresolvedReferences
    from   plyer                 import irblaster
except Exception as e:
    Logger.info("plyer not available")
    pass

'''
<root>
  <repositorymanager>
    <entry>
      <name>IR Control on Android devices</name>
      <description language='English'>Send IR Commands on Android devices with IR tranmitter WIP</description>
      <description language='German'>Sendet IR Befehle auf Android Geräten mit eingebautem IR Sender WIP</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/interfaces/ir_on_android</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/interfaces/ir_on_android.zip</sourcefile>
          <targetpath>interfaces</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>interfaces</type>
          <name>Generic Infrared Interface</name>
        </dependency>
      </dependencies>
      <skipfiles>
        <file>ir_on_android/interface.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


oBaseInterFaceInfrared = Globals.oInterFaces.LoadInterface('generic_infrared')

class cInterface(oBaseInterFaceInfrared.cInterface):

    class cInterFaceSettings(oBaseInterFaceInfrared.cInterface.cInterFaceSettings):
        def __init__(self,oInterFace):
            oBaseInterFaceInfrared.cInterface.cInterFaceSettings.__init__(self,oInterFace)
            self.bIsConnected = False
            self.bOnError     = False

        def Connect(self):

            self.bIsConnected = False
            if not oBaseInterFaceInfrared.cInterface.cInterFaceSettings.Connect(self):
                Logger.debug("ir_on_android: Connect cancelled by root class")
                return False
            try:
                if irblaster.exists():
                    self.ShowDebug("Connected")
                    self.bIsConnected = True
                    return True
                else:
                    self.ShowDebug("No Ir-Blaster at device")
                    self.bIsConnected = False

            except Exception as e:
                self.ShowError(u'Cannot open IR Device',e)
                self.bOnError=True
            return False

        def Disconnect(self):
            if oBaseInterFaceInfrared.cInterface.cInterFaceSettings.Disconnect(self):
                return False


    def __init__(self):
        oBaseInterFaceInfrared.cInterface.__init__(self)
        self.aSettings   = {}
        self.oSetting = None
    def Init(self, uObjectName, oFnObject=None):
        cBaseInterFace.Init(self,uObjectName, oFnObject)
        self.oObjectConfig.dDefaultSettings['FNCodeset']['active']                   = "enabled"

    def DeInit(self, **kwargs):
        oBaseInterFaceInfrared.cInterface.DeInit(self,**kwargs)
        for aSetting in self.aSettings:
            self.aSettings[aSetting].DeInit()

    def SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut=False):
        cBaseInterFace.SendCommand(self,oAction,oSetting,uRetVar,bNoLogOut)

        iRet=1

        if oAction.uCCF_Code != u"":
            oAction.oIRCode=CCfToAndroidIR(oAction.uCCF_Code,ToInt(oAction.uRepeatCount))
            oAction.uCCF_Code = u""

        uCmd=ReplaceVars(oAction.uCmd)

        self.ShowInfo(u'Sending Command: '+uCmd + u' to '+oSetting.uConfigName)

        oSetting.Connect()
        if oSetting.bIsConnected:
            try:
                Logger.debug("Sending IR Commend to IRBLASTER")
                irblaster.transmit(oAction.oIRCode.iFrequency,oAction.oIRCode.aPattern)
            except Exception as e:
                self.ShowWarning(u'Can\'t send message: '+e.message,oSetting.uConfigName)
        else:
            Logger.debug("Not Connected")
        return iRet

class cIRCommand(object):
    """ Object to hold an Android  IR Command  """
    def __init__(self,iFrequency, aPattern):
        self.iFrequency=iFrequency
        self.aPattern=aPattern

def CCfToAndroidIR(sCCFString,iRepeatCount):
    iCount = 0
    aList = sCCFString.split(" ")
    iFrequency = int(aList[1], 16)
    aList=aList[3:]
    iFrequency = ToInt(iFrequency * 0.241246)
    iPulses = int(1000000 / iFrequency)
    aPattern = []
    for uElem in aList:
        iCount = int(uElem, 16)
        aPattern.append(int(iCount*iPulses))
    return cIRCommand(iFrequency, aPattern)

'''

    // based on code from http://stackoverflow.com/users/1679571/randy (http://stackoverflow.com/a/25518468)
    private IRCommand hex2ir(final String irData) {
        List<String> list = new ArrayList<String>(Arrays.asList(irData.split(" ")));
        list.remove(0); // dummy
        int frequency = Integer.parseInt(list.remove(0), 16); // frequency
        list.remove(0); // seq1
        list.remove(0); // seq2

        frequency = (int) (1000000 / (frequency * 0.241246));
        int pulses = 1000000 / frequency;
        int count;

        int[] pattern = new int[list.size()];
        for (int i = 0; i < list.size(); i++) {
            count = Integer.parseInt(list.get(i), 16);
            pattern[i] = count * pulses;
        }

        return new IRCommand(frequency, pattern);
    }

'''
