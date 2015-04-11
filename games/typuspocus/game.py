# -*- coding: iso-8859-1 -*-
import pygame
from pygame.locals import *
from engine import Game, Scene
from audiencia import AudienciaScene
import audiencia
import cosas
from motor import MainMotor, Estados
import hollow
from sounds import sounds
import time, random
from levels import niveles
import countries
import hiscore_client
DEBUG = 0

CLOCK_TICK = pygame.USEREVENT

class Timer:
    def __init__(self, total_time):
        self.total_time = total_time
        self.time_left = total_time
        
    def setTimeLeft(self, time):
        self.time_left = time
        
    def blit(self, surface, (x, y)):
        full = 300
        width = 20
        current = (self.time_left*full)/self.total_time
        pygame.draw.rect(surface, (0,0,0), Rect(x-1,y-1,width+3,full+2))
        pygame.draw.rect(surface, (30,255,30), Rect(x,y+full-current,width,
                current))
        
        
class LineManager:
    def __init__(self, hechizo, font_size = 80, font = "escenario/MagicSchoolOne.ttf", altfont_size = 80, altfont = "escenario/VeraSe.ttf", width=600):
        self.font = pygame.font.Font(font,font_size)
        self.altfont = pygame.font.Font(altfont,altfont_size)
        text = set([ t for t in hechizo ])
        self.cache = {}
        colores = [
            [(130,130,170), (0,0,255)],
            [(255,255,0),(255,0,0)],
            [(170,170,100),(170,0,0)],
            [(255,0,0),(128,0,0)],
            ]
        for t in text:
            if t in " ,.<>:;":
                font = self.altfont
            else:
                font = self.font
            if t == " ":
                self.cache[t] = [ 
                    hollow.textOutline(font,t,*colores[0]),
                    hollow.textOutline(font,t,*colores[1]),
                    hollow.textOutline(font,"_",*colores[2]),
                    hollow.textOutline(font,"_",*colores[3])
                    ]
            else:
                self.cache[t] = [ hollow.textOutline(font,t,*c) for c in colores ]

            self.height = self.cache[t][0].get_height()

        words = hechizo.split(" ")
        lines = []
        current = ""
        line_len = 0
        for word in words:
            word_len = sum([ self.get(l,0).get_width() for l in word ])
            if line_len + word_len > width:
                lines.append( current[1:]+" " )
                current = ""
                line_len = 0
                
            current += " "+word
            line_len += 1+word_len
        lines.append( current[1:] )
        
        self.lines = lines            

    def get(self, letter, style):
        return self.cache[letter][style]
        
    def getLineFromCursor(self, cursor):
        offset = 0
        for line in self.lines:
            if len(line)+offset>cursor:
                return (offset,line)
            offset += len(line)
        return 0,0
        

class Alarm:
    alarm_time = 5
    blink_time = 0.5
    sound_time = 3
    
    def __init__(self):
        self.armed = False
        self.start = None
        font = pygame.font.Font("escenario/MagicSchoolOne.ttf",50)
        self.message = hollow.textOutline(font, "Start typing the spell!", (230,100,100), (0,0,0))
        self.last_blink = None
        self.blink_state = True
        self.last_sound = None
        
    def arm(self):
        self.start = time.time()
        self.armed = True
        
    def disarm(self):
        self.armed = False
        
    def blit(self, screen):
        if self.armed:
            if time.time()-self.start>self.alarm_time:
                if self.last_blink is None:
                    self.last_blink = time.time()
                    
                if time.time()-self.last_blink > self.blink_time:
                    self.blink_state = not self.blink_state
                    self.last_blink = time.time()
                    
                if self.blink_state:
                    screen.blit(self.message, (400-self.message.get_width()/2, 430))
                if self.last_sound is None:
                    self.last_sound = time.time()
                    sounds.signal()
                    
                if time.time()-self.last_sound > self.sound_time:
                    sounds.signal()
                    self.last_sound = time.time()
                    

                
        
        
PERDIO, GANO = range(2)
PLAYING, WINNING, WON, TIMEOUT, TOMATOING, TOMATO, LOSING, LOST, DONE = range(9)


