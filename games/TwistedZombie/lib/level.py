import pygame
from pygame.locals import *
import sys
import random

from sprites import *
import music
import utils
from hero import Hero
from moldsmanager import MoldsManager
from bottlemanager import BottleManager
from config import  *
from explotion import Explotion
from wheather import Wheather
from visual import Visual
from menu import Menu
from scores import HighScores

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

# bottle_density (azul, verde, naranja, roja_destroy)

levels = {1: dict(energy_leap=0.057, mold_density=70, mold_velocity=19,
                  max_time=20, img=LEVEL1, bottle_density=(500,300,4000,1),
                  background=BGLEVEL1),
          2: dict(energy_leap=0.061, mold_density=76, mold_velocity=15,
                  max_time=25, img=LEVEL2, bottle_density=(500,250,4000,3),
                  background=BGLEVEL2),
          3: dict(energy_leap=0.066, mold_density=72, mold_velocity=11,
                  max_time=25, img=LEVEL3, bottle_density=(500,200,4000,4),
                  background=BGLEVEL3),
          4: dict(energy_leap=0.068, mold_density=67, mold_velocity=9,
                  max_time=30, img=LEVEL4, bottle_density=(500,150,4000,5),
                  background=BGLEVEL4),
          5: dict(energy_leap=0.069, mold_density=63, mold_velocity=6,
                  max_time=35, img=LEVEL5, bottle_density=(500,100,4000,7),
                  background=BGLEVEL5)}

LEVELS = 5

