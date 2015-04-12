#! usr/bin/env python


"Import modules."
import os, sys
import math, random

import pygame
from pygame.locals import *



"Loads an image from a file."
def load_image(file, colorkey=False):
    file = os.path.join('data/images', file)
    try:
        image = pygame.image.load(file)
    except:
        print 'Unable to load: ' + file
    return image.convert_alpha()


"Loads an image from a file."
def load_sound(file, volume=1.0):
    file = os.path.join('data/sounds', file)
    try:
        sound = pygame.mixer.Sound(file)
        sound.set_volume(volume)
    except:
        print 'Unable to load: ' + file
    return sound

"Loads a shapestrip."
def load_shapestrip(name, width):
    img = load_image(name)
    fw = img.get_width()
    num=fw/width
    imgs=[]
    for x in xrange(int(num)):
        surf = pygame.Surface((width, img.get_height()))
        surf = surf.convert_alpha()
        surf.fill((255, 255, 255, 0))
        surf.blit(img, (0, 0),(x*width, 0, width, img.get_height()))
        imgs.append(surf)
    return imgs



"Basic Stats."
SCORE = 0
LEVEL = 1
HIGHSCORE = int(open('data/highscore.high').read())

"Ship stats."
SHIELD = 200
TARGET_SHIELD = 200
RELOAD = 20
FUEL = 200
BOOST = 0.1
EXP = 0
CHEATED = False
INVINCIBLE = False
SHIP_TYPE = 'Shuttle'
LASER_COLOR = 'Blue'
BUFFER = 40

"Constants."
DEAD_TIMER = 0
FONT = 'data/Hemi Head 426.TTF'
FONT2 = 'data/Hemi Head 426.TTF'
FONT3 = 'data/Hemi Head 426.TTF'
MUSIC = 'data/music/Super Sonic Racing.ogg'
MUSIC2 = 'data/music/Can You Feel The Sunshine.ogg'
MUSIC3 = 'data/music/Diamond In The Sky.ogg'
MUSIC4 = 'data/music/Livin\' In The City.ogg'

"Initialise pygame!"
pygame.init()


"Try to center the window."
try:
    os.environ['SDL_VIDEO_CENTERED'] = '1'
except:
    pass

"Set the display mode."
pygame.display.set_caption('PyAsteroids - v2.0')
pygame.display.set_icon(pygame.image.load('data/icon.gif'))
screen = pygame.display.set_mode((800, 600), HWSURFACE|HWPALETTE|ASYNCBLIT)

"Load some resources."
font = pygame.font.Font(FONT, 16)
font2 = pygame.font.Font(FONT2, 30)
font3 = pygame.font.Font(FONT2, 70)

ren = font2.render('Now Loading...', 1, (255, 255, 255))
screen.blit(ren, (580, 555))
pygame.display.flip()
pygame.time.wait(500)


background = load_image('Background.bmp')
shieldbar = load_image('Shield.png')
fuelbar = load_image('Fuel.png')
expbar = load_image('Exp.png')
bar = load_image('Metal Bar.png')

ship1 = load_image('Shuttle Idle.png')
ship2 = load_image('Hornet Idle.png')
ship3 = load_image('Rocket Idle.png')
ship4 = load_image('Wasp Idle.png')
ship5 = load_image('Hawk Idle.png')
ship6 = load_image('Saturn Idle.png')
ship7 = load_image('Pluto Idle.png')
ship8 = load_image('Falcon Idle.png')
ship9 = load_image('Bumblebee Idle.png')
ship10 = load_image('Boomerang Idle.png')

stats1 = load_image('Shuttle Stats.png')
stats2 = load_image('Hornet Stats.png')
stats3 = load_image('Rocket Stats.png')
stats4 = load_image('Wasp Stats.png')
stats5 = load_image('Hawk Stats.png')
stats6 = load_image('Saturn Stats.png')
stats7 = load_image('Pluto Stats.png')
stats8 = load_image('Falcon Stats.png')
stats9 = load_image('Bumblebee Stats.png')
stats10 = load_image('Boomerang Stats.png')

clock = pygame.time.Clock()

all = pygame.sprite.RenderUpdates()
msgs = pygame.sprite.RenderUpdates()
sprites = pygame.sprite.Group()
shots = pygame.sprite.Group()
orbs = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
drones = pygame.sprite.Group()
powerups = pygame.sprite.Group()


shoot_sound = load_sound('Laser.wav')
enemy_sound = load_sound('Ufo Laser.wav')
boom_sound = load_sound('Explosion.wav')
powerup_sound = load_sound('Powerup.wav')

sounds = [shoot_sound, enemy_sound, boom_sound, powerup_sound]

SOUND_VOLUME = 100
MUSIC_VOLUME = 100



"Pixelperfect collision detection."
def PixelPerfectCollisionDetection(sp1, sp2):

    rect1 = sp1.rect;
    rect2 = sp2.rect;
    rect  = rect1.clip(rect2)

    x1 = rect.x-rect1.x
    y1 = rect.y-rect1.y
    x2 = rect.x-rect2.x
    y2 = rect.y-rect2.y

    for r in xrange(0, rect.height):
        for c in xrange(0, rect.width):

            if sp1.image.get_at((c+x1, r+y1))[3] & sp2.image.get_at((c+x2, r+y2))[3]:
                return 1

    return 0

"Pixelperfect collision detection for a sprite and a group."
def spritecollide_pp(sprite, group, dokill):

    crashed = []
    spritecollide = sprite.rect.colliderect
    ppcollide = PixelPerfectCollisionDetection
    if dokill:
        for s in group.sprites():
            if spritecollide(s.rect):
                if ppcollide(sprite, s):
                    s.kill()
                    crashed.append(s)
    else:
        for s in group.sprites():
            if spritecollide(s.rect):
                if ppcollide(sprite, s):
                    crashed.append(s)
    return crashed

"Pixelperfect collision detection for two groups of sprites."
def groupcollide_pp(groupa, groupb, dokilla, dokillb):

    crashed = {}
    SC = spritecollide_pp
    if dokilla:
        for s in groupa.sprites():
            c = SC(s, groupb, dokillb)
            if c:
                crashed[s] = c
                s.kill()
    else:
        for s in groupa.sprites():
            c = SC(s, groupb, dokillb)
            if c:
                crashed[s] = c
    return crashed


"Let's you toggle fullscreen."
def toggle_fullscreen():
    screen = pygame.display.get_surface()
    tmp = screen.convert()
    caption = pygame.display.get_caption()

    w,h = screen.get_width(),screen.get_height()
    flags = screen.get_flags()
    bits = screen.get_bitsize()

    pygame.display.init()

    screen = pygame.display.set_mode((w,h),flags^FULLSCREEN,bits)
    screen.blit(tmp,(0,0))
    pygame.display.set_caption(*caption)

    return screen


"Used for the buttons."
class Cursor:

    def __init__(self):

        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.topleft = pygame.mouse.get_pos()

