import pygame
import data
import os

class MusicPlayer:
    def __init__(self, filename=None):
        pygame.mixer.init()
        if filename is not None:
            pygame.mixer.music.load(data.filepath(os.path.join("music", filename)))
        
    def load(self, filename):
        pygame.mixer.music.load(data.filepath(os.path.join("music", filename)))
        
    def play(self):
        pygame.mixer.music.play(-1)
    
    def stop(self):
        pygame.mixer.music.stop()