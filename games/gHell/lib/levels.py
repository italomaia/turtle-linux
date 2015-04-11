import view
from world import *

DEFAULT_CAMERA_AREA = view.View.CAMERA_AREA

class LevelZero(view.View):
    lives = 50
    name = "Level 0: Grossini's return"
    target = 5
    order = 0
    CAMERA_AREA=(0, -90, 0, -90)
    mountainScale = 0.4
    
    def setup_level(self):
        self.step = 0.15
        self.energyRegenCoef = 100
        self.world.add_active( Generator((0,10), 10) )
        self.world.add_passive( Segment(-10,20,10,20) )
        self.world.add_passive( Goal(60,20,15.) )
        self.world.add_passive( Floor(-200) )

class LevelOne(view.View):
    lives = 50
    name = "Level 1: Easy for Grossini"
    target = 5
    order = 1
    CAMERA_AREA=(200, -150, -200, 150)
    mountainScale = 0.6
    
    def setup_level(self):
        self.step = 0.15
        self.energyRegenCoef = 100
        self.world.add_active( Generator((0,10), 10 ) )
        self.world.add_passive( Segment(-10,20,10,20) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )

class LevelTwo(view.View):
    lives = 50
    name = "Level 2: Grossini can do it"
    target = 10
    order =2 
    CAMERA_AREA=(400, -300, -400, 300)
    mountainScale = 0.8
    
    def setup_level(self):
        self.step = 0.20
        self.energyRegenCoef = 50
        self.world.add_active( Generator((0,10), 10) )
        self.world.add_passive( Segment(-100,20,100,20) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )

class LevelThree(view.View):
    lives = 20
    name = "Level 3: Grossini goes through clouds"
    order =3
    target = 10
    CAMERA_AREA=(550, -500, -550, 400)
    
    def setup_level(self):
        self.step = 0.20
        self.energyRegenCoef = 50
        self.world.add_active( Generator((0,10)) )
        self.world.add_passive( Segment(-100,20,100,20) )
        self.world.add_passive( LimitedLifeSegment(-100,20,0,100, life=5) )
        self.world.add_passive( LimitedLifeSegment(0,100,100,20, life=5) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )

class LevelFour(view.View):
    lives = 20
    name = "Level 4: Grossini, the clouds and the ceiling"
    target = 10
    order = 4
    
    def setup_level(self):
        self.step = 0.15
        self.energyRegenCoef = 50
        self.world.add_active( Generator((0,10)) )
        self.world.add_passive( Segment(-100,20,100,20) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )
        self.world.add_passive( Ceiling(20) )
        
class LevelFive(view.View):
    lives = 30
    name = "Level 5: Grossini, use the force"
    target = 5
    order = 5
    
    def setup_level(self):
        self.step = 0.15
        self.energyRegenCoef = 10
        self.world.add_active( Generator((0,10)) )
        self.world.add_passive( Segment(-100,20,100,20) )
        self.world.add_attractor( Attractor(-100,20, force=-15) )
        self.world.add_attractor( Attractor(5,-50, force=2) )
        self.world.add_attractor( Attractor(30,-70, force=1) )
        self.world.add_attractor( Attractor(60,-75, force=1) )
        self.world.add_attractor( Attractor(100,20, force=-15) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )

class LevelSix(view.View):
    lives = 30
    name = "Level 6: Grossini and Grossini"
    target = 5
    order = 6
    
    def setup_level(self):
        self.step = 0.125
        self.energyRegenCoef = 10
        self.world.add_active( Generator((-55,10)) )
        self.world.add_attractor( Attractor(-50,-20, force=1) )
        self.world.add_active( Generator((55,10)) )
        self.world.add_attractor( Attractor(50,-20, force=1) )
        
        self.world.add_passive( Segment(-100,100,100,100) )
        self.world.add_passive( Goal(0,150,15.) )
        self.world.add_passive( Floor(-200) )
        
class LevelSeven(view.View):
    lives = 40
    name = "Level 7: Grossinis, the force, and Grossini"
    target = 10
    order = 7
    
    def setup_level(self):
        self.step = 0.15
        self.energyRegenCoef = 10
        self.world.add_active( Generator((-125,10)) )
        self.world.add_active( Generator((125,10)) )
        
        self.world.add_passive( Segment(-100,100,100,100) )
        self.world.add_attractor( Attractor(-125,-50, force=-2) )
        self.world.add_attractor( Attractor(-90,-70, force=3) )
        self.world.add_attractor( Attractor(-25,-75, force=4) )
        self.world.add_attractor( Attractor(25,-75, force=4) )
        self.world.add_attractor( Attractor(90,-70, force=3) )
        self.world.add_attractor( Attractor(125,-50, force=-2) )
        self.world.add_passive( Goal(0,150,15.) )
        self.world.add_passive( Floor(-200) )

class LevelEight(view.View):
    lives = 100
    name = "Level 666: Flacid Wand's Revenge"
    target = 20
    order = 8
    textoWin = "Game finished!"
    
    def setup_level(self):
        self.step = 0.15
        self.energyRegenCoef = 10
        self.world.add_active( Generator((-75,10)) )
        self.world.add_active( Generator((75,10)) )
        
        self.world.add_passive( Segment(-150,100,150,100) )
        self.world.add_passive( Goal(0,150,15.) )
        self.world.add_passive( Floor(-200) )
        self.world.add_passive( Ceiling(150) )
        w = 50
        xbase = -150
        xstep = 150
        ybase = -200
        ystep = 30
        for x in range(3):
            for y in range(10):
                self.world.add_passive( LimitedLifeSegment(
                    xbase+xstep*x-w,
                    ybase+ystep*y,
                    xbase+xstep*x+w,
                    ybase+ystep*y,
                    life=2) )

import types

levels = []

def cmp(l1,l2):
    return l1.order.__cmp__(l2.order)
    
for name, klass in locals().items():
    if type(klass) is types.ClassType and issubclass(klass, view.View):
        levels.append( klass )
levels.sort(cmp)

for n in range(len(levels)-1):
    levels[n].nextLevel = levels[n+1]

import separador
levels[-1].nextLevel = separador.Win