"A simple button."
class Button:

    def __init__(self, text, font, command, pos, text_color, size = '', sound=None):

        button_color = 'Blue'
        self.font = font
        self.text_ren = text
        self.text = self.font.render(text, 1, text_color)
        self.shadow = self.font.render(text, 1, (0, 0, 0))

        if self.text.get_width() >= 1:
            self.size = 1
        if self.text.get_width() >= 1:
            self.size = 1
        if self.text.get_width() >= 90:
            self.size = 2
        if self.text.get_width() >= 90:
            self.size = 2
        if self.text.get_width() >= 145:
            self.size = 3
        if self.text.get_width() >= 145:
            self.size = 3

        self.sound = sound
        self.size = size

        self.non_selected_image = pygame.image.load('data/gui/%sButton Normal.png' % size)
        self.selected_image = pygame.image.load('data/gui/%sButton Highlighted.png' % size)
        self.pressed_image = pygame.image.load('data/gui/%sButton Pressed.png' % size)
        self.image = self.non_selected_image

        self.pos = pos
        self.rect = self.image.get_rect(topleft = self.pos)

        self.cursor = Cursor()
        self.command = command

        self.text_color = text_color

        self.normpos = self.rect
        self.selectpos = self.image.get_rect(topleft = self.pos).move(3, 3)
        self.text_indent = 0

        self.selected = False
        self.commanding = False
        self.commanded = False
        self.highlighted = False


    def render(self, screen):

        self.text = self.font.render(str(self.text_ren), 1, self.text_color)
        self.cursor.update()
        mousebutton = pygame.mouse.get_pressed()

        screen.blit(self.image, self.rect)
        screen.blit(self.shadow, (self.rect.center[0] + 1 - self.text.get_width()/2, self.rect.center[1] + self.text_indent + 1 - self.text.get_height()/2))
        screen.blit(self.text, (self.rect.center[0] - self.text.get_width()/2, self.rect.center[1] + self.text_indent - self.text.get_height()/2))

        if self.cursor.rect.colliderect(self.rect):
            self.image = self.selected_image
            self.highlighted = True
            if mousebutton[0]:
                if not self.selected and self.sound is not None:
                    self.sound.play()
                self.selected = True
                self.image = self.pressed_image
                self.text_indent = 4
            else:
                if self.command is not None and self.selected and not self.commanding:
                    self.commanded = True
                    self.commanding = True
                    self.command()
                self.selected = False
                self.text_indent = 0
        else:
            self.highlighted = False
            self.commanding = False
            self.text_indent = 0
            self.selected = False
            self.rect = self.normpos
            self.image = self.non_selected_image



    def change_text(self, text):
        self.text = self.font.render(text, 1, self.text_color)



class Slider:

    def __init__(self, pos, value):

        self.non_selected_image = pygame.image.load('data/gui/Slider Button Normal.png')
        self.selected_image = pygame.image.load('data/gui/Slider Button Highlighted.png')
        self.slider_image = pygame.image.load('data/gui/Slider.png')
        self.image = self.slider_image
        self.buttonimage = self.non_selected_image

        self.pos = pos
        self.rect = self.image.get_rect(topleft = self.pos)
        self.buttonrect = self.selected_image.get_rect(topleft = (pos[0] + value, pos[1]))

        self.cursor = Cursor()
        self.value = value

        self.normpos = self.rect

        self.selected = False
        self.commanding = False


    def render(self, screen):

        self.value = self.buttonrect.left - self.rect.left


        self.cursor.update()
        mousebutton = pygame.mouse.get_pressed()

        screen.blit(self.image, self.rect)
        screen.blit(self.buttonimage, self.buttonrect)

        if self.cursor.rect.colliderect(self.buttonrect):
            self.buttonimage = self.selected_image
            if mousebutton[0]:
                self.selected = True

        if self.cursor.rect.colliderect(self.rect):
            if mousebutton[0]:
                self.selected = True

        if not mousebutton[0]:
            self.selected = False
            self.buttonimage = self.non_selected_image

        if self.selected:
            self.buttonrect.centerx = self.cursor.rect.centerx


        self.buttonrect = self.buttonrect.clamp(self.rect)


"A simple input box."
class Textbox:
    def __init__(self, **args):

        self.font = pygame.font.Font("data/Hemi Head 426.TTF", 12)
        self.key_pressed = False
        self.size = (125, 17)
        self.pos = (0, 0)
        self.text = ''
        self.cursor = Cursor()
        self.selected = False
        self.highlight = ''
        self.frame = 0

        self.clock = pygame.time.Clock()
        self.fill_color = (255, 255, 255)
        self.line_color = (0, 0, 0)
        self.text_color = (0, 0, 0)

        self.x_text = 0

        self.key_pressed = False
        self.key_timer = 0

        self.char = ''


        if args.has_key('text'): self.text = args['text']
        if args.has_key('pos'): self.pos = args['pos']
        if args.has_key('size'): self.size = args['size']
        if args.has_key('font'): self.font = args['font']
        if args.has_key('line_color'): self.line_color = args['line_color']
        if args.has_key('text_color'): self.text_color = args['text_color']
        if args.has_key('fill_color'): self.fill_color = args['fill_color']

        self.ren = self.font.render(self.text + '|', 1, (0, 0, 0))
        self.image = pygame.Surface((self.size[0], self.size[1]))
        self.image.fill(self.fill_color)
        self.rect = Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.text_rect = self.ren.get_rect(topleft = self.pos)

    def render(self, screen):

        self.text_rect = self.ren.get_rect()
        self.text_rect.left = self.rect.left - self.pos[0]

        if self.ren.get_width() >= self.size[0] - 10:
            self.text_rect.right = self.rect.right - self.pos[0] - 5

        self.frame += 1
        self.cursor.update()
        mousebutton = pygame.mouse.get_pressed()

        if self.cursor.rect.colliderect(self.rect):
            if mousebutton[0]:
                self.selected = True
        if not self.cursor.rect.colliderect(self.rect):
            if mousebutton[0]:
                self.selected = False

        if self.selected:
            self.highlight = '|'
        else:
            self.highlight = ''

        if self.frame >= 100:
            self.frame = 0

        pygame.draw.rect(self.image, self.fill_color, [0, 0,
                                                   self.size[0], self.size[1]])
        self.ren = self.font.render(self.text + self.highlight, 1, self.text_color)
        self.image.blit(self.ren, (self.text_rect[0] + 2, self.text_rect[1] + 1))
        pygame.draw.rect(self.image, self.line_color, [0, 0,
                                                   self.size[0], self.size[1]], 1)
        screen.blit(self.image, self.pos)

        self.key_timer += 1

        if self.key_pressed:
            if self.key_timer >= 50:
                if not self.key_timer & 3 and not self.char == 'backspace':
                    self.text += self.char
                if not self.key_timer & 3 and self.char == 'backspace':
                    self.text = self.text[:-1]


    def update(self, event):

        if self.selected:
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.key_pressed = True
                    self.char = 'backspace'
                    self.key_timer = 0
                if event.key is not K_BACKSPACE and not event.key == K_RETURN:
                    self.text = self.text + event.unicode
                    self.key_pressed = True
                    self.char = event.unicode
                    self.key_timer = 0
            if event.type == KEYUP:
                self.key_pressed = False



