from __future__ import division

import random

from collections import defaultdict

from functools import partial
from common import *
from constants import *

from creatures import *

def dynamic_arrival_number(game, creature_type):
    total = 0
    for tag, value in creature_type.interest_tags.items():
        for p in game.plants:
            if tag in p.tags:
                total += value
    return total

def add(a, b):
    return a + b
def times(a, b):
    return a * b
def divide_by(a, b):
    return b / a

class DynamicScaler(object):
    def __init__(self):
        self.funcs = []
        #self.mul = 1
        #self.add = 0
    def __call__(self, game, cons):
        base_num = dynamic_arrival_number(game, cons)
        for f in self.funcs:
            base_num = f(base_num)     
        return int(base_num)
    
    

    def __mul__(self, other):
        self.funcs.append(partial(times, other))
        return self
    def __rmul__(self, other):
        self.funcs.append(partial(times, other))
        return self
    
    def __div__(self, other):
        self.funcs.append(partial(divide_by, other))
        return self
    def __truediv__(self, other):
        self.funcs.append(partial(divide_by, other))
        return self
    def __add__(self, other):
        self.funcs.append(partial(add, other))
        return self
    def __radd(self, other):
        self.funcs.append(partial(add, other))
        return self
        
class Swarm(object):

    base_arrivals_by_sec = {}

    def __init__(self, game):
        self.game = game
           
    def spawn_location(self):
        return self.random_spawn_location()
    
    def random_spawn_location(self):
        return random_point_on_circle(self.game.map_centre, self.game.r)
                
    def arrivals_for_tick(self, tick):
        #return self.arrivals[tick]
        if tick % TICK_RATE != 0:
            return None
        sec = tick // TICK_RATE
        #for t, arrivals in self.base_arrivals_by_sec.items():
        arrivals = self.arrivals_by_sec.get(sec)
        if arrivals is None:
            return None
        try:
            cons, num, location = arrivals
        except ValueError:
            cons, num = arrivals
            location = self.spawn_location()
        if not isinstance(num, int):
            num = num(self.game, cons)
        return ([(cons, num)], location)
    
class AphidsAphidsAphids(Swarm):
    
    arrivals_by_sec = {
         2: (Aphid, 1),
         5: (Aphid, 2),
        10: (Aphid, 3),
        15: (Aphid, 5),
        20: (Aphid, 8),
        25: (Aphid, 8),
        30: (Aphid, 12),
        35: (Aphid, 12),
        40: (Aphid, 12),
        45: (Aphid, 16),
        50: (Aphid, 16),
        59: (Aphid, 16),
        60: (Aphid, 16),
        69: (Aphid, 21),
        70: (Aphid, 21),
        79: (Aphid, 21),
        80: (Aphid, 32),
        89: (Aphid, 32),
        90: (Aphid, 42)
    }

class AntsFromAbove(Swarm):
    dynamic = DynamicScaler
    
    arrivals_by_sec = {
         5: (RedAnt, 3),
        10: (RedAnt, 3),
        15: (RedAnt, dynamic() / 3),
        20: (RedAnt, 8),
        25: (RedAnt, 3),
        26: (RedAnt, 3),
        27: (RedAnt, 3),
        28: (RedAnt, 3),
        29: (RedAnt, 3),
        30: (RedAnt, 3),
        35: (RedAnt, dynamic() / 2),
        45: (RedAnt, dynamic() / 2),
        50: (RedAnt, dynamic() / 2),
        55: (RedAnt, 5),
        56: (RedAnt, 5),
        57: (RedAnt, 5),
        58: (RedAnt, 5),
        59: (RedAnt, 5),
        60: (RedAnt, 5),
        65: (RedAnt, 20),
        70: (RedAnt, dynamic() / 2),
        75: (RedAnt, dynamic() / 2),
        80: (RedAnt, 8),
        81: (RedAnt, 8),
        82: (RedAnt, 8),
        83: (RedAnt, 8),
        84: (RedAnt, 8),
        85: (RedAnt, 8),
        90: (RedAnt, 15),
        95: (PrayingMantis, dynamic()),
        100: (RedAnt, dynamic())
    }
    
    def spawn_location(self):
        return v((random.random() * self.game.w, self.game.h + 100))
    
    
