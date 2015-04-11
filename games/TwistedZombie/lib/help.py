'''score releted stuff'''

import math
import pygame
from pygame.locals import *

from config import *
import utils
import music

class Help(object):

    def __init__(self, screen, father=None):
        self.screen = screen
        self.father = father
        pass
        
    def loop(self):
        return self.father


