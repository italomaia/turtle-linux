import swarm
import creatures
import creature
import plant
import random
from constants import *
from common import *
from vector import Vector as v

all_gardens = []



class Garden(object):
    class GardenMeta(type):
        def __init__(self, name, bases, dict):
            super(self.GardenMeta, self).__init__(name, bases, dict)
            all_gardens.append(self)
    __metaclass__ = GardenMeta

    good_creatures = [creatures.Bee]
    plants = [plant.Honeysuckle]
    initial_compost = 500
    length = 2
    cutscene_name = None
    swarm_types = [swarm.UltimateRandomSwarm]
    img_name = None

    def __init__(self, game):
        self.game = game
        self.swarms = {}
        for idx, swarm_type in enumerate(self.swarm_types):
            self.swarms[swarm_type(self.game)] = idx

    def tick(self):
        pass

    def initial_setup(self):
        self.game.add_plant_at(plant.Honeysuckle, self.game.map_centre)

    def arrivals(self):
        stuff = []
        for swarm, offset in self.swarms.iteritems():
            arrivals = swarm.arrivals_for_tick(self.game.ticks - int(offset * TICK_RATE))
            if arrivals:
                stuff.append(arrivals)
        return stuff

    def good_creature_arrival_location(self):
        return random_point_on_circle(self.game.map_centre, self.game.r)

    @property
    def have_won(self):
        if self.game.ticks < self.length * TICK_RATE: return False
        for creature in self.game.creatures:
            if creature.is_evil: return False
        return True

    @property
    def have_lost(self):
        if not self.game.plants: return True
        return False


class Tutorial(Garden):
    good_creatures = [creatures.Bee]
    plants = [plant.Honeysuckle, plant.Rose]
    swarm_types = [swarm.GradualEarwig]
    initial_compost = 100
    img_name = "tutoriallevel.png"
    cutscene_name = "tutorial.scene"

    def __init__(self, *args, **kwds):
        super(Tutorial, self).__init__(*args, **kwds)
        self.done_cutscene = False

    def initial_setup(self):
        for _ in xrange(5):
            self.game.add_creature_at(creatures.Earwig, random_point_on_circle(self.game.map_centre, self.game.r / 2))

    def tick(self):
        if not self.done_cutscene and self.game.compost >= 200:
            self.done_cutscene = True
            self.game.mode.start_cutscene("tutorial2.scene")

    @property
    def have_lost(self):
        return False

    @property
    def have_won(self):
        for p in self.game.plants:
            if isinstance(p, plant.Rose) and p.age > 60:
                return True
        return False


class ProtectTheRoses(Garden):
    good_creatures = [creatures.ShieldBug, creatures.Ladybird]
    plants = [plant.Bluebell]
    initial_compost = 2 * plant.Bluebell.compost_cost
    length = 95
    swarm_types = [swarm.AphidsAphidsAphids]
    img_name = "roselevel.png"
    cutscene_name = "roses.scene"

    def initial_setup(self):
        self.game.add_plant_at(plant.Rose, self.game.map_centre + v((-150, 0)), True)
        self.game.add_plant_at(plant.Rose, self.game.map_centre + v((150, 0)), True)
        self.game.add_creature_at(creatures.Ladybird, self.game.map_centre)

    @property
    def have_lost(self):
        for p in self.game.plants:
            if isinstance(p, plant.Rose):
                return False
        return True


class AntWar(Garden):
    good_creatures = [creatures.BlackAnt]
    plants = [plant.Orange, plant.Sunflower]
    length = 105
    swarm_types = [swarm.AntsFromAbove]
    initial_compost = 200
    img_name = "antwar.png"
    cutscene_name = "antwar.scene"

    def initial_setup(self):
        self.game.add_plant_at(plant.Orange, v((80, self.game.h/2)), True)
        self.game.add_plant_at(plant.Orange, v((self.game.w - 80, self.game.h/2)), True)

    def good_creature_arrival_location(self):
        return v((self.game.w * (0.2 + 0.6*random.random()), -200))


