import pygame
from pygame.locals import *
import scene
import qgl
import math
import leafs
import data

class exitMenu:
    pass

class xmenu(scene.EventHandler):
    def __init__(self, theScene, options):
        scene.EventHandler.__init__(self)
        self.d={}
        self.options = options.keys()
        self.callbacks = options
        self.scene = theScene 
        self.viewport = qgl.scene.OrthoViewport()
        self.viewport.screen_dimensions = (0,0,800,600)
        self.rootnode.add(self.viewport)
        self.shown=False
        self.selected=None
        self.groups=[]
        self.textures = []
        
        for option in self.options:
            try:
                name = data.filepath("base-%s.png"%option)
                open(name,"r")
                texture = qgl.scene.state.Texture(name)
            except Exception, e:
                texture = qgl.scene.state.Texture(data.filepath("base.png"))
            self.textures.append(texture)
        
    @property
    def rootnode(self):
        return self.scene.root_node
        
    def select(self, group):
        if group in self.groups:
            elemento = self.options[self.d[group]]
            handler = self.callbacks[elemento]
            self.pop_handler()    
            if handler is exitMenu:
                return
            self.push_handler(handler(self.worldPopupPosition))
            
    def convertDiffToOGL(self):
        ax,ay,bx,by=self.viewport.screen_dimensions 
        return (bx-ax)/2, (by-ay)/2
        
    def calc(self, pos):
        #def r1(coef, r, k):
        #    """returns 2 puntos"""
        #    return [(r*math.sin(coef*k), r*math.cos(coef*k)),
        #            (r*math.sin(coef*(k+1)), r*math.cos(coef*(k+1)))]
        def r2(startAng, coef2, r, k):
            """returns 2 puntos"""
            return [(r*math.sin(startAng), r*math.cos(startAng)),
                    (r*math.sin(startAng+coef2), r*math.cos(startAng+coef2))]

        #make it's group
        count = len(self.options)
        groups=[]
        
        r=80.0
        coef = math.pi*2 / count
        coef2 = coef*0.95
        cc = coef*0.025
        bandRatio=7.0/8
        dx,dy=self.convertDiffToOGL()
        for k in range(count):
            g=qgl.scene.Group()
            v = [(0,0)]+ r2(coef*k+cc,coef2,r*bandRatio,k)+r2(coef*k+cc,coef2,r,k)
            # #draw a textured square..
            ##groups[k].add(texture, sphere)
            ##groups[k].translate = (r*math.sin(c), r*math.cos(c), 0) 
            ##groups[k].scale = (1, 1, 1)
            # #draw a simple triangle with simplest shading
            #v = [(0,0)]+ r1(coef,r*bandRatio,k)+r1(coef,r,k)
            #groups[k].add( texture, leafs.Triangle(v) )
            
            sphere = qgl.scene.state.Quad((40,40))            
            gg = qgl.scene.Group()
            gg.add(self.textures[k], sphere)
            pp = v[2][0]+v[3][0], v[2][1]+v[3][1]
            gg.translate= ( pp[0]/2,pp[1]/2,0)
            
            g.add( leafs.PorcionMuzza(v) )
            g.add(gg)
            
            g.selectable = True
            g.translate=pos[0]-dx,dy-pos[1],0            
            self.d[g]=k
            groups.append(g)
        self.groups = groups

    def handle_event(self, event):
        picker = self.scene.picker
        if event.type is MOUSEMOTION:
            picker.set_position(event.pos)
            self.rootnode.accept (picker)
            if picker.hits:
                self.moves(picker.hits)
                
        elif event.type is MOUSEBUTTONDOWN:
            picker.set_position(event.pos)
            self.rootnode.accept(picker)
            if picker.hits:
                for hit in picker.hits:
                    self.select(hit)
            else:
                self.pop_handler()
                
        elif event.type is USEREVENT:
            if event.code is scene.EV_HANDLER_ACTIVE:
                pos = self.popupPosition
                self.show(pos)
            elif event.code is scene.EV_HANDLER_PASSIVE:
                self.hide()

            
    def mouseIn(self, group):
        t = group.scale
        if t[0]<1.5:
            group.scale=t[0]+0.1,t[1]+0.1,t[2]
                        
    def mouseOut(self, group):
        t = group.scale
        if t[0]>1:
            group.scale=1,1,t[2]
            
    def moves(self, groups):
        oldselected = self.selected
        groups = filter(lambda g:g in self.groups, groups)
        self.selected = groups[0]
        self.mouseIn(self.selected)
        #for oldg in oldselected:
        if oldselected not in [self.selected, None]:
            self.mouseOut(oldselected)
    
    def show(self, pos):
        self.calc(pos)
        self.viewport.add( *self.groups )
        self.viewport.accept(self.scene.compiler)
        self.shown=True
        
    def hide(self):
        self.viewport.remove( *self.groups )    
        self.shown=False
        
    def switch(self, pos=None):
        if self.shown:
            self.hide()
        else:
            if pos is None:
                raise ValueError('Invalid position')
            self.show(pos)
                
    def popup(self, position):
        self.popupPosition = position
        self.worldPopupPosition = self.scene.worldPosFromMouse(position)
        self.scene.push_handler(self)
