from __future__ import division

import math

from pyglet.gl import *
from pyglet import window, clock, app
from pyglet.window import key
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED

from vector import *
from vector import Vector as v

import actor
import cheat
import data
import enemy
import mode
import weapons
import world
import gamestate
import oxygen
import signpost
import sound
import caterpie
import spatialhash
from constants import *


def draw_circle(c, r):
    glBegin(GL_LINE_LOOP)
    for u in xrange(16):
        theta = u * math.pi/8
        glVertex2f(c[0] + r * math.cos(theta), c[1] + r * math.sin(theta))
    glEnd()
    
class GameMode(mode.Mode):
    name = 'game'
    
    barometer = data.load_image('hud/barometer.svgz', anchor_x='center')
    pipe = data.load_image('hud/pipe.svgz', anchor_x='center')
    pipe_sign = data.load_image('hud/pipesign.svgz', anchor_x='center')

    spools = [data.load_image('hud/spoolempty.svgz', anchor_x='center'),
                   data.load_image('hud/spoolone.svgz', anchor_x='center'),
                   data.load_image('hud/spooltwo.svgz', anchor_x='center'),
                   data.load_image('hud/spoolthree.svgz', anchor_x='center'),
                   data.load_image('hud/spoolfour.svgz', anchor_x='center'),
                   data.load_image('hud/spoolfive.svgz', anchor_x='center'),
                   data.load_image('hud/spoolsix.svgz', anchor_x='center'),
                   data.load_image('hud/spoolseven.svgz', anchor_x='center'),
                   data.load_image('hud/spooleight.svgz', anchor_x='center'),
                   ]

    countdowns = [data.load_image('hud/countdownone.svgz'),
                  data.load_image('hud/countdowntwo.svgz'),
                  data.load_image('hud/countdownthree.svgz'),
                  data.load_image('hud/countdownfour.svgz'),
                  data.load_image('hud/countdownfive.svgz'),]
    
    def __init__(self):
        self.is_set_up = False
    
    def set_up(self):
        gs = self.control.gamestate
        stage = gs.current_stage
        self.world = world.PlayableWorld(gs, stage)
        self.world.push_handlers(self)
        self.world.drag = 0.0001
        self.world.gravity = 0
        
        self.player = actor.Player(self.world)
        self.player.weapon = weapons.PeeweeGun()
        self.player.bearing = self.world.initial_oxygen.bearing
        self.player.old_bearing = self.player.bearing
        
        self.world.player = self.player
        
        self.camera_pos = self.player.pos
        self.camera_bearing = self.player.bearing
        self.camera_zoom = 1
        self.zoom_factor = 1
        
        self.score_display = caterpie.TextBox(
            xpos = 0.0,
            ypos = 0.0,
            width = 1.0,
            height = 1.0,
            halign = 'center',
            valign = 'bottom',
            outline = None,
            background = None,
            font_size = SCORE_FONT_SIZE,
            padding = SCORE_PADDING,
        )

        self.title = caterpie.TextBox(
            xpos = 0.0, ypos = 0.5,
            width = 1.0, height = 0.3,
            halign = "center", valign = "center",
            padding = MENU_PADDING,
            margin = MENU_MARGIN,
            font_size = MENU_FONT_SIZE,
            color = (255,255,255,255)
        )
        self.showing_title = True

        self.popup = caterpie.TextBox(
            xpos = 0.3, ypos = 0.3,
            width = 0.4, height = 0.4,
            halign = "center", valign = "center",
            padding = 0.02, font_size = 0.03,
            color = (255,255,255,255),
        )

        self.countdown = caterpie.ImageBox(
            xpos = 0.4, ypos = 0.75,
            width = 0.2, height = 0.2,
            outline = None,
            background = None,
            graphic = None,
        )
        self.current_countdown = None

        self.update_score()
        
        self.is_set_up = True
        self.ticking = False
        self.fade_level = 1
        self.target_fade = 1
        self.fade_callback = None

        self.show_oxygen_data = False

    def connect(self, control):
        self.control = control
        self.window = control.window
        self.camera_scale = self.window.height / float(SCREEN_HEIGHT)

        if DEBUG:
            self.cheat_controller = cheat.CheatController(self)
            self.window.push_handlers(self.cheat_controller)

        if not self.is_set_up:
            self.set_up()

        self.score_display.window = self.window
        self.title.window = self.window
        self.title.text = self.control.gamestate.current_level_name
        if self.world.goal:
            self.title.text += '\n\nGoal: ' + self.world.goal.name
        self.popup.window = self.window
        self.countdown.window = self.window
        self.update_countdown(False)

        self.fade_in(self.start_ticking)
        
    def disconnect(self):
        if DEBUG:
            self.window.remove_handlers(self.cheat_controller)
        self.window = None
        self.control = None
        
    def inv_camera_transform(self, screen_loc):
        return (v(screen_loc) - (self.window.width * 0.5, self.window.height * 0.2)).rotated(self.camera_bearing) / (self.camera_scale * self.camera_zoom) + self.camera_pos
        
    def screen_bb(self):
        pts = [self.inv_camera_transform(x) for x in [(0,0), (0, self.window.height), (self.window.width, 0), (self.window.width, self.window.height)]]
        return BoundingBox(*pts)
        
    def on_draw(self):
        self.window.clear()
        
        glPushMatrix()
        glTranslatef(self.window.width * 0.5, self.window.height * 0.2, 0)
        glRotatef(-self.camera_bearing, 0, 0, 1)
        self.world.background.draw(0, 0, radius=(.5*self.window.width + .8*self.window.height))
        s = self.camera_scale * self.camera_zoom
        glScalef(s, s, s)
        glTranslatef(-self.camera_pos.x, -self.camera_pos.y, 0)

        bb = self.screen_bb()

        for d in self.world.door_hash.in_box(bb):
            d.draw()
        self.world.world_graphics.draw(bb)
