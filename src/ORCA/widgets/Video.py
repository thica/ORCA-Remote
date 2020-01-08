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

from typing                         import Tuple
from xml.etree.ElementTree          import Element
from kivy.uix.widget                import Widget
from kivy.uix.video                 import Video
from kivy.logger                    import Logger
from ORCA.widgets.base.Base         import cWidgetBase
from ORCA.utils.TypeConvert         import ToUnicode
from ORCA.utils.LogError            import LogError
from ORCA.utils.FileName            import cFileName

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.ScreenPage            import cScreenPage
else:
    from typing import TypeVar
    cScreenPage   = TypeVar("cScreenPage")

__all__ = ['cWidgetVideo']

class cWidgetVideo(cWidgetBase):
    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-VIDEO
    WikiDoc:TOCTitle:Video
    = VIDEO =

    The Video widgets shows a viddeo or a video stream. Supported codecs various by platform. To control the Video Widget (stream address, start, stop, pause,....) you need to enter the name of the widget to a configuration of the ORCA-Video interface. Then you have to send the control commands to the interface. sing the update widget action, you can change the stream address.

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "VIDEO". Capital letters!
    |}</div>

    Below you see an example for a video widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name="VIDEO 1" type="VIDEO" height="of:width:self:*0.75" />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    # noinspection PyUnusedLocal
    def __init__(self,**kwargs):
        super(cWidgetVideo, self).__init__()
        self.bRepeat:bool           = False
        self.fOldVolume:float       = -1.0
        self.iOldPosition:int       = -1
        self.iOldDuration:int       = -1
        self.oConnection            = None
        self.uFileName:str          = ''
    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Connect(self,oConnection):
        """ connects to the stream or file """
        self.oConnection = oConnection

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        try:
            if self.CreateBase(Parent=oParent, Class=Video):
                self.oParent.add_widget(self.oObject)
                self.oObject.bind(position=self.On_Position_change,duration=self.On_Duration_Change)
                return True
            return False
        except Exception as e:
            LogError(uMsg=u'Widget:Video:Error on Create',oException=e)
            return False

    # noinspection PyUnusedLocal
    def On_Position_change(self,instance:Video, value:str) -> None:
        """ Handles the change of the position """
        if self.oConnection:
            iPosition:int=int(value)
            if not iPosition==self.iOldPosition:
                self.iOldPosition = iPosition
                self.oConnection.Receive(u'position:'+ToUnicode(iPosition))

    # noinspection PyUnusedLocal
    def On_Duration_Change(self,instance:Video, value:str) -> None:
        """ Handle the change of the Duration """
        if self.oConnection:
            iDuration:int=int(value)
            if iDuration!=self.iOldDuration:
                self.iOldDuration = iDuration
                self.oConnection.Receive(u'duration:'+ToUnicode(iDuration))

    def SetFileName(self,uFileName:str) -> bool:
        """ Sets the filename or stream """
        try:
            if self.oObject:
                self.uFileName=uFileName.encode('utf8')
                self.oObject.source=self.NormalizeStream(uFileName)
                return True
            else:
                Logger.warning('Widget Video: You can''t set Filename before object is created:'+uFileName)

        except Exception as e:
            LogError(uMsg=u'Widget:Video:Error on SetFileName:'+uFileName,oException=e)

        return False
    # noinspection PyMethodMayBeStatic
    def NormalizeStream(self,uStream:str) -> str:
        """ Normalizes the stream name """
        if not uStream.startswith('rtsp') and uStream.startswith('http'):
            uStream  = (cFileName(u'').ImportFullPath(uStream)).string
        if Globals.uPlatform!='win':
            # prevent bug in ffmpeg (Android) not able to deal with unicode strings
            # todo: check with later kivy/ffmpeg versions
            uStream=uStream.encode('utf8')
        return uStream

    def StatusControl(self,uStatus:str,uStream:str) -> Tuple[int,str]:
        """ Controls the video stream """
        try:
            if uStatus==u'play':
                self.oObject.source=self.NormalizeStream(uStream)
                self.oObject.state = 'play'
                return 0,''
            if uStatus==u'stop':
                self.oObject.state = 'stop'
                return 0,''
            if uStatus==u'pause':
                self.oObject.state = 'pause'
                return 0,''
            if uStatus==u'getvolume':
                return 0,ToUnicode(self.oObject.volume)
            if uStatus==u'volume_down':
                self.oObject.volume=max(0.0,self.oObject.volume-0.05)
                return 0,ToUnicode(self.oObject.volume)
            if uStatus==u'volume_up':
                self.oObject.volume=min(1.0,self.oObject.volume+0.05)
                return 0,ToUnicode(self.oObject.volume)
            if uStatus==u'repeat_toggle':
                self.bRepeat=not self.bRepeat
                return 0,ToUnicode(self.bRepeat)
            if uStatus==u'repeat_on':
                self.bRepeat=True
                return 0,ToUnicode(self.bRepeat)
            if uStatus==u'repeat_off':
                self.bRepeat=False
                return 0,ToUnicode(self.bRepeat)
            if uStatus==u'mute_on':
                if self.oObject.volume!=0:
                    self.fOldVolume=self.oObject.volume
                    self.oObject.volume=0
                return 0,ToUnicode(self.oObject.volume)
            if uStatus==u'mute_off':
                if self.fOldVolume!=-1:
                    self.oObject.volume=self.fOldVolume
                return 0,ToUnicode(self.oObject.volume)
            if uStatus==u'mute_toggle':
                if self.oObject.volume!=0:
                    self.fOldVolume=self.oObject.volume
                    self.oObject.volume=0
                elif self.fOldVolume!=-1:
                    self.oObject.volume=self.fOldVolume
                return 0,ToUnicode(self.oObject.volume)
        except Exception as e:
            LogError(uMsg=u'Widget:Video:Error on Statuscontrol:'+uStatus,oException=e)

        return 0,''
