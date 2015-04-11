import pyglet

from pyglet.window import key


ssn = 0

class CheatController(object):

    def __init__(self, handler):
        self.handler = handler

    def on_key_press(self, sym, mods):
        global ssn
        if sym == key.S:
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot-%d.png' % (ssn,))
            ssn += 1
