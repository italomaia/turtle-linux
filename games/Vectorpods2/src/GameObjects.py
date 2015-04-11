#! /usr/bin/env python

# Vectorpods 2 - A arcade space shooter programmed by PyMike
# Copyright (C) 2007  PyMike
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import sys, os
import math, random

import pygame
from pygame.locals import *

from Engine import *
from Constants import *


class Ship(Sprite):

    def __init__(self):

        Sprite.__init__(self, self.containers)
        self.points = SHIP_ACCEL_POINTS
        self.pos = [320, 240]
        self.velocity = [0, 0]
        self.angle = 180
        self.scale = 0.6
        self.accel = 0.02
        self.timer = 0
        self.rotate_points()

    def update(self):
        self.points = SHIP_NORMAL_POINTS
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.timer += 1
        if self.timer >= 4:
            self.timer = 0
        
        key = pygame.key.get_pressed()
        if key[K_LEFT]:
            self.angle += 3
        if key[K_RIGHT]:
            self.angle -= 3
        if key[K_UP]:
            if self.timer == 2:
                self.points = SHIP_ACCEL_POINTS
            self.velocity[0] += self.accel*math.sin(math.radians(self.angle))
            self.velocity[1] += self.accel*math.cos(math.radians(self.angle))
        if key[K_DOWN]:
            if self.timer == 2:
                self.points = SHIP_ACCEL_POINTS
            self.velocity[0] -= self.accel*math.sin(math.radians(self.angle))
            self.velocity[1] -= self.accel*math.cos(math.radians(self.angle))

        if self.pos[0] > SCREEN_SIZE[0]:
            self.velocity[0] = -self.velocity[0]
        if self.pos[0] < 0:
            self.velocity[0] = -self.velocity[0]
        if self.pos[1] > SCREEN_SIZE[1]:
            self.velocity[1] = -self.velocity[1]
        if self.pos[1] < 0:
            self.velocity[1] = -self.velocity[1]

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        for i in range(15):
            Particle(self.pos)


class Shot(Sprite):

    def __init__(self, pos, angle):

        Sprite.__init__(self, self.containers)

        self.pos = list(pos)
        self.points = SHOT_POINTS
        self.size = [2, 2]
        self.angle = angle
        self.speed = 6
        self.nose_distance = 10
        self.life = 50
        self.scale = 1.0
        self.rect = Rect(self.pos[0], self.pos[1], 2, 2)

        self.pos[0] += self.nose_distance*math.sin(math.radians(self.angle))
        self.pos[1] += self.nose_distance*math.cos(math.radians(self.angle))
        self.rotate_points()

    def update(self):
        self.life -= 1
        if self.life <= 0:
            pygame.sprite.Sprite.kill(self)

        self.pos[0] += self.speed*math.sin(math.radians(self.angle))
        self.pos[1] += self.speed*math.cos(math.radians(self.angle))
        self.rect.center = self.pos

        if self.pos[0] > 640:
            pygame.sprite.Sprite.kill(self)
        if self.pos[0] < 0:
            pygame.sprite.Sprite.kill(self)
        if self.pos[1] > 480:
            pygame.sprite.Sprite.kill(self)
        if self.pos[1] < 0:
            pygame.sprite.Sprite.kill(self)

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        for i in range(5):
            Particle(self.pos)

class EnemyShot(Sprite):

    def __init__(self, pos, angle):

        Sprite.__init__(self, self.containers)

        self.pos = list(pos)
        self.points = SHOT_POINTS
        self.size = [2, 2]
        self.angle = angle
        self.speed = -3.5
        self.nose_distance = 20
        self.scale = 1.0
        self.rect = Rect(self.pos[0], self.pos[1], 2, 2)

        self.pos[0] -= self.nose_distance*math.sin(math.radians(self.angle))
        self.pos[1] -= self.nose_distance*math.cos(math.radians(self.angle))
        self.life = 60
        self.rotate_points()

    def update(self):

        self.life -= 1
        if self.life <= 0:
            pygame.sprite.Sprite.kill(self)

        self.pos[0] += self.speed*math.sin(math.radians(self.angle))
        self.pos[1] += self.speed*math.cos(math.radians(self.angle))
        self.rect.center = self.pos

        if self.pos[0] > 640:
            pygame.sprite.Sprite.kill(self)
        if self.pos[0] < 0:
            pygame.sprite.Sprite.kill(self)
        if self.pos[1] > 480:
            pygame.sprite.Sprite.kill(self)
        if self.pos[1] < 0:
            pygame.sprite.Sprite.kill(self)

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        for i in range(5):
            Particle(self.pos)