class Level(Scene):
    linebyline = False
    
    def init(self, level_number, motor, laAudiencia):
        self.audiencia = laAudiencia
        self.motor = motor
        self.line_manager = LineManager(self.motor.hechizo)
        self.offset_cache = [None]*len(self.motor.hechizo)
        self.style_cache = [None]*len(self.motor.hechizo)
        self.last_cursor = 0
        self.level_number = level_number
        
        self.line_group = pygame.sprite.OrderedUpdates()
        self.line = None
        self.audiencia = AudienciaScene(self.game, self.level_number, self.audiencia)
        self.subscenes.append( self.audiencia )
        self.todasLasTeclas = ""
        
        pygame.time.set_timer(CLOCK_TICK, 1000)        
        #pygame.mixer.music.load("sounds/8bp063-07-dorothys_magic_bag-rondo_alla_turka.mp3")
        #pygame.mixer.music.set_volume(0.5)
        #pygame.mixer.music.play(-1)
        
        self.tick_count = True
        
        self.state = PLAYING

        self.level_timer = Timer(self.motor.getTimeLeft())
        self.audiencia.setVoluntario(self.motor.voluntario, False)
        self.messagefont = pygame.font.Font("escenario/VeraMono.ttf",30)
        self.ratefont = pygame.font.Font("escenario/VeraMono.ttf",20)
        self.cursorfont = pygame.font.Font("escenario/MagicSchoolOne.ttf",100)
        self.motor.start()
        sounds.volumenDeeJay(1.0)
        self.alarm = Alarm()
        self.alarm.arm()
        
        
    def event(self, evt):
        if self.state == PLAYING:
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    self.end()
                
                self.alarm.disarm()
                res = None
                letra = evt.unicode #.lower()
                if letra.isalpha() or (letra and letra in " ,.<>:;1234567890'-"):
                    res, event = self.motor.hitLetra( letra )
                    self.checkEaster(letra)
                if evt.key == K_BACKSPACE:
                    self.motor.hitBackspace()
                if evt.key == K_RETURN:
                    res, event = self.motor.hitLetra(" ")
                    
                if res:
                    self.audiencia.gameEvent( event )
                    
            elif evt.type == CLOCK_TICK:
                sound_len = 100
                timeleft = self.motor.getTimeLeft()
                total_time = self.motor._getTiempoJuego()
                tick_rate = sound_len + timeleft * (1000-sound_len)/total_time
                if self.tick_count:
                    sounds.tick1()
                else:
                    sounds.tick2()
                self.tick_count = not self.tick_count
                pygame.time.set_timer(CLOCK_TICK, tick_rate)
                if DEBUG: print "tickrate", tick_rate
            
                
            if self.motor.cursor >= len(self.motor.hechizo):
                sounds.apagarVoces()
                sounds.volumenDeeJay(0.5)
                if self.motor.tuvoExito():
                    self.state = WINNING
                    sounds.suspensook()
                else:
                    self.state = LOSING
                    sounds.suspensomal()
                self.wintime = pygame.time.get_ticks()
                    
          
        elif self.state in [ WON ]:
            if evt.type == KEYDOWN:
                    sounds.apagarSonidos()
                    self.end(GANO)
        elif self.state in [ LOST, TOMATO ]:
            if evt.type == KEYDOWN:
                    sounds.apagarSonidos()
                    self.end(PERDIO)
    
    
    
    def loop(self):
        sounds.heatDeeJay(self.motor.calor)
        # aca updateamos el mundo cada paso
        if self.state == PLAYING:
            if self.motor.getTimeLeft() <= 0:
                self.state = TOMATOING
                sounds.gritosmalaonda()
                self.audiencia.tomateame()
                self.wintime = pygame.time.get_ticks()
                
            self.level_timer.setTimeLeft( self.motor.getTimeLeft() )
                
                
            evt = self.motor.tick()
            self.audiencia.setCalor( self.motor.calor )
            
            if evt:
                self.audiencia.gameEvent( evt )
        elif self.state == WINNING:
            if pygame.time.get_ticks() -self.wintime > 2000:
                self.state = WON
                self.audiencia.setVoluntario(None, True) 
                sounds.gritosfelicitacion()
        elif self.state == LOSING:
            if pygame.time.get_ticks() -self.wintime > 2000:
                self.state = LOST
                self.audiencia.setVoluntario(self.motor.voluntario_error, True)
                sounds.gritosmalaonda()
        elif self.state == TOMATOING:
            if pygame.time.get_ticks() -self.wintime > 2000:
                self.state = TOMATO

                
    def checkEaster(self, letra):
        self.todasLasTeclas += letra
        if "who is your daddy" in self.todasLasTeclas:
            self.audiencia.doEasterEgg()
            self.todasLasTeclas = ""
        if "puto del ojete" in self.todasLasTeclas:
            sounds.abucheo()
            self.todasLasTeclas = ""
        if "gimme score" in self.todasLasTeclas:
            self.motor.score += 10
            sounds.signal()
            self.todasLasTeclas = ""
        if "make me win" in self.todasLasTeclas:
            self.state = WINNING
            self.wintime = pygame.time.get_ticks()
                 
                          
    def update(self):
        font = self.messagefont
            
        if self.state == PLAYING:
            #self.game.screen.blit(self.background, (0,0))
            if self.linebyline:
                cursor = self.motor.cursor
                offset, line = self.line_manager.getLineFromCursor( cursor )
                
                ypos = 540
                xpos = (800-sum([ self.line_manager.get(l,0).get_width() for l in line ]))/2
                cursor_xpos = xpos
                for position, letter in enumerate(line):
                    style = self.motor.estado[position+offset]
                    
                    if position+offset == cursor:
                        cursor_xpos = xpos
                        
                    i = self.line_manager.get(letter, self.motor.estado[position+offset])
                    
                    self.game.screen.blit( i, (xpos, ypos) )
                    xpos += i.get_width()
                    cursor_img = self.cursorfont.render("^", True, (255,255,255))
                    self.game.screen.blit(cursor_img, 
                                          (cursor_xpos,ypos+self.line_manager.height)
                                          )                    
            else:
                # paint forward
                xpos = 400
                ypos = 300
                cursor = self.motor.cursor
                if DEBUG: print "falta == ",self.motor.hechizo[cursor:]
                for position, letter in enumerate(self.motor.hechizo[cursor:]):
                    style = self.motor.estado[position+cursor]
                    
                        
                    i = self.line_manager.get(letter, self.motor.estado[position+cursor])
                    
                    self.game.screen.blit( i, (xpos, ypos) )
                    xpos += i.get_width()
                    if xpos > 800: break
                    
                surface= self.line_manager.get(self.motor.hechizo[cursor], self.motor.estado[cursor])
                width = surface.get_width()
                height = surface.get_height()
                
                cursor_sf = hollow.textOutline(self.cursorfont, "^", (150,150,250), (0,0,0))
                self.game.screen.blit( cursor_sf, (400+width/2-cursor_sf.get_width()/2,370))
                
                
                #pain backwards
                xpos = 400
                letters = [l for l in self.motor.hechizo[:cursor]]
                if DEBUG: print "done==", self.motor.hechizo[:cursor]
                letters.reverse()
                for position, letter in enumerate(letters):
                    style = self.motor.estado[-position+cursor]
                    
                        
                    i = self.line_manager.get(letter, self.motor.estado[-1-position+cursor])
                    width = i.get_width()
                    if xpos - width < 0: break
                    xpos -= width
                    self.game.screen.blit( i, (xpos, ypos) )
                                

            self.level_timer.blit( self.game.screen, (770, 50))

            # ponemos el rate de teclas
            rate = self.motor.getRate()
            if rate < self.motor.precision_requerida:
                color_tx = (255,0,0)
            else:
                color_tx = (0,255,0)
            rate_sf = hollow.textOutline( self.ratefont, "%i%%"%(int(rate*100)),  color_tx, (0,0,0) )
            self.game.screen.blit( rate_sf, (770-rate_sf.get_width()/2, 35-rate_sf.get_height()/2))

            # y el score
            score = self.motor.score
            score_sf = hollow.textOutline(self.ratefont, "Score: %3.1f"%score, (0,0,255), (0,0,0))
            self.game.screen.blit( score_sf, (790-score_sf.get_width(), 15-score_sf.get_height()/2))
            
            
            self.alarm.blit(self.game.screen)
        if self.state in [WON, LOST, TOMATO]:
            im = hollow.textOutline(font, "[press any key]", (30,30,200), (255,255,255))
            ypos = 400
            xpos = (800-im.get_width())/2
            
            self.game.screen.blit( im, (xpos, ypos) )
            
            
