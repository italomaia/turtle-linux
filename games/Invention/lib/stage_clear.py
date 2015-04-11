# Python imports
import pygame
import data

class StageClear:
    """ Just a stage clear intermission screen. Nothing at all
        fancy here. """
    def __init__(self, screen = None):
        if screen is None:
            self.screen = pygame.display.set_mode((600, 600))
        else:
            self.screen = screen
        self.running = True

    def main(self):
        """ Display the screen. """
        stage_clear_graphic = pygame.image.load(data.filepath("stage_clear.png"))
        next_stage = False
        self.screen.blit(stage_clear_graphic, (0, 0))
        pygame.display.flip()
        while not next_stage:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    next_stage = True
                elif event.type == pygame.QUIT:
                    self.running = False
                    return False
            pygame.time.delay(60)
