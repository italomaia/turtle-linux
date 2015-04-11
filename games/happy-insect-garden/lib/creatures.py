
from creature import Creature
from plant import Plant
from movement_algorithms import *


#good creatures
class Bee(Creature):
    speed = 6
    turn_rate = 8
    wiggle_frequency = 50

    img_name = 'beethick.png'
    size = 30

    interest_tags = {"flower": 1, "sweet":5, "evilflying":30, "blue": -10, "armoured": 1, "distractsgood": 10, "boss": 500}
    tags = ["yellow", "black", "buzzy", "goodflying"]
    target_preferences = ["creatures", "plants"]

    hp = 100
    damage = 6
    biomass = 12

    is_evil = False

    def __init__(self, pos, *args, **kwargs):
        super(Bee, self).__init__(
            WigglingMovement(
                BoundedTurningConstantSpeed,
                pos,
                self.speed,
                self.wiggle_frequency,
                self.turn_rate),
            *args,
            **kwargs)

class Dragonfly(Creature):
    speed = 12
    move_time = 10
    static_time = 20

    biomass = 15

    img_name = "dragonfly.png"
    size = 60

    damage = 6
    hp = 200

    interest_tags = {"red": 1, "yellow": 1, "fruit": 2, "pink": 2, "ugly": 4, "purple": -10, "small": 1, "boss": 500}
    tags = ["goodflying", "pretty"]
    target_preferences = ["creatures", "plants"]

    def __init__(self, pos, *args, **kwargs):
        super(Dragonfly, self).__init__(
            Zippy(ZeroTurning, pos, self.speed, self.move_time, self.static_time),
            *args,
            **kwargs)

    def deal_damage(self, target):
        target.take_damage(2*self.damage if target.__class__ is Locust else self.damage, self)

class BlackAnt(Creature):
    speed = 3
    flying = False

    img_name = "antthick.png"
    size = 25
    train_time = 3500

    hp = 40
    damage = 1
    biomass = 1

    interest_tags = {"evilant": 100, "evilground": 1, "sweet": 10, "dark": 5}
    tags = ["goodant", "goodground"]
    target_preferences = ["creatures"]

    def __init__(self, pos, game, *args, **kwargs):
        super(BlackAnt, self).__init__(
            AvoidPlants(ZeroTurning, pos, self.speed, game),
            game,
            *args,
            **kwargs)

    def deal_damage(self, target):
        target.take_damage(4*self.damage if target.__class__ is RedAnt else self.damage, self)

class ShieldBug(Creature):
    speed = 5
    flying = False
    biomass = 6

    img_name = "shieldbug.png"
    size = 40
    hp = 250
    damage = 2

    interest_tags = {"evilground": 5, "blue": 2, "green": 2, "pink": 2}
    tags = ["goodground", "armoured"]
    target_preferences = ["creatures", "plants"]

    def __init__(self, pos, *args, **kwargs):
        super(ShieldBug, self).__init__(ZeroTurning(pos, self.speed), *args, **kwargs)

class Butterfly(Creature):
    speed = 4

    img_name = "butterfly.png"
    size = 50

    interest_tags = {"yellow": 1, "red": 1, "blue": 1, "pink": 2, "brown": -5, "pretty": 2, "flower": 2}
    tags = ["goodflying", "butterfly", "pretty"]
    target_preferences = ["plants"]

    turn_rate = 3
    wiggle_frequency = 5

    hp = 90
    damage = 0
    biomass = 4

    def __init__(self, pos, *args, **kwargs):
        super(Butterfly, self).__init__(
            WigglingMovement(
                BoundedTurningConstantSpeed,
                pos,
                self.speed,
                self.wiggle_frequency,
                self.turn_rate),
            *args,
            **kwargs)
        
    def tick(self):
        super(Butterfly, self).tick()
        for p in self.game.plant_index.bucket_for_pos(self.pos):
            p.hp = min(p.__class__.hp, p.hp + 1)

