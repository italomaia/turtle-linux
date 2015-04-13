# coding:utf-8

import os
from datetime import datetime, timedelta
from gi.repository import Gtk, Gdk
from subprocess import call, Popen
from glob import glob

GLADE_FILE = 'main.glade'
GLADE_PATH = os.path.exists(GLADE_FILE) and 'main.glade' or os.path.join('/usr/local/vapor/glade', GLADE_FILE)
GAMES_PATH = '/usr/games/'


def make_run_game_path(path):
    return os.path.join(path, 'run_game.py')


def make_preview_path(path):
    return os.path.join(path, 'preview.jpg')


class Game(Gtk.Image):
    game_path = None
    run_game_path = None
    preview_path = None
    last_click = None
    
    def __init__(self, game_path, *args, **kw):
        super(Gtk.Image, self).__init__(*args, **kw)
        self.window = self.get_root_window()
        self.game_path = game_path
        self.run_game_path = make_run_game_path(game_path)
        self.preview_path = make_preview_path(game_path)

    def name(self):
        camel_case_name = os.path.basename(self.game_path)
        name = []
        for c in camel_case_name:
            if c.isupper():
                name.append(' ')
            name.append(c)
        return ''.join(name).strip()

    def make_eventbox(self):
        box = Gtk.EventBox()
        box.add(self)
        box.connect('button-press-event', self.run)

        box.connect('enter-notify-event', self.on_mouse_over)
        box.connect('leave-notify-event', self.on_mouse_leave)
        box.set_tooltip_text(u'Clique para jogar %s' % self.name())
        return box

    def widget(self):
        self.box = self.make_eventbox()
        self.set_from_file(self.preview_path)
        self.show()
        return self.box

    def on_mouse_over(self, *args, **kwargs):
        cursor = Gdk.Cursor(Gdk.CursorType.HAND1)
        self.window.set_cursor(cursor)

    def on_mouse_leave(self, *args, **kwargs):
        cursor = Gdk.Cursor(Gdk.CursorType.ARROW)
        self.window.set_cursor(cursor)
    
    def run(self, widget, key, data=None):
        if (self.last_click is not None) and (datetime.now() - self.last_click < timedelta(seconds=4)):
            return

        self.last_click = datetime.now()

        if key.button == Gdk.BUTTON_PRIMARY:
            os.chdir(self.game_path)
            Popen(['/usr/bin/env', 'python', self.run_game_path])
    

class Main(object):
    games = None
    on_window_delete_event = Gtk.main_quit
    
    def __init__(self, builder):
        self.games = list()
        self.builder = builder
        self.load_games()
        self.scrolled_game_grid_viewport = builder.get_object('scrolled_game_grid_viewport')
        self.setup_game_grid(builder.get_object('game_grid'))
        self.setup_window(builder.get_object('main_window'))
        self.show_previews()

    def load_games(self):
        for path in glob('%s*' % GAMES_PATH):
            if self.is_game_folder(path):
                self.register_game(path)

    def setup_game_grid(self, grid):
        self.game_grid = grid
        lines = int(len(self.games) / 4)

        for line in range(lines):
            grid.insert_row(line)

    def setup_window(self, window):
        self.window = window
        # we need this mask so that eventbox captures mouse clicks
        self.window.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.window.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#ffffff'))
        self.window.fullscreen()

    def show_previews(self):
        grid = self.game_grid

        for i in range(len(self.games)):
            game = self.games[i]

            size = 4
            x, y = i%size, int(i/size)
            grid.attach(game.widget(), x, y, 1, 1)
    
    def register_game(self, path):
        self.games.append(Game(path))
    
    def is_game_folder(self, path):
        run_game_path = make_run_game_path(path)
        preview_path = make_preview_path(path)
        
        return os.path.exists(run_game_path) and os.path.exists(preview_path)
    
    def on_window_resize(self, window):
        grid = self.game_grid

    def on_window_key_press(self, widget, key, data=None):
        if key.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()

    def on_game_image_click(self, widget):
        widget.run()


def main():
    builder = Gtk.Builder()
    builder.add_from_file(GLADE_PATH)
    main = Main(builder)
    builder.connect_signals(main)

    main_window = builder.get_object('main_window')
    main_window.show_all()

    Gtk.main()