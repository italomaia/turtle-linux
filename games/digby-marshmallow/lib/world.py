import spatialhash
from vector import *
from common import *
import squirtle
import swag
import enemy
import pyglet
import door
import oxygen

import random # uh oh

class EditableWorld(object):

    def __init__(self, stage=None):
        self.static = spatialhash.SpatialHash(2000)
        self.actors = spatialhash.SpatialHash(500)
        self.doors = {}
        self.swag_counts = {}
        if stage is not None:
            for obj in stage["objects"]:
                self.static.add(obj)
            if 'background' in stage:
                self.background = squirtle.SVG(stage['background'], anchor_x='center', anchor_y='center')
            else:
                self.background = squirtle.SVG('data/images/background/space.svgz', anchor_x='center', anchor_y='center')
            for act in stage.get("actors", []):
                self.actors.add(act)
            self.doors = stage.get('doors', {})
            self.swag_counts = stage.get('swag_counts', {})
            
    @property
    def segments(self):
        for obj in self.static:
            for seg in obj.segments:
                yield seg
    
    def __repr__(self):
        swag_counts = {}
        serial = ''
        serial += 'background = %r\n' % (self.background.filename,)
        serial += 'doors = %r\n' % (self.doors,)
        serial += 'actors = [\n'
        for obj in self.actors:
            if isinstance(obj, swag.Swag):
                swag_counts[obj.name] = swag_counts.get(obj.name, 0) + 1
            serial += '%r,\n' % (obj,)
        serial += ']\n'
        serial += 'swag_counts = %r\n' % (swag_counts,)
        serial += 'objects = ['
        for obj in self.static:
            obj.update()
            serial += '%r,' % (obj,)
        serial += ']\n'
        return serial
    
                               
class PlayableWorld(pyglet.event.EventDispatcher):
    event_types = ['on_get_swag', 'on_finish_level', 'on_suffocate', 'on_shoot']
    def __init__(self, state, stage):
        self.state = state
        edit_world = EditableWorld(stage)
        self.static = spatialhash.SpatialHash(100)
        self.world_graphics = spatialhash.SpatialHash(2000)
        self.door_hash = spatialhash.SpatialHash(500)
        self.background = edit_world.background
        for obj in edit_world.static:
            self.world_graphics.add(obj)
            for seg in obj.segments:
                self.static.add(seg)
        self.world_graphics.chunk()
        self.active = spatialhash.SpatialHash(300)

        self.initial_oxygen = None

        for act in edit_world.actors:
            act.world = self
            if isinstance(act, oxygen.Oxygen):
                if act.is_initial:
                    self.initial_oxygen = act
            if isinstance(act, swag.Goal):
                self.goal = act
            self.active.add(act)
        self.doors = edit_world.doors
        for my_door in self.doors.itervalues():
            my_door.set_world(self)
            self.door_hash.add(my_door)
        self.swag_counts = edit_world.swag_counts
        self.new_active = set()
        if not self.initial_oxygen:
            self.initial_oxygen = oxygen.Oxygen(self, pos=(0, 0), radius=50, image_file='images/all/oxygen.svgz')
            self.new_active.add(self.initial_oxygen)

            
class StaticObject(object):

    def __init__(self, image, pos=(0.0, 0.0), bearing=0.0, scale=1.0,
                 points=None, z=0):
        self.image = image
        self.pos = Vector(pos)
        self.bearing = bearing
        self.scale = scale
        self.points = points
        self.z = z
        if self.points is None:
            self.update()

    def __repr__(self):
        args = (self.image, self.pos, self.bearing, self.scale, self.points, self.z)
        return "StaticObject(%r, %r, %r, %r, %r, %r)" % args

    def update(self):
        del self.radius
        del self.bb
        del self.segments
        self.points = []
        last_pt = None
        if self.image.hull:
            sw, sh = self.image.width / 2, self.image.height / 2
            for pt in max(self.image.hull, key=len):
                v = Vector((pt[0] - sw, pt[1] - sh))
                v = v.rotated(self.bearing) * self.scale
                new_pt = self.pos + v
                if last_pt != new_pt:
                    self.points.append(new_pt)
                    last_pt = new_pt
        else:
            print "Warning: no points in ", svg.filename

    @cached
    def radius(self):
        return max(pt.length for pt in self.points)

    @cached
    def bb(self):
        return BoundingBox(*self.points)
    
    @cachedgen
    def segments(self):
        num_points = len(self.points)
        for n in xrange(num_points):
            if self.points[n] != self.points[n-1]:
                yield LineSegment.from_endpoints(self.points[n-1], self.points[n])

    def draw(self):
        self.image.draw(self.pos[0], self.pos[1], angle=self.bearing,
                        scale=self.scale)
