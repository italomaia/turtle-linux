import pygame
import random
from sprites import BloodDrop
import utils
from config import *

class Explotion(object):

    def __init__(self):
        self.blood = pygame.sprite.RenderUpdates()
        self.explotion = False    
        self.blood_flag = 0 
        for x in xrange(333):    
            blood_drop = BloodDrop()
            self.blood.add(blood_drop)

    def update(self, tics, screen):
        if self.explotion:
            self.blood.update(tics)
            self.blood.draw(screen)

            self.explotion = False
            for blood_drop in self.blood:
                if not blood_drop.is_dead():
                    self.explotion = True
                    break

    def boom(self, pos_xy):
        self.explotion = True
        for blood_drop in self.blood:
            blood_drop.set_position(pos_xy[0], pos_xy[1])
