from __future__ import division

from pyglet import text
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED
from pyglet.window import key
from pyglet.gl import *

import data
import mode
import achievement
import achievementdisplay
import interface
import sound
import garden
from constants import *
from common import *

class GameOverMode(mode.Mode):
    name = "gameover"
    
    def __init__(self, game=None, *args, **kwargs):
        super(GameOverMode, self).__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()
        self.game = game

        self.initialised = False

        self.get_shape = lambda: (0.0, 0.0) + self.window.get_size()

        self.background = data.load_svg("endscreen.svg") if game.victorious else data.load_svg("gameoverscreen.svg")
        txt = "You Win!" if self.game.victorious else "Oh no!"

        self.game_over_label = interface.TextBox(
            xpos = 0.0, ypos = 0.7,
            width = 1.0, height = 0.3,
            halign = "center", valign = "bottom",
            padding = 0.02, margin = 0.02,
            proxy = self, font_name = FONT_NAME,
            font_size = 0.1, text = txt,
        )
        
        self.menu = interface.TextMenu(
            xpos = 0.0, ypos = 0.3,
            width = 1.0, height = 0.4,
            halign = "center", valign = "center",
            padding = 0.02, margin = 0.02,
            outline = (1.0, 1.0, 1.0, 0.5),
            background = (0.0, 0.0, 0.0, 0.5),
            proxy = self, font_name = FONT_NAME,
            font_size = 0.05,
        )

        is_last = (type(self.game.garden) is garden.all_gardens[-1])
        if self.game.victorious and not is_last:
            self.menu.add_options(
                ("Next Garden", self.next_garden),
                ("Again!", self.restart_garden),
                ("Main Menu", self.back_to_menu),
            )
        elif self.game.victorious:
            self.menu.add_options(
                ("Again!", self.restart_garden),
                ("Main Menu", self.back_to_menu),
            )
        else:
            self.menu.add_options(
                ("Retry", self.restart_garden),
                ("Main Menu", self.back_to_menu),
            )

    @cached
    def golframe(self):
        return interface.make_frame(self.game_over_label)
    @cached
    def mframe(self):
        return interface.make_frame(self.menu)

    def connect(self, control):
        super(GameOverMode, self).connect(control)
        if not self.initialised:
            self.animate_fade_in()
            self.ach_display = achievementdisplay.AchievementDisplay(self.control.window.width, self.control.window.height)

        txt = "You Win!" if self.game.victorious else "Game Over!"
        self.game_over_label = text.Label(
            txt,
            font_name=FONT_NAME,
            font_size=0.1*self.window.height,
            batch=self.batch,
            x=0.5*self.window.width,
            y=0.85*self.window.height,
            anchor_x='center',
            halign='center')

        achievement.handler.push_handlers(self)
        self.window.push_handlers(self.menu)
        

    def disconnect(self):
        self.window.remove_handlers(self.menu)
        super(GameOverMode, self).disconnect()

    def on_achievement(self, achievement):
        self.ach_display.show_achievement(achievement)
        
    def back_to_menu(self):
        sound.click()
        self.animate_fade_out()
        self.animate_wait_call(self.control.switch_handler, "menu")
        
    def on_key_press(self, sym, mods):
        if sym == key.ESCAPE:
            self.back_to_menu()
        else:
            return EVENT_UNHANDLED
        return EVENT_HANDLED
    
    def on_mouse_press(self, x, y, buttons, mods):
        return EVENT_HANDLED
        
    def restart_garden(self):
        sound.click()
        garden_cls = type(self.game.garden)
        self.animate_fade_out()
        self.animate_wait_call(self.control.switch_handler, "game", garden_cls)

    def next_garden(self):
        sound.click()
        garden_cls = type(self.game.garden)
        idx = garden.all_gardens.index(garden_cls)
        garden_cls = garden.all_gardens[idx + 1]
        self.animate_fade_out()
        self.animate_wait_call(self.control.switch_handler, "game", garden_cls)

    def draw_background(self):
        scale = self.window.height / self.background.height
        xoffset = (self.window.width - self.background.width * scale) / 2
        self.background.draw(xoffset, 0.0, scale=scale)

    def on_draw(self):
        self.window.clear()
        self.draw_background()
        self.batch.draw()
        self.menu.draw()
        self.mframe()
        self.game_over_label.draw()
        #self.golframe()
        self.ach_display.draw()
        super(GameOverMode, self).on_draw()

    def tick(self):
        super(GameOverMode, self).tick()
        self.ach_display.tick()