"Puts up a short message on the screen."
class Msg(pygame.sprite.Sprite):
    def __init__(self, text, color, life, ypos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(FONT, 30)
        self.color = color
        msg = text
        self.image = self.font.render(msg, 1, self.color)
        self.rect = self.image.get_rect(center=(400, ypos))
        self.life = life

    def update(self, surface):
        self.life = self.life - 1
        if self.life <= 0: self.kill()


"Puts up a short message on the screen."
class Msg2(pygame.sprite.Sprite):
    def __init__(self, text, color, life, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(FONT, 17)
        self.color = color
        msg = text
        self.image = self.font.render(msg, 1, self.color)
        self.rect = self.image.get_rect(center=pos)
        self.life = life

    def update(self, surface):
        self.life = self.life - 1
        if self.life <= 0: self.kill()



"The user controlled spaceship."
class Player(pygame.sprite.Sprite):

    def __init__(self):

        pygame.sprite.Sprite.__init__(self, self.containers)

        global SHIP_TYPE, BOOST, RELOAD
        self.image = load_image(SHIP_TYPE + ' Idle.png')
        self.original_img = load_image(SHIP_TYPE + ' Idle.png')
        self.blank_image = load_image('Blank.png')

        self.angle = 0

        self.x = 400
        self.y = 240

        self.rect = self.image.get_rect(center = (self.x, self.y))

        self.x_velocity = 0
        self.y_velocity = 0

        self.frame = 0
        self.safe_timer = 100

        self.reload_timer = 0
        self.fuel_div = 0.3
        self.shield_eff = 0.0



    def update(self, surface):

        self.frame += 1
        global FUEL
        if FUEL >= 200:
            FUEL = 200

        key = pygame.key.get_pressed()
        self.rotate((key[K_LEFT] - key[K_RIGHT]) * self.roto_speed/2)

        global RELOAD
        if self.reload_timer > 0:
            self.reload_timer -= RELOAD

        if self.safe_timer > 0:
            self.safe_timer -= 1
            if self.frame & 2:
                self.image = self.blank_image


        self.rect = self.image.get_rect(center = (self.x, self.y))
        self.add_inertia()
        self.wrap(surface)
        self.cap_speed(7)



    def add_inertia(self):

        self.x += float(self.x_velocity)
        self.y += float(self.y_velocity)



    def cap_speed(self, max_speed):

        abs_vel = 0.0
        abs_vel += pow(self.x_velocity,2)+ pow(self.y_velocity,2)
        if abs_vel > pow(max_speed,2):
            ratio = pow(max_speed,2)/abs_vel
            self.x_velocity *= ratio
            self.y_velocity *= ratio



    def wrap(self, surface):

        if self.x >= surface.get_width() + self.image.get_width()/2:
            self.x = -self.image.get_width()
        if self.x < -self.image.get_width():
            self.x = surface.get_width() + self.image.get_width()/2 - 1

        if self.y >= surface.get_height() + self.image.get_height()/2:
            self.y = -self.image.get_height()
        if self.y < -self.image.get_height():
            self.y = surface.get_height() + self.image.get_height()/2 - 1



    def rotate(self, angle):

        self.oldCenter = self.rect.center

        self.angle += angle
        self.image = pygame.transform.rotate(self.original_img, self.angle)

        self.rect = self.image.get_rect()
        self.rect.center = self.oldCenter



    def accelerate(self, accel_speed):
        self.x_velocity = self.x_velocity + (math.sin(self.angle*2*math.pi/360)*-accel_speed)
        self.y_velocity = self.y_velocity + (math.cos(self.angle*2*math.pi/360)*-accel_speed)


    def kill(self):
        if self.alive():
            Explosion(self.rect.center)
        pygame.sprite.Sprite.kill(self)


"The laser/shot you fire."
class Shot(pygame.sprite.Sprite):

    def __init__(self, color, pos, angle, master_x, master_y):

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.image = pygame.transform.rotate(load_image(color + ' Laser.png'), angle)
        self.oldImage = self.image.copy()
        self.rect = self.image.get_rect()

        self.speed = 8
        self.angle = angle
        self.start_angle = self.angle

        self.x = pos[0]
        self.y = pos[1]

        global BUFFER
        self.buffer = BUFFER


        self.rad_angle = self.angle * math.pi / 180

        self.buffer_x = self.buffer * -math.sin(self.rad_angle)
        self.buffer_y = self.buffer * -math.cos(self.rad_angle)

        self.x = master_x + self.buffer_x
        self.y = master_y + self.buffer_y

        self.rect = self.image.get_rect(center = (self.x, self.y))


    def update(self, surface):

        self.rect = self.image.get_rect(center = (self.x, self.y))

        self.move_forward(self.speed, self.start_angle)
        self.kill_offscreen(surface)


    def kill_offscreen(self, surface):

        if self.x >= surface.get_width() + self.image.get_width()/2:
            self.kill()
        if self.x < -self.image.get_width():
            self.kill()

        if self.y >= surface.get_height() + self.image.get_height()/2:
            self.kill()
        if self.y < -self.image.get_height():
            self.kill()


    def move_forward(self, speed, angle):
        self.x = self.x + (math.sin(angle*2*math.pi/360)*-speed)
        self.y = self.y + (math.cos(angle*2*math.pi/360)*-speed)




"The orb enemies fire."
class Orb(pygame.sprite.Sprite):

    def __init__(self, pos, angle, master_x, master_y):

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.image = load_image('Orb.png')
        self.oldImage = self.image.copy()
        self.rect = self.image.get_rect()

        self.speed = 4
        self.angle = angle
        self.start_angle = self.angle

        self.x = pos[0]
        self.y = pos[1]

        self.buffer = 18


        self.rad_angle = self.angle * math.pi / 180

        self.buffer_x = self.buffer * -math.sin(self.rad_angle)
        self.buffer_y = self.buffer * -math.cos(self.rad_angle)

        self.x = master_x + self.buffer_x
        self.y = master_y + self.buffer_y

        self.rect = self.image.get_rect(center = (self.x, self.y))


    def update(self, surface):

        self.rect = self.image.get_rect(center = (self.x, self.y))

        self.move_forward(self.speed, self.start_angle)
        self.kill_offscreen(surface)


    def kill_offscreen(self, surface):

        if self.x >= surface.get_width() + self.image.get_width()/2:
            self.kill()
        if self.x < -self.image.get_width():
            self.kill()

        if self.y >= surface.get_height() + self.image.get_height()/2:
            self.kill()
        if self.y < -self.image.get_height():
            self.kill()


    def move_forward(self, speed, angle):
        self.x = self.x + (math.sin(angle*2*math.pi/360)*-speed)
        self.y = self.y + (math.cos(angle*2*math.pi/360)*-speed)




"The BIG, BAD, ASTEROIDS!"
class Asteroid(pygame.sprite.Sprite):

    def __init__(self, surface, size, pos, angle, speed):


        pygame.sprite.Sprite.__init__(self, self.containers)

        if size == 4:
            self.image = load_image('Big Asteroid.png')
            self.hitimage = load_image('Big Asteroid Hit.png')
            self.health = 5
        if size == 3:
            self.image = load_image('Medium Asteroid.png')
            self.hitimage = load_image('Medium Asteroid Hit.png')
            self.health = 3
        if size == 2:
            self.image = load_image('Small Asteroid.png')
            self.hitimage = load_image('Small Asteroid Hit.png')
            self.health = 1
        if size == 1:
            self.image = load_image('Tiny Asteroid.png')
            self.hitimage = load_image('Tiny Asteroid Hit.png')
        self.size = size
        self.original_img = self.image.copy()
        self.original_img2 = self.hitimage.copy()
        self.rect = self.image.get_rect()

        self.speed = speed

        self.angle = angle
        self.start_angle = self.angle

        self.x = pos[0]
        self.y = pos[1]

        self.rect = self.image.get_rect(center = (self.x, self.y))
        self.surface = surface


    def kill(self):
        self.health -= 1
        self.image = self.hitimage
        self.image = self.hitimage
        self.image = self.hitimage
        if self.health <= 0:
            pygame.sprite.Sprite.kill(self)
            if not random.randrange(15):
                Powerup('Fuel', self.rect.center)
            if not random.randrange(20):
                Powerup('Laser', self.rect.center)
            if not random.randrange(20):
                Powerup('Shield', self.rect.center)
            if not random.randrange(20):
                Powerup('Boost', self.rect.center)
            if self.size == 4:
                global SCORE
                SCORE += 100
                Msg2('+100', (255, 255, 255), 40, self.rect.center)
                Asteroid(self.surface, 3, self.rect.center, random.randrange(100, 240), random.randrange(1, 3))
                Asteroid(self.surface, 3, self.rect.center, random.randrange(100, 240), random.randrange(1, 3))
            if self.size == 3:
                global SCORE
                SCORE += 75
                Msg2('75', (255, 255, 255), 40, self.rect.center)
                Asteroid(self.surface, 2, self.rect.center, random.randrange(100, 240), random.randrange(1, 3))
                Asteroid(self.surface, 2, self.rect.center, random.randrange(100, 240), random.randrange(1, 3))
                Asteroid(self.surface, 2, self.rect.center, random.randrange(100, 240), random.randrange(1, 3))
            if self.size == 2:
                global SCORE
                SCORE += 25
                Msg2('+25', (255, 255, 255), 40, self.rect.center)
                Explosion(self.rect.center)
                #Asteroid(self.surface, 1, self.rect.center, random.randrange(100, 240), random.randrange(1, 3))
                #Asteroid(self.surface, 1, self.rect.center, random.randrange(100, 240), random.randrange(1, 3))
                #Asteroid(self.surface, 1, self.rect.center, random.randrange(100, 240), random.randrange(1, 3))
            if self.size == 1:
                Explosion(self.rect.center)


    def update(self, surface):

        self.rect = self.image.get_rect(center = (self.x, self.y))
        self.rotate(0.5)
        self.move_forward(self.speed, self.start_angle)
        self.wrap(surface)


    def move_forward(self, speed, angle):
        self.x = self.x + (math.sin(angle*2*math.pi/360)*-speed)
        self.y = self.y + (math.cos(angle*2*math.pi/360)*-speed)


    def wrap(self, surface):

        if self.x >= surface.get_width() + self.image.get_width()/2:
            self.x = -self.image.get_width()
        if self.x < -self.image.get_width():
            self.x = surface.get_width() + self.image.get_width()/2 - 1

        if self.y >= surface.get_height() + self.image.get_height()/2:
            self.y = -self.image.get_height()
        if self.y < -self.image.get_height():
            self.y = surface.get_height() + self.image.get_height()/2 - 1


    def rotate(self, angle):

        self.oldCenter = self.rect.center

        self.angle += angle
        self.image = pygame.transform.rotate(self.original_img, self.angle)
        self.hitimage = pygame.transform.rotate(self.original_img2, self.angle)

        self.rect = self.image.get_rect()
        self.rect.center = self.oldCenter


"An alien drone that shoots at you."
class Drone(pygame.sprite.Sprite):

    def __init__(self, target):

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.image = load_image('Drone Idle.png')
        self.original_img = load_image('Drone Idle.png')

        self.x = -self.image.get_width()/2
        self.y = random.randrange(400)
        self.rect = self.image.get_rect(center = (self.x, self.y))

        self.angle = 0
        self.target = target
        self.speed = 0
        self.frame = 0
        self.health = 3


    def kill(self):
        self.health -= 1
        if self.health <= 0:
            pygame.sprite.Sprite.kill(self)
            Explosion(self.rect.center)


    def update(self, surface):

        self.frame += 1
        if self.frame & 2:
            self.original_img = load_image('Drone Accelerating.png')
        else:
            self.original_img = load_image('Drone Idle.png')


        self.wrap(surface)
        self.rect = self.image.get_rect(center = (self.x, self.y))

        self.x += 3
        self.y += 2


        "Get the position of the player."
        x = self.target.x - self.x
        y = self.target.y - self.y

        angle = math.atan2(y, x)

        "Convert it to an angle."
        if x != 0 or y != 0:
            self.target_angle = int(270.0 - (angle * 180.0)/math.pi)

        "Rotate the Shuttle to the angle."
        if int(self.angle) != int(self.target_angle):
            change = self.target_angle - self.angle
            if change < -180.0:
                change = change + 360.0
            elif change >= 180.0:
                change = change - 360.0
            if change > 0.0:
                self.speed = 3
            else:
                self.speed = -3

            self.angle += self.speed


        "Rotate the Shuttle's image."
        self.rotate(self.speed)
        self.wrap(surface)

        if self.target_angle >= 360:
            self.target_angle = 0
        if self.target_angle < 0:
            self.target_angle = 360


    def wrap(self, surface):

        if self.x >= surface.get_width() + self.image.get_width()/2:
            self.x = -self.image.get_width()
        if self.x < -self.image.get_width():
            self.x = surface.get_width() + self.image.get_width()/2 - 1

        if self.y >= surface.get_height() + self.image.get_height()/2:
            self.y = -self.image.get_height()
        if self.y < -self.image.get_height():
            self.y = surface.get_height() + self.image.get_height()/2 - 1


    def rotate(self, angle):

        self.oldCenter = self.rect.center

        self.angle += angle
        self.image = pygame.transform.rotate(self.original_img, self.angle)

        self.rect = self.image.get_rect()
        self.rect.center = self.oldCenter




"An alien droid that shoots at you and follows."
class Droid(pygame.sprite.Sprite):

    def __init__(self, target):

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.image = load_image('Droid Idle.png')
        self.original_img = load_image('Droid Idle.png')

        self.x = -self.image.get_width()/2
        self.y = random.randrange(400)
        self.rect = self.image.get_rect(center = (self.x, self.y))

        self.angle = 0
        self.target = target
        self.speed = 0
        self.frame = 0
        self.health = 4

        self.x_velocity = 0
        self.y_velocity = 0


    def kill(self):
        self.health -= 1
        if self.health <= 0:
            pygame.sprite.Sprite.kill(self)
            Explosion(self.rect.center)


    def update(self, surface):

        self.frame += 1
        if self.frame & 2:
            self.original_img = load_image('Droid Accelerating.png')
        else:
            self.original_img = load_image('Droid Idle.png')


        self.wrap(surface)
        self.rect = self.image.get_rect(center = (self.x, self.y))


        "Get the position of the player."
        x = self.target.x - self.x
        y = self.target.y - self.y

        angle = math.atan2(y, x)

        "Convert it to an angle."
        if x != 0 or y != 0:
            self.target_angle = int(270.0 - (angle * 180.0)/math.pi)

        "Rotate the Shuttle to the angle."
        if int(self.angle) != int(self.target_angle):
            change = self.target_angle - self.angle
            if change < -180.0:
                change = change + 360.0
            elif change >= 180.0:
                change = change - 360.0
            if change > 0.0:
                self.speed = 3
            else:
                self.speed = -3

            self.angle += self.speed
        self.accelerate(0.1)


        self.rotate(self.speed)
        self.wrap(surface)
        self.add_inertia()
        self.cap_speed(5)

        if self.target_angle >= 360:
            self.target_angle = 0
        if self.target_angle < 0:
            self.target_angle = 360


    def wrap(self, surface):

        if self.x >= surface.get_width() + self.image.get_width()/2:
            self.x = -self.image.get_width()
        if self.x < -self.image.get_width():
            self.x = surface.get_width() + self.image.get_width()/2 - 1

        if self.y >= surface.get_height() + self.image.get_height()/2:
            self.y = -self.image.get_height()
        if self.y < -self.image.get_height():
            self.y = surface.get_height() + self.image.get_height()/2 - 1


    def rotate(self, angle):

        self.oldCenter = self.rect.center

        self.angle += angle
        self.image = pygame.transform.rotate(self.original_img, self.angle)

        self.rect = self.image.get_rect()
        self.rect.center = self.oldCenter


    def add_inertia(self):

        self.x += float(self.x_velocity)
        self.y += float(self.y_velocity)


    def cap_speed(self, max_speed):

        abs_vel = 0.0
        abs_vel += pow(self.x_velocity,2)+ pow(self.y_velocity,2)
        if abs_vel > pow(max_speed,2):
            ratio = pow(max_speed,2)/abs_vel
            self.x_velocity *= ratio
            self.y_velocity *= ratio

    def accelerate(self, accel_speed):
        self.x_velocity = self.x_velocity + (math.sin(self.angle*2*math.pi/360)*-accel_speed)
        self.y_velocity = self.y_velocity + (math.cos(self.angle*2*math.pi/360)*-accel_speed)



"Kaboom!"
class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = pos)
        self.frame = 0

    def update(self, surface):

        self.frame += 1
        try:
            self.image = self.images[self.frame/2]
            self.image.convert_alpha()
        except:
            self.kill()


"Kaboom!"
class Laser_Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = pos)
        self.frame = 0

    def update(self, surface):

        self.frame += 1
        try:
            self.image = self.images[self.frame/2]
            self.image.convert_alpha()
        except:
            self.kill()