class AphidsFromLeft(Swarm):
    arrivals_by_sec = {
        10: (Aphid, 3),
        15: (Aphid, 5),
        20: (Aphid, 8),
        25: (Aphid, 8),
        30: (Aphid, 12),
        35: (Aphid, 12),
        40: (Aphid, 12),
        45: (Aphid, 16),
        50: (Aphid, 16),
        69: (Aphid, 21),
        70: (Aphid, 21),
        79: (Aphid, 21),
        80: (Aphid, 32),
        89: (Aphid, 32),
        90: (Aphid, 42)
    }
    
    def spawn_location(self):
        return v((-100, random.random() * self.game.h))
    
class LocustsFromRight(Swarm):
    arrivals_by_sec = {
        10: (Locust, 1),
        15: (Locust, 2),
        20: (Locust, 3),
        25: (Locust, 3),
        30: (Locust, 5),
        35: (Locust, 5),
        40: (Locust, 5),
        45: (Locust, 8),
        50: (Locust, 8),
        55: (Locust, 8),
        60: (Locust, 8),
        65: (Locust, 13),
        70: (Locust, 13),
        75: (Locust, 13),
        80: (Locust, 13),
        85: (Locust, 13),
        90: (Locust, 21)    
    }
    
    def spawn_location(self):
        return v((self.game.w + 100, random.random() * self.game.h))


class SluggishSwarm(Swarm):

    def __init__(self, *args, **kwds):
        super(SluggishSwarm, self).__init__(*args, **kwds)
        self.slug_max = 2
        self.snail_max = 1

    def arrivals_for_tick(self, tick):
        res = []
        if tick != tick % 300 == 0:
            slug_min, snail_min = self.slug_max // 2, self.snail_max // 2
            res.append((Slug, random.randint(slug_min, self.slug_max)))
            res.append((Snail, random.randint(snail_min, self.snail_max)))
            if random.random() < 0.1:
                self.slug_max += 2
            if random.random() < 0.1:
                self.snail_max += 1
        return res, self.random_spawn_location()


class ContinualWasps(Swarm):
    def __init__(self, *args, **kwds):
        super(ContinualWasps, self).__init__(*args, **kwds)
        self.wasp_rate = 60
        self.wasp_ramp_up = 120
    def arrivals_for_tick(self, tick):
        res, location = [], (0, 0)
        if tick > 600 and tick % self.wasp_rate == 0:
            res.append((Wasp, 1))
            location = self.random_spawn_location()
        if tick % self.wasp_ramp_up == 0:
            self.wasp_rate = max(10, self.wasp_rate-1)
        return res, location


class GradualEarwig(Swarm):
    def arrivals_for_tick(self, tick):
        res, location = [], (0, 0)
        if tick % 100 == 50:
            res.append((Earwig, 3))
            location = self.random_spawn_location()
        return res, location
    
class ContinualTermites(Swarm):
    def __init__(self, *args, **kwds):
        super(ContinualTermites, self).__init__(*args, **kwds)
        self.termite_rate = 60
        self.termite_ramp_up = 120
    def arrivals_for_tick(self, tick):
        res, location = [], (0, 0)
        if tick > 600 and tick % self.termite_rate == 0:
            res.append((Termite, 1))
            location = self.random_spawn_location()
        if tick % self.termite_ramp_up == 0:
            self.termite_rate = max(5, self.termite_rate-1)
        return res, location

class Bosses(Swarm):
    arrivals_by_sec = {
        40: (StagBeetle, 1),
        60: (StagBeetle, 1),
        80: (PrayingMantis, 1),
        90: (StagBeetle, 1),
        100: (PrayingMantis, 1),
        110: (StagBeetle, 1),
        120: (Bird, 1),
        121: (Locust, 10),
        122: (Locust, 10),
        123: (Locust, 10),
        124: (Locust, 10),
        125: (Locust, 10)
    }
    
class UltimateRandomSwarm(Swarm):
    dynamic = DynamicScaler
    
    creature_danger = {
        Aphid: 3,
        Wasp: 6,
        Locust: 8,
        RedAnt: 30,
        Termite: 2,
        Slug: 7,
        Snail: 14,
        Earwig: 10,
        StagBeetle: 20,
        PrayingMantis: 30,
        Bird: 6000
    }
        
        
    def arrivals_for_tick(self, tick):
        res, location = [], (0, 0)
        if tick < 600:
            pass
        else:
            for creature in Creature.evil_creatures:
                if random.random() < 0.0005:
                    res.append((creature, ((self.dynamic() + 3) * tick / (100 * self.creature_danger[creature]))(self.game, creature)))
            if res:
                location = self.random_spawn_location()
        return res, location
        
