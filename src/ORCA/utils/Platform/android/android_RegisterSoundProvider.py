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


AudioAndroid: implementation of Sound with Android Core Function

"""

from jnius                                import detach
from ORCA.utils.LogError                  import LogError
from ORCA.utils.Platform.android_helper   import GetAndroidModule



from kivy.logger        import Logger
Logger.debug("Loading Module android_RegisterSoundprovider")



from kivy.clock         import Clock
from kivy.core.audio    import Sound, SoundLoader
from kivy.logger        import Logger


oMPlayer = None

try:
    # noinspection PyUnresolvedReferences
    from jnius import autoclass
    # noinspection PyUnresolvedReferences
    from jnius import detach
    oMediaPlayer  = autoclass('android.media.MediaPlayer')
    oMPlayer      = oMediaPlayer()
    Logger.debug("Sucessfully loaded autoclass, detach, Mediaplayer")
except Exception as e:
    Logger.error("Can't load Android Mediaplayer from jnius")
    Logger.error(e.message)


class SoundAndroid(Sound):

    _check_play_ev = None

    @staticmethod
    def extensions():
        return u'mp3'

    def __init__(self, *args, **kwargs):
        self._data      = oMPlayer
        self.start_time = 0
        self.secs       = 0
        super(SoundAndroid, self).__init__(**kwargs)

    def _check_play(self, p_dt):
        if self.state == 'play':
            return
        if self.loop:
            def do_loop(p_dt):
                self.play()
            Clock.schedule_once(do_loop)
        else:
            self.stop()
        return False

    def play(self):
        if not self._data:
            return
        self._data.setVolume(self.volume ,self.volume )
        self._data.setVolume(1.0,1.0)

        self._data.start()
        self.start_time = Clock.time()
        # schedule event to check if the sound is still playing or not
        self._check_play_ev = Clock.schedule_interval(self._check_play, 0.1)
        super(SoundAndroid, self).play()

    def stop(self):
        if not self._data:
            return
        self._data.stop()
        self.secs=0
        # ensure we don't have anymore the callback
        if self._check_play_ev is not None:
            self._check_play_ev.cancel()
            self._check_play_ev = None
        super(SoundAndroid, self).stop()

    def load(self):
        self.unload()
        if self.filename is None:
            return
        if not self._data:
            return

        try:
            self.secs = 0
            self._data.setDataSource(self.filename)
            self._data.prepare()
            # self.length = self._data.getDuration() / 1000
        except Exception as e:
            Logger.error('SoundAndroid:error in title: %s : %s' % (self.filename,e.message))
            return None

    def unload(self):
        self.stop()
        if not self._data:
            return

        self._data.reset()

    def seek(self, position):
        if not self._data:
            return
        self._data.seekTo(position * 1000)

'''
    def get_pos(self):
        if self._data is not None and self._channel:
            return self._channel.get_pos()
        return 0

    def on_volume(self, instance, volume):
        if self._data is not None:
            self._data.set_volume(volume)

    def _get_length(self):
        return self._channel.get_length()
'''


def RegisterSoundProvider():
    Logger.info("Register MP3 Sound on Android")
    SoundLoader.register(SoundAndroid)
