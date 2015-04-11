#Utilities functions and classes

import pygame
from pygame.locals import *
import os

def load_image(fullname, colorkey=None):

    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            #colorkey = image.get_at((0,0))
            colorkey = (255, 255, 255)
        image.set_colorkey(colorkey, RLEACCEL)
    return image

class NoneSound(object):
    def play(self): pass


class DataBag(object):
    pass


def load_sound(fullname):

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()

    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

def create_surface(size, color, alpha=None):
    s = pygame.Surface(size)
    s.fill(color)
    s.set_alpha(alpha)

    return s
