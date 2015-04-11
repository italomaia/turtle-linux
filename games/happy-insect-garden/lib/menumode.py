"""Menu mode implementation.

"""

from __future__ import division

import math

from pyglet import app
from pyglet import graphics
from pyglet import window
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *

import achievement
import creature
import data
import descriptions
import garden
import interface
import mode
import sound

import config
from common import *
from constants import *

have_shown_no_avbin = False

class PopupButton(interface.ImageButton):
    active = False
    popup = 1.2

    def set_mouse(self, x, y):
        self.active = (x, y) in self

    def draw_content(self):
        """Draw the content.

        """
        if self.graphic is not None:
            cx, cy, cw, ch = self.content_shape
            gw = self.graphic.width
            gh = self.graphic.height
            ax = self.graphic.anchor_x
            ay = self.graphic.anchor_y
            glPushMatrix()
            glTranslatef(cx, cy, 0.0)
            glScalef(cw / gw, ch / gh, 1.0)
            glTranslatef(ax, ay, 0.0)
            if self.active:
                glScalef(self.popup, self.popup, 1.0)
            glColor3f(1.0, 1.0, 1.0)
            self.graphic.blit(0.0, 0.0)
            glPopMatrix()


class FramedIconGrid(interface.IconGrid):

    keyword_names = frozenset([
        "frame", "popup",
    ])

    frame = None
    popup = 1.5

    def get_popup(self, idx):
        return self.popup

    def draw_content(self):
        cx, cy, cw, ch = self.content_shape
        dim_x, dim_y = self.dimensions
        size = self.icon_size
        stride = self.icon_stride

        def draw(idx):
            img = self.images[idx]
            gw, gh = img.width, img.height
            ix, iy, iw, ih = self.icon_shapes[idx]
            if idx == self.current:
                glPushMatrix()
                tx, ty = self.scroll_vector
                glTranslatef(-tx, -ty, 0.0)
                glDisable(GL_SCISSOR_TEST)
                bx, by, bw, bh = self.box_shape
                scale = bw / self.frame.width
                self.frame.draw(bx, by + bh, scale=scale)
                glEnable(GL_SCISSOR_TEST)
                glPopMatrix()
            glPushMatrix()
            glTranslatef(ix, iy, 0.0)
            if idx == self.current:
                popup = self.get_popup(idx)
                glTranslatef(size / 2, size / 2, 0.0)
                glScalef(popup, popup, 1.0)
                glTranslatef(-size / 2, -size / 2, 0.0)
                glDisable(GL_SCISSOR_TEST)
            scale = min(iw / gw, ih / gh)
            glTranslatef(size / 2, size / 2, 0.0)
            glScalef(scale, scale, 1.0)
            self.draw_icon(idx)
            if idx == self.current:
                glEnable(GL_SCISSOR_TEST)
            glPopMatrix()

        idxs = range(len(self.images))
        if self.current is not None:
            idxs.remove(self.current)
            idxs.append(self.current)
        map(draw, idxs)

        if self.current is None:
            glPushMatrix()
            tx, ty = self.scroll_vector
            glTranslatef(-tx, -ty, 0.0)
            glDisable(GL_SCISSOR_TEST)
            bx, by, bw, bh = self.box_shape
            scale = bw / self.frame.width
            self.frame.draw(bx, by + bh, scale=scale)
            glEnable(GL_SCISSOR_TEST)
            glPopMatrix()


class BestiaryGrid(FramedIconGrid):
    popup = 1.5
    def get_popup(self, idx):
        if achievement.creature_gets[idx].value > 0:
            return self.popup
        return 1.2
    def draw_icon(self, idx):
        glColor3f(0.0, 0.0, 0.0)
        if achievement.creature_gets[idx].value > 0:
            glColor3f(1.0, 1.0, 1.0)
        image = self.images[idx]
        glRotatef(45.0, 0.0, 0.0, 1.0)
        image.blit(0.0, 0.0)


class GardenGrid(FramedIconGrid):
    popup = 1.3
    def get_popup(self, idx):
        if idx == 0 or achievement.levels[idx-1].value > 0:
            return self.popup
        return 1.2
    def draw_icon(self, idx):
        glColor3f(0.0, 0.0, 0.0)
        if idx == 0 or achievement.levels[idx-1].value > 0:
            glColor3f(1.0, 1.0, 1.0)
        image = self.images[idx]
        image.blit(0.0, 0.0)


