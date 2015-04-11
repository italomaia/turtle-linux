import math

import data
import squirtle

from vector import *
from vector import Vector as v

from constants import *

class Actor(object):

    collides = True
    mass = 0
    extra_keys = []
    def __init__(self, world, pos=(0,0), radius=50, bearing=0, image_file=None, name=None, **kwargs):
        self.world = world
        self.pos = v(pos)
        self.old_pos = v(pos)
        self.radius = radius
        self.bearing = bearing
        self.old_bearing = bearing
        self.image_file = image_file
        self.image = squirtle.SVG(data.file_path(image_file), anchor_x='center', anchor_y='center')
        self.dead = False
        self.impulse = v((0,0))
        self.name = name
        # do not use
        self.scale = 0.0
        self.z = 0
    
    def apply_impulse(self, impulse):
        self.impulse += impulse
    
    def stun(self, frames):
        pass
    
    def tick(self):
        # objects by default continue to move in a straight line (see Newton)
        delta = self.pos - self.old_pos
        self.old_pos = self.pos
        dtheta = self.bearing - self.old_bearing
        self.old_bearing = self.bearing
        self.bearing += dtheta * ANGULAR_DRAG
        real_old_pos = self.old_pos
        
        # add drag forces to delta
        drag = delta * -delta.length * self.radius * self.world.drag
        delta += drag
        
        # add other accumulated forces to delta
        delta += self.impulse
        self.impulse = v((0,0))
        
        if not self.collides:

            self.pos += delta
        
        else:
        
            steps = 1 + int(1.05 * delta.length / self.radius)
            sub_delta = delta / steps
            
            for ii in xrange(steps):
            
                self.pos += sub_delta
                
                original_pos = self.pos
                check_collisions = True
                tries = 0
                while check_collisions:
                
                    check_collisions = False
                    tries += 1
                    if tries > 200:
                        # this is a problem, so rather than take the game down, we do something which just
                        # looks bad
                        self.pos = original_pos
                        return

                    for wall in self.world.static.overlaps(self):
                        cp = wall.closest_point(self.pos)
                        approach = (self.pos - cp)
                        if approach.length < self.radius - EPSILON:
                            self.pos = cp + approach.normalised() * self.radius
                            check_collisions = True

                # now, the actor is definitely in a safe place
                # work backwards to work out its eventual reflection and update old_pos to make it bounce
                
                displacement = self.pos - original_pos
                if displacement.length > 0:
                    mirror_point = original_pos + displacement * 0.5
                    mirror_line = Line(displacement.normalised(), mirror_point * displacement.normalised())
                    self.old_pos = mirror_line.reflect(self.old_pos)
                    sub_delta = mirror_line.parallel_through_origin.reflect(sub_delta)
                    self.old_pos = self.pos + (self.old_pos - self.pos) * ELASTICITY
                    
    def colliders(self):
        lst = []
        for a in self.world.active.overlaps(self):
            if (a.pos - self.pos).length <= self.radius + a.radius:
                lst.append(a)
        return lst
           
    @property
    def bb(self):
        r = (self.radius, self.radius)
        return BoundingBox(self.pos - r, self.pos + r)

    def neighbours(self, distance):
        lst = []
        for a in self.world.active.in_box(self.extended_bb(distance)):
            if a is self: continue
            if (a.pos - self.pos).length <= self.radius + a.radius + distance:
                lst.append(a)
        return lst
        
    def extended_bb(self, extent):
        r = (self.radius + extent, self.radius + extent)
        return BoundingBox(self.pos - r, self.pos + r)
               
    def draw(self):
        sf = self.radius * 2 / self.image.width
        self.image.draw(self.pos.x, self.pos.y, angle=self.bearing, radius=self.radius)

    def __repr__(self):
        rep =  "%s.%s(%r, pos=%r, radius=%r, bearing=%r, image_file=%r, name=%r" % (self.__class__.__module__, self.__class__.__name__, self.world, self.pos, self.radius, self.bearing, self.image_file, self.name)
        for key in self.extra_keys:
            rep += ', %s=%r' % (key, getattr(self, key))
        return rep + ')'

