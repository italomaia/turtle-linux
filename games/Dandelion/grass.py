# Author: Alexander Malmberg <alexander@malmberg.org>

import ctypes
import math
import random
import OpenGL
from OpenGL.GL import *

import chunked_drawable
import shaders


class Grass(chunked_drawable.ChunkedDrawable):
  def __init__(self, game):
    self.c1 = [0.576, 0.733, 0.267, 1]
    self.c2 = [0.600, 0.550, 0.208, 1]
    self.detail = 5
    self.num_grass = 300
    self.num_vert = (self.detail * 2 + 1) * self.num_grass
    self.num_idx =  (self.detail * 2 + 3) * self.num_grass - 1

    super(Grass, self).__init__(game)

  def FillIBO(self, ibo):
    idx = (ctypes.c_uint * self.num_idx)()
    i = j = 0
    for _ in xrange(self.num_grass):
      if i != 0:
        idx[j] = i
        j += 1

      for k in xrange(self.detail + 1):
        idx[j] = i
        j += 1
        i += 1

        if k != 0:
          idx[j] = i
          j += 1
          i += 1

      idx[j] = i - 1
      j += 1

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

  def GenerateChunk(self, x, _, vbo):
    vert = (ctypes.c_float * (self.num_vert * 5))()

    i = 0
    for _ in xrange(self.num_grass):
      position = random.uniform(0, self.chunk_width)
      orientation = random.uniform(-0.2, 0.05)
      height = random.gammavariate(5, 2)
      color = random.uniform(0, 1)

      y0 = -1 + 0.02 * height
      y1 = -1

      lp = []
      rp = []
      ys = []

      # The position for purposes of wind takes into account the
      # offset of the chunk.
      wr = (x * self.chunk_width - self.game.width
            + position + random.uniform(-0.3, 0.3))

      for k in xrange(self.detail + 1):
        y = k / float(self.detail)
        p = math.log(1 + y)
        # TODO(alex): should calculate minimum separation based on
        # resolution. Should also have a global object somewhere with
        # LoD, resolution, minimum separation info
        # TODO(alex): could bump up min separation, fade color towards
        # top. really helps if we can't get anti-aliasing
        min_sep = 0.001
        if p * 0.005 > min_sep:
          l = p * (orientation - 0.005)
          r = p * (orientation + 0.005)
        else:
          l = p * orientation - min_sep / 2
          r = p * orientation + min_sep / 2

        vert[i + 0] = (l + position) / self.chunk_width
        vert[i + 1] = y * y1 + (1 - y) * y0
        vert[i + 2] = (1 - y) * (1 - y)
        vert[i + 3] = wr
        vert[i + 4] = color
        i += 5

        if k != 0:
          vert[i + 0] = (r + position) / self.chunk_width
          vert[i + 1] = y * y1 + (1 - y) * y0
          vert[i + 2] = (1 - y) * (1 - y)
          vert[i + 3] = wr
          vert[i + 4] = color
          i += 5

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vert, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

  def Draw(self):
    shaders.Shaders.UseWindColorMix(self.game.wind_offset, self.c1, self.c2)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableVertexAttribArray(1)
    super(Grass, self).Draw()
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableVertexAttribArray(1)
    glUseProgram(0)

  def DrawChunk(self):
    glVertexPointer(4, GL_FLOAT, 20, ctypes.cast(0, ctypes.c_void_p))
    glVertexAttribPointer(1, 1, GL_FLOAT, False, 20,
                          ctypes.cast(16, ctypes.c_void_p))
    glDrawElements(GL_TRIANGLE_STRIP, self.num_idx, GL_UNSIGNED_INT, None)
