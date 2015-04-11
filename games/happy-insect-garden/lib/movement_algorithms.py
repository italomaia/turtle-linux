from __future__ import division
import random

import vector
from vector import Vector as v

class MovementAlgorithm(object):
    def __init__(self, pos, speed):
        self.pos = pos
        self.angle = 0
        self.speed = speed
        self.dest = None
        self.vel = None
        
    def advance(self):
        self.update_velocity()
        self.update_position_and_angle()
    
    def update_position_and_angle(self):
        self.pos = self.pos.__add__(self.vel)
        try:
            if not self.vel.is_zero:    
                self.angle = self.vel.angle
        except AttributeError:
            pass
        
    
class MovementWrapperAlgorithm(MovementAlgorithm):
    def __init__(self, underlying_alg, pos, speed, *args):
        super(MovementWrapperAlgorithm, self).__init__(pos, speed)
        self.underlying_algorithm = underlying_alg(pos, speed, *args)
        
    def update_velocity(self):
        self.underlying_algorithm.dest = self.dest
        self.vel = self.underlying_algorithm.update_velocity()
        self.modify_underlying_velocity()
        
    def update_position_and_angle(self):
        super(MovementWrapperAlgorithm, self).update_position_and_angle()
        self.underlying_algorithm.pos = self.pos
        self.underlying_algorithm.angle = self.angle
        

class WigglingMovement(MovementWrapperAlgorithm):
    def __init__(self, underlying_alg, pos, speed, frequency, *args):
        super(WigglingMovement, self).__init__(underlying_alg, pos, speed, *args)
        self.phase = 0
        self.frequency = frequency
        
    def modify_underlying_velocity(self):
        from math import sin
        if self.vel.length2 <  0.9 * self.speed ** 2: #should be < speed, but cope with floats.
            return
        self.vel = self.vel.rotated(20 * sin(self.phase / self.frequency))
        self.phase += 0.8 + 0.4 * random.random()
        
        #FANTASTIC way of making drunk bees - uncomment this line
        #self.underlying_algorithm.vel = self.vel

        

class Zippy(MovementWrapperAlgorithm):
    def __init__(self, underlying_alg, pos, speed, move_time, static_time, *args):
        super(Zippy, self).__init__(underlying_alg, pos, speed, *args)
        self.move_time = move_time
        self.static_time = static_time
        self.is_moving = True
        self.time_count = 0
        
    def modify_underlying_velocity(self):
        if not self.is_moving:
            self.vel = vector.zero
            
        self.time_count += 1
        if self.is_moving:
            if self.time_count > self.move_time:
                self.is_moving = False
                self.time_count = 0
        else:
            if self.time_count > self.static_time:
                self.is_moving = True
                self.time_count = 0
                
class AvoidPlants(MovementWrapperAlgorithm):
    def __init__(self, underlying_alg, pos, speed, game, *args):
        super(AvoidPlants, self).__init__(underlying_alg, pos, speed, *args)
        self.game = game
        
    def modify_underlying_velocity(self):
        if self.game.is_in_plant(self.pos):
            return
        desired_position = self.pos + self.vel
        if self.game.is_in_plant(desired_position):
            self.vel = vector.zero
            self.dest = None
            
                
class ZeroTurning(MovementAlgorithm):
    def update_velocity(self):
        #doesn't actually speed things up
        #if (self.dest != self.last_dest):
        direction = (self.dest - self.pos)
        if direction.length2 > self.speed ** 2:
            #avoid scaled_to here - we can do better
            old_length = direction.length
            scale_factor = self.speed/old_length
            direction = v((direction[0]*scale_factor, direction[1]*scale_factor))
        self.vel = direction
        return self.vel
    
class BoundedTurning(MovementAlgorithm):
    def __init__(self, pos, speed, turn_rate):
        super(BoundedTurning, self).__init__(pos, speed)
        self.turn_rate = turn_rate

    def update_velocity(self):
        direction = self.dest - self.pos
        if self.vel is None or self.vel.is_zero:
            if direction.length2 > self.speed ** 2:
                #avoid scaled_to here - we can do better
                old_length = direction.length
                scale_factor = self.speed/old_length
                direction = v((direction[0]*scale_factor, direction[1]*scale_factor))
            self.vel = direction
        else:
            tturn = self.vel.signed_angle_to(direction)
            if abs(tturn) <= self.turn_rate:  
                if direction.length2 > self.speed ** 2:
                    #avoid scaled_to here - we can do better
                    old_length = direction.length
                    scale_factor = self.speed/old_length
                    direction = v((direction[0]*scale_factor, direction[1]*scale_factor))
                self.vel = direction
            else:
                self.vel = self.vel.rotated(cmp(tturn, 0) * self.turn_rate)
        return self.vel
            
        
class BoundedTurningConstantSpeed(MovementAlgorithm):
    def __init__(self, pos, speed, turn_rate):
        super(BoundedTurningConstantSpeed, self).__init__(pos, speed)
        self.turn_rate = turn_rate
        
    def update_velocity(self):
        target_direction = self.dest - self.pos
        try:
            tturn = self.vel.signed_angle_to(target_direction)
            if abs(tturn) <= self.turn_rate:
                self.vel = self.vel.rotated(tturn)
            else:
                self.vel = self.vel.rotated(cmp(tturn, 0) * self.turn_rate)
        except AttributeError:
            #uncommon case - first call only
            self.vel = target_direction.scaled_to(self.speed)
        return self.vel
 