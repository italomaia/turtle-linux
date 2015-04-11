#! /usr/bin/env python

import sys, os
import math, random

import pygame
from pygame.locals import *

from Utilities import *

class Camera(object):
    
    def __init__(self, player, worldsize):
        self.player = player
        self.rect = Rect(0, 0, 400, 320)
        self.rect.center = self.player.rect.center
        self.world = Rect(0, 0, worldsize[0], worldsize[1])
    
    def update(self):
        self.rect.center = self.player.rect.center
        self.rect.clamp_ip(self.world)
    
    def Rect(self, obj):
        return Rect(obj.rect.x - self.rect.x, obj.rect.y - self.rect.y, obj.rect.w, obj.rect.h)
    

class Group(object):
 
    def __init__(self):
        self.sprites = []
  
    def __len__(self):
        return len(self.sprites)
 
    def __iter__(self):
        return iter(self.sprites)
 
    def __getitem__(self, i):
        return self.sprites[i]
 
    def add(self, obj):
        if obj not in self.sprites:
            self.sprites.append(obj)
 
    def remove(self, obj):
        if obj in self.sprites:
            self.sprites.remove(obj)
    
    def draw(self, surface, camera=None):
        for obj in self.sprites:
            if camera:
                surface.blit(obj.image, camera.Rect(obj))
            else:
                obj.draw(surface)
    
    def update(self):
        for obj in self.sprites:
            obj.update()

class Object(object):
  
    def __init__(self, groups):
        self.groups = groups
        for g in self.groups:
            g.add(self)
 
    def kill(self):
        for g in self.groups:
            g.remove(self)
        self.groups = []

    def alive(self):
        return len(self.groups) != 0
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
    
    def update(self):
        pass

class Player(Object):
    
    def __init__(self):
        Object.__init__(self, self.groups)
        self.images = [LoadImage("up-1.png"), LoadImage("up-2.png"), FlipImage(LoadImage("side-1.png")), FlipImage(LoadImage("side-2.png")), LoadImage("down-1.png"), LoadImage("down-2.png"), LoadImage("side-1.png"), LoadImage("side-2.png")]
        self.image = self.images[0]
        self.rect = SmoothRect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect.center = (200, 160)
        self.dir = 0
        self.pressed = [0, 0, 0, 0]
        self.held = [0, 0, 0, 0]
        self.frame = 0
        self.rel_timer = 0
        self.hp = 10
        self.hit_timer = 0
        self.powerup = 0
        self.ptype = None
    
    def update(self):
        self.dir = self.dir % 4 #precaution
        self.frame += 1
        self.hit_timer -= 1
        
        self.held = [0, 0, 0, 0]
        key = pygame.key.get_pressed()
        if key[K_UP]:
            self.held[0] = 1   
        if key[K_LEFT]:
            self.held[1] = 1
        if key[K_DOWN]:
            self.held[2] = 1   
        if key[K_RIGHT]:
            self.held[3] = 1
        
        self.rel_timer -= 1
        if self.powerup > 0:
            self.powerup -= 1
        if self.powerup <= 0:
            self.ptype = None
        if self.rel_timer <= 0:
            if key[K_SPACE]:
                Sounds["shoot"].play()
                if self.powerup > 0:
                    if self.ptype == "plasma":
                        size = 2
                        self.rel_timer = 6
                    elif self.ptype == "rocket":
                        size = 3
                        self.rel_timer = 10
                else:
                    size = 1
                    self.rel_timer = 5
                Shot(self.rect.center, self.dir, size)

        i = 0
        pressed = False
        moving = False
        for x in self.pressed:
            if x != 0:
                pressed = True
                self.dir = i
                moving = True
            i += 1
    
        if not pressed:
            i = 0
            for x in self.held:
                if x != 0:
                    pressed = True
                    self.dir = i
                    moving = True
                i += 1

        increment = self.dir*2
        if moving:
            increment = self.frame/4%2 + self.dir*2
            self.rect.move_ip(int(math.sin(math.radians(self.dir*90))*-4), int(math.cos(math.radians(self.dir*90))*-4))
        self.image = self.images[increment]
    
    def collide(self, rect):
        if self.rect.colliderect(rect):
            if self.rect.right < rect.left+8:
                self.rect.right = rect.left
            if self.rect.left > rect.right-8:
                self.rect.left = rect.right
            if self.rect.bottom < rect.top+8:
                self.rect.bottom = rect.top
            if self.rect.top > rect.bottom-8:
                self.rect.top = rect.bottom

