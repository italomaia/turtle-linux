import os

import data
import pyglet
import functools
import game
import cPickle
import traceback
import creatures
import plant
import garden
import creature

from constants import *
from common import *


## Achievement handler

class AchievementHandler(pyglet.event.EventDispatcher):
    event_types = ['on_achievement']

    def __init__(self):
        self.achievements = []
        self.triggers = dict((evt, []) for evt in game.Game.event_types)
        self.variables = []
        self.var_updaters = dict((evt, []) for evt in game.Game.event_types)
        for evt in game.Game.event_types:
            setattr(self, evt, functools.partial(self.handle_event, evt))

    def add_achievement(self, ach):
        self.achievements.append(ach)
        self.triggers[ach.event].append(ach)

    def add_variable(self, var):
        self.variables.append(var)
        for event in var.events:
            self.var_updaters[event].append(var)

    def handle_event(self, event, *args, **kwargs):
        try:
            for var in self.var_updaters[event]:
                getattr(var, event)(*args, **kwargs)
            for ach in self.triggers[event]:
                if not ach.achieved and ach.is_achieved(*args, **kwargs):
                    ach.achieve()
                    self.dispatch_event('on_achievement', ach)
        except TypeError:
            import traceback
            traceback.print_exc()
            raise
        if event == 'on_game_end':
            self.save()

    def load(self):
        try: variables, achievements = cPickle.load(open(ACHIEVEMENT_FILE, 'rb'))
        except: return
        for var in self.variables:
            try: var.value = variables[var.id]
            except: pass
        for ach in self.achievements:
            if ach.id in achievements: ach.achieved = True

    def save(self):
        variables = dict((var.id, var.value) for var in self.variables)
        achievements = [ach.id for ach in self.achievements if ach.achieved]
        cPickle.dump((variables, achievements), open(ACHIEVEMENT_FILE, 'wb'))

handler = AchievementHandler()

import atexit
atexit.register(handler.save)


## Achievements

class Achievement(object):
    def __init__(self, event, trigger, conditions, name, description=None, id=None, img_name='rosette.png'):
        if not os.path.exists(os.path.join(DATA_DIR, "images", img_name)):
            print "missing award: %r" % img_name
            img_name = 'rosette.png'
        self.event = event
        self.trigger = trigger
        self.conditions = conditions
        self.name = name
        self.description = description or name
        self.id = id or name
        self.achieved = False
        self.img_name = img_name

    def achieve(self):
        self.achieved = True

    def is_achieved(self, *args, **kwargs):
        if not self.trigger or self.trigger(*args, **kwargs):
            for condition in self.conditions:
                if not condition():
                    return False
            return True
        return False


## Tracked variables

class TrackedVariable(object):

    def __init__(self):
        self.value = 0
        self.events = []

    def register(self):
        handler.add_variable(self)

    @cached
    def id(self):
        namespace = globals()
        for name in namespace:
            if namespace[name] is self:
                return name
        raise Exception

    def __ge__(self, other):
        if isinstance(other, TrackedVariable):
            return lambda: self.value >= other.value
        return lambda: self.value >= other

    def __gt__(self, other):
        if isinstance(other, TrackedVariable):
            return lambda: self.value > other.value
        return lambda: self.value > other

    def __le__(self, other):
        if isinstance(other, TrackedVariable):
            return lambda: self.value <= other.value
        return lambda: self.value <= other

    def __lt__(self, other):
        if isinstance(other, TrackedVariable):
            return lambda: self.value < other.value
        return lambda: self.value < other

    def __eq__(self, other):
        if isinstance(other, TrackedVariable):
            return lambda: self.value == other.value
        return lambda: self.value == other

class CounterVariable(TrackedVariable):
    def __init__(self, event, *conditions):
        super(CounterVariable, self).__init__()
        self.events += [event]
        self.conditions = conditions
        setattr(self, event, self.inc)
        self.register()

    def inc(self, *args, **kwargs):
        for condition in self.conditions:
            if not condition(*args, **kwargs): return
        self.value += 1

