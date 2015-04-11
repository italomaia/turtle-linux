#! /usr/bin/env python

import sys, os

import pygame
from pygame.locals import *

BackgroundColor = (89, 178, 89)
Sounds = {}

def LoadImage(filename):
    img = pygame.image.load(os.path.join("data", filename))
    img.set_colorkey(BackgroundColor, RLEACCEL)
    return img.convert()

def FlipImage(img):
    return pygame.transform.flip(img, 1, 0)

def Pixelize(surface, tilesize):
    new = pygame.Surface(surface.get_size())
    for y in range(surface.get_height()/tilesize):
        for x in range(surface.get_width()/tilesize):
            pygame.draw.rect(new, surface.get_at((x*tilesize, y*tilesize)), (x*tilesize, y*tilesize, tilesize, tilesize))
    return new

def LoadSound(filename):
    snd = pygame.mixer.Sound(os.path.join("data", filename))
    snd.set_volume(0.5)
    return snd

class _rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class SmoothRect(object):
    
    def __init__(self, x, y, w, h):
        self._r = _rect(x, y, w, h)
   
    def __getattr__(self, name):
        if name in ('top', 'y'):
            return self._r.y
        elif name in ('left', 'x'):
            return self._r.x
        elif name == 'bottom':
            return self._r.y + self._r.h
        elif name == 'right':
            return self._r.x + self._r.w
        elif name == 'topleft':
            return self._r.x, self._r.y
        elif name == 'bottomleft':
            return self._r.x, self._r.y + self._r.h
        elif name == 'topright':
            return self._r.x + self._r.w, self._r.y
        elif name == 'bottomright':
            return self._r.x + self._r.w, self._r.y + self._r.h
        elif name == 'midtop':
            return self._r.x + self._r.w / 2, self._r.y
        elif name == 'midleft':
            return self._r.x, self._r.y + self._r.h / 2
        elif name == 'midbottom':
            return self._r.x + self._r.w / 2, self._r.y + self._r.h
        elif name == 'midright':
            return self._r.x + self._r.w, self._r.y + self._r.h / 2
        elif name == 'center':
            return self._r.x + self._r.w / 2, self._r.y + self._r.h / 2
        elif name == 'centerx':
            return self._r.x + self._r.w / 2
        elif name == 'centery':
            return self._r.y + self._r.h / 2
        elif name == 'size':
            return self._r.w, self._r.h
        elif name == 'width' or name == "w":
            return self._r.w
        elif name == 'height' or name == "h":
            return self._r.h
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        if name == 'top' or name == 'y':
            self._r.y = int(value)
        elif name == 'left' or name == 'x':
            self._r.x = int(value)
        elif name == 'bottom':
            self._r.y = int(value) - self._r.h
        elif name == 'right':
            self._r.x = int(value) - self._r.w
        elif name == 'topleft':
            self._r.x, self._r.y = int(value[0]), int(value[1])
        elif name == 'bottomleft':
            self._r.x = int(value[0])
            self._r.y = int(value[1]) - self._r.h
        elif name == 'topright':
            self._r.x = int(value[0]) - self._r.w
            self._r.y = int(value[1])
        elif name == 'bottomright':
            self._r.x = int(value[0]) - self._r.w
            self._r.y = int(value[1]) - self._r.h
        elif name == 'midtop':
            self._r.x = int(value[0]) - self._r.w / 2
            self._r.y = int(value[1])
        elif name == 'midleft':
            self._r.x = int(value[0])
            self._r.y = int(value[1]) - self._r.h / 2
        elif name == 'midbottom':
            self._r.x = int(value[0]) - self._r.w / 2
            self._r.y = int(value[1]) - self._r.h
        elif name == 'midright':
            self._r.x = int(value[0]) - self._r.w
            self._r.y = int(value[1]) - self._r.h / 2
        elif name == 'center':
            self._r.x = int(value[0]) - self._r.w / 2
            self._r.y = int(value[1]) - self._r.h / 2
        elif name == 'centerx':
            self._r.x = int(value) - self._r.w / 2
        elif name == 'centery':
            self._r.y = int(value) - self._r.h / 2
        elif name == 'size':
            if int(value[0]) < 0 or int(value[1]) < 0:
                self._ensure_proxy()
            self._r.w, self._r.h = int(value)
        elif name == 'width':
            if int(value) < 0:
                self._ensure_proxy()
            self._r.w = int(value)
        elif name == 'height':
            if int(value) < 0:
                self._ensure_proxy()
            self._r.h = int(value)
        elif name == "_r":
            self.__dict__["_r"] = value
        else:
            raise AttributeError, name

    def __len__(self):
        return 4

    def __getitem__(self, key):
        return (self._r.x, self._r.y, self._r.w, self._r.h)[key]

    def __setitem__(self, key, value):
        r = [self._r.x, self._r.y, self._r.w, self._r.h]
        r[key] = value
        self._r.x, self._r.y, self._r.w, self._r.h = r
        
    def move(self, dx, dy):
        return Rect(self._r.x + dx, self._r.y + dy, self._r.h, self._r.w)
        
    def move_ip(self, dx, dy):
        self._r.x += dx
        self._r.y += dy
        
    def colliderect(self, rect):
        return _rect_collide(self, rect)
        
    def collidepoint(self, rect):
        return rect._r.x >= self._r.x and \
               rect._r.y >= self._r.y and \
               rect._r.x < self._r.x + self._r.w and \
               rect._r.y < self._r.y + self._r.h
    
    def clamp_ip(self, rect):
        if self.left < rect.left:
            self.left = rect.left
        if self.right > rect.right:
            self.right = rect.right
        if self.top < rect.top:
            self.top = rect.top
        if self.bottom > rect.bottom:
            self.bottom = rect.bottom
        
def _rect_collide(a, b):
    return a.x + a.w > b.x and b.x + b.w > a.x and \
           a.y + a.h > b.y and b.y + b.h > a.y