class Ladybird(Creature):
    speed = 3

    img_name = "ladybird.png"
    size = 20
    biomass = 5
    hp = 100

    interest_tags = {"green": 4, "red":3, "brown": -20, "ugly": 1}
    tags = ["goodflying", "red", "black"]
    target_preferences = ["creatures", "plants"]
    sight_radius = 200
    turn_rate = 7
    wiggle_frequency = 15
    damage = 2

    def __init__(self, pos, *args, **kwargs):
        super(Ladybird, self).__init__(
            WigglingMovement(
                BoundedTurningConstantSpeed,
                pos,
                self.speed,
                self.wiggle_frequency,
                self.turn_rate),
            *args,
            **kwargs)

    def deal_damage(self, target):
        target.take_damage(3*self.damage if target.__class__ is Aphid else self.damage, self)

class StickInsect(Creature):
    speed = 2.5
    img_name = "stick.png"
    size = 35
    flying = False
    interest_tags = {"flower": 2, "fruit": 3, "vegetable": 3, "purple": -5, "evilground": 50}
    sight_radius = 100 #intentionally small - static defence
    tags = ["goodground"]
    target_preferences = ["creatures", "plants"]
    train_time = 1500

    hp = 90
    damage = 10
    biomass = 5

    #might need a special case to stop these re-targetting to another plant?
    def __init__(self, pos, *args, **kwargs):
        super(StickInsect, self).__init__(ZeroTurning(pos, self.speed), *args, **kwargs)


class Woodlouse(Creature):
    speed = 3

    img_name = "woodlouse.png"
    size = 40

    interest_tags = {"dark": 5, "wood": 5}
    tags = ["goodground", "distractsevil", "armoured"]
    wiggle_frequency = 12
    target_preferences = ["plants"]

    hp = 100
    damage = 0
    biomass = 0

    def __init__(self, pos, *args, **kwargs):
        super(Woodlouse, self).__init__(
            WigglingMovement(ZeroTurning, pos, self.speed, self.wiggle_frequency),
            *args, **kwargs)



#evil creatures

class Aphid(Creature):
    speed = 2
    img_name = "aphid.png"
    size = 20
    hp = 30
    damage = 3
    biomass = 3
    is_evil = True
    flying = False
    interest_tags = {"flower":1, "red":2}
    tags = ["evilground", "green", "small"]
    target_preferences = ["plants"]

    def __init__(self, pos, *args, **kwargs):
        super(Aphid, self).__init__(ZeroTurning(pos, self.speed), *args, **kwargs)


class Wasp(Creature):
    speed = 5
    img_name = "wasp.png"
    size = 40
    is_evil = True
    sight_radius = 200
    interest_tags = {"goodflying": 3, "distractsevil" : 20, "brown": 2, "yellow": 2}
    tags = ["evilflying"]
    target_preferences = ["creatures"]
    turn_rate = 10

    hp = 50
    damage = 5
    biomass = 2

    def __init__(self, pos, *args, **kwargs):
        super(Wasp, self).__init__(
            BoundedTurningConstantSpeed(pos, self.speed, self.turn_rate), *args, **kwargs)


class Locust(Creature):
    speed = 4
    turn_rate = 10
    wiggle_frequency = 15
    img_name = 'locust.png'
    size = 70
    is_evil = True
    interest_tags = {"flower": 1, "vegetable": 3, "fruit": 5}
    tags = ["evilflying", "ugly"]
    target_preferences = ["plants"]

    damage = 2
    hp = 150
    biomass = 6

    def __init__(self, pos, *args, **kwargs):
        super(Locust, self).__init__(
            WigglingMovement(ZeroTurning, pos, self.speed, self.wiggle_frequency),
            *args,
            **kwargs)

    def deal_damage(self, target):
        target.take_damage(2*self.damage if isinstance(target, Plant) else self.damage, self)


class RedAnt(Creature):
    speed = 3
    flying = False
    biomass = 6

    img_name = "redant.png"
    size = 25

    hp = 15
    damage = 3
    sight_radius = 100

    interest_tags = {"flower": 6, "vegetable": 20, "sweet": 3, "goodant":1}
    tags = ["evilant", "evilground"]
    is_evil = True
    target_preferences = ["creatures", "plants"]

    def __init__(self, pos, *args, **kwargs):
        super(RedAnt, self).__init__(ZeroTurning(pos, self.speed), *args, **kwargs)