"Kaboom!"
class Powerup_Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = pos)
        self.frame = 0

    def update(self, surface):

        self.frame += 1
        try:
            self.image = self.images[self.frame/2]
            self.image.convert_alpha()
        except:
            self.kill()



"Add some fuel."
class Powerup(pygame.sprite.Sprite):
    def __init__(self, type, pos):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = load_image(type + ' Powerup.png')
        self.type = type

        self.frame = 0
        self.plus = 1

        self.x = pos[0]
        self.y = pos[1]

        self.rect = self.image.get_rect(center = (self.x, self.y))

        if self.rect.left < 400: self.xspeed = random.choice([0.5, 0.75, 1, 1.5])
        if self.rect.left >= 400: self.xspeed = random.choice([-0.5, -0.75, -1, -1.5])
        if self.rect.top < 300: self.yspeed = random.choice([0.5, 0.75, 1, 1.5])
        if self.rect.top >= 300: self.yspeed = -random.choice([0.5, 0.75, 1, 1.5])

    def update(self, surface):

        self.x += self.xspeed
        self.y += self.yspeed

        self.rect = self.image.get_rect(center = (self.x, self.y))
        if self.rect.left >= 800: self.kill()
        if self.rect.right <= 0: self.kill()


class ParticleExplosion(pygame.sprite.Sprite):

    def __init__(self, pos):

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.size = random.randrange(5,15)
        self.color = random.choice([[255, 200, 0], [255, 0, 0], [255, 255, 0], [100, 100, 100]])
        self.image = pygame.Surface((self.size, self.size))
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        pygame.draw.ellipse(self.image, self.color, [0, 0, self.size, self.size])
        self.rect = self.image.get_rect(center = pos)

        self.opague = 255
        self.x_vel = random.randrange(-5, 5)
        self.y_vel = random.randrange(-5, 5)

    def update(self, surface):
        self.rect.move_ip(self.x_vel, self.y_vel)
        self.opague -= 10
        self.image.set_alpha(self.opague)


