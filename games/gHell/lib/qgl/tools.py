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

This module contains tools for generating resources which can be used in a 
QGL scenegraph.

"""


import sys
import glob

import pygame
from pygame.locals import *

import qgl
import zipfile

def make_sequence(wildcard, output_file):
    """
    Usage:
    make_sequence("*.jpg", "output.zip")
    
    This function will back multiple image files, specified by a wildcard 
    into a zip file, which can then be used by a qgl.scene.Sequence leaf.
    """
    pygame.init()
    pygame.display.set_mode((320,240))
    pack = qgl.texture.Pack()
    coords = []
    for filename in glob.glob(wildcard):
        coords.append(pack.pack(filename))
    f = zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED)
    f.writestr("texture.rgba", pygame.image.tostring(pack.image, "RGBA"))
    f.writestr("coords.repr", repr(coords))
    f.writestr("size.repr", repr(pack.image.get_size()))
    f.close()
        
