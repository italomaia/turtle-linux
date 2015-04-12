# Author: Alexander Malmberg <alexander@malmberg.org>

import ctypes
import math
import pygame
import random
import OpenGL
from OpenGL.GL import *

import drawable
import shaders


fairy_vshader = """\
#version 120

varying vec2 position;

void main() {
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  position = gl_Vertex.xy;
}
"""
fairy_fshader = """\
#version 120

varying vec2 position;

void main() {
  gl_FragColor.rgb = vec3(1, 1, 1);
  gl_FragColor.a = 0.00001 / dot(position, position);
}
"""


class Fairy(drawable.Drawable):
  program = None
  dlist = None
  def __init__(self, game, x, y):
    self.game = game
    self.x = x
    self.y = y
    self.vx = 0
    self.vy = 0
    self.speed = 0.001
    self.dest = None  # Go here if set.

    if Fairy.program == None:
      Fairy.program = shaders.CompileProgram(
        'fairy', fairy_vshader, fairy_fshader)

    if Fairy.dlist == None:
      Fairy.dlist = glGenLists(1)
      glNewList(Fairy.dlist, GL_COMPILE)
      glColor(1, 1, 1, 1)
      glBegin(GL_TRIANGLE_STRIP)
      glVertex(-0.1, -0.1)
      glVertex(-0.1,  0.1)
      glVertex( 0.1, -0.1)
      glVertex( 0.1,  0.1)
      glEnd()
      glEndList()

  def Draw(self):
    glPushMatrix()
    glTranslate(self.x, self.y, 0)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glEnable(GL_BLEND)

    glUseProgram(Fairy.program)

    glCallList(Fairy.dlist)

    glUseProgram(0)
    glDisable(GL_BLEND)
    glPopMatrix()

  def Update(self, dt, events, keys):
    if self.dest:
      self.speed *= math.exp(-0.0001 * dt)
      dx, dy = self.dest
    else:
      dx = -self.game.cx
      dy = -self.game.cy
    self.vx += 0.00001 * dt * (dx - self.x)
    self.vy += 0.00001 * dt * (dy - self.y)
    v = math.sqrt(self.vx ** 2 + self.vy ** 2)
    if abs(v) > 0.00001:
      self.vx *= self.speed / v
      self.vy *= self.speed / v
    self.x += dt * self.vx
    self.y += dt * self.vy