class Shot(Object):
    
    def __init__(self, pos, dir, power=1):
        Object.__init__(self, self.groups)
        self.dir = dir
        self.image = pygame.Surface((6*power, 12*power))
        self.image.fill((127, 255, 127))
        if power == 3:
            self.image = LoadImage("rocket-shot.png")
        self.image = pygame.transform.rotate(self.image, self.dir*90)
        self.rect = SmoothRect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect.center = pos
        self.damage = power
        
        if self.dir == 0:
            self.rect.move_ip(-6, -9)
            Flash((self.rect.centerx-3, self.rect.centery-9))
        if self.dir == 2:
            self.rect.move_ip(-6, 9)
            Flash((self.rect.centerx, self.rect.centery+9))
        if self.dir == 1:
            self.rect.move_ip(-6, 0)
            Flash((self.rect.centerx-9, self.rect.centery))
        if self.dir == 3:
            self.rect.move_ip(6, 0)
            Flash((self.rect.centerx+9, self.rect.centery))
    
    def update(self):
        self.rect.move_ip(math.sin(math.radians(self.dir*90))*-14, math.cos(math.radians(self.dir*90))*-14)

    def kill(self):
        if self.damage == 3:
            BigExplosion(self.rect.center)
        else:
            Flash(self.rect.center)
        Object.kill(self)

class Tree(Object):
    
    def __init__(self, pos):
        Object.__init__(self, self.groups)
        self.image = LoadImage("tree.png")
        self.rect = SmoothRect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect.topleft = pos

class Zombie(Object):
    
    def __init__(self, pos):
        Object.__init__(self, self.groups)
        self.images = [LoadImage("z-1.png"), LoadImage("z-2.png")]
        self.image = self.images[0]
        self.rect = SmoothRect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect.topleft = pos
        self.frame = 0
        self.speed = random.choice([1, 1.5, 2, 2.5])
        if self.speed == 1:
            self.hp = 4
        if self.speed == 1.5:
            self.hp = 3
        if self.speed == 2:
            self.hp = 2
        if self.speed == 2.5:
            self.hp = 1
        
    def move(self, player, camera):
        self.frame += 1
        area = Rect(0, 0, 400, 320)
        if area.colliderect(camera.Rect(self)):
            self.image = self.images[self.frame/4%2]
            if self.rect.left >= player.rect.right:
                self.rect.move_ip(-self.speed, 0)
            if self.rect.right <= player.rect.left:
                self.rect.move_ip(self.speed, 0)
            if self.rect.top >= player.rect.bottom:
                self.rect.move_ip(0, -self.speed)
            if self.rect.bottom <= player.rect.top:
                self.rect.move_ip(0, self.speed)
    
    def hit(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
            Explosion(self.rect.center)

class Explosion(Object):
    
    def __init__(self, pos):
        Object.__init__(self, self.groups)
        self.images = [LoadImage("ze-1.png"), LoadImage("ze-2.png"), LoadImage("ze-3.png"), LoadImage("ze-4.png")]
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.frame = 0
        
    def update(self):
        self.frame += 1
        self.image = self.images[self.frame/4%4]
        if self.frame >= 16:
            self.kill()

class BigExplosion(Object):
    
    def __init__(self, pos):
        Object.__init__(self, self.groups)
        self.image = LoadImage("explosion.png")
        self.rect = self.image.get_rect(center=pos)
        self.frame = 0
        Sounds["explosion"].play()
        
    def update(self):
        self.frame += 1
        if not self.frame % 2:
            self.image = FlipImage(self.image)
        if self.frame >= 16:
            self.kill()

class Flash(Object):
    
    def __init__(self, pos):
        Object.__init__(self, self.groups)
        self.image = LoadImage("flash.png")
        self.rect = SmoothRect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect.center = pos
        self.frame = 0
        
    def update(self):
        self.frame += 1
        if self.frame >= 2:
            self.kill()

class PowerUp(Object):
    
    def __init__(self, pos, img):
        Object.__init__(self, self.groups)
        self.image = LoadImage(img)
        self.rect = SmoothRect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect.center = (pos[0]+24, pos[1]+24)
        self.scale = 1.0
        self.dead = False
    
    def update(self):
        if self.dead:
            self.scale -= 0.2
        if self.scale <= 0:
            self.kill()
        c = self.rect.center
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width()*self.scale), int(self.image.get_height()*self.scale)))
        self.rect = self.image.get_rect(center=c)

class Health(PowerUp):
    
    def __init__(self, pos):
        PowerUp.__init__(self, pos, "health.png")

class Plasma(PowerUp):
    
    def __init__(self, pos):
        PowerUp.__init__(self, pos, "plasma.png")

class Rocket(PowerUp):
    
    def __init__(self, pos):
        PowerUp.__init__(self, pos, "rocket.png")
