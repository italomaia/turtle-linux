from __future__ import division

from pyglet.gl import *
import pyglet

from entity import Entity

import data
import math

from vector import *

def interp_color(a, c0, c1):
    if a > 1: a = 1
    elif a < 0: a = 0
    b = 1 - a
    return (b*c0[0] + a*c1[0], b*c0[1] + a*c1[1], b*c0[2] + a*c1[2])

class Plant(Entity):
    
    class PlantMeta(type):
        def __init__(self, name, bases, dict):
            super(self.PlantMeta, self).__init__(name, bases, dict)
            if self.img_name is not None:
                self.all_plants.append(self)
    __metaclass__ = PlantMeta
    
    all_plants = []
    
    compost_cost = 100
    hp = 500
    death_event_name = 'on_kill_plant'
    is_evil = False
    ticks_per_heal = 2
    hotkey = 'K'
    img_name = None
    
    def __init__(self, pos, game):
        super(Plant, self).__init__(pos, game, game.mode.plant_layer)
        self.pos = pos
        self.sprite.scale = 0
        self.sprite.rotation = 0
        self.age = 0
        
    def tick(self):
        self.age += 1
        if self.sprite:
            if self.age < 31:
                self.sprite.scale = (1 - math.cos(self.age * .5) * ((30 - self.age)/30) ** 3) * self.size/self.sprite._texture.height
            self.sprite.color = interp_color(self.hp/self.__class__.hp, (100,100,100), (255,255,255))
        super(Plant, self).tick()


class Honeysuckle(Plant):
    img_name = "yellow.png"
    hotkey = 'H'
    size = 100
    compost_cost = 100
    tags = ["yellow", "sweet", "flower"]

class Rose(Plant):
    img_name = "rose.png"
    hotkey = 'R'
    size = 100
    compost_cost = 200
    tags = ["red", "flower"]
    
class Apple(Plant):
    img_name = "apple.png"
    hotkey = 'A'
    size = 150
    compost_cost = 200
    tags = ["red", "fruit", "sweet"]
    
class Bluebell(Plant):
    compost_cost = 75
    hotkey = 'B'
    img_name = "bluebell.png"
    tags = ["blue", "flower"]
    
class Daisy(Plant):
    compost_cost = 160
    hotkey = 'D'
    img_name = "daisy.png"
    tags = ["white", "flower"]
    
class Sunflower(Plant):
    compost_cost = 300
    hotkey = 'S'
    img_name = "sunflower.png"
    tags = ["yellow", "flower"]
    
class Fuchsia(Plant):
    img_name = "fuchsia.png"
    hotkey = 'F'
    compost_cost = 50
    tags = ["purple", "flower"]
    
class Cherry(Plant):
    img_name = "cherry.png"
    hotkey = 'Y'
    tags = ["pink", "red", "flower", "fruit"]
    
class Orange(Plant):
    size = 150
    hotkey = 'O'
    img_name = "orange.png"
    tags = ["fruit", "orange", "sweet"]
    
class Cabbage(Plant):
    hotkey = 'C'
    img_name = "cabbage.png"
    tags = ["green", "vegetable"]
    
class Marrow(Plant):
    img_name = "marrow.png"
    hotkey = 'M'
    tags = ["green", "vegetable"]
    compost_cost = 500
    def tick(self):
        if self.sprite: self.sprite.scale = self.size/self.sprite._texture.height
        super(Marrow, self).tick()
        self.hp += self.game.compost / 10000.
        self.size = self.hp // 10
        
class Log(Plant):
    hotkey = 'L'
    img_name = "log.png"
    compost_cost = 50
    tags = ["brown", "dark", "wood"]
    
class Carrot(Plant):
    hotkey = 'T'
    img_name = "carrot.png"
    tags = ["orange", "vegetable"]
    
