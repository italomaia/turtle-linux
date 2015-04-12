"""Main starter module.

The DEBUG constant can be safely assumed set by the time this module is
imported.

"""

import sys
import os

import config
from common import *
from constants import *


## Command line parsing
#######################

SCRIPT_NAME = os.path.basename(os.path.join(".", sys.argv[0]))
SCRIPT_DIR = os.path.dirname(os.path.join(".", sys.argv[0]))

USAGE_MESSAGE = """\
usage: %s [OPTIONS]...
Mandatory arguments for long options are required for short options too.

  -h, --help                    print this usage message
  -v, --version                 print version information
""" % SCRIPT_NAME

if DEBUG: USAGE_MESSAGE += """\
  -p, --profile                 run in the profiler
  -l, --level=NAME              test the named level
"""

def usage(exit_code):
    """Print the usage message and exit with the supplied status.

    :Parameters:
        `exit_code` : int
            The status code with which to exit.

    """
    print USAGE_MESSAGE
    sys.exit(exit_code)

def version():
    """Print version information and exit successfully.

    """
    print VERSION
    sys.exit()

def parse_args():
    """Parse command line arguments.

    For details of what the options do see USAGE_MESSAGE.

    """
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvpl", ["help", "version",
                                   "profile", "level"])
    except getopt.GetoptError, exc:
        usage(2)

    if len(args) > 0:
        usage(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(0)
        elif opt in ("-v", "--version"):
            version()
        elif DEBUG and opt in ("-p", "--profile"):
            config.profile = True
        elif DEBUG and opt in ("-l", "--level"):
            config.start_mode = "game"
            config.start_level = arg
        else:
            usage(2)

parse_args()


## Controller
#############
import pyglet
pyglet.options['debug_gl'] = False
from pyglet import window
from pyglet import media
from pyglet import clock
from pyglet import event
from pyglet import app
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *

import music
import style
import game
import cutscene
import mode
import menu
import editor
import squirtle
import gamestate
import data

class Controller(object):
    """Top level controller object.

    An instance of this represents an instance of the game. There is a brief
    chain of function calls, which ends with the `run` method here and then
    `app.run` from Pyglet, which is the way the game is started.

    Modes and handlers are the abstraction of interface. A mode is a class and
    a handler is an instance of a mode. Modes are described in the `mode`
    module.

    """

    def __init__(self):
        self._handler = None
        self.suspended = {}
        try:
            profile = data.load_profile('main.profile')
        except IOError:
            profile = None
        self.gamestate = gamestate.GameState(profile)
        self.keys = key.KeyStateHandler()
        self.music = music.MusicManager()

    def get_handler(self):
        try:
            return self._handler
        except AttributeError:
            return

    def set_handler(self, handler):
        if isinstance(handler, tuple):
            name, args, kwds = handler
            handler = mode.get_handler(name, *args, **kwds)
        if self._handler is not None:
            self._handler.disconnect()
            self.window.remove_handlers(self.keys)
            self.window.remove_handlers(self._handler)
            self._handler = None
        if handler is not None:
            self._handler = handler
            self.window.push_handlers(handler)
            self.window.push_handlers(self.keys)
            handler.connect(self)

    handler = property(get_handler, set_handler)
    del get_handler, set_handler

    def switch_handler(self, name, *args, **kwds):
        """Connect a new handler.

        Additional arguments are passed to the mode constructer.

        :Parameters:
            `name` : str
                The name of the mode class to use.
            `suspend` : bool
                Default False. If True, the current mode is suspended rather
                than dropped.

        """
        suspend = kwds.pop("suspend", False)
        if suspend:
            self.suspend_handler()
        self.handler = (name, args, kwds)

    def resume_handler(self, name, suspend=True):
        """Resume an old handler.

        Only one mode handler for each mode is stored. If another handler for
        the same mode is suspended then only the newer one can be resumed.

        :Parameters:
            `name` : str
                The name of the mode class to resume.
            `suspend` : bool
                Default False. If True, the current mode is suspended rather
                than dropped.

        """
        handler = self.suspended.pop(name)
        if suspend:
            self.suspend_handler()
        self.handler = handler
        self.handler = self.suspended.pop(mode)

    def clear_handler(self):
        """Clear the current handler, if any.

        """
        if self.handler is not None:
            self.handler = None

    def suspend_handler(self):
        """Suspend the current handler, if any.

        """
        if self.handler is not None:
            self.suspended[type(self.handler).name] = self.handler
            self.handler = None

    def tick(self, dt):
        """Update the game logic.

        """
        if self.handler is not None:
            self.handler.tick()

    def update(self, dt):
        """Maintain parallel features.

        :Parameters:
            `dt` : float
                The actual time since the last update was called.

        """
        self.music.update(dt)
        if self.handler is not None:
            self.handler.update(dt)

    def setup_gl(self):
        """Configure GL properties.

        """
        self.window.switch_to()
        squirtle.setup_gl()
        glClearColor(0.0, 0.0, 0.0, 1.0)
        self.window.clear()
        self.window.flip()

    def setup_pyglet(self):
        """Configure Pyglet attributes.

        """
        self.window = window.Window(visible=False, caption=CAPTION,
                                    fullscreen=config.fullscreen)
        clock.schedule_interval_soft(self.tick, 1.0 / TICK_RATE)
        clock.schedule_interval_soft(self.update, 1.0 / UPDATE_RATE)

    def run(self):
        """Start the game.

        """
        self.setup_pyglet()
        self.setup_gl()
        self.switch_handler(config.start_mode)
        self.window.set_visible()
        app.run()


## Main function
################

def main():
    """Start the game.

    """
    if config.profile:
        import datetime, cProfile
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(SCRIPT_DIR, "profile-%s.log" % timestamp)
        cProfile.runctx("Controller().run()", globals(), None, filename)
    else:
        Controller().run()