Foreground = None #= pygame.image.load("escenario/foreground.png")

def test():
    global Foreground
    Foreground = pygame.image.load("escenario/foreground.png")
    Foreground.convert()


class BannerScene(Scene):
    def renderOn(self, surface, lines=[]):
        Yellow = (255,255,160)
        posx=110
        widx=600
        posy=80
        widy=385 # 30 * 9 = 270  (1 titulo, 3 en blanco, 5 del nivel) mejorar.. 
        introSurface = surface.subsurface(pygame.Rect(posx,posy,widx,widy))
        fontYsize = 30
                
        deltaY = (widy - (len(lines)*fontYsize))/2+20
        nline=0        
        for line in lines:
            s = self.font.render(line, True, Yellow)
            tx,ty =s.get_size()
            introSurface.blit(s, ((widx-tx)/2, deltaY+nline*fontYsize))
            nline+=1

class LevelIntro(BannerScene):
    def init(self, level_number, level_name, audiencia, level=None):
        test()
        self.level_number = level_number
        self.audiencia = audiencia
        self.level_name = level_name
        self.font = pygame.font.Font("escenario/MagicSchoolOne.ttf",50)
        self.overlay = pygame.image.load("escenario/screens/overlay.png").convert_alpha()
        self.level = level
        
    def update(self):
        self.audiencia.update()
        self.game.screen.fill((0,0,0))
        self.background = self.game.screen.subsurface(pygame.Rect(0,0,800,525))
        self.audiencia.render(self.background)
        self.background.blit(Foreground, (0,0))
        self.game.screen.blit(self.overlay, (0,0))
        if self.level<>None:
            self.renderOn(self.game.screen, [self.level.nombre, '',''] +
                                    self.level.historyintro.split('\n') )
           
    def event(self, evt):
        if evt.type == KEYDOWN:
                self.end()

EstadoMensaje, EstadoContinuar = range(2)

class LevelSuccess(BannerScene):
    def init(self, score, levelscore, xaudiencia, level):
        self.score = score
        self.level = level
        self.audiencia = xaudiencia
        self.levelscore = levelscore
        #self.font =  pygame.font.Font("escenario/VeraMono.ttf",50)
        self.overlay = pygame.image.load("escenario/screens/overlay.png").convert_alpha()
        self.status = EstadoMensaje
        
    def update(self):
        self.audiencia.update()
        self.game.screen.fill((0,0,0))
        self.background = self.game.screen.subsurface(pygame.Rect(0,0,800,525))
        
        self.audiencia.render(self.background)
        self.background.blit(Foreground, (0,0))    
        
        self.game.screen.blit(self.overlay, (0,0))
        if self.status == EstadoMensaje:
            self.font = pygame.font.Font("escenario/MagicSchoolOne.ttf",50)
            self.renderOn(self.game.screen,[self.level.nombre, '',''] +
                                    self.level.historygood.split('\n'))
        else:
            self.font =  pygame.font.Font("escenario/VeraMono.ttf",30)
            self.renderOn(self.game.screen, 
                ["Level Completed","",
                "Points accumulated:"+str(self.levelscore),"", 
                "New Score:"+str(self.score) ])
                
    def event(self, evt):
        if evt.type == KEYDOWN:
            if self.status == EstadoMensaje:
                self.status=EstadoContinuar
            else:
                self.end()

