import qgl
import world
from scene import Scene
import leafs
import pygame
import qgl
import euclid
import world
import data
import random
import math, time
from intro import Intro 
from main_menu import MainMenu
import separador

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from common import *
from zza import xmenu

import scene 
import zza

QUAD_HEIGHT=4
CELESTE_CIELO = (0.09, 0.27, 0.64, 0)
PUERTA_SIZE=(1655,2189)

def addBall(theView):
    class AddBall(scene.doNothingHandler):
        view = theView
        def __init__(self, popupPosition, *a):
            scene.doNothingHandler.__init__(self, *a)
            self.popupPosition = popupPosition
            print "adding ball...", a, popupPosition
        def run(self):
            self.view.addBallEv(self.popupPosition)
    return AddBall

def rectaHandler(theView):
    class RectaHandler(scene.twoClicks):
        view=theView
        def __init__(self, popupPosition, *a):
            scene.twoClicks.__init__(self, *a)
            self.popupPosition = popupPosition
        def run(self):
            if self.click2.position is None:
                self.pop_handler()
                self.view.hideLineGhost()            
            elif not self.view.addLineEv(self.popupPosition, self.click2.position):
                self.click2=None
                self.push_handler(self)
            else:
                self.view.hideLineGhost()            
        def motion(self, position):
            self.view.showLineGhost(self.popupPosition, position)
            
    return RectaHandler

        
def GroupAdd(f):
    def bigF(self, *args, **kwargs):
        ng = f(self, *args,**kwargs)
        ng.accept(self.compiler)
        self.group.add(ng)
        return ng
    return bigF


class InterludeScene(Scene):
    def __init__(self, nextScene, text="press enter...", *a):
        Scene.__init__(self, *a)
        self.nextScene = nextScene
        font = data.filepath('You Are Loved.ttf')
        figure = leafs.TextoAlineado(text, font, size=1000, alignx=0.5, aligny=0.5)
        self.group.add(figure)
        self.accept()

    def update(self, dt):
        pass

    def update_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.game.change_scene(Intro(self.game,True))
        elif event.type == KEYDOWN:
            self.game.change_scene(self.nextScene(self.game))


