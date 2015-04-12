import math
import OpenGL
from OpenGL.GL import *
import pygame
import random

import drawable
import ground
import shaders


class Root(drawable.Drawable):
  def __init__(self, game, ground, x):
    self.game = game
    self.ground = ground
    self.x = x + self.game.cx
    self.y = -1
    self.dir = math.pi / 2
    self.speed = 0.01
    self.path = [(self.x, self.y, 0, 0)]
    self.length = 0
    self.growing = True
    self.time = 0
    self.color = (0.8, 0.8, 0.8, 1)
    self.to_color = self.color
    self.marked_to = 1

  def Draw(self):
    glPushMatrix()
    glTranslate(-self.game.cx, 0, 0)
    glBegin(GL_TRIANGLE_STRIP)
    f = self.time / 1.
    glColor(shaders.Lerp(min(1, f), self.color, self.to_color))
    for i, (x, y, vx, vy) in enumerate(self.path):
      thickness = 0.5 - 0.4 * i / (len(self.path) + self.length)
      glVertex(x - thickness * vy, y + thickness * vx)
      glVertex(x + thickness * vy, y - thickness * vx)
    vx = self.speed * math.cos(self.dir)
    vy = -self.speed * math.sin(self.dir)
    thickness = 0.1
    x += vx * self.length
    y += vy * self.length
    glVertex(x - thickness * vy, y + thickness * vx)
    glVertex(x + thickness * vy, y - thickness * vx)
    glColor(0, 0, 0, 1)
    glEnd()
    glPopMatrix()

  def Update(self, dt, events, keys):
    self.time += dt / 1000.
    if not self.growing:
      return
    progress = 1 - math.exp(-0.0002 * dt)
    self.speed *= 1 - progress
    if keys[pygame.K_RIGHT]:
      self.dir += 0.002 * dt
    elif keys[pygame.K_LEFT]:
      self.dir -= 0.002 * dt
    else:
      self.speed += progress * 0.05
    self.dir += dt * random.uniform(-0.002, 0.002)
    vx = self.speed * math.cos(self.dir)
    vy = -self.speed * math.sin(self.dir)
    self.length += 0.01 * dt
    while self.length > 1:
      self.length -= 1
      ox, oy = self.x, self.y
      self.x += vx
      self.y += vy
      self.path.append((self.x, self.y, vx, vy))

      tx = self.x
      ty = self.y

      if (not self.ground.map.CheckLine(ox, oy, self.x, self.y)
          or ty > -1 or tx < -self.game.width or tx > self.game.width):
        self.StopGrowing((0.3, 0.25, 0.2, 1))
        return

      if ty < -2.5:
        self.StopGrowing((0.2, 0.5, 0.2, 1))
        self.game.AddFairy(tx, ty)
        return

    self.MarkPath()

  def StopGrowing(self, to_color):
    self.growing = False
    self.to_color = to_color
    self.time = 0
    self.MarkPath()

  def MarkPath(self):
    while self.marked_to < len(self.path):
      x0, y0, _, _ = self.path[self.marked_to - 1]
      x1, y1, _, _ = self.path[self.marked_to]
      if y1 > -1.35:
        self.marked_to += 1
        continue

      if self.growing and (abs(x1 - self.x) < 0.02 or abs(y1 - self.y) < 0.02):
        break

      self.ground.map.MarkLine(1, x0, y0, x1, y1)
      self.marked_to += 1
