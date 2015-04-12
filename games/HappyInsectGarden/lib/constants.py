"""Constant definitions.

This file is loaded during the program initialisation before the main module is
imported. Consequently, this file must not import any other modules, or those
modules will be initialised before the main module, which means that the DEBUG
value may not have been set correctly.

This module is intended to be imported with 'from ... import *' semantics but
it does not provide an __all__ specification.

"""
import sys

#: Enable debug features. Should never be changed manually but is set to True
#: automatically when running `test_game.py`.
DEBUG = False

#: Version string. This may be represented somewhere in-game. It is also read
#: by `setup.py` as part of its versioning features.
VERSION = u"1.0"

#: The directory (relative to the top level) wherein all the resources for the
#: game are stored, probably subdivided into types of resources. See `data.py`.
DATA_DIR = "data"

#: The name of the persistent config file written and read by the config
#: module. See `config.py`.
CONFIG_FILE = "local.py"

#: The caption that appears at the top of the window. Obviously this is only
#: visible in windowed mode.
CAPTION = u"Happy Insect Garden"

#: The "top-level" tick rate; the maximum number of times per second that the
#: controller will call its tick method.
TICK_RATE = 60.0

#: The "top-level" update rate; the maximum number of times per second that the
#: controller will call its update method.
UPDATE_RATE = 60.0

#: Font name (for some reason this needs customising for MacOS).
FONT_NAME = "Fontin" if sys.platform != "darwin" else "Fontin Regular"

#: The width and height of the game world in world units.
WORLD_WIDTH = 1200
WORLD_HEIGHT = 900

#: Different musics.
MENU_MUSIC = "English Country Garden.mp3"
GAMEOVER_MUSIC = "Greensleeves.mp3"
VICTORY_MUSIC = "Hesleyside Reel.mp3"
GAME_MUSICS = ["All Things Bright And Beautiful.mp3",
               "Little Brown Jug.mp3",
               "The British Grenadiers.mp3",
               "Where The Bee Sucks.mp3"]

ACHIEVEMENT_FILE = "achievements.data"

# now useful stuff
SPATIAL_INDEX_RESOLUTION = 160
PLANT_INDEX_RESOLUTION = 40

HIGH_LIKELIHOOD_TARGET_CHANGE = 0.1
LOW_LIKELIHOOD_TARGET_CHANGE = 0.01
