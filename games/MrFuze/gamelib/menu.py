#! /usr/bin/env python

import pygame, sys
from pygame.locals import *

from game import *
from ezmenu import *
from data import *
from cutscenes import *

def RunGame(screen):
    Game(screen)
    play_music("titlescreen.ogg", 0.75)

def ContinueGame(screen):
    Game(screen, True)
    play_music("titlescreen.ogg", 0.75)

def Help(screen):
    cutscene(screen, ["HELP",
    "",
    "Move: Arrow Keys",
    "Jump: Z key",
    "Shoot: X key",
    "",
    "",
    "In each level, a fuse is gradually", 
    "burning on a ubre-bomb. If the fuse",
    "burns out, the bomb will explode, and",
    "you'll lose a life. Your object is",
    "to shoot as many mutants as possible",
    "with your electrocuting string, and",
    "touch the bomb at the end of each level",
    "to de-activate it. Good luck Mr. Fuze!"])

def Credits(screen):
    cutscene(screen, ["CREDITS",
    "",
    "Code, Art, and Sound Effects",
    "PyMike <pymike93@gmail.com>",
    "",
    "Music",
    "http://modarchive.org/"])

class Menu(object):
 
    def __init__(self, screen):
        self.screen = screen
        self.menu = EzMenu(["NEW GAME", lambda: RunGame(screen)], ["CONTINUE", lambda: ContinueGame(screen)], ["HELP", lambda: Help(screen)], ["CREDITS", lambda: Credits(screen)], ["QUIT GAME", sys.exit])
        self.menu.set_highlight_color((255, 0, 0))
        self.menu.set_normal_color((255, 255, 255))
        self.menu.center_at(300, 400)
        self.menu.set_font(pygame.font.Font(filepath("font.ttf"), 16))
        self.bg = load_image("titlescreen.png")
        self.font = pygame.font.Font(filepath("font.ttf"), 16)
        play_music("titlescreen.ogg", 0.75)
        self.clock = pygame.time.Clock()
        events = pygame.event.get()
        self.menu.update(events)
        self.menu.draw(self.screen)
        self.main_loop()
  
    def main_loop(self):
        while 1:
            self.clock.tick(30)
            events = pygame.event.get()
            self.menu.update(events)
            for e in events:
                if e.type == QUIT:
                    pygame.quit()
                    return
                if e.type == KEYDOWN and e.key == K_ESCAPE:
                    pygame.quit()
                    return
        
            self.screen.blit(self.bg, (0, 0))
            ren = self.font.render("COPYRIGHT (C) 2008", 1, (255, 255, 255))
            self.screen.blit(ren, (320-ren.get_width()/2, 310))
       
            self.menu.draw(self.screen)
            pygame.display.flip()
        
        