class PerGameCounterVariable(CounterVariable):
    def __init__(self, event, *conditions):
        super(CounterVariable, self).__init__()
        self.events += [event, 'on_game_start']
        self.conditions = conditions

        setattr(self, event, self.inc)
        self.register()

    def on_game_start(self, game, *args, **kwargs):
        self.value = 0

class GameStateVariable(TrackedVariable):
    def __init__(self, event, name):
        super(GameStateVariable, self).__init__()

        self.events += [event]
        self.name = name
        setattr(self, event, self.update)
        self.register()

    def update(self, game, *args, **kwargs):
        self.value = getattr(game, self.name)


## Utility

def add_achievement(*args, **kwargs):
    handler.add_achievement(Achievement(*args, **kwargs))


## Triggers

def got_creature(creature_type):
    def did_get(game, c):
        return c is creature_type
    return did_get

def killed_creature(creature_type):
    def did_kill(game, k, d):
        return type(d) is creature_type
    return did_kill

def planted_plant(plant_type):
    def did_plant(game, p):
        return type(p) is plant_type and game.ticks > 0
    return did_plant

def won_garden(garden_type):
    def did_win(game):
        return game.victorious and type(game.garden) is garden_type
    return did_win


## Recruiting dudes

bees_got = CounterVariable('on_add_creature', got_creature(creatures.Bee))
dragonflies_got = CounterVariable('on_add_creature', got_creature(creatures.Dragonfly))
black_ants_got = CounterVariable('on_add_creature', got_creature(creatures.BlackAnt))
shield_bugs_got = CounterVariable('on_add_creature', got_creature(creatures.ShieldBug))
butterflies_got = CounterVariable('on_add_creature', got_creature(creatures.Butterfly))
ladybirds_got = CounterVariable('on_add_creature', got_creature(creatures.Ladybird))
stick_insects_got = CounterVariable('on_add_creature', got_creature(creatures.StickInsect))
woodlice_got = CounterVariable('on_add_creature', got_creature(creatures.Woodlouse))

add_achievement('on_add_creature', None, [bees_got >= 3], "Attract 3 bees!", img_name='beeaward1.png')
add_achievement('on_add_creature', None, [bees_got >= 15], "Attract 15 bees!", img_name='beeaward2.png')
add_achievement('on_add_creature', None, [bees_got >= 120], "Attract 120 bees!", img_name='beeaward3.png')

add_achievement('on_add_creature', None, [dragonflies_got >= 3], "Attract 3 dragonflies!", img_name='dragonaward1.png')
add_achievement('on_add_creature', None, [dragonflies_got >= 15], "Attract 15 dragonflies!", img_name='dragonaward2.png')
add_achievement('on_add_creature', None, [dragonflies_got >= 120], "Attract 120 dragonflies!", img_name='dragonaward3.png')

add_achievement('on_add_creature', None, [black_ants_got >= 30], "Attract 30 ants!", img_name='antaward1.png')
add_achievement('on_add_creature', None, [black_ants_got >= 150], "Attract 150 ants!", img_name='antaward2.png')
add_achievement('on_add_creature', None, [black_ants_got >= 1200], "Attract 1200 ants!", img_name='antaward3.png')

add_achievement('on_add_creature', None, [shield_bugs_got >= 3], "Attract 3 shield bugs!", img_name='shieldaward1.png')
add_achievement('on_add_creature', None, [shield_bugs_got >= 15], "Attract 15 shield bugs!", img_name='shieldaward2.png')
add_achievement('on_add_creature', None, [shield_bugs_got >= 120], "Attract 120 shield bugs!", img_name='shieldaward3.png')

add_achievement('on_add_creature', None, [butterflies_got >= 6], "Attract 6 butterflies!", img_name='butterflyaward1.png')
add_achievement('on_add_creature', None, [butterflies_got >= 30], "Attract 30 butterflies!", img_name='butterflyaward2.png')
add_achievement('on_add_creature', None, [butterflies_got >= 240], "Attract 240 butterflies!", img_name='butterflyaward3.png')

