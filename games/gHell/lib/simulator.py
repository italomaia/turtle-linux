import engine, pygame
from pygame.locals import *
from world import *

def getpos(what):
    return (what.position.x, what.position.y)
    
    
BAR_START = 0
BAR_END = 1
MAX_ENERGY = 100

class LevelEnd:
    def __init__(self, win, score):
        self.win = win
        self.score = score
        
        
class Simulator(engine.Scene):
    lives = 100
    name = "Level One"
    target = 20
    energy_step = 2
    
    def init(self, *args, **kwargs):
        self.world = World()
        self.view = engine.View(self.game, 0,0, 1)
        self.setup_level(*args, **kwargs)
        self.state = BAR_START
        self.goal = 0
        self.lost = 0
        self.bars = 0
        self.energy = MAX_ENERGY
        self.stack = []
        
    def get_score(self):
        return self.goal * 2 - self.lost - self.bars*2
    def setup_level(self):
        self.world.add_active( Generator((0,10)) )
        self.world.add_passive( Segment(-10,20,10,20) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )
        
    def event(self, evt):
        if evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                self.end(LevelEnd(False, 0))
            if evt.key == K_z:
                self.view.scale(1.0/1.1)
            if evt.key == K_x:
                self.view.scale(1.1)
        elif evt.type == MOUSEBUTTONDOWN:
            print evt.button
            if evt.button == 3:
                if self.state == BAR_END:
                    self.stack.pop()
                    self.state = BAR_START
            elif evt.button == 1:
                if self.state == BAR_START and self.energy>=MAX_ENERGY:
                    pos = self.view.from_screen(evt.pos)
                    self.stack.append( pos )
                    self.state = BAR_END
                elif self.state == BAR_END:
                    start, end = self.new_segment( 
                        self.stack.pop(),
                        self.view.from_screen(evt.pos)
                        )
                    if not start==end:
                        self.world.add_passive( 
                            Segment( start[0], start[1], end[0], end[1] )
                            )
                        self.bars += 1
                        self.energy = 0
                    self.state = BAR_START
                
    def loop(self, dt):
        self.world.loop(0.3)
        self.energy += self.energy_step
        
        for evt in self.world.get_events():
            if isinstance(evt, BallAtGoal):
                self.goal += 1
            if isinstance(evt, BallLost):
                self.lost += 1                
        if self.lost > self.lives:
            self.end( LevelEnd(False, 0) )
        if self.goal > self.target:
            self.end( LevelEnd(True, self.goal * 2 - self.lost) )
            
    def update(self):
        self.game.screen.blit( self.background, (0,0) ) 
        
        for s in self.world.passive:
            if isinstance(s, Floor):
                where = self.view.to_screen( (0,s.height) )
                pygame.draw.rect( 
                    self.game.screen,
                    (124,154,255),
                    (0, where[1], self.game.x_size, self.game.y_size),
                    0
                    )
            elif isinstance(s, Ceiling):
                where = self.view.to_screen( (0,s.height) )
                pygame.draw.rect( 
                    self.game.screen,
                    (100,100,20),
                    (0, 0, self.game.x_size, where[1]),
                    0
                    )
                    
        for s in self.world.passive:
            if isinstance(s, LimitedLifeSegment):
                pygame.draw.line( 
                    self.game.screen,
                    (0,255,0),
                    self.view.to_screen( s.segment.p1 ) ,
                    self.view.to_screen( s.segment.p2 ) ,
                    )
            elif s.__class__ is Segment:
                pygame.draw.line( 
                    self.game.screen,
                    (255,255,255),
                    self.view.to_screen( s.segment.p1 ) ,
                    self.view.to_screen( s.segment.p2 ) ,
                    )
            elif isinstance(s, Goal):
                pygame.draw.circle( 
                    self.game.screen,
                    (0,0,255),
                    self.view.to_screen( s.segment.c ) ,
                    self.view.scale_to_screen( s.segment.r ) , 
                    )
        for s in self.world.attractors:
            if isinstance(s, Attractor):
                pygame.draw.circle( 
                    self.game.screen,
                    (0,255,255),
                    self.view.to_screen( s.position ) ,
                    abs(self.view.scale_to_screen( s.force/20 ) ), 
                    )
        for b in self.world.balls:
            pygame.draw.circle( 
                self.game.screen,
                (255,255,255),
                self.view.to_screen( getpos(b) ) ,
                self.view.scale_to_screen( 3 ) , 
                )        
        if self.state == BAR_END:
            start, end = self.new_segment( 
                    self.stack[-1],
                    self.view.from_screen( pygame.mouse.get_pos() ),
                   )
            start = self.view.to_screen( start )
            end = self.view.to_screen( end )            
            pygame.draw.line( 
                    self.game.screen,
                    (255,255,255),
                    start ,
                    end ,
                    )
        self.log("goal:   "+str(self.goal))
        self.log("lost:   "+str(self.lost))
        self.log("alive:  "+str(len(self.world.balls)))
        self.log("fps:    "+str( self.game.clock.get_fps() ))
        if self.energy >= MAX_ENERGY:
            self.log("energy: READY!")
        else:
            self.log("energy: "+str( self.energy ))
    
    
    def can_place(self, start, end):
        for s in self.world.passive:
            if isinstance(s, Ceiling):
                print s.height, start[1], end[1], s.height <= max(start[1], end[1])
                if s.height <= max(start[1], end[1]):
                    return False
        return True
            
    def new_segment(self, start, end):
        if start == end: return start, start+Vector2(100,0)
        s = LineSegment2( Point2(*start), Point2(*end) )
        v = s.v.normalized()
        v *= 100
        start, end = s.p1, s.p1+v
        if not self.can_place(start, end):
            return (0,0),(0,0)
        return start, end
    
    
