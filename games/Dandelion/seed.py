# Author: Alexander Malmberg <alexander@malmberg.org>

import math
import OpenGL
from OpenGL.GL import *
import pygame
import random

import drawable
import sapling
import shaders


  # b: a
  # g: hair_length
  # r: length
  # w: cy
  # z: rot
  # y: y
  # x: x
seed_vshader_src = """\
#version 120

const vec4 color = vec4(0.15, 0.05, 0, 0.5);

void main() {
  vec2 v;
  float s, c;
  s = sin(gl_Color.b);
  c = cos(gl_Color.b);
  v.x = gl_Color.g * s;
  v.y = gl_Color.g * c + gl_Vertex.w + gl_Color.r;

  s = sin(gl_Vertex.z);
  c = cos(gl_Vertex.z);
  vec4 vv;
  vv.x =  v.x * c - v.y * s + gl_Vertex.x;
  vv.y =  v.x * s + v.y * c + gl_Vertex.y;
  vv.z = 0;
  vv.w = 1;

  gl_Position = gl_ModelViewProjectionMatrix * vv;
  gl_FrontColor = color;
}
"""
"""
x, y, cy, length, a, hair_length

dx = sin(a) * hair_length
dy = cos(a) * hair_length

(sin(a) * hair_length, cy + length + cos(a) * hair_length)

(0, cy)                x, y, rot, cy, length=0, hair_length=0, a=0
(0, cy + length)       x, y, rot, cy, length=length, hair_length=0, a=0
(dx, cy + length + dy) x, y, rot, cy, length=length, hair_length=hair_length, a=a
"""