add_achievement('on_add_creature', None, [ladybirds_got >= 3], "Attract 3 ladybirds!", img_name='ladyaward1.png')
add_achievement('on_add_creature', None, [ladybirds_got >= 15], "Attract 15 ladybirds!", img_name='ladyaward2.png')
add_achievement('on_add_creature', None, [ladybirds_got >= 120], "Attract 120 ladybirds!", img_name='ladyaward3.png')

add_achievement('on_add_creature', None, [stick_insects_got >= 3], "Attract 3 stick insects!", img_name='stickaward1.png')
add_achievement('on_add_creature', None, [stick_insects_got >= 15], "Attract 15 stick insects!", img_name='stickaward2.png')
add_achievement('on_add_creature', None, [stick_insects_got >= 120], "Attract 120 stick insects!", img_name='stickaward3.png')

add_achievement('on_add_creature', None, [woodlice_got >= 3], "Attract 3 woodlice!", img_name='woodlouseaward1.png')
add_achievement('on_add_creature', None, [woodlice_got >= 15], "Attract 15 woodlice!", img_name='woodlouseaward2.png')
add_achievement('on_add_creature', None, [woodlice_got >= 120], "Attract 120 woodlice!", img_name='woodlouseaward3.png')

## Killing enemies

aphids_killed = CounterVariable('on_kill_dude', killed_creature(creatures.Aphid))
wasps_killed = CounterVariable('on_kill_dude', killed_creature(creatures.Wasp))
locusts_killed = CounterVariable('on_kill_dude', killed_creature(creatures.Locust))
red_ants_killed = CounterVariable('on_kill_dude', killed_creature(creatures.RedAnt))
termites_killed = CounterVariable('on_kill_dude', killed_creature(creatures.Termite))
slugs_killed = CounterVariable('on_kill_dude', killed_creature(creatures.Slug))
snails_killed = CounterVariable('on_kill_dude', killed_creature(creatures.Snail))
earwigs_killed = CounterVariable('on_kill_dude', killed_creature(creatures.Earwig))
stag_beetles_killed = CounterVariable('on_kill_dude', killed_creature(creatures.StagBeetle))
praying_mantises_killed = CounterVariable('on_kill_dude', killed_creature(creatures.PrayingMantis))

add_achievement('on_kill_dude', None, [aphids_killed >= 50], "Kill 50 aphids!", img_name='aphidaward1.png')
add_achievement('on_kill_dude', None, [aphids_killed >= 250], "Kill 250 aphids!", img_name='aphidaward2.png')
add_achievement('on_kill_dude', None, [aphids_killed >= 750], "Kill 750 aphids!", img_name='aphidaward3.png')

add_achievement('on_kill_dude', None, [wasps_killed >= 10], "Kill 10 wasps!", img_name='waspaward1.png')
add_achievement('on_kill_dude', None, [wasps_killed >= 50], "Kill 50 wasps!", img_name='waspaward2.png')
add_achievement('on_kill_dude', None, [wasps_killed >= 150], "Kill 150 wasps!", img_name='waspaward3.png')

add_achievement('on_kill_dude', None, [locusts_killed >= 10], "Kill 10 locusts!", img_name='locustaward1.png')
add_achievement('on_kill_dude', None, [locusts_killed >= 50], "Kill 50 locusts!", img_name='locustaward2.png')
add_achievement('on_kill_dude', None, [locusts_killed >= 150], "Kill 150 locusts!", img_name='locustaward3.png')

add_achievement('on_kill_dude', None, [red_ants_killed >= 30], "Kill 30 red ants!", img_name='redantaward1.png')
add_achievement('on_kill_dude', None, [red_ants_killed >= 150], "Kill 150 red ants!", img_name='redantaward2.png')
add_achievement('on_kill_dude', None, [red_ants_killed >= 450], "Kill 450 red ants!", img_name='redantaward3.png')

