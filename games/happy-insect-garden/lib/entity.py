from __future__ import division

from pyglet.gl import *
import pyglet

from vector import Vector as v
from common import *

import data

class Entity(object):
    hp = 20
    size = 100
    tags = []
    img_name = None
    is_evil = False
    flying = False
    
    @cached
    def radius(self):
        return self.size/2
    
    def __init__(self, pos, game, layer):
        self.game = game
        self.dead = False
        self.sprite = pyglet.sprite.Sprite(data.load_image(self.img_name, centered=True), batch=game.mode.batch, group=layer, usage='stream')
        self.sprite.set_position(*pos)
        self.age = 0
        
    def tick(self):
        self.age += 1
        
        if self.age % self.ticks_per_heal == 0 and self.hp < self.__class__.hp:
            self.hp += 1
        
        
    def take_damage(self, amt, aggressor):
        self.hp -= amt
        if self.hp <= 0 and not self.dead:
            self.dead = True
            if self.sprite:
                self.sprite.delete()
            self.sprite = None
            for tag in self.tags:
                self.game.tagged_entity_index[tag].remove(self)
            self.game.dispatch_event(self.death_event_name, self.game, aggressor, self)
    
