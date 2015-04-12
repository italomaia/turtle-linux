from __future__ import division

import pyglet
import random

from collections import defaultdict
from spatialindex import SpatialIndex, PlantCoverageIndex

from common import *
from creatures import *
import creatures
from plant import Honeysuckle

import garden

from vector import Vector as v



class Game(pyglet.event.EventDispatcher):
    event_types = ['on_kill_dude', 'on_gain_compost', 'on_second_pass', 'on_game_start', 'on_game_end', 'on_add_plant', 'on_kill_plant', 'on_add_creature']

    def __init__(self, mode, garden_cls, w, h):
        self.mode = mode
        self.w = w
        self.h = h
        self.r = (w**2 + h**2) ** 0.5 / 2
        
        self.victorious = False
        self.compost = 1000000
        self.ticks = 0
        self.garden = garden_cls(self)
        
        self.plants = []
        self.plant_index = PlantCoverageIndex()
        self.plant_tally = {}
        self.rebuild_plant_index()
        
        self.creatures = []
        self.creature_queues = dict([(creature_type, 0) for creature_type in self.garden.good_creatures])
        self.creature_index = SpatialIndex()
        
        self.tagged_entity_index = defaultdict(list)
        
        self.garden.initial_setup()
        self.compost = self.garden.initial_compost
        self.count_creatures()
        
        
    def count_creatures(self):
        self.creature_tally = defaultdict(int)
        self.creature_index.reset()
        for c in self.creatures:
            self.creature_index.add(c)
            self.creature_tally[type(c)] += 1

    @cached
    def map_centre(self):
        return v((self.w/2,self.h/2))

    def tick(self):
        if self.ticks == 0:
            self.dispatch_event('on_game_start', self)
        
        for creatures, base_location in self.garden.arrivals():
            for creature_type, num in creatures:
                for i in xrange(num):
                    self.add_creature_at(creature_type, random_point_in_circle(base_location, 100))
        
        self.count_creatures()
        for c in self.creatures:
            c.tick()        
        for p in self.plants:
            p.tick()
        biomass = sum(c.biomass for c in self.creatures if c.dead)
        if biomass:
            self.compost += biomass
            self.dispatch_event('on_gain_compost', self)
        self.creatures = [c for c in self.creatures if not c.dead]
        old_plants = self.plants
        self.plants = [p for p in self.plants if not p.dead]
        if old_plants != self.plants:
            self.rebuild_plant_index()

        if self.garden.have_lost:
            self.mode.game_over()

        else:
            # don't switch_handler twice by winning and losing on the same tick
            self.ticks += 1
            if self.ticks % 60 == 0:
                self.dispatch_event('on_second_pass', self)
                
            if self.garden.have_won:
                self.victorious = True
                self.mode.game_over()

        for creature_type in self.creature_queues:
            if self.ticks % (creature_type.train_time//max(1, self.vacant_spaces(creature_type))) == 0:
                self.creature_queues[creature_type] += 1
            if self.creature_queues[creature_type] > 0:
                if self.can_enter(creature_type):
                    self.add_creature_at(creature_type, self.garden.good_creature_arrival_location())
                    self.creature_queues[creature_type] -= 1
        self.garden.tick()
    
    def can_enter(self, creature_type):
        return self.vacant_spaces(creature_type) > 0
    
    def vacant_spaces(self, creature_type):
        return max(0, self.total_allowed(creature_type) - self.creature_tally[creature_type])
    
    def total_allowed(self, creature_type):
        total = 0
        for plant in self.plants:
            for tag in creature_type.interest_tags:
                if tag in plant.tags:
                    weight = creature_type.interest_tags[tag]
                    if weight > 0:
                        total += weight
        return total

    def add_plant_at(self, plant_type, pos, autoage=False):
        if (self.compost >= plant_type.compost_cost and 
            plant_type.size * .5 < pos.x < self.w - plant_type.size * .5 and
            plant_type.size * .5 < pos.y < self.h - plant_type.size * .5):
            for other in self.plants:
                if (other.pos - pos).length < (other.size + plant_type.size) * .5: return None
            plant = plant_type(pos, self)
            self.plant_tally.setdefault(plant_type, 0)
            self.plant_tally[plant_type] += 1
            if autoage:
                plant.age = 29
                plant.tick()
            self.plants.append(plant)
            self.compost -= plant_type.compost_cost
            self.plant_index.add(plant)
            for tag in plant.tags:
                self.tagged_entity_index[tag].append(plant)
            self.dispatch_event('on_add_plant', self, plant)
            return plant
            
    def add_creature_at(self, creature_type, pos):
        creature = creature_type(pos, self)
        self.creatures.append(creature)
        for tag in creature.tags:
            self.tagged_entity_index[tag].append(creature)
        self.dispatch_event('on_add_creature', self, creature_type)

    def on_kill_plant(self, game, aggressor, plant):
        self.plant_tally[type(plant)] -= 1

    def somewhere(self):
        return v((distribute_outwards(random.random()) * self.w,
                  distribute_outwards(random.random()) * self.h))

    
    def rebuild_plant_index(self):
        self.plant_index = PlantCoverageIndex()
        for p in self.plants:
            self.plant_index.add(p)
    
    def is_in_plant(self, test_pos):
        return self.plant_index.is_covered(test_pos)
    
    def end(self):
        self.dispatch_event('on_game_end', self)
        

#maps (0, 1) to (0, 1), distributed outwards.
def distribute_outwards(x):
    from math import pow
    r = x ** (1/3)
    if random.random() < (1/2):
        r = -r
    r = (r+1)/2
    return r
