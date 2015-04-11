from __future__ import division

from collections import defaultdict

from common import *
from constants import *

class SpatialIndex(object):
    
    def __init__(self):
        self.reset()
        
    def reset(self):
       self.hash = defaultdict(list)
        
    def bucket_for_pos(self, pos):
        xb = int(pos.x // SPATIAL_INDEX_RESOLUTION)
        yb = int(pos.y // SPATIAL_INDEX_RESOLUTION)
        return self.hash[xb, yb]
        
    def add(self, obj):
        self.hash[obj.pos.x // SPATIAL_INDEX_RESOLUTION, obj.pos.y // SPATIAL_INDEX_RESOLUTION].append(obj)
        
    def objects_near(self, pos, radius=0, pred=None):
        min_x = int((pos.x - radius) // SPATIAL_INDEX_RESOLUTION)
        min_y = int((pos.y - radius) // SPATIAL_INDEX_RESOLUTION)
        max_x = int((pos.x + radius) // SPATIAL_INDEX_RESOLUTION)
        max_y = int((pos.y + radius) // SPATIAL_INDEX_RESOLUTION)
        res = []
        for xi in xrange(min_x, max_x + 1):
            for yi in xrange(min_y, max_y + 1):
                res.extend(self.hash[xi, yi])
        if pred is not None:
            res = filter(pred, res)
        return res
        
    def closest_to(self, pos, radius, pred=None):
        res = None
        res_d2 = radius ** 2
        for c in self.objects_near(pos, radius=radius, pred=pred):
            d2 = (c.pos - pos).length2
            if d2 < res_d2:
                res = c
                res_d2 = d2
        return res
    
class PlantCoverageIndex(object):
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.hash = defaultdict(list)
        
    def bucket_for_pos(self, pos):
        xb = int(pos.x // PLANT_INDEX_RESOLUTION)
        yb = int(pos.y // PLANT_INDEX_RESOLUTION)
        return self.hash[xb, yb]
    
    def add(self, obj):
        x = obj.pos.x
        y = obj.pos.y
        radius = obj.radius
        min_x = int((x - radius) // PLANT_INDEX_RESOLUTION)
        min_y = int((y - radius) // PLANT_INDEX_RESOLUTION)
        max_x = int((x + radius) // PLANT_INDEX_RESOLUTION)
        max_y = int((y + radius) // PLANT_INDEX_RESOLUTION)
        for xi in xrange(min_x, max_x + 1):
            for yi in xrange(min_y, max_y + 1):
                self.hash[xi, yi].append(obj)
        
    def is_covered(self, pos):
        for obj in self.bucket_for_pos(pos):
            if (obj.pos - pos).length2 < obj.radius ** 2:
                return True
        return False
     
        