import ctypes
import math
import pygame
import random
import OpenGL
from OpenGL.GL import *

import drawable
import shaders


class CollisionMap(object):
  def __init__(self, width, height, x0, y0, x1, y1):
    self.width = width
    self.height = height
    self.x0 = x0
    self.x1 = x1
    self.y0 = y0
    self.y1 = y1
    self.map = (ctypes.c_ubyte * self.height * self.width)()

  def MapToGrid(self, x, y):
    x = int((x - self.x0) / (self.x1 - self.x0) * self.width)
    y = int((y - self.y0) / (self.y1 - self.y0) * self.height)
    x = min(self.width - 1, max(0, x))
    y = min(self.height - 1, max(0, y))
    return x, y

  def CheckRectangle(self, x0, y0, x1, y1):
    x0, y0 = self.MapToGrid(x0, y0)
    x1, y1 = self.MapToGrid(x1, y1)
    for y in xrange(y0, y1 + 1):
      for x in xrange(x0, x1 + 1):
        if self.map[x][y]:
          return False
    return True

  def FillRectangle(self, v, x0, y0, x1, y1):
    x0, y0 = self.MapToGrid(x0, y0)
    x1, y1 = self.MapToGrid(x1, y1)
    for y in xrange(y0, y1 + 1):
      for x in xrange(x0, x1 + 1):
        self.map[x][y] = v

  def ValueAt(self, x, y):
    x, y = self.MapToGrid(x, y)
    return self.map[x][y]

  def MarkAt(self, v, x, y):
    x, y = self.MapToGrid(x, y)
    self.map[x][y] = v

  def Line(self, x0, y0, x1, y1):
    """Brensenham's line algorithm."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    f = 0
    if dx > dy:
      if x1 < x0:
        x0, y0, x1, y1 = x1, y1, x0, y0
      if y1 < y0:
        s = -1
      else:
        s = 1
      yield x0, y0
      while x0 < x1:
        x0 += 1
        f += dy
        while f > dx:
          y0 += s
          f -= dx
        yield x0, y0
    else:
      if y1 < y0:
        x0, y0, x1, y1 = x1, y1, x0, y0
      if x1 < x0:
        s = -1
      else:
        s = 1
      yield x0, y0
      while y0 < y1:
        y0 += 1
        f += dx
        while f > dy:
          x0 += s
          f -= dy
        yield x0, y0

  def MarkLine(self, v, x0, y0, x1, y1):
    x0, y0 = self.MapToGrid(x0, y0)
    x1, y1 = self.MapToGrid(x1, y1)

    for x, y in self.Line(x0, y0, x1, y1):
      self.map[x][y] = v

  def CheckLine(self, x0, y0, x1, y1):
    x0, y0 = self.MapToGrid(x0, y0)
    x1, y1 = self.MapToGrid(x1, y1)

    for x, y in self.Line(x0, y0, x1, y1):
      if self.map[x][y]:
        return False
    return True

class Ground(drawable.Drawable):
  def __init__(self, game):
    self.game = game
    self.time = 0

    self.map = CollisionMap(400, 400,
                            -self.game.width, -1,
                            self.game.width, -2.5)

    self.l = glGenLists(1)
    glNewList(self.l, GL_COMPILE)

    light_orange = 0.912, 0.708, 0.283, 1
    orange = 0.17, 0.11, 0.07
    dark_orange = 0.24, 0.17, 0.11, 1

    glBegin(GL_TRIANGLE_STRIP)

    glColor(*light_orange)
    glVertex(-game.width, -1)
    glVertex( game.width, -1)
    glColor(*((v1 + v2) / 2 for v1, v2 in zip(orange, dark_orange)))
    glVertex(-game.width, -1.1)
    glVertex( game.width, -1.1)
    glColor(*orange)
    glVertex(-game.width, -1.3)
    glVertex( game.width, -1.3)

    glColor(*dark_orange)
    glVertex(-game.width, -2.3)
    glVertex( game.width, -2.3)

    glColor((0.263, 0.690, 0.133, 1))
    glVertex(-game.width, -2.4)
    glVertex( game.width, -2.4)

    glColor((1, 1, 1, 1))
    glVertex(-game.width, -2.5)
    glVertex( game.width, -2.5)

    glEnd()

    shaders.Shaders.UseRock(
      (0.300, 0.220, 0.140, 1),
      (0.419, 0.329, 0.235, 1),
      (0.309, 0.227, 0.156, 1))
    margin = 0.005

    def DrawRock(hsteps, x0, y0, x1, y1):
      glBegin(GL_TRIANGLE_STRIP)
      glVertex(x0, y0 * 0.95 + y1 * 0.05, 0, 0)
      glVertex(x0, y0 * 0.05 + y1 * 0.95, 0, 1)
      for i in xrange(1, hsteps):
        x = i / float(hsteps)
        lo = y0 + random.gauss(0, (y1 - y0) * 0.01)
        hi = y1 + random.gauss(0, (y1 - y0) * 0.01)
        x += random.gauss(0, 0.01)
        glVertex(x0 + (x1 - x0) * x, lo, x, 0)
        glVertex(x0 + (x1 - x0) * x, hi, x, 1)
      glVertex(x1, y0 * 0.95 + y1 * 0.05, 1, 0)
      glVertex(x1, y0 * 0.05 + y1 * 0.95, 1, 1)
      glEnd()

    def DrawRocks(num, wr, hr):
      for _ in xrange(num):
        w = random.uniform(*wr)
        x0 = random.uniform(-self.game.width + w / 2, self.game.width - w / 2)
        x0 -= w / 2
        x1 = x0 + w
        y0 = random.uniform(-1.3, -2.0)
        y1 = y0 - random.uniform(*hr)
        if self.map.CheckRectangle(x0, y0, x1, y1):
          DrawRock(int(w * 25), x0, y0, x1, y1)
          self.map.FillRectangle(
            1, x0 + margin, y0 - margin, x1 - margin, y1 + margin)

    DrawRocks(40, (0.3, 0.4), (0.2, 0.25))
    DrawRocks(60, (0.2, 0.25), (0.15, 0.20))

    glUseProgram(0)

    glEndList()

  def Draw(self):
    glPushMatrix()
    glTranslate(-self.game.cx, 0, 0)
    glCallList(self.l)

    # Cheesy glow.
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    a = math.sin(self.time * 3) / 2 + 0.5
    glColor(0.4, 0.2, 0.2, a)
    glBegin(GL_TRIANGLE_STRIP)
    glVertex(-self.game.width, -2.5)
    glVertex( self.game.width, -2.5)
    glColor(0, 0, 0, 0)
    glVertex(-self.game.width, -2.2)
    glVertex( self.game.width, -2.2)
    glEnd()
    glDisable(GL_BLEND)

    # Collision map debugging.
    if False:
      glEnable(GL_BLEND)
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
      glBegin(GL_QUADS)
      xw = self.map.x1 - self.map.x0
      yw = self.map.y1 - self.map.y0
      for ix in xrange(self.map.width):
        x = ix / float(self.map.width) * xw + self.map.x0
        for iy in xrange(self.map.height):
          y = iy / float(self.map.height) * yw + self.map.y0
          if self.map.map[ix][iy]:
            glColor(1, 1, 1, 0.4)
          else:
            glColor(1, 0, 1, 0.4)
          glVertex(x, y)
          glVertex(x + xw / self.map.width, y)
          glVertex(x + xw / self.map.width, y + yw / self.map.width)
          glVertex(x, y + yw / self.map.width)
      glEnd()
      glDisable(GL_BLEND)

    glPopMatrix()

  def Update(self, dt, events, keys):
    self.time += dt / 1000.