add_achievement('on_kill_dude', None, [termites_killed >= 10], "Kill 10 termites!", img_name='termiteaward1.png')
add_achievement('on_kill_dude', None, [termites_killed >= 50], "Kill 50 termites!", img_name='termiteaward2.png')
add_achievement('on_kill_dude', None, [termites_killed >= 150], "Kill 150 hundred termites!", img_name='termiteaward3.png')

add_achievement('on_kill_dude', None, [slugs_killed >= 10], "Kill 10 slugs!", img_name='slugaward1.png')
add_achievement('on_kill_dude', None, [slugs_killed >= 50], "Kill 50 slugs!", img_name='slugaward2.png')
add_achievement('on_kill_dude', None, [slugs_killed >= 150], "Kill 150 slugs!", img_name='slugaward3.png')

add_achievement('on_kill_dude', None, [snails_killed >= 10], "Kill 10 snails!", img_name='snailaward1.png')
add_achievement('on_kill_dude', None, [snails_killed >= 50], "Kill 50 snails!", img_name='snailaward2.png')
add_achievement('on_kill_dude', None, [snails_killed >= 150], "Kill 150 snails!", img_name='snailaward3.png')

add_achievement('on_kill_dude', None, [earwigs_killed >= 50], "Kill 50 earwigs!", img_name='earwigaward1.png')
add_achievement('on_kill_dude', None, [earwigs_killed >= 150], "Kill 150 earwigs!", img_name='earwigaward2.png')
add_achievement('on_kill_dude', None, [earwigs_killed >= 1000], "Kill 1000 earwigs!", img_name='earwigaward3.png')

add_achievement('on_kill_dude', None, [stag_beetles_killed >= 10], "Kill 10 stag beetles!", img_name='stagbeetleaward1.png')
add_achievement('on_kill_dude', None, [stag_beetles_killed >= 50], "Kill 50 stag beetles!", img_name='stagbeetleaward2.png')
add_achievement('on_kill_dude', None, [stag_beetles_killed >= 150], "Kill 150 stag beetles!", img_name='stagbeetleaward3.png')

add_achievement('on_kill_dude', None, [praying_mantises_killed >= 5], "Kill 5 praying mantises!", img_name='mantisaward1.png')
add_achievement('on_kill_dude', None, [praying_mantises_killed >= 25], "Kill 25 praying mantises!", img_name='mantisaward2.png')
add_achievement('on_kill_dude', None, [praying_mantises_killed >= 75], "Kill 75 praying mantises!", img_name='mantisaward3.png')

## Planting

honeysuckles_planted = CounterVariable('on_add_plant', planted_plant(plant.Honeysuckle))
roses_planted = CounterVariable('on_add_plant', planted_plant(plant.Rose))
apples_planted = CounterVariable('on_add_plant', planted_plant(plant.Apple))
bluebells_planted = CounterVariable('on_add_plant', planted_plant(plant.Bluebell))
daisies_planted = CounterVariable('on_add_plant', planted_plant(plant.Daisy))
sunflowers_planted = CounterVariable('on_add_plant', planted_plant(plant.Sunflower))
fuchsias_planted = CounterVariable('on_add_plant', planted_plant(plant.Fuchsia))
cherries_planted = CounterVariable('on_add_plant', planted_plant(plant.Cherry))
oranges_planted = CounterVariable('on_add_plant', planted_plant(plant.Orange))
cabbages_planted = CounterVariable('on_add_plant', planted_plant(plant.Cabbage))
marrows_planted = CounterVariable('on_add_plant', planted_plant(plant.Marrow))
logs_planted = CounterVariable('on_add_plant', planted_plant(plant.Log))
carrots_planted = CounterVariable('on_add_plant', planted_plant(plant.Carrot))

