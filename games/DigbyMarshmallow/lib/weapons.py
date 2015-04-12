import random

import actor

from constants import *
from vector import Vector as v

class Weapon(object):
    muzzle_velocity = 20
    scatter = 0
    projectile_radius = 15
    projectile_image="images/all/shot.svgz"
    projectile_force = 50
    
    def make_projectile(self, world, pos, bearing):
        p = Projectile(world, pos=pos, radius=self.projectile_radius, bearing=bearing, image_file=self.projectile_image)
        d = (random.random() - 0.5) * self.scatter
        p.apply_impulse(v((self.muzzle_velocity, d)).rotated(bearing))
        p.force = self.projectile_force
        return p
    
class PeeweeGun(Weapon):
    scatter = 3

class Projectile(actor.Actor):
    def __init__(self, *args, **kwargs):
        super(Projectile, self).__init__(*args, **kwargs)
        self.age = 0
    def tick(self):
        super(Projectile, self).tick()
        
        self.bearing = (self.pos - self.old_pos).angle
        self.age += 1
        if self.age > 60:
            self.dead = True
    
    def hit(self, victim):
        self.dead = True
        # check this next line - I think crazy stuff might happen if a projectile hits an enemy just
        # after it's bounced off a wall
        victim.apply_impulse(v((self.force,0)).rotated(self.bearing))
        victim.stun(STUN_FRAMES)