class Level(object):
    '''TwistedMold level'''

    def __init__(self, screen, father, level, total_points):

        self.screen = screen
        self.father = father
        self.level = level
        self.background = utils.load_image(levels[level]['background'])
      
        #parameters
        self.energy_leap = levels[level]['energy_leap']
        self.mold_density = levels[level]['mold_density']
        self.mold_velocity = levels[level]['mold_velocity']
        self.max_time = levels[level]['max_time']
        #menu control
        self.options = [("Yes", self.father),("No", None)]
        self.exit = False
    
        #Create the game clock
        self.clock = pygame.time.Clock()

        self.mm = MoldsManager(self.mold_density, self.mold_velocity)
        self.bm = BottleManager(*levels[self.level]['bottle_density'])
        self.bm.mm = self.mm

        self.total_points = total_points
        
        self.pointsCounter = Points(self.total_points)
        self.levelIndicator = LevelIndicator(self.level)
        self.mm.level = self
        self.tics = 0

        self.snow_slim = pygame.sprite.Group()
        self.snow_fat = pygame.sprite.Group()        

        for x in range(75):
            sprite = Wheather(1,2)
            self.snow_slim.add(sprite)

        for x in range(75):
            sprite = Wheather(3,5)
            self.snow_fat.add(sprite)
    
        self.energy_bar = EnergyBar(self.energy_leap)
        self.bm.energy_bar = self.energy_bar
        self.mm.energy_bar = self.energy_bar

        self.level_time = LevelTime(self.max_time)

        self.gadgets = pygame.sprite.RenderUpdates()
        self.gadgets.add(self.pointsCounter)
        self.gadgets.add(self.energy_bar)
        self.gadgets.add(self.level_time)
        self.gadgets.add(self.levelIndicator)

        self.hero = Hero()
        self.bm.hero=self.hero
        self.mm.hero=self.hero

        self.explotion = Explotion()

        self.control_down = -1
        self.control_up = -1
        self.control_left = -1
        self.control_right = -1
        self.control_tiempo = 5

        self.next_scream = random.randrange(400,500)

        #Show level image
        Visual(self.screen, [utils.load_image(levels[self.level]['img'])], [2], None).loop()

    def loop(self):  
        music.play_music(PLAYMUSIC)
        while not self.finish():
            self.tics += 1  

            if not self.next_scream:
                music.play_random_scream()            
                self.next_scream = random.randrange(400,500)
            else:
                self.next_scream -= 1               
   
            self.screen.blit(self.background, (-(self.tics % 700),0)) 
            self.update()
            self.draw()

            #Control
            for event in pygame.event.get():
                self.control(event)

            self.clock.tick(CLOCK_TICS)

            if self.control_down == 0: self.hero.down()
            if self.control_up == 0: self.hero.up()
            if self.control_right == 0: self.hero.right()
            if self.control_left == 0: self.hero.left()

            if self.control_down >= 0:
                self.control_down += 1
                if self.control_down >= self.control_tiempo:
                    self.control_down = 0
                    
            if self.control_up >= 0:
                self.control_up += 1
                if self.control_up >= self.control_tiempo:
                    self.control_up = 0

            if self.control_right >= 0:
                self.control_right += 1
                if self.control_right >= self.control_tiempo:
                    self.control_right = 0

            if self.control_left >= 0:
                self.control_left += 1
                if self.control_left >= self.control_tiempo:
                    self.control_left = 0

            self.clock.tick(CLOCK_TICS)

            pygame.display.flip()
    
        if self.exit:
            return self.father
        elif not self.level_time.seconds:                   
            #music.stop_music()

            if self.level < LEVELS:
                def f(screen):
                    return Level(screen, self.father, self.level + 1, self.total_points)
                return f
            else:
                
                def f(screen):
                    def g(screen):
                        return HighScores(self.screen, self.father, self.total_points)
                    music.play_music(WINMUSIC)
                    return Visual(screen,utils.load_image(WIN),-1,g)
                return f

        elif self.energy_bar.energy_percent <= 0:
            def f(screen):
                def g(screen):
                    return HighScores(self.screen, self.father, self.total_points) 
                music.play_gameover()
                return Visual(screen, [utils.load_image(GAMEOVER)], [3], g)               

            return f

    def update(self):
        if self.level in(4,5):
            self.snow_slim.update()               

        self.energy_bar.update(self.tics)
        self.level_time.update(self.tics)

        self.bm.update()        

        self.mm.gen(self.tics)
        self.mm.move(self.tics)

        if self.level in(4,5):
            self.snow_fat.update() 

        #Blood Explotion
        self.explotion.update(self.tics, self.screen)
 
        #Verify collision
        if self.mm.is_fitting(self.hero, self.tics):
            self.explotion.boom(self.hero.get_center())
            self.total_points += 1

        self.pointsCounter.update(self.total_points)  
        self.levelIndicator.update(self.level)          
            
    
    def draw(self):
        self.snow_slim.draw(self.screen)
        
        self.bm.draw(self.screen)
        self.mm.draw(self.screen)
        
        self.hero.draw(self.screen)
        self.snow_fat.draw(self.screen)    
        self.gadgets.draw(self.screen)

    def control(self, event):
        
        if event.type == QUIT:
            sys.exit(0)

        if event.type == KEYDOWN:
            if event.key == K_DOWN:
                self.control_down = 0
            if event.key == K_UP:
                self.control_up = 0
            if event.key == K_RIGHT:
                self.control_right = 0
            if event.key == K_LEFT:
                self.control_left = 0
            if event.key in(K_SPACE, K_s):
                self.hero.twist_right()
                music.play_scream()
            if event.key == K_a:
                self.hero.twist_left()
                music.play_scream()

            if event.key == K_ESCAPE:
                pygame.mixer.music.set_volume(0.5)
                mem = Menu(self.screen, self.options, "Do you want to quit?").loop()
                pygame.mixer.music.set_volume(1.0)

                if mem == self.father:
                    music.stop_music()
                    self.exit = True

        if event.type == KEYUP:
            if event.key == K_DOWN:
                self.control_down = -1
            if event.key == K_UP:
                self.control_up = -1
            if event.key == K_RIGHT:
                self.control_right = -1
            if event.key == K_LEFT:
                self.control_left = -1

    def finish(self):
        if self.level_time.seconds == 0 or self.energy_bar.energy_percent <= 0 or self.exit:
            return True

        return False


def main():
    Level().loop()

if __name__ == "__main__":
    main()
