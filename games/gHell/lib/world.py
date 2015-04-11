from euclid import *
import time

gravity = Vector2(0,-9.81/10) # m/s**2
max_speed = 50
            
def cap(vec, what):
        if vec.magnitude() > what:
            vec.normalize()
            return vec * what
        return vec

class Event: pass

class Collision(Event):
    def __init__(self, ball, other, where):
        self.ball = ball
        self.other = other
        self.where = where
        
    def apply(self):
        self.ball.apply_collision(self.other)
        self.other.apply_collision(self.ball)
            
    def __repr__(self):
        return "<coll of %s with %s>"%(self.ball, self.other)

class BallAtGoal(Event):
    def __init__(self, ball):
        self.ball = ball

class BallLost(Event):
    def __init__(self, ball):
        self.ball = ball

class ObjectGone(Event):
    def __init__(self, who):
        self.object = who
    
    def __repr__(self):
        return "<object_gone %s>"%self.object        

class NewObject(Event):    
    def __init__(self, who):
        self.object = who

    def __repr__(self):
        return "<object_ball %s>"%self.object
        
class GameObject:
    def set_world(self, world):
        self.world = world
      
    def __repr__(self):
        return "<o @ %s>"%(str(self.segment))
        
    def apply_collision(self, other):
        pass
        
    def collide(self, other, space_delta):
        return None
        
class Generator(GameObject):
    def __init__(self, position, lapse=5, max=10, view=None):
        if not isinstance(position, Point2):
            position = Point2(*position)
        self.position = position
        self.lapse = lapse
        self.max = 10
        self.dt = 0
        self.view = view
      
    def __repr__(self):
        return "<o @ %s>"%(str(self.position))
                
    def loop(self, dt):
        self.dt += dt
        while self.dt > self.lapse:
            self.dt -= self.lapse
            if len(self.world.balls) < self.max:
                self.world.add_ball( Ball(self.position) )
                                 
class Ball(GameObject):
    def __init__(self, position, velocity=None):
        if not isinstance(position, Point2):
            position = Point2(*position)
        self.position = position
        if velocity is None: velocity=Vector2(0,0)
        self.velocity = velocity
        
    def loop(self, delta):
        start = self.position
        movement = self.velocity*delta

        collision = True
        last = None
        while collision:
            collision = self.world.collide(self, movement, last)

            if not collision:
                q = (start + movement)
                self.position = Point2( q.x, q.y )
            else:
                movement = collision.other.reflect( 
                                (start+movement)-collision.where
                         )
                self.velocity = collision.other.reflect( self.velocity )
                self.velocity = cap(self.velocity, max_speed)

                self.position = collision.where
                start = collision.where
                last = collision.other
                
                collision.apply()

        self.velocity += gravity*delta
        self.velocity = cap(self.velocity, max_speed)
        
                
    def __repr__(self):
        return "<ball: p=%s v=%s>"%(str(self.position), self.velocity)
          
class Attractor(GameObject):
    def __init__(self, x, y, force):
        self.position = Point2(x,y)
        self.force = force
      
    def __repr__(self):
        return "<o @ %s>"%(str(self.position))
                
    def attract(self, other):
        force = self.force/((self.position.distance(other.position)/5)**2)
        vec = self.position-other.position
        vec.normalize()
        vec *= force
        other.velocity += vec
        other.velocity = cap(other.velocity, max_speed)
        
class Segment(GameObject):
    def __init__(self, x1, y1, x2, y2, bounce=1.1):
        self.segment =LineSegment2(Point2(x1, y1), Point2(x2, y2))
        self.bounce = bounce
        
    def collide(self, who, movement):
        if movement.magnitude()<0.0000002: return None

        pos = who.position
        dest = pos+movement
        segment = LineSegment2( Point2(pos.x, pos.y), Point2(dest.x, dest.y) )
        where = segment.intersect( self.segment )
        if where:
            c = Collision( who, self, where )
            return c
            
    def reflect(self, what):
        return what.reflect( Vector2(-self.segment.v.y, self.segment.v.x).normalize())*self.bounce
        
    
class LimitedLifeSegment(Segment):
    def __init__(self, x1, y1, x2, y2, bounce=1.1, life=1):
        Segment.__init__(self, x1, y1, x2, y2, bounce)
        self.life = life
        self.hits = 0
    
    def apply_collision(self, other):
        self.hits += 1
        if self.hits >= self.life:
            self.world.remove_passive(self)
            
