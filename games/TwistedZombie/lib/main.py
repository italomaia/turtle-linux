import sys
import pygame
from pygame.locals import *
import utils
import music
from config import  *
from level import Level
from menu import Menu
from scores import HighScores
from visual import Visual

from help import Help

from credits import Credits


if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

def main():
    #Initialize 
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    icon = utils.load_image(ICON, (0,0,0))
    pygame.display.set_icon(icon)

    #Introduction
    images = [utils.load_image(image) for image in INTRO_IMAGES]
    visual = Visual(screen, images, INTRO_TIMES)
    music.play_music(INTROMUSIC, 1)
    visual.loop()
    music.stop_music()
    
    #Shooter opcion
    opcion = menu
    while opcion is not exit:
        change = opcion(screen).loop()
        if change:
            opcion = change
    opcion()        #Exit

def menu(screen):
    options = [("Play", play), ("Story", story), ("Help", help), \
               ("High Scores", scores), ("Credits", credits), ("Exit",  exit)]
    return Menu(screen, options, WINDOW_TITLE)

def play(screen):
    return Level(screen, menu, 1, 0)

def scores(screen):
    return HighScores(screen,menu)

def help(screen):
    bg = utils.load_image(HELPBG)    
    text = utils.load_image(HELP, (0,0,0))
    bg.blit(text, (0,0))
    return Visual(screen, bg, -1, menu)

def credits(screen):
    return Credits(screen,menu)

def story(screen):
    bg = utils.load_image(STORYBG)
    text = utils.load_image(STORY, (0,0,0))
    bg.blit(text, (0,0))
    return Visual(screen, bg, -1, menu)

def exit():
    sys.exit(0)

if __name__ == "__main__":
    main()
