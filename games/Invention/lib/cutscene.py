import pygame
import data

from constants import Constants
from music_player import MusicPlayer

class Cutscene:
    def __init__(self, screen=None):
        self.cutscenes = []
        for i in range(8):
            self.cutscenes.append(pygame.image.load(data.filepath("scene" + str(i + 1) + ".png")))
        if screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
        else:
            self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.font = pygame.font.Font(None, 24)
        
        self.music_player = MusicPlayer("palnap4.ogg")
            
    def display(self, number):
        self.music_player.play()
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    return
                elif event.type == pygame.QUIT:
                    self.running = False
                    return
            self.screen.blit(self.cutscenes[number], (0, 0))
            pygame.display.flip()
            self.clock.tick(30)
        self.music_player.stop()