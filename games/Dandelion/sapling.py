import math
import OpenGL
from OpenGL.GL import *
import pygame
import random

import drawable
import bee, fairy, ground, root, seed, shaders


class Scroller(drawable.Drawable):
  def __init__(self, game, target_cy):
    self.game = game
    self.start_cy = self.game.cy
    self.target_cy = target_cy
    self.time = 0
    self.duration = 2
    self.done = False

  def Update(self, dt, events, keys):
    self.time += dt / 1000.
    f = min(1, self.time / self.duration)
    f = shaders.SmoothStep(f)
    self.game.cy = self.target_cy * f + self.start_cy * (1 - f)
    if f == 1:
      self.done = True
      self.game.RemoveDrawable(self)


def OldFlower(game, x):
  s = Sapling(game, x)
  s.age = 3333
  s.wound = 0
  s.phase = 'seeds'
  s.flower = Bud(game)
  s.flower.petals = []
  s.flower.leaves = []
  s.flower.seed_count = 1000
  s.flower.BringSeeds()
  s.flower.seeding_time = -10000
  return s


class Sapling(drawable.Drawable):
  def __init__(self, game, x):
    self.game = game
    self.x = x
    self.vcx = 0
    self.age = 0
    self.roots = []
    self.active_root = None
    self.wound = 0.001
    self.flower = None
    self.phase = 'seed'
    self.head_vx = 0
    self.head_x = 0

    self.scroll_down = None
    self.scroll_up = None

    self.varray = (ctypes.c_float * 2 * (11 * 2 + 201 * 2))()

  def Draw(self):
    glColor(0, 0, 0)
    # Seed.
    size = 0.01 * self.wound * self.age
    vi = 0
    if size > 0:
      for i in range(11):
        a = math.pi * 2 * i / 10
        self.varray[vi] = self.x, -1
        self.varray[vi + 1] = (self.x + 0.6 * size * math.cos(a),
                               -1 + size * math.sin(a))
        vi += 2
    # Stalk.
    for i, x, y, vx, vy in self.Stalk():
      thickness = 1.5 - 1.5 * i / 400
      self.varray[vi] = x - vy * thickness, y + vx * thickness
      self.varray[vi + 1] = x + vy * thickness, y - vx * thickness
      vi += 2
    glVertexPointer(2, GL_FLOAT, 8, self.varray)
    glEnableClientState(GL_VERTEX_ARRAY)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, vi)
    glDisableClientState(GL_VERTEX_ARRAY)
    if self.flower:
      self.flower.Draw()

  def Stalk(self):
    x = self.x
    y = -1
    vx = 0.000001 * self.age * math.cos(1.7)
    vy = 0.000001 * self.age * math.sin(1.7)
    wound = self.wound
    age = self.age
    if wound:
      age += 0.002 * self.head_x / wound
    yield -1, x, y, vx, vy
    for i in range(200):
      x += vx
      y += vy
      vy += (i - 0.01 * age) * wound * vx
      vx -= (i - 0.01 * age) * wound * vy
      yield i, x, y, vx, vy

  def BudPosition(self):
    i, x, y, vx, vy = list(self.Stalk())[-1]
    return x, y, math.atan2(vy, vx) - math.pi * 0.5

  def Update(self, dt, events, keys):
    self.age += dt
    progress = 1 - math.exp(-0.0003 * dt)
    # Remove this for awesome twisting.
    self.age *= 1 - progress
    if self.phase == 'seed' and self.age > 1500:
      self.game.ground = ground.Ground(self.game)
      self.game.AddDrawable(self.game.ground, 2)
      self.phase = 'sink'
      self.scroll_down = Scroller(self.game, 1.5)
      self.game.AddDrawable(self.scroll_down, 0)
    elif self.phase == 'sink':
      if self.scroll_down.done:
        self.phase = 'roots'
    elif self.phase == 'roots':
      if not self.active_root or not self.active_root.growing:
        r = root.Root(self.game, self.game.ground, self.x)
        self.roots.append(r)
        self.active_root = r
        self.game.AddDrawable(r, 2.5 + 0.001 * len(self.roots))
      if not pygame.mixer.music.get_busy():
        # TODO(alex): ugly
        self.active_root.growing = False
        self.phase = 'raise'
        self.scroll_up = Scroller(self.game, 0)
        self.game.AddDrawable(self.scroll_up, 0)
        pygame.mixer.music.load('music/grow.ogg')
        pygame.mixer.music.play()
    elif self.phase == 'raise':
      if self.scroll_up.done:
        for r in self.roots:
          self.game.RemoveDrawable(r)
        self.game.RemoveDrawable(self.game.ground)
        self.flower = Bud(self.game)
        self.game.Transition(self.game.SPRING)
        self.phase = 'bloom'
    elif self.phase == 'bloom':
      self.vcx -= 0.000001 * dt * (self.game.cx + self.x + 0.6)
      self.vcx *= math.exp(-0.002 * dt)
      self.game.cx = self.game.cx + dt * self.vcx
      if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load('music/rain.ogg')
        pygame.mixer.music.play()
        self.game.Transition(self.game.RAIN)
        self.rains = []
        self.rain_x = self.x
        self.rain_vx = 0.001
        self.rain_time = 0
        self.rain_caught = 0
        self.phase = 'rain'
    elif self.phase == 'rain':
      if keys[pygame.K_RIGHT]: self.head_vx += 0.01 * dt
      if keys[pygame.K_LEFT]: self.head_vx -= 0.01 * dt
      self.head_vx *= math.exp(-0.01 * dt)
      self.head_x += dt * self.head_vx
      # Spawn rain.
      self.rain_time += dt
      while self.rain_time > 20:
        r = Rain(self.game, self, self.rain_x, 1.1 - Rain.vy * self.rain_time)
        self.rains.append(r)
        self.game.AddDrawable(r, 5)
        self.rain_time -= 20
      self.rain_x += dt * self.rain_vx
      self.rain_vx += 0.00001 * dt * (self.x - self.rain_x)
      for r in list(self.rains):
        if r.y < -1:
          r.Explode()
          self.rains.remove(r)
        else:
          d2 = (r.x - self.flower.x) ** 2 + (r.y - self.flower.y) ** 2
          if d2 < 0.02:
            r.Explode()
            self.rains.remove(r)
            self.rain_caught += 1
      while self.rain_caught >= 100:
        self.game.AddFairy(self.flower.x, self.flower.y)
        self.rain_caught -= 100
      if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load('music/bee.ogg')
        pygame.mixer.music.play()
        self.game.Transition(self.game.SPRING)
        self.bee = bee.Bee(self.game, self.x, 1)
        self.game.AddDrawable(self.bee, 1.9)
        self.phase = 'bee'
        for r in self.rains:
          r.Explode()
        self.rains = []
    elif self.phase == 'bee':
      if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load('music/ending.ogg')
        pygame.mixer.music.play()
        self.game.Transition(self.game.AUTUMN)
        self.phase = 'absorb'
      if keys[pygame.K_RIGHT]: self.bee.vx += 0.00001 * dt
      if keys[pygame.K_LEFT]: self.bee.vx -= 0.00001 * dt
      if keys[pygame.K_UP]: self.bee.vy += 0.00001 * dt
      if keys[pygame.K_DOWN]: self.bee.vy -= 0.00001 * dt
      d2 = (self.flower.x - self.bee.x) ** 2 + (self.flower.y - self.bee.y) ** 2
      if d2 < 0.01:
        self.bee.vx *= -1
        self.bee.vy *= -1
        self.game.AddDrawable(bee.Pollen(self.game, self.bee.x, self.bee.y, self.bee.vx, self.bee.vy), 1.9)
        f = self.game.AddFairy(self.bee.x, self.bee.y)
        f.vx = self.bee.vx
        f.vy = self.bee.vy
        # Try to make sure the bee doesn't get stuck.
        self.bee.x += dt * self.bee.vx
        self.bee.y += dt * self.bee.vy
        self.bee.vx += random.gauss(0, 0.001)
    elif self.phase == 'absorb':
      free_fairies = 0
      for f in list(self.game.drawable_to_depth):
        if isinstance(f, fairy.Fairy):
          f.dest = self.flower.x, self.flower.y
          d2 = (f.x - self.flower.x) ** 2 + (f.y - self.flower.y) ** 2
          if d2 < 0.01:
            self.game.RemoveDrawable(f)
            self.flower.seed_count += 1
          else:
            free_fairies += 1
      if free_fairies == 0:
        self.flower.BringSeeds()
        if self.flower.seeds:
          self.phase = 'seeds'
        else:
          self.phase = 'done'  # Game over.
    elif self.phase == 'seeds':
      if any(e.type == pygame.KEYDOWN for e in events):
        s = self.flower.seeds.pop(random.randrange(len(self.flower.seeds)))
        s.x = self.flower.x
        s.y = self.flower.y
        s.rot += self.flower.rot
        s.Fly(self.game)
        self.phase = 'done'
      if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load('music/just_wind.ogg')
        pygame.mixer.music.play()
    elif self.phase == 'done':
      if self.game.cy == 1.5:  # Discard seeds in underground view.
        self.flower.seeds = []
      if abs(self.x + self.game.cx) > 2:  # Discard whole thing if off-screen.
        self.game.RemoveDrawable(self)
    if self.flower:
      self.wound = (1 - progress) * self.wound - progress * 0.00005
      self.flower.x, self.flower.y, self.flower.rot = self.BudPosition()
      self.flower.Update(dt, events, keys)