def Intro():
    intro = pygame.image.load('data/images/logo 1.bmp')
    intro2 = pygame.image.load('data/images/logo 2.bmp')
    fadeCount = 0
    introCount = 0
    clock = pygame.time.Clock()
    pygame.mixer.music.load('data/music/Intro.ogg')
    pygame.mixer.music.play()
    music = MUSIC2

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                elif event.key == K_RETURN:
                    pygame.mixer.music.load(music)
                    pygame.mixer.music.play(-1)
                    Menu()
        while 1:
            clock.tick(60)
            background = pygame.Surface(screen.get_size())
            background.fill((0, 0, 0))
            background.set_alpha(255)

            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        sys.exit()
                    elif event.key == K_RETURN:
                        pygame.mixer.music.load(music)
                        pygame.mixer.music.play(-1)
                        Menu()

            if fadeCount < 70:
                background.set_alpha(255-fadeCount*4)
                screen.blit(intro, (0, 0))
                screen.blit(background, (0, 0))
                pygame.display.flip()
                fadeCount = fadeCount + 1
                continue

            if introCount < 10:
                introCount = introCount + 1
            else:
                break

        fadeCount = 0
        introCount = 0
        intro = pygame.image.load('data/images/logo 1.bmp')
        intro2 = pygame.image.load('data/images/logo 2.bmp')

        while 1:
            clock.tick(60)
            background = pygame.Surface(screen.get_size())
            background.fill((0, 0, 0))
            background.set_alpha(255)

            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        sys.exit()
                    elif event.key == K_RETURN:
                        pygame.mixer.music.load(music)
                        pygame.mixer.music.play(-1)
                        Menu()

            if fadeCount < 70:
                intro.set_alpha(255-fadeCount*6)
                screen.blit(intro2, (0, 0))
                screen.blit(intro, (0, 0))
                pygame.display.flip()
                fadeCount = fadeCount + 1
                continue

            if introCount < 25:
                introCount = introCount + 1
            else:
                break

        fadeCount = 0
        introCount = 0
        intro = pygame.image.load('data/images/logo 1.bmp')
        intro2 = pygame.image.load('data/images/logo 2.bmp')

        while 1:
            clock.tick(60)
            background = pygame.Surface(screen.get_size())
            background.fill((0, 0, 0))
            background.set_alpha(255)

            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        sys.exit()
                    elif event.key == K_RETURN:
                        pygame.mixer.music.load(music)
                        pygame.mixer.music.play(-1)
                        Menu()

            if fadeCount < 65:
                intro2.set_alpha(255-fadeCount*4)
                screen.blit(background, (0, 0))
                screen.blit(intro2, (0, 0))
                pygame.display.flip()
                fadeCount = fadeCount + 1
                continue
            elif fadeCount == 65:
                fadeCount = fadeCount + 1
                screen.blit(background, (0, 0))
                pygame.display.flip()

            if introCount < 100:
                introCount = introCount + 1
            else:
                pygame.mixer.music.load(music)
                pygame.mixer.music.play(-1)
                Menu()





def Menu():

    global SCORE, LEVEL, DEAD_TIMER, SHIELD, TARGET_SHIELD, RELOAD, FUEL, BOOST, HIGHSCORE, EXP, CHEATED, INVINCIBLE
    logo = load_image('Logo.png')

    SCORE = 0
    LEVEL = 1
    SHIELD = 200
    TARGET_SHIELD = 200
    RELOAD = 20
    BOOST = 0.1
    FUEL = 200
    EXP = 0
    CHEATED = False
    INVINCIBLE = False

    pygame.mouse.set_visible(1)

    buttons = []
    buttons.append(Button('New Game', font2, Ship_Select, (280, 300), (255, 255, 255)))
    buttons.append(Button('Options', font2, Options, (280, 375), (255, 255, 255)))
    buttons.append(Button('Quit Game', font2, sys.exit, (280, 450), (255, 255, 255)))

    while 1:

        for s in sprites:
            s.kill()

        "Get input."
        event = pygame.event.poll()

        if event.type == QUIT:
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()
            if event.key == K_F1:
                toggle_fullscreen()
                pygame.time.wait(1500)

        "Draw the scene."
        screen.blit(background, (0, 0))
        screen.blit(logo, (390 - logo.get_width()/2, 70))

        ren = font.render('Copyright (C) 2007', 1, (0,0,0))
        screen.blit(ren, (401 - ren.get_width()/2, 221))
        ren = font.render('Created by Michael J. Burns', 1, (0,0,0))
        screen.blit(ren, (401 - ren.get_width()/2, 241))

        ren = font.render('Copyright (C) 2007', 1, (140,240,255))
        screen.blit(ren, (400 - ren.get_width()/2, 220))
        ren = font.render('Created by Michael J. Burns', 1, (140,240,255))
        screen.blit(ren, (400 - ren.get_width()/2, 240))
        for b in buttons:
            b.render(screen)
        pygame.display.flip()


def supersonic_music():
    pygame.mixer.music.load(MUSIC)
    pygame.mixer.music.play(-1)
def sunshine_music():
    pygame.mixer.music.load(MUSIC2)
    pygame.mixer.music.play(-1)
def diamond_music():
    pygame.mixer.music.load(MUSIC3)
    pygame.mixer.music.play(-1)
def city_music():
    pygame.mixer.music.load(MUSIC4)
    pygame.mixer.music.play(-1)

