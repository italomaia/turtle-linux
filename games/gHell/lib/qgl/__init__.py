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

QGL is a scenegraph based OpenGL rendering engine for Python.

The render module contains visitor classes which compile a scenegraph, draw 
the scenegraph, and a visitor which is used for mouse picking.

The texture module contains a Coords class, and some classes which are used 
to pack multiple images into one larger image.

The loaders module contains functions for loading Mesh data from 3d model 
files.

The aabb module contains a class for using Bounding Boxes.

The math module contains misc. math functions which are not present in the 
standard library.

"""

from qgl import render
from qgl import scene
from qgl import texture
from qgl import loaders
from qgl import aabb
from qgl import qmath