class Bud(drawable.Drawable):
  def __init__(self, game):
    self.game = game
    self.age = 0
    self.x = 0
    self.y = 0
    self.rot = 0
    self.vx = 0
    self.vy = 0
    self.seeds = []
    self.seed_count = 0
    self.seeding_time = float('inf')
    self.petals = []
    self.leaves = []
    for i in 1, -1:
      self.leaves.append(Petal((0, 0, 0), 0, 0.05, i * math.pi, -0.55 * i * math.pi))

  def Draw(self):
    glPushMatrix()
    glTranslate(self.x, self.y, 0)
    glRotate(self.rot * 180 / math.pi, 0, 0, 1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex(0, 0)
    size = 0.01 * (1 - math.exp(-0.0005 * self.age))
    for i in range(11):
      a = math.pi * 2 * i / 10
      glVertex(size * math.cos(a), 2 * size * math.sin(a))
    glEnd()
    for x in self.petals + self.leaves:
      x.Draw()
    seed.Seed.StartDrawMany()
    for x in self.seeds:
      x.DrawOneOfMany()
    seed.Seed.StopDrawMany()
    glPopMatrix()

  def Update(self, dt, events, keys):
    self.age += dt
    if 7000 < self.age < self.seeding_time and not self.petals:
      for i in range(10):
        self.petals.append(Petal((1, 0.9, 0), 0.04, 0.04, (-1) ** i * math.pi, math.pi * (i - 4.5) / 9))
      for i in range(8):
        self.petals.append(Petal((1, 0.8, 0), 0.04, 0.03, (-1) ** i * math.pi, math.pi * (i - 3.5) / 9))
      for i in range(8):
        self.petals.append(Petal((1, 0.9, 0), 0.02, 0.02, (-1) ** i * math.pi, math.pi * (i - 3.5) / 9))
      for x in self.petals + self.leaves:
        x.Open()
    seeding = (1 - math.exp(-0.0005 * max(0, self.age - self.seeding_time)))
    if seeding > 0:
      for s in self.seeds:
        s.rot = seeding * s.final_rot
        s.length = seeding * s.final_length
    for x in self.petals + self.leaves:
      x.Update(dt, events, keys)


  def BringSeeds(self):
    for r in (0.03, 0.06), (0.07, 0.08), (0.08, 0.09):
      for i in range(20):
        s = seed.Seed(0, 0)
        s.final_rot = math.pi * 2 * i / 20 + random.uniform(-0.06, 0.06) - math.pi
        s.final_length = random.uniform(*r)
        s.length = 0
        self.seeds.append(s)
    self.seeds = random.sample(self.seeds, min(self.seed_count, len(self.seeds)))
    self.seeding_time = self.age
    for x in self.petals + self.leaves:
      x.Detach(self.game, self)
    self.petals = []
    self.leaves = []


class Petal(drawable.Drawable):
  def __init__(self, color, size, growth, arc, open):
    self.game = None
    self.color = color
    self.size = size
    self.growth = growth
    self.arc = arc
    self.rot = 0
    self.open = open
    self.age = 0
    self.opening_start = float('inf')
    self.x = 0
    self.y = 0

  def Draw(self):
    glColor(*self.color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex(self.x, self.y)
    size = self.size + self.growth * (1 - math.exp(-0.0005 * self.age))
    rot = self.rot + self.open * (1 - math.exp(-0.0005 * max(0, self.age - self.opening_start)))
    for i in range(20):
      a = self.arc * (i + 1) / 20
      x = 0.5 * size * math.sin(a)
      y = size - size * math.cos(a)
      glVertex(self.x + x * math.cos(rot) - y * math.sin(rot), self.y + x * math.sin(rot) + y * math.cos(rot))
    glEnd()
    glColor(0, 0, 0)

  def Update(self, dt, events, keys):
    self.age += dt
    if self.game:  # Free-floating.
      self.x += dt * self.vx
      self.y += dt * self.vy
      if self.y < -1.1:
        self.game.RemoveDrawable(self)

  def Open(self):
    self.opening_start = self.age

  def Detach(self, game, flower):
    self.game = game
    self.x = flower.x
    self.y = flower.y
    self.rot = flower.rot
    self.vx = random.gauss(0, 0.0001)
    self.vy = random.gauss(-0.0005, 0.0001)
    game.AddDrawable(self, 5)


class Rain(drawable.Drawable):
  vy = -0.003
  def __init__(self, game, sapling, x, y):
    self.game = game
    self.sapling = sapling
    self.x = x
    self.y = y
    self.vx = random.gauss(0, 0.0002)
    self.vy = Rain.vy
    self.size = 0.2
    self.explode = None

  def Draw(self):
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glEnable(GL_BLEND)

    glColor(1, 1, 1, self.explode if self.explode else 0.8)
    glBegin(GL_TRIANGLES)
    glVertex(self.x - 10 * self.vx, self.y - 10 * self.vy)
    glVertex(self.x + 10 * self.vx - self.vy, self.y + 10 * self.vy + self.vx)
    glVertex(self.x + 10 * self.vx + self.vy, self.y + 10 * self.vy - self.vx)
    glEnd()

    glDisable(GL_BLEND)

  def Update(self, dt, events, keys):
    if self.explode is not None:
      self.vy -= 0.00001 * dt
      self.explode *= math.exp(-0.01 * dt)
      if self.explode < 0.00001:
        self.game.RemoveDrawable(self)
    self.x += dt * self.vx
    self.y += dt * self.vy

  def Explode(self):
    self.vy *= -0.5
    self.vx = random.gauss(0, 0.001)
    self.explode = 0.8