class Asteroid(Sprite):

    def __init__(self, pos, scale=1.25):

        Sprite.__init__(self, self.containers)

        self.points = random.choice([ASTEROID1_POINTS, ASTEROID2_POINTS, ASTEROID3_POINTS])
        self.pos = list(pos)
        self.angle = random.randrange(360)
        self._angle = self.angle
        self.scale = scale + 0.25

        self.speed = random.choice([-0.75, -0.5, -0.25, -0.125, -0.0625, -0.625/2, 0.625/2, 0.0625, 0.125, 0.25, 0.5, 0.75])
        self.rect = Rect(self.pos[0], self.pos[1], 30*self.scale*2, 30*self.scale*2)
        self.rotate_points()
        self.setVelocity()

    def setVelocity(self):
        self.velocity = [math.sin(math.radians(self._angle))*self.speed, math.cos(math.radians(self._angle))*self.speed]

    def update(self):
        self.angle += 0.5
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.rect.center = self.pos

        if self.pos[0] > 640:
            self.velocity[0] = -self.velocity[0]
            self.pos[0] = 639
        if self.pos[0] < 0:
            self.velocity[0] = -self.velocity[0]
            self.pos[0] = 1
        if self.pos[1] > 480:
            self.velocity[1] = -self.velocity[1]
            self.pos[1] = 479
        if self.pos[1] < 0:
            self.velocity[1] = -self.velocity[1]
            self.pos[1] = 1

    def hit(self):
        self.kill()
        for i in range(10):
            Particle(self.pos)
        if self.scale > 0.5:
            if self.scale == 1.5:
                a1 = Asteroid((self.pos[0]-16, self.pos[1]-16), self.scale-0.75)
                a2 = Asteroid((self.pos[0]+16, self.pos[1]+16), self.scale-0.75)
                a1._angle = random.randrange(210, 330)
                a2._angle = random.randrange(30, 150)
                a1.setVelocity()
                a2.setVelocity()
            elif self.scale == 1.0:
                Asteroid((self.pos[0], self.pos[1]-12), self.scale-0.75)
                Asteroid((self.pos[0]+12, self.pos[1]+12), self.scale-0.75)
                Asteroid((self.pos[0]-12, self.pos[1]+12), self.scale-0.75)

class Ufo(Sprite):

    def __init__(self):

        Sprite.__init__(self, self.containers)

        self.points = UFO_POINTS
        self.pos = [0, 240]
        self.velocity = [random.choice([0.5, 1]), random.choice([-1, -0.5, 0.5, 1])]
        self.angle = 0
        self.scale = 0.6
        self.rect = Rect(self.pos[0], self.pos[1], 15, 15)
        self.timer = 0
        self.rotate_points()

    def update(self):

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.rect.center = self.pos

        if self.pos[0] > 640:
            self.velocity[0] = -self.velocity[0]
        if self.pos[0] < 0:
            self.velocity[0] = -self.velocity[0]
        if self.pos[1] > 480:
            self.velocity[1] = -self.velocity[1]
        if self.pos[1] < 0:
            self.velocity[1] = -self.velocity[1]

    def draw(self, surface):
        self.drawpoints = []
        for p in self.points:
            newX = int(p[0]*math.cos(math.radians(-self.angle))*self.scale - p[1]*math.sin(math.radians(-self.angle))*self.scale + self.pos[0])
            newY = int(p[0]*math.sin(math.radians(-self.angle))*self.scale + p[1]*math.cos(math.radians(-self.angle))*self.scale + self.pos[1])
            self.drawpoints.append((newX,newY))
        if self.use_antialias:
            pygame.draw.aalines(surface,(255,255,255),0,self.drawpoints,1)
        else:
            pygame.draw.lines(surface,(200,200,200),0,self.drawpoints,1)

    def kill(self):
        Sprite.kill(self)
        for i in range(15):
            Particle(self.pos)


class Particle(Sprite):

    def __init__(self, pos):

        Sprite.__init__(self, self.containers)

        self.pos = list(pos)
        self.size = [1, 1]
        self.vx = random.choice([-3, -2.75, -2.5, -2.25 -2, -1.75, -1.5, -1.25, -1, -0.75, -0.5, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3])/2
        self.vy = random.choice([-3, -2.75, -2.5, -2.25 -2, -1.75, -1.5, -1.25, -1, -0.75, -0.5, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3])/2
        self.color = 255

    def update(self):

        self.pos[0] += self.vx
        self.pos[1] += self.vy

        self.color -= 3
        if self.color <= 50:
            self.kill()

        if self.pos[0] > 640:
            self.kill()
        if self.pos[0] < 0:
            self.kill()
        if self.pos[1] > 480:
            self.kill()
        if self.pos[1] < 0:
            self.kill()

    def draw(self, surface):
        if self.use_antialias:
            surface.fill((self.color, self.color, self.color), (int(self.pos[0]), int(self.pos[1]), self.size[0], self.size[1]))
        else:
            surface.fill((200, 200, 200), (int(self.pos[0]), int(self.pos[1]), self.size[0], self.size[1]))


class Exhaust(Sprite):

    def __init__(self, pos, angle):

        Sprite.__init__(self, self.containers)

        self.pos = list(pos)
        self.size = [1, 1]
        self.v = random.choice([0.5, 0.75, 1, 1.25, 1.5, 1.75, 2])/2
        self.color = 255
        self.tail_distance = 7
        self.angle = angle
        self.angle += random.randrange(-20, 20)

        self.pos[0] -= self.tail_distance*math.sin(math.radians(self.angle))
        self.pos[1] -= self.tail_distance*math.cos(math.radians(self.angle))

    def update(self):

        self.pos[0] -= self.v*math.sin(math.radians(self.angle))
        self.pos[1] -= self.v*math.cos(math.radians(self.angle))

        self.color -= 4
        if self.color <= 50:
            self.kill()

        if self.pos[0] > 640:
            self.kill()
        if self.pos[0] < 0:
            self.kill()
        if self.pos[1] > 480:
            self.kill()
        if self.pos[1] < 0:
            self.kill()

    def draw(self, surface):
        if self.use_antialias:
            surface.fill((self.color, self.color, self.color), (int(self.pos[0]), int(self.pos[1]), self.size[0], self.size[1]))
        else:
            surface.fill((200, 200, 200), (int(self.pos[0]), int(self.pos[1]), self.size[0], self.size[1]))
