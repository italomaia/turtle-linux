from pyglet.gl import *
from vector import *
import random
import data

class ParticleGroup(pyglet.graphics.Group):
    def __init__(self, texture, size=20, parent=None):
        super(ParticleGroup, self).__init__(parent)
        self.texture = texture
        self.size = size
    def set_state(self):
        #glEnable(GL_TEXTURE_2D)
        #glBindTexture(GL_TEXTURE_2D, self.texture.id)
        #glEnable(GL_POINT_SPRITE)
        #glTexEnvf (GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE)
        glEnable(GL_POINT_SMOOTH)
        glPointSize(int(self.size))
    def unset_state(self):
        glDisable(GL_POINT_SPRITE)
        glDisable(GL_TEXTURE_2D)

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and self.texture == other.texture)

def fire_update(pos, vel, color):
    return pos + vel, vel, (color[0], color[1] - .02, color[2] - .05, color[3] - .02)

def smoke_update(color):
    return (color[0], color[1], color[2], color[3] - .02)

class ParticleSystem(object):
    def __init__(self, limit=256, update_func=smoke_update, batch=None, group=None):
        self.batch = batch or pyglet.graphics.Batch()
        self.group = ParticleGroup(pyglet.resource.texture("particle.png"), parent=group)
        self.limit = limit
        self.freelist = range(limit)
        self.livelist = []
        self.drawlist = batch.add(limit, GL_POINTS, self.group, ('v2f/stream', [0,0] * limit), ('c4f/stream', [0,0,0,0] * limit))
        self.velocities = [zero] * limit
        self.update = update_func
    def add_particle(self, pos, vel, color):
        try:
            pid = self.freelist.pop()
            self.livelist.append(pid)
        except:
            pid = random.randrange(self.limit)
        self.drawlist.vertices[2*pid:2*pid+2] = pos
        self.velocities[pid] = vel
        self.drawlist.colors[4*pid:4*pid+4] = color

    def tick(self):
        colors = self.drawlist.colors
        vertices = self.drawlist.vertices
        dead = []
        for n, pid in enumerate(self.livelist):
            if colors[4*pid+3] <= 0:
                dead.append(n)
                continue
            vertices[2*pid:2*pid+2] = self.velocities[pid] + vertices[2*pid:2*pid+2]
            colors[4*pid+3] -= .02
        if dead:
            dead.reverse()
            for n in dead:
                pid = self.livelist.pop(n)
                self.freelist.append(pid)



