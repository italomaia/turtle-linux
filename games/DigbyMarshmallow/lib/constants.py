"""Constant definitions.

This file is loaded during the program initialisation before the main module is
imported. Consequently, this file must not import any other modules, or those
modules will be initialised before the main module, which means that the DEBUG
value may not have been set correctly.

"""

#: Enable debug features. Should never be changed manually but is set to True
#: automatically when running `test_game.py`.
DEBUG = False

#: Version number. This may be represented somewhere in-game. It is also read
#: by `setup.py` as part of its versioning features.
VERSION = "1.0"

#: The directory (relative to the top level) wherein all the resources for the
#: game are stored, probably subdivided into types of resources. See `data.py`.
DATA_DIR = "data"

#: The caption that appears at the top of the window. Obviously this is only
#: visible in windowed mode.
CAPTION = "The Space Adventures of Digby Marshmallow, Space Burglar " \
          "Extraordinaire ...In Space"

#: The "top-level" tick rate; the maximum number of times per second that the
#: controller will call its tick method.
TICK_RATE = 60.0

#: The "top-level" update rate; the maximum number of times per second that the
#: controller will call its update method.
UPDATE_RATE = 60.0

## Menu display parameters.
MENU_PADDING = 0.02
MENU_MARGIN = 0.02
MENU_SPACING = 0.02
MENU_FONT_SIZE = 0.05

## Tool display parameters.
TOOL_PADDING = 0.005
TOOL_MARGIN = 0.005
TOOL_OUTLINE_NORMAL = (1.0, 1.0, 1.0, 1.0)
TOOL_OUTLINE_HIGHLIGHT = (0.0, 1.0, 0.0, 1.0)
TOOL_BACKGROUND_NORMAL = (0.0, 0.0, 0.0, 0.8)
TOOL_BACKGROUND_HIGHLIGHT = (0.5, 0.5, 0.5, 0.8)

SCORE_FONT_SIZE = 0.04
SCORE_PADDING = 0.02
#: Floating point epsilon used in equality tests
EPSILON = 10e-6

## Scale factor for world
SCREEN_HEIGHT = 1000

FADE_RATE = 0.05
GAME_FADEIN_RATE = 0.008
GAME_FADEOUT_RATE = 0.05
DEATH_FADEOUT_RATE = 0.005
#: Gameplay stuff
DEFAULT_PIPE_LENGTH = 5000
PLAYER_RADIUS = 50
PLAYER_ROTATION = .3
PLAYER_THRUST = .5
PLAYER_LIFT = 2
ELASTICITY = 0.7
ANGULAR_DRAG = 0.95
SHOT_COOLDOWN = 25
STUN_FRAMES = 15
IMPACT_SPIN = 15
# Graphical effects
SMOKEPUFF_RATE = 3

LEVELICON_SIZE = 0.15
LEVELICON_SPACING = 0.02

LEVELS_PER_ROW = 7
LEVEL_ROWS = 4