class LevelFailSuccess(LevelSuccess):
    ## please make me simpler!
    def update(self):
        self.audiencia.update()
        self.game.screen.fill((0,0,0))
        self.background = self.game.screen.subsurface(pygame.Rect(0,0,800,525))
        
        self.audiencia.render(self.background)
        self.background.blit(Foreground, (0,0))    
        
        self.game.screen.blit(self.overlay, (0,0))
        if self.status == EstadoMensaje:
            self.font = pygame.font.Font("escenario/MagicSchoolOne.ttf",50)
            self.renderOn(self.game.screen,[self.level.nombre, '',''] +
                                    self.level.historybad.split('\n'))
        else:
            self.font =  pygame.font.Font("escenario/VeraMono.ttf",30)
            self.renderOn(self.game.screen, 
                ["Level Completed","",
                "Points accumulated:"+str(self.levelscore),"", 
                "New Score:"+str(self.score) ])
                
class GameOver(Scene):
    def init(self, score, laaudiencia, level):
        self._background = pygame.image.load("escenario/screens/gameover.png").convert()
        self.level=level
        self.menu = Menu(
                 pygame.font.Font("escenario/MagicSchoolOne.ttf",50),
                 pygame.font.Font("escenario/MagicSchoolOne.ttf",70),
                 ["No", "Yes",],
                 margin = -40,
                 normal_color = (173,148,194),
                 selected_color = (244,232,255),
                 )
                 
        self.score = score
        self.font = font =  pygame.font.Font("escenario/VeraMono.ttf",30)
        self.audiencia = laaudiencia
        
    def do_action(self, sel):
        if sel:
            self.end( True )
        else:
            self.end( False )
            
    def paint(self):
        self.game.screen.blit(self.background, (0,0))
        self.menu.blit(self.game.screen, 400, 320)
        
    def event(self, evt):
        if evt.type == MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            x -= 400
            y -= 180
            if self.menu.set_mouse(x,y):
                sounds.pasa()
                self.paint()
        elif evt.type == MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            x -= 400
            y -= 180
            sel = self.menu.click_mouse(x,y)
            if sel is not None:
                sounds.enter()
                self.do_action(sel)
        elif evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                self.end()
            elif evt.key == K_DOWN:
                self.menu.next()
                sounds.pasa()
                self.paint()
            elif evt.key == K_UP:
                self.menu.prev()
                sounds.pasa()
                self.paint()
            elif evt.key in [K_RETURN, K_SPACE]:
                sel = self.menu.selected
                sounds.enter()
                self.do_action(sel)                
                
                
levels = [
          # title, parameters
          ("Starting out..", dict(cantidad_palabras =5)),
          ("Getting better..", dict(
                        cantidad_palabras=30, 
                        tiempo_por_caracter=0.4)
                      ),
          ("This guys want speed..", dict(
                      cantidad_palabras=40, 
                      tiempo_por_caracter=0.35, 
                      preferencia_precision=0.1) 
                      ),
          ("Perfectionism is king..", dict(
                       cantidad_palabras=40, 
                       tiempo_por_caracter=0.30, 
                       preferencia_precision=0.9
                       )),
          ("Mixed emotions..", dict(
                        cantidad_palabras=30, 
                        tiempo_por_caracter=0.25
                        )),
      ]                
      
      
class Menu:
    def __init__(self, font, font_selected, opts, margin=0, normal_color=(255,255,255), selected_color=(255,255,255), selected_border_color=None, normal_border_color=None):
        self.font = font
        self.font_selected = font_selected
        if selected_border_color == None:
            selected_border_color = (0,0,0)
        if normal_border_color == None:
            normal_border_color = (0,0,0)
        self.margin = margin
        self.color = color
        self.opts = opts
        self.selected = 0
        self.selected_img = []
        self.unselected_img = []
        
        line_step = 0
        for text in self.opts:
            sel = hollow.textOutline(font_selected, text, selected_color, selected_border_color )
            unsel = hollow.textOutline(font, text, normal_color, normal_border_color )
            self.selected_img.append( sel )
            self.unselected_img.append( unsel )
            line_step = max(max(sel.get_height(), unsel.get_height())+self.margin, line_step)
            
        self.line_step = line_step
            
                
    def blit(self, surface, center_x, start_y):
        for i in range(len(self.opts)):
            
            if i == self.selected:
                img = self.selected_img[i]
            else:
                img = self.unselected_img[i]
                
            x = center_x-img.get_width()/2
            y = start_y + self.line_step * i - img.get_height()/2
            
            surface.blit( img, (x,y) )
            
    def next(self):
        self.selected = (self.selected + 1)%len(self.opts)
        
    def prev(self):
        self.selected = (self.selected - 1)%len(self.opts)     
        
    def set_mouse(self, x, y):
        i = self.get_mouse_over(x,y)
        if i is not None and  i != self.selected:
            self.selected = i
            return True        
    
    def get_mouse_over(self, x, y):
        for i in range(len(self.opts)):
            img = self.selected_img[i]
                
            tx = 0-img.get_width()/2
            ty = 0 + self.line_step * i - img.get_height()/2
            
            if tx <= x <= tx+img.get_width():
                if ty+10 <= y <= ty+img.get_height()-10:
                    return i
        return None
        
    def click_mouse(self, x, y):
        i = self.get_mouse_over(x,y)
        if i is not None:
            return i      
            
