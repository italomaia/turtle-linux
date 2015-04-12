"""Interface object framework.

"""

from __future__ import division

import pyglet
from pyglet.window import key
from pyglet.gl import *
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED

import config
from common import *
from constants import *


#: Global directory of modes, updated automatically when modes are created.
mode_directory = {}

class EventBlocker(object):
    def on_key_press(self, sym, mods): return EVENT_HANDLED
    def on_key_release(self, sym, mods): return EVENT_HANDLED
    def on_mouse_drag(self, x, y, dx, dy, btns, mods): return EVENT_HANDLED
    def on_mouse_enter(self, x, y): return EVENT_HANDLED
    def on_mouse_leave(self, x, y): return EVENT_HANDLED
    def on_mouse_motion(self, x, y, dx, dy): return EVENT_HANDLED
    def on_mouse_press(self, x, y, btn, mods): return EVENT_HANDLED
    def on_mouse_release(self, x, y, btn, mods): return EVENT_HANDLED
    def on_mouse_scroll(self, x, y, sx, sy): return EVENT_HANDLED
EventBlocker = EventBlocker()

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


class Mode(object):
    """Base class for root interface objects.

    Modes are designed to connect to the controller. They are responsible for
    all event handling.

    """

    #: The name used to key the mode in the mode directory.
    name = None

    ## Metaclass
    ############

    class ModeMeta(type):
        """Metaclass for root interface objects.

        Updates the mode directory when a new mode is created.

        """

        def __init__(self, name, bases, dict):
            """Construct a ModeMeta object.

            """
            super(self.ModeMeta, self).__init__(name, bases, dict)
            if self.name is None and None in mode_directory:
                raise AssertionError, "must override mode name in subclasses"
            elif self.name in mode_directory:
                raise AssertionError, "mode %r already exists" % self.name
            mode_directory[self.name] = self

    __metaclass__ = ModeMeta

    ## Constructor
    ##############

    def __init__(self):
        """Construct a Mode object.

        """
        super(Mode, self).__init__()
        #: Default key state handler.
        self.keys = key.KeyStateHandler()
        self.anim_stack = [{}]
        self.anim_event = False
        self.fade_opacity = 0.0

    ## Controller methods
    #####################

    def connect(self, control):
        """Respond to the connecting controller.

        :Parameters:
            `control` : Controller
                The connecting Controller object.

        """
        self.control = control
        self.window = control.window
        self.window.push_handlers(self.keys)
        self.content_size = self.window.get_size()

    def disconnect(self):
        """Respond to the disconnecting controller.

        """
        if self.is_animating:
            self.window.remove_handlers(EventBlocker)
        self.window.remove_handlers(self.keys)
        self.window = None
        self.control = None

    def tick(self):
        """Process a single tick.

        """
        for name in list(self.anim_stack[0]):
            per_tick, finish = self.anim_stack[0][name]
            if per_tick():
                self.stop_animation(name)
                finish()
                
    def update(self, dt):
        """Update real time components.

        :Parameters:
            `dt` : float
                The actual time that has passed since the last tick.

        """

    ## Animation methods
    ####################

    def start_animation(self, name, per_tick, finish, wait=False):
        if not self.is_animating or self.anim_event:
            self.window.push_handlers(EventBlocker)
        if wait or name in self.anim_stack[-1]:
            self.anim_stack.append({})
        self.anim_stack[-1][name] = (per_tick, finish)

    def stop_animation(self, name):
        del self.anim_stack[0][name]
        if len(self.anim_stack[0]) == 0:
            self.anim_stack.pop(0)
        if len(self.anim_stack) == 0:
            self.anim_stack.append({})
            if not self.anim_event:
                self.window.remove_handlers(EventBlocker)
            self.anim_event = False

    def animate_wait_call(self, func, *args, **kwds):
        def per_tick():
            return True
        def finish():
            func(*args, **kwds)
        self.start_animation("wait_call", per_tick, finish, True)

    def animate_allow_events(self):
        def per_tick():
            return True
        def finish():
            self.anim_event = True
            self.window.remove_handlers(EventBlocker)
        self.start_animation("allow_events", per_tick, finish)

    def animate_fade_out(self, rate=0.04, target=1.0):
        self.fade_opacity = 0.0
        delay = range(5)
        def per_tick():
            self.fade_opacity = min(target, self.fade_opacity + rate)
            if self.fade_opacity >= target:
                return not delay.pop()
        def finish():
            self.fade_opacity = target
        self.start_animation("fade", per_tick, finish)

    def animate_fade_in(self, rate=0.04, start=1.0):
        self.fade_opacity = start
        delay = range(5)
        def per_tick():
            self.fade_opacity = max(0.0, self.fade_opacity - rate)
            if self.fade_opacity <= 0.0:
                return not delay.pop()
        def finish():
            self.fade_opacity = 0.0
        self.start_animation("fade", per_tick, finish)

    @property
    def is_animating(self):
        return self.anim_stack != [{}]
    
    def on_draw(self):
        if self.fade_opacity > 0.0:
            sw, sh = self.window.get_size()
            c = [0.0, 0.0, 0.0, self.fade_opacity] * 4
            v = [0, 0, 0, sh, sw, sh, sw, 0]
            pyglet.graphics.draw(4, GL_QUADS, ('c4f', c), ('v2f', v))    
