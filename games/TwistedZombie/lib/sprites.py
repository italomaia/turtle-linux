import pygame
import os
import utils
from config import *
import random
import math



class Points(pygame.sprite.Sprite):
    
    def __init__(self, points):
        pygame.sprite.Sprite.__init__(self)
        self.points = points
        self.font = pygame.font.Font(FONT1, 20)
        self.image = self._image()
        self.rect = self.image.get_rect(top=HEIGHT - 50, right=WIDTH - 1)

    def update(self, points):
        self.points = points
        self.image = self._image()
        self.rect = self.image.get_rect(top=HEIGHT - 50, right=WIDTH - 1)

    def _image(self):
        return self.font.render("Points: " + str(self.points) + " ", True, COLORSCORED)

class LevelIndicator(pygame.sprite.Sprite):
    
    def __init__(self, level):
        pygame.sprite.Sprite.__init__(self)
        self.level = level
        self.font = pygame.font.Font(FONT1, 20)
        self.image = self._image()
        self.rect = self.image.get_rect(top=HEIGHT - 50, right=WIDTH - 300)

#    def update(self, level):
#        self.points = points
#        self.image = self._image()
#        self.rect = self.image.get_rect(top=HEIGHT - 50, right=WIDTH - 1)

    def _image(self):
        return self.font.render("Level " + str(self.level), True, COLORSCORED)



class EnergyBar(pygame.sprite.Sprite):
    '''An energy bar'''
    def __init__(self, energy_leap):
        pygame.sprite.Sprite.__init__(self)
        self.energy_leap = energy_leap
        self.energy_percent = 100 #percent remanding of time
        self.image = self._image()
        self.rect = self.image.get_rect(bottom=HEIGHT, left=0)

    def update(self, tics):
        self.energy_percent -= self.energy_leap
        self.image = self._image()

    def add_energy(self, add_percent):
        self.energy_percent = min(100, add_percent + self.energy_percent)
        
    def _image(self):

        font = pygame.font.Font(FONT1, 14)
        text = font.render("Energy", True, BLACK)
        h = 15
        w = max(int(WIDTH * self.energy_percent / 100), 0)
        if self.energy_percent > 60: 
            color = GREEN
        elif self.energy_percent > 30:
            color = ORANGE
        else:
            color = RED
        img = utils.create_surface((w,h), color)
        w1 = img.get_rect().width
        w2 = text.get_rect().width
        if w1 > 1.2 * w2:        
            img.blit(text, (w1 - w2, 0))
        return img

class LevelTime(pygame.sprite.Sprite):

    def __init__(self, seconds=270):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(FONT1, 20)
        self.seconds = seconds 
        self.image = self._image()
        self.rect = self.image.get_rect(left=3, top = HEIGHT - 50)

    def update(self, tics):
        if tics % CLOCK_TICS: return 
        self.seconds -= 1
        self.image = self._image()

    def _image(self):
        return self.font.render("TIME: " + str(self.seconds), True, COLORSCORED)
    
class BodyPart(pygame.sprite.Sprite):

    def __init__(self, src_image, rect, offset):
        pygame.sprite.Sprite.__init__(self)
        self.image = src_image.subsurface(rect)
        self.rect = pygame.Rect((0, 0), rect.size)
        self.offset = offset

    def setup_rect(self, x, y):
        self.rect = pygame.Rect(x+self.offset[0]*SIDE, y+self.offset[1]*SIDE, \
                                self.rect.width, self.rect.height)

class Bottle(pygame.sprite.Sprite):

    def __init__(self, params):
        pygame.sprite.Sprite.__init__(self) 
        self.velocity = params["velocity"]
        self.image = utils.load_image(params["image"], (0,0,0))
        self.rotation = params["rotation"]
        self.original_image = self.image
        
        self.energy = params["energy"]
        self.destroy_all = params.get("destroy_all", False)
        self.rect = self.image.get_rect(top=random .randrange(0, 550), right=WIDTH)
        self.ang = 0
        
    def update(self):
        if not random.randrange(2): 
            '''From right to left'''
	    center = self.rect.center

            self.image = pygame.transform.rotate(self.original_image,self.ang)
	    self.rect = self.image.get_rect(center=center)                        
            self.ang += self.rotation
            self.rect.move_ip(-self.velocity, 0)

class BloodDrop(pygame.sprite.Sprite):
    def __init__ (self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface((8,8))
        self.image.set_colorkey((0,0,0))
        
        radius = random.choice(range(1,3))
        color = (random.choice(range(100,200)) , 196, 245)
        pos = (4,4)
        pygame.draw.circle(self.image, color, pos, radius)

        self.rect = self.image.get_rect()
        self.dead = True
    
    def update(self, times):
        if not self.dead:
            self.x += self.vx
            self.y += self.vy
            self.vy += 1.2
            self.rect.left = self.x
            self.rect.top = self.y
            self.dead = (self.y > 550)
        
    def set_position(self, left, top):
        ang = random.randrange(0,3600)/10.0
        ang = math.pi * ang / 180.0
        vel = random.randrange(50,250)/10.0
        self.vx = math.cos(ang) * vel
        self.vy = math.sin(ang) * vel
        self.x = left
        self.y = top
        self.rect.left = left
        self.rect.top = top
        self.dead = False

    def is_dead(self):
        return self.dead