class Credits(Scene):
    us = [
        ["Doppelganger","Alecu"],
        ["Nigromante", "LucioTorre"],
        ["Alchemist", "Riq"],
        ["Medium","LeitoMonk"],
        ["FortuneTeller", "Tenuki"],
        ["SpellCaster","PabloZ"],
        ["Druid","FacundoBatista"],
        ["HarryPopperist","NubIs"],
        ["Voodoo","nrm"],  #andres
        ]
    them = [
        ["Maniqueist", "stortroopers.com"],
        ["Snake Wranglers","Python Argentina"]
        ]
    sections = []  
    BEGIN, HIT, RETREAT, HANDOUT, DONE, LOOP = range(6)
    
    hand_start = -647,-200
    hand_end = -300,250
    puff_position = 400,250
    begin_duration = 1.5
    hit_duration = 0.0
    retreat_duration = 1.5
    handout_duration = 4
    done_duration = 0
    loop_duration = 5
    
    def init(self, font, color=[(255,255,255), (255,255,0)], outline_color=[(0,0,0)]*2, line_step=40):
        self.line_step = line_step
        random.shuffle(self.us)
        random.shuffle(self.them)
        self.sections = self.us + self.them
        self.section_imgs = []
        for section in self.sections:
            lines = []
            for n,line in enumerate(section):
                img = hollow.textOutline(font, line, color[n], outline_color[n])
                lines.append( img )
            self.section_imgs.append( lines )
            
        self.section_number = 0
        self.state = self.BEGIN
        self.state_start = time.time()
        self.hand_pos = None
        self.hand_img = None
        self.puff = None
        self.puff_pos = None
        self.text = None
        
        self.nubes = [ pygame.image.load("escenario/nube/nube%d.png"%(n+1)).convert_alpha() for n in range(5) ]
        self.hand = pygame.image.load("escenario/manos/mano1.png").convert_alpha()
        self.hand2 = pygame.image.load("escenario/manos/mano2.png").convert_alpha()
        sounds.gritosfelicitacion()
        
    def event(self, evt):
        if evt.type == KEYDOWN:
            sounds.apagarVoces()
            self.end()
                
                
    def loop(self):
        if self.state == self.BEGIN:
            if time.time() - self.state_start >= self.begin_duration:
                self.state = self.HIT
                self.state_start = time.time()          
            else:
                p = ((time.time()-self.state_start)/self.begin_duration)**2
                
                sx, sy = self.hand_start
                ex, ey = self.hand_end
                nx = sx + (ex-sx)*p
                ny = sy + (ey-sy)*p
                
                self.hand_pos = nx, ny
                self.hand_img = self.hand
            
        elif self.state == self.HIT:
            self.text = self.section_imgs[ self.section_number ]
            self.section_number += 1
            self.puff = True
            sounds.MagiaOK()
            self.state = self.RETREAT
               
                
        elif self.state == self.RETREAT:
            if time.time() - self.state_start >= self.retreat_duration:
                self.state = self.HANDOUT
                self.state_start = time.time()
            else:
                p = (1-(time.time()-self.state_start)/self.begin_duration)**2+0.1
                
                sx, sy = self.hand_start
                ex, ey = self.hand_end
                nx = sx + (ex-sx)*p
                ny = sy + (ey-sy)*p
                
                self.hand_pos = nx, ny
                self.hand_img = self.hand2
                
        elif self.state == self.HANDOUT:
            if time.time() - self.state_start >= self.handout_duration:
                self.state = self.DONE
                self.state_start = time.time()
            else:
                self.hand_pos = None
        elif self.state == self.DONE:
            if time.time() - self.state_start >= self.done_duration:
                if self.section_number < len(self.section_imgs):
                    self.state = self.BEGIN
                    self.state_start = time.time()
                else:
                    self.state = self.LOOP
                    self.state_start = time.time()
                    self.text = None
                    self.hand_pos = None
            else:
                self.hand_pos = None
        elif self.state == self.LOOP:
            if time.time() - self.state_start >= self.begin_duration:
                self.state = self.BEGIN
                self.state_start = time.time()
                self.section_number = 0

                
                    
    def update(self):
        self.game.screen.blit(self.background, (0,0))
        
        if self.text:
            lineas = len(self.text)
            space = lineas * self.line_step
            start = 320-space/2
            
            for i,line in enumerate(self.text):
                self.game.screen.blit(line, (
                        400-line.get_width()/2, 
                        start + self.line_step*i - line.get_height()
                        ))
        if self.puff:
            delta = time.time()-self.state_start
            if delta >= 1:
                self.puff = None
                sounds.arenga()
            
            else:
                pos = int(delta*5)
                pos = min(pos, 4)
                self.game.screen.blit(self.nubes[pos], (300,150) )
        if self.hand_pos:
            self.game.screen.blit(self.hand_img, self.hand_pos )
        
