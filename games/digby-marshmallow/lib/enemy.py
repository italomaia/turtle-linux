import math
import random

import actor
import weapons

import vector
from vector import Vector as v
from constants import *

class Enemy(actor.Actor):

    mass = 10
    thrust = 1.5
    max_energy = 250

    def __init__(self, *args, **kwargs):
        super(Enemy, self).__init__(*args, **kwargs)
        self.energy = self.max_energy
        self.tired = False
        self.stunned = False
        self.stun_time = 0
    
    def tick(self):
        if self.energy < self.max_energy:
            self.energy += 1
        if self.energy > self.max_energy * 0.8:
            self.tired = False
            
        if self.stun_time > 0:
            self.stun_time -= 1
        else:
            self.stunned = False
            
        super(Enemy, self).tick()
        for proj in self.world.active.overlaps(self):
            if isinstance(proj, weapons.Projectile):
                if (proj.pos - self.pos).length < self.radius + proj.radius:
                    proj.hit(self)
                    
    def think(self):
        pass
        
    def stun(self, time):
        self.stun_time += time
        self.stunned = True
        self.bearing += IMPACT_SPIN
        
    ## BEHAVIOURS
                    
    def flock(self, sense_radius=500, target_sep=100, effect=1):
        flock_vector = v((0,0))
        for other in self.neighbours(sense_radius):
            if self.__class__ == other.__class__ and self.sees(other, sight_radius=sense_radius):
                relative_pos = other.pos - self.pos
                d = relative_pos.length
                if d:
                    sgn = 1 if d > target_sep else -1
                    flock_vector += (relative_pos.normalised() * sgn)
        if flock_vector.length > 0:
            self.apply_impulse(flock_vector.normalised() * effect)

    def bumble(self):
        self.apply_impulse(v((random.gauss(0, 1), random.gauss(0, 1))))
                    
    def face_player(self):
        dir = self.world.player.pos - self.pos
        if dir.length > 0:
            self.bearing = dir.angle
            self.old_bearing = dir.angle

    def align_with_velocity(self):
        dir = self.pos - self.old_pos
        if dir.length > 0:
            self.bearing = dir.angle
            self.old_bearing = dir.angle

    def accelerate(self):
        self.apply_impulse(v((self.thrust,0)).rotated(self.bearing))

    def tire(self, amt=2):
        self.energy -= amt
        if self.energy < self.max_energy * 0.2:
            self.tired = True
        
    ## CONDITIONALS

    def sees_player(self, sight_radius=1000):
        return self.sees(self.world.player, sight_radius=sight_radius)
    
    def sees(self, other, sight_radius=1000):
        sightline = vector.LineSegment.from_endpoints(self.pos, other.pos)
        if sightline.length > sight_radius:
            return False
        obs = self.world.static.on_line(sightline.start, sightline.end)
        for o in obs:
            if o.intersects_seg(sightline):
                return False
        return True
        
    def is_awake(self):
        return not self.tired
    
## Enemy behaviour classes    

class RelentlessChasingEnemy(Enemy):

    def think(self):
        if self.sees_player():
            self.face_player()
            self.accelerate()
            self.flock(sense_radius=100)
    
class ChasingEnemy(Enemy):
        
    def think(self):
        if self.is_awake() and self.sees_player():
            self.face_player()
            self.accelerate()
            self.flock(sense_radius=100)
            self.tire()
            
class SwarmingEnemy(Enemy):

    thrust = 0.3
    
    def think(self):
        self.bumble()
        self.accelerate()
        self.flock(effect=2)
        self.align_with_velocity()
