from __future__ import division

from math import sqrt, cos, sin, acos, atan2, degrees, radians

from common import *
from constants import *


class Vector(tuple):
    """2-d float vector implementation.

    Vectors can be instantiated with either two numbers or an iterable of two
    numbers. In either case, the numbers are converted to floats. In general
    a operation that can be performed on a pair of vectors can also be
    performed on a vector and some iterable of numbers.

    """

#    def __new__(cls, *args):
#        """Construct a Vector object.
#
#        """
#        if len(args) == 1:
#            args = args[0]
#        args = map(float, args)
#        return tuple.__new__(cls, args)

    def __eq__(self, other):
        """Confirm whether two vectors have the same components.

        :Parameters:
            `other` : Vector
                The object to compare to.

        """
        if not isinstance(other, Vector):
            other = Vector(other)
        return tuple.__eq__(self, other)

    def __hash__(self):
        """Compute the hash of the components.

        """
        return self[0] ^ self[1]

    def __str__(self):
        """Construct a concise string representation.

        """
        elt_string = ", ".join("%.2f" % x for x in self)
        return "Vector((%s))" % elt_string
    
    def __repr__(self):
        """Construct a precise string representation.

        """
        elt_string = ", ".join(repr(x) for x in self)
        return "Vector((%s))" % elt_string

    @property
    def x(self):
        """The horizontal coordinate.

        """
        return self[0]

    @property
    def y(self):
        """The vertical coordinate.

        """
        return self[1]

    @property
    def length(self):
        """The length of the vector.

        """
        try:
            return self._length
        except AttributeError:
            vx, vy = self
            self._length = sqrt(vx ** 2 + vy ** 2)
            return self._length

    @property
    def angle(self):
        """The angle the vector makes to the positive x axis in the range
        (-180, 180].

        """
        try:
            return self._angle
        except AttributeError:
            self._angle = degrees(atan2(self.y, self.x))
            return self._angle

    def __add__(self, other):
        """Add the vectors componentwise.

        :Parameters:
            `other` : Vector
                The object to add.

        """
        if not isinstance(other, Vector):
            other = Vector(other)
        return Vector((self[0] + other[0], self[1] + other[1]))
    __radd__ = __add__

    def __sub__(self, other):
        """Subtract the vectors componentwise.

        :Parameters:
            `other` : Vector
                The object to subtract.

        """
        if not isinstance(other, Vector):
            other = Vector(other)
        return Vector((self[0] - other[0], self[1] - other[1]))

    def __rsub__(self, other):
        if not isinstance(other, Vector):
            other = Vector(other)
        return Vector((other[0] - self[0], other[1] - self[1]))

    def __mul__(self, other):
        """Either multiply the vector by a scalar or compute the dot product
        with another vector.

        :Parameters:
            `other` : Vector or float
                The object by which to multiply.

        """
        try:
            other = float(other)
            return Vector((self[0] * other, self[1] * other))
        except TypeError:
            if not isinstance(other, Vector):
                other = Vector(other)
            return self[0] * other[0] + self[1] * other[1]
    __rmul__ = __mul__

    def __div__(self, other):
        """Divide the vector by a scalar.

        :Parameters:
            `other` : float
                The object by which to divide.

        """
        if not isinstance(other, float):
            other = float(other)
        return Vector((self[0] / other, self[1] / other))
    __truediv__ = __div__

    def __floordiv__(self, other):
        """Divide the vector by a scalar, roudning down.

        :Parameters:
            `other` : float
                The object by which to divide.

        """
        if not isinstance(other, float):
            other = float(other)
        return Vector((self[0] // other, self[1] // other))


    def __neg__(self):
        """Compute the unary negation of the vector.

        """
        return Vector((-self[0], -self[1]))

    def rotated(self, angle):
        """Compute the vector rotated by an angle.

        :Parameters:
            `angle` : float
                The angle (in radians) by which to rotate.

        """
        vx, vy = self
        angle = radians(angle)
        ca, sa = cos(angle), sin(angle)
        return Vector((vx * ca - vy * sa, vx * sa + vy * ca))
    
    def normalised(self):
        """Compute the vector scaled to unit length.

        """
        vx, vy = self
        l = self.length
        return Vector((vx / l, vy / l))

    def perpendicular(self):
        """Compute the perpendicular.

        """
        vx, vy = self
        return Vector((-vy, vx))

    def dot(self, other):
        """Compute the dot product with another vector.

        :Parameters:
            `other` : Vector
                The vector with which to compute the dot product.

        """
        if isinstance(other, Vector):
            other = Vector(other)
        return self[0] * other[0] + self[1] * other[1]

    def cross(self, other):
        """Compute the cross product with another vector.

        :Parameters:
            `other` : Vector
                The vector with which to compute the cross product.

        """
        if not isinstance(other, Vector):
            other = Vector(other)
        return self[0] * other[1] - self[1] * other[0]

    def project(self, other):
        """Compute the projection onto another vector.

        :Parameters:
            `other` : Vector
                The vector onto which to compute the projection.

        """
        if not isinstance(other, Vector):
            other = Vector(other)
        return other * self.dot(other) / other.dot(other)
    
    def angle_to(self, other):
        """Compute the angle made to another vector.

        :Parameters:
            `other` : Vector
                The vector with which to compute the angle.

        """
        if not isinstance(other, Vector):
            other = Vector(other)
        angle = acos(self.dot(other) / (self.length * other.length))
        return degrees(angle)

    def signed_angle_to(self, other):
        theta = self.angle_to(other)
        if self.perpendicular() * other > 1: theta *= -1
        return theta
        
    def distance_to(self, other):
        """Compute the distance to another point vector.

        :Parameters:
            `other` : Vector
                The point vector to which to compute the distance.

        """
        if not isinstance(other, Vector):
            other = Vector(other)
        return (self - other).length

    def in_tri(self, a, b, c):
        areas = tri_area(self, a, b), tri_area(self, b, c), tri_area(self, c, a)
        if min(areas) > 0 or max(areas) < 0:
            return True
        return False

    def approx(self, other):
        if abs(self[0] - other[0]) < EPSILON and abs(self[1] - other[1]) < EPSILON:
            return True
        else:
            return False
def tri_area(a, b, c):
    return 0.5 * (b - a).cross(c - a)

def tri_angle(a, b, c):
    return (a-b).signed_angle_to(c-b)
class Line(object):

    def __init__(self, direction, distance):
        self.direction = direction
        self.distance = distance
        self.along = direction.perpendicular()
        
    def closest_point(self, point):
        return point.project(self.along) + self.direction * self.distance
        
    def reflect(self, point):
        point_distance = point * self.direction
        new_distance = 2 * self.distance - point_distance
        offset = point - point.project(self.direction)
        return self.direction * new_distance + offset

    def signed_dist(self, pt):
        return (self.direction * pt) - distance
        
    @cached
    def parallel_through_origin(self):
        if self.distance == 0:
            return self
        return Line(self.direction, 0)
        
class LineSegment(object):

    def __init__(self, line, min_dist, max_dist):
        self.line = line
        self.min_dist = min_dist
        self.max_dist = max_dist
    @classmethod
    def from_endpoints(cls, start, end):
        start = Vector(start)
        end = Vector(end)
        direction = (end - start).perpendicular().normalised()
        distance = end * direction
        line = Line(direction, distance)
        pd = direction.perpendicular()
        d1 = start * pd
        d2 = end * pd
        return LineSegment(line, min(d1,d2), max(d1,d2))
 
    @cached
    def length(self):
        return abs(self.max_dist - self.min_dist)
        
    @cached
    def pos(self):
        return self.line.direction * self.line.distance + self.line.direction.perpendicular() * (.5 * (self.min_dist + self.max_dist))
    
    @cached
    def radius(self):
        return .5 * abs(self.max_dist - self.min_dist)
        
    @cached
    def start(self):
        return self.line.direction * self.line.distance + self.line.direction.perpendicular() * self.min_dist
    
    @cached
    def end(self):
        return self.line.direction * self.line.distance + self.line.direction.perpendicular() * self.max_dist

    def closest_point(self, point):
        pd = self.line.along
        perp_dist = point * pd
        perp_dist = max(min(perp_dist, self.max_dist), self.min_dist)
        return (pd * perp_dist) + self.line.direction * self.line.distance

    def intersects_seg(self, other):
        if self.bb.intersects(other.bb):
            areas = [tri_area(self.start, other.start, self.end), tri_area(other.start, self.end, other.end),
                     tri_area(self.end, other.end, self.start), tri_area(other.end, self.start, other.start)]
            return min(areas) * max(areas) > EPSILON
        return False
    @cached
    def bb(self):
        return BoundingBox(self.start, self.end)
        
class BoundingBox(object):
    def __init__(self, *pts):
        xs, ys = zip(*pts)
        self.lo = Vector((min(xs), min(ys)))
        self.hi = Vector((max(xs), max(ys)))
        self.mid = .5 * (self.lo + self.hi)

    def __contains__(self, pt):
        return self.hi.x > pt[0] > self.lo.x and self.hi.y > pt[1] > self.lo.y

    def intersects(self, other):
        if self.lo.x > other.hi.x or self.lo.y > other.hi.y or self.hi.x < other.lo.x or self.hi.y < other.lo.y:
            return False
        else:
            return True
            
    def __str__(self):
        return "BoundingBox(%s, %s)" % (self.lo, self.hi)
