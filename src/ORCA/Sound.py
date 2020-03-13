# -*- coding: utf-8 -*-
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2020  Carsten Thielepape
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
from typing                         import List
from typing                         import Dict
from typing                         import Union

from xml.etree.ElementTree          import Element
from kivy.core.audio                import SoundLoader
from kivy.logger                    import Logger
from kivy.config                    import ConfigParser
from ORCA.ui.ShowErrorPopUp         import ShowErrorPopUp
from ORCA.utils.LogError            import LogError
from ORCA.utils.XML                 import GetXMLTextAttribute
from ORCA.utils.XML                 import LoadXMLFile
from ORCA.utils.TypeConvert         import ToFloat
from ORCA.utils.Platform            import OS_RegisterSoundProvider
from ORCA.utils.ConfigHelpers       import Config_GetDefault_Int
from ORCA.utils.FileName            import cFileName


import ORCA.Globals as Globals

__all__ = ['cSound']

class cSound:
    """ Represents the Sound Object """
    def __init__(self):
        self.aSounds:Dict[str,List] = { u'startup'     :[None,100],
                                        u'shutdown'    :[None,100],
                                        u'error'       :[None,100],
                                        u'message'     :[None,100],
                                        u'question'    :[None,100],
                                        u'notification':[None,100],
                                        u'ring'        :[None,100],
                                        u'success'     :[None,100],
                                        u'click'       :[None,100]}

        self.dSoundObjects:Dict[str,Any] = {}
        self.aSoundsList:List[str]       = []                      # List of all available soundsets (Just their names)
        OS_RegisterSoundProvider()

    def Init(self):
        """ get a list of all sounds """
        self.aSoundsList = Globals.oPathSoundsRoot.GetFolderList()

    def LoadSoundsDescription(self):
        """ Loads the sound description (tunes) """
        try:
            Logger.debug (u'TheScreen: Loading Sounds')
            oET_Root:Element = LoadXMLFile(oFile=Globals.oFnSoundsXml)

            if oET_Root is not None:
                for oXMLSound in oET_Root.findall('sound'):
                    uSoundName:str      = GetXMLTextAttribute(oXMLNode=oXMLSound,uTag=u'name',bMandatory=False,vDefault=u'')
                    oFnSound:cFileName  = cFileName('').ImportFullPath(uFnFullName=GetXMLTextAttribute(oXMLNode=oXMLSound,uTag=u'file',bMandatory=False,vDefault=u''))
                    if uSoundName in self.aSounds:
                        self.aSounds[uSoundName][0]=oFnSound
                    else:
                        Logger.warning(u'Unknown Sound:'+oFnSound)
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg=u'TheScreen:  LoadSoundDescription: can\'t load SoundDescription',oException=e))

    def ReadSoundVolumesFromConfig(self,*,oConfig:ConfigParser) -> None:
        """
        Reads the sound volumes from the given configparser
        """
        for uSoundName in self.aSounds:
            self.SetSoundVolume(uSoundName=uSoundName,iValue=Config_GetDefault_Int(oConfig=oConfig, uSection=u'ORCA', uOption=u'soundvolume_' + uSoundName, uDefaultValue=u'100'))

    def SetSoundVolume(self,*,uSoundName:str,iValue:int):
        self.aSounds[uSoundName][1] = iValue

    def PlaySound(self,*,uSoundName:str, vSoundVolume:Union[float,str]=-1.0):
        """ plays a given sound with a given volume """
        iSoundVolume:int
        fVolume:float
        vVolume:Union[str,float]
        aTup:List
        oFnSound:cFileName

        try:
            aTup = self.aSounds.get(uSoundName)
            vVolume = vSoundVolume
            if aTup:
                oFnSound  = aTup[0]
                iSoundVolume = aTup[1]
            else:
                oFnSound=cFileName('').ImportFullPath(uFnFullName=uSoundName)
                iSoundVolume=100

            if oFnSound and not oFnSound.IsEmpty():
                oSound=self.dSoundObjects.get(oFnSound.string)
                # temporary disabled
                if oSound is None or True:
                    oSound = SoundLoader.load(oFnSound.string)
                    self.dSoundObjects[oFnSound.string]=oSound
                if oSound:
                    if oSound.state != 'stop':
                        oSound.stop()

                    if isinstance(vSoundVolume, str):
                        if vSoundVolume!=u'':
                            vVolume = ToFloat(vSoundVolume)

                    if not vVolume==-1.0 and not vVolume==u'':
                        fVolume = vVolume*(iSoundVolume/100.0)
                    else:
                        fVolume = iSoundVolume*1.0

                    fVolume = fVolume /100.0
                    oSound.volume = fVolume

                    if fVolume>0:
                        oSound.play()
            return True
        except Exception as e:
            LogError(uMsg=u'Playing sound failed:'+uSoundName,oException=e)
            return False
