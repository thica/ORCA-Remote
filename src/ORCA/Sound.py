# -*- coding: utf-8 -*-
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

from typing                         import Any
from typing                         import cast
from typing                         import List
from typing                         import Dict
from typing                         import Union
from typing                         import Optional
#from typing                         import TypedDict
from enum                           import Enum
from enum                           import auto


from xml.etree.ElementTree          import Element
from kivy.core.audio                import SoundLoader
from kivy.logger                    import Logger
from kivy.config                    import ConfigParser
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp
from ORCA.utils.LogError            import LogError
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import LoadXMLFile
from ORCA.utils.TypeConvert         import ToFloat
from ORCA.utils.TypeConvert         import ToBool
from ORCA.utils.Platform            import OS_RegisterSoundProvider
from ORCA.utils.ConfigHelpers       import Config_GetDefault_Int
from ORCA.utils.FileName            import cFileName

from ORCA.Globals import Globals

__all__ = ['cSound']

'''
# reserved for python 3.8
class dSoundDef(TypedDict):
    """
    Little typing helper
    """
    oFnSound: Optional[cFileName]
    iSoundVolume: int
'''

dSoundDef = Dict

class cSound:
    """ Represents the Sound Object """

    class eSounds(Enum):
        startup         = auto()
        shutdown        = auto()
        error           = auto()
        message         = auto()
        question        = auto()
        notification    = auto()
        ring            = auto()
        success         = auto()
        click           = auto()

    def __init__(self) ->None:

        self.aSounds: Dict[Union[str,Enum], dSoundDef] = {}

        for uName, eValue in self.eSounds.__members__.items():
            self.aSounds[uName]  = {'oFnSound':None,'iSoundVolume':100}
            self.aSounds[eValue] = self.aSounds[uName]

        self.dSoundObjects:Dict[str,Any] = {}
        self.aSoundsList:List[str]       = []                      # List of all available soundsets (Just their names)
        self.bMute                       = False
        ## OS_RegisterSoundProvider()

    def Init(self) ->None:
        """ get a list of all sounds """
        self.aSoundsList = Globals.oPathSoundsRoot.GetFolderList()

    def LoadSoundsDescription(self) ->None:
        """ Loads the sound description (tunes) """
        try:
            Logger.debug ('TheScreen: Loading Sounds')
            oET_Root:Element = LoadXMLFile(oFile=Globals.oFnSoundsXml)

            if oET_Root is not None:
                for oXMLSound in oET_Root.findall('sound'):
                    uSoundName:str      = GetXMLTextAttribute(oXMLNode=oXMLSound,uTag='name',bMandatory=False,vDefault='')
                    oFnSound:cFileName  = cFileName(GetXMLTextAttribute(oXMLNode=oXMLSound,uTag='file',bMandatory=False,vDefault=''))
                    if uSoundName in self.aSounds:
                        self.aSounds[uSoundName]['oFnSound']=oFnSound
                    else:
                        Logger.warning('Unknown Sound:'+oFnSound)
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg='TheScreen: LoadSoundDescription: can\'t load SoundDescription',oException=e))

    def ReadSoundVolumesFromConfig(self,*,oConfig:ConfigParser) -> None:
        """
        Reads the sound volumes from the given configparser
        """
        for uSoundName in self.aSounds:
            if isinstance(uSoundName,str):
                self.SetSoundVolume(SoundName=uSoundName,iValue=Config_GetDefault_Int(oConfig=oConfig, uSection='ORCA', uOption='soundvolume_' + uSoundName, uDefaultValue='100'))
        self.bMute = ToBool(Config_GetDefault_Int(oConfig=oConfig, uSection='ORCA', uOption='sound_muteall', uDefaultValue='0'))

    def SetSoundVolume(self,*,SoundName:Union[str,Enum],iValue:int) -> None:
        """
        Sets the volume for a give sound
        :param SoundName: The name of the sound
        :param int iValue: The sound volume (0-100)
        :return:
        """
        self.aSounds[SoundName]['iSoundVolume'] = iValue
        return None

    def PlaySound(self,*,SoundName:Union[str,Enum], vSoundVolume:Union[float,str]=-1.0) -> bool:
        """ plays a given sound with a given volume """

        iSoundVolume:int
        fVolume:float
        vVolume:Union[str,float]
        dSound:Optional[Dict[str,Union[cFileName,int]]]
        oFnSound:cFileName

        if self.bMute:
            return True

        try:
            dSound = self.aSounds.get(SoundName)
            vVolume = vSoundVolume
            if dSound is not None:
                oFnSound     = dSound['oFnSound']
                iSoundVolume = dSound['iSoundVolume']
            else:
                oFnSound=cFileName(SoundName)
                iSoundVolume=100

            if oFnSound and not oFnSound.IsEmpty():
                oSound=self.dSoundObjects.get(str(oFnSound))
                # temporary disabled
                if oSound is None or True:
                    oSound = SoundLoader.load(str(oFnSound))
                    self.dSoundObjects[str(oFnSound)]=oSound
                if oSound:
                    if oSound.state != 'stop':
                        oSound.stop()

                    if isinstance(vSoundVolume, str):
                        if vSoundVolume!='':
                            vVolume = ToFloat(vSoundVolume)

                    if not vVolume==-1.0 and not vVolume=='':
                        fVolume = cast(float,vVolume)*(iSoundVolume/100.0)
                    else:
                        fVolume = iSoundVolume*1.0

                    fVolume = fVolume /100.0
                    oSound.volume = fVolume

                    if fVolume>0:
                        oSound.play()

            return True
        except Exception as e:
            LogError(uMsg='Playing sound failed:'+str(SoundName),oException=e)
            return False