class AchievementsGrid(FramedIconGrid):
    popup = 3.0
    def get_popup(self, idx):
        if achievement.handler.achievements[idx].achieved:
            return self.popup
        return 1.2
    def draw_icon(self, index):
        glColor3f(0.0, 0.0, 0.0)
        achs = achievement.handler.achievements
        if achs[index].achieved:
            glColor3f(1.0, 1.0, 1.0)
        else:
            dx, dy = self.dimensions
            y, x = divmod(index, dx)
            choices = [(x,y),(x-1,y),(x,y-1),(x+1,y),(x,y+1)]
            if x >= dx - 1: choices.remove((x+1, y))
            if y >= dy - 1: choices.remove((x, y+1))
            if y <= 0: choices.remove((x, y-1))
            if x <= 0: choices.remove((x-1, y))
            choices = [(x, y) for x, y in choices if 0 <= y*dx+x < len(achs)]
            if any(achs[y*dx+x].achieved for x, y in choices):
                glColor3f(0.2, 0.2, 0.2)
        image = self.images[index]
        image.blit(0.0, 0.0)


class MenuMode(mode.Mode):
    name = "menu"

    class MenuStyle(interface.Style):
        font_name = FONT_NAME
        padding = 0.02
        margin = 0.02
        spacing = 0.02
        unselected_color = (0.6, 0.6, 0.0, 1.0)
        selected_color = (1.0, 1.0, 0.0, 1.0)

    def __init__(self):
        super(MenuMode, self).__init__()

        # Customise the interface.
        interface.set_default_style(self.MenuStyle)
        self.MenuStyle.proxy = self

        # Interface proxy method.
        self.get_shape = lambda: self.fake_pos + self.window.get_size()
        self.fake_pos = (0.0, 0.0)

        ## Interface components
        #######################

        # Background

        self.bee_background = data.load_svg("menubee.svg")
        self.flowers_background = data.load_svg("menuflowers.svg")
        self.frame = data.load_svg("frame.svg", anchor_y="top")

        # Title

        self.title = interface.TextBox(
            xpos = 0.0, ypos = 0.75,
            width = 1.0, height = 0.25,
            halign = "center", valign = "bottom",
            font_size = 0.08, text = CAPTION,
        )

        # Main

        self.main_menu = interface.TextMenu(
            xpos = 0.0, ypos = 0.0,
            width = 1.0, height = 0.7,
            halign = "center", valign = "top",
            outline = (0.0, 0.0, 0.5, 1.0),
            background = (0.0, 0.0, 0.0, 0.4),
            font_size = 0.05,
        )

        self.main_menu.add_options(
            ("Play Game", self.option_gardens),
            ("Bestiary", self.option_bestiary),
            ("Awards", self.option_achievements),
            ("Options", self.option_options),
            ("Credits", self.option_credits),
            ("Quit", self.option_quit),
        )

        self.show_main = False

        # Gardens

        self.gardens = GardenGrid(
            xpos = 0.18, ypos = -0.02,
            width = 0.82, height = 0.62,
            halign = "center", valign = "top",
            scrolling = True, direction = "vertical",
            activate = self.option_gardens_activate,
            select = self.option_gardens_select,
            deselect = self.option_gardens_deselect,
            frame = self.frame, dimensions = (4, 2),
            spacing = 0.06, padding = 0.01,
        )
        self.gardens.row_factor = 0.0

        for idx, g in enumerate(garden.all_gardens):
            self.gardens.add_images(g.img_name or 'garden.png')

        self.gardens_back = PopupButton(
            xpos = 0.0, ypos = 0.0,
            width = 0.15, height = 0.65,
            halign = "center", valign = "center",
            scale_h = 0.15,
            graphic = data.load_image("back.png", centered=True),
            callback = self.option_gardens_back,
        )

        self.show_gardens = False

        # Bestiary

        self.bestiary = BestiaryGrid(
            xpos = 0.18, ypos = -0.02,
            width = 0.82, height = 0.62,
            halign = "center", valign = "top",
            scrolling = True, direction = "vertical",
            activate = self.option_bestiary_activate,
            select = self.option_bestiary_select,
            deselect = self.option_bestiary_deselect,
            frame = self.frame, dimensions = (7, 3),
        )

        for c in creature.Creature.all_creatures:
            self.bestiary.add_images(c.img_name)
            i = data.load_image(c.img_name)

        self.bestiary_textboxes = []
        for c in creature.Creature.all_creatures:
            creature_box = interface.TextBox(
                xpos = 0.4, ypos = 0.0,
                width = 0.6, height = 0.6,
                padding = 0.02, margin = 0.05,
                halign = "left", valign = "center",
                outline = (0.5, 0.5, 0.5, 1.0),
                background = (0.0, 0.0, 0.0, 0.8),
                expand = "horizontal", font_size = 0.025,
                text = descriptions.creature_descriptions[c],
                html = True,
            )
            self.bestiary_textboxes.append(creature_box)


        self.bestiary_left = interface.ImageBox(
            xpos = 0.0, ypos = 0.0,
            width = 0.4, height = 0.6,
            padding = 0.02, margin = 0.05,
        )

        self.bestiary_right = None

        self.bestiary_back = PopupButton(
            xpos = 0.0, ypos = 0.0,
            width = 0.15, height = 0.65,
            halign = "center", valign = "center",
            scale_h = 0.15,
            graphic = data.load_image("back.png", centered=True),
            callback = self.option_bestiary_back,
        )

        self.bestiary_scroll_up = PopupButton(
            xpos = 0.0, ypos = 0.0,
            width = 0.15, height = 0.65,
            halign = "center", valign = "top",
            scale_h = 0.15,
            graphic = data.load_image("up.png", centered=True),
            callback = self.option_bestiary_scroll_up,
        )

        self.bestiary_scroll_down = PopupButton(
            xpos = 0.0, ypos = 0.0,
            width = 0.15, height = 0.65,
            halign = "center", valign = "bottom",
            scale_h = 0.15,
            graphic = data.load_image("down.png", centered=True),
            callback = self.option_bestiary_scroll_down,
        )

        self.show_bestiary = False
        self.show_bestiary_entry = False

        # Achievements

        self.achievements = AchievementsGrid(
            xpos = 0.18, ypos = -0.02,
            width = 0.82, height = 0.62,
            halign = "center", valign = "top",
            scrolling = True, direction = "vertical",
            activate = self.option_achievements_activate,
            select = self.option_achievements_select,
            deselect = self.option_achievements_deselect,
            frame = self.frame, dimensions = (9, 14),
        )

        for ach in achievement.handler.achievements:
            self.achievements.add_images(ach.img_name)

        self.achievements_mouseover = interface.TextBox(
            xpos = 0.18, ypos = 0.0,
            width = 0.82, height = 0.2,
            outline = (0.5, 0.5, 0.5, 1.0),
            background = (0.0, 0.0, 0.0, 0.8),
            font_size = 0.03,
        )

        self.achievements_back = PopupButton(
            xpos = 0.0, ypos = 0.0,
            width = 0.15, height = 0.65,
            halign = "center", valign = "center",
            scale_h = 0.15,
            graphic = data.load_image("back.png", centered=True),
            callback = self.option_achievements_back,
        )

        self.achievements_scroll_up = PopupButton(
            xpos = 0.0, ypos = 0.0,
            width = 0.15, height = 0.65,
            halign = "center", valign = "top",
            scale_h = 0.15,
            graphic = data.load_image("up.png", centered=True),
            callback = self.option_achievements_scroll_up,
        )

        self.achievements_scroll_down = PopupButton(
            xpos = 0.0, ypos = 0.0,
            width = 0.15, height = 0.65,
            halign = "center", valign = "bottom",
            scale_h = 0.15,
            graphic = data.load_image("down.png", centered=True),
            callback = self.option_achievements_scroll_down,
        )

        self.show_achievements = False

        # Options

        self.options_menu = interface.TextMenu(
            xpos = 0.0, ypos = 0.0,
            width = 1.0, height = 0.7,
            halign = "center", valign = "top",
            outline = (0.0, 0.0, 0.5, 1.0),
            background = (0.0, 0.0, 0.0, 0.4),
            font_size = 0.05,
        )

        self.options_menu.add_options(
            ("Fullscreen: On", self.option_options_fullscreen),
            ("Music: On", self.option_options_music),
            ("Sound effects: On", self.option_options_sound_effects),
            ("Back", self.option_options_back),
        )

        self.options_map = {
            0: "fullscreen",
            1: "music",
            2: "sound_effects",
        }

        for idx, name in self.options_map.items():
            if not getattr(config, name):
                text = self.options_menu.options[idx].label.text
                text = text.rsplit(":", 1)[0] + ": Off"
                self.options_menu.options[idx].label.text = text
                self.options_menu.clear_cache()

        self.show_options = False
        self.refresh_options = False

        self.no_avbin_box = interface.TextBox(
            xpos = 0.0, ypos = 0.0,
            width = 1.0, height = 1.0,
            halign = "center", valign = "center",
            outline = (0.0, 0.0, 0.5, 1.0),
            background = (0.0, 0.0, 0.0, 0.7),
            font_size = 0.04, html = False,
            text = """Sorry!
In order to hear sounds or music, 
you'll need to install AVBin from
http://code.google.com/p/avbin/""",
        )

        self.show_no_avbin = False
        # Credits

        self.credits_box = interface.TextBox(
            xpos = 0.0, ypos = 0.0,
            width = 1.0, height = 0.7,
            halign = "center", valign = "center",
            outline = (0.0, 0.0, 0.5, 1.0),
            background = (0.0, 0.0, 0.0, 0.4),
            font_size = 0.04, html = True,
            text = descriptions.credits_text,
        )

        self.show_credits = False

        # All components

        self.interface_components = [self.title, self.main_menu, self.gardens, self.gardens_back, self.bestiary, self.bestiary_left, self.bestiary_back, self.bestiary_scroll_up, self.bestiary_scroll_down, self.achievements, self.achievements_mouseover, self.achievements_back, self.achievements_scroll_up, self.achievements_scroll_down, self.options_menu, self.no_avbin_box, self.credits_box] + self.bestiary_textboxes

        interface.set_default_style(None)

        ## Animation
        ############

        self.title_opacity = 1.0
        self.flowers_offset = 0.0
        self.main_menu_offset = 0.0
        self.gardens_offset = 0.0
        self.bestiary_offset = 0.0
        self.bestiary_entry_offset = 0.0
        self.achievements_offset = 0.0
        self.options_menu_offset = 0.0
        self.credits_offset = 0.0

    ## Controller methods
    #####################

    def connect(self, control):
        super(MenuMode, self).connect(control)
        self.get_size = self.window.get_size
        self.set_main()
        self.animate_fade_in()
        self.animate_main_menu_slide_in()
        self.animate_wait_call(lambda: None)
        self.animate_flowers_slide_up()
        self.control.music.change_song(MENU_MUSIC, 1.0, None)
        if not pyglet.media.have_avbin and not have_shown_no_avbin:
            self.set_show_no_avbin()

    def disconnect(self):
        self.clear_state()
        super(MenuMode, self).disconnect()

    def tick(self):
        super(MenuMode, self).tick()
        # Alter title opacity.
        color = list(self.title.color)
        color[-1] = max(0.0, min(1.0, self.title_opacity))
        self.title.color = tuple(color)

    ## Animation methods
    ####################

    def animate_title_fade_to(self, text):
        self.title_opacity = 1.0
        def per_tick():
            if self.title.text != text:
                self.title_opacity -= 0.06
                if self.title_opacity <= 0.0:
                    self.title_opacity = 0.0
                    self.title.text = text
                return False
            else:
                self.title_opacity += 0.06
                return self.title_opacity >= 1.0
        def finish():
            self.title_opacity = 1.0
        self.start_animation("title", per_tick, finish)

    def animate_flowers_slide_down(self):
        self.flowers_offset = 0.0
        def per_tick():
            self.flowers_offset += 0.08
            return self.flowers_offset >= 1.0
        def finish():
            self.flowers_offset = 1.0
        self.start_animation("flowers", per_tick, finish)

    def animate_flowers_slide_up(self):
        self.flowers_offset = 1.0
        def per_tick():
            self.flowers_offset -= 0.08
            return self.flowers_offset <= 0.0
        def finish():
            self.flowers_offset = 0.0
        self.start_animation("flowers", per_tick, finish)

    def animate_main_menu_slide_in(self):
        self.main_menu_offset = 1.0
        def per_tick():
            self.main_menu_offset -= 0.04
            return self.main_menu_offset <= 0.0
        def finish():
            self.main_menu_offset = 0.0
        self.start_animation("main_menu", per_tick, finish)

    def animate_main_menu_slide_out(self):
        self.main_menu_offset = 0.0
        def per_tick():
            self.main_menu_offset += 0.04
            return self.main_menu_offset >= 1.0
        def finish():
            self.main_menu_offset = 1.0
        self.start_animation("main_menu", per_tick, finish)

    def animate_gardens_slide_in(self):
        self.gardens_offset = 1.0
        def per_tick():
            self.gardens_offset -= 0.04
            return self.gardens_offset <= 0.0
        def finish():
            self.gardens_offset = 0.0
        self.start_animation("gardens", per_tick, finish)

    def animate_gardens_slide_out(self):
        self.gardens_offset = 0.0
        def per_tick():
            self.gardens_offset += 0.04
            return self.gardens_offset >= 1.0
        def finish():
            self.set_main()
            self.gardens_offset = 1.0
        self.start_animation("gardens", per_tick, finish)

    def animate_bestiary_slide_in(self):
        self.bestiary_offset = 1.0
        def per_tick():
            self.bestiary_offset -= 0.04
            return self.bestiary_offset <= 0.0
        def finish():
            self.bestiary_offset = 0.0
        self.start_animation("bestiary", per_tick, finish)

    def animate_bestiary_slide_out(self):
        self.bestiary_offset = 0.0
        def per_tick():
            self.bestiary_offset += 0.04
            return self.bestiary_offset >= 1.0
        def finish():
            self.set_main()
            self.bestiary_offset = 1.0
        self.start_animation("bestiary", per_tick, finish)

    def animate_bestiary_entry_slide_in(self):
        self.bestiary_entry_offset = 1.0
        def per_tick():
            self.bestiary_entry_offset -= 0.04
            return self.bestiary_entry_offset <= 0.0
        def finish():
            self.bestiary_entry_offset = 0.0
        self.start_animation("bestiary_entry", per_tick, finish)

    def animate_bestiary_entry_slide_out(self):
        self.bestiary_entry_offset = 0.0
        def per_tick():
            self.bestiary_entry_offset += 0.04
            return self.bestiary_entry_offset >= 1.0
        def finish():
            self.bestiary_entry_offset = 1.0
        self.start_animation("bestiary_entry", per_tick, finish)

    def animate_achievements_slide_in(self):
        self.achievements_offset = 1.0
        def per_tick():
            self.achievements_offset -= 0.04
            return self.achievements_offset <= 0.0
        def finish():
            self.achievements_offset = 0.0
        self.start_animation("achievements", per_tick, finish)

    def animate_achievements_slide_out(self):
        self.achievements_offset = 0.0
        def per_tick():
            self.achievements_offset += 0.04
            return self.achievements_offset >= 1.0
        def finish():
            self.set_main()
            self.achievements_offset = 0.0
        self.start_animation("achievements", per_tick, finish)

    def animate_options_menu_slide_in(self):
        self.options_menu_offset = 1.0
        def per_tick():
            self.options_menu_offset -= 0.04
            return self.options_menu_offset <= 0.0
        def finish():
            self.options_menu_offset = 0.0
        self.start_animation("options_menu", per_tick, finish)

    def animate_options_menu_slide_out(self):
        self.options_menu_offset = 0.0
        def per_tick():
            self.options_menu_offset += 0.04
            return self.options_menu_offset >= 1.0
        def finish():
            self.options_menu_offset = 1.0
        self.start_animation("options_menu", per_tick, finish)

    def animate_credits_slide_in(self):
        self.credits_offset = 1.0
        def per_tick():
            self.credits_offset -= 0.04
            return self.credits_offset <= 0.0
        def finish():
            self.credits_offset = 0.0
        self.start_animation("credits", per_tick, finish)

    def animate_credits_slide_out(self):
        self.credits_offset = 0.0
        def per_tick():
            self.credits_offset += 0.04
            return self.credits_offset >= 1.0
        def finish():
            self.credits_offset = 1.0
        self.start_animation("credits", per_tick, finish)

    ## State methods
    ################

    def clear_state(self):
        if self.show_main:
            self.window.remove_handlers(self.main_menu)
            self.show_main = False
        if self.show_gardens:
            self.window.remove_handlers(self.gardens)
            self.window.remove_handlers(self.gardens_back)
            self.show_gardens = False
        if self.show_bestiary:
            self.window.remove_handlers(self.bestiary)
            if self.show_bestiary_entry:
                self.window.remove_handlers(self.bestiary_left)
                self.window.remove_handlers(self.bestiary_right)
                self.show_bestiary_entry = False
            else:
                for child in self.bestiary.children:
                    self.window.remove_handlers(child)
            self.window.remove_handlers(self.bestiary_back)
            self.window.remove_handlers(self.bestiary_scroll_up)
            self.window.remove_handlers(self.bestiary_scroll_down)
            self.show_bestiary = False
        if self.show_achievements:
            self.window.remove_handlers(self.achievements)
            self.window.remove_handlers(self.achievements_back)
            self.window.remove_handlers(self.achievements_scroll_up)
            self.window.remove_handlers(self.achievements_scroll_down)
            self.show_achievements = False
        if self.show_options:
            self.window.remove_handlers(self.options_menu)
            self.show_options = False
        if self.show_credits:
            self.window.remove_handlers(self.credits_box)
            self.show_credits = False

    def set_main(self):
        self.clear_state()
        self.window.push_handlers(self.main_menu)
        self.show_main = True

    def set_gardens(self):
        self.clear_state()
        self.window.push_handlers(self.gardens)
        self.window.push_handlers(self.gardens_back)
        self.show_gardens = True

    def set_bestiary(self):
        self.clear_state()
        self.bestiary.content_shape
        self.window.push_handlers(self.bestiary)
        self.window.push_handlers(self.bestiary_back)
        self.window.push_handlers(self.bestiary_scroll_up)
        self.window.push_handlers(self.bestiary_scroll_down)
        self.show_bestiary = True

    def set_bestiary_entry(self):
        self.clear_state()
        self.show_bestiary = True
        self.show_bestiary_entry = True

    def set_achievements(self):
        self.clear_state()
        self.window.push_handlers(self.achievements)
        self.window.push_handlers(self.achievements_back)
        self.window.push_handlers(self.achievements_scroll_up)
        self.window.push_handlers(self.achievements_scroll_down)
        self.show_achievements = True

    def set_options(self):
        self.clear_state()
        self.window.push_handlers(self.options_menu)
        self.show_options = True

    def set_credits(self):
        self.clear_state()
        self.window.push_handlers(self.credits_box)
        self.show_credits = True

    ## Option handlers
    ##################

    # Main

    def option_gardens(self):
        sound.click()
        self.show_gardens = True
        self.animate_flowers_slide_down()
        self.animate_wait_call(lambda: None)
        self.animate_title_fade_to(u"Gardens")
        self.animate_main_menu_slide_out()
        self.animate_gardens_slide_in()
        self.animate_wait_call(self.set_gardens)

    def option_bestiary(self):
        sound.click()
        self.show_bestiary = True
        self.animate_flowers_slide_down()
        self.animate_wait_call(lambda: None)
        self.animate_title_fade_to(u"Bestiary")
        self.animate_main_menu_slide_out()
        self.animate_bestiary_slide_in()
        self.animate_wait_call(self.set_bestiary)

    def option_achievements(self):
        sound.click()
        self.show_achievements = True
        self.animate_flowers_slide_down()
        self.animate_wait_call(lambda: None)
        self.animate_title_fade_to(u"Awards")
        self.animate_main_menu_slide_out()
        self.animate_achievements_slide_in()
        self.animate_wait_call(self.set_achievements)

    def option_options(self):
        sound.click()
        self.show_options = True
        self.animate_title_fade_to(u"Options")
        self.animate_main_menu_slide_out()
        self.animate_options_menu_slide_in()
        self.animate_wait_call(self.set_options)

    def option_credits(self):
        sound.click()
        self.show_credits = True
        self.animate_title_fade_to(u"Credits")
        self.animate_main_menu_slide_out()
        self.animate_credits_slide_in()
        self.animate_wait_call(self.set_credits)

    def option_quit(self):
        sound.click()
        self.control.music.stop_song(2.0)
        self.animate_fade_out()
        self.animate_wait_call(app.exit)

    # Gardens

    def option_gardens_activate(self, index):
        if DEBUG or index == 0 or achievement.levels[index-1].value > 0:
            sound.click()
            self.control.music.stop_song(2.0)
            self.animate_fade_out()
            self.animate_wait_call(self.control.switch_handler, "game", garden.all_gardens[index])

    def option_gardens_select(self, index):
        pass

    def option_gardens_deselect(self, index):
        pass

    def option_gardens_back(self):
        sound.click()
        self.show_main = True
        self.animate_title_fade_to(CAPTION)
        self.animate_gardens_slide_out()
        self.animate_main_menu_slide_in()
        self.animate_wait_call(self.set_main)
        self.animate_flowers_slide_up()

    # Bestiary

    def option_bestiary_activate(self, index):
        if achievement.creature_gets[index].value > 0 or DEBUG:
            sound.click()
            self.show_bestiary_entry = True
            c = creature.Creature.all_creatures[index]
            self.bestiary_left.graphic = data.load_image(c.img_name)
            self.bestiary_right = self.bestiary_textboxes[index]
            self.animate_fade_out(target=0.5)
            self.animate_bestiary_entry_slide_in()
            self.animate_wait_call(self.set_bestiary_entry)

    def option_bestiary_select(self, index):
        pass

    def option_bestiary_deselect(self, index):
        pass

    def option_bestiary_back(self):
        sound.click()
        if self.show_bestiary_entry:
            self.animate_fade_in(start=0.5)
            self.animate_bestiary_entry_slide_out()
            self.animate_wait_call(self.set_bestiary)
        elif self.show_bestiary:
            self.show_main = True
            self.animate_title_fade_to(CAPTION)
            self.animate_bestiary_slide_out()
            self.animate_main_menu_slide_in()
            self.animate_wait_call(self.set_main)
            self.animate_flowers_slide_up()

    def option_bestiary_scroll_up(self):
        if self.bestiary.scroll_max > 0:
            sound.click()
            self.bestiary.scroll_relative(-2)
            self.bestiary.set_current(None)

    def option_bestiary_scroll_down(self):
        if self.bestiary.scroll_max > 0:
            sound.click()
            self.bestiary.scroll_relative(2)
            self.bestiary.set_current(None)

    # Achievements

    def option_achievements_activate(self, index):
        pass

    def option_achievements_select(self, index):
        dx, dy = self.achievements.dimensions
        y, x = divmod(index, dx)
        choices = [(x,y),(x-1,y),(x,y-1),(x+1,y),(x,y+1)]
        if x >= dx - 1: choices.remove((x+1, y))
        if y >= dy - 1: choices.remove((x, y+1))
        if y <= 0: choices.remove((x, y-1))
        if x <= 0: choices.remove((x-1, y))
        achs = achievement.handler.achievements
        choices = [(x, y) for x, y in choices if 0 <= y*dx+x < len(achs)]
        if any(achs[y*dx+x].achieved for x, y in choices):
            ach = achs[index]
            self.achievements_mouseover.text = unicode(ach.name)

    def option_achievements_deselect(self, index):
        self.achievements_mouseover.text = u""

    def option_achievements_back(self):
        sound.click()
        self.show_main = True
        self.animate_title_fade_to(CAPTION)
        self.animate_achievements_slide_out()
        self.animate_main_menu_slide_in()
        self.animate_wait_call(self.set_main)
        self.animate_flowers_slide_up()

    def option_achievements_scroll_up(self):
        if self.achievements.scroll_max > 0:
            sound.click()
            self.achievements.scroll_relative(-2)
            self.achievements.set_current(None)

    def option_achievements_scroll_down(self):
        if self.achievements.scroll_max > 0:
            sound.click()
            self.achievements.scroll_relative(2)
            self.achievements.set_current(None)

    # Options

    def option_options_fullscreen(self):
        sound.click()
        config.save_option("fullscreen", not config.fullscreen)
        text = self.options_menu.options[0].label.text.rsplit(":", 1)[0]
        text = text + [": Off", ": On"][config.fullscreen]
        self.options_menu.options[0].label.text = text
        self.window.set_fullscreen(config.fullscreen)
        for component in self.interface_components:
            component.clear_cache()
        self.refresh_options = True
        self.set_options()

    def option_options_music(self):
        sound.click()
        if not pyglet.media.have_avbin:
            self.set_show_no_avbin()
            return
        config.save_option("music", not config.music)
        text = self.options_menu.options[1].label.text.rsplit(":", 1)[0]
        text = text + [": Off", ": On"][config.music]
        self.options_menu.options[1].label.text = text
        self.options_menu.clear_cache()
        if config.music: self.control.music.start_song(MENU_MUSIC, 1.0)
        else: self.control.music.stop_song(2.0)

    def option_options_sound_effects(self):
        if not pyglet.media.have_avbin:
            self.set_show_no_avbin()
            return
        config.save_option("sound_effects", not config.sound_effects)
        sound.click()
        text = self.options_menu.options[2].label.text.rsplit(":", 1)[0]
        text = text + [": Off", ": On"][config.sound_effects]
        self.options_menu.options[2].label.text = text
        self.options_menu.clear_cache()

    def option_options_back(self):
        sound.click()
        self.show_main = True
        self.animate_title_fade_to(CAPTION)
        self.animate_options_menu_slide_out()
        self.animate_main_menu_slide_in()
        self.animate_wait_call(self.set_main)

    def set_show_no_avbin(self):
        global have_shown_no_avbin
        have_shown_no_avbin = True
        self.show_no_avbin = True
        def on_mouse_release(x, y, but, mods):
            self.show_no_avbin = False
            self.window.pop_handlers()
            return EVENT_HANDLED
        
        def on_mouse_press(x, y, but, mods):
            return EVENT_HANDLED
            
        def on_mouse_motion(x, y, dx, dy):
            return EVENT_HANDLED
        
        self.window.push_handlers(on_mouse_release, on_mouse_press, on_mouse_motion)
                
    # Credits

    def option_credits_back(self):
        sound.click()
        self.show_main = True
        self.animate_title_fade_to(CAPTION)
        self.animate_credits_slide_out()
        self.animate_main_menu_slide_in()
        self.animate_wait_call(self.set_main)

    ## Event handlers
    #################

    def on_key_press(self, sym, mods):
        if sym == key.ESCAPE:
            if self.show_gardens:
                self.option_gardens_back()
            elif self.show_bestiary_entry:
                self.option_bestiary_back()
            elif self.show_bestiary:
                self.option_bestiary_back()
            elif self.show_achievements:
                self.option_achievements_back()
            elif self.show_options:
                self.option_options_back()
            elif self.show_credits:
                self.option_credits_back()
            else:
                self.option_quit()
        elif sym == key.ENTER:
            if self.show_bestiary_entry:
                self.option_bestiary_back()
            elif self.show_credits:
                self.option_credits_back()
            else:
                return EVENT_UNHANDLED
        else:
            return EVENT_UNHANDLED
        return EVENT_HANDLED

    def on_mouse_release(self, x, y, btn, mods):
        if self.show_bestiary_entry:
            self.option_bestiary_back()
        elif self.show_credits:
            self.option_credits_back()
        else:
            return EVENT_UNHANDLED
        return EVENT_HANDLED

    ## Rendering
    ############

    def draw_background(self):
        scale = self.window.height / self.bee_background.height
        xoffset = (self.window.width - self.bee_background.width * scale) / 2
        yoffset = self.window.height * pop_cubic(self.flowers_offset)
        self.bee_background.draw(xoffset, 0.0, scale=scale)
        self.flowers_background.draw(xoffset, -yoffset, scale=scale)

    def draw_main_menu(self):
        glPushMatrix()
        ease_offset = ease_cubic(self.main_menu_offset)
        x_offset = ease_offset * -self.window.width
        self.fake_pos = (x_offset, 0.0)
        glTranslatef(x_offset, 0.0, 0.0)
        self.main_menu.draw()
        #interface.make_frame(self.main_menu)()
        self.fake_pos = (0.0, 0.0)
        glPopMatrix()

    def draw_gardens(self):
        glPushMatrix()
        ease_offset = ease_cubic(self.gardens_offset)
        x_offset = ease_offset * self.window.width
        self.fake_pos = (x_offset, 0.0)
        glTranslatef(x_offset, 0.0, 0.0)
        self.gardens.draw()
        self.gardens_back.draw()
        self.fake_pos = (0.0, 0.0)
        glPopMatrix()

    def draw_bestiary(self):
        glPushMatrix()
        ease_offset = ease_cubic(self.bestiary_offset)
        x_offset = ease_offset * self.window.width
        self.fake_pos = (x_offset, 0.0)
        glTranslatef(x_offset, 0.0, 0.0)
        self.bestiary.draw()
        if self.bestiary.scroll_max > 0:
            self.bestiary_scroll_up.draw()
            self.bestiary_scroll_down.draw()
        self.bestiary_back.draw()
        self.fake_pos = (0.0, 0.0)
        glPopMatrix()

    def draw_achievements(self):
        glPushMatrix()
        ease_offset = ease_cubic(self.achievements_offset)
        x_offset = ease_offset * self.window.width
        self.fake_pos = (x_offset, 0.0)
        glTranslatef(x_offset, 0.0, 0.0)
        self.achievements.draw()
        self.achievements_back.draw()
        if self.achievements.scroll_max > 0:
            self.achievements_scroll_up.draw()
            self.achievements_scroll_down.draw()
        if self.achievements_mouseover.text:
            self.achievements_mouseover.draw()
            interface.make_frame(self.achievements_mouseover)()
        self.fake_pos = (0.0, 0.0)
        glPopMatrix()

    def draw_options_menu(self):
        if self.refresh_options:
            self.refresh_options = False
            self.options_menu.clear_cache()
        glPushMatrix()
        ease_offset = ease_cubic(self.options_menu_offset)
        x_offset = ease_offset * self.window.width
        self.fake_pos = (x_offset, 0.0)
        glTranslatef(x_offset, 0.0, 0.0)
        self.options_menu.draw()
        self.fake_pos = (0.0, 0.0)
        glPopMatrix()

    def draw_bestiary_entry(self):
        glPushMatrix()
        ease_offset = ease_cubic(self.bestiary_entry_offset)
        y_offset = ease_offset * -self.window.height * self.bestiary_left.height
        self.fake_pos = (0.0, y_offset)
        glTranslatef(0.0, y_offset, 0.0)
        self.bestiary_left.draw()
        self.bestiary_right.draw()
        interface.make_frame(self.bestiary_right)()
        self.fake_pos = (0.0, 0.0)
        glPopMatrix()

    def draw_credits(self):
        glPushMatrix()
        ease_offset = ease_cubic(self.credits_offset)
        x_offset = ease_offset * self.window.width
        self.fake_pos = (x_offset, 0.0)
        glTranslatef(x_offset, 0.0, 0.0)
        self.credits_box.draw()
        self.fake_pos = (0.0, 0.0)
        glPopMatrix()

    def on_draw(self):
        glClearColor(0.5, 0.5, 1.0, 1.0)
        self.window.clear()
        self.draw_background()
        self.title.draw()
        if self.show_main:
            self.draw_main_menu()
        if self.show_gardens:
            self.draw_gardens()
        if self.show_bestiary:
            self.draw_bestiary()
        if self.show_achievements:
            self.draw_achievements()
        if self.show_options:
            self.draw_options_menu()
        if self.show_no_avbin:
            self.no_avbin_box.draw()
        if self.show_credits:
            self.draw_credits()
        super(MenuMode, self).on_draw()
        if self.show_bestiary_entry:
            self.draw_bestiary_entry()
