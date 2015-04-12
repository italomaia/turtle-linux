# Author: Alexander Malmberg <alexander@malmberg.org>

import collections
import math
import pygame
import random
import OpenGL
from OpenGL import GL

import fader, fairy, grass, hill, sapling, shaders, sky


class Game(object):
  def __init__(self, width):
    shaders.Shaders.Init()
    self.width = width
    self.cx, self.cy = 0, 0  # Camera position
    self.wind_offset = 0
    self.clock = pygame.time.Clock()

    # Map from depth to set of drawables.
    self.drawables = {}
    # Map from drawable to depth.
    self.drawable_to_depth = {}

    self.transition = self.AUTUMN
    self.fairy_sounds = [pygame.mixer.Sound('music/fairy%d.ogg' % (i + 1)) for i in range(5)]
    for s in self.fairy_sounds:
      s.set_volume(0.3)

  AUTUMN = {'sky': ((0.906, 0.855, 0.263), (1, 0.992, 0.960)),
            'hill1': (0.925, 0.835, 0.361),
            'hill2': (0.919, 0.772, 0.322),
            'hill3': (0.912, 0.708, 0.283),
            'grass': ((0.576, 0.733, 0.267, 1), (0.600, 0.550, 0.208, 1)),
            }
  WINTER = {'sky': ((0.9, 0.9, 0.9), (0.8, 0.8, 0.8)),
            'hill1': (0.72, 0.78, 0.79),
            'hill2': (0.59, 0.64, 0.72),
            'hill3': (0.44, 0.48, 0.60),
            'grass': ((0.7, 0.8, 0.7, 1), (0.5, 0.7, 0.5, 1)),
            }
  RAIN = {'sky': ((0.5, 0.55, 0.5), (0.7, 0.8, 0.7)),
            'hill1': (0.4, 0.5, 0.4),
            'hill2': (0.3, 0.4, 0.3),
            'hill3': (0.2, 0.3, 0.2),
          'grass': ((0.05, 0.1, 0.05, 1), (0.0, 0.05, 0.0, 1)),
          }
  SPRING = {'sky': ((0.6, 0.8, 1), (1, 1, 1)),
            'hill1': (0.4, 0.7, 0.2),
            'hill2': (0.3, 0.6, 0.1),
            'hill3': (0.2, 0.5, 0.0),
            'grass': ((0.47, 0.68, 0.18, 1), (0.23, 0.42, 0.10, 1)),
            }
  SUMMER = {'sky': ((0.46, 0.52, 0.62), (0.73, 0.75, 0.78)),
            'hill1': (0.51, 0.62, 0.46),
            'hill2': (0.47, 0.57, 0.40),
            'hill3': (0.42, 0.51, 0.33),
            'grass': ((0.47, 0.68, 0.18, 1), (0.23, 0.42, 0.10, 1)),
            }

  def AddDrawable(self, drawable, depth):
    self.drawables.setdefault(depth, set()).add(drawable)
    self.drawable_to_depth[drawable] = depth

  # TODO(alex): for drawables that hold GL state (VBO:s and stuff)
  # need to signal deletion in some way so they can clean up
  def RemoveDrawable(self, drawable):
    depth = self.drawable_to_depth.pop(drawable)
    self.drawables[depth].remove(drawable)

  def RemoveAllDrawables(self):
    self.drawables = {}
    self.drawable_to_depth = {}

  def Run(self):
    fps_debug = 0
    timing_stats = collections.defaultdict(lambda: 0)
    while True:
      if False:
        # For debugging:
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glClearColor(0, 0, 1, 0)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT | GL.GL_COLOR_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslate(0, -1, 0)
        GL.glScale(1.0, 1.0, 1.0)
        GL.glTranslate(0, 1, 0)

      GL.glLoadIdentity()
      GL.glTranslate(self.cx, self.cy, 0)
      t0 = pygame.time.get_ticks()
      for depth in sorted(self.drawables):
        for drawable in self.drawables[depth]:
          tt0 = pygame.time.get_ticks()
          drawable.Draw()
          tt1 = pygame.time.get_ticks()
          timing_stats[str(drawable.__class__) + ' Draw'] += tt1 - tt0
      t1 = pygame.time.get_ticks()
      timing_stats['Drawing'] += t1 - t0

      t0 = pygame.time.get_ticks()
      pygame.display.flip()
      t1 = pygame.time.get_ticks()
      timing_stats['Flip'] += t1 - t0

      dt = self.clock.tick()
      fps_debug += dt
      if False and fps_debug > 5000:
        print (dt, self.clock)
        for k, v in sorted(timing_stats.iteritems()):
          print ('%5i %s' % (v, k))
        timing_stats = collections.defaultdict(lambda: 0)
        fps_debug = 0

      eventlist = pygame.event.get()
      for e in eventlist:
        if (e.type == pygame.QUIT
            or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)):
          return

      t0 = pygame.time.get_ticks()
      self.Update(dt, eventlist, pygame.key.get_pressed())
      for depth in sorted(self.drawables):
        for drawable in list(self.drawables[depth]):
          tt0 = pygame.time.get_ticks()
          drawable.Update(dt, eventlist, pygame.key.get_pressed())
          tt1 = pygame.time.get_ticks()
          timing_stats[str(drawable.__class__) + ' Update'] += tt1 - tt0
      t1 = pygame.time.get_ticks()

      self.wind_offset += 3. * dt / 1000

      timing_stats['Updating'] += t1 - t0

  def StartTitleScreen(self):
    self.sky = sky.Sky(self, self.width)
    self.hill1 = hill.Hill(
      self, list(self.transition['hill1']), 0.8, 0.0, 8.0)
    self.hill2 = hill.Hill(
      self, list(self.transition['hill2']), 0.8, 0.0, 5.0)
    self.hill3 = hill.Hill(
      self, list(self.transition['hill3']), 0.6, 0.0, 2.0)
    self.grass = grass.Grass(self)

    self.AddDrawable(self.sky, 0)
    self.AddDrawable(self.hill1, 1.1)
    self.AddDrawable(self.hill2, 1.2)
    self.AddDrawable(self.hill3, 1.3)
    self.AddDrawable(self.grass, 3)

    self.flower = sapling.OldFlower(self, -0.6)
    self.AddDrawable(self.flower, 2)

    self.fader = fader.Fader(self, (0, 0, 0), 200, 500)
    self.AddDrawable(self.fader, 10)

    self.ground = None  # Created when the time comes.

  def Transition(self, colors):
    self.transition = colors

  def Update(self, dt, events, keys):
    def Shift(this, that):
      progress = 1 - math.exp(-0.001 * dt)
      this[0] = progress * that[0] + (1 - progress) * this[0]
      this[1] = progress * that[1] + (1 - progress) * this[1]
      this[2] = progress * that[2] + (1 - progress) * this[2]
    Shift(self.sky.c1, self.transition['sky'][0])
    Shift(self.sky.c2, self.transition['sky'][1])
    Shift(self.grass.c1, self.transition['grass'][0])
    Shift(self.grass.c2, self.transition['grass'][1])
    Shift(self.hill1.color, self.transition['hill1'])
    Shift(self.hill2.color, self.transition['hill2'])
    Shift(self.hill3.color, self.transition['hill3'])

  def AddFairy(self, x, y):
    random.choice(self.fairy_sounds).play()
    f = fairy.Fairy(self, x, y)
    self.AddDrawable(f, 5)
    return f
