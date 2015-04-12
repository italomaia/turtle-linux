from pyglet import media
import config
import data


class FadingPlayer(media.Player):

    def __init__(self):
        super(FadingPlayer, self).__init__()
        self.fading = False
        self.fade_time = 0.0
        self.fade_rate = 0.0
        self.fade_grace = 0.0

    def start_fade(self, target, time, grace):
        self.fading = True
        self.fade_time = time
        self.fade_grace = grace
        target = min(1.0, max(0.0, target))
        delta = float(target - self.volume)
        self.fade_rate = delta / time

    def stop_fade(self, dt):
        if self.fade_grace > 0.0:
            self.fade_grace = max(0.0, self.fade_grace - dt)
        if self.fade_grace == 0.0:
            self.fading = False
            self.fade_rate = 0.0

    def dispatch_events(self, dt=None):
        if dt is not None:
            if self.fade_time > 0.0:
                self.fade_time = max(0.0, self.fade_time - dt)
                volume = self.volume + self.fade_rate * dt
                self.volume = min(1.0, max(0.0, volume))
            if self.fade_time == 0.0:
                self.stop_fade(dt)
        super(FadingPlayer, self).dispatch_events(dt)


def makeorder(func):
    def decorated(self, *args, **kwds):
        prepend = kwds.pop("prepend", False)
        if prepend: self.orders.insert(0, [func, args])
        else: self.orders.append([func, args])
    return decorated


class MusicManager(object):

    def __init__(self):
        self.orders = []
        self.volume = 1.0
        self.player = FadingPlayer()
        self.fadein = None
        self.fadeout = None
        self.current_order = None
        self.fade_grace = 0.5
        self.playing = None

    @makeorder
    def change_song(self, song, fadein=None, fadeout=None):
        self.start_song(song, fadein, prepend=True)
        self.stop_song(fadeout, prepend=True)

    @makeorder
    def start_song(self, song, fadein=None):
        if self.player.source is not None:
            self.start_song(song, fadein, prepend=True)
            self.stop_song(None, prepend=True)
        source = data.load_song(song)
        self.player.queue(source)
        self.player.play()
        if fadein is not None:
            self.player.start_fade(self.volume, fadein, self.fade_grace)
        else:
            self.player.volume = self.volume
        self.playing = song

    @makeorder
    def stop_song(self, fadeout=None):
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

    def update(self, dt):
        if self.player.fading:
            pass
        elif self.orders:
            self.current_order = self.orders.pop(0)
            func, args = self.current_order
            func(self, *args)
            self.current_order = None
        elif self.playing and not self.player.source:
            self.start_song(self.playing)
        self.player.dispatch_events(dt)


"""
import mode
class MusicTest(mode.Mode):
    name = "musictest"
    def connect(self, control):
        self.control = control
        self.window = control.window
        self.music = control.music
    def on_key_press(self, sym, mods):
        from pyglet.window import key
        if sym == key.Q:
            self.music.change_song("Test1.mp3", 2.0, 2.0)
        elif sym == key.W:
            self.music.change_song("Test2.mp3", 2.0, 2.0)
        elif sym == key.E:
            self.music.stop_song(2.0)
"""
