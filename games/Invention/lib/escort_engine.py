# Python imports
import pygame
import data

# Game-related imports
from constants import Constants
from girl import Girl
from wrench_block import WrenchBlock
from gobject_group import GobjectGroup
from music_player import MusicPlayer
from sound_player import SoundPlayer

class EscortEngine:
    """ This is the main engine to be used in the game. This is the
        Lemmings-esque escort engine. Call set_stage(#) before calling main(). """
    def __init__(self, screen=None):
        # See if we've been given a screen to use
        if screen is None:
            self.screen = pygame.display.set_mode((600, 600))
        else:
            self.screen = screen

        self.running = True
        self.clock = pygame.time.Clock()

        # Gots to have us a background and a walkable mask
        self.background = None
        self.mask = None

        # If anyone takes screenshots, they can do so with this!
        self.screenshot_counter = 0

        # Initialize our reusable robotic girl
        self.girl = Girl()

        # What is the current state of our game
        self.state = "Running"
        
        # Load our music player
        self.music_player = MusicPlayer()
        self.sound_player = SoundPlayer()
        self.girl.sound_player = self.sound_player

    def set_stage(self, stage_number):
        """ Set the current stage to the specified number and load the
            appropriate images. In addition, set the starting information
            for the player. Then, set the mask/image to the proper images
            and blit the background to the screen. """
        if stage_number == 1:
            self.background = pygame.image.load(data.filepath("stage8.png"))
            self.original_mask = pygame.image.load(data.filepath("stage8_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 150)
            
            self.music_player.load("alma_mater.ogg")
        elif stage_number == 2:
            self.background = pygame.image.load(data.filepath("stage1.png"))
            self.original_mask = pygame.image.load(data.filepath("stage1_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 525)
            
            self.music_player.load("alma_mater.ogg")
        elif stage_number == 3:
            self.background = pygame.image.load(data.filepath("stage5.png"))
            self.original_mask = pygame.image.load(data.filepath("stage5_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 500)
            
            self.music_player.load("alma_mater.ogg")
        elif stage_number == 4:
            self.background = pygame.image.load(data.filepath("stage4.png"))
            self.original_mask = pygame.image.load(data.filepath("stage4_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 100)
            
            self.music_player.load("alma_mater.ogg")
        elif stage_number == 5:
            self.background = pygame.image.load(data.filepath("stage2.png"))
            self.original_mask = pygame.image.load(data.filepath("stage2_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (25, 100)
            
            self.music_player.load("alma_mater.ogg")
        elif stage_number == 6:
            self.background = pygame.image.load(data.filepath("stage10.png"))
            self.original_mask = pygame.image.load(data.filepath("stage10_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 75)
            
            self.music_player.load("jam_box_public.ogg")
        elif stage_number == 7:
            self.background = pygame.image.load(data.filepath("stage3.png"))
            self.original_mask = pygame.image.load(data.filepath("stage3_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 100)
            
            self.music_player.load("jam_box_public.ogg")
        elif stage_number == 8:
            self.background = pygame.image.load(data.filepath("stage13.png"))
            self.original_mask = pygame.image.load(data.filepath("stage13_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 135)
            
            self.music_player.load("jam_box_public.ogg")
        elif stage_number == 9:
            self.background = pygame.image.load(data.filepath("stage6.png"))
            self.original_mask = pygame.image.load(data.filepath("stage6_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 225)
            
            self.music_player.load("jam_box_public.ogg")
        elif stage_number == 10:
            self.background = pygame.image.load(data.filepath("stage7.png"))
            self.original_mask = pygame.image.load(data.filepath("stage7_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 300)
            self.girl.modifier = Constants.ANTIGRAVITY
            self.girl.image = pygame.transform.flip(self.girl.image, False, True)
            
            self.music_player.load("jam_box_public.ogg")
        elif stage_number == 11:
            self.background = pygame.image.load(data.filepath("stage14.png"))
            self.original_mask = pygame.image.load(data.filepath("stage14_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 135)
            self.girl.modifier = Constants.ANTIGRAVITY
            self.girl.image = pygame.transform.flip(self.girl.image, False, True)
            
            self.music_player.load("rejects.ogg")
        elif stage_number == 12:
            self.background = pygame.image.load(data.filepath("stage9.png"))
            self.original_mask = pygame.image.load(data.filepath("stage9_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 450)
            
            self.music_player.load("rejects.ogg")
        elif stage_number == 13:
            self.background = pygame.image.load(data.filepath("stage12.png"))
            self.original_mask = pygame.image.load(data.filepath("stage12_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 475)
            
            self.music_player.load("rejects.ogg")
        elif stage_number == 14:
            self.background = pygame.image.load(data.filepath("stage11.png"))
            self.original_mask = pygame.image.load(data.filepath("stage11_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 75)
            
            self.music_player.load("rejects.ogg")
        elif stage_number == 15:
            self.background = pygame.image.load(data.filepath("stage15.png"))
            self.original_mask = pygame.image.load(data.filepath("stage15_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (305, 311)
            
            self.music_player.load("rejects.ogg")
        elif stage_number == 16:
            self.background = pygame.image.load(data.filepath("stage16.png"))
            self.original_mask = pygame.image.load(data.filepath("stage16_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 475)
            
            self.music_player.load("manna_and_me.ogg")
        elif stage_number == 17:
            self.background = pygame.image.load(data.filepath("stage17.png"))
            self.original_mask = pygame.image.load(data.filepath("stage17_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 125)
            
            self.music_player.load("manna_and_me.ogg")
        elif stage_number == 18:
            self.background = pygame.image.load(data.filepath("stage18.png"))
            self.original_mask = pygame.image.load(data.filepath("stage18_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 140)
            self.girl.modifier = Constants.ANTIGRAVITY
            self.girl.image = pygame.transform.flip(self.girl.image, False, True)
            
            self.music_player.load("manna_and_me.ogg")
        elif stage_number == 19:
            self.background = pygame.image.load(data.filepath("stage19.png"))
            self.original_mask = pygame.image.load(data.filepath("stage19_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (0, 410)
            
            self.music_player.load("manna_and_me.ogg")
        elif stage_number == 20:
            self.background = pygame.image.load(data.filepath("stage20.png"))
            self.original_mask = pygame.image.load(data.filepath("stage20_mask.png"))
            self.girl.direction = 0
            self.girl.rect.topleft = (75, 110)
            
            self.music_player.load("manna_and_me.ogg")
        # All of that is done; now set up the initial environment to have the
        # player wander around in.
        self.mask = pygame.surface.Surface(self.original_mask.get_rect().size)
        self.mask.blit(self.original_mask, (0, 0))
        self.screen.blit(self.background, (0, 0))

    def grab_screenshot(self):
        """ Take a screenshot of the current screen. """
        pygame.image.save(self.screen, "screenshot" + str(self.screenshot_counter) + ".bmp")
        self.screenshot_counter += 1

    def main(self):
        """ The main game loop. Be sure to call set_stage(#) first! """
        # Initialize our player sprite group
        player_group = pygame.sprite.RenderPlain(self.girl)

        # Initialize all of our "wrenches", or in-game draggable objects
        wrenches = []
        wrench_group = GobjectGroup()
        for i in range(Constants.START_BLOCKS):
            wrenches.append(WrenchBlock())
            wrench_group.add(wrenches[i])
            
        self.music_player.play()

        # Game loop!
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.grab_screenshot()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "exit"
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        wrench_group.handle_click(True)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        wrench_group.handle_click(False)
                elif event.type == pygame.QUIT:
                    self.running = False

            # Clear all of the drawn sprites
            player_group.clear(self.screen, self.background)
            wrench_group.clear(self.screen, self.background)

            # This special little bit right here is for handling masks with the
            # draggable objects.
            wrench_group.clear(self.mask, self.original_mask)
            wrench_group.update()
            wrench_group.draw_to_mask(self.mask)

            # Update the player
            player_group.update(self.mask)

            # Draw the player and the wrenches to the screen
            player_group.draw(self.screen)
            wrench_group.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(Constants.MAX_FPS)

            # If we've hit a condition to end the game, do so.
            if self.girl.done:
                self.girl.done = False
                self.state = "victory"
                self.running = False
            elif not self.girl.living:
                self.girl.living = True
                self.state = "failure"
                self.running = False

        self.music_player.stop()
