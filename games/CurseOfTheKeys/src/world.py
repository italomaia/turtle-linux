import os, sys, pygame, random, time, datetime
from pygame.locals import *
from data import *

class Resource:
    def __init__(self, name, tilesize,surf=False):
        if not surf:
            self.res=self.load_image(name)
        else:
            self.res=name
        _, _, w, h=self.res.get_rect()
        self.tiles=[]
        for y in range(0, h/tilesize):
            for x in range(0, w/tilesize):
                tile = pygame.Surface((tilesize, tilesize), depth=self.res)
                chop_rect=(x*tilesize, y*tilesize, tilesize, tilesize)
                tile.blit(self.res, (0, 0), chop_rect)
                #tile=pygame.transform.scale(tile, (TILESIZE*ZOOM, TILESIZE*ZOOM))
                self.tiles.append(tile)
                
    def get(self, no):
        return self.tiles[no]
    
    def load_image(self, name):
        try:
            image = pygame.image.load(name)
        except pygame.error, message:
            print 'Cannot load image:', name
            raise SystemExit, message
        image = image.convert_alpha()
        return image

class Fog(pygame.sprite.Sprite):
    def __init__(self,image,x=20,y=20):
        pygame.sprite.Sprite.__init__(self)
        self.fog_image=image.convert_alpha()
        self.rect=image.get_rect()
        self.fog_pos=(0,20,0)
        self.c=0
        self.x=x
        self.y=y
        self.i1=pygame.transform.scale(self.fog_image,(random.randrange(60,200),random.randrange(16,24)))
        self.i2=pygame.transform.scale(self.fog_image,(random.randrange(60,200),random.randrange(16,24)))
        self.i3=pygame.transform.scale(self.fog_image,(random.randrange(60,200),random.randrange(16,24)))
        
    def random(self,y):
        if random.randrange(0,2):
            y+=1
        else:
            y-=1
        
        if y<0:
            y+=1
        if y>10:
            y-=1
            
        return y
    
    def update(self):
        self.c+=1
        if self.c>150:
            self.c=0
            y,x,c=self.fog_pos
            self.fog_pos=(self.random(y),self.random(x),self.random(c))
    
    def draw(self,screen):
        #pygame.transform.scale(self.fog_image.convert_alpha(),(random.randrange(60,200),random.randrange(16,24)))
        screen.blit(self.i1,(self.fog_pos[0]+self.x,0+self.y),(0,0,480,50))
        screen.blit(self.i2,(self.fog_pos[1]+self.x,16+self.y))
        screen.blit(self.i3,(self.fog_pos[2]+self.x,32+self.y))
        self.update()
        return
    
class Map:
    def __init__(self, array, R, wx, wy,single=False):
        #pygame.sprite.Sprite.__init__(self)
        self.single=single
        self.image=pygame.Surface((MAPSIZE*TILESIZE, MAPSIZE*TILESIZE))
        self.winter_image=pygame.Surface((MAPSIZE*TILESIZE, MAPSIZE*TILESIZE))
        self.array=array
        self.R=R
        self.data = [None] * MAPSIZE
        
        for i in range(MAPSIZE):
            self.data[i] = [None] * MAPSIZE
        self.update(True)
        self.world_x=wx
        self.world_y=wy
        self.key=None
        self.outposts={}
        
    def update(self,init=False,tiles=None):    
        if tiles:
            self.R=tiles
        x=0
        y=0
        self.image=pygame.Surface((MAPSIZE*TILESIZE, MAPSIZE*TILESIZE))
        self.winter_image=pygame.Surface((MAPSIZE*TILESIZE, MAPSIZE*TILESIZE))
        if init:
            for line in self.array:
                for c in line:
                    self.data[x][y]=c
                    self.image.blit(self.R.get(self.get(c)['TileNo']), (x*TILESIZE, y*TILESIZE))
                    self.winter_image.blit(self.R.get(self.get(c)['wTileNo']), (x*TILESIZE, y*TILESIZE))
                    x+=1
                x=0    
                y+=1
        else:
            for line in self.data:
                for c in line:
                    self.image.blit(self.R.get(self.get(c)['TileNo']), (x*TILESIZE, y*TILESIZE))
                    self.winter_image.blit(self.R.get(self.get(c)['wTileNo']), (x*TILESIZE, y*TILESIZE))
                    y+=1
                y=0    
                x+=1
            
    def get(self, type):    
        for t in Terrain:
            if t['Symbol']==type:
                return t
    
    def get_capital(self):
        for y in range(0,12):
            for x in range(0,12):
                if self.data[x][y]=='C':
                    return (x,y)
    
    def hide_key(self):
        pos=[]
        for y in range(0,12):
            for x in range(0,12):
                t=self.get(self.data[x][y])
                if t['can_key']:
                    pos.append((x,y))
        
        self.key=random.choice(pos)

class World:
    def __init__(self, maps, finalmap,tiles,startx,starty):
        self.finalmap=Map(finalmap,tiles,5,8,True)
        
        self.h=maps.__len__()
        self.w=maps[0].__len__()
        
        self.data=[None]*self.w
        for i in range(self.w):
            self.data[i]=[None]*self.h
        
        mapcount=self.h*self.w
        
        start=startx+starty*self.h
        
        k1=start
        while k1==start:
            k1=random.choice(range(0,mapcount))
        
        k2=k1
        while k2==k1 or k2==start:
            k2=random.choice(range(0,mapcount))
        
        k3=k1
        while k3==k1 or k3==k2 or k3==start:
            k3=random.choice(range(0,mapcount))                
        
        c=0
        for x in range(self.w):
            for y in range(self.h):
                map=Map(maps[x][y], tiles, x, y)
                if c in [k1,k2,k3]:
                    map.hide_key()
                self.data[x][y]=map                  
                c+=1
                
    def get(self, x, y):
        return self.data[x][y]
    
    def can_move_up(self,map):
        if map.single:
            return 0
        wy=map.world_y
        if wy==0:
            return 0
        else:
            return 1
    
    def can_move_down(self,map):
        if map.single:
            return 0
        wy=map.world_y
        if wy<self.h-1:
            return 1
        else:
            return 0

    
    def can_move_right(self,map):
        if map.single:
            return 0        
        wx=map.world_x
        if wx<self.w-1:
            return 1
        else:
            return 0

    
    def can_move_left(self,map):
        if map.single:
            return 0        
        wx=map.world_x
        if wx==0:
            return 0
        else:
            return 1

    
    def move(self, co, map):
        """Returns the new map relative to the old map"""
        if map.single:
            return OUT_OF_WOLRD
        x, y=co
        wx=map.world_x
        wy=map.world_y

        if x==1:
            if wx > 0:
                #move right
                return self.data[wx-1][wy]
        if x==-1:
            if wx < self.w-1:
                #move left
                return self.data[wx+1][wy]
                
        if y==1:
            if wy > 0:
                #move up
                return self.data[wx][wy-1]
        if y==-1:
            # move down
            if wy < self.h-1:
                return self.data[wx][wy+1]    
        
        return OUT_OF_WOLRD