def Music():

    buttons = []
    buttons.append(Button('Soundtrack 1', font2, supersonic_music, (280, 150), (255, 255, 255)))
    buttons.append(Button('Soundtrack 2', font2, sunshine_music, (280, 225), (255, 255, 255)))
    buttons.append(Button('Soundtrack 3', font2, diamond_music, (280, 300), (255, 255, 255)))
    buttons.append(Button('Soundtrack 4', font2, city_music, (280, 375), (255, 255, 255)))
    buttons.append(Button('Options', font2, Options, (280, 450), (255, 255, 255)))

    while 1:

        "Get input."
        event = pygame.event.poll()

        if event.type == QUIT:
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Menu()
            if event.key == K_F1:
                toggle_fullscreen()
                pygame.time.wait(1500)

        "Draw the scene."
        screen.blit(background, (0, 0))

        ren = font3.render('Choose a Soundtrack', 1, (0,0,0))
        screen.blit(ren, (403 - ren.get_width()/2, 73))
        ren = font3.render('Choose a Soundtrack', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 70))

        for b in buttons:
            b.render(screen)

        pygame.display.flip()



def Options():

    global SOUND_VOLUME, MUSIC_VOLUME

    logo = load_image('Logo.png')


    pygame.mouse.set_visible(1)

    buttons = []

    buttons.append(Button('Main Menu', font2, Menu, (280, 450), (255, 255, 255)))
    buttons.append(Slider((340, 270), SOUND_VOLUME))
    buttons.append(Slider((340, 325), MUSIC_VOLUME))
    buttons.append(Button('Music...', font2, Music, (280, 375), (255, 255, 255)))

    while 1:

        "Get input."
        event = pygame.event.poll()

        if event.type == QUIT:
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()
            if event.key == K_F1:
                toggle_fullscreen()
                pygame.time.wait(1500)


        pygame.mixer.music.set_volume(float(MUSIC_VOLUME/100))
        for s in sounds:
            s.set_volume(float(SOUND_VOLUME/100))

        SOUND_VOLUME = float(buttons[1].value)
        MUSIC_VOLUME = float(buttons[2].value)

        "Draw the scene."
        screen.blit(background, (0, 0))

        ren = font3.render('Options', 1, (0,0,0))
        screen.blit(ren, (403 - ren.get_width()/2, 103))
        ren = font3.render('Options', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 100))

        ren = font.render('Sound', 1, (0,0,0))
        screen.blit(ren, (401 - ren.get_width()/2, 252))
        ren = font.render('Music', 1, (0,0,0))
        screen.blit(ren, (401 - ren.get_width()/2, 304))

        ren = font.render('Sound', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 251))
        ren = font.render('Music', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 303))

        for b in buttons:
            b.render(screen)
        pygame.display.flip()


def start_game_shuttle():
    global SHIP_TYPE
    SHIP_TYPE = 'Shuttle'
    Game()
def start_game_wasp():
    global SHIP_TYPE
    SHIP_TYPE = 'Wasp'
    Game()
def start_game_hornet():
    global SHIP_TYPE
    SHIP_TYPE = 'Hornet'
    Game()
def start_game_rocket():
    global SHIP_TYPE
    SHIP_TYPE = 'Rocket'
    Game()
def start_game_hawk():
    global SHIP_TYPE
    SHIP_TYPE = 'Hawk'
    Game()
def start_game_saturn():
    global SHIP_TYPE
    SHIP_TYPE = 'Saturn'
    Game()
def start_game_pluto():
    global SHIP_TYPE
    SHIP_TYPE = 'Pluto'
    Game()
def start_game_falcon():
    global SHIP_TYPE
    SHIP_TYPE = 'Falcon'
    Game()
def start_game_bumblebee():
    global SHIP_TYPE
    SHIP_TYPE = 'Bumblebee'
    Game()
def start_game_boomerang():
    global SHIP_TYPE
    SHIP_TYPE = 'Boomerang'
    Game()

def Ship_Select():

    global SHIP_TYPE

    logo = load_image('Logo.png')


    pygame.mouse.set_visible(1)

    buttons = []

    buttons.append(Button('Shuttle', font, start_game_shuttle, (300, 120), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Hornet', font, start_game_hornet, (300, 145), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Rocket', font, start_game_rocket, (300, 170), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Wasp', font, start_game_wasp, (300, 195), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Hawk', font, start_game_hawk, (300, 220), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Saturn', font, start_game_saturn, (300, 245), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Pluto', font, start_game_pluto, (300, 270), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Falcon', font, start_game_falcon, (300, 295), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Bumblebee', font, start_game_bumblebee, (300, 320), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Boomerang', font, start_game_boomerang, (300, 345), (255, 255, 255), 'Tiny '))
    buttons.append(Button('Main Menu', font2, Menu, (280, 450), (245, 255, 255), ''))

    while 1:

        "Get input."
        event = pygame.event.poll()

        if event.type == QUIT:
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Menu()
            if event.key == K_F1:
                toggle_fullscreen()
                pygame.time.wait(1500)

        "Draw the scene."
        screen.blit(background, (0, 0))

        ren = font3.render('Choose a ship', 1, (0,0,0))
        screen.blit(ren, (403 - ren.get_width()/2, 33))
        ren = font3.render('Choose a ship', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 30))

        if buttons[0].highlighted:
            screen.blit(stats1, (100, 220))
            screen.blit(ship1, (40, 260))
        if buttons[1].highlighted:
            screen.blit(stats2, (100, 220))
            screen.blit(ship2, (40, 255))
        if buttons[2].highlighted:
            screen.blit(stats3, (100, 220))
            screen.blit(ship3, (43, 253))
        if buttons[3].highlighted:
            screen.blit(stats4, (100, 220))
            screen.blit(ship4, (43, 258))
        if buttons[4].highlighted:
            screen.blit(stats5, (100, 220))
            screen.blit(ship5, (40, 263))
        if buttons[5].highlighted:
            screen.blit(stats6, (100, 220))
            screen.blit(ship6, (40, 255))
        if buttons[6].highlighted:
            screen.blit(stats7, (100, 220))
            screen.blit(ship7, (35, 257))
        if buttons[7].highlighted:
            screen.blit(stats8, (100, 220))
            screen.blit(ship8, (35, 257))
        if buttons[8].highlighted:
            screen.blit(stats9, (100, 220))
            screen.blit(ship9, (25, 255))
        if buttons[9].highlighted:
            screen.blit(stats10, (100, 220))
            screen.blit(ship10, (10, 255))

        for b in buttons:
            b.render(screen)

        pygame.display.flip()




def Pause_Menu():

    global SCORE, LEVEL, DEAD_TIMER, SHIELD, TARGET_SHIELD, RELOAD, FUEL, BOOST, HIGHSCORE, EXP
    global SOUND_VOLUME, MUSIC_VOLUME, CHEATED, INVINCIBLE, SHIP_TYPE

    logo = load_image('Logo.png')


    pygame.mouse.set_visible(1)

    buttons = []
    textbars = []

    buttons.append(Button('Main Menu', font2, Menu, (280, 450), (255, 255, 255)))
    buttons.append(Slider((340, 305), SOUND_VOLUME))
    buttons.append(Slider((340, 355), MUSIC_VOLUME))
    textbars.append(Textbox(text='', font=font, size=(185, 20), pos=(305, 240)))

    cheats = ['Rapid fire', 'Hey speedo!', 'Medic!', 'Out of gas', 'Machine gun',
              'Harm me not!', 'Chaos control!']

    while 1:

        "Get input."
        event = pygame.event.poll()

        if event.type == QUIT:
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                break
            if event.key == K_F1:
                toggle_fullscreen()
                pygame.time.wait(1500)
            if event.key == K_RETURN:
                for t in textbars:
                    if t.selected == True:
                        if t.text not in cheats:
                            t.text = ''
                        if t.text in cheats:
                            if t.text == cheats[0]:
                                CHEATED = True
                                RELOAD = 10
                                t.text = 'Cheat worked!'
                            if t.text == cheats[1]:
                                CHEATED = True
                                BOOST = 0.3
                                t.text = 'Cheat worked!'
                            if t.text == cheats[2]:
                                CHEATED = True
                                TARGET_SHIELD = 200
                                t.text = 'Cheat worked!'
                            if t.text == cheats[3]:
                                CHEATED = True
                                FUEL = 200
                                t.text = 'Cheat worked!'
                            if t.text == cheats[4]:
                                CHEATED = True
                                RELOAD = 5
                                t.text = 'Cheat worked!'
                            if t.text == cheats[5]:
                                CHEATED = True
                                INVINCIBLE = True
                                t.text = 'Cheat worked!'
                            if t.text == cheats[6]:
                                CHEATED = True
                                BOOST = 7
                                t.text = 'Cheat worked!'


        pygame.mixer.music.set_volume(float(MUSIC_VOLUME/100))
        for s in sounds:
            s.set_volume(float(SOUND_VOLUME/100))

        SOUND_VOLUME = float(buttons[1].value)
        MUSIC_VOLUME = float(buttons[2].value)

        "Draw the scene."
        screen.blit(background, (0, 0))

        ren = font3.render('Paused', 1, (0,0,0))
        screen.blit(ren, (403 - ren.get_width()/2, 103))
        ren = font3.render('Paused', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 100))

        ren = font.render('Sound', 1, (0,0,0))
        screen.blit(ren, (401 - ren.get_width()/2, 282))
        ren = font.render('Music', 1, (0,0,0))
        screen.blit(ren, (401 - ren.get_width()/2, 334))

        ren = font.render('Sound', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 281))
        ren = font.render('Music', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 333))

        ren = font.render('Cheat Input', 1, (0,0,0))
        screen.blit(ren, (401 - ren.get_width()/2, 221))
        ren = font.render('Cheat Input', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 220))

        ren = font.render('Press Escape to return to game', 1, (0,0,0))
        screen.blit(ren, (401 - ren.get_width()/2, 31))
        ren = font.render('Press Escape to return to game', 1, (120,240,240))
        screen.blit(ren, (400 - ren.get_width()/2, 30))

        for b in buttons:
            b.render(screen)
        for t in textbars:
            t.render(screen)
            t.update(event)
        pygame.display.flip()