class Seed(drawable.Drawable):

  seed_program = None

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.cx = 0
    self.cy = 0
    self.rot = 0
    self.length = random.uniform(0.03, 0.09)
    self.hair_length = 0.016
    self.hairs = [math.pi / 4 * (j - 1) + random.uniform(-0.3, 0.3)
                  for j in xrange(3)]
    self.phase = 'attached'

    if Seed.seed_program is None:
      Seed.seed_program = shaders.CompileProgram('seed', seed_vshader_src)

  @classmethod
  def StartDrawMany(self):
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    glColor(0.15, 0.05, 0, 0.5)
    glUseProgram(Seed.seed_program)
    glBegin(GL_LINES)

  @classmethod
  def StopDrawMany(self):
    glEnd()
    glUseProgram(0)
    glDisable(GL_BLEND)

  def DrawOneOfMany(self):
    rr = self.rot
    glColor(0, 0, 0)
    glVertex(self.x, self.y, rr, self.cy)
    glColor(self.length, 0, 0)
    glVertex(self.x, self.y, rr, self.cy)
    for a in self.hairs:
      glColor(self.length, 0, 0)
      glVertex(self.x, self.y, rr, self.cy)
      glColor(self.length, self.hair_length, a)
      glVertex(self.x, self.y, rr, self.cy)

  def Draw(self):
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    glColor(0.15, 0.05, 0, 0.5)
    glUseProgram(Seed.seed_program)

    glBegin(GL_LINES)
    rr = self.rot
    glColor(0, 0, 0)
    glVertex(self.x, self.y, rr, self.cy)
    glColor(self.length, 0, 0)
    glVertex(self.x, self.y, rr, self.cy)
    for a in self.hairs:
      glColor(self.length, 0, 0)
      glVertex(self.x, self.y, rr, self.cy)
      glColor(self.length, self.hair_length, a)
      glVertex(self.x, self.y, rr, self.cy)
    glEnd()

    glUseProgram(0)
    glDisable(GL_BLEND)

  def Fly(self, game):
    self.game = game
    game.AddDrawable(self, 2)
    self.vx = 0
    self.vy = 0
    self.spin = 0
    # Put rotation axis at the top.
    self.cy = -self.length
    self.x -= math.sin(self.rot) * self.length
    self.y += math.cos(self.rot) * self.length

    # Populate space with pickups.
    self.pickups = []
    self.pickup_i = 10
    self.pickup_x = self.x
    self.pickup_y = self.y
    for i in range(self.pickup_i):
      p = Pickup(self.game,
                 self.pickup_x + i + 0.5,
                 self.pickup_y + random.uniform(-0.2, 0.2))
      self.pickups.append(p)
      self.game.AddDrawable(p, 1.9)
    self.snow = []
    self.warmth = []

    pygame.mixer.music.load('music/wind.ogg')
    pygame.mixer.music.play()
    self.phase = 'wind'

  def Update(self, dt, events, keys):
    if self.phase == 'wind':
      wind = 0.00001, -0.00001
    else:
      wind = 0, -0.00001
    ovx = self.vx
    self.vx += wind[0]
    self.vy += wind[1]
    control = 0.0001
    self.vx += control if keys[pygame.K_RIGHT] else 0
    self.vx -= control if keys[pygame.K_LEFT] else 0
    self.vy += control if keys[pygame.K_UP] and self.phase != 'drop' else 0
    self.vy -= control if keys[pygame.K_DOWN] else 0
    terminal_v = 0.001
    v2 = self.vx ** 2 + self.vy ** 2
    if v2 > terminal_v ** 2:
      self.vx *= terminal_v / math.sqrt(v2)
      self.vy *= terminal_v / math.sqrt(v2)
    self.x += dt * self.vx
    self.y += dt * self.vy
    # Stay on screen.
    self.x = min(self.game.width - self.game.cx, max(-self.game.width - self.game.cx, self.x))
    self.y = min(1, max(-1, self.y))

    while self.pickup_i + self.pickup_x + 0.5 < self.x + self.game.width * 2:
      p = Pickup(self.game,
                 self.pickup_x + self.pickup_i + 0.5,
                 self.pickup_y + random.uniform(-0.2, 0.2))
      self.pickup_i += 1
      self.pickups.append(p)
      self.game.AddDrawable(p, 1.9)

    # Swinging back and forth with arbitrary formulas.
    dr = -math.atan(10000 * (self.vx - ovx))
    self.spin += dt * 0.00001 * (dr - self.rot)
    self.spin *= math.exp(-0.002 * dt)
    self.rot += dt * self.spin

    if self.phase == 'wind':
      # Check for pickups.
      for i, p in enumerate(self.pickups):
        d2 = (p.x - self.x) ** 2 + (p.y - self.y) ** 2
        if d2 < p.size ** 2:
          self.pickups.pop(i)
          self.game.AddFairy(p.x, p.y)
          p.Gotcha()
          break
      # Let camera follow.
      target_cx = min(self.game.cx, -self.x)
      f = math.exp(-0.01 * dt)
      self.game.cx = f * self.game.cx + (1 - f) * target_cx
      if not pygame.mixer.music.get_busy():
        for p in self.pickups:
          p.Gotcha()
        self.game.Transition(self.game.WINTER)
        pygame.mixer.music.load('music/snow.ogg')
        pygame.mixer.music.play()
        self.phase = 'snow'
    elif self.phase == 'snow':
      # Spawn snow.
      if random.random() < 0.2:
        s = Snow(self.game, self.x + random.uniform(-self.game.width, self.game.width), 1.1)
        self.snow.append(s)
        self.game.AddDrawable(s, 4)
      if random.random() < 0.01:
        w = Warmth(self.game, self.x + random.uniform(-self.game.width, self.game.width), -2)
        self.warmth.append(w)
        self.game.AddDrawable(w, 3.5)
      if not pygame.mixer.music.get_busy():
        self.phase = 'drop'
    elif self.phase == 'drop':
      if self.y == -1:
        self.game.RemoveDrawable(self)
        self.game.AddDrawable(sapling.Sapling(self.game, self.x), 4)
        pygame.mixer.music.load('music/roots.ogg')
        pygame.mixer.music.play()
    if self.phase in 'snow or drop':
      # Check for collision.
      for s in self.snow:
        d2 = (s.x - self.x) ** 2 + (s.y - self.y) ** 2
        if d2 < s.size ** 2:
          self.vy = -0.001
      for i, w in enumerate(self.warmth):
        d2 = (w.x - self.x) ** 2 + (w.y - self.y) ** 2
        if d2 < w.size ** 2:
          self.warmth.pop(i)
          w.Explode()
          self.game.AddFairy(w.x, w.y)
          break


