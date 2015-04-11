# Python imports
import pygame
import data

from constants import Constants

from music_player import MusicPlayer

class StageFailure:
    """ Just a stage clear intermission screen. Nothing at all
        fancy here. """
    def __init__(self, screen = None):
        if screen is None:
            self.screen = pygame.display.set_mode((600, 600))
        else:
            self.screen = screen
        self.running = True
        
        self.explode_anims = []
        for i in range(4):
            self.explode_anims.append(pygame.image.load(data.filepath("explode" + str(i + 1) + ".png")))
            
        self.explode_anims *= 3
        
        self.music_player = MusicPlayer("palnap4.ogg")

    def main(self):
        """ Display the screen. """
        self.music_player.play()
        current_frame = 0
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 24)
        try_again_text = font.render("[ press any key to try again ]", 1, (0, 255, 255))
        failure_text = font.render("You failed!", 1, (0, 255, 255))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    return
                elif event.type == pygame.QUIT:
                    self.running = False
                    return False
            self.screen.fill((0, 0, 20))
            if current_frame < 40: 
                current_frame += 1
                self.screen.blit(self.explode_anims[(current_frame / 5)], (self.screen.get_rect().centerx - 50, self.screen.get_rect().centery - 50))
            else:
                current_frame = 0
            self.screen.blit(failure_text, (self.screen.get_rect().centerx - 50, 100))
            self.screen.blit(try_again_text, (self.screen.get_rect().centerx - 125, self.screen.get_rect().centery + 200))
            pygame.display.flip()
            clock.tick(Constants.MAX_FPS)