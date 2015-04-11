import pygame
import random
import utils
from config import *
from mold import Mold
import music
import math

class MoldsManager(object):

    def __init__(self, mold_density, mold_velocity):
        self.molds = []
        self.mold_density = mold_density
        self.mold_velocity = mold_velocity
        self.destroy_all_flag = False
        self.destroy_all_finish = 0

        self.tops = []
        for y in range(LEVEL_TOP, LEVEL_TOP+LEVEL_HEIGHT-4, 4):
            self.tops.append(y)

    def move(self, times):

        if self.destroy_all_finish == 40:
            self.destroy_all_flag = False
            self.destroy_all_finish = 0

        if self.destroy_all_flag:
            self.expansion_radius = self.destroy_all_finish*15+20
            y,x = self.destroy_all_center
            temp = []
            for m in self.molds:
                xp,yp = m.get_center()
                distance = math.sqrt(math.pow(xp - x, 2) + \
                                     math.pow(yp - y, 2))
                if distance < self.expansion_radius:
                    temp.append(m)
                    break

            for t in temp:
                #self.level.pos_points += 1
                self.molds.remove(t)
                del t
        
        if times % self.mold_velocity != 0: return
    
        for m in self.molds:
            m.move()
            # Delete old mold
            if m.x+BODY_WIDTH < 0:
                self.molds.remove(m)
                del m

    def draw(self, screen):
        if self.destroy_all_flag:
            self.destroy_all_finish += 1
            x,y = self.destroy_all_center
            circle = pygame.draw.circle(screen, (240,251,227),(y,x),self.expansion_radius, 20)

        for m in self.molds:
            m.draw(screen)

    def destroy_all(self, destroy_all_center):
        self.destroy_all_flag = True
        self.destroy_all_center = destroy_all_center

    def gen(self, times):

        if random.randrange(self.mold_density) != 0: return

        # Create the new mold
        top = random.choice(self.tops)
        mold = Mold(LEVEL_WIDTH, top, random.randrange(0, 6))

        # Avoid molds overlaping
        for m in self.molds:
            if mold.is_collision(m):
                del mold
                return

        self._add(mold)

    def _add(self, m):
        self.molds.append(m)

    def _remove(self, m):
        self.molds.remove(m)

    def is_fitting(self, hero, times):
        '''Ask if the hero fit any mold and remove the fitted mold.'''
        for m in self.molds:
            if hero.is_fitting(m):
                self.molds.remove(m)
                del m
                music.play_bloop()
                self.level.energy_bar.add_energy(3)
                return True
            
        return False

