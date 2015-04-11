import mode
import interface
import data
from constants import *

class CutsceneMode(mode.Mode):
    name = "cutscene"
    def __init__(self, garden_cls):
        super(CutsceneMode, self).__init__()
        self.garden_cls = garden_cls
        if garden_cls.cutscene_name:
            self.pages = data.load_scene(garden_cls.cutscene_name)
        else:
            self.pages = []
        self.text_box = interface.TextBox(
            xpos = 0.0, ypos = 0.0,
            width = 0.5, height = 1.0,
            halign = "left", valign = "center",
            expand = 'horizontal',
            font_size = 0.03,
            margin = 0.1,
            padding = 0.1,
            outline = (1, 1, 1, 1),
            background = (0, 0, 0, .1),
            font_name = FONT_NAME,
            text="""A couple of lines of text.
Lots of them.
Hooray!"""
        )
        self.center_text = interface.TextBox(
            xpos = 0.0, ypos = 0.0,
            width = 1.0, height = 1.0,
            halign = "center", valign = "center",
            font_size = 0.03,
            margin = 0.1,
            padding = 0.1,
            outline = (1, 1, 1, 1),
            background = (0, 0, 0, .1),
            font_name = FONT_NAME,
            text="""Centered text!
On multiple lines!"""
        )
        self.centered = False
        self.initialised = False
        
    def connect(self, control):
        super(CutsceneMode, self).connect(control)
        self.text_box.window = self.window
        self.center_text.window = self.window
        self.animate_fade_in()
    
    def tick(self):
        super(CutsceneMode, self).tick()
        if not self.initialised:
            self.advance_page()
            self.initialised = True
    
    def advance_page(self):
        try:
            self.text_box.text = self.center_text.text = self.pages.pop(0) 
        except IndexError:
            if self.initialised:
                self.animate_fade_out()
                self.animate_wait_call(self.control.switch_handler, 'game', self.garden_cls)
            else:
                self.control.switch_handler('game', self.garden_cls)
            
    def on_key_press(self, sym, mods):
        self.advance_page()
            
    def on_draw(self):
        self.window.clear()
        if self.initialised:
            if self.centered:
                self.center_text.draw()
            else:
                self.text_box.draw()
        super(CutsceneMode, self).on_draw()