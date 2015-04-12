"""Interface object framework.

"""

import config
from common import *
from constants import *


mode_directory = {}

def get_handler(name, *args, **kwds):
    """Return a handler for the given mode name or None.

    Additional arguments are passed to the mode constructer.

    :Parameters:
        `name` : str
            The mode name to look for.

    """
    mode = mode_directory.get(name)
    if mode is not None:
        return mode(*args, **kwds)


class ModeMeta(type):
    """Metaclass for interface objects.

    Updates the mode directory when a new mode is created.

    """

    def __init__(self, *args, **kwds):
        super(ModeMeta, self).__init__(*args, **kwds)
        if self.name is None and None in mode_directory:
            raise AssertionError("must override mode name in subclasses")
        elif self.name in mode_directory:
            raise AssertionError("mode already exists with name %r" % self.name)
        mode_directory[self.name] = self


class Mode(object):
    """Baseclass for interface objects.

    Modes have an update method that is called every tick and define event
    handlers for the window and controller. Handlers (instances of a mode) are
    automatically pushed onto the window and controller event stacks when they
    are switched to, if they want to receive other events (e.g. from the model)
    they must manage that themselves.

    """

    __metaclass__ = ModeMeta
    name = None

    def connect(self, control):
        """Respond to the connecting controller.

        :Parameters:
            `control` : Controller
                The connecting Controller object.

        """

    def disconnect(self):
        """Respond to the disconnecting controller.

        """

    def tick(self):
        """Process a single tick.

        """

    def update(self, dt):
        """Update real time components.

        :Parameters:
            `dt` : float
                The actual time that has passed since the last tick.

        """
