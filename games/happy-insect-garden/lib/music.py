from __future__ import division

from pyglet import media

import data

import config
from common import *
from constants import *


class FadingPlayer(media.Player):
    """Fading media player.

    """

    def __init__(self):
        """Create a FadingPlayer object.

        """
        super(FadingPlayer, self).__init__()
        self.fading = False
        self.fade_time = 0.0
        self.fade_rate = 0.0
        self.fade_grace = 0.0

    def start_fade(self, target, time, grace):
        """Commence a fade from the current volume (possibly mid fade).

        :Parameters:
            `target` : float
                The target volume.
            `time` : float
                The number of seconds to fade over.
            `grace` : float
                The amount of time to wait before releasing the fade.

        """
        self.fading = True
        self.fade_time = time
        self.fade_grace = grace
        target = min(1.0, max(0.0, target))
        delta = float(target - self.volume)
        self.fade_rate = delta / time

    def stop_fade(self, dt):
        """Try to end the fade.

        :Parameters:
            `dt` : float
                The number of seconds to knock off the grace time.

        """
        if self.fade_grace > 0.0:
            self.fade_grace = max(0.0, self.fade_grace - dt)
        if self.fade_grace == 0.0:
            self.fading = False
            self.fade_rate = 0.0

    def dispatch_events(self, dt=None):
        """Process the fade state.

        """
        if dt is not None:
            if self.fade_time > 0.0:
                self.fade_time = max(0.0, self.fade_time - dt)
                volume = self.volume + self.fade_rate * dt
                self.volume = min(1.0, max(0.0, volume))
            if self.fade_time == 0.0:
                self.stop_fade(dt)
        #super(FadingPlayer, self).dispatch_events(dt)


def makeorder(func):
    """Decorate a function as an order for the music manager.

    """
    def decorated(self, *args, **kwds):
        prepend = kwds.pop("prepend", False)
        if prepend: self.orders.insert(0, [func, args, kwds])
        else: self.orders.append([func, args, kwds])
    decorated.func_name = func.func_name
    decorated.func_doc = func.func_doc
    return decorated


class MusicManager(object):
    """Music manager, using a fading media player.

    """

    def __init__(self):
        """Create a MusicManager object.

        """
        self.orders = []
        self.volume = 1.0
        self.player = FadingPlayer()
        self.player.volume = 0.0
        self.fade_grace = 0.5
        self.playing = None

    @makeorder
    def change_song(self, song, fadein=None, fadeout=None, onlyonce=False, as_sfx=False):
        """Order to change the playing song.

        """
        self.start_song(song, fadein, onlyonce, prepend=True, as_sfx=as_sfx)
        self.stop_song(fadeout, prepend=True)

    @makeorder
    def start_song(self, song, fadein=None, onlyonce=False, as_sfx=False):
        """Order to start playing a new song.

        """
        if not media.have_avbin: return
        if self.player.source is not None:
            self.start_song(song, fadein, prepend=True, as_sfx=as_sfx)
            self.stop_song(None, prepend=True)
        elif config.music or (as_sfx and config.sound_effects):
            source = data.load_song(song)
            self.player.queue(source)
            self.player.play()
            if fadein is not None:
                self.player.start_fade(self.volume, fadein, self.fade_grace)
            else:
                self.player.volume = self.volume
            self.playing = song
            if onlyonce:
                self.player.eos_action = "pause"
            else:
                self.player.eos_action = "loop"

    @makeorder
    def stop_song(self, fadeout=None):
        """Order to stop playing the current song.

        """
        if self.player.source is None:
            self.player.volume = 0.0
        if self.player.volume > 0.0:
            if fadeout is not None:
                self.player.start_fade(0.0, fadeout, self.fade_grace)
            else:
                self.player.volume = 0.0
            self.stop_song(fadeout, prepend=True)
        else:
            self.player.next()
        self.playing = None

    def update(self, dt=None):
        """Update the manager state, processing new orders.

        """
        if self.player.fading:
            pass
        elif self.orders:
            func, args, kwds = self.orders.pop(0)
            func(self, *args, **kwds)
            self.update()
        elif self.playing and not self.player.source:
            self.start_song(self.playing)
        if dt is not None:
            self.player.dispatch_events(dt)
