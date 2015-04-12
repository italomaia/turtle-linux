# Author: Alexander Malmberg <alexander@malmberg.org>

import ctypes
import math
import random
import OpenGL
from OpenGL.GL import *

import drawable


class ChunkedDrawable(drawable.Drawable):
  def __init__(self, game, speed=1.0):
    self.game = game
    self.speed = speed
    self.chunk_width = self.game.width * 2.2

    self.ibo, self.vbo1, self.vbo2 = glGenBuffers(3)
    self.FillIBO(self.ibo)

    self.x = 0

    self.state = self.InitialState()
    self.state = self.GenerateChunk(0, self.state, self.vbo1)
    self.state = self.GenerateChunk(1, self.state, self.vbo2)

  def ScrollTo(self, x):
    # Game wants left side of screen to be at 'x'.
    chunk_space = x / self.speed / self.chunk_width
    while chunk_space > self.x + 1:
      self.vbo1, self.vbo2 = self.vbo2, self.vbo1
      self.state = self.GenerateChunk(self.x + 2, self.state, self.vbo2)
      self.x += 1
    return math.modf(chunk_space)[0]

  def FillIBO(self, ibo):
    """Fill the given ibo. The indices are shared by all chunks."""
    pass

  def InitialState(self):
    """Return starting state for chunk generation."""
    pass

  def GenerateChunk(self, state, vbo):
    """Generate vertices into the given vbo, return new state.

    Each chunk lives in [0,1) horizontally. This gets mapped to
    [x * self.chunk_width - self.game.width,
     (x + 1) * self.chunk_width - self.game.width) in world space.
    """
    pass

  def DrawChunk(self):
    glVertexPointer(2, GL_FLOAT, 8, ctypes.cast(0, ctypes.c_void_p))
    glDrawElements(GL_TRIANGLE_STRIP, self.num_idx, GL_UNSIGNED_INT, None)

  def Draw(self):
    glPushMatrix()
    glLoadIdentity()
    glTranslate(-self.game.width, 0, 0)
    glScale(self.chunk_width, 1, 0)

    f = self.ScrollTo(-self.game.cx)
    glTranslate(-f, self.game.cy, 0)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

    glBindBuffer(GL_ARRAY_BUFFER, self.vbo1)
    self.DrawChunk()

    glTranslate(1, 0, 0)

    glBindBuffer(GL_ARRAY_BUFFER, self.vbo2)
    self.DrawChunk()

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glPopMatrix()