class LevelZero(Simulator):
    lives = 50
    name = "Level Zero"
    target = 20
    
    def setup_level(self):
        self.world.add_active( Generator((-50,10)) )
        self.world.add_passive( Segment(-60,20,-40,20) )
        self.world.add_passive( Goal(50,60,15.) )
        self.world.add_passive( Floor(-200) )

class LevelOne(Simulator):
    lives = 50
    name = "Level One"
    target = 20
    
    def setup_level(self):
        self.world.add_active( Generator((0,10)) )
        self.world.add_passive( Segment(-10,20,10,20) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )

class LevelTwo(Simulator):
    lives = 25
    name = "Level Two"
    target = 20
    
    def setup_level(self):
        self.world.add_active( Generator((0,10)) )
        self.world.add_passive( Segment(-100,20,100,20) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )

class LevelThree(Simulator):
    lives = 20
    name = "Level Three"
    target = 20
    
    def setup_level(self):
        self.world.add_active( Generator((0,10)) )
        self.world.add_passive( Segment(-100,20,100,20) )
        self.world.add_passive( LimitedLifeSegment(-100,20,0,100, life=5) )
        self.world.add_passive( LimitedLifeSegment(0,100,100,20, life=5) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )

class LevelFour(Simulator):
    lives = 20
    name = "Level Four"
    target = 20
    
    def setup_level(self):
        self.world.add_active( Generator((0,10)) )
        self.world.add_passive( Segment(-100,20,100,20) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )
        self.world.add_passive( Ceiling(00) )
        
class LevelFive(Simulator):
    lives = 30
    name = "Level Five"
    target = 20
    
    def setup_level(self):
        self.world.add_active( Generator((0,10)) )
        self.world.add_passive( Segment(-100,20,100,20) )
        self.world.add_attractor( Attractor(-100,20, force=-70) )
        self.world.add_attractor( Attractor(5,-50, force=50) )
        self.world.add_attractor( Attractor(100,20, force=-70) )
        self.world.add_passive( Goal(0,60,15.) )
        self.world.add_passive( Floor(-200) )

class LevelSix(Simulator):
    lives = 50
    name = "Level Six"
    target = 20
    
    def setup_level(self):
        self.world.add_active( Generator((-125,10)) )
        self.world.add_active( Generator((125,10)) )
        
        self.world.add_passive( Segment(-150,100,150,100) )
        self.world.add_passive( Goal(0,150,15.) )
        self.world.add_passive( Floor(-200) )
        
class LevelSeven(Simulator):
    lives = 100
    name = "Level Seven"
    target = 20
    
    def setup_level(self):
        self.world.add_active( Generator((-125,10)) )
        self.world.add_active( Generator((125,10)) )
        
        self.world.add_passive( Segment(-150,100,150,100) )
        self.world.add_attractor( Attractor(-125,-50, force=-50) )
        self.world.add_attractor( Attractor(-75,-50, force=50) )
        self.world.add_attractor( Attractor(-25,-50, force=50) )
        self.world.add_attractor( Attractor(0,-150, force=-50) )        
        self.world.add_attractor( Attractor(25,-50, force=50) )
        self.world.add_attractor( Attractor(75,-50, force=50) )
        self.world.add_attractor( Attractor(125,-50, force=-50) )
        self.world.add_passive( Goal(0,150,15.) )
        self.world.add_passive( Floor(-200) )

class LevelEight(Simulator):
    lives = 100
    name = "Level Eight"
    target = 20
    
    def setup_level(self):
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
        

class Runner(engine.Scene):
    log_font_size = 40
    PRE_LEVEL = 0
    POST_LEVEL = 1
    LOST = 2
    WON  = 3
    
    levels = [
            LevelZero,
            LevelOne,
            LevelTwo,
            LevelThree,
            LevelFour,
            LevelFive,
            LevelSix,
            LevelSeven,
            LevelEight,
        ]
    def init(self):
        self.state = self.PRE_LEVEL
        self.current_level = 0
        self.score = 0
        
    def event(self, evt):
        if self.state == self.PRE_LEVEL:
            if evt.type == KEYDOWN:
                self.result = self.runScene( self.levels[self.current_level](self.game) )
                if self.result.win:
                    self.score += self.result.score
                    self.current_level += 1
                    if len(self.levels) <= self.current_level:
                        self.state = self.WON
                    else:
                        self.state = self.POST_LEVEL
                else:
                    self.state = self.LOST
                
                
        elif self.state == self.POST_LEVEL:
            if evt.type == KEYDOWN:
                self.state = self.PRE_LEVEL
                
        elif self.state == self.LOST:
            if evt.type == KEYDOWN:
                self.end()
                
        elif self.state == self.WON:
            if evt.type == KEYDOWN:
                self.end()
                
    def update(self):
        self.game.screen.blit(self.background, (0,0) )
        if self.state == self.PRE_LEVEL:
            self.log("next level")
            self.log( "level: "+self.levels[self.current_level].name )
            self.log( "score: "+str(self.score))
        if self.state == self.POST_LEVEL:
            self.log("level finished")
            self.log( "score: "+str(self.score))
        if self.state == self.LOST:
            self.log("you lost")
            self.log( "score: "+str(self.score))
        if self.state == self.WON:
            self.log("you won")
            self.log( "score: "+str(self.score))
                
def main():
    g = engine.Game(800, 600, framerate = 20, title = "simulator")
    g.run( Runner(g) ) 
    
if __name__ == "__main__":
    main()    
