# Author: Alexander Malmberg <alexander@malmberg.org>

import ctypes
import math
import random
import OpenGL
from OpenGL.GL import *

import chunked_drawable


class Hill(chunked_drawable.ChunkedDrawable):
  def __init__(self, game, color, height, displacement, speed):
    self.game = game
    self.color = color
    self.height = height
    self.displacement = displacement
    self.detail = 100
    self.num_vert = self.detail * 2 + 2
    super(Hill, self).__init__(game, speed)

  def FillIBO(self, ibo):
    idx = (ctypes.c_uint * self.num_vert)()
    for i in xrange(self.num_vert):
      idx[i] = i
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

  def InitialState(self):
    p = random.uniform(0, 0.3)
    dp = random.uniform(-0.2, 0.2)
    return p, dp

  def GenerateChunk(self, _, state, vbo):
    p, dp = state
    step = 1 / float(self.detail)
    points = (ctypes.c_float * 2 * self.num_vert)()
    points[0] = (0, -1)
    points[1] = (0, p * self.height + self.displacement - 1)
    for i in xrange(self.detail):
      ddp = random.uniform(-1, 1)
      if p < self.displacement:
        dp = 0.8 * abs(dp)
      elif p > 0.5 * self.height:
        ddp = -abs(ddp)
      dp += ddp * step * self.speed
      dp *= 0.99
      p += dp * step * self.speed
      sp = max(0, p * self.height + self.displacement)
      points[i * 2 + 2] = ((i + 1) * step, -1)
      points[i * 2 + 3] = ((i + 1) * step, sp - 1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, points, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return p, dp

  def Draw(self):
    glColor(*self.color)
    glEnableClientState(GL_VERTEX_ARRAY)
    super(Hill, self).Draw()
    glDisableClientState(GL_VERTEX_ARRAY)

  def DrawChunk(self):
    glVertexPointer(2, GL_FLOAT, 8, ctypes.cast(0, ctypes.c_void_p))
    glDrawElements(GL_TRIANGLE_STRIP, self.num_vert, GL_UNSIGNED_INT, None)