class Ranking(Scene):
    rankings = ["Orko","Lord Zedd",  "David Copperfield", "Harry Potter","Skeletor", "Mum-ra",  "Harry Houdini", "Mandrake", "Gandalf", "Merlin",  ]
    stages = [10,20,40,60,80,100,120,140,200]
    def init(self, rank=None, score=None):
        
        if score is None:
            score = random.randint(0,1000)
            if rank is None:
                rank = 9#random.randint(0,10)    
        elif rank is None:
            rank = sum([1 for i in self.stages if score > i])
                
        self._background = pygame.image.load("escenario/screens/ranking.png").convert()
        self.paint_info = False
        self.score = score
        self.rank = rank
        self.kaping = True
        self.font = pygame.font.Font("escenario/MagicSchoolOne.ttf",65)
        self.font2 = pygame.font.Font("escenario/MagicSchoolOne.ttf",90)
        self.font3 = pygame.font.Font("escenario/MagicSchoolOne.ttf",110)
        
        font = pygame.font.Font("escenario/MagicSchoolOne.ttf",30)
        self.textos = [ font.render("%2i:"%(10-i)+line, True, (255,255,255)) for (i,line) in enumerate(self.rankings) ]
        
        self.start_time = time.time()
        sounds.sube()
        
    def event(self, evt):
        if evt.type == KEYDOWN:
                self.end()
                
    def update(self):
        ypos = 450
        self.game.screen.blit(self.background, (0,0))
        for i, sf in enumerate(self.textos):
            
            if int(time.time()-self.start_time) >= i:
                if self.rank>=i:
                    self.game.screen.blit( sf, (100, ypos) )
                if self.rank == i:
                    self.paint_info = True
                if i > self.rank:
                    break
            ypos -= 35
            
        yri = self.font.render("Your ranking is:", True, (255,248,144))
        print "rank", self.rank
        yr = self.font2.render(self.rankings[self.rank], True, (255,254,232))
        
        ysi = self.font.render("Score", True, (255,248,144))
        ys = self.font3.render(str(self.score), True,  (255,254,232))
        
        if self.paint_info:
            if self.kaping:
                self.kaping = False
                sounds.golpe()
            self.game.screen.blit(yri, (480-yri.get_width()/2, 150))
            self.game.screen.blit(yr, (480-yr.get_width()/2, 205))
            self.game.screen.blit(ysi, (680-ysi.get_width()/2, 300))
            self.game.screen.blit(ys, (670-ys.get_width()/2, 340))

class Locked(Scene):
    def init(self):
        self._background = pygame.image.load("escenario/screens/locked.png").convert()
        sounds.bu()
        

        
    def paint(self):
        self.game.screen.blit(self.background, (0,0))
        font = pygame.font.Font("escenario/MagicSchoolOne.ttf",60)
        sf2 = hollow.textOutline(font, "You must first finish your career",(255,254,232), (0,0,0))
        sf3 = hollow.textOutline(font, "before touring the world",(255,254,232), (0,0,0))
            
        self.game.screen.blit(sf2, (400-sf2.get_width()/2, 350))
        self.game.screen.blit(sf3, (400-sf3.get_width()/2, 420))
        
            
    def event(self, evt):
        if evt.type == KEYDOWN:
            sounds.apagarVoces()
            self.end()

        
class Hiscores(Scene):
    def init(self):
        self.client = hiscore_client.HiScoreClient()
        self._background = pygame.image.load("escenario/screens/highscores.png").convert()
        

        
    def paint(self):
        self.game.screen.blit(self.background, (0,0))
        font = pygame.font.Font("escenario/MagicSchoolOne.ttf",40)
        font2 = pygame.font.Font("escenario/MagicSchoolOne.ttf",90)
        font3 = pygame.font.Font("escenario/MagicSchoolOne.ttf",30)
        scores = self.client.listHiScores()
        for i in range(8):
            if i < len(scores):
                points, when, name, ip = scores[i]
            else:
                points, name = "--", ""
                
            if not name: name = " "
            
            sf1 = hollow.textOutline(font3, str(i),(255,254,232), (0,0,0))
            sf2 = hollow.textOutline(font, name,(255,254,232), (0,0,0))
            sf3 = hollow.textOutline(font, str(points),(255,254,232), (0,0,0))
                
            ypos = 200 + i*30
            self.game.screen.blit(sf1, (200-sf1.get_width(), ypos))
            self.game.screen.blit(sf2, (270, ypos))
            self.game.screen.blit(sf3, (620, ypos))
            
            
    def event(self, evt):
        if evt.type == KEYDOWN:
            sounds.apagarVoces()
            self.end()
    
class EnterHiscores(Scene):
    def init(self, score):
        self.client = hiscore_client.HiScoreClient()
        self._background = pygame.image.load("escenario/screens/highscores.png").convert()
        self.name = ""
        self.score = score
        
    def paint(self):
        self.game.screen.blit(self.background, (0,0))
        font = pygame.font.Font("escenario/MagicSchoolOne.ttf",65)
        font2 = pygame.font.Font("escenario/MagicSchoolOne.ttf",90)
        
        sf = hollow.textOutline(font2, "Enter your name",(255,254,232), (0,0,0))
        self.game.screen.blit(sf, (400-sf.get_width()/2, 200))
        
        sf = hollow.textOutline(font2, self.name,(255,254,232), (0,0,0))
        self.game.screen.blit(sf, (400-sf.get_width()/2, 330))
            
            
    def event(self, evt):
        if evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                sounds.apagarVoces()
                self.end()
            elif evt.key == K_RETURN:
                self.client.addHiScore(self.score, self.name)
                sounds.apagarVoces()
                self.end()
                
            else:
                letra = evt.unicode #.lower()
                if letra.isalpha() or (letra and letra in " ,.<>:;1234567890"):
                    self.name += letra
                    self.paint()
                    sounds.pasa()
                if evt.key == K_BACKSPACE:
                    self.name = self.name[:-1]
                    self.paint()
                    sounds.pasa()
                
