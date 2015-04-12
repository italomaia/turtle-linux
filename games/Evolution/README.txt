Up The Chain Of Evolution
=========================

Entry in PyWeek #4  <http://www.pyweek.org/4/>
Team: Fluffy Menace
Members: Richard (code), Fydo (art + sfx), JDruid (music + sfx)
Version: 1.1


DEPENDENCIES:

You might need to install some of these before running the game:

  Python:     http://www.python.org/
  PyGame:     http://www.pygame.org/
  PyOpenGL:   http://pyopengl.sf.net/


RUNNING THE GAME:

On Windows or Mac OS X, locate the "run_game.pyw" file and double-click it.

Othewise open a terminal / console and "cd" to the game directory and run:

  python run_game.py

A "-win" argument on the command-line is optional and runs the game
in windowed mode.


HOW TO PLAY THE GAME:

You've been sent back in time by a (possibly mad) scientist in order to
recover items he needs to save the planet!

A side-effect of the time travel has you booted back to the bottom of the
evolutionary scale. The only way is up!

** Move around using the cursor keys.
** Press SPACE to detect the items to collect.


STUFF OF NOTE IN THIS GAME:

(this section written by Richard)

Fydo's artwork. Wow, it was amazing to work with someone so talented and
fast.

JDruid's music. Cool stuff, and produced just the right pieces of
music that we needed.

On a programming note, this game has some interesting features.

The landscape is generated from a pixmap (see lvl/one*.png or one.xcf
for the complete overview). The pixmap is examined and turned into a series
of cubic bezier curves, rendered partly by OpenGL (the solid bits) and 
partly by hand (the line bits).

I also used curves to render the trees and clouds. Run lib/cloud.py and
lib/tree.py for some examples (hitting SPACE to regenerate).

Unfortunately the curved landscape was a pain to work with and there's some
collision glitches (and probably bugs, but nothing I've run into lately).

The game concept is two-fold:

1. hyper-evolution up from a lowly worm to some form more suitable for a
   given environment, and
2. mostly free-form exploration of a large, interesting playing world.

The latter didn't really work in the final submission for PyWeek because time
constraints meant we couldn't construct that large, interesting world. Just
a large one. We had intended to have NPCs to talk to (and bribe with the
money you find in order to locate more items around the world). There's
also clearly scope for more skill-based challenges and so on.

The code and the design discussion is available at:

   http://code.google.com/p/fluffymenace/

There's some dev switches on the command-line:

  -nomusic
  -nointro

And in-game you can hit "d" to pause simulation and hit "s" to step.


UNIMPLEMENTED:
- better level design
- baddies that move
- flying and swimming baddies

KNOWN BUGS:
- none that we're aware of!

IMPROVEMENTS ON THE TABLE
- reduce the number of line segments in landscape
- use ARB_occlusion_query if it's available for flying collision
- background for sky
- we can vary friction on ground to allow sliding but don't use it



LICENSE:

(Please note that there are two licenses here. All the PNG files are under
the Free Art License, and the rest is licensed below)

---

  Up The Chain Of Evolution - Art Assets
  All PNG files contained in this archive are affected by this license
  Copyright © 2007 Chris Hopp
  Copyleft: this work of art is free, you can redistribute it and/or modify it
  according to terms of the Free Art license.
  You will find a specimen of this license on the site 
  Copyleft Attitude http://artlibre.org as well as on other sites.

---
  
Up The Chain Of Evolution
Copyright (c) 2007 Richard Jones, Chris Hopp, Joona Karjalainen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
