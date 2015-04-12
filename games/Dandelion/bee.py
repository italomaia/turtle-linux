import math
import OpenGL
from OpenGL.GL import *
import pygame
import random

import drawable
import bee, ground, root, seed

class Bee(drawable.Drawable):
  def __init__(self, game, x, y):
    self.game = game
    self.x = x
    self.y = y
    self.vx = 0
    self.vy = 0

  def Draw(self):
    glColor(0, 0, 0)
    glBegin(GL_TRIANGLE_FAN)
    for i in range(8):
      a = math.pi * 2 * i / 7
      glVertex(self.x + 0.01 * math.cos(a), self.y + 0.01 * math.sin(a))
    glEnd()

  def Update(self, dt, events, keys):
    self.vy -= 0.000001 * dt
    v = math.sqrt(self.vx ** 2 + self.vy ** 2)
    max_speed = 0.005
    if v > max_speed:
      self.vx *= max_speed / v
      self.vy *= max_speed / v
    self.x += dt * self.vx
    self.y += dt * self.vy
    if self.game.width - self.game.cx < self.x:
      self.x -= 2 * self.game.width
    if self.x < -self.game.width - self.game.cx:
      self.x += 2 * self.game.width
    if 1 < self.y:
      self.y -= 2
    if self.y < -1:
      if self.game.transition == self.game.SPRING:  # Bee season.
        self.y += 2
      else:
        self.game.RemoveDrawable(self)


class Pollen(drawable.Drawable):
  def __init__(self, game, x, y, vx, vy):
    self.game = game
    self.particles = [[x, y, random.gauss(vx * 0.4, 0.0001), random.gauss(vy * 0.4, 0.0001)] for i in range(100)]

  def Update(self, dt, events, keys):
    for p in self.particles:
      p[3] -= 0.000001 * dt
      p[0] += dt * p[2]
      p[1] += dt * p[3]
    if all(p[1] < -1.1 for p in self.particles):
      self.game.RemoveDrawable(self)

  def Draw(self):
    glColor(1, 1, 0)
    glBegin(GL_TRIANGLES)
    for x, y, vx, vy in self.particles:
      l = math.sqrt(vx ** 2 + vy ** 2)
      vx *= 0.01 / l
      vy *= 0.01 / l
      glVertex(x, y)
      glVertex(x + vx, y + vy)
      glVertex(x + vx + vy, y + vy - vx)
    glEnd()
