from __future__ import division
import random
import data

from pyglet.gl import *
import pyglet

from vector import Vector as v, zero as zero_vector
from common import *
from entity import Entity
from constants import *

class Creature(Entity):

    class CreatureMeta(type):
        def __init__(self, name, bases, dict):
            super(self.CreatureMeta, self).__init__(name, bases, dict)
            if self.img_name is not None:
                self.all_creatures.append(self)
                if self.is_evil:
                    self.evil_creatures.append(self)
                else:
                    self.good_creatures.append(self)
    __metaclass__ = CreatureMeta

    all_creatures = []
    evil_creatures = []
    good_creatures = []
    
    #ought to be inherited from Entity, but above metaclass requires them here
    img_name = None
    is_evil = False

    biomass = 25
    max_hp = 10
    damage = 1
    ticks_per_heal = 3
    flying = True
    sight_radius = 200
    train_time = 2000
    target_preferences = []
    death_event_name = 'on_kill_dude'
    
    @classmethod
    def hates(cls, other_cls):
        if not isinstance(other_cls, type):
            other_cls = type(other_cls)
        return (cls.is_evil is not other_cls.is_evil)
    
    def __init__(self, movement_algorithm, game):
        super(Creature, self).__init__(
            movement_algorithm.pos,
            game,
            game.mode.flying_layer if self.flying else game.mode.ground_layer)
        
        self.movement_algorithm = movement_algorithm
        self.sprite.scale = self.size/self.sprite.height
        self.target = None
        self.enemy = None
        self.target_offsets = {}
        self.reset_acquire_probs()
        self.can_attack = self.can_attack_flying if self.flying else self.can_attack_non_flying
        
    def set_dest(self, dest):
        self.movement_algorithm.dest = dest
    def get_dest(self):
        return self.movement_algorithm.dest
    dest = property(get_dest, set_dest)

    @property
    def pos(self):
        return self.movement_algorithm.pos
    
    def reset_acquire_probs(self):
        self.acquire_probs = {}
        for pref in self.target_preferences:
            self.acquire_probs[pref] = HIGH_LIKELIHOOD_TARGET_CHANGE
    
    def target_offset(self, target):
        if target not in self.target_offsets:
            self.target_offsets[target] = random_point_in_circle(zero_vector, target.radius)
        return self.target_offsets[target]

    def target_list(self, preference):
        if preference == "plants":
            return self.game.plants
        elif preference == "creatures":
            return self.game.creature_index.objects_near(self.pos, self.sight_radius)

    def acquire_target(self, r):
        target = None
        for idx, pref in enumerate(self.target_preferences):
            if r < self.acquire_probs[pref]:
                targets = self.target_list(pref)
                target = self.get_new_target(targets)
                if target is not None:
                    for pref in self.target_preferences[idx:]:
                        self.acquire_probs[pref] = LOW_LIKELIHOOD_TARGET_CHANGE
                    break
                else:
                    self.acquire_probs[pref] = HIGH_LIKELIHOOD_TARGET_CHANGE
            else:
                break
        if target is not None:
            self.target = target

    def tick(self):
        if self.dest is None or (self.target is not None and self.target.dead):
            self.target = None
            r = 0.0
        else:
            r = random.random()

        if self.target is None:
            self.reset_acquire_probs()
        self.acquire_target(r)
            
        if self.target is not None:
            self.dest = self.target.pos + self.target_offset(self.target)
        elif r < 0.02:
            self.dest = self.game.somewhere()
            
        self.movement_algorithm.advance()
        self.update_sprite()
        self.deal_damage_if_applicable()
        
        super(Creature, self).tick()
        if self.age % 3 == 0 and self.hp < self.__class__.hp:
            self.hp += 1
        
    def update_sprite(self):
        try:
            s = self.sprite
            pos = self.movement_algorithm.pos
            
            #Twiddle the underlying parameters directly, then update the coordinates.
            s._x = pos[0]
            s._y = pos[1]
            s._rotation = -self.movement_algorithm.angle
            s._update_position()
        except AttributeError: #sprite might get deleted before we tick on the tick we die.
            pass
        
        
    def deal_damage_if_applicable(self):
        if self.target is not None and self.can_attack(self.target) and self.is_in_range(self.target):
            self.deal_damage(self.target)
        else:
            if random.random() < HIGH_LIKELIHOOD_TARGET_CHANGE:
                self.enemy = self.game.creature_index.closest_to(self.pos, radius=(self.size), pred=self.can_attack)
            if self.enemy:
                self.deal_damage(self.enemy)

    def deal_damage(self, target):
        target.take_damage(self.damage, self)
        
    def is_in_range(self, other):
        return (other.pos - self.pos).length2 < (self.radius + other.radius) ** 2
    
    can_attack_flying = hates
    def can_attack_non_flying(self, other):
        return (not other.flying) and self.hates(other)
        
    def get_negative_weights_at(self, pos):
        weight = 0
        for tag in self.interest_tags:
            if self.interest_tags[tag] < 0:
                for x in self.game.tagged_entity_index[tag]:
                    weight += self.interest_tags[tag] / (1 + (pos - x.pos).length2/10000)
        return weight
        
        
    def get_new_target(self, possible_targets):
        target_weightings = []
        
        #Yes, this is intentionally outside the for loop.
        #We're using the accumulated values to select one of them.
        total_weight = 0
        for possible_target in possible_targets:
            if isinstance(possible_target, self.__class__):
                continue
            weight = 0
            for tag in possible_target.tags:
                if tag in self.interest_tags:
                    tag_weight = self.interest_tags[tag]
                    if tag_weight > 0: #negatives handled afterwards
                        weight += tag_weight
            weight += self.get_negative_weights_at(possible_target.pos)
            if(weight > 0):
                total_weight += weight
                target_weightings.append((possible_target, total_weight))
        random_value = random.random() * total_weight
        
        #no targets we have any interest in found
        if not target_weightings:
            return None
            
        for possible_target, accumulated_chance in target_weightings:
            if random_value < accumulated_chance:
                return possible_target
