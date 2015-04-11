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

sounds = []
def load_sound(file, volume=1.0):
    sound = pygame.mixer.Sound(os.path.join("data", "sounds", file))
    sound.set_volume(volume)
    return sound

def load_sounds():
    sounds.append(load_sound("shoot.wav", 0.2))
    sounds.append(load_sound("boom.wav"))
    sounds.append(load_sound("ufo-shoot.wav", 0.2))
    sounds.append(load_sound("background.wav", 0.7))
    return sounds

def load_font(file, size):
    return pygame.font.Font(os.path.join("data", "fonts", file), size)

def render_text(surface, text, font, pos, center=False):
    ren = font.render(text, 1, (255, 255, 255))
    if center:
        pos = [pos[0] - ren.get_width()/2, pos[1] - ren.get_height()/2]
    surface.blit(ren, pos)
    return ren

def play_shoot():
    sounds[0].play()

def play_boom():
    sounds[1].play()

def play_ufo():
    sounds[2].play()

def play_bg():
    sounds[3].play(-1)

def load_highscore():
    f = os.path.expanduser("~/.vectorpods2")
    if os.path.exists(f):
        hs = open(os.path.expanduser("~/.vectorpods2"), "rU").read()
        return int(hs)
    else:
        hs = open(os.path.expanduser("~/.vectorpods2"), "wr").write(str(0))
        return 0
    
def save_highscore(score):
    open(os.path.expanduser("~/.vectorpods2"), "wr").write(str(score))

def PointCollision(asteroid, point):
    x = point[0]
    y = point[1]
    Lines = []
    index = 0
    for index in xrange(len(asteroid.drawpoints)):
        p0 = asteroid.drawpoints[index]
        try: p1 = asteroid.drawpoints[index+1]
        except: p1 = asteroid.drawpoints[0]
        Lines.append([p0,p1])
    for l in Lines:
        p0 = l[0]
        p1 = l[1]
        x0 = p0[0]; y0 = p0[1]
        x1 = p1[0]; y1 = p1[1]
        test = (y - y0)*(x1 - x0) - (x - x0)*(y1 - y0)
        if test > 0: return False
    return True

def __lineCollision(a, b):
    s1 = a[0]
    s2 = b[0]
    e1 = a[1]
    e2 = b[1]
    A = e1[0] - s1[0]
    B = e1[1] - s1[1]
    C = e2[0] - s2[0]
    D = e2[1] - s2[1]
    E = s1[1] - s2[1]
    F = s1[0] - s2[0]
 
    denom = (D*A)-(C*B)
    if denom == 0:
        return False
    numA = C*E - D*F
    numB = A*E - B*F

    Ta = numA / float(denom)
    Tb = numB / float(denom)
    if (Ta >= 0 and Ta <= 1) and (Tb >= 0 and Tb <= 1):
        return True
    return False

def Collision(obj1, obj2):
    lines1 = []
    lines2 = []
    for n in xrange(len(obj1)):
        lines1.append([obj1[n-1], obj1[n]])
    for n in xrange(len(obj2)):
        lines2.append([obj2[n-1], obj2[n]])
    for line1 in lines1:
        for line2 in lines2:
            if __lineCollision(line1, line2):
                return True
    return False

def GeneratePos():
    up = [random.randrange(0, 640), random.randrange(0, 140)]
    down = [random.randrange(0, 640), random.randrange(340, 480)]
    return random.choice([up, down])

def AngleToTarget(pos1, pos2):
    x = pos2[0] - pos1[0]
    y = pos2[1] - pos1[1]
    angle = math.atan2(y, x)
    return int(270.0 - (angle * 180.0)/math.pi)

stars = []
for i in range(50):
    stars.append([random.randrange(640), random.randrange(480)])

def Stars():
    return stars


class Group(pygame.sprite.Group):

    def draw(self, surface):
        for s in self.sprites():
            s.draw(surface)

    def update(self):
        for s in self.sprites():
            s.update()

class Sprite(pygame.sprite.Sprite):

    def __init__(self, *groups):

        pygame.sprite.Sprite.__init__(self, groups)
        self.use_antialias = True

    def rotate_points(self):
        self.drawpoints = []
        for p in self.points:
            newX = int(p[0]*math.cos(math.radians(-self.angle))*self.scale - p[1]*math.sin(math.radians(-self.angle))*self.scale + self.pos[0])
            newY = int(p[0]*math.sin(math.radians(-self.angle))*self.scale + p[1]*math.cos(math.radians(-self.angle))*self.scale + self.pos[1])
            self.drawpoints.append((newX,newY))

    def draw(self, surface):
        self.rotate_points()
        if self.use_antialias:
            pygame.draw.aalines(surface,(255,255,255),1,self.drawpoints,1)
        else:
            pygame.draw.lines(surface,(200,200,200),1,self.drawpoints,1)
        
