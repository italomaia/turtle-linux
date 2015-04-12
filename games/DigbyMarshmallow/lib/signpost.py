import actor
from content import texts

class Signpost(actor.Actor):
    extra_keys = ['text_key']
    def __init__(self, *args, **kwargs):
        super(Signpost, self).__init__(*args, **kwargs)
        self.text_key = kwargs.get('text_key', '')
        self.text = texts.texts.get(self.text_key, '[[ missing key : %r ]]' % self.text_key)
        self.z = 1
        
    def tick(self):
        super(Signpost, self).tick()
        p = self.world.player
        ppos = p.pos - self.pos
        l = ppos.length
        if l < self.radius + p.radius and l > 0:
            mag = -0.5 * min(l, 1)
            p.apply_impulse(ppos.normalised() * mag)