import effects
import weapons
import swag
import oxygen
class Player(Actor):

    mass = 10

    def __init__(self, world):
        super(Player, self).__init__(world, pos=world.initial_oxygen.pos, radius=PLAYER_RADIUS, bearing=0, image_file="images/all/digby.svgz")
        self.connect_oxygen(world.initial_oxygen)

        self.engine_fx_cooldown = 0
        
        self.rotation = 0
        self.thrust = 0
        self.lift = 0
        self.firing = False
        self.cooldown = 0
    
    def attempt_connect(self):
        for c in self.colliders():
            if isinstance(c, oxygen.Oxygen) and c is not self.oxygen:
                self.connect_oxygen(c)
                break
                
    def connect_oxygen(self, oxygen):
        self.oxygen = oxygen
        self.pipe = [oxygen.pos]
        self.pinned_length = 0
        self.pipe_used = 0
        self.pipe_length = oxygen.pipe_length
            
    def tick(self):
    
        for c in self.colliders():
            if c.mass > 0:
                rpn = (c.pos - self.pos).normalised()
                c.apply_impulse(rpn * self.mass)
                self.apply_impulse(-rpn * c.mass)
    
        self.bearing += self.rotation
        if self.thrust or self.lift:
            dir = v((self.thrust, self.lift)).rotated(self.bearing)
            self.apply_impulse(dir)
            if self.engine_fx_cooldown <= 0:
                self.world.new_active.add(effects.SmokePuff(self.world, self.pos))
                self.engine_fx_cooldown = SMOKEPUFF_RATE
            else:
                self.engine_fx_cooldown -= 1
            
        old_pos = v(self.pos) #Need to store this, because we may mess with it to do bouncing, etc.
        
        super(Player, self).tick()

        def candidate_key(pt):
            v1 = self.pipe[-1] - pt
            v2 = self.pipe[-1] - old_pos
            return v1.angle_to(v2) #, v1.length
            
        def int_point(pt):
            return v((pt.x//1.0, pt.y//1.0))
        
        hooked = False
        unhooked = []
        swept_angle = 0
        while True:
            candidates = []
            for wall in self.world.static.in_tri(self.pipe[-1], old_pos, self.pos):
                pt = int_point(wall.start) # why does this work?
                if pt not in unhooked and pt.in_tri(self.pipe[-1], old_pos, self.pos):
                    angle = candidate_key(pt)
                    if angle > swept_angle:
                        candidates.append((angle, pt))
            if not hooked and len(self.pipe) > 1 and self.pipe[-1].in_tri(self.pipe[-2], old_pos, self.pos):
                unhook_angle = (self.pipe[-1] - old_pos).angle_to(self.pipe[-2] - self.pipe[-1])
            else:
                unhook_angle = None
            if not candidates and unhook_angle is None:
                break
            if unhook_angle is not None and (not candidates or unhook_angle < min(candidates)):
                swept_angle = (self.pipe[-2] - old_pos).angle_to(self.pipe[-2] - self.pipe[-1])
                self.pinned_length -= (self.pipe[-2] - self.pipe[-1]).length
                unhooked.append(self.pipe.pop())
            else:
                angle, pivot = min(candidates)
                swept_angle = angle
                self.pipe.append(pivot)
                self.pinned_length += (self.pipe[-2] - self.pipe[-1]).length
                hooked = True
                
        pipe_vector = self.pos - self.pipe[-1]
        if pipe_vector.length > self.pipe_length - self.pinned_length:
            sf = (self.pipe_length - self.pinned_length)/ pipe_vector.length
            self.pos = (1 - sf) * self.pipe[-1] + self.pos * sf
        self.pipe_used = min(pipe_vector.length + self.pinned_length, self.pipe_length)

        if self.firing and self.cooldown > SHOT_COOLDOWN:
            self.cooldown = 0
            p = self.weapon.make_projectile(self.world, pos=self.pos, bearing=self.bearing+90)
            p.apply_impulse(self.pos - self.old_pos)
            self.world.new_active.add(p)
            self.world.dispatch_event('on_shoot')
        self.cooldown += 1
        if not self.firing:
            self.cooldown = SHOT_COOLDOWN
        self.oxygen.contained -= 1
        for c in self.colliders():
            if isinstance(c, swag.Swag):
                self.world.dispatch_event('on_get_swag', c)
                if c.goal:
                    self.world.dispatch_event('on_finish_level')
                c.dead = True
