# Funny intro for fluffy menace
# by Fydo

# yes, this could probably be coded better.. but ... it's pyweek ;)

# bunny fade in
# Menace falls till y= 260
# fluffy falls till y = 225 , menace switches to menace2 (bonk!)
# credits fade in

import pygame
from pygame.locals import *
from OpenGL.GL import *

import data
import textures

class Intro:
    def __init__(self): 
    
        self.smash1 = pygame.mixer.Sound(data.filepath('smash1.ogg', 'sfx'))
        self.smash1played = False
        self.smash2 = pygame.mixer.Sound(data.filepath('smash2.ogg', 'sfx'))
        self.smash2played = False
        self.boing = pygame.mixer.Sound(data.filepath('jump.ogg', 'sfx'))
        self.numboings = 0
        self.boingsplayed = 0
    
        self.menaceloc = (275, 100)
        self.menacerot = False
        self.fluffyloc = (245, 100)
        self.bunnyloc = (160, 240)
        self.creditsalpha = 0
        self.alldone = False
        self.fadeincredits = False
        self.fadeouttime = False
        self.running = 0

        texture = textures.Texture(data.filepath('logo.png'))
        self.menace = texture.sub(214, 128-56, 512-214, 56)
        self.fluffy = texture.sub(77, 128-80, 202-77, 80-24)
        self.credits1 = texture.sub(60, 0, 238-60, 28)
        self.credits2 = texture.sub(238, 0, 512-238, 128-68)
        self.bunny = texture.sub(0, 128-95, 48, 95)
        
        #self.music = pygame.mixer.Sound(os.path.join('data', 'intro.ogg'))

    def figurelocations(self, dt):
        if self.menaceloc[1] < 275:
            self.menaceloc = (275, self.menaceloc[1] + (0.3 * dt))
        else:
            if self.smash1played == False:
                self.smash1.play()
                self.smash1played = True
                
            self.menaceloc = (275, 275)
            if self.fluffyloc[1] < 235:
                self.fluffyloc = (245, self.fluffyloc[1] + (0.4 * dt))
            else:
                if self.smash2played == False:
                    self.smash2.play()
                    self.smash2played = True
                
                self.menacerot = True
                self.fluffyloc = (245, 235)
                self.fadeincredits = True
                if self.numboings == 0 and (self.creditsalpha / 8.0) >= 60:
                    if self.boingsplayed == 0:
                        self.boingsplayed += 1
                        self.boing.play()
                    if self.bunnyloc[1] > 220:
                        self.bunnyloc = (self.bunnyloc[0], self.bunnyloc[1] - (0.35 * dt))
                    else:
                        self.numboings += 1
                
                if self.numboings == 1:
                    if self.bunnyloc[1] < 240:
                        self.bunnyloc = (self.bunnyloc[0], self.bunnyloc[1] + (0.2 * dt))
                    else:
                        self.numboings += 1
                        
                if self.numboings == 2 and (self.creditsalpha / 8.0) >= 100:
                    if self.boingsplayed == 1:
                        self.boingsplayed += 1
                        self.boing.play()
                    if self.bunnyloc[1] > 220:
                        self.bunnyloc = (self.bunnyloc[0], self.bunnyloc[1] - (0.35 * dt))
                    else:
                        self.numboings += 1
                
                if self.numboings == 3:
                    if self.bunnyloc[1] < 240:
                        self.bunnyloc = (self.bunnyloc[0], self.bunnyloc[1] + (0.2 * dt))
                    else:
                        self.numboings += 1
                
                    
    def run(self):
        clock = pygame.time.Clock()

        glClearColor(0, 0, 0, 1)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        while not self.alldone:

            for e in pygame.event.get():
                if e.type == QUIT: sys.exit()
                if e.type != KEYDOWN: continue
                elif e.key == K_ESCAPE: return
                elif e.key == K_SPACE: return

            glClear(GL_COLOR_BUFFER_BIT)

            dt = clock.tick(60)
            self.figurelocations(dt)

            glColor(1, 1, 1, 1)
            glBegin(GL_QUADS)
            glVertex2f(0, 568)
            glVertex2f(1024, 568)
            glVertex2f(1024, 408)
            glVertex2f(0, 408)
            glEnd()

            glPushMatrix()
            x, y = self.bunnyloc
            glTranslatef(x, 768-y - self.bunny.h, 0)
            self.bunny.render()
            glPopMatrix()

            glPushMatrix()
            x, y = self.fluffyloc
            glTranslatef(x, 768-y - self.fluffy.h, 0)
            self.fluffy.render()
            glPopMatrix()
            
            glPushMatrix()
            x, y = self.menaceloc
            glTranslatef(x, 768-y - self.menace.h, 0)
            if self.menacerot:
                glTranslatef(0, -22, 0)
                glRotate(5, 0, 0, 1)
            self.menace.render()
            glPopMatrix()
            
            if self.fadeincredits == True:
                glColor(1, 1, 1, (self.creditsalpha) / (8.0 * 256))
                self.creditsalpha += (dt * 2)
                glPushMatrix()
                x, y = (590, 390)
                glTranslatef(x + 48, 768-y - self.credits1.h, 0)
                self.credits1.render()
                glTranslatef(-48, -128+68, 0)
                self.credits2.render()
                glPopMatrix()

            if self.fadeouttime == True and self.running != 1:
                glColor(0, 0, 0, self.running)
                glEnable(GL_BLEND)
                glBegin(GL_QUADS)
                glVertex2f(0, 0)
                glVertex2f(1024, 0)
                glVertex2f(1024, 768)
                glVertex2f(0, 768)
                glEnd()
                glDisable(GL_BLEND)
                self.running += .025
                
            if self.fadeouttime == True and self.running >= 1:
                self.alldone = True
                
            pygame.display.flip()
            
            
            if (self.creditsalpha / 8.0) >= 255:
                if self.fadeouttime == False:
                    pygame.time.wait(600) 
                    self.fadeouttime = True
                    
        pygame.time.wait(100) 