class Pickup(drawable.Drawable):
  def __init__(self, game, x, y):
    self.game = game
    self.x = x
    self.y = y
    self.alpha = 0
    self.size = 0.1
    self.exploding = 0

  def Draw(self):
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    glColor(1, 1, 1, self.alpha)
    glPushMatrix()
    glTranslate(self.x, self.y, 0)
    glRotate((self.game.cx + self.x) * 20, 0, 0, 1)
    glBegin(GL_TRIANGLE_FAN)
    for i in range(8):
      a = math.pi * 2 * i / 7
      glVertex(self.size * math.cos(a), self.size * math.sin(a))
    glEnd()
    glColor(0, 0, 0, 1)
    glPopMatrix()
    glDisable(GL_BLEND)

  def Update(self, dt, events, keys):
    progress = 1 - math.exp(-0.001 * dt)
    self.alpha = (1 - progress) * self.alpha + progress * (0.5 if not self.exploding else 0)
    self.size += dt * self.exploding
    if self.size > 0.4:
      self.game.RemoveDrawable(self)

  def Gotcha(self):
    self.exploding = 0.0001


class Snow(drawable.Drawable):
  def __init__(self, game, x, y):
    self.game = game
    self.x = x
    self.y = y
    self.size = 0.1

  def Draw(self):
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glEnable(GL_BLEND)
    glColor(0.1, 0.1, 0.2, 1)
    glPushMatrix()
    glTranslate(self.x, self.y, 0)
    glBegin(GL_TRIANGLE_FAN)
    for i in range(8):
      a = math.pi * 2 * i / 7
      glVertex(self.size * math.cos(a), self.size * math.sin(a))
    glEnd()
    glColor(0, 0, 0, 1)
    glPopMatrix()
    glDisable(GL_BLEND)

  def Update(self, dt, events, keys):
    if self.y + self.size < -1 - self.game.cy:
      self.game.RemoveDrawable(self)
    self.y -= 0.001 * dt


warmth_vshader = """\
#version 120

varying vec2 position;
varying vec4 color;

void main() {
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  position = gl_Vertex.xy;
  color = gl_Color.rgba;
}
"""
warmth_fshader = """\
#version 120

varying vec2 position;
varying vec4 color;

void main() {
  gl_FragColor.rgb = color.rgb;
  gl_FragColor.a = color.a * exp(-100 * length(position) * length(position));
}
"""

class Warmth(drawable.Drawable):
  program = None
  def __init__(self, game, x, y):
    self.game = game
    self.x = x
    self.y = y
    self.size = 0.2
    self.explode = None

    if Warmth.program == None:
      Warmth.program = shaders.CompileProgram(
        'warmth', warmth_vshader, warmth_fshader)

  def Draw(self):
    glPushMatrix()
    glTranslate(self.x, self.y, 0)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glEnable(GL_BLEND)

    glUseProgram(Warmth.program)

    if self.explode is None:
      glColor(0.6, 0.8, 0, 1)
    else:
      glColor(0.6, 0.8, 0, self.explode)
    glBegin(GL_TRIANGLE_STRIP)
    glVertex(-1, -1)
    glVertex(-1,  1)
    glVertex( 1, -1)
    glVertex( 1,  1)
    glEnd()

    glUseProgram(0)
    glDisable(GL_BLEND)
    glPopMatrix()

  def Update(self, dt, events, keys):
    if self.explode is not None:
      self.explode *= math.exp(-0.01 * dt)
      if self.explode < 0.00001:
        self.game.RemoveDrawable(self)
    if self.y - 1 > 1 - self.game.cy:
      self.game.RemoveDrawable(self)
    self.y += 0.0002 * dt

  def Explode(self):
    self.explode = 1
