import random
from OpenGL.GL import *

import data
import textures
from euclid import *

GRAVITY = Vector2(0, -1./32)

class Puff(object):
    texture = None
    texture_file = 'puff.png'

    done = False

    def __init__(self, position, color, num=20, speed=2, gravity=1.,
            fade=.05):
        self.position = position
        self.color = list(color)
        self.gravity = gravity
        self.fade = fade

        self.spots = []
        for i in range(num):
            r = Matrix3.new_rotate(math.pi * 2 * random.random())
            m = speed + speed * random.random()
            self.spots.append((Point2(*position), r * Vector2(0, m)))

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

    def animate(self, dt):
        self.color[3] -= self.fade
        if self.color[3] <= 0:
            self.done = True
            return
        for s in self.spots:
            s[0].__iadd__(s[1])
            s[1].__iadd__(GRAVITY * dt * self.gravity)

    @classmethod
    def renderMany(cls, puffs):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindTexture(GL_TEXTURE_2D, cls.texture.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

        glPushMatrix()
        ox, oy = 0, 0
        for puff in puffs:
            glColor4f(*puff.color)
            for spot in puff.spots:
                x, y = spot[0]
                glTranslatef(x - ox, y - oy, 0)
                ox, oy = x, y
                glBegin(GL_QUADS)
                glCallList(puff.quad_list)
                glEnd()
        glPopMatrix()

        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)

if __name__ == '__main__':
    import sys
    import pygame
    from pygame.locals import *

    pygame.init()
    vw, vh = viewport = (1024, 768)
    screen = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)
    clock = pygame.time.Clock()

    # set up 2d mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, 0, vw, vh)
    glOrtho(0, vw, 0, vh, -50, 50)
    glMatrixMode(GL_MODELVIEW)
    glClearColor(.3, .3, .3, 1)
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_MAP2_VERTEX_3)

    puff = Puff((512, 512), (1., .7, .3, 1.))

    while 1:
        ts = clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: sys.exit()
            if e.type == KEYDOWN and e.key == K_ESCAPE: sys.exit()
            if e.type == KEYDOWN and e.key == K_SPACE:
                puff = Puff((512, 512), (1., .7, .3, 1.), gravity=0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        puff.animate(ts)
        puff.renderMany([puff])
        pygame.display.flip()

