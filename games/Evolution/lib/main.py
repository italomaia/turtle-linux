'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "lib"
directory.
'''

import sys

from OpenGL.GL import *
import pygame
from pygame.locals import *

from euclid import *

import logo
import data
import map
import player
import textures
import items
import menu

MUSIC_END = USEREVENT + 1

def main():
    pygame.mixer.pre_init(44100,-16,2, 1024 * 3)
    pygame.init()
    pygame.mixer.init()
    Game().run()

class Game:
        
    def run(self):

        self.vw, self.vh = viewport = (1024, 768)
        if '-win' in sys.argv:
            flags = OPENGL | DOUBLEBUF
        else:
            flags = OPENGL | DOUBLEBUF | FULLSCREEN
        pygame.display.gl_set_attribute(GL_STENCIL_SIZE, 8)
        screen = pygame.display.set_mode(viewport, flags)
        pygame.mouse.set_visible(False)
        clock = pygame.time.Clock()

        # set up 2d mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, self.vw, self.vh)
        glOrtho(0, self.vw, 0, self.vh, -50, 50)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)

        # for smooth lines
        glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)

        # for bez maps
        glEnable(GL_MAP2_VERTEX_3)

        # INTRO
        if '-nointro' not in sys.argv:
            i = logo.Intro()
            pygame.time.wait(200) 
            i.run()
            pygame.event.clear(KEYDOWN)
        
        # MENU
        while 1:

            mainMenu = menu.Menu()
            result = mainMenu.run()
            
            if result == True:
                return
            
            del mainMenu
            pygame.event.clear(KEYDOWN)
    
            if '-nomusic' not in sys.argv:
                pygame.mixer.music.fadeout(1000)
                try:
                    pygame.mixer.music.load(data.filepath('justdreamy.ogg'))
                except pygame.error:
                    pass
                else:
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_endevent(MUSIC_END)

            self.map = map.Map('one')
            glClearColor(202/255., 1., 1., 1.)

            self.player = player.Player(self.map.player_start)

            k_up = k_down = k_left = k_right = 0

            running = n = 0
            fx, fy = self.player.x, self.player.y

            playing = True
            show_radar = False
            debug = step = False
            
            #timemachinesound = pygame.mixer.Sound(data.filepath('timemachine2.ogg', 'sfx'))
            #timemachinesound.play()
            
            while playing == True:
                dt = clock.tick(60)
                #if not n % 100: print 'FPS:', clock.get_fps()
                #n += 1

                # sanity limit due to dodgy clock startup
                if dt > 33: dt = 33

                for e in pygame.event.get():
                    if e.type == QUIT: sys.exit()
                    if e.type == MUSIC_END:
                        pygame.mixer.music.play()
                    if e.type not in (KEYDOWN, KEYUP): continue
                    down = e.type == KEYDOWN     # key down or up?
                    if e.key == K_RIGHT: k_right = down
                    elif e.key == K_LEFT: k_left = down
                    elif e.key == K_UP: k_up = down
                    elif e.key == K_DOWN: k_down = down
                    elif e.key == K_SPACE: show_radar = down
                    elif e.key == K_d and down: debug = not debug
                    elif e.key == K_s: step = down
                    elif e.key == K_ESCAPE and down:
                        playing = False     # quit the game

                f = Point2(fx, fy)
                p = Point2(self.player.x, self.player.y)
                if self.player.isGroundMode():
                    p.y += self.vh/4
                v = p - f
                fx, fy = f + v/8
                self.tx, self.ty = self.map.focus(fx, fy, self.vw, self.vh)

                glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

                glPushMatrix()
                glTranslatef(-self.tx, -self.ty, 0)

                self.map.animate(dt)

                # need map in stencil buffer so we render it before we animate
                # the player
                onscreen_items = self.map.render(self.tx, self.ty,
                    self.vw, self.vh, debug)

                if running != 1 and (not debug or step):
                    self.player.run(self, dt, k_left, k_right, k_up, k_down)
                    self.player.hitItems(self, onscreen_items, dt)

                if self.player.isInCave(self.map):
                    self.player.renderLight(self.tx, self.ty, self.vw, self.vh)

                self.player.render(debug)

                if show_radar:
                    self.player.renderRadar(self)

                glPopMatrix()

                self.player.renderHUD(self)

                if running != 1:
                    glColor(0, 0, 0, 1-running)
                    glEnable(GL_BLEND)
                    glBegin(GL_QUADS)
                    glVertex2f(0, 0)
                    glVertex2f(self.vw, 0)
                    glVertex2f(self.vw, self.vh)
                    glVertex2f(0, self.vh)
                    glEnd()
                    glDisable(GL_BLEND)
                    running += .01

                pygame.display.flip()
                
                if len(self.player.components) == items.NUM_COMPONENTS:
                    self.runFinalScreen(True)
                    playing = False
                elif not self.player.health:
                    self.runFinalScreen(False)
                    playing = False

            self.map.destroy()


    def runFinalScreen(self, won):
        pygame.mixer.music.fadeout(300)
    
        if won:
            texture = textures.Texture(data.filepath('youwon.png'))
            sound = pygame.mixer.Sound(data.filepath('funfair.ogg'))
        else:
            texture = textures.Texture(data.filepath('youfailed.png'))
            sound = pygame.mixer.Sound(data.filepath('ohnoes.ogg'))
        
        done = False
        glClearColor(0, 0, 0, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
        clock = pygame.time.Clock()
        sound.play()
        elapsed = 0

        while not done:
            
            for e in pygame.event.get():
                if e.type == QUIT: sys.exit()
                if e.type != KEYDOWN: continue
                elif e.key == K_ESCAPE:
                    done = True
                    
            glClear(GL_COLOR_BUFFER_BIT)
            dt = clock.tick(60)
            
            if elapsed < 1.0:
                glColor(1, 1, 1, elapsed)
            elif elapsed > 5:
                glColor(1, 1, 1, ((8 - elapsed) / 3.0))
            else:
                glColor(1, 1, 1, 1)
                
            glPushMatrix()
            glTranslatef(0, 100, 0)
            texture.render()
            glPopMatrix()
            pygame.display.flip()
            
            if elapsed > 8:
                done = True
                
            elapsed += (dt / 1000.0)

