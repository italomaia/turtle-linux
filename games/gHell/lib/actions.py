import time, random
from euclid import *

class Manager:
    def __init__(self):
        self.now = 0
        self.actions = []
        self.to_remove = []
                        
    def do(self, who, what):
        a = what(self, who)
        a._start()
        self.actions.append( a )
        
        
    def done(self, what):
        self.to_remove.append( what )
        
    def loop(self, dt):
        self.now += dt
        for action in self.actions:
            action._loop(dt)
            if action.done():
                self.done( action )
                
            
        for x in self.to_remove:
            self.actions.remove( x )
        self.to_remove = []
        
class Action:
    def __init__(self, manager, target, *args, **kwargs):
        self.manager = manager
        self.target = target
        self.init(*args, **kwargs)
        
    def _start(self):
        self.start_time = self.manager.now
        self.runtime = 0
        self.start()
        
    def _loop(self, dt):
        self.loop(dt)
        self.runtime += dt
        
    def init(self):
        pass

    def done(self): return True
            
    def start(self):
        pass
    def end(self):
        pass
    def loop(self, dt):
        pass
        
class ActionCreator:
    def __init__(self, creator):
        self.creator = creator
        
    def __call__(self, *args, **kwargs):
        return self.creator(*args, **kwargs)
        
    def __add__(self, other):
        return sequence(self, other)
            
class ActionSequencer(Action):
    def init(self, actions):
        self.actions = actions
        self.count = 0
        
    def instantiate(self):
        self.current = self.actions[self.count](self.manager, self.target)
        self.current._start()
    
    def start(self):
        self.instantiate()
        
    def done(self):
        return ( self.count >= len(self.actions) )
        
    def loop(self, dt):
        self.current._loop(dt)
        if self.current.done():
            self.count += 1
            if not self.done():
                self.instantiate()            
        
def sequence(*actions):
    def create(manager, target):
        return ActionSequencer(manager, target, 
            actions)
    return ActionCreator(create)
    
class TimeWarperAction(Action):
    def init(self, warper, action):
        self.action = action(self.manager, self.target)
        self.warper = warper
                
    def start(self):
        self.action._start()
        
    def done(self):
        return self.action.done()
        
    def loop(self, dt):
        self.action._loop(self.warper(self.runtime + dt) - self.warper(self.runtime))
        
def timewarp(warper, action):
    def create(manager, target):
        return TimeWarperAction(manager, target, 
            warper, action)
    return ActionCreator(create)
 
def linear(factor):
    def warper(value):
        return value*factor
    return warper
    
class RepeatAction(Action):
    def init(self, action, times=-1):
        self.action = action
        self.times = times
        self.count = 0
        self.instantiate()
        
    def instantiate(self):
        self.current = self.action(self.manager, self.target)
        self.current._start()
        
    def done(self):
        return (self.times != -1) and (self.count>=self.times)
        
    def loop(self, dt):
        if self.current.done():
            if self.times==-1 or self.count < self.times:
                self.count += 1
                self.instantiate()
            else:
                return
        self.current._loop(dt)
        

        
def repeat(action, times=-1):
    def create(manager, target):
        return RepeatAction(manager, target, 
            action, times)
    return ActionCreator(create)
   
class RandomRepeatAction(Action):
    def init(self, actions, times=-1):
        self.actions = actions
        self.pending = self.actions[:]
        self.times = times
        self.count = 0
        self.instantiate()
        
    def instantiate(self):
        if not self.pending:
            self.pending = self.actions[:]
        c = random.choice(self.pending)
        self.current = c(self.manager, self.target)
        self.pending.remove(c)
        self.current._start()
        
    def done(self):
        return (self.times != -1) and (self.count>=self.times)
        
    def loop(self, dt):
        if self.current.done():
            if self.times==-1 or self.count < self.times:
                self.count += 1
                self.instantiate()
            else:
                return
        self.current._loop(dt)
        

        
def random_repeat(actions, times=-1):
    def create(manager, target):
        return RandomRepeatAction(manager, target, 
            actions, times)
    return ActionCreator(create)
     
    
class DelayAction(Action):
    def init(self, delta):
        self.delta = delta
        
    def done(self):
        return ( self.delta <= self.runtime )

def delay(delta):
    def create(manager, target):
        return DelayAction(manager, target, 
            delta)
    return ActionCreator(create)        

def random_delay(low, hi):
    def create(manager, target):
        return DelayAction(manager, target, 
            random.randint(low, hi))
    return ActionCreator(create)  
    
