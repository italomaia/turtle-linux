from __future__ import division

import random
import pyglet

from pyglet.gl import *
from vector import Vector as v

def somewhere():

    return v((random.random() * 800, random.random() * 600))

class Mockup(object):
    
    def __init__(self):
        self.w = pyglet.window.Window(800, 600)
        self.w.push_handlers(self)
        pyglet.clock.schedule_interval(self.tick, 1/60)
        
        self.squads = set(map(lambda _: FlySquad(), xrange(10)))
        self.squads.add(WaspSquad(self))
        
    def on_draw(self):
        self.w.clear()
        for s in self.squads:
            s.draw()
        
    def tick(self, dt):
        for s in self.squads:
            s.tick()
        self.squads = set(filter(lambda s: s.members, list(self.squads)))
        
class Squad(object):
    def __init__(self):
        self.members = set()
    def tick(self):
        self.members = set(filter(lambda m: not m.dead, self.members))
        for m in self.members:
            m.tick()
    
class FlySquad(Squad):
    def __init__(self):
        super(FlySquad, self).__init__()
        for ii in xrange(5):
            self.members.add(Fly())
        self.dest = somewhere()
        
    def tick(self):
        self.dest += v((4, 0)).rotated(random.random() * 360)
        for m in self.members:
            m.turn_towards(self.dest)
        super(FlySquad, self).tick()
            
    def draw(self):
        glColor3f(1, 1, 1)
        glPointSize(3)
        glBegin(GL_POINTS)
        for m in self.members:
            glVertex2f(*m.pos)
        glEnd()
        
class WaspSquad(Squad):
    def __init__(self, game):
        super(WaspSquad, self).__init__()
        self.g = game
        for i in xrange(3):
            self.members.add(Wasp())
        self.victims = None
        
    def tick(self):
        objectives = self.g.squads - set([self])
        if not self.victims in objectives:
            if objectives:
                self.victims = random.choice(list(objectives))
            else:
                self.victims = None
        if self.victims and self.victims.members:
            for m in self.members:
                if m.victim is None:
                    m.victim = random.choice(list(self.victims.members))
                m.turn_towards(m.victim.pos)
        super(WaspSquad, self).tick()

    def draw(self):
        glColor3f(1, 1, 0)
        glPointSize(5)
        glBegin(GL_POINTS)
        for m in self.members:
            glVertex2f(*m.pos)
        glEnd()

class Creature(object):
    speed = 1
    turn_rate = 10
    def __init__(self):
        self.pos = somewhere()
        self.vel = v((self.speed, 0)).rotated(random.random() * 360)
        self.dead = False
    def tick(self):
        self.pos += self.vel
    def turn_towards(self, dest):
        targetdir = dest - self.pos
        if not targetdir.is_zero:
            tturn = targetdir.angle - self.vel.angle
            if tturn < -180:
                tturn += 360
            if tturn >= 180:
                tturn -= 360
            if abs(tturn) <= self.turn_rate:
                self.vel = self.vel.rotated(tturn)
            else:
                self.vel = self.vel.rotated(cmp(tturn, 0) * self.turn_rate)
    
class Fly(Creature):
    speed = 5
    turn_rate = 10
    def __init__(self):
        super(Fly, self).__init__()
        
class Wasp(Creature):
    speed = 8
    turn_rate = 15
    def __init__(self):
        super(Wasp, self).__init__()
        self.victim = None
        
    def tick(self):
        super(Wasp, self).tick()
        if self.victim:
            if (self.victim.pos - self.pos).length < 10:
                self.victim.dead = True
            if self.victim.dead:
                self.victim = None

if __name__ == '__main__':
    m = Mockup()
    pyglet.app.run()