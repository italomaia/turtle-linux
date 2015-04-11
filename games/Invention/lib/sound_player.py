import pygame
import data
import os

class SoundPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.swoosh = pygame.mixer.Sound(data.filepath(os.path.join("sounds", "swoosh.ogg")))
        self.fire = pygame.mixer.Sound(data.filepath(os.path.join("sounds", "fire.ogg")))
        self.thud = pygame.mixer.Sound(data.filepath(os.path.join("sounds", "thud.ogg")))
        
    def play_swoosh(self):
        self.swoosh.play()
        
    def play_fire(self):
        self.fire.play()
        
    def play_thud(self):
        self.thud.play()
        
        