pergame_honeysuckles_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Honeysuckle))
pergame_roses_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Rose))
pergame_apples_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Apple))
pergame_bluebells_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Bluebell))
pergame_daisies_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Daisy))
pergame_sunflowers_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Sunflower))
pergame_fuchsias_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Fuchsia))
pergame_cherries_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Cherry))
pergame_oranges_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Orange))
pergame_cabbages_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Cabbage))
pergame_marrows_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Marrow))
pergame_logs_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Log))
pergame_carrots_planted = PerGameCounterVariable('on_add_plant', planted_plant(plant.Carrot))

add_achievement('on_add_plant', None, [honeysuckles_planted >= 3], "Plant 3 honeysuckles!", img_name='yellowaward1.png')
add_achievement('on_add_plant', None, [pergame_honeysuckles_planted >= 8], "Plant 8 honeysuckles in one game!", img_name='yellowaward2.png')
add_achievement('on_add_plant', None, [honeysuckles_planted >= 25], "Plant 25 honeysuckles!", img_name='yellowaward3.png')

add_achievement('on_add_plant', None, [roses_planted >= 3], "Plant 3 roses!", img_name='roseaward1.png')
add_achievement('on_add_plant', None, [pergame_roses_planted >= 8], "Plant 8 roses in one game!", img_name='roseaward2.png')
add_achievement('on_add_plant', None, [roses_planted >= 25], "Plant 25 roses!", img_name='roseaward3.png')

add_achievement('on_add_plant', None, [apples_planted >= 3], "Plant 3 apples!", img_name='appleaward1.png')
add_achievement('on_add_plant', None, [pergame_apples_planted >= 8], "Plant 8 apples in one game!", img_name='appleaward2.png')
add_achievement('on_add_plant', None, [apples_planted >= 25], "Plant 25 apples!", img_name='appleaward3.png')

add_achievement('on_add_plant', None, [bluebells_planted >= 3], "Plant 3 bluebells!", img_name='bluebellaward1.png')
add_achievement('on_add_plant', None, [pergame_bluebells_planted >= 8], "Plant 8 bluebells in one game!", img_name='bluebellaward2.png')
add_achievement('on_add_plant', None, [bluebells_planted >= 25], "Plant 25 bluebells!", img_name='bluebellaward3.png')

add_achievement('on_add_plant', None, [daisies_planted >= 3], "Plant 3 daisies!", img_name='daisyaward1.png')
add_achievement('on_add_plant', None, [pergame_daisies_planted >= 8], "Plant 8 daisies in one game!", img_name='daisyaward2.png')
add_achievement('on_add_plant', None, [daisies_planted >= 25], "Plant 25 daisies!", img_name='daisyaward3.png')

add_achievement('on_add_plant', None, [sunflowers_planted >= 3], "Plant 3 sunflowers!", img_name='sunfloweraward1.png')
add_achievement('on_add_plant', None, [pergame_sunflowers_planted >= 8], "Plant 8 sunflowers in one game!", img_name='sunfloweraward2.png')
add_achievement('on_add_plant', None, [sunflowers_planted >= 25], "Plant 25 sunflowers!", img_name='sunfloweraward3.png')

add_achievement('on_add_plant', None, [fuchsias_planted >= 3], "Plant 3 fuchsias!", img_name='fuchsiaaward1.png')
add_achievement('on_add_plant', None, [pergame_fuchsias_planted >= 8], "Plant 8 fuchsias in one game!", img_name='fuchsiaaward2.png')
add_achievement('on_add_plant', None, [fuchsias_planted >= 25], "Plant 25 fuchsias!", img_name='fuchsiaaward3.png')

add_achievement('on_add_plant', None, [cherries_planted >= 3], "Plant 3 cherries!", img_name='cherryaward1.png')
add_achievement('on_add_plant', None, [pergame_cherries_planted >= 8], "Plant 8 cherries in one game!", img_name='cherryaward2.png')
add_achievement('on_add_plant', None, [cherries_planted >= 25], "Plant 25 cherries!", img_name='cherryaward3.png')

