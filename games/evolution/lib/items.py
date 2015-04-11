import random

import pygame
from OpenGL.GL import *

import textures
import data
import sprite
import trees
import clouds

class HitBox:
    def __init__(self, position, hb):
        x, y = position
        dx, dy, w, h = hb
        self.left= x + dx
        self.right = self.left + w
        self.bottom = y + dy
        self.top = self.bottom + h

class Item(object):
    texture = None
    quad_list = None 
    hb = None

    # draw order
    order = 0

    def __init__(self, map, position):
        if self.texture is None:
            filename = data.filepath(self.texture_file)
            t = self.__class__.texture = textures.Texture(filename)
            self.__class__.width = t.width
            self.__class__.height = t.height
            self.__class__.quad_list = glGenLists(1)
            glNewList(self.quad_list, GL_COMPILE)
            glTexCoord2f(0, 0)
            glVertex2f(0, 0)
            glTexCoord2f(1, 0)
            glVertex2f(t.width, 0)
            glTexCoord2f(1, 1)
            glVertex2f(t.width, t.height)
            glTexCoord2f(0, 1)
            glVertex2f(0, t.height)
            glEndList()

        self.setPosition(map, position)

    def get_hitbox(self):
        if self.hb is None:
            return self
        return HitBox(self.bottomleft, self.hb)
    hitbox = property(get_hitbox)

    def setPosition(self, map, position):
        x, y = position

        # rest using midpoint at bottom
        x += self.width/2
        cell = map.get_fg(x, y)
        if not cell.is_surface:
            cell = cell.to_bottom
        if cell.is_surface:
            # rest item on ground using center point
            angle, x, y = cell.getSurfacePosition(x, y)
            if angle is None:
                x, y = position

        x -= self.width/2

        self.bottomleft = x, y
        self.left = x
        self.right = x + self.width
        self.bottom = y
        self.top = y + self.height
        self.topleft = x, y + self.height
        self.topright = x + self.width, y + self.height
        self.bottomright = x + self.width, y
        self.center = x + self.width/2, y + self.height/2

    @classmethod
    def renderMany(cls, items):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBindTexture(GL_TEXTURE_2D, cls.texture.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glColor(1, 1, 1, 1)
        glPushMatrix()
        ox, oy = 0, 0
        for item in items:
            x, y = item.bottomleft
            glTranslatef(x - ox, y - oy, 0)
            ox, oy = x, y
            glBegin(GL_QUADS)
            glCallList(item.quad_list)
            glEnd()
        glPopMatrix()
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)

    def inScreen(self, x1, y1, x2, y2):
        x, y = self.bottomleft
        if x > x2: return False
        if (x + self.width) < x1: return False
        if y > y2: return False
        if (y + self.height) < y1: return False
        return True

class AnimatedItem(Item):
    frame = 0
    framecount = 0

    def __init__(self, map, position):
        self.width = self.fw
        self.height = self.fh
        Item.__init__(self, map, position)
        self.setPosition(map, position)

    @classmethod
    def renderMany(cls, items):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBindTexture(GL_TEXTURE_2D, cls.texture.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glColor(1, 1, 1, 1)
        glBegin(GL_QUADS)
        ox, oy = 0, 0
        for item in items:
            x, y = item.bottomleft
            su, sv = float(item.frame * item.width) / cls.texture.width, 0
            eu, ev = float((item.frame + 1) * item.width) / cls.texture.width, 1
            glTexCoord2f(su, sv)
            glVertex2f(x, y)
            glTexCoord2f(eu, sv)
            glVertex2f(x+item.width, y)
            glTexCoord2f(eu, ev)
            glVertex2f(x+item.width, y+item.height)
            glTexCoord2f(su, ev)
            glVertex2f(x, y+item.height)
        glEnd()
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)

    @classmethod
    def animate(cls, dt):
        cls.framecount += dt
        if cls.framecount > 50:
            cls.framecount = 0.00
            cls.frame += 1
            if cls.frame >= cls.texture.width/cls.fw: cls.frame = 0

class Starguy(AnimatedItem):
    texture_file = 'starguy.png'
    frame = 0
    fw = 64
    fh = 64

