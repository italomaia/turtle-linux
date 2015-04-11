#the  big cutscene thingy
# by fydo

# yeah, this is a big mess, but i haven't got time to clean it up now ;)

import pygame, sys
from pygame.locals import *
from OpenGL.GL import *

import data
import textures

class Story:
    def __init__(self): 
        self.exit = False
        self.fadetonextscene = False
        self.cuttonextscene = False
        self.fadein = True
        
        self.voiceover1 = pygame.mixer.Sound(data.filepath('intro-danger.ogg', 'sfx'))
        self.voiceover1played = False
        self.voiceover2 = pygame.mixer.Sound(data.filepath('intro-scientist-plan.ogg', 'sfx'))
        self.voiceover2played = False
        self.voiceover3 = pygame.mixer.Sound(data.filepath('intro-scientist-needhelp.ogg', 'sfx'))
        self.voiceover3played = False
        self.voiceover4 = pygame.mixer.Sound(data.filepath('intro-scientist-items.ogg', 'sfx'))
        self.voiceover4played = False
        self.voiceover5 = pygame.mixer.Sound(data.filepath('intro-scientist-problem.ogg', 'sfx'))
        self.voiceover5played = False
        self.voiceover6 = pygame.mixer.Sound(data.filepath('intro-scientist-timemachine.ogg', 'sfx'))
        self.voiceover6played = False
        self.voiceover7 = pygame.mixer.Sound(data.filepath('intro-scientist-warn.ogg', 'sfx'))
        self.voiceover7played = False
        self.voiceover8 = pygame.mixer.Sound(data.filepath('timemachine2.ogg', 'sfx'))
        self.voiceover8played = False
        
        self.sndexplode = pygame.mixer.Sound(data.filepath('explode.ogg', 'sfx'))

        texture = textures.Texture(data.filepath('scene1.png'))
        self.scene = 1
        self.scene1bg = texture.sub(0, 212, 1024, 300)
        self.earth = texture.sub(0, 0, 217, 212)
        self.earthoffset = -5
        self.explode = texture.sub(219, 0, 650, 212)
        self.showexplode = False
        
        texture2 = textures.Texture(data.filepath('scene2.png'))
        self.scene2bg = texture2.sub(0, 724, 1024, 300)
        self.prof = texture2.sub(0, 424, 306, 300)
        self.profoffset = 0
        self.profhand1 = texture2.sub(812, 424, 210, 300)
        self.profback = texture2.sub(0, 124, 455, 300)
        self.monitor = texture2.sub(460, 124, 560, 300)
        self.wall = texture2.sub(308, 424, 477, 300)
        self.walloffset = 0
        
        texture3 = textures.Texture(data.filepath('scene3.png'))
        self.scene3bg = texture3.sub(0, 724, 1024, 300)
        self.scene4bg = texture3.sub(0, 318, 1024, 405)
        self.closeup = texture3.sub(0, 18, 540, 300)
        self.sceneoffset = 0
        
        texture4 = textures.Texture(data.filepath('subtitles.png'))
        self.subtitle1 = texture4.sub(0, 482, 512, 30)
        self.subtitle1show = False
        self.subtitle2 = texture4.sub(0, 452, 512, 30)
        self.subtitle2show = False
        self.subtitle3 = texture4.sub(0, 422, 512, 30)
        self.subtitle3show = False
        self.subtitle4 = texture4.sub(0, 392, 512, 30)
        self.subtitle4show = False
        self.subtitle5 = texture4.sub(0, 362, 512, 30)
        self.subtitle5show = False
        self.subtitle6 = texture4.sub(0, 302, 512, 60)
        self.subtitle6show = False
        self.subtitle7 = texture4.sub(0, 212, 512, 90)
        self.subtitle7show = False
        self.subtitle8 = texture4.sub(0, 182, 512, 30)
        self.subtitle8show = False
        self.subtitle9 = texture4.sub(0, 152, 512, 30)
        self.subtitle9show = False
        self.subtitle10 = texture4.sub(0, 122, 512, 30)
        self.subtitle10show = False
        self.subtitle11 = texture4.sub(0, 62, 512, 60)
        self.subtitle11show = False
        self.subtitle12 = texture4.sub(0, 0, 512, 62)
        self.subtitle12show = False
        
        #self.starguy = textures.TextureGrid(data.filepath('starguy.png'), 64, 64).row(0)
        
        #self.music = pygame.mixer.Sound(os.path.join('data', 'intro.ogg'))
        
    def subtitlefun(self):
        glPushMatrix()
        x, y = (256, 560)
        glTranslatef(x, 768-y, 0)
               
        if self.subtitle1show == True:
            self.subtitle1.render()
        elif self.subtitle2show == True:
            self.subtitle2.render()
        elif self.subtitle3show == True:
            self.subtitle3.render()
        elif self.subtitle4show == True:
            self.subtitle4.render()
        elif self.subtitle5show == True:
            self.subtitle5.render()
        elif self.subtitle6show == True:
            glTranslatef(0, -30, 0)
            self.subtitle6.render()
        elif self.subtitle7show == True:
            glTranslatef(0, -60, 0)
            self.subtitle7.render()
        elif self.subtitle8show == True:
            self.subtitle8.render()
        elif self.subtitle9show == True:
            self.subtitle9.render()
        elif self.subtitle10show == True:
            self.subtitle10.render()
        elif self.subtitle11show == True:
            glTranslatef(0, -30, 0)
            self.subtitle11.render()
        elif self.subtitle12show == True:
            glTranslatef(0, 120, 0)
            self.subtitle12.render()
            
        glPopMatrix()
        
    def figurestuff(self, dt):
        if self.scene == 1:
            self.earthoffset -= (0.01 * dt)
            if self.earthoffset < -10 and self.voiceover1played == False:
                self.voiceover1played = True
                self.subtitle1show = True
                self.voiceover1.play()
            if self.earthoffset < -40 and self.showexplode == False:
                self.sndexplode.play()
                self.showexplode = True
            if self.earthoffset < -60:
                self.fadetonextscene = True
                #self.exit = True
        elif self.scene == 2:
            self.profoffset -= (0.008 * dt)
            self.walloffset += (0.0022 * dt)
            if self.profoffset < -4 and self.voiceover2played == False:
                self.voiceover2played = True
                self.subtitle2show = True
                self.voiceover2.play()
            if self.profoffset < -27 and self.voiceover3played == False:
                self.voiceover3played = True
                self.subtitle2show = False
                self.subtitle3show = True
                self.voiceover3.play()
            if self.profoffset < -63:
                self.fadetonextscene = True
                #self.exit = True
        elif self.scene == 3:
            self.profoffset -= (0.018 * dt)
            self.walloffset += (0.008 * dt)
            if self.profoffset < -5 and self.voiceover4played == False: 
                self.voiceover4played = True
                self.subtitle4show = True
                self.voiceover4.play()
            if self.profoffset < -40 and self.voiceover5played == False:
                self.voiceover5played = True
                self.subtitle4show = False
                self.subtitle5show = True
                self.voiceover5.play()
            if self.profoffset < -90:
                self.subtitle5show = False
                self.subtitle6show = True
            if self.profoffset < -188:
                #self.exit = True
                self.fadetonextscene = True
        elif self.scene == 4:
            self.sceneoffset += (0.0175 * dt) #oh so precise!
            if self.sceneoffset > 4 and self.voiceover6played == False: 
                self.voiceover6played = True
                self.subtitle7show = True
                self.voiceover6.play()
                
            if self.sceneoffset > 75:
                #self.exit = True
                self.fadetonextscene = True
        elif self.scene == 5:
            self.earthoffset -= (0.01 * dt)
            if self.earthoffset < -2.5:
                self.subtitle8show = True
            if self.earthoffset < -45:
                self.fadetonextscene = True
        elif self.scene == 6:
            self.profoffset -= (0.008 * dt)
            if self.profoffset < -2 and self.voiceover7played == False:
                self.voiceover7played = True
                self.subtitle9show = True
                self.voiceover7.play()
            if self.profoffset < -10:
                self.cuttonextscene = True
        elif self.scene == 7:
            if self.profoffset == 0:
                self.voiceover8.play()
            self.profoffset += (0.008 * dt)
            if self.profoffset > 2 and self.voiceover8played == False:
                pygame.mixer.music.set_volume(0.1)
                #self.voiceover8played = True
                self.subtitle10show = True
                #if self.profoffset % 4 < 0.1 :
                    #self.voiceover8.play()
            
            if self.profoffset > 18:
                pygame.mixer.music.set_volume(0.5)
                self.cuttonextscene = True
                
        elif self.scene == 8:
            self.profoffset += (0.008 * dt)
            if self.profoffset > 18:
                self.fadetonextscene = True
                
        elif self.scene == 9:
            self.profoffset += (0.006 * dt)
            
            if self.profoffset > 2:
                self.subtitle11show = True
            
            if self.profoffset > 8:
                self.showcloseup = True
                
            if self.profoffset > 26:
                self.fadetonextscene = True
                
        elif self.scene == 10:
            self.subtitle12show = True
            self.profoffset += (0.008 * dt)
            
            if self.profoffset > 45:
                self.fadetonextscene = True
            
        
        
    def setfornextscene(self):
        self.profoffset = 0
        self.earthoffset = 0
        
        self.subtitle1show = False
        self.subtitle2show = False
        self.subtitle3show = False
        self.subtitle4show = False
        self.subtitle5show = False
        self.subtitle6show = False
        self.subtitle7show = False
        self.subtitle8show = False
        self.subtitle9show = False
        self.subtitle10show = False
        self.subtitle11show = False
        self.subtitle12show = False
        
        self.scene += 1
        self.running = 0
        if self.scene == 11:
            self.exit = True
                
    def run(self):
    
        if '-nomusic' not in sys.argv:
            try:
                pygame.mixer.music.load(data.filepath('intro.ogg'))
            except pygame.error:
                pass
            else:
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()
    
        clock = pygame.time.Clock()
        self.running = 0
        
        glClearColor(0, 0, 0, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        while 1:

            for e in pygame.event.get():
                if e.type == QUIT: sys.exit()
                if e.type != KEYDOWN: continue
                else: 
                    self.exit = True

            glClear(GL_COLOR_BUFFER_BIT)
            
            dt = clock.tick(60)
            self.figurestuff(dt)
            
            glPushMatrix()
            #x, y = (0, 0)
            glTranslatef(0, 300, 0)
            if self.scene == 1 or self.scene == 5:
                self.scene1bg.render()
            elif self.scene == 2 or self.scene == 6 or self.scene == 8:
                self.scene2bg.render()
            elif self.scene == 3:
                self.scene3bg.render()
            elif self.scene == 4:
                glTranslatef(0, -100, 0)
                glTranslatef(0, self.sceneoffset, 0)
                self.scene4bg.render()
            elif self.scene == 7 or self.scene == 9:
                self.scene4bg.render()
            glPopMatrix()

            if self.scene == 1:
                glEnable(GL_BLEND)
                glPushMatrix()
                x, y = (350 + self.earthoffset, 450)
                glTranslatef(x, 768-y, 0)
                self.earth.render()
                glPopMatrix()
                glDisable(GL_BLEND)
                if self.showexplode == True:
                    glPushMatrix()
                    x, y = (150 + self.earthoffset, 320)
                    glTranslatef(x, 768-y, 0)
                    self.explode.render()
                    glPopMatrix()
                    
            elif self.scene == 2:
                glPushMatrix()
                x, y = (200 + self.profoffset, 168)
                glTranslatef(x, 768-y-300, 0)
                self.prof.render()
                glPopMatrix()
                
                glPushMatrix()
                x, y = (550 + self.walloffset, 168)
                glTranslatef(x, 768-y-300, 0)
                self.wall.render()
                glPopMatrix()
                
                if self.voiceover3played == True:
                    glPushMatrix()
                    x, y = (530 + self.profoffset, 168)
                    glTranslatef(x, 768-y-300, 0)
                    self.profhand1.render()
                    glPopMatrix()
                    
            elif self.scene == 3:                
                glPushMatrix()
                x, y = (350 + self.walloffset, 168)
                glTranslatef(x, 768-y-300, 0)
                self.monitor.render()
                glPopMatrix()
                
                glPushMatrix()
                x, y = (155 + self.profoffset, 179)
                glTranslatef(x, 768-y-300, 0)
                self.profback.render()
                glPopMatrix()
            elif self.scene == 5:
                glEnable(GL_BLEND)
                glPushMatrix()
                x, y = (400 + self.earthoffset, 450)
                glTranslatef(x, 768-y, 0)
                self.earth.render()
                glPopMatrix()
                glDisable(GL_BLEND)
            elif self.scene == 6:
                glPushMatrix()
                x, y = (210 + self.profoffset, 168)
                glTranslatef(x, 768-y-300, 0)
                self.prof.render()
                glPopMatrix()
                
                glPushMatrix()
                x, y = (560, 168)
                glTranslatef(x, 768-y-300, 0)
                self.wall.render()
                glPopMatrix()
            elif self.scene == 7:
                glColor(255, 255, 255, ((self.profoffset % 3) / 3 ) * 0.7)
                glEnable(GL_BLEND)
                glBegin(GL_QUADS)
                glVertex2f(0, 0)
                glVertex2f(1024, 0)
                glVertex2f(1024, 768)
                glVertex2f(0, 768)
                glEnd()
                glDisable(GL_BLEND)
                glColor(1, 1, 1, 1)
            elif self.scene == 8:
                glPushMatrix()
                x, y = (560, 168)
                glTranslatef(x, 768-y-300, 0)
                self.wall.render()
                glPopMatrix()
            elif self.scene == 9:
                glPushMatrix()
                x, y = (490 - ((self.profoffset - 8) / 3), 168)
                glTranslatef(x, 768-y-300, 0)
                self.closeup.render()
                glPopMatrix()
                
            #black bars (oh man i love em!)
            if 1: #self.scene != 1:
                glColor(0, 0, 0, 1)
                
                #top bar
                glBegin(GL_QUADS)
                glVertex2f(0, 600)
                glVertex2f(1024, 600)
                glVertex2f(1024, 768)
                glVertex2f(0, 768)
                glEnd()
                
                #Bottom
                glBegin(GL_QUADS)
                glVertex2f(0, 0)
                glVertex2f(1024, 0)
                glVertex2f(1024, 300)
                glVertex2f(0, 300)
                glEnd()
                
                glColor(1, 1, 1, 1) #rjones rocks ;)
            
            self.subtitlefun()
            
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
            
            if self.fadetonextscene == True: #or self.exit == True:
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
                self.running += .02
                if self.running >= 1:
                    self.fadetonextscene = False
                    self.fadein = True
                    self.setfornextscene()
            elif self.cuttonextscene == True:
                self.cuttonextscene = False
                self.setfornextscene()
            
            pygame.display.flip()
            
            if self.exit == True: #and self.running >= 1:
                pygame.mixer.music.fadeout(400)
                return
