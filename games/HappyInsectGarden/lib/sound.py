import data
import config
import random
from pyglet import media

class Sound(object):
    def __init__(self, snd_name):
        if not media.have_avbin: return
        self.sound = data.load_sound(snd_name)
        self.player = None
    def __call__(self):
        if not media.have_avbin: return
        if config.sound_effects and (not self.player or not self.player.time):
            self.player = self.sound.play()

class RandomSound(Sound):
    def __init__(self, *snd_names):
        if not media.have_avbin: return
        self.sounds = [data.load_sound(snd_name) for snd_name in snd_names]
        self.player = None

    def __call__(self):
        if not media.have_avbin: return
        if config.sound_effects and (not self.player or not self.player.time):
            self.player = random.choice(self.sounds).play()

beep = Sound("beep.wav")
click = Sound("click.wav")
plant = Sound("plant.wav")
bad = Sound("bad.wav")
pop = RandomSound("pop1.wav", "pop2.wav", "pop3.wav", "pop4.wav", "pop5.wav")
cheer = Sound("cheer.wav")