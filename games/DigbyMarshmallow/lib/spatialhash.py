from math import floor, ceil
from vector import Vector as v
from vector import LineSegment

from pyglet.gl import *
class SpatialHash(object):
    
    def __init__(self, csize=50):
        self.csize = csize
        self.store = {}
        self.obj_set = set()
        
    def __len__(self):
        return len(self.obj_set)
        
    def __iter__(self):
        for act in self.obj_set:
            yield act
    def bounds(self, act):
        lo_x = int(floor((act.pos[0] - act.radius) / self.csize))
        hi_x = int(floor((act.pos[0] + act.radius) / self.csize))
        lo_y = int(floor((act.pos[1] - act.radius) / self.csize))
        hi_y = int(floor((act.pos[1] + act.radius) / self.csize))
        #if (hi_x - lo_x + 1)*(hi_y - lo_y + 1) > 100: print inspect.stack()
        for u in xrange(lo_x, hi_x + 1):
            for v in xrange(lo_y, hi_y + 1):
                yield u, v
    
    def box_bounds(self, box):
        lo_x = int(floor(box.lo.x / self.csize))
        hi_x = int(floor(box.hi.x / self.csize))
        lo_y = int(floor(box.lo.y / self.csize))
        hi_y = int(floor(box.hi.y / self.csize))
        #if (hi_x - lo_x + 1)*(hi_y - lo_y + 1) > 100: print inspect.stack()[2]

        for u in xrange(lo_x, hi_x + 1):
            for v in xrange(lo_y, hi_y + 1):
                yield u, v
    
    def line_bounds(self, a, b):
        if a == b:
            yield int(floor(a[0] / self.csize)), int(floor(a[1] / self.csize))
            return
        if (a[0] > b[0]): a, b = b, a
        elif (a[0] == b[0]):
            for u, v in self.line_bounds((a[1], a[0]), (b[1], b[0])): yield v, u
            return
        lo_x = int(floor(a[0] / self.csize))
        hi_x = int(floor(b[0] / self.csize))
        m = (b[1] - a[1])/(b[0] - a[0])
        for u in xrange(lo_x, hi_x + 1):
            lo_y = int(floor(((u * self.csize - a[0]) * m + a[1])/self.csize))
            hi_y = int(floor((((u + 1) * self.csize - a[0]) * m + a[1])/self.csize))
            lo_y2 = int(floor(min(a[1], b[1]) / self.csize))
            hi_y2 = int(floor(max(a[1], b[1]) / self.csize))
            
            if hi_y < lo_y: lo_y, hi_y = hi_y, lo_y
            lo_y = max(lo_y, lo_y2)
            hi_y = min(hi_y, hi_y2)
            
            for v in xrange(lo_y, hi_y + 1):
                yield u, v
    
    def tri_bounds(self, a, b, c):
        for pt in self.line_bounds(a, b): yield pt
        for pt in self.line_bounds(b, c): yield pt
        for pt in self.line_bounds(c, a): yield pt
           
    def overlaps(self, act):
        items = set()
        for u, v in self.bounds(act):
            if (u, v) in self.store:
                items.update(self.store[u, v])
        return items
    
    def on_line(self, a, b):
        items = set()
        for u, v in self.line_bounds(a, b):
            if (u, v) in self.store:
                items.update(self.store[u, v])
        return items
    
    def in_tri(self, a, b, c):
        items = set()
        for u, v in self.tri_bounds(a, b, c):
            if (u, v) in self.store:
                items.update(self.store[u, v])
        return items
        
    def in_box(self, box):
        items = set()
        for u, v in self.box_bounds(box):
            if (u, v) in self.store:
                items.update(self.store[u, v])
        return items
    
    def update(self, lst):
        for act in lst:
            self.add(act)
    def add(self, act):
        self.obj_set.add(act)
        if isinstance(act, LineSegment):
            bounds = self.line_bounds(act.start, act.end)
        else:
            bounds = self.bounds(act)
        for u, v in bounds:
            if (u, v) in self.store:
                self.store[u, v].add(act)
            else:
                self.store[u, v] = set([act])
    
    def remove(self, act):
        if isinstance(act, LineSegment):
            bounds = self.line_bounds(act.start, act.end)
        else:
            bounds = self.bounds(act)
        for u, v in bounds:
            self.store[u, v].remove(act)
        self.obj_set.remove(act)

    def chunk(self):
        self._disp_lists = {}
        for u, v in self.store:
            lst = glGenLists(1)
            glNewList(lst, GL_COMPILE)
            for obj in sorted(self.store[u, v], key = lambda x : x.z):
                obj.draw()
            glEndList()
            self._disp_lists[u, v] = lst
    
    def draw(self, bb):
        for u, v in self.box_bounds(bb):
            try:
                glCallList(self._disp_lists[u, v])
            except KeyError:
                pass
