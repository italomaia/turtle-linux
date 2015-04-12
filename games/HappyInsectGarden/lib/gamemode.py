"""Main game.

"""

from __future__ import division

import random

from pyglet import graphics
from pyglet import text
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED
from pyglet.window import key
from pyglet.gl import *

import achievement
import achievementdisplay
import creature
import data
import game
import garden
import interface
import mode
import particles
import plant
import sound


import config
from vector import *
from common import *
from constants import *




class ToolMenu(interface.IconGrid):
    pass


class WorldTransformGroup(pyglet.graphics.Group):
    def __init__(self, mode, parent=None):
        super(WorldTransformGroup, self).__init__(parent)
        self.mode = mode

    def set_state(self):
        glPushMatrix()
        scale, xo, yo = self.mode.screen_transform
        glScalef(scale, scale, 1)

    def unset_state(self):
        glPopMatrix()


class GameMode(mode.Mode):
    name = "game"

    class GameStyle(interface.Style):
        font_name = FONT_NAME

    def __init__(self, garden_cls=garden.ProtectTheRoses, *args, **kwargs):
        super(GameMode, self).__init__(*args, **kwargs)
        self.garden_cls = garden_cls
        self.initialised = False

        self.cutscene_pages = []
        self.stop_ticking = False

        self.background = data.load_svg("grass.svg")
        self.batch = pyglet.graphics.Batch()
        self.gui_batch = pyglet.graphics.Batch()
        wl = WorldTransformGroup(self, pyglet.graphics.OrderedGroup(0))

        self.background_layer = pyglet.graphics.OrderedGroup(0, wl)
        self.plant_layer = pyglet.graphics.OrderedGroup(1, wl)
        self.ground_layer = pyglet.graphics.OrderedGroup(2, wl)
        self.particle_layer = pyglet.graphics.OrderedGroup(3, wl)
        self.flying_layer = pyglet.graphics.OrderedGroup(4, wl)

        self.gui_layer = pyglet.graphics.OrderedGroup(1)

        self.particles = particles.ParticleSystem(batch=self.batch, group=self.particle_layer)

        if DEBUG: 
            debug_label = text.Label("DEBUG", font_name=FONT_NAME, font_size=20, x=0, y=0, batch=self.batch, group=self.gui_layer)
            self.fps = pyglet.clock.ClockDisplay()
        self.plant_type_to_add = self.garden_cls.plants[0]

        # Customise the interface.
        interface.set_default_style(self.GameStyle)
        self.GameStyle.proxy = self
        self.GameStyle.window = self

        ## Interface components
        #######################

        # Tool menu

        self.tool_button = interface.ImageButton(
            xpos = 0.0, ypos = 0.83,
            width = 0.2, height = 0.17,
            padding = 0.02, margin = 0.02,
            scale_h = 0.08, expand = "both",
            background = (0.0, 0.0, 0.0, 0.5),
            graphic = data.load_image(self.plant_type_to_add.img_name),
            callback = self.tool_button_click,
        )

        self.tool_menu = ToolMenu(
            xpos = 0.0, ypos = 0.0,
            width = 0.2, height = 0.83,
            padding = 0.02, margin = 0.02,
            background = (0.0, 0.0, 0.0, 0.5),
            dimensions = (2, 8), scrolling = True,
            activate = self.tool_menu_activate,
            select = self.tool_menu_select,
            deselect = self.tool_menu_deselect,
        )

        self.tool_texts = []
        for p in garden_cls.plants:
            self.tool_texts.append(interface.TextBox(
                xpos = 0.0, ypos = 0.0,
                width = 0.2, height = 0.2,
                padding = 0.02, margin = 0.03,
                halign = "center", valign = "bottom",
                expand = "horizontal", font_size = 0.02,
                html = True,
            ))
            self.tool_texts[-1].text = "<b>%s</b><br/><i>Cost: %s</i><br/><i>Shortcut: %s</i>" % (p.__name__, p.compost_cost, p.hotkey)

        self.tool_mouseover = None

        self.show_tool_menu = False
        self.tool_menu_offset = -0.2

        # Status menu

        self.status_button = interface.IconGrid(
            xpos = 0.8, ypos = 0.83,
            width = 0.2, height = 0.17,
            padding = 0.02, margin = 0.02,
            background = (0.0, 0.0, 0.0, 0.5),
            expand = "both", scrolling = True,
            dimensions = (2, 1), font_name = FONT_NAME,
            font_size = 0.02, color = (1.0, 1.0, 1.0, 1.0),
        )

        self.status_area = interface.IconGrid(
            xpos = 0.8, ypos = 0.0,
            width = 0.2, height = 0.83,
            padding = 0.03, margin = 0.02,
            background = (0.0, 0.0, 0.0, 0.5),
            expand = "both", scrolling = True,
            dimensions = (2, 9), font_name = FONT_NAME,
            font_size = 0.02, color = (1.0, 1.0, 1.0, 1.0),
            popup = 1.0
        )

        self.status_button.add_images("compost.png", u"100")

        self.status_area.add_images(
            None, u"",
            None, u"",
            None, u"",
            None, u"",
            None, u"",
            None, u"",
            None, u"",
            None, u"",
            None, u"",
        )

        self.show_status_area = False
        self.status_area_offset = 0.3

        self.status_map = {}

        i = 0
        for c in creature.Creature.all_creatures:
            if not c.is_evil:
                img = data.load_image(c.img_name, centered=True)
                lbl = self.status_area.images[i+1]
                self.status_map[c] = img, lbl
                i += 2

        self.frame = data.load_image("woodframe.png")

        # Advisor

        self.advisor_text = interface.TextBox(
            xpos = 0.2, ypos = 0.02,
            width = 0.6, height = 0.2,
            padding = 0.02, margin = 0.0,
            halign = "left", valign = "top",
            color = (0.0, 0.0, 0.0, 1.0),
            background = (1.0, 1.0, 1.0, 1.0),
            expand = "both", font_name = FONT_NAME,
            font_size = 0.03,
        )

        self.advisor_text_2 = interface.TextBox(
            xpos = 0.2, ypos = 0.02,
            width = 0.6, height = 0.2,
            padding = 0.02, margin = 0.0,
            halign = "left", valign = "top",
            color = (0.0, 0.0, 0.0, 1.0),
            background = (1.0, 1.0, 1.0, 1.0),
            expand = "both", font_name = FONT_NAME,
            font_size = 0.03,
        )

        self.advisor = data.load_svg("dude.svg")
        self.show_advisor = False
        self.advisor_offset = 0.0
        self.advisor_text_offset = 0.0

        interface.set_default_style(None)
        self.fake_pos = (0.0, 0.0)

    def get_shape(self):
        fx, fy = self.fake_pos
        scx, scy, scw, sch = self.scissor_shape
        return scx + fx, scy + fy, scw - fx, sch - fy
    def get_size(self):
        scx, scy, scw, sch = self.scissor_shape
        return scw, sch

    ## State methods
    ################

    def clear_state(self):
        if self.show_tool_menu:
            self.window.remove_handlers(self.tool_menu)
            self.show_tool_menu = False

    def set_tool_menu(self):
        self.clear_state()
        self.window.push_handlers(self.tool_menu)
        self.show_tool_menu = True

    ## Option handlers
    ##################

    def tool_button_click(self):
        sound.click()
        if not self.show_tool_menu:
            self.set_tool_menu()
        else:
            self.clear_state()

    def tool_menu_activate(self, index):
        sound.click()
        self.set_plant_to_add(self.game.garden.plants[index])
        self.tool_menu.set_current(None)
        self.clear_state()

    def tool_menu_select(self, index):
        self.tool_mouseover = self.tool_texts[index]

    def tool_menu_deselect(self, index):
        self.tool_mouseover = None

    def status_area_activate(self, index):
        pass

    def status_area_select(self, index):
        pass

    def status_area_deselect(self, index):
        pass

    ## Controller methods
    #####################

    def connect(self, control):
        super(GameMode, self).connect(control)
        if not self.initialised:
            self.game = game.Game(self, self.garden_cls, WORLD_WIDTH, WORLD_HEIGHT)
            self.game.push_handlers(achievement.handler)
            self.game.push_handlers(self)
            self.key_press_despatch = {
                key.ESCAPE: (self.game_over, []),
                key.H: (self.set_plant_to_add, [plant.Honeysuckle]),
                key.R: (self.set_plant_to_add, [plant.Rose]),
                key.A: (self.set_plant_to_add, [plant.Apple]),
                key.B: (self.set_plant_to_add, [plant.Bluebell]),
                key.D: (self.set_plant_to_add, [plant.Daisy]),
                key.S: (self.set_plant_to_add, [plant.Sunflower]),
                key.F: (self.set_plant_to_add, [plant.Fuchsia]),
                key.Y: (self.set_plant_to_add, [plant.Cherry]),
                key.O: (self.set_plant_to_add, [plant.Orange]),
                key.C: (self.set_plant_to_add, [plant.Cabbage]),
                key.M: (self.set_plant_to_add, [plant.Marrow]),
                key.L: (self.set_plant_to_add, [plant.Log]),
                key.T: (self.set_plant_to_add, [plant.Carrot]),
                key.SPACE: (self.open_menus, []),}
            self.ach_display = achievementdisplay.AchievementDisplay(self.control.window.width, self.control.window.height)
            achievement.handler.push_handlers(self)
            self.particles.group.size *= self.screen_transform[0]
            self.tool_menu.add_images(*(p.img_name for p in self.game.garden.plants))

            self.initialised = True
        music = random.choice(GAME_MUSICS)
        self.control.music.start_song(music, 2.0)
        self.window.push_handlers(self.tool_button)
        garden_cls = type(self.game.garden)
        if garden_cls.cutscene_name:
            self.start_cutscene(garden_cls.cutscene_name)

    def disconnect(self):
        self.clear_state()
        self.window.remove_handlers(self.tool_button)
        achievement.handler.remove_handlers(self)
        if DEBUG: self.fps.unschedule()
        super(GameMode, self).disconnect()

    def tick(self):
        if not self.stop_ticking:
            angle = random.random() * 360
            for creature in self.game.creatures:
                if creature.flying and creature.movement_algorithm.vel and (random.random() * 10) ** 2 < creature.movement_algorithm.vel.length2:
                    self.particles.add_particle(creature.pos, unit_x.rotated(angle), (.1,0,0,.2) if creature.is_evil else (1,.9,.8,.2))
            self.particles.tick()
            self.game.tick()

        self.ach_display.tick()

        # Animate tool menu.
        xpos = self.tool_menu.xpos + self.tool_menu_offset
        xpos = xpos + 0.2 * ((0.0 if self.show_tool_menu else -0.2) - xpos)
        self.tool_menu_offset = xpos - self.tool_menu.xpos

        # Animate status menu.
        xpos = self.status_area.xpos + self.status_area_offset
        xpos = xpos + 0.2 * ((0.8 if self.show_status_area else 1.0) - xpos)
        self.status_area_offset = xpos - self.status_area.xpos

        super(GameMode, self).tick()

    ## Animation
    ############

    def animate_advisor_text_slide_in(self):
        self.advisor_text_offset = 1.0
        def per_tick():
            self.advisor_text_offset -= 0.04
            return self.advisor_text_offset <= 0.0
        def finish():
            self.advisor_text_offset = 0.0
        self.start_animation("advisor_text", per_tick, finish)

    def animate_advisor_text_slide_out(self):
        self.advisor_text_offset = 0.0
        def per_tick():
            self.advisor_text_offset += 0.04
            return self.advisor_text_offset >= 1.0
        def finish():
            self.advisor_text_offset = 1.0
        self.start_animation("advisor_text", per_tick, finish)

    def animate_advisor_slide_in(self):
        self.advisor_offset = 1.0
        def per_tick():
            self.advisor_offset -= 0.04
            return self.advisor_offset <= 0.0
        def finish():
            self.advisor_offset = 0.0
        self.start_animation("advisor", per_tick, finish)

    def animate_advisor_slide_out(self):
        self.advisor_offset = 0.0
        def per_tick():
            self.advisor_offset += 0.04
            return self.advisor_offset >= 1.0
        def finish():
            self.advisor_offset = 1.0
        self.start_animation("advisor", per_tick, finish)

    ## Event handlers
    #################

    def start_cutscene(self, name):
        if achievement.levels[garden.all_gardens.index(type(self.game.garden))].value == 0:
            self.cutscene_pages = data.load_scene(name)
            self.stop_ticking = True
            self.advance_page()

    def on_key_press(self, sym, mods):
        if self.show_advisor:
            self.advance_page()
            return EVENT_HANDLED
        if DEBUG and sym == key.W and mods & key.MOD_SHIFT:
            self.game.victorious = True
            self.game_over()
        elif DEBUG and sym == key.L and mods & key.MOD_SHIFT:
            self.game.victorious = False
            self.game_over()
        elif sym in self.key_press_despatch:
            func, args = self.key_press_despatch[sym]
            func(*args)
        else:
            return EVENT_UNHANDLED
        return EVENT_HANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_release(self, x, y, buttons, mods):
        scx, scy = self.scissor_shape[:2]
        gx, gy = x - scx, y - scy
        if (gx, gy) in self.status_button:
            sound.click()
            self.show_status_area = not self.show_status_area
            return EVENT_HANDLED
        if self.show_advisor:
            sound.click()
            self.advance_page()
            return EVENT_HANDLED
        x, y = self.screen_to_world(x, y)
        if x is not None:
            p = self.game.add_plant_at(self.plant_type_to_add, Vector((x, y)))
            if p: sound.plant()
            else: sound.bad()

    def on_add_plant(self, game, plant):
        for j in xrange(5):
            for i in xrange(6*(j+1)):
                angle = random.random() * 360
                vel = (j+1)*.6*unit_x.rotated(angle)
                self.particles.add_particle(plant.pos + vel*10, vel, (.4, .6, .4, .3))

    def on_kill_plant(self, game, killer, plant):
        for j in xrange(5):
            for i in xrange(6*(j+1)):
                angle = random.random() * 360
                vel = (j+1)*.6*unit_x.rotated(angle)
                self.particles.add_particle(plant.pos + vel*10, vel, (.6, .5, .4, .3))

    def on_kill_dude(self, game, killer, dead):
        sound.pop()
        pos = dead.pos
        for i in xrange(1 + dead.biomass // 2):
            vel = v(random.gauss(0,1), random.gauss(0,1))
            angle = random.random() * 360
            self.particles.add_particle(pos, vel, (.1,0,0,.5) if dead.is_evil else (1,.9,.8,.5))

    def on_achievement(self, achievement):
        self.ach_display.show_achievement(achievement)

    def open_menus(self):
        sound.click()
        if self.show_tool_menu and self.show_status_area:
            self.clear_state()
            self.tool_menu.set_current(None)
            self.show_status_area = False
        else:
            self.set_tool_menu()
            self.show_status_area = True

    def set_plant_to_add(self, plant_type):
        if plant_type in self.game.garden.plants:
            self.plant_type_to_add = plant_type
            self.tool_button.graphic = data.load_image(plant_type.img_name)

    def game_over(self):
        if self.game.victorious:
            self.control.music.change_song(VICTORY_MUSIC, None, 0.5, True, True)
        else:
            self.control.music.change_song(GAMEOVER_MUSIC, None, 0.5, True, True)
        self.stop_ticking = True
        self.animate_fade_out(rate=0.01)
        def switch():
            self.control.switch_handler("gameover", self.game)
            # 'on_game_end' goes to 'gameover'.
            self.game.end()
        self.animate_wait_call(switch)

    def advance_page(self):
        if len(self.cutscene_pages) > 0:
            if self.show_advisor:
                self.advisor_text.text = self.cutscene_pages.pop(0)
                self.advisor_text, self.advisor_text_2 = self.advisor_text_2, self.advisor_text
                self.animate_advisor_text_slide_out()
            else:
                self.show_advisor = True
                self.stop_ticking = True
                self.advisor_text_offset = 1.0
                self.advisor_text_2.text = self.cutscene_pages.pop(0)
                self.animate_advisor_slide_in()
        else:
            def start():
                self.show_advisor = False
                self.stop_ticking = False
            self.animate_advisor_slide_out()
            self.animate_wait_call(start)

    ## View rectangle
    #################

    @cached
    def scissor_shape(self):
        """The shape of the scissor box around the word box.

        """
        ww, wh = WORLD_WIDTH, WORLD_HEIGHT
        scale, xo, yo = self.screen_transform

        return [
            int(math.floor(xo * scale)),
            int(math.floor(yo * scale)),
            int(math.floor(ww * scale)),
            int(math.floor(wh * scale)),
        ]

    @cached
    def screen_transform(self):
        """The screen transformation data.

        """
        sw, sh = self.window.get_size()
        ww, wh = WORLD_WIDTH, WORLD_HEIGHT

        scale = min(sh / wh, sw / ww)
        xo = (sw / scale - ww) / 2
        yo = (sh / scale - wh) / 2

        return scale, xo, yo

    def screen_to_world(self, x, y):
        """Convert the given coordinates to world coordinates. Return None if
        the coordinates are outside the scissor box.

        :Parameters:
            `x`, `y` : int
                The screen coordinates to convert.

        """
        scx, scy, scw, sch = self.scissor_shape
        if scx <= x <= scx + scw and scy <= y <= scy + sch:
            scale, xo, yo = self.screen_transform
            return x / scale - xo, y / scale - yo
        return None, None

    def apply_screen_transform(self):
        """Perform the transform to place the world box in the middle of the
        screen and apply a scissor box around it.

        """
        scale, xo, yo = self.screen_transform

        glTranslatef(xo * scale, yo * scale, 0.0)
        glScissor(*self.scissor_shape)

    ## Rendering
    ############

    def update_status_area(self):
        self.status_button.images[1].text = unicode(self.game.compost)
        self.status_area.content_shape
        images = self.status_area.images
        result, extra = [], []
        for c in self.status_map:
            img, lbl = self.status_map[c]
            n = self.game.creature_tally.get(c, 0)
            if n > 0:
                lbl.text = unicode(n)
                result.extend([img, lbl])
            #else:
            #    lbl.text = u""
            #    extra.extend([None, lbl])
        self.status_area.images = result + extra

    def draw_background(self):
        scale, xo, yo = self.screen_transform
        ww, wh = WORLD_WIDTH, WORLD_HEIGHT
        img_scale = wh * scale / self.background.height
        offset = (ww * scale - self.background.width * img_scale) / 2
        self.background.draw(offset, 0, scale=img_scale)

    def on_draw(self):
        from creatures import Bee, BlackAnt

        # Clear the color buffer to black.
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Set the clear color to green.
        glClearColor(0.3, 0.5, 0.0, 1.0)

        glPushMatrix()
        self.apply_screen_transform()
        glEnable(GL_SCISSOR_TEST)
        self.window.clear()

        self.draw_background()
        self.batch.draw()

        # GUI
        self.draw_gui()
        glDisable(GL_SCISSOR_TEST)
        if DEBUG: self.fps.draw()
        glPopMatrix()
        self.ach_display.draw()

        super(GameMode, self).on_draw()

    @cached
    def tbframe(self):
        return interface.make_frame(self.tool_button)
    @cached
    def tmframe(self):
        return interface.make_frame(self.tool_menu)
    @cached
    def sbframe(self):
        return interface.make_frame(self.status_button)
    @cached
    def saframe(self):
        return interface.make_frame(self.status_area)

    def draw_gui(self):
        self.update_status_area()

        ## Status Area

        # Status button
        self.status_button.draw()
        self.sbframe()

        # Status grid
        glPushMatrix()
        offset = self.status_area_offset * self.window.width
        glTranslatef(offset, 0.0, 0.0)
        self.fake_pos = (offset, 0.0)
        self.status_area.draw()
        self.saframe()
        self.fake_pos = (0.0, 0.0)
        glPopMatrix()

        ## Tool Menu

        # Tool button
        self.tool_button.draw()
        self.tbframe()

        # Tool grid
        glPushMatrix()
        offset = self.tool_menu_offset * self.window.width
        glTranslatef(offset, 0.0, 0.0)
        self.fake_pos = (-self.tool_menu.margin*self.window.height, 0.0)
        self.tool_menu.draw_frame = self.tmframe
        self.tool_menu.draw()
        if self.tool_mouseover is not None:
            self.tool_mouseover.draw()
        self.fake_pos = (0.0, 0.0)
        glPopMatrix()

        # Advisor
        if self.show_advisor:
            scale = self.advisor.width / self.scissor_shape[2]
            offset = self.advisor.height * ease_cubic(self.advisor_offset)
            text_height = self.advisor_text.height * self.window.height
            text_offset = text_height * ease_cubic(self.advisor_text_offset)
            glPushMatrix()
            glTranslatef(0.0, -offset, 0.0)
            self.advisor.draw(x=0, y=0, scale=1/scale)
            scx, scy, scw, sch = self.advisor_text.scissor_shape
            o = int(offset)
            glScissor(scx-o, scy-o, scw, sch)
            glEnable(GL_SCISSOR_TEST)
            glPushMatrix()
            glTranslatef(0.0, text_offset, 0.0)
            if self.advisor_text_offset < 1.0:
                self.advisor_text.draw()
            glTranslatef(0.0, -text_height, 0.0)
            self.advisor_text_2.draw()
            glPopMatrix()
            fade_l = 0.02 * self.window.height
            pyglet.graphics.draw(8, GL_QUADS, ('v2f', [scx, scy, scx+scw, scy, scx+scw, scy+fade_l, scx, scy+fade_l, scx, scy+sch, scx+scw, scy+sch, scx+scw, scy+sch-fade_l, scx, scy+sch-fade_l]), ('c4f', [1,1,1,1, 1,1,1,1, 1,1,1,0, 1,1,1,0] *2))
            glPopMatrix()
