'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import pygame, os
from pygame.locals import *

import menu, data
try:
    import psyco
    psyco.full()
except:
    print "No psyco for you, you psyco!"

def main():
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    #pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    pygame.mouse.set_visible(0)
    pygame.display.set_icon(pygame.image.load(data.filepath("icon.gif")))
    pygame.display.set_caption("Mr. Fuze - PyMike's Entry for PyWeek #7")
    screen = pygame.display.set_mode((640, 480))
    menu.Menu(screen)
