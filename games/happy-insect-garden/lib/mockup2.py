from __future__ import division

import random
import pyglet

from pyglet.gl import *
from vector import Vector as v

from creature import Bee, EvilBee
from plant import Plant
from game import Game


class Mockup(object):
    
    def __init__(self):
        self.w = pyglet.window.Window(800, 600)
        self.w.push_handlers(self)

        self.g = Game(800, 600)
        pyglet.clock.schedule_interval(lambda t: self.g.tick(), 1/60)
        
    def on_draw(self):
        self.w.clear()
        glPointSize(7)
        glColor3f(0,1,0)
        glBegin(GL_POINTS)
        for p in self.g.plants:
            glVertex2f(*p.pos)
        glEnd()
        for c in self.g.creatures:
            c.draw()            

    def on_mouse_release(self, x, y, buttons, mods):
        self.g.plants.add(Plant(v((x, y))))
        

if __name__ == '__main__':
    m = Mockup()
    pyglet.app.run()