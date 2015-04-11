import pygame
from pygame.locals import *
from math import exp
import sys
import utils
import music
from config import *

class Menu(object):
    '''A generic menu user interface. Allow both keyboard and mouse selection'''

    def __init__(self, screen, options, title, index=0):
        self.screen = screen
        self.items = [x[0] for x in options]
        self.returns = [x[1] for x in options]
        self.last_index = len(self.items) - 1
        self.index = index
        self.done = False
        self.separator = 2
        font1 = pygame.font.Font(FONT2, 50)
        font2 = pygame.font.Font(FONT2, 45)
        self.hor_step = font2.get_height() + 10
        self.clock = pygame.time.Clock()
        self.selected_imgs = [font2.render(text, True, WHITE) for text in self.items]
        self.selected_imgs2 = [font2.render(text, True, BLUE) for text in self.items]
        self.unselected_imgs = [font2.render(text, True, GREY) for text in self.items]
        self.unselected_imgs2 = [font2.render(text, True, BLUE) for text in self.items]
        self.unselected_rects = None
        self.timeloop = 0
        self.state = 0 
        
        self.background = utils.load_image(MENUBGIMAGE)
        title_img = font1.render(title, True, GREY)
        title_img2 = font1.render(title, True, BLUE)
        topleft = (self.background.get_rect().width - title_img.get_rect().width) / 2, 30
        topleft2 = (self.background.get_rect().width - title_img.get_rect().width) / 2-self.separator, 30-self.separator
        self.background.blit(title_img2, topleft2)
        self.background.blit(title_img, topleft)

        self.draw_end = False
        self._draw_items()

    def loop(self):
        '''Returns the asosiated object for the selected item'''
        pygame.event.clear()
        if not music.is_playing_music():
            music.play_music(MENUMUSIC)
        while (not self.draw_end) and (not self.done): # menu draw the first time

            self.clock.tick(CLOCK_TICS)

            self.screen.blit(self.background, (0,0))

            if pygame.event.peek([KEYDOWN, KEYUP, QUIT]):
                for event in pygame.event.get():
                    self.control(event)

            self._draw_items()
            pygame.display.flip()

            self.timeloop += 1
            if self.timeloop == 50:
                self.state=1
        
        self.draw_end = False
        while not self.done: # menu draw only if some key is pressed

            self.clock.tick(CLOCK_TICS)

            self.screen.blit(self.background, (0,0))

            pygame.event.clear()
            event = pygame.event.wait()
            self.control(event)

            self._draw_items()
            pygame.display.flip()

            self.timeloop += 1
            if self.timeloop == 50:
                self.state=1
        
        return self.returns[self.index]

    def control(self, event):
        if event.type == QUIT:
            sys.exit(0)
        if event.type == KEYDOWN:
            if event.key in (K_SPACE, K_RETURN, K_KP_ENTER):
                music.play_menu2()
                self.select()
            elif event.key == K_UP:
                music.play_menu1()
                if self.index > 0:
                    self.set_index(self.index - 1)
                else:
                    self.set_index(self.last_index)
            elif event.key == K_DOWN:
                music.play_menu1()
                if self.index < self.last_index:
                    self.set_index(self.index + 1)
                else:
                    self.set_index(0)
        if event.type == MOUSEMOTION:
            x,y = pygame.mouse.get_pos()
            for i in range(len(self.unselected_rects)):
                r = self.unselected_rects[i]
                if r.collidepoint(x,y):
                    self.set_index(i)
                    return
        if event.type == MOUSEBUTTONDOWN:
            x,y = pygame.mouse.get_pos()
            for i in range(len(self.unselected_rects)):
                r = self.unselected_rects[i]
                if r.collidepoint(x,y):
                    self.select()
                    return
                
    def set_index(self, index):
        if self.index != index:
            #self.sounds["snd1"].play()
            self.index = index

    def select(self):
        #self.sounds["snd2"].play()
        self.done = True

    def _draw_items(self):
        rects = []
        y = self.hor_step + 50 # Tune this value as you need
        for i in range(len(self.items)):
            if i == self.index:
                img = self.selected_imgs[i]
                img2 = self.selected_imgs2[i]
            else:
                img = self.unselected_imgs[i]
                img2 = self.unselected_imgs2[i]
            
            x2 = self.screen.get_width()/2
            
            if (self.state == 0) and (i%2 == 0):
                x1 = x2 - (600 * (50 - self.timeloop) / 50)
            elif (self.state == 0) and (i%2 == 1): 
                x1 = x2 + (600 * (50 - self.timeloop) / 50)
            else:  
                x1 = x2
                self.draw_end = True
            x = (x1+(x2-x1)*(1-exp(-self.timeloop/20.0)))
            x -= img.get_width() / 2
            self.screen.blit(img2, (x-self.separator,y-self.separator))
            self.screen.blit(img, (x,y))

            if self.unselected_rects is None:
                rects += [img.get_rect().move(x,y)]

            y += self.hor_step

        if self.unselected_rects is None:
            self.unselected_rects = rects
