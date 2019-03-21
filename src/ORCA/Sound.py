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


from kivy.core.audio                import SoundLoader
from kivy.compat                    import string_types
from kivy.logger                    import Logger

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

class cSound(object):
    """ Represents the Sound Object """
    def __init__(self):
        self.aSounds = {u'startup'     :[None,100],
                        u'shutdown'    :[None,100],
                        u'error'       :[None,100],
                        u'message'     :[None,100],
                        u'question'    :[None,100],
                        u'notification':[None,100],
                        u'ring'        :[None,100],
                        u'success'     :[None,100],
                        u'click'       :[None,100]}

        self.dSoundObjects = {}
        self.aSoundsList   = None                      # List of all available soundsets (Just their names)
        OS_RegisterSoundProvider()

    def Init(self):
        """ get a list of all sounds """
        self.aSoundsList            = Globals.oPathSoundsRoot.GetFolderList()

    def LoadSoundsDescription(self):
        """ Loads the sound description (tunes) """
        try:
            Logger.debug (u'TheScreen: Loading Sounds')
            oET_Root = LoadXMLFile(Globals.oFnSoundsXml)

            if oET_Root is not None:
                for oXMLSound in oET_Root.findall('sound'):
                    uSoundName  = GetXMLTextAttribute(oXMLSound,u'name',False,u'')
                    oFnSound  = cFileName('').ImportFullPath(GetXMLTextAttribute(oXMLSound,u'file',False,u''))
                    if uSoundName in self.aSounds:
                        self.aSounds[uSoundName][0]=oFnSound
                    else:
                        uMsg=Logger.warning(u'Unknown Sound:'+oFnSound)
        except Exception as e:
            uMsg=LogError(u'TheScreen:  LoadSoundDescription: can\'t load SoundDescription',e)
            ShowErrorPopUp(uMessage=uMsg)

    def ReadSoundVolumesFromConfig(self,oConfig):
        for uSoundName in self.aSounds:
            self.SetSoundVolume(uSoundName,Config_GetDefault_Int(oConfig, u'ORCA', u'soundvolume_' + uSoundName, u'100'))

    def SetSoundVolume(self,uSoundName,iValue):
        self.aSounds[uSoundName][1] = iValue

    def PlaySound(self,uSoundName, fSoundVolume=-1):

        """ plays a given sound with a given volume """
        try:
            oTup = self.aSounds.get(uSoundName)
            fVolume = fSoundVolume
            if oTup:
                oFnSound  = oTup[0]
                iSoundVolume = oTup[1]
            else:
                oFnSound=cFileName('').ImportFullPath(uSoundName)
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

                    if isinstance(fSoundVolume, string_types):
                        if fSoundVolume!=u'':
                            fVolume=ToFloat(fSoundVolume)

                    if not fVolume==-1 and not fVolume==u'':
                        fVolume=fVolume*(iSoundVolume/100.0)
                    else:
                        fVolume=iSoundVolume

                    fVolume=fVolume /100.0
                    oSound.volume=fVolume

                    if fVolume>0:
                        oSound.play()
            return True
        except Exception as e:
            LogError(u'Playing sound failed:'+uSoundName,e)
            return False