add_achievement('on_add_plant', None, [oranges_planted >= 3], "Plant 3 oranges!", img_name='orangeaward1.png')
add_achievement('on_add_plant', None, [pergame_oranges_planted >= 8], "Plant 8 oranges in one game!", img_name='orangeaward2.png')
add_achievement('on_add_plant', None, [oranges_planted >= 25], "Plant 25 oranges!", img_name='orangeaward3.png')

add_achievement('on_add_plant', None, [cabbages_planted >= 3], "Plant 3 cabbages!", img_name='cabbageaward1.png')
add_achievement('on_add_plant', None, [pergame_cabbages_planted >= 8], "Plant 8 cabbages in one game!", img_name='cabbageaward2.png')
add_achievement('on_add_plant', None, [cabbages_planted >= 25], "Plant 25 cabbages!", img_name='cabbageaward3.png')

add_achievement('on_add_plant', None, [marrows_planted >= 3], "Plant 3 marrows!", img_name='marrowaward1.png')
add_achievement('on_add_plant', None, [pergame_marrows_planted >= 8], "Plant 8 marrows in one game!", img_name='marrowaward2.png')
add_achievement('on_add_plant', None, [marrows_planted >= 25], "Plant 25 marrows!", img_name='marrowaward3.png')

add_achievement('on_add_plant', None, [logs_planted >= 3], "Place 3 logs!", img_name='logaward1.png')
add_achievement('on_add_plant', None, [pergame_logs_planted >= 8], "Place 8 logs in one game!", img_name='logaward2.png')
add_achievement('on_add_plant', None, [logs_planted >= 25], "Place 25 logs!", img_name='logaward3.png')

add_achievement('on_add_plant', None, [carrots_planted >= 3], "Plant 3 carrot!", img_name='carrotaward1.png')
add_achievement('on_add_plant', None, [pergame_carrots_planted >= 8], "Plant 8 carrots in one game!", img_name='carrotaward2.png')
add_achievement('on_add_plant', None, [carrots_planted >= 25], "Plant 25 carrots!", img_name='carrotaward3.png')

## Winning levels

add_achievement('on_game_end', won_garden(garden.Tutorial), [], "Complete the tutorial!", img_name='tutoriallevelaward.png')
add_achievement('on_game_end', won_garden(garden.ProtectTheRoses), [], "Protect the roses!", img_name='roselevelaward.png')
add_achievement('on_game_end', won_garden(garden.AntWar), [], "Survive the ant war!", img_name='antwarlevelaward.png')
add_achievement('on_game_end', won_garden(garden.TheGreatDivide), [], "Conquer the great divide!", img_name='greatdividelevelaward.png')
add_achievement('on_game_end', won_garden(garden.VegetablePatch), [], "Win the marrow contest!", img_name='marrowlevelaward.png')
add_achievement('on_game_end', won_garden(garden.ButterflyCollection), [], "Collect the butterflies!", img_name='butterflylevelaward.png')
add_achievement('on_game_end', won_garden(garden.MeetTheBoss), [], "Defeat the ultimate challenge!", img_name='birdlevelaward.png')
## Super winning levels

# ProtectTheRoses -- never lose a bluebell
def superwin_roses(game):
    if not game.victorious:
        return False
    if type(game.garden) is garden.ProtectTheRoses:
        bluebells = game.plant_tally.get(plant.Bluebell, 0)
        return bluebells == pergame_bluebells_planted.value
    return False
add_achievement('on_game_end', superwin_roses, [], "Protect the roses without losing a bluebell!", img_name='roselevelspecialaward.png')

# AntWar -- keep two sunflowers
def superwin_antwar(game):
    if not game.victorious:
        return False
    if type(game.garden) is garden.AntWar:
        return game.plant_tally.get(plant.Sunflower, 0) >= 2
    return False
add_achievement('on_game_end', superwin_antwar, [], "Survive the ant war with two sunflowers!", img_name='antlevelspecialaward.png')

