#! /usr/bin/env python

# Vectorpods 2 - A arcade space shooter programmed by PyMike
# Copyright (C) 2007  PyMike
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import sys, os
import math, random

import pygame
from pygame.locals import *

from Game import *
from Menu import *
from Constants import *

def Run():
    pygame.init()
    pygame.display.set_caption("Vectorpods 2 - PyMike - March 2008")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    game = Menu(screen)
    game.Run()
