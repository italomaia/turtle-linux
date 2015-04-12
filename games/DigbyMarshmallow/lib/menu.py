import pyglet
from pyglet import app
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED
from pyglet.window import key
from pyglet.gl import *

import mode
import caterpie

import config
from common import *
from constants import *

from content import levels, swags
import data
import os
import squirtle
import swag
class MenuMode(mode.Mode):
    name = "menu"
    downarrow_image = data.load_image("menu/down.svgz")
    uparrow_image = data.load_image("menu/up.svgz")
    star_image = data.load_image("menu/perfect.svgz")
    diary_image = data.load_image("menu/diary.svgz")
    questionmark_image = data.load_image("menu/questionmark.svgz")
    back_image = data.load_image("menu/back.svgz")
    bg_image = data.load_image("menu/background.svgz", anchor_x='center', anchor_y='center')
    def __init__(self, default="main"):
        self.control = None
        self.window = None

        self.title = caterpie.TextBox(
            xpos = 0.0, ypos = 0.7,
            width = 1.0, height = 0.3,
            halign = "center", valign = "center",
            padding = MENU_PADDING,
            margin = MENU_MARGIN,
            font_size = MENU_FONT_SIZE,
            text = "The Space Adventures of Digby Marshmallow, " \
                   "Space Burglar Extraordinaire ...In Space!",
        )

        self.level_display = caterpie.TextBox(
            xpos = 0.0, ypos = 0.7,
            width = 1.0, height = 0.3,
            halign = "center", valign = "center",
            padding = MENU_PADDING,
            margin = MENU_MARGIN,
            font_size = MENU_FONT_SIZE,
            text = "Select a level...",
            expand = "both",
        )

        self.collection_display = caterpie.TextBox(
            xpos = 0.0, ypos = 0.7,
            width = 1.0, height = 0.3,
            halign = "center", valign = "center",
            padding = MENU_PADDING,
            margin = MENU_MARGIN,
            font_size = MENU_FONT_SIZE,
            text = "Swag Collection",
            expand = "both",
        )
        
        self.menu = caterpie.TextMenu(
            xpos = 0.0, ypos = 0.1,
            width = 1.0, height = 0.6,
            halign = "center", valign="top",
            padding = MENU_PADDING,
            margin = MENU_MARGIN,
            spacing = MENU_SPACING,
            font_size = MENU_FONT_SIZE,
            scrolling=True
        )
        
        highlight_color = (0.4, 0.3, 0.5, 0.6)

        def arrow_set_mouse(self, x, y):
            if (x, y) in self:
                self.background = highlight_color
            else:
                style = caterpie.get_default_style()
                self.background = style.background

        self.downarrow = caterpie.ImageButton(
            halign="center", valign="top",
            graphic = self.downarrow_image,
            callback = (self.menu.scroll_relative, 5),
        )
        self.downarrow.set_mouse = arrow_set_mouse.__get__(self.downarrow)

        self.uparrow = caterpie.ImageButton(
            height = 0.05, halign="center", valign="bottom",
            graphic = self.uparrow_image,
            callback = (self.menu.scroll_relative, -5),
        )
        self.uparrow.set_mouse = arrow_set_mouse.__get__(self.uparrow)

        self.interface = [self.title, self.menu, self.level_display, self.collection_display]

        self.states = {

            "main" : [
                ("Start Game", (self.set_state, "levels")),
                ("Editor", self.do_editor),
                ("Collection", self.do_collection),
                ("Options", self.do_options),
                ("Quit", self.do_quit),
            ] if DEBUG else [
                ("Start Game", (self.set_state, "levels")),
                ("Collection", self.do_collection),
                ("Options", self.do_options),
                ("Quit", self.do_quit),
            ],

            "death" : [
                "You died!",
                ("Retry", self.do_retry_level),
                ("New level", (self.set_state, "levels")),
                ("Menu", (self.set_state, "main")),
            ],

            "continue" : [
                ("Continue", self.do_next_level),
                ("Retry", self.do_retry_level),
                ("New level", (self.set_state, "levels")),
                ("Menu", (self.set_state, "main")),
            ],

            "options" : [
                ("option:fullscreen", self.toggle_fullscreen),
                ("Back", (self.set_state, "main"))
            ],
            "collection" : [],
            "victory" : [],

        }

        self.scroll_states = ["levels"]
        self.title_states = ["main", "options"]
        self.menu_states = ["main", "options", "death", "continue"]

        self.state = None
        self.default = default

        self.fade_level = 1.0
        self.collection_back = None
        self.collection_up = None
        self.collection_down = None
        
    def fade_in(self, callback):
        self.fading = True
        self.target_fade = 0
        self.fade_callback = callback
        self.window.remove_handlers(self.menu)

    def fade_out(self, callback):
        self.fading = True
        self.target_fade = 1
        self.fade_callback = callback
        self.window.remove_handlers(self.menu)

    def stop_fade(self):
        self.fading = False
        self.target_fade = self.fade_level
        self.fade_callback = None
        if self.window is not None:
            if self.state in self.menu_states:
                self.window.push_handlers(self.menu)

    def tick(self):
        if self.target_fade > self.fade_level:
            self.fade_level = min(self.target_fade, self.fade_level + FADE_RATE)
        elif self.target_fade < self.fade_level:
            self.fade_level = max(self.target_fade, self.fade_level - FADE_RATE)
        elif self.fading:
            if isinstance(self.fade_callback, tuple):
                func = self.fade_callback[0]
                args = self.fade_callback[1:]
                func(*args)
            else:
                self.fade_callback()
            self.stop_fade()
        if self.state in ('collection', 'victory'):
            if self.control.keys[key.UP]:
                self.collection.view_y += 10
            elif self.control.keys[key.DOWN]:
                self.collection.view_y -= 10

    def connect(self, control):
        self.control = control
        self.window = control.window
        for component in self.interface:
            component.window = self.window

        self.position_buttons()
        self.prepare_levelicons()
        self.control.music.start_song("ABreezeFromAlabama.mp3")
        
        self.states['levels'] = []
        for n in xrange(min(control.gamestate.current_max_level + 1, len(levels.levels))):
            text = levels.levels[n][1]
            if n in control.gamestate.best_swags:
                text += ' (%d%%)' % (control.gamestate.best_swags[n][0],)
            option_spec = (text, (self.do_start_game, n))
            self.states['levels'].append(option_spec)
        self.states['levels'].append(("Back", (self.set_state, "main")))
        self.update_collection(self.control.gamestate.level_collected_swag if self.default == 'victory' else None)
        self.set_state(self.default)
        self.fade_in(lambda: None)

        
    def update_collection(self, swag_list=None):
        gs = self.control.gamestate
        self.collection_elements = []
        doc = pyglet.text.decode_attributed('')
        total_value = 0
       
        if swag_list is None:
            title_text = 'Swag Collection'
        else:
            title_text = 'Victory!'
        for cls, radius, name, img, value in swags.swags:
            if swag_list is None:
                total = 0
                for n in gs.best_swags:
                    swag_dict = gs.best_swags[n][1]
                    if name in swag_dict:
                        total += swag_dict[name]
            else:
                total = swag_list.get(name, 0)
            if total:
                elt = squirtle.SVGElement(data.load_image(os.path.join('swag', img), anchor_x='center', anchor_y='center'), 0.02 * self.window.height, radius=radius * self.window.height/SCREEN_HEIGHT, width=self.window.width * .35)
                self.collection_elements.append(elt)
                doc.insert_element(len(doc.text), elt)
                doc.insert_text(len(doc.text), '%d x %s ($%d) = $%d\n\n' % (total, name, value, total*value))
                total_value += total * value
        
        if swag_list is not None:
            swag_val = 0
            for a in gs.current_stage['actors']:
                if isinstance(a, swag.Swag):
                    swag_val += a.value
            title_text += ' (%d%%)' % (100 * total_value/swag_val,)
            if total_value == swag_val:
                title_text = 'Flawless ' + title_text
        title_text += '\nTotal Value: $%d' % (total_value,)
        self.collection_display.text = title_text
        if doc.text:
            doc.insert_text(len(doc.text), '\n\n\n')
            doc.set_style(0, len(doc.text), {'font_name': "Fontdinerdotcom", 'font_size': 0.04 * self.window.height, 'color': (255, 255, 255, 255)})
        self.collection = pyglet.text.layout.IncrementalTextLayout(
            doc,
            self.window.width * .9, self.window.height * .7,
            multiline=True)
        self.collection.content_valign = 'top'
        self.collection.x = self.window.width * .05
        self.collection.y = self.window.height * .65
        self.collection.anchor_x = 'left'
        self.collection.anchor_y = 'top'
        
        sw, sh = self.window.get_size()
        size = sh * 0.1
        self.collection_back = caterpie.ImageButton(
            xpos = sw * .05, ypos = sh * 0.1,
            width = size, height = size,
            callback = (self.set_state, 'continue' if swag_list is not None else 'main'),
            graphic = self.back_image,
            outline = None,
            background = None,
        )
        def up():
            self.collection.view_y += 50
        def down():
            self.collection.view_y -= 50
        self.collection_up = caterpie.ImageButton(
            xpos = sw * .95 - size, ypos = sh * 0.55,
            width = size, height = size,
            callback = up,
            graphic = self.uparrow_image,
            outline=None,
            background=None,
        )
        self.collection_down = caterpie.ImageButton(
            xpos = sw * .95 - size, ypos = sh * 0.05,
            width = size, height = size,
            callback = down,
            graphic = self.downarrow_image,
            outline=None,
            background=None,
        )
    def disconnect(self):
        for component in self.interface:
            component.window = None
        self.window.remove_handlers(self.menu)
        self.window.remove_handlers(self.uparrow)
        self.window.remove_handlers(self.downarrow)
        self.window.remove_handlers(self.collection_back)
        self.window.remove_handlers(self.collection_down)
        self.window.remove_handlers(self.collection_up)

        for icon in self.levelicons:
            self.window.remove_handlers(icon)
        self.window = None
        self.control = None

    def prepare_levelicons(self):
        sw, sh = self.window.get_size()
        li_size = sh * LEVELICON_SIZE
        spacing = sh * LEVELICON_SPACING
        y = spacing * 4 + li_size * 3
        self.levelicons = []
        self.currenticon = 0
        for j in xrange(4):
            x = (sw - li_size * 7 - spacing * 6) / 2
            for i in xrange(7):
                idx = 7*j+i
                def set_mouse(btn, x, y):
                    if btn.idx == 27:
                        self.level_display.text = "Select a level...\n"
                    if (x, y) in btn:
                        self.hover_level(btn.idx)
                if idx == 27:
                    graphic = self.back_image
                elif idx > self.control.gamestate.current_max_level:
                    graphic = self.questionmark_image
                elif levels.levels[idx][0].endswith(".scene"):
                    graphic = self.diary_image
                else:
                    graphic = pyglet.image.load(data.file_path(os.path.join("screenshots", levels.levels[idx][3])))
                    w, h = graphic.width, graphic.height
                    graphic = graphic.get_region(int(.5 * w - .4 * h), 0, int(h*.8), int(h*.8))
                if isinstance(graphic, pyglet.image.AbstractImage):
                    btn = caterpie.BitmapButton(xpos = x, ypos = y,
                        width = li_size, height = li_size,
                        padding = li_size / 10,
                        callback = (self.click_level, idx),
                        graphic = graphic,
                        outline=(0,0,0,1)
                    )
                else:
                    btn = caterpie.ImageButton(
                        xpos = x, ypos = y,
                        width = li_size, height = li_size,
                        padding = li_size / 10,
                        callback = (self.click_level, idx),
                        graphic = graphic,
                        outline=(0,0,0,1)
                    )
                btn.idx = idx
                btn.set_mouse = set_mouse.__get__(btn)
                self.levelicons.append(btn)
                x += spacing + li_size
            y -= spacing + li_size
        self.hover_level(0)

    def set_state(self, name):
        if self.state == "levels":
            for icon in self.levelicons:
                self.window.remove_handlers(icon)
        if self.state in ("collection", "victory"):
            self.window.remove_handlers(self.collection_back)
            self.window.remove_handlers(self.collection_down)
            self.window.remove_handlers(self.collection_up)
        if self.state == 'victory':
            self.control.gamestate.finish_level(self.control)
            self.update_collection()

        if self.state in self.menu_states:
            self.window.remove_handlers(self.menu)
        self.state = name
        self.menu.clear_options()
        self.menu.add_options(*self.states[name])
        if name in self.scroll_states:
            self.menu.scrolling = True
            self.position_buttons()
        else:
            self.menu.scrolling = False

        
        if name in ('victory', 'collection'):
            self.window.push_handlers(self.collection_back)
            self.window.push_handlers(self.collection_down)
            self.window.push_handlers(self.collection_up)
        if name == "levels":
            for icon in self.levelicons:
                self.window.push_handlers(icon)
        if self.state in self.menu_states:
            self.window.push_handlers(self.menu)

    def position_buttons(self):
        bx, by, bw, bh = self.menu.box_shape
        sw, sh = self.window.get_size()
        bh = self.menu.height * sh - 2 * self.menu.margin * sh
        self.uparrow.xpos = bx
        self.uparrow.ypos = by + bh
        self.uparrow.width = bw
        self.uparrow.height = bh / 10
        self.downarrow.xpos = bx
        self.downarrow.ypos = by - bh / 10
        self.downarrow.width = bw
        self.downarrow.height = bh / 10

    def click_level(self, idx):
        if idx == 27:
            self.set_state("main")
            return
        elif idx <= self.control.gamestate.current_max_level:
            self.fade_out((self.control.gamestate.start_level, idx, self.control))
            self.control.music.stop_song(1.0)
        else:
            pass

    def hover_level(self, idx):
        self.levelicons[self.currenticon].outline=(0,0,0,1)
        self.currenticon = idx
        self.levelicons[self.currenticon].outline=(1,1,1,1)
        if idx == 27:
            self.level_display.text = "Back..."
        elif idx <= self.control.gamestate.current_max_level:
            file, name, music, img = levels.levels[idx]
            self.level_display.text = name
            if idx in self.control.gamestate.best_swags:
                self.level_display.text += ' (%d%%)' % (self.control.gamestate.best_swags[idx][0],)
        else:
            self.level_display.text = "????"

    def do_next_level(self):
        self.fade_out((self.control.gamestate.start_level, self.control.gamestate.current_level, self.control))
        self.control.music.stop_song(1.0)

    def do_retry_level(self):
        self.fade_out((self.control.gamestate.start_level, self.control.gamestate.current_retry_level, self.control))
        self.control.music.stop_song(1.0)
        
    def do_start_game(self, n):
        self.fade_out((self.control.gamestate.start_level, n, self.control))
        self.control.music.stop_song(1.0)

    def do_editor(self):
        self.fade_out((self.control.switch_handler, "editor"))
        self.control.music.stop_song(1.0)
    
    def do_options(self):
        self.set_state("options")
        self.option_labels = {}
        for opt in self.menu.options:
            if opt.label.text.startswith("option:"):
                self.option_labels[opt.label.text[7:]] = opt.label
        suffix = ["Off", "On"][config.fullscreen]
        self.option_labels["fullscreen"].text = "Fullscreen: %s" % suffix

    def do_collection(self):
        self.set_state("collection")

    def do_quit(self):
        self.fade_out(app.exit)

    def toggle_fullscreen(self):
        config.fullscreen = not config.fullscreen
        config.save_option("fullscreen")
        suffix = ["Off", "On"][config.fullscreen]
        self.option_labels["fullscreen"].text = "Fullscreen: %s" % suffix

    def on_key_press(self, sym, mods):
        if self.state in ('collection', 'victory'):
            if sym in (key.UP, key.DOWN):
                return EVENT_UNHANDLED
        if self.state == 'collection' and sym == key.LEFT:
            self.set_state('main')
        if self.state == 'victory':
            self.set_state('continue')
        nexticon = None
        if self.state == 'levels':
            if sym == key.UP:
                nexticon = self.currenticon - LEVELS_PER_ROW
            if sym == key.DOWN:
                nexticon = self.currenticon + LEVELS_PER_ROW
            if sym == key.LEFT:
                nexticon = self.currenticon - 1
            if sym == key.RIGHT:
                nexticon = self.currenticon + 1
            if nexticon is not None:
                self.hover_level(nexticon % (LEVELS_PER_ROW * LEVEL_ROWS))
            if sym == key.ENTER:
                self.click_level(self.currenticon)
        if sym == key.ESCAPE:
            if self.state != 'main':
                self.set_state('main')
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_draw(self):
        self.window.clear()
        self.bg_image.draw(self.window.width / 2, self.window.height / 2, height=self.window.height)
        if self.state in self.menu_states:
            self.menu.draw()
            if self.menu.scrolling:
                self.uparrow.draw()
                self.downarrow.draw()
        elif self.state == "levels":
            for icon in self.levelicons:
                icon.draw()
                if self.control.gamestate.best_swags.get(icon.idx, [0.0, {}])[0] == 100.0:
                    w = icon.width / 3
                    self.star_image.draw(icon.xpos, icon.ypos, width=w)
            self.level_display.draw()
        elif self.state in ("collection", "victory"):
            sw, sh = self.window.get_size()
            glColor4f(0,0,0, 0.8)
            glBegin(GL_QUADS)
            glVertex2f(sw * .1, 0)
            glVertex2f(sw * .9, 0)
            glVertex2f(sw * .9, sh * .7)
            glVertex2f(sw * .1, sh * .7)
            glEnd()
            self.collection.draw()
            glEnable(GL_SCISSOR_TEST)
            glScissor(int(self.collection.x), int(self.collection.y - self.collection.height), int(self.collection.width), int(self.collection_display.box_shape[1]  - self.collection.y + self.collection.height))
            for elt in self.collection_elements:
                elt.draw()
            glDisable(GL_SCISSOR_TEST)
            self.collection_display.draw()
            self.collection_back.draw()
            if self.collection.view_y > self.collection.height - self.collection.content_height + EPSILON:
                self.collection_down.draw()
            if self.collection.view_y:
                self.collection_up.draw()
            
        if self.state in self.title_states:
            self.title.draw()
        if self.fade_level:
            sw, sh = self.window.get_size()
            glColor4f(0, 0, 0, self.fade_level)
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(sw, 0)
            glVertex2f(sw, sh)
            glVertex2f(0, sh)
            glEnd()
