from vector import *
from pyglet.gl import *

import math
import actor

import squirtle
import data
import weapons

class Door(object):
    def __init__(self, world, start, end, thickness=5, closed=True):
        self.world = world
        self.start = Vector(start)
        self.end = Vector(end)
        self.pos = .5 * (self.start + self.end)
        self.ls = LineSegment.from_endpoints(start, end)
        self.radius = math.sqrt(self.ls.radius ** 2 + .25 * thickness ** 2)
        self.front = LineSegment(Line(self.ls.line.direction, self.ls.line.distance + .5*thickness), self.ls.min_dist, self.ls.max_dist)
        self.back = LineSegment(Line(-self.ls.line.direction, -self.ls.line.distance + .5*thickness), -self.ls.max_dist, -self.ls.min_dist)
        self.closed = closed
        self.thickness = thickness
        self.z = -10000
        
    def __repr__(self):
        return "door.Door(%r, %r, %r, closed=%r)" % (self.world, self.start, self.end, self.closed)
        
    def set_world(self, world):
        self.world = world
        if self.closed:
            self.world.static.add(self.front)
            self.world.static.add(self.back)
            
    def close(self):
        if not self.closed and self.world:
            self.world.static.add(self.front)
            self.world.static.add(self.back)
            self.closed = True
        
    def open(self):
        if self.closed and self.world:
            self.world.static.remove(self.front)
            self.world.static.remove(self.back)
            self.closed = False
    
    def toggle(self):
        if self.closed:
            self.open()
        else:
            self.close()
            
    def draw(self):
        if self.closed:
            import random
            n = int(self.ls.length / (12 * self.thickness))
            along = (self.end - self.start) / n
            across = self.ls.line.direction * self.thickness
            glLineWidth(3)
            glBegin(GL_LINE_STRIP)
            glColor3f(1, 1, 1)
            for i in xrange(n + 1):
                glVertex2f(*(self.start + i * along + random.gauss(0, 4) * across))
            glEnd()
            glLineWidth(1)
        
class Switch(actor.Actor):
    extra_keys = ['alt_image_file', 'doors']
    def __init__(self, *args, **kwargs):
        super(Switch, self).__init__(*args, **kwargs)
        self.alt_image = squirtle.SVG(data.file_path(kwargs['alt_image_file']), anchor_x='center', anchor_y='center')
        self.alt_image_file = kwargs['alt_image_file']
        self.doors = kwargs.get('doors', {})
    
    def tick(self):
        for proj in self.world.active.overlaps(self):
            if isinstance(proj, weapons.Projectile):
                if (proj.pos - self.pos).length < self.radius + proj.radius:
                    proj.hit(self)
                    self.trigger()
                    
    def trigger(self):
        self.image, self.alt_image = self.alt_image, self.image
        for id, command in self.doors.items():
            if command == 'open':
                self.world.doors[id].open()
            elif command == 'close':
                self.world.doors[id].close()
            elif command == 'toggle':
                self.world.doors[id].toggle()
                

class OnceSwitch(Switch):
    def trigger(self):
        if not hasattr(self, 'switched'):
            super(OnceSwitch, self).trigger()
    
