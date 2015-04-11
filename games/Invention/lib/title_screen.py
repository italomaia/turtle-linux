# Python imports
import pygame
import data

# Game-related imports
from music_player import MusicPlayer

class TitleScreen:
    """ Just a stage clear intermission screen. Nothing at all
        fancy here. """
    def __init__(self, screen = None):
        if screen is None:
            self.screen = pygame.display.set_mode((600, 600))
        else:
            self.screen = screen
        self.running = True
        
        self.music_player = MusicPlayer("palnap4.ogg")
        
        self.clock = pygame.time.Clock()
        
        self.choice = 0

    def main(self):
        """ Display the screen and a little bit of text at the bottom
            of the screen. """
        self.music_player.play()
        xasm_logo = pygame.image.load(data.filepath("xasm.png"))
        title_screen = pygame.image.load(data.filepath("title.png"))
        font = pygame.font.Font(None, 24)
        start_game = False
        alpha = 0
        fade_in = True
        
        logo_alpha = 0
        
        skip = False
        
        while logo_alpha < 255 and not skip:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    skip = True
                elif event.type == pygame.QUIT:
                    self.running = False
                    return
            self.screen.fill((0, 0, 0))
            xasm_logo.set_alpha(logo_alpha)
            self.screen.blit(xasm_logo, (0, 0))
            logo_alpha += 3
            pygame.display.flip()
            self.clock.tick(30)
        
        while logo_alpha > 0 and not skip:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    skip = True
                elif event.type == pygame.QUIT:
                    self.running = False
                    return
            self.screen.fill((0, 0, 0))
            xasm_logo.set_alpha(logo_alpha)
            self.screen.blit(xasm_logo, (0, 0))
            logo_alpha -= 3
            pygame.display.flip()
            self.clock.tick(30)
        
        skip = False
        counter = 50
        while counter > 0 and not skip:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    skip = True
                elif event.type == pygame.QUIT:
                    self.running = False
                    return
            self.screen.fill((0, 0, 0))
            text = font.render("Dedicated to the memory of Phoebe...", 1, (255, 255, 255))
            text2 = font.render("We'll miss you...", 1, (255, 255, 255))
            self.screen.blit(text, (150, 300))
            self.screen.blit(text2, (225, 325))
            pygame.display.flip()
            self.clock.tick(30)
            counter -= 1
            
        choice = 0
        
        while not start_game:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.choice -= 1
                    elif event.key == pygame.K_DOWN:
                        self.choice += 1
                    elif event.key == pygame.K_RETURN:
                        start_game = True
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        return
                elif event.type == pygame.QUIT:
                    self.running = False
                    return
            if self.choice < 0:
                self.choice = 1
            elif self.choice > 1:
                self.choice = 0
            new_game = "[ new game ]"
            continue_game = "[ continue game ]"
            if self.choice == 0:
                new_game = "> " + new_game
            elif self.choice == 1:
                continue_game = "> " + continue_game
            # There's some weird-ass PyGame font bug in 1.7, so the text is
            # ant-aliased.
            text = font.render(new_game, 1, (5, 231, 96))
            text2 = font.render(continue_game, 1, (5, 231, 96))
            self.screen.blit(title_screen, (0, 0))
            self.screen.blit(text, (200, 525))
            self.screen.blit(text2, (200, 550))
            pygame.display.flip()
            self.clock.tick(30)
        self.music_player.stop()