# TheGreatDivide -- only plant 6 plants
def superwin_greatdivide(game):
    if not game.victorious:
        return False
    if type(game.garden) is garden.TheGreatDivide:
        # We start with 2, so this number is 8.
        return pergame_plants_planteed.value <= 8
    return False
add_achievement('on_game_end', superwin_antwar, [], "Conquer the great divide with at most 6 additional plants!", img_name='dividelevelspecialaward.png')

# VegetablePatch -- have 25 vegetables
def superwin_marrow(game):
    if not game.victorious:
        return False
    if type(game.garden) is garden.VegetablePatch:
        marrows = game.plant_tally.get(plant.Marrow, 0)
        carrots = game.plant_tally.get(plant.Carrot, 0)
        cabbages = game.plant_tally.get(plant.Cabbage, 0)
        return marrows + carrots + cabbages >= 25
    return False
add_achievement('on_game_end', superwin_marrow, [], "Win the marrow contest with a very large vegetable patch!", img_name='marrowlevelspecialaward.png')

# ButterflyCollection -- collect 20 butterflies
def superwin_butterfly(game):
    if not game.victorious:
        return False
    if type(game.garden) is garden.ButterflyCollection:
        return game.creature_tally.get(creatures.Butterfly, 0) >= 20
    return False
add_achievement('on_game_end', superwin_butterfly, [], "Collect ten additional butterflies.", img_name='butterflylevelspecialaward.png')

## Killing bosses


## Miscellaneous

def in_random_level(game, *args, **kwds):
    return type(game.garden) is garden.RandomnessAndThenSome

compost = GameStateVariable('on_gain_compost', 'compost')
play_time = CounterVariable('on_second_pass')
random_time = PerGameCounterVariable('on_second_pass', in_random_level)

add_achievement('on_gain_compost', None, [compost >= 1000], "Collect 1000 compost!", img_name='compostaward1.png')
add_achievement('on_gain_compost', None, [compost >= 5000], "Collect 5000 compost!", img_name='compostaward2.png')
add_achievement('on_gain_compost', None, [compost >= 10000], "Collect 10000 compost!", img_name='compostaward3.png')

add_achievement('on_second_pass', None, [play_time >= 10 * 60], "Play for 10 minutes!", img_name='timeaward1.png')
add_achievement('on_second_pass', None, [play_time >= 30 * 60], "Play for 30 minutes!", img_name='timeaward2.png')
add_achievement('on_second_pass', None, [play_time >= 60 * 60], "Play for an hour!", img_name='timeaward3.png')

add_achievement('on_second_pass', None, [random_time >= 1 * 60], "Survive for 1 minute in the random garden!", img_name='randomaward1.png')
add_achievement('on_second_pass', None, [random_time >= 2 * 60], "Survive for 2 minutes in the random garden!", img_name='randomaward2.png')
add_achievement('on_second_pass', None, [random_time >= 3 * 60], "Survive for 3 minutes in the random garden!", img_name='randomaward3.png')
add_achievement('on_second_pass', None, [random_time >= 5 * 60], "Survive for 5 minutes in the random garden!", img_name='randomaward4.png')
add_achievement('on_second_pass', None, [random_time >= 8 * 60], "Survive for 8 minutes in the random garden!", img_name='randomaward5.png')
add_achievement('on_second_pass', None, [random_time >= 13 * 60], "Survive for 13 minutes in the random garden!", img_name='randomaward6.png')

## Creature counters

def make_creature_gets():
    result = []
    for c in creature.Creature.all_creatures:
        id = "_got_%s" % c.__name__
        var = CounterVariable('on_add_creature', got_creature(c))
        globals()[id] = var
        result.append(var)
    return result
creature_gets = make_creature_gets()

## Level counters

def make_level_wins():
    result = []
    for g in garden.all_gardens:
        id = "_won_%s" % g.__name__
        var = CounterVariable('on_game_end', won_garden(g))
        globals()[id] = var
        result.append(var)
    return result
levels = make_level_wins()

## Load saved data

handler.load()
