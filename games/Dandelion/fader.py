# Author: Alexander Malmberg <alexander@malmberg.org>

import OpenGL
from OpenGL.GL import *

import drawable


class Fader(drawable.Drawable):
  def __init__(self, game, color, start, duration):
    self.game = game
    self.color = color
    self.start = start
    self.duration = duration
    self.time = 0

  def Draw(self):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    alpha = 1 - float(self.time - self.start) / self.duration
    glColor(self.color[0], self.color[1], self.color[2], alpha)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()  # Fill screen regardless of aspect ratio.
    glBegin(GL_TRIANGLE_STRIP)
    glVertex(-1, -1)
    glVertex(-1,  1)
    glVertex( 1, -1)
    glVertex( 1,  1)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glDisable(GL_BLEND)

  def Update(self, dt, events, keys):
    self.time += dt
    if self.time > self.start + self.duration:
      self.game.RemoveDrawable(self)