class Termite(Creature):
    speed = 4
    flying = False
    biomass = 2

    img_name = "termite.png"
    size = 30
    damage = 2

    interest_tags = {"white": 5, "fruit": 3, "blue": 3, "flower": 1, "wood": 1, "goodant": 10}
    tags = ["evilant", "evilground"]
    is_evil = True
    target_preferences = ["creatures", "plants"]

    def __init__(self, pos, *args, **kwargs):
        super(Termite, self).__init__(ZeroTurning(pos, self.speed), *args, **kwargs)

class Slug(Creature):
    speed = 1.5
    flying = False

    img_name = "slug.png"
    size = 40

    interest_tags = {"vegetable": 5, "green": 5, "fruit": 1}
    tags = ["evilground", "slimy"]
    is_evil = True
    target_preferences = ["plants"]

    hp = 100
    damage = 3
    biomass = 9

    def __init__(self, pos, *args, **kwargs):
        super(Slug, self).__init__(ZeroTurning(pos, self.speed), *args, **kwargs)

class Snail(Creature):
    speed = 1.5
    flying = False

    img_name = "snail.png"
    size = 40

    interest_tags = {"vegetable": 5, "green": 5, "fruit": 1}
    tags = ["evilground", "slimy", "armoured"]
    is_evil = True
    target_preferences = ["plants"]

    hp = 300
    damage = 5
    biomass = 14

    def __init__(self, pos, *args, **kwargs):
        super(Snail, self).__init__(ZeroTurning(pos, self.speed), *args, **kwargs)

class Earwig(Creature):
    speed = 4
    flying = False

    img_name = "earwig.png"
    size = 60

    is_evil = True
    interest_tags = {"fruit": 5, "brown": 10}
    tags = ["evilground", "distractsgood"]
    #target_preferences = ["plants", "creatures"]
    biomass = 3

    def __init__(self, pos, game, *args, **kwargs):
        super(Earwig, self).__init__(
            AvoidPlants(ZeroTurning, pos, self.speed, game),
            game,
            *args,
            **kwargs)

class StagBeetle(Creature):
    speed = 3
    flying = False

    img_name = "stagbeetle.png"
    size = 75

    hp = 500
    damage = 8
    biomass = 50
    sight_radius = 300
    
    is_evil = True
    interest_tags = {"goodground": 3, "yellow": 1, "distractsevil": 20}
    tags = ["evilground", "tank"]
    target_preferences = ["creatures", "plants"]
    wiggle_frequency = 20

    def __init__(self, pos, *args, **kwargs):
        super(StagBeetle, self).__init__(
            WigglingMovement(ZeroTurning, pos, self.speed, self.wiggle_frequency),
            *args,
            **kwargs)


class PrayingMantis(Creature):
    speed = 5
    flying = False

    img_name = "mantis.png"
    size = 80
    hp = 2500
    damage = 15
    biomass = 100
    sight_radius = 500

    is_evil = True
    interest_tags = {"goodground": 10, "yellow": 1, "red": 1, "green": 1, "distractsevil": 20}
    tags = ["evilground", "tank"]
    target_preferences = ["creatures"]
    wiggle_frequency = 20

    def __init__(self, pos, *args, **kwargs):
        super(PrayingMantis, self).__init__(
            WigglingMovement(ZeroTurning, pos, self.speed, self.wiggle_frequency),
            *args,
            **kwargs)

class Bird(Creature):
    speed = 5
    turn_rate = 3

    flying = True

    img_name = "bird.png"
    size = 200
    hp = 25000
    damage = 40
    biomass = 500
    sight_radius = 1000

    is_evil = True
    interest_tags = {"goodflying": 5, "goodground": 3, "evilflying": 1, "evilground": 1, "pink": 1, "pretty": 10, "distractsevil": 20}
    tags = ["evilflying", "boss"]
    target_preferences = ["creatures"]

    def __init__(self, pos, *args, **kwargs):
        super(Bird, self).__init__(
            BoundedTurningConstantSpeed(pos, self.speed, self.turn_rate),
            *args,
            **kwargs)

    def can_attack_flying(self, other):
        return "boss" not in other.tags