class CallAction(Action):
    def init(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def done(self):
        return True
        
    def start(self):
        self.func(*self.args, **self.kwargs)

def call(func, *args, **kwargs):
    def create(manager, target):
        return CallAction(manager, target, 
            func, args, kwargs)
    return ActionCreator(create)        

class SpawnAction(Action):
    def init(self, actions, target):
        self.actions = actions
        if target is None:
            self.spawn_target = self.target
        else:
            self.spawn_target = target
        
    def done(self):
        return True
        
    def start(self):
        for a in self.actions:
            self.manager.do(self.spawn_target, a)

def spawn(*actions, **kwargs):
    def create(manager, target):
        return SpawnAction(manager, target, 
            actions, kwargs.get("target",None))
    return ActionCreator(create)    
    
class PlaceAction(Action):
    def init(self, position):
        self.position = position
        
    def done(self):
        return True
        
    def start(self):
        self.target.translate = self.position

def place(position):
    def create(manager, target):
        return PlaceAction(manager, target, 
            position)
    return ActionCreator(create)       
        
class GotoAction(Action):
    def init(self, start, end, duration=1000):
        self.start_position = start
        self.end_position = end
        self.duration = duration
        
    def loop(self, dt):
        delta = self.end_position-self.start_position
        self.target.translate = (self.start_position +
                    delta * (
                        min(1,float(self.runtime)/self.duration)
                    ))
                    
    def done(self):
        return (self.runtime > self.duration)

    
def goto(goal, duration=1000):
    def create(manager, target):
        return GotoAction(manager, target, 
                start=target.translate, 
                end=goal, duration=duration)
    return ActionCreator(create)

def move(delta, duration=1000):
    def create(manager, target):
        return GotoAction(manager, target, 
                start=target.translate, 
                end=target.translate+delta, duration=duration)
    return ActionCreator(create)
        
class RotateAction(Action):
    def init(self, start, angle, duration=1000):
        self.start_angle = start
        self.angle = angle
        self.duration = duration
        
    def loop(self, dt):
        self.target.angle = (self.start_angle +
                    self.angle * (
                        min(1,float(self.runtime)/self.duration)
                    )) % 360 
    
                    
    def done(self):
        return (self.runtime > self.duration)


def rotate(angle, duration=1000):
    def create(manager, target):
        return RotateAction(manager, target, 
                start=target.angle, 
                angle=angle, duration=duration)
    return ActionCreator(create)

class ScaleAction(Action):
    def init(self, start, end, duration=1000):
        self.start_scale = start
        self.end_scale = end
        self.duration = duration
        
    def loop(self, dt):
        delta = self.end_scale-self.start_scale

        self.target.scale = (self.start_scale +
                    delta * (
                        min(1,float(self.runtime)/self.duration)
                    ))
        
                    
    def done(self):
        return (self.runtime > self.duration)


def scale(amount, duration=1000):
    def create(manager, target):
        return ScaleAction(manager, target, 
                start=target.scale, 
                end=target.scale*amount, duration=duration)
    return ActionCreator(create)

    
    
if __name__ == "__main__":
    class E: pass
    def foofunc(*args, **kwargs):
        print args
        print kwargs
   
    e = E()
    m = Manager()
    e.angle = 0
    e.translate = Point3(0,0,0)
    
    b = move(Point3(10,0,-10), duration=1000)
    m.do(e, place(Point3(100,100,100)) + repeat(b, 3))
    for x in range(12):
        m.loop(1000)
        time.sleep(0.5)
        print e.translate
    
    b = move(Point3(10,0,-10), duration=6000)
    m.do(e, b + timewarp(linear(2), b) )
    for x in range(12):
        m.loop(1000)
        time.sleep(0.5)
        print e.translate
    
    r = (
        rotate(90, duration=5000) + 
        delay(4000) + 
        call(foofunc, 1, 2, 3, foo=1, bar=2) +
        rotate(-360,duration=5000)
        )
    m.do(e, r)
    for x in range(18):
        m.loop(1000)
        time.sleep(0.5)
        print e.angle
    
    a = goto(Point3(10,10,10), duration=5000)
    m.do(e, a)
    for x in range(10):
        m.loop(1000)
        time.sleep(0.5)
        print e.translate, m.actions
    b = move(Point3(10,0,-10), duration=3000)
    m.do(e, b)
    for x in range(10):
        m.loop(1000)
        time.sleep(0.5)
        print e.translate, m.actions
        
    c = b + a
    m.do(e, c)
    for x in range(10):
        m.loop(1000)
        time.sleep(0.5)
        print e.translate, m.actions
            
        
        