class TheGreatDivide(Garden):
    good_creatures = [creatures.Dragonfly, creatures.Ladybird]
    plants = [plant.Rose, plant.Fuchsia, plant.Apple, plant.Log]
    length = 95
    swarm_types = [swarm.AphidsFromLeft, swarm.LocustsFromRight]
    initial_compost = 500
    img_name = "greatdividelevel.png"
    cutscene_name = "greatdivide.scene"

    def initial_setup(self):
        self.game.add_plant_at(plant.Rose, v((0.2 * self.game.w, 0.5 * self.game.h)), True)
        self.game.add_plant_at(plant.Apple, v((0.8 * self.game.w, 0.5 * self.game.h)), True)
        self.game.add_creature_at(creatures.Ladybird, v((0.3 * self.game.w, 0.5 * self.game.h)))
        self.game.add_creature_at(creatures.Dragonfly, v((0.7 * self.game.w, 0.5 * self.game.h)))

    @property
    def have_lost(self):
        found_apple = False
        found_rose = False
        for p in self.game.plants:
            if isinstance(p, plant.Apple):
                found_apple = True
            elif isinstance(p, plant.Rose):
                found_rose = True
            if found_apple and found_rose:
                return False
        return True


class VegetablePatch(Garden):
    good_creatures = [creatures.StickInsect, creatures.Bee]
    plants = [plant.Carrot, plant.Cabbage, plant.Daisy]
    swarm_types = [swarm.SluggishSwarm] * 3
    initial_compost = 500
    img_name = "marrowlevel.png"
    cutscene_name = "vegpatch.scene"

    def initial_setup(self):
        self.game.add_plant_at(plant.Marrow, self.game.map_centre, True)

    @property
    def have_won(self):
        for p in self.game.plants:
            if isinstance(p, plant.Marrow):
                return p.size >= 500
        return False

    @property
    def have_lost(self):
        for p in self.game.plants:
            if isinstance(p, plant.Marrow):
                return False
        return True


class ButterflyCollection(Garden):
    good_creatures = [creatures.Bee, creatures.Butterfly, creatures.Woodlouse]
    plants = [plant.Honeysuckle, plant.Log, plant.Fuchsia]
    swarm_types = [swarm.ContinualWasps]
    initial_compost = 400
    img_name = "butterflylevel.png"
    cutscene_name = "butterflylevel.scene"
    
    def initial_setup(self):
        self.game.add_creature_at(creatures.Butterfly, self.game.map_centre)

    @property
    def have_won(self):
        if self.game.ticks >= TICK_RATE * 120:
            return self.game.creature_tally[creatures.Butterfly] >= 10
        return False

    @property
    def have_lost(self):
        return self.game.creature_tally[creatures.Butterfly] == 0


class MeetTheBoss(Garden):
    good_creatures = [creatures.Bee, creatures.ShieldBug, creatures.Dragonfly]
    plants = [plant.Bluebell, plant.Daisy, plant.Fuchsia, plant.Cherry]
    have_won = False
    have_lost = False
    swarm_types = [swarm.ContinualTermites, swarm.AphidsFromLeft, swarm.LocustsFromRight, swarm.Bosses]
    length = 125
    initial_compost = 200
    img_name = "birdlevel.png"

    cutscene_name = 'boss.scene'
    
    def initial_setup(self):
        self.game.add_plant_at(plant.Cherry, self.game.map_centre)
        self.game.add_plant_at(plant.Daisy, self.game.map_centre + v((200, 0)))
        self.game.add_plant_at(plant.Bluebell, self.game.map_centre - v((200, 0)))

    @property
    def have_won(self):
        if self.game.ticks >= TICK_RATE * 125:
            for c in self.game.creatures:
                if isinstance(c, creatures.Bird):
                    return False
            return True
        return False

    @property
    def have_lost(self):
        if not self.game.plants:
            return True
        return False

class RandomnessAndThenSome(Garden):
    good_creatures = creature.Creature.good_creatures
    plants = plant.Plant.all_plants
    have_won = False

    swarm_types = [swarm.UltimateRandomSwarm]
    initial_compost = 500
    cutscene_name = 'random.scene'
    
    def initial_setup(self):
        pass

    @property
    def have_lost(self):
        if self.game.ticks > 1200 and not self.game.plants:
            return True
        return False


all_gardens.remove(Garden)
