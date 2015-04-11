# Python imports
import pygame
import data
import random

# Game-related imports
from constants import Constants
from game_object import GameObject

class WrenchBlock(GameObject):
    """ This is our main player object, which inherits from the
        generic GameObject class. """
    def __init__(self):
        GameObject.__init__(self)
        self.load_anims("part", 11)
        # Load a random part and place it randomly on the conveyor belt.
        self.reset()
        self.rect.left = random.randint(0, 536)
        
        self.moved_once = False
        
    def reset(self):
        if random.randint(0, 8) == 8:
            new_number = random.randint(6, 10)
            self.rect.top = 0
        else:
            new_number = random.randint(0, 5)
            self.rect.top = 20
        self.image = self.animations[new_number]
        self.rect.size = self.image.get_rect().size
        self.moved_once = False

    def update(self):
        """ Update the animations/position of the wrench block object. """
        if self.rect.top <= 50:
            # We're moving on the conveyor belt. Whee!
            self.rect.left += 1
            if self.rect.left >= 600:
                # Reset my position.
                self.reset()
                self.rect.left = 0
        if self.clicked:
            # Move to where the mouse is to simulate being dragged.
            self.rect.center = pygame.mouse.get_pos()
            self.moved_once = True
