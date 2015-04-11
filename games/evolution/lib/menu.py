#main menu

import pygame, sys
from pygame.locals import *
from OpenGL.GL import *

import data
import textures
import story

class Menu:
    def __init__(self): 
    
        self.menumove = pygame.mixer.Sound(data.filepath('menumove.ogg', 'sfx'))
        self.menuselect = pygame.mixer.Sound(data.filepath('menuselect.ogg', 'sfx'))

        texture = textures.Texture(data.filepath('menu.png'))
        self.menubg = texture#.sub(0, 256, 1024, 768)
        self.loadingscreen = texture.sub(0, 0, 1024, 70)
        self.starguy = textures.TextureGrid(data.filepath('starguy.png'), 64, 64).row(0)
        self.spinspeed = 25
        
        self.bg = textures.Texture(data.filepath('menu-back.png'))
        self.bgoffset = 0
        self.movingup = True
        self.fadein = True
        
        #self.music = pygame.mixer.Sound(os.path.join('data', 'intro.ogg'))

    def figurestuff(self, dt):
        self.starframecount += dt
        if self.starframecount > self.spinspeed:
            self.starframecount = 0
            self.starframe += 1
            if self.starframe == 16:
                self.starframe = 0
        if self.movingup == True:        
            if self.bgoffset < 83:
                self.bgoffset += (dt * 0.004)
            else:
                self.movingup = False
        else:
            if self.bgoffset > 1:
                self.bgoffset -= (dt * 0.004)
            else:
                self.movingup = True
                    
    def initstuff(self):
        self.alldone = False
        self.cursorplace = 0
        self.starframe = 0
        self.starframecount = 0.00
        self.fadeouttime = False
        self.running = 0
        self.bgoffset = 0
        self.spinspeed = 25
        self.fadein = True
    
    def run(self):
        clock = pygame.time.Clock()
        self.initstuff()
    
        if '-nomusic' not in sys.argv:
            try:
                pygame.mixer.music.load(data.filepath('tripper.ogg'))
            except pygame.error:
                pass
            else:
                pygame.mixer.music.play()
    
        glClearColor(0, 0, 0, 1)
        
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        while not self.alldone:
            for e in pygame.event.get():
                if e.type == QUIT: sys.exit()
                if e.type != KEYDOWN: continue
                elif e.key == K_ESCAPE: 
                    self.fadeouttime = True
                    self.cursorplace = 2
                    self.spinspeed = 0
                elif e.key == K_UP or e.key == K_LEFT:
                    self.menumove.play()
                    self.cursorplace -= 1
                    if self.cursorplace < 0:
                        self.cursorplace = 2 #wrap over
                elif e.key == K_DOWN or e.key == K_RIGHT:
                    self.menumove.play()
                    self.cursorplace += 1
                    if self.cursorplace > 2:
                        self.cursorplace = 0 #wrap over
                elif e.key == K_SPACE or e.key == K_RETURN:
                    self.spinspeed = 0
                    self.menuselect.play()
                    self.fadeouttime = True

            glClear(GL_COLOR_BUFFER_BIT)

            dt = clock.tick(60)
            self.figurestuff(dt)
            
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glPushMatrix()
            #x, y = (0, 0)
            glTranslatef(0, 256 + self.bgoffset, 0)
            self.bg.render()
            glPopMatrix()
            
            glPushMatrix()
            #x, y = (0, 0)
            glTranslatef(0, -256, 0)
            self.menubg.render()
            glPopMatrix()
            glDisable(GL_BLEND)
            
            glPushMatrix()
            x, y = (646, 347 + (90 * self.cursorplace))
            glTranslatef(x, 768-y - 64, 0)
            self.starguy.render(self.starframe)
            glPopMatrix()
            
            if self.fadeouttime == True and self.running >= 1:
                self.alldone = True
                
                if self.cursorplace != 2:
                    #pygame.display.flip()
                    glClear(GL_COLOR_BUFFER_BIT)
                    glPushMatrix()
                    x, y = (0, 349)
                    glTranslatef(x, 768-y, 0)
                    self.loadingscreen.render()
                    glPopMatrix()
                    if self.cursorplace == 1:
                        timemachinesound = pygame.mixer.Sound(data.filepath('timemachine2.ogg', 'sfx'))
                        timemachinesound.play()
                else:
                    return True
            
            if self.fadein == True:
                glColor(0, 0, 0, 1-self.running)
                glEnable(GL_BLEND)
                glBegin(GL_QUADS)
                glVertex2f(0, 0)
                glVertex2f(1024, 0)
                glVertex2f(1024, 768)
                glVertex2f(0, 768)
                glEnd()
                glDisable(GL_BLEND)
                glColor(1, 1, 1, 1)
                self.running += .02
                if self.running >= 1:
                    self.running = 0
                    self.fadein = False
            
            if self.fadeouttime == True and self.running < 1:
                glColor(0, 0, 0, self.running)
                glEnable(GL_BLEND)
                glBegin(GL_QUADS)
                glVertex2f(0, 0)
                glVertex2f(1024, 0)
                glVertex2f(1024, 768)
                glVertex2f(0, 768)
                glEnd()
                glDisable(GL_BLEND)
                glColor(1, 1, 1, 1)
                self.running += .04
                
            pygame.display.flip()
            
            if self.alldone == True and self.cursorplace == 0:
                pygame.mixer.music.fadeout(1000)
                #play cutscene stuff
                thestory = story.Story()
                thestory.run()
                del thestory
                pygame.mixer.stop()
                self.initstuff() #don't exit yet! tee hee
                try:
                    pygame.mixer.music.load(data.filepath('tripper.ogg'))
                    pygame.mixer.music.play()
                except:
                    pass
                    
        #pygame.time.wait(100)
        return False