class GameIntro(Scene):
    sections = [
        ["My son,"," this will be a ","challenging day for you."],
        ["You have always been","the black sheep of","our great family."],
        ["But your old man,","the Great Grossini, is","not what he used to be."],
        ["I'm suffering from","Flaccid Wand, so tonite","you will replace me."],
        ["Farewell!"],
        ]
        
    lines_start = [5,10,17.5,23.5,26,0]
    
    START, ENTERING, READY, TALKING, PAUSE, GONE = range(6)
    
    start_position = -20,350
    end_position = 465,330
    start_duration = 1
    entering_duration = 5
    ready_duration = 4
    talking_duration = 1
    pause_duration = 1
    gone_duration = 3.5
    
    def init(self, font, color=(0,0,0), outline_color=(0,0,0), line_step=40):
        self.line_step = line_step
        self.section_imgs = []
        for section in self.sections:
            lines = []
            for line in section:
                img = font.render( line, True, color)
                lines.append( img )
            self.section_imgs.append( lines )
            
        self.section_number = 0
        self.state = self.START
        self.state_start = time.time()
        self.guy_pos = None
        self.guy_img = None
        self.puff = None
        self.puff_pos = None
        self.text = False
        self.talking_done = False
        self.lamp_on = False
        self.ballon_on = False
        self.alpha = True
        
        self.nubes = [ pygame.image.load("escenario/nube/nube%d.png"%(n+1)).convert_alpha() for n in range(5) ]
        self.guy = pygame.image.load("audiencia/dad.gif").convert_alpha()
        self.guy_alpha = pygame.Surface( (self.guy.get_width(), self.guy.get_height()) )
        self.guy_alpha.set_alpha(180)
        
        self.lampara = pygame.image.load("escenario/screens/dad.png").convert_alpha()
        self.globo = pygame.image.load("escenario/screens/balloon.png").convert_alpha()
        
    def event(self, evt):
        if evt.type == KEYDOWN:
            sounds.apagarVoces()
            self.end()
                
                
                
    def loop(self):
        if self.state == self.START:
            if time.time() - self.state_start >= self.start_duration:
                self.state = self.ENTERING
                self.state_start = time.time() 
                sounds.camina()                
                
        
        if self.state == self.ENTERING:
            if time.time() - self.state_start >= self.entering_duration:
                self.state = self.READY
                self.state_start = time.time() 
                sounds.farol()         
                self.lamp_on = True
                self.alpha = False
            else:
                p = ((time.time()-self.state_start)/self.entering_duration)
                
                sx, sy = self.start_position
                ex, ey = self.end_position
                nx = sx + (ex-sx)*p
                ny = sy + (ey-sy)*p
                
                self.guy_pos = nx, ny
                self.guy_img = self.guy
               
                
        elif self.state == self.READY:
            if time.time() - self.state_start >= self.ready_duration:
                self.state = self.TALKING
                self.state_start = time.time()
                self.text = False
                self.ballon_on = True                
                sounds.intro()
            else:
                pass
        elif self.state == self.TALKING:
            if self.talking_done:
                self.state = self.PAUSE
                self.ballon_on = False
                self.state_start = time.time()
            else:
                self.text = True
        elif self.state == self.PAUSE:
            if time.time() - self.state_start >= self.pause_duration:
                self.state = self.GONE
                self.state_start = time.time()
                self.guy_pos = None
                self.puff = True
                sounds.MagiaOK()                
            else:
                pass
        elif self.state == self.GONE:
            if time.time() - self.state_start >= self.gone_duration:
                self.end()
            else:
                pass
                
                
                 
    def update(self):
        self.game.screen.blit(self.background, (0,0))
        
        if self.lamp_on:
            self.game.screen.blit(self.lampara, (0,0))
            
        if self.ballon_on:
            self.game.screen.blit(self.globo, (30,30))
        
        if self.text:
            delta = time.time()-self.state_start
            
            for i in range(len(self.lines_start)):
                if self.lines_start[i] > delta:
                    break
            pos = i
            if pos >= len(self.sections):
                self.text = False
                self.talking_done = True
            else:
                
                text = self.section_imgs[pos]
                
                lineas = len(text)
                space = lineas * self.line_step
                start = 210-space/2
                
                for i,line in enumerate(text):
                    self.game.screen.blit(line, (
                            220-line.get_width()/2, 
                            start + self.line_step*i - line.get_height()
                            ))
        if self.puff:
            delta = time.time()-self.state_start
            if delta >= 1:
                self.puff = None
            else:
                pos = int(delta*5)
                pos = min(pos, 4)
                self.game.screen.blit(self.nubes[pos], (420,300) )
                
        if self.guy_pos:
            self.game.screen.blit(self.guy_img, self.guy_pos )
            if self.alpha:
                self.game.screen.blit(self.guy_alpha, self.guy_pos )
            
class TourLevel:
    def __init__(self, country):
        self.historyintro = "Touring in "+country
        self.titulo = "World Tour"
        self.nombre = "World Tour"
        self.historybad = "You are deported from\n%s"%country
        self.historygood = "The people at\n%s\nlove you!"%country
    