"Main game script."
def Game():

    shieldbar = load_image('Shield.png')
    fuelbar = load_image('Fuel.png')
    Explosion.images = [load_image('explosion/Explosion 1.png'),
                        load_image('explosion/Explosion 2.png'),
                        load_image('explosion/Explosion 3.png'),
                        load_image('explosion/Explosion 4.png'),
                        load_image('explosion/Explosion 5.png'),
                        load_image('explosion/Explosion 6.png'),
                        load_image('explosion/Explosion 7.png'),
                        load_image('explosion/Explosion 8.png'),
                        load_image('explosion/Explosion 9.png'),
                        load_image('explosion/Explosion 10.png'),
                        load_image('explosion/Explosion 11.png')]

    Laser_Explosion.images = [load_image('Laser Explosion 1.png'),
                        load_image('Laser Explosion 2.png'),
                        load_image('Laser Explosion 3.png'),
                        load_image('Laser Explosion 4.png')]
    Powerup_Explosion.images = [load_image('Laser Explosion 2.png'),
                        load_image('Laser Explosion 3.png'),
                        load_image('Laser Explosion 4.png')]


    "Add some groups to the sprites."

    Msg.containers = msgs, sprites
    Msg2.containers = msgs, sprites

    Player.containers = all, sprites
    Shot.containers = all, shots, sprites
    Orb.containers = all, orbs, sprites
    Asteroid.containers = all, asteroids, sprites
    Drone.containers = all, drones, sprites
    Droid.containers = all, drones, sprites
    Explosion.containers = all, sprites
    Powerup.containers = all, powerups, sprites
    Laser_Explosion.containers = all, sprites
    Powerup_Explosion.containers = all, sprites
    ParticleExplosion.containers = all, sprites


    "Initialise some starting actors."
    player = Player()
    Asteroid(screen, 4, (0, 0), 200, 2)

    global SCORE, LEVEL, DEAD_TIMER, SHIELD, TARGET_SHIELD, RELOAD, FUEL, BOOST, HIGHSCORE, EXP, CHEATED, INVINCIBLE, SHIP_TYPE, LASER_COLOR, BUFFER
    LEVEL = 1
    SCORE = 0
    SHIELD = 200
    RELOAD = 20
    BOOST = 0.1
    FUEL = 200
    EXP = 0


    if SHIP_TYPE == 'Shuttle':
            LASER_COLOR = 'Purple'
            RELOAD = 6
            player.roto_speed = 8
            BOOST = 0.08
            player.fuel_div = 0.25
            player.shield_eff = 3
            BUFFER = 40
    if SHIP_TYPE == 'Hornet':
            LASER_COLOR = 'Blue'
            RELOAD = 7
            player.roto_speed = 7
            BOOST = 0.07
            player.fuel_div = 0.2
            player.shield_eff = 2
            BUFFER = 40
    if SHIP_TYPE == 'Rocket':
            LASER_COLOR = 'Yellow'
            RELOAD = 2.75
            player.roto_speed = 6
            BOOST = 0.25
            player.fuel_div = 0.0
            player.shield_eff = 0
            BUFFER = 45
    if SHIP_TYPE == 'Wasp':
            LASER_COLOR = 'Yellow'
            RELOAD = 6
            player.roto_speed = 10
            BOOST = 0.15
            player.fuel_div = 0.35
            player.shield_eff = 2
            BUFFER = 40
    if SHIP_TYPE == 'Hawk':
            LASER_COLOR = 'Green'
            RELOAD = 10
            player.roto_speed = 6
            BOOST = 0.05
            player.fuel_div = 0.2
            BUFFER = 30
            player.shield_eff = 4
    if SHIP_TYPE == 'Saturn':
            LASER_COLOR = 'Yellow'
            RELOAD = 5
            player.roto_speed = 7
            BOOST = 0.1
            player.fuel_div = 0.3
            BUFFER = 45
            player.shield_eff = 1
    if SHIP_TYPE == 'Pluto':
            LASER_COLOR = 'Yellow'
            RELOAD = 7
            player.roto_speed = 7
            BOOST = 0.06
            player.fuel_div = 0.2
            BUFFER = 45
            player.shield_eff = 5
    if SHIP_TYPE == 'Falcon':
            LASER_COLOR = 'Blue'
            RELOAD = 6
            player.roto_speed = 5.5
            BOOST = 0.065
            player.fuel_div = 0.4
            BUFFER = 45
            player.shield_eff = 2
    if SHIP_TYPE == 'Bumblebee':
            LASER_COLOR = 'Yellow'
            RELOAD = 4.5
            player.roto_speed = 4.5
            BOOST = 0.07
            player.fuel_div = 0.3
            BUFFER = 45
            player.shield_eff = 2
    if SHIP_TYPE == 'Boomerang':
            LASER_COLOR = 'Purple'
            RELOAD = 10
            player.roto_speed = 4
            BOOST = 0.1
            player.fuel_div = 0.3
            BUFFER = 50
            player.shield_eff = 5

    "Main loop."
    while 1:


        "Cap the framerate."
        clock.tick(60)


        "Get input."
        event = pygame.event.poll()

        if event.type == QUIT:
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Pause_Menu()
            if event.key == K_F1:
                toggle_fullscreen()
                pygame.time.wait(1500)

        key = pygame.key.get_pressed()

        if key[K_SPACE]:
            if player.reload_timer <= 0:
                player.reload_timer = 100
                shoot_sound.play()
                Shot(LASER_COLOR, player.rect.center, player.angle, player.rect.center[0],
                     player.rect.center[1])

        if (key[K_UP]) and FUEL > 0 and player.alive():
            player.accelerate(accel_speed=BOOST)
            FUEL -= 0.5 - player.fuel_div
            if player.frame & 2:
                player.original_img = load_image(SHIP_TYPE + ' Accel.png')
            else:
                player.original_img = load_image(SHIP_TYPE + ' Idle.png')
        elif (key[K_DOWN]) and FUEL > 0 and player.alive():
            player.accelerate(accel_speed=-BOOST)
            FUEL -= 0.5 - player.fuel_div
            if player.frame & 2:
                player.original_img = load_image(SHIP_TYPE + ' Accel.png')
            else:
                player.original_img = load_image(SHIP_TYPE + ' Idle.png')
        else:
            player.original_img = load_image(SHIP_TYPE + ' Idle.png')


        "Detect collisions."
        for shot in groupcollide_pp(shots, asteroids, 1, 1):
            Laser_Explosion(shot.rect.center)
            boom_sound.play()
            EXP += 20

        for shot in groupcollide_pp(shots, drones, 1, 1):
            Laser_Explosion(shot.rect.center)
            boom_sound.play()
            SCORE += 75
            EXP += 75
            Msg2('+75', (255, 255, 255), 40, shot.rect.center)
            Powerup(random.choice(['Fuel', 'Boost', 'Laser', 'Shield']), shot.rect.center)

        "Detect collisions."
        for orb in groupcollide_pp(orbs, asteroids, 1, 0):
            Explosion(orb.rect.center)
            boom_sound.play()

        for asteroid in spritecollide_pp(player, asteroids, 0):
            if player.safe_timer <= 0 and player.alive() and not INVINCIBLE:

                Explosion(asteroid.rect.center)
                Explosion(player.rect.center)

                asteroid.kill()
                boom_sound.play()

                TARGET_SHIELD -= (10 - player.shield_eff)*asteroid.size
                player.safe_timer = 25


        for drone in spritecollide_pp(player, drones, 0):
            if player.safe_timer <= 0 and player.alive() and not INVINCIBLE:

                Explosion(drone.rect.center)
                Explosion(player.rect.center)

                drone.kill()
                boom_sound.play()

                DEAD_TIMER = 0
                TARGET_SHIELD -= (10 - player.shield_eff)

        for orb in spritecollide_pp(player, orbs, 0):
            if player.safe_timer <= 0 and player.alive() and not INVINCIBLE:

                Laser_Explosion(orb.rect.center)
                #Laser_Explosion(player.rect.center)
                orb.kill()
                boom_sound.play()

                DEAD_TIMER = 0
                TARGET_SHIELD -= (10 - player.shield_eff)

        for powerup in spritecollide_pp(player, powerups, 1):
            if player.alive():
                if powerup.type == 'Fuel':
                    FUEL = 200
                    if player.fuel_div < 0.5:
                        player.fuel_div += 0.01
                    Msg('Full Fuel Tank!', (255, 255, 255), 100, 190)
                    EXP += 5
                if powerup.type == 'Shield':
                    TARGET_SHIELD += 50
                    if player.shield_eff < 5:
                        player.shield_eff += 0.25
                    Msg('Shield + 50', (255, 255, 255), 100, 215)
                    EXP += 100
                if powerup.type == 'Laser':
                    if RELOAD < 11: RELOAD += 0.25
                    Msg('Laser Cannons Powered Up!', (255, 255, 255), 100, 240)
                    EXP += 50
                if powerup.type == 'Boost':
                    if BOOST < 0.25:
                        BOOST += 0.005
                    Msg('Boost Powered Up!', (255, 255, 255), 100, 265)
                    EXP += 15
                powerup_sound.play()
                Powerup_Explosion(powerup.rect.center)

        if TARGET_SHIELD <= 0:
            player.kill()
        if RELOAD > 10:
            RELOAD = 10

        if TARGET_SHIELD > SHIELD:
            SHIELD += 1
        if TARGET_SHIELD < SHIELD:
            SHIELD -= 1


        "Start next level when there's no asteroids left."
        if not asteroids:
            LEVEL += 1
            Msg('Level %d' % LEVEL, (255, 255, 255), 100, 100)
            for i in range(LEVEL):
                Asteroid(screen, 4, random.choice([(0, 0), (0, 600), (400, 0), (400, 600)]), random.choice([45, 135, 225, 315]), random.randrange(1, 3))

        "Randomely spawn a enemy drone."
        if not random.randrange(650) and not drones:
            Drone(player)
        if not random.randrange(750) and not drones:
            Droid(player)

        "Randomely make the enemies shoot."
        if not random.randrange(40):
            for drone in drones:
                enemy_sound.play()
                Orb(drone.rect.center, drone.angle, drone.rect.center[0],
                     drone.rect.center[1])

        for d in drones:
            d.target = player

        "Draw the scene."
        screen.blit(background, (0, 0))
        all.draw(screen)
        all.update(screen)
        msgs.draw(screen)
        msgs.update(screen)

        if SCORE > HIGHSCORE and not CHEATED:
            HIGHSCORE = SCORE
            open('data/highscore.high', 'w').write(str(SCORE))

        if TARGET_SHIELD > 200:
            TARGET_SHIELD = 200
        if SHIELD > 200:
            SHIELD = 200

        if FUEL >= 200:
            FUEL = 200

        "Stats."
        if SHIELD > 1:
            shieldbar = pygame.transform.scale(shieldbar, (SHIELD, 10))
            screen.blit(shieldbar, (70, 15))
        if FUEL > 1:
            fuelbar = pygame.transform.scale(fuelbar, (FUEL, 10))
            screen.blit(fuelbar, (70, 35))
        screen.blit(bar, (67, 12))
        screen.blit(bar, (67, 32))

        rel_bar = pygame.transform.scale(expbar, (RELOAD*20, 10))
        screen.blit(rel_bar, (574, 502))
        ful_bar = pygame.transform.scale(expbar, (player.fuel_div*400, 10))
        screen.blit(ful_bar, (574, 522))
        rot_bar = pygame.transform.scale(expbar, (player.shield_eff*40, 10))
        screen.blit(rot_bar, (574, 542))
        bst_bar = pygame.transform.scale(expbar, (BOOST*800, 10))
        screen.blit(bst_bar, (574, 562))

        screen.blit(bar, (572, 500))
        screen.blit(bar, (572, 520))
        screen.blit(bar, (572, 540))
        screen.blit(bar, (572, 560))

        ren = font.render('Shield', 1, (255, 255, 255))
        screen.blit(ren, (10, 15))

        ren = font.render('Fuel', 1, (255, 255, 255))
        screen.blit(ren, (10, 35))

        ren = font.render('Score: %07d' % SCORE, 1, (255, 255, 255))
        screen.blit(ren, (290, 12))

        ren = font.render('Highscore: %07d' % HIGHSCORE, 1, (255, 255, 255))
        screen.blit(ren, (460, 12))

        ren = font.render('Level: %02d' % LEVEL, 1, (255, 255, 255))
        screen.blit(ren, (290, 32))


        ren = font.render('Reload', 1, (255, 255, 255))
        screen.blit(ren, (480, 500))
        ren = font.render('Fuel Tanks', 1, (255, 255, 255))
        screen.blit(ren, (480, 520))
        ren = font.render('Shield Eff.', 1, (255, 255, 255))
        screen.blit(ren, (480, 540))
        ren = font.render('Boost', 1, (255, 255, 255))
        screen.blit(ren, (480, 560))

        if TARGET_SHIELD <= 0:
            ren = font3.render('Game Over!', 1, (255, 255, 255))
            screen.blit(ren, (400 - ren.get_width()/2, 290 - ren.get_height()/2))

        pygame.display.flip()



"Run the script if launched in this window."
if __name__ == '__main__': Intro()