#            draw_circle(obj.pos, obj.radius)
        
        for a in sorted(self.world.active.in_box(bb), key=lambda x: x.z):
            a.draw()

        glLineWidth(3)
        glColor3f(1,1,1)
        glBegin(GL_LINE_STRIP)
        for pt in self.player.pipe:
            glVertex2f(*pt)
        glVertex2f(*self.player.pos)
        glEnd()
        glLineWidth(1)

        self.player.draw()

        
        glPopMatrix()
        self.score_display.draw()

        # Draw pipe meter.
        sw, sh = self.window.get_size()
        scale = sh * .9 / self.barometer.height
        p_level = 1 - self.player.pipe_used/self.player.pipe_length
        glPushMatrix()
        glTranslatef(sw * .1, sh * .05, 0)
        glScalef(scale, scale, scale)
        glEnable(GL_SCISSOR_TEST)
        glScissor(0, int(sh * .05 + 64 * scale), sw, int(sh * .9))
        self.pipe.draw(0, 64 -p_level * self.pipe.height)
        glDisable(GL_SCISSOR_TEST)
        self.spools[min(int(p_level * len(self.spools)), len(self.spools) - 1)].draw(0, -16)
        self.pipe_sign.draw(0, 448)
        glPopMatrix()
        
        b_level = self.player.oxygen.contained/self.player.oxygen.capacity
        glPushMatrix()
        glTranslatef(sw * .9, sh * .05, 0)
        glScalef(scale, scale, scale)
        glColor3f(1, 0, 0)
        glBegin(GL_QUADS)
        glVertex2f(-16, 32)
        glVertex2f(16, 32)
        glVertex2f(16, b_level * 384 + 64)
        glVertex2f(-16, b_level * 384 + 64)
        glEnd()
        self.barometer.draw(0, 0)
        glPopMatrix()
                              
        if self.fade_level:
            glColor4f(0, 0, 0, self.fade_level)
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(self.window.width, 0)
            glVertex2f(self.window.width, self.window.height)
            glVertex2f(0, self.window.height)
            glEnd()
        
        if self.showing_title:
            self.title.draw()
            if self.world.goal:
                self.world.goal.image.draw(self.window.width * .5, self.window.height * .3, radius=self.world.goal.radius* self.window.height/SCREEN_HEIGHT)
        if self.popup.text:
            self.popup.draw()

        if self.countdown.graphic is not None:
            self.countdown.draw()

            
    def fade_in(self, callback):
        self.target_fade = 0
        self.fade_rate = GAME_FADEIN_RATE
        self.fade_callback = callback
        
    def fade_out(self, callback):
        self.target_fade = 1
        self.fade_rate = GAME_FADEOUT_RATE
        self.fade_callback = callback
        self.control.music.stop_song(1.0)
        
    def start_ticking(self):
        self.ticking = True
        self.showing_title = False

    def tick(self):
        self.fade_level += self.fade_rate * (1 if self.target_fade > self.fade_level else -1)
        if self.fade_callback and abs(self.fade_level - self.target_fade) < self.fade_rate:
            self.fade_level = self.target_fade
            fc = self.fade_callback
            self.fade_callback = None
            if isinstance(fc, tuple):
                fc[0](*fc[1:])
            else:
                fc()
            if self.control is None:
                self.ticking = False
            
        if self.ticking:
            self.update_controls()
    
            self.player.apply_impulse((0, -self.world.gravity))
            self.player.tick()
            
            thinkers = []
            actives = [a for a in self.world.active]
            for a in actives:
                self.world.active.remove(a)
                a.apply_impulse((0, -self.world.gravity))
                a.tick()
                if not a.dead:
                    self.world.active.add(a)
                    if isinstance(a, enemy.Enemy) and not a.stunned:
                        thinkers.append(a)
                                    
            self.world.active.update(self.world.new_active)
            self.world.new_active = set()
            
            for t in thinkers:
                t.think()
            
            self.update_camera()
            self.update_pipe()
            self.update_oxygen()
            self.update_popup()
            self.update_countdown()

    def update_countdown(self, beep=True):
        c = self.player.oxygen.contained
        cd = int(math.ceil(c / TICK_RATE))
        if 1 <= cd <= 5:
            if cd != self.current_countdown and beep:
                sound.beep()
            self.countdown.graphic = self.countdowns[cd-1]
            self.current_countdown = cd
        else:
            self.current_countdown = None
            self.countdown.graphic = None

    def update_popup(self):
        found_oxy = False
        if not self.show_oxygen_data:
            if self.player.oxygen not in self.player.colliders():
                self.show_oxygen_data = True
        txt = ''
        for c in self.player.colliders():
            if isinstance(c, signpost.Signpost):
                txt = c.text
                break
            if isinstance(c, oxygen.Oxygen) and self.show_oxygen_data:
                capacity = max(0, c.capacity)
                contained = max(0, min(100, 100 * c.contained / c.capacity))
                pipe_length = max(0, c.pipe_length // 100)
                text = u"Oxygen: %d ml at %d%%\nPipe length: %d m" % \
                        (capacity, contained, pipe_length)
                txt = text
                found_oxy = True
        self.popup.text = txt

    def update_camera(self):
        self.camera_pos += (self.player.pos - self.camera_pos) * 0.2
        self.camera_bearing += (self.player.bearing - self.camera_bearing) * 0.2
        self.camera_zoom += (self.zoom_factor - self.camera_zoom) * 0.1
    
    def update_score(self):
        self.score_display.text = "Swag: $%d" % (self.world.state.level_score,)
    
    def update_pipe(self):
        pass
   
    def update_oxygen(self):
        pass

    def update_controls(self):
        def control_state(neg_key, pos_key, magnitude):
            res = 0
            if self.control.keys[neg_key]: res -= magnitude
            if self.control.keys[pos_key]: res += magnitude
            return res
            
        self.player.rotation = control_state(key.RIGHT, key.LEFT, PLAYER_ROTATION)
        self.player.thrust = control_state(key.Q, key.W, PLAYER_THRUST)
        self.player.lift = control_state(key.DOWN, key.UP, PLAYER_LIFT)
        
        self.player.firing = self.control.keys[key.SPACE]
        
    def on_key_press(self, sym, modifiers):
        if DEBUG and sym == key.Z:
            self.zoom_factor = .1
        elif sym in (key.LCTRL, key.RCTRL):
            self.player.attempt_connect()
            self.update_countdown(False)
        elif sym == key.ESCAPE:
            self.fade_out((self.control.switch_handler, "menu"))
        else:
            return EVENT_UNHANDLED
        return EVENT_HANDLED
    def on_key_release(self, sym, modifiers):
        if sym == key.Z:
            self.zoom_factor = 1

    def on_shoot(self):
        sound.shoot()
    
    def on_get_swag(self, swag):
        self.world.state.score_swag(swag)
        self.update_score()
        sound.pickup()

    def on_finish_level(self):
        self.control.gamestate.win_level()
        self.ticking = False
        self.fade_out(self.leave_game)
        
    def leave_game(self):
        self.control.switch_handler('menu', 'victory')
    
    def on_suffocate(self):
        self.ticking = False
        self.fade_out((self.control.gamestate.fail_level, self.control))
        self.fade_rate = DEATH_FADEOUT_RATE
        sound.wahwah()
