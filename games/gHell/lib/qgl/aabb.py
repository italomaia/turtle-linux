#Copyright (c) 2006 Simon Wittber
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation files
#(the "Software"), to deal in the Software without restriction,
#including without limitation the rights to use, copy, modify, merge,
#publish, distribute, sublicense, and/or sell copies of the Software,
#and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""

This module contains a BoudningBox implementation, which can be used to build
a volume heirarchy, which can will then provide efficient culling and 
collision testing.

"""

#import Numeric


class BoundingBox(object):
    """
    An bounding box class.
    """
    def __init__(self, position=(0.0,0.0,0.0), extents=(0.0,0.0,0.0)):
        self.position = Numeric.array(position, Numeric.Float)
        self.extents = Numeric.array(extents, Numeric.Float)
        
    @classmethod
    def from_extents(cls, (minx,maxx,miny,maxy,minz,maxz)):
        """
        Return a BoundingBox created from minx, max, miny, maxy, minz and 
        maxz dimensions.
        """
        width = (maxx - minx) * 0.5
        height = (maxy - miny) * 0.5
        depth = (maxz - minz) * 0.5
        centrex = minx + (width)
        centrey = miny + (height)
        centrez = minz + (depth)
        return cls(position=(centrex, centrey, centrez), extents=(width,height,depth))
        
    def intersects(self, b):
        """
        Return True if self intersects with b.
        """
        t = b.position - self.position 
        return abs(t[0]) <= (self.extents[0] + b.extents[0]) and abs(t[1]) <= (self.extents[1] + b.extents[1])  and abs(t[2]) <= (self.extents[2] + b.extents[2]) 
        
    def min(self, index):
        """
        Return min coordinate (specified by index x=0,y=1,z=2)
        """
        return self.position[index] - self.extents[index]
    
    def max(self, index):
        """
        Return max coordinate (specified by index x=0,y=1,z=2)
        """
        return self.position[index] + self.extents[index]
        
    def __add__(self, b):
        """
        Adds another bounding box volume, the new box covers both volumes.
        """
        extents = min((self.min(0), b.min(0))), max((self.max(0), b.max(0))), min((self.min(1), b.min(1))), max((self.max(1), b.max(1))), min((self.min(2), b.min(2))), max((self.max(2), b.max(2)))
        return self.from_extents(extents)
    
    def __repr__(self):
        return "<%s %s %s>" % (self.__class__.__name, self.position, self.extents)