class MainMenu(Scene):
    def init(self):
        self._background = pygame.image.load("escenario/screens/menu.png").convert()
        self.font = font =  pygame.font.Font("escenario/MagicSchoolOne.ttf",90)
        self.menu = Menu(
                 pygame.font.Font("escenario/MagicSchoolOne.ttf",50),
                 pygame.font.Font("escenario/MagicSchoolOne.ttf",70),
                 ["Career", "World Tour", "Hiscores", "Credits", "Quit"],
                 margin = -40,
                 normal_color = (173,148,194),
                 selected_color = (244,232,255),
                 )
        sounds.menu()
        
        try:
            open("unlock_tour.key")
            self.tour_locked = False
        
        except IOError:
            self.tour_locked = True
        
    def paint(self):
        self.game.screen.blit(self.background, (0,0))
        self.menu.blit(self.game.screen, 400, 180)
        
    def event(self, evt):
        if evt.type == MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            x -= 400
            y -= 180
            if self.menu.set_mouse(x,y):
                sounds.pasa()
                self.paint()
        elif evt.type == MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            x -= 400
            y -= 180
            sel = self.menu.click_mouse(x,y)
            if sel is not None:
                sounds.enter()
                self.do_action(sel)
        elif evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                self.end()
            elif evt.key == K_DOWN:
                self.menu.next()
                sounds.pasa()
                self.paint()
            elif evt.key == K_UP:
                self.menu.prev()
                sounds.pasa()
                self.paint()
            elif evt.key in [K_RETURN, K_SPACE]:
                sel = self.menu.selected
                sounds.enter()
                sounds.apagarVoces()
                self.do_action(sel)
                sounds.menu()
                
    def do_action(self, sel):
        if sel == 0: # history
            self.play_history()
        elif sel == 1: # freestyle
            if self.tour_locked:
                self.runScene( Locked(self.game) )
            else:
                self.play_world_tour()
        elif sel == 2: # hiscores
            self.runScene( Hiscores(self.game) )
        elif sel == 3: # credits
            self.runScene( Credits( self.game, self.font ) )
        elif sel == 4: #quit            
            self.end()
                    
    def play_history(self):
            result = GANO
            count = 0
            score = 0
            futech = 0
            while True:
                if count < len(niveles):
                    nivel = niveles[count]
                    subtitle = nivel.nombre
                    params = nivel.params
                    for k,v in nivel.__dict__.items(): 
                        params[k] = v
                    wardrobes = nivel.audiencia
                    #.nombre
                    #.audiencia
                    #.objeto
                    #.hechizo
                    #.historyintro
                    #.historygood
                    #.historybad
                    #.titulo
                    #.params
                else:
                    self.runScene(Ranking(self.game, score=score))
                    self.runScene(EnterHiscores(self.game, score))
                    self.runScene(Hiscores(self.game))
                    self.tour_locked = False
                    break

                laAudiencia = audiencia.Audiencia(count, wardrobes)
                self.runScene( LevelIntro( self.game, str(count), subtitle , laAudiencia, nivel) )
                laAudiencia.doGame()
                l =  Level(self.game, count, MainMotor(**params), laAudiencia) 
                result = self.runScene( l )
                newscore = int(l.motor.score)
                score += newscore
                if result == GANO:
                    laAudiencia.doWin()
                    self.runScene( LevelSuccess(self.game, score, newscore, laAudiencia, nivel))
                    count += 1
                else:
                    laAudiencia.doGameOver()
                    self.runScene( LevelFailSuccess(self.game, score, newscore, laAudiencia, nivel))
                    cont = self.runScene( GameOver( self.game, score, laAudiencia, nivel ) )
                    if not cont:
                        self.runScene(Ranking(self.game, score=score))
                        self.runScene(EnterHiscores(self.game, score))
                        self.runScene(Hiscores(self.game))
                        break
                    else:
                        score = 0


    def play_world_tour(self):
            result = GANO
            count = 0
            score = 0
            futech = 0
            while True:
                laAudiencia = audiencia.Audiencia(level_number=count)
                params = dict(tiempo_por_caracter=1.0/(count+3))
                current_level = TourLevel(countries.getCountry())
                self.runScene( LevelIntro( self.game, str(count), "World Tour" , laAudiencia, current_level) )
                laAudiencia.doGame()
                l =  Level(self.game, count, MainMotor(**params), laAudiencia) 
                result = self.runScene( l )
                newscore = int(l.motor.score)
                score += newscore
                if result == GANO:
                    laAudiencia.doWin()
                    self.runScene( LevelSuccess(self.game, score, newscore, laAudiencia,current_level))
                    count += 1
                else:
                    laAudiencia.doGameOver()
                    self.runScene( LevelFailSuccess(self.game, score, newscore, laAudiencia, current_level))
                    cont = self.runScene( GameOver( self.game, score, laAudiencia,current_level ) )
                    if not cont:
                        self.runScene(Ranking(self.game, score=score))
                        self.runScene(EnterHiscores(self.game, score))
                        self.runScene(Hiscores(self.game))
                        break
                    else:
                        score = 0
                        
                


def main():
    g = Game(800, 525, framerate = 20, title = "Typus Pocus", icon="escenario/icono.png")
    g.run( GameIntro(g, pygame.font.Font("escenario/MagicSchoolOne.ttf",50)) )
    g.run( MainMenu(g) )
    
if __name__ == "__main__":
    main()
