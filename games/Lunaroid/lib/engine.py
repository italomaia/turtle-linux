import retrogamelib as rgl
from objects import *

class Engine(object):
    
    def __init__(self, game):
        self.tiles = []
        self.image = rgl.util.load_image("data/world.png")
        self.pos = [0, 0]
        self.game = game

    def parse_level(self):
        tiles = []
        self.tiles = []
        for y in range(15):
            tiles.append([])
            for x in range(16):
                wx, wy = (self.pos[0]*16) + x, (self.pos[1]*15) + y
                color = list(self.image.get_at((wx, wy))[:-1])
                if color == [0, 0, 0]:
                    w = Wall(self, (x*16, y*16))
                    if self.get_at(wx, wy-1) != [0, 0, 0]:
                        w.on_end[0] = True
                    if self.get_at(wx, wy+1) != [0, 0, 0]:
                        w.on_end[1] = True
                    if self.get_at(wx-1, wy) != [0, 0, 0]:
                        w.on_end[2] = True
                    if self.get_at(wx+1, wy) != [0, 0, 0]:
                        w.on_end[3] = True
                    tiles[-1].append(w)
                elif color == [0, 255, 255]:
                    if self.get_at(wx-1, wy) == [0, 255, 255]:
                        side = 1
                    else:
                        side = -1
                    d = Door(self, (x*16, y*16), side)
                    tiles[-1].append(d)
                elif color == [255, 255, 0]:
                    if self.get_at(wx-1, wy) == [255, 255, 0]:
                        side = 1
                    else:
                        side = -1
                    d = Door(self, (x*16, y*16), side, True)
                    tiles[-1].append(d)
                else:
                    tiles[-1].append(None)
                if color == [0, 0, 255]:
                    Rusher(self, (x*16, y*16))
                if color == [0, 255, 0]:
                    Bat(self, (x*16, y*16))
                if color == [0, 200, 0]:
                    Boss(self, (x*16, y*16))
                if color == [255, 200, 0]:
                    if not self.game.player.has_missile:
                        Missile(self, (x*16, y*16))
                if color == [255, 0, 0]:
                    if self.get_at(wx-1, wy) != [0, 0, 0]:
                        side = 1
                    else:
                        side = -1
                    Crawly(self, (x*16, y*16), side)
                if color == [255, 0, 255]:
                    Squatter(self, (x*16, y*16))
        self.tiles = tiles

    def get_at(self, x, y):
        try:
            return list(self.image.get_at((x, y)))[:-1]
        except:
            pass
