import data


class Sound(object):
    def __init__(self, name):
        self.source = data.load_sound(name)
    def __call__(self):
        self.source.play()


hit = Sound("hit.wav")
shoot = Sound("shoot.wav")
pickup = Sound("pickup.wav")
wahwah = Sound("wahwah.mp3")
beep = Sound("beep.mp3")