class View(Scene):
    textoWin = "level completed!"
    CAMERA_AREA=(690, -700, -690, 500) # left, top, right, bottom
    mountainScale = 1.0

    @property
    def textoWin(self):
        return self.name + " completed"

    def setup_level(self):
        return
    def centerMouse(self):
        ww, wh = WINDOW_SIZE
        pygame.mouse.set_pos(ww/2,wh/2)
            
    def __init__(self, game):
        Scene.__init__(self, game, ORTHOGONAL)
        self.centerMouse()
        self.ceilings = None
        self.lastPut = None
        self.horEnergy = True #riq's preferences
        self.world = world.World()
        self.ballsAtGoal = 0
        self.lost = 0
        self.llss = [] #limited life segments
        self.attractors = []
        self.root_node.background_color = CELESTE_CIELO
        self._energy = 2000
        self.cameraArea = self.CAMERA_AREA
        self.maxEnergy=3000
        import sound
        sound.playRandomSong()
        
        self.setup_level()
             
        mountainsGroup = qgl.scene.Group()
        mountainsTexture = qgl.scene.state.Texture(data.filepath("montagnas.png"))
        FACTOR= 5.5
        mountainsQuad = qgl.scene.state.Quad((2403/FACTOR,427/FACTOR))
        mountainsGroup.scale = (self.mountainScale, self.mountainScale, 0.0)
        mountainsGroup.translate = (0,-55.-70.0*(self.cameraArea[3])/500.,0)
        mountainsGroup.add(mountainsTexture, mountainsQuad)
        self.group.add(mountainsGroup)

        self.initLineGhost()
        self.group.scale = (5.0,5.0,0.0)
        self.initScores()
        self.updateScores()
        self.accept()

    def initScores(self):
        self.font = data.filepath('You Are Loved.ttf')
        self.scoreg = qgl.scene.Group()
        self.lostg = qgl.scene.Group()
        self.savedg = qgl.scene.Group()

        self.energyg = qgl.scene.Group()
        if not self.horEnergy:
            scoreQuad = leafs.AlignedQuad( (32,512), 0.5, 1 ) 
            scoreText = qgl.scene.state.Texture(data.filepath("fullcharge.png"))
            self.energyg.scale = (1,1,1)
            self.energyg.translate=(0,-280,0)
        else:
            scoreQuad = leafs.AlignedQuad( (128,16), 1, 0.5 ) 
            scoreText = qgl.scene.state.Texture(data.filepath("fullcharge.png"))
            #scoreText = qgl.scene.state.Texture(data.filepath("emptycharge.png"))
            self.energyg.scale = (1,1,1)
            self.energyg.translate=(-50,210,0)
            
        color = qgl.scene.state.Color ( (1.0,1.0,1.0, 0.7) )
        self.energyg.add(scoreText, color, scoreQuad)
        #self.energyg.angle = 90
        self.energyg.accept(self.compiler)
        self.scoreg.add(self.energyg)
        self.scoreg.translate= (-330, 0,0)
        self.root_node.add(self.scoreg)


        ##self.emptyg = qgl.scene.Group()        
        ##base = qgl.scene.state.Quad((64,16))
        ##empty = qgl.scene.state.Texture(data.filepath("fullcharge.png"))
        ##self.emptyg.translate=(0,-3,0)
        ##self.emptyg.scale = (0.4,0.2,1)
        ##self.emptyg.add(empty,base)
        ##self.energyg = qgl.scene.Group()
        ##scoreQuad = qgl.scene.state.Quad((64,16))
        ##scoreText = qgl.scene.state.Texture(data.filepath("fullcharge.png"))
        ##self.energyg.scale = (0.20,0.20,1)
        ##self.energyg.translate=(0,-3,0)
        ##self.energyg.add(scoreQuad, scoreText)
        
        #ballGroup = qgl.scene.Group()
        #ballTexture = qgl.scene.state.Texture(data.filepath("scoreback2.png"))
        #ballQuad = qgl.scene.state.Quad((64,8))
        #ballGroup.add(ballTexture)
        #ballGroup.add(ballQuad)
        #ballGroup.translate=(0,1,0)
        #ballGroup.scale=(0.6,1,1)

        #self.scoreg.add(ballGroup)        
        ##self.scoreg.add(self.emptyg)
        ##self.scoreg.add(self.energyg)
        self.scoreg.add(self.lostg)
        self.scoreg.add(self.savedg)
        
    def updateScores(self):
        def rend(st):
            scoreg = qgl.scene.Group()
            figure = leafs.TextoAlineado(st, self.font, 
                    size=100, alignx=0.5, aligny=0.5)
            col = qgl.scene.state.Color( (1.0,1.0,1.0, 1) )
            scoreg.add(col,figure)
            scoreg.scale = (5,5,1)
            return scoreg

        e = self.energy()
        #print 'energy:',e
        if not self.horEnergy:
            self.energyg.scale = (1,  e*1.0/self.maxEnergy, 1)
        else:
            self.energyg.scale = (e*1.0/self.maxEnergy, 1, 1)
        
        self.scoreg.remove(self.savedg)
        self.savedg = rend("saved: %d/%d"%(self.ballsAtGoal,self.target))
        self.savedg.translate = (0,250,0) 
        self.scoreg.add(self.savedg)
        
        self.scoreg.remove(self.lostg)
        self.lostg = rend("lost: %d/%d"%(self.lost,self.lives))
        self.lostg.translate= (0,270,0)
        self.scoreg.add(self.lostg)
        self.scoreg.accept(self.compiler)

    def addLineEv(self, (x1,y1), (x2,y2)):
        if self.can_put(x1,y1,x2,y2):
            segment = world.Segment(x1, y1, x2, y2)
            self.world.add_passive(segment)
            self.lastPut = time.time()
            v=euclid.Vector2(x1,y1)-euclid.Vector2(x2,y2)
            self._energy -= self.vectorReqEnergy(v)
            if self._energy<0: self._energy=0
            return True
        return False
        
    def energy(self):
        if not self.lastPut is None:
            t=time.time()
            self._energy+=(t-self.lastPut)*self.energyRegenCoef
            if self._energy>self.maxEnergy:
                self._energy=self.maxEnergy
            self.lastPut = t
        return self._energy
        
    def vectorReqEnergy(self, v):
        return v.magnitude()** (1.5)
    
    def can_put(self, x1,y1,x2,y2):
        #check put
        v=euclid.Vector2(x1,y1)-euclid.Vector2(x2,y2)
        if v.magnitude()==0:
            return False
        y=max(y1,y2)
        #print 'aca:',self.vectorReqEnergy(v), self.energy()
        testenergy = (self.vectorReqEnergy(v)<self.energy())
        #print y, self.ceilings
        return ((self.ceilings is None) or (y<self.ceilings)) and (testenergy)
        
    def isValid(self, npos):
        x,y=npos
        return (self.ceilings is None) or (y<self.ceilings)
    
                
    def addBallEv(self, worldPos):
        ball = world.Ball(euclid.Point2(*worldPos) )
        self.addBall(ball)
        
    def levelFinished(self):
        self.game.score += self.score()
        self.game.change_scene(
            separador.Interlude(self.nextLevel, self.textoWin, self.game))
        
    def score(self):
        return (self.ballsAtGoal * 2 - self.lost) 
        
    def levelLost(self):
        self.game.change_scene(separador.Separador(self.game, self.score()))

    def update(self, dt):
        import sound
        self.world.loop(self.step)
        for evt in self.world.get_events():
            #print 'EVENTO:',evt
            if isinstance(evt, world.Collision):
                n = evt.ball.velocity.magnitude()/50
                if (n>1.0):
                    n = 1.0
                vol = 1.0
                sound.playSound(n, vol)
                
            elif isinstance(evt, world.BallAtGoal):
                self.ballsAtGoal += 1
                self.lost-=1
                if self.ballsAtGoal>=self.target:
                    #you won
                    self.levelFinished()

            elif isinstance(evt, world.ObjectGone):
                self.group.remove(evt.object.group)
                if isinstance(evt.object, world.Ball):
                    self.lost+=1
                    if self.lost>=self.lives:
                        self.levelLost()
                
            elif isinstance(evt, world.NewObject):
                # check hierarchy upside-down
                if isinstance(evt.object, world.Ball):
                    self.addBall(evt.object)
                elif isinstance(evt.object, world.Floor):
                    self.addFloor(evt.object)
                elif isinstance(evt.object, world.LimitedLifeSegment):
                    self.addLimitedLifeSegment(evt.object)
                elif isinstance(evt.object, world.Segment):
                    self.addSegment(evt.object)    
                elif isinstance(evt.object, world.Generator):
                    self.addGenerator(evt.object)
                elif isinstance(evt.object, world.Goal):
                    self.addGoal(evt.object)
                elif isinstance(evt.object, world.Ceiling):
                    self.addCeiling(evt.object)
                elif isinstance(evt.object, world.Attractor):
                    self.addAttractor(evt.object)
                else:
                    print evt.object    
                    print evt.object.__class__
                    raise "Unknown Object"
        self._update_camera2(pygame.mouse.get_pos())

    def _update_camera2(self, pos):
        left, up = 0, 0
        right, down = WINDOW_SIZE
        bound_left, bound_top, bound_right, bound_bottom = self.cameraArea
        
        camera_x = (bound_right-bound_left)*float(pos[0]-left)/(right-left) + bound_left
        camera_y = (bound_bottom-bound_top)*float(pos[1]-up)/(down-up) + bound_top
        
        self.group.translate = (camera_x, camera_y, 0)

    def getViewMatrix(self):
        translate = -1*euclid.Point3(*self.group.translate)
        scale = euclid.Point3(1.0/self.group.scale[0], 1.0/self.group.scale[1], 0)
        return euclid.Matrix4.new_scale(*scale).translate(*translate)

    def handle_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.game.change_scene(Intro(self.game,True))
        elif event.type == KEYDOWN and event.key == K_F10:
            self.levelFinished()
        elif event.type is MOUSEMOTION:
            pass
        elif event.type is MOUSEBUTTONDOWN:
            if event.button<>1:
                return
            self.picker.set_position(event.pos)
            self.root_node.accept(self.picker)
            if len(self.picker.hits)>0:
                for hit in self.picker.hits:
                    return
            else:
                h = rectaHandler(self)
                npos = self.worldPosFromMouse(event.pos)
                if self.isValid(npos):
                    self.push_handler( h(npos ) )
                #self.menu.popup(event.pos)

    def worldPosFromMouse(self, mousePos):
        a,b = self.screenToAmbient(*mousePos)             
        x1,y1,z1 = self.getViewMatrix() * euclid.Point3(a,b,0)
        return x1, y1

    def render(self):
        for ball in self.world.balls:
            position = ball.position
            ball.group.translate = (position.x, position.y, 0)
            ball.group.angle -= ball.velocity[0]
        for at in self.attractors:
            at.group.angle += at.force/10
        for ls in self.llss:
            d = 1- ( ls.hits * 1.0/ls.life)
            col = ls.color
            col.rgba = ( 1.0,1.0,1.0,d)
        self.updateScores()
        self.root_node.accept(self.renderer)
        
    @GroupAdd
    def addBall(self,ball):
        ballGroup = qgl.scene.Group()
        ballTexture = qgl.scene.state.Texture(data.filepath("dad.gif"))
        ballQuad = qgl.scene.state.Quad((3,6))
        ballGroup.add(ballTexture)
        ballGroup.add(ballQuad)
        ballGroup.axis = (0,0,1)
        ballGroup.angle = 180
        position = ball.position
        ballGroup.translate = (position.x, position.y, 0)
        ball.group = ballGroup
        return ballGroup

    @GroupAdd
    def addFloor(self, *a, **kw):
        return self.addSegment(*a, **kw)

    def initLineGhost(self):
        self.ghostGroup = qgl.scene.Group()
        self.ghostGroup.scale = (0,0,0)
        segmentTexture = self.getCloudTexture(30)
        segmentQuad = qgl.scene.state.Quad((1,QUAD_HEIGHT))
        self.ghostColor = qgl.scene.state.Color( (1.0,1.0,1.0,0.5))
        self.ghostGroup.add(segmentTexture, self.ghostColor, segmentQuad)
        self.group.add(self.ghostGroup)

    def showLineGhost(self, (x1, y1), (x2, y2)):
        dy = y2-y1
        dx = x2-x1
        energy = self.vectorReqEnergy(euclid.Vector2(dx,dy))
        #print energy, self.energy()
        if (energy>self.energy()) or (not self.isValid( (x2,y2) ) ):
            self.ghostColor.rgba= ( 1.0, 0.0, 0.0, 0.5 ) 
        else:
            self.ghostColor.rgba= ( 1.0, 1.0, 1.0, 0.5 ) 
        self.ghostGroup.angle = math.degrees(math.atan2(dy, dx))
        self.ghostGroup.translate = ( x1 + dx/2, y1 + dy/2, 0.0 )
        size = math.hypot(dx,dy)+1
        self.ghostGroup.scale = (size, 1.0, 0.0)

    def hideLineGhost(self):
        self.ghostGroup.scale = (0,0,0)

    def addCeiling(self, ceiling):
        if self.ceilings is None or (self.ceilings> ceiling.height):
            self.ceilings = ceiling.height
            
            self.ceilingsGroup = qgl.scene.Group()
            ceilingTexture = qgl.scene.state.Texture(data.filepath("opl_sky1.png"))
            ceilingQuad = leafs.AlignedQuad( (800,600), 0.5, 1)
            self.ceilingsGroup.translate = (0,self.ceilings,0)
            color = qgl.scene.state.Color( (1.0, 1.0, 1.0, 0.5) )
            self.ceilingsGroup.add(ceilingTexture, color, ceilingQuad)
            self.ceilingsGroup.accept(self.compiler)
            self.group.add(self.ceilingsGroup)
            #self.addSegment(ceiling)

    def getSizeImage(self, size):
        partes = [ (10, 0), (30,1), (60,2), (999999999999,3)]
        for maxSize, numImg in partes:
            if size <= maxSize:
                return numImg
        
        
    def getCloudTexture(self, size):
        print size, self.getSizeImage(size)
        return qgl.scene.state.Texture(data.filepath("rebotador%d.png"%self.getSizeImage(size)))

    @GroupAdd
    def addSegment(self, segment):
        x1,y1 = segment.segment.p.x, segment.segment.p.y
        dx,dy = segment.segment.v.x, segment.segment.v.y
        
        segmentGroup = qgl.scene.Group()
        segmentGroup.angle = math.degrees(math.atan2(dy, dx))
        size = math.hypot(dx,dy)+1
        segmentGroup.translate = ( x1 + dx/2, y1 + dy/2, 0.0 )
        segmentTexture = self.getCloudTexture(size)
        segmentQuad = qgl.scene.state.Quad((size, QUAD_HEIGHT))
        segmentGroup.add(segmentTexture)
        segmentGroup.add(segmentQuad)
        segment.group = segmentGroup
        return segmentGroup

    @GroupAdd
    def addGoal(self, goal):
        x,y=goal.segment.c.x, goal.segment.c.y
        r=goal.segment.r
        goalGroup = qgl.scene.Group()
        goalGroup.translate = (x, y, 0.0)
        goalTexture = qgl.scene.state.Texture(data.filepath("goal.png"))
        goalQuad = qgl.scene.state.Quad((r*2,r*2))
        goalGroup.add(goalTexture)
        goalGroup.add(goalQuad)
        goalGroup.scale = (1,1.2,1)
        goal.group = goalGroup
        return goalGroup

    @GroupAdd
    def addAttractor(self, atr):
        x,y=atr.position.x, atr.position.y
        r=2.0
        atrGroup = qgl.scene.Group()
        atrGroup.translate = (x, y, 0.0)
        atrTexture = qgl.scene.state.Texture(data.filepath("attractor.png"))
        atrQuad = qgl.scene.state.Quad((r*2,r*2))
        atrGroup.add(atrTexture)
        atrGroup.add(atrQuad)
        atr.group = atrGroup
        atr.angle = 0 
        self.attractors.append(atr)
        return atrGroup


    @GroupAdd
    def addGenerator(self, gen):
        r=2
        x,y = gen.position
        genGroup = qgl.scene.Group()
        genGroup.translate = (x, y, 0.0)
        genTexture = qgl.scene.state.Texture(data.filepath("generador.png"))
        genQuad = qgl.scene.state.Quad((r*2,r*2))
        genGroup.add(genTexture)
        genGroup.add(genQuad)
        gen.group = genGroup
        return genGroup

    @GroupAdd
    def addLimitedLifeSegment(self, segment ):
        x1,y1 = segment.segment.p.x, segment.segment.p.y
        dx,dy = segment.segment.v.x, segment.segment.v.y
        segmentGroup = qgl.scene.Group()
        sgc = qgl.scene.state.Color( ( 1.0,1.0,1.0,1) )
        
        segmentGroup.angle = math.degrees(math.atan2(dy, dx))
        size = math.hypot(dx,dy)+1
        segmentGroup.translate = ( x1 + dx/2, y1 + dy/2, 0.0 )
        segmentTexture = self.getCloudTexture(size)
        segmentQuad = qgl.scene.state.Quad((size,QUAD_HEIGHT))
        segmentGroup.add(segmentTexture, sgc, segmentQuad)
        segment.color=sgc
        segment.group=segmentGroup
        self.llss.append(segment)
        return segmentGroup

if __name__ == '__main__':
    import game
    g = game.Game()
    g.change_scene(View(g))
    g.main_loop()