class Coin(AnimatedItem):
    texture_file = 'coin.png'
    frame = 0
    fw = 32
    fh = 32

def Coin1(map, position, coins=(48, )):
    x, y = position
    return [Coin(map, (dx + x, y)) for dx in coins]
def Coin2(map, position):
    return Coin1(map, position, (48, 112))
def Coin3(map, position):
    return Coin1(map, position, (22, 64, 106))

class Baddie(AnimatedItem):
    texture_file = 'badguy.png'
    fw = 64
    fh = 64

    hb = (10, 0, 40, 50)

class Component(Item):
    texture_file = 'components.png'

    def __init__(self, map, position, uvs, key_pos):
        self.key_pos = key_pos

        if self.texture is None:
            filename = data.filepath(self.texture_file)
            t = self.__class__.texture = textures.Texture(filename)
            self.__class__.width = t.width
            self.__class__.height = t.height

        self.setPosition(map, position)

        self.quad_list = glGenLists(1)
        glNewList(self.quad_list, GL_COMPILE)
        su, sv, eu, ev = uvs
        glTexCoord2f(su, sv)
        glVertex2f(0, 0)
        glTexCoord2f(eu, sv)
        glVertex2f(64, 0)
        glTexCoord2f(eu, ev)
        glVertex2f(64, 64)
        glTexCoord2f(su, ev)
        glVertex2f(0, 64)
        glEndList()

    def render(self):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBindTexture(GL_TEXTURE_2D, self.texture.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glPushMatrix()
        x, y = self.bottomleft
        glTranslatef(x, y, 0)
        glBegin(GL_QUADS)
        glCallList(self.quad_list)
        glEnd()
        glPopMatrix()
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)

    @classmethod
    def Flowerpot(cls, map, position):
        return cls(map, position, (0, 0, .25, 1), (84, 173))
    @classmethod
    def Donut(cls, map, position):
        return cls(map, position, (.25, 0, .5, 1), (185, 169))
    @classmethod
    def Icecream(cls, map, position):
        return cls(map, position, (.5, 0, .75, 1), (1, 12))
    @classmethod
    def Hat(cls, map, position):
        return cls(map, position, (.75, 0, 1, 1), (169, 75))
NUM_COMPONENTS = 4

def setPlayerStart(map, position):
    map.player_start = position

class Tree(Item):
    width = 256
    height = 512
    order = -1
    def __init__(self, map, position):
        # cell width == 128, my width == 256, so shift left to center
        x, y = position
        position = x-64, y
        self.setPosition(map, position)

        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        random.choice((trees.draw_pointy, trees.draw_fluffy))((0, 0),
            (self.width, self.height))
        glEndList()

    @classmethod
    def renderMany(cls, trees):
        glPushMatrix()
        ox, oy = 0, 0
        for tree in trees:
            x, y = tree.bottomleft
            glTranslatef(x - ox, y - oy, 0)
            ox, oy = x, y
            tree.render()
        glPopMatrix()

    def render(self):
        glCallList(self.display_list)

    def inScreen(self, x1, y1, x2, y2):
        x, y = self.bottomleft
        w2, h2 = self.width/2, self.height/2
        if x - w2 > x2: return False
        if (x + self.width + w2) < x1: return False
        if y - h2 > y2: return False
        if (y + self.height + w2) < y1: return False
        return True

class Cloud(Tree):
    width = 256
    height = 128
    order = -2
    def __init__(self, map, position):
        # cell width == 128, my width == 256, so shift left to center
        x, y = position
        position = x-64, y
        self.setPosition(map, position)

        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        clouds.draw_cloud((0, 0), (self.width, self.height))
        glEndList()


itemtypes = {
     (255, 0, 0): setPlayerStart,
     (255, 150, 0): Coin1,
     (255, 200, 0): Coin2,
     (255, 255, 0): Coin3,
     (150, 150, 255): Component.Flowerpot,
     (255, 0, 150): Component.Donut,
     (150, 0, 255): Component.Icecream,
     (255, 150, 150): Component.Hat,
     (88, 145, 68): Tree,
     (142, 142, 142): Cloud,
     (255, 0, 255): Baddie,
     (255, 255, 255): Starguy,
}