class Floor(Segment):
    def __init__(self, height):
        self.height = height
        self.segment =Line2(Point2(-100, height), Point2(100, height))
            
    def reflect(self, what):
        return Vector2(0,0)

    def apply_collision(self, ball):
        self.world.add_event( BallLost(ball) )
        self.world.remove_ball(ball)

class Ceiling(GameObject):
    def __init__(self, height):
        self.height = height
        self.segment =Line2(Point2(-100, height), Point2(100, height))
            

class Goal(GameObject):
    def __init__(self, x, y,radius):
        self.segment =Circle(Point2(x, y), radius)
            
    def collide(self, who, movement):
        if movement.magnitude()<0.0000002: return None

        pos = who.position
        dest = pos+movement
        segment = LineSegment2( Point2(pos.x, pos.y), Point2(dest.x, dest.y) )
        try:
            where = segment.intersect( self.segment )
        except:
            where = None
        if where:
            c = Collision( who, self, where.p1 )
            return c

    def reflect(self, what):
        return what
        
    def apply_collision(self, ball):
        self.world.add_event( BallAtGoal(ball) )
        self.world.remove_ball(ball)
                    
class World:
    def __init__(self):
        self.balls = []
        self.balls_to_remove = []
        self.balls_to_append = []
        
        self.active = []
        self.active_to_remove = []
        self.active_to_append = []
        
        self.passive = []
        self.passive_to_remove = []
        self.passive_to_append = []
        
        self.attractors = []
        
        self.events = []
        
    def add_event(self, evt):
        self.events.insert( 0, evt )
        
    def get_events(self):
        for i in range(len(self.events)):
            yield self.events.pop()
                
    def add_ball(self,ball):
        ball.set_world(self)
        self.add_event(NewObject(ball))
        self.balls_to_append.append( ball )

    def remove_ball(self, ball):
        self.balls_to_remove.append(ball)
        self.add_event( ObjectGone( ball ) )
        
    def add_passive(self, what):
        what.set_world( self )
        self.add_event(NewObject(what))
        self.passive_to_append.append( what )
        
    def remove_passive(self, what):
        self.passive_to_remove.append( what )
        self.add_event( ObjectGone( what ) )
    
    def add_active(self, what):
        what.set_world( self )
        self.add_event(NewObject(what))        
        self.active_to_append.append( what )
        
    def remove_active(self, what):
        self.active_to_remove.append( what )
        self.add_event( ObjectGone( what ) )
            
    def add_attractor(self, what):
        what.set_world( self )
        self.add_event(NewObject(what))        
        self.attractors.append( what )
        
    def loop(self, delta):
        for o in self.balls: 
            o.loop(delta)
            for a in self.attractors:
                a.attract( o )
        for o in self.active: o.loop(delta)
        
        
        for g in self.balls_to_remove:
            if g in self.balls: self.balls.remove(g)
        self.balls_to_remove = []
        
        for g in self.balls_to_append:
            if not g in self.balls: self.balls.append(g)
        self.balls_to_append = []
        
        
        for g in self.passive_to_remove:
            if g in self.passive: self.passive.remove(g)
        self.passive_to_remove = []  
        
        for g in self.passive_to_append:
            if not g in self.passive: self.passive.append(g)
        self.passive_to_append = []        
        
        for g in self.active_to_remove:
            if g in self.active: self.active.remove(g)
        self.active_to_remove = []  
        
        for g in self.active_to_append:
            if not g in self.active: self.active.append(g)
        self.active_to_append = []       
        
    def collide(self, who, movement, last=None):
        colls = []
        for l in [self.active, self.passive]:
            for o in l:
                if not o == last:
                    c = o.collide(who, movement)
                    if c:
                        colls.append( c )
        if colls:
            mindist = -1
            for c in colls:
                try:
                    dist = who.position.distance(c.where)
                except:
                    self.add_event( c )
                    return c
                if mindist == -1 or mindist > dist:
                    mindist = dist
                    winner = c
            self.add_event( winner )
            return winner
        return None
        
    
if __name__ == "__main__":
    w = World()
    
    w.add_passive( Floor(0,0,2,0) )

    
    w.add_ball( ball = Ball(Point2(1, 10) ) )
    w.add_passive( Segment(0,3,2,3, bounce=2) )

    w.add_ball( ball = Ball(Point2(5, 10) ) )
    w.add_passive( Segment(4,4,6,3) )

    w.add_passive( Goal(1,30, 3.) )
    dt = 1
    print "Start..."
    while True:
        time.sleep(dt)
        w.loop(dt)
        print ">>", w.balls
        for e in w.get_events():
            print "evt:", e
         
