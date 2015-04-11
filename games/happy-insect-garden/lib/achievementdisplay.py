from __future__ import division
import pyglet
from pyglet.gl import *
from constants import *
from common import *
import math
import data
import sound

MAX_TIME = 200
HORIZ_OFFSET = 0.065
VERT_POS = 0.1
class AchievementDisplay(object):
    def __init__(self, w, h):
        self.queue = []
        self.timer = 0
        self.w, self.h = w, h
        self.text = pyglet.text.Label(font_name=FONT_NAME, font_size=h*0.04, anchor_x='left', anchor_y='center', y=h*VERT_POS)
        self.sprite = None
        self.current = None
        self.spr_height = h*0.1
        
    def show_achievement(self, ach):
        self.queue.append(ach)
    
    def _get_current(self):
        return self._current
    def _set_current(self, val):
        self._current = val
        if self.sprite:
            self.sprite.delete()
            self.sprite = None
        if val:
            self.text.text = val.name
            self.sprite = pyglet.sprite.Sprite(data.load_image(val.img_name, centered=True), x=self.w*.5 - (self.h*HORIZ_OFFSET + self.text.content_width)*.5, y=self.h*VERT_POS)
            self.text.color = (255, 255, 255, 255)
    current = property(_get_current, _set_current)
    
    def tick(self):
        if self.timer:
            self.timer -= 1
        else:
            if self.queue:
                self.current = self.queue.pop(0)
                self.timer = MAX_TIME
            else:
                self.current = None
        
        if self.current:
            a = (MAX_TIME - self.timer)/MAX_TIME
            
            self.sprite.scale = (1 - ((1-a) ** 4) * math.cos(20*a)) * self.spr_height/self.sprite._texture.height
            if a == 0:
                sound.cheer()                        
            if a < 0.1:
                self.text.x = self.sprite.x - self.text.content_width
            elif a < 0.2:
                b = ease_cubic(10 * (a - 0.1))
                self.text.x = self.sprite.x + b * (self.h * HORIZ_OFFSET) + (1 - b) * (-self.text.content_width)
            elif a > 0.6:
                b = 2.5*(a - 0.6)
                alpha = int(255 * (1-b))
                self.sprite.opacity = alpha
                self.text.color = (255, 255, 255, alpha)
                
    def draw(self):
        if self.current:
            glPushAttrib(GL_SCISSOR_BIT)
            glEnable(GL_SCISSOR_TEST)
            glScissor(int(self.sprite.x), 0, int(self.w - self.sprite.x), self.h)
            self.text.draw()
            glPopAttrib()    
            self.sprite.draw()
