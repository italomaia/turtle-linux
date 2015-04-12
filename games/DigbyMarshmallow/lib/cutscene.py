from pyglet.window import key
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED
from pyglet.gl import *
from constants import *

import mode
import caterpie

import data
import os

class CutsceneMode(mode.Mode):
    name = 'cutscene'
    
    def __init__(self):
        self.control = None
        self.window = None
        self.text = ''
        self.image = None
        self.text_box = caterpie.TextBox(
            xpos = 0.0, ypos = 0.0,
            width = 0.5, height = 1.0,
            halign = "left", valign = "center",
            padding = MENU_PADDING,
            margin = MENU_MARGIN,
            font_size = MENU_FONT_SIZE,
            color = (255,255,255,255),
            expand = "horizontal"
        )
        self.center_box = caterpie.TextBox(
            xpos = 0.0, ypos = 0.0,
            width = 1.0, height = 1.0,
            halign = "center", valign = "center",
            padding = MENU_PADDING,
            margin = MENU_MARGIN,
            font_size = MENU_FONT_SIZE,
            color = (255,255,255,255),
        )
        self.fade_level = 1.0
        self.centered = False
    def fade_in(self, callback):
        self.fading = True
        self.target_fade = 0
        self.fade_callback = callback

    def fade_out(self, callback):
        self.fading = True
        self.target_fade = 1
        self.fade_callback = callback

    def stop_fade(self):
        self.fading = False
        self.target_fade = self.fade_level
        self.fade_callback = None

    def tick(self):
        if self.target_fade > self.fade_level:
            self.fade_level = min(self.target_fade, self.fade_level + FADE_RATE)
        elif self.target_fade < self.fade_level:
            self.fade_level = max(self.target_fade, self.fade_level - FADE_RATE)
        elif self.fading:
            old_callback = self.fade_callback
            if isinstance(self.fade_callback, tuple):
                func = self.fade_callback[0]
                args = self.fade_callback[1:]
                func(*args)
            else:
                self.fade_callback()
            if old_callback is self.fade_callback:
                self.stop_fade()
    
    def update_text(self):
        self.text = self.text_box.text = self.center_box.text = self.frames[self.frameno][0]
        img_file = self.frames[self.frameno][1]
        flags = self.frames[self.frameno][2]
        if 'center' in flags:
            self.centered = True
        else:
            self.centered = False
        if img_file:
            self.image = data.load_image(os.path.join('scenes', img_file), anchor_y='center')
        self.fade_in(lambda: None)

    def connect(self, control):
        self.control = control
        self.window = control.window
        self.text_box.window = self.window
        self.center_box.window = self.window
        self.frameno = 0
        self.frames = control.gamestate.current_frames
        self.update_text()
        
    def disconnect(self):
        self.control = None
        self.window = None

    def on_draw(self):
        self.window.clear()
        if self.text:
            if self.centered:
                self.center_box.draw()
            else:
                self.text_box.draw()
        if not self.centered and self.image:
            self.image.draw(self.window.width * .55, self.window.height *.5 , width = self.window.width*.4)
        if self.fade_level:
            sw, sh = self.window.get_size()
            glColor4f(0, 0, 0, self.fade_level)
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(sw, 0)
            glVertex2f(sw, sh)
            glVertex2f(0, sh)
            glEnd()

    def finish(self):
        self.control.gamestate.finish_level(self.control)
        if self.control.gamestate.advance:
            self.control.gamestate.start_level(self.control.gamestate.current_level, self.control)
        else:
            self.control.switch_handler('menu', 'levels')
    def on_key_press(self, sym, modifiers):
        if not self.fading:
            self.frameno += 1
            if self.frameno >= len(self.control.gamestate.current_frames):
                self.control.gamestate.win_level()
                self.fade_out(self.finish)
            else:
                self.fade_out(self.update_text)
        return EVENT_HANDLED
            
