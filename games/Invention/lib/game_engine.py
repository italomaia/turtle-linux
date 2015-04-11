# Python imports
import pygame
import data

from constants import Constants

# --- Title Screen imports --- #
from title_screen import TitleScreen

# --- Stage Clear imports --- #
from stage_clear import StageClear

# --- Stage Failure imports --- #
from stage_failure import StageFailure

# --- Escort Engine imports --- #
from escort_engine import EscortEngine

# --- Cutscene imports --- #
from cutscene import Cutscene

class GameEngine:
    """ This is the big-bad overall game engine that controls all of the
        sub-games, minigames, and dialogs. """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
        pygame.display.set_caption("invention")

        self.running = True
        self.game_over = False
        
        self.show_cutscenes = False
        self.current_stage = 0
        
        self.choice = 0
    
    def load_saved(self):
        try:
            save_file = open(data.filepath("escortsave"), "r")
            current_level = (int)(save_file.read())
            save_file.close()
        except:
            current_level = 0
            print "Could not read from save file!"
        # Change this value to default to starting at a different level
        self.current_stage = current_level

    def main(self):
        """ The main sequence of classes to run for the game. """
        result = True
        # Display the title screen
        self.title()
        if self.choice == 0:
            self.current_stage = 0
            self.show_cutscenes = True
        elif self.choice == 1:
            # Continue
            self.load_saved()
            self.show_cutscenes = False
        if self.show_cutscenes:
            for scene in range(7):
                if not self.cutscene(scene): return
        while True:
            # If any of these steps returns False, then break the loop. This
            # allows the escape key/quit button to be used to stop the game.
            if not self.escort_game(): break
            try:
                save_file = open(data.filepath("escortsave"), "w")
                save_file.write(str(self.current_stage))
                save_file.close()
            except:
                print "Could not write to save file!"

    def title(self):
        """ Display the title screen. """
        ts = TitleScreen(self.screen)
        ts.main()
        self.choice = ts.choice
        return ts.running

    def stage_clear(self):
        """ Display the stage clear screen. """
        sc = StageClear(self.screen)
        sc.main()
        return sc.running

    def failed_stage(self):
        """ Display the stage failed screen. """
        sf = StageFailure(self.screen)
        sf.main()
        return sf.running
        
    def cutscene(self, cutscene_number):
        cs = Cutscene(self.screen)
        cs.display(cutscene_number)
        return cs.running

    def escort_game(self):
        """ Display the Escort Engine game. """
        ee = EscortEngine(self.screen)
        self.current_stage += 1
        ee.set_stage(self.current_stage)
        ee.main()
        if ee.state is "victory":
            if self.current_stage == 20:
                self.cutscene(7)
                return False
            else:
                self.stage_clear()
            return True
        elif ee.state is "failure":
            self.failed_stage()
            self.current_stage -= 1
            return True
        elif ee.state is "exit":
            return False
