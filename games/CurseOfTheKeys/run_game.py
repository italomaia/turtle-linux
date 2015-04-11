#! /usr/bin/python

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Part of the graphic tiles used in this program is the public 
domain roguelike tileset "RLTiles".
Some of the tiles have been modified by Dominic Kexel.

You can find the original tileset at:
<http://rltiles.sf.net>

Part of the graphic tiles used in this program are taken from
<http://rivendell.fortunecity.com/goddess/268/>

Images used for backgrounds etc. are taken from
<http://morguefile.com/>

All sounds are taken from
<http://soundsnap.com>

(c) 2008 by Dominic Kexel
"""

from src import *

if __name__=="__main__":
    try:
        import psyco
        psyco.full()
        
    except:
        print "no psyco found"
        
    os.chdir('src')
    g=Game()
    q=g.run()

    