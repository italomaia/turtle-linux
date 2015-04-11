import random

import actor

from vector import Vector as v

class SmokePuff(actor.Actor):

    collides = False

    def __init__(self, world, pos):
        super(SmokePuff, self).__init__(world, pos=pos, radius=10, image_file="images/all/star.svgz")
        self.apply_impulse(v((random.gauss(0,2),random.gauss(0,2))))
        
    def tick(self):
        super(SmokePuff, self).tick()
        self.radius += .5
        if self.radius > 20:
            self.dead = True
