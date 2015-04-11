import qgl
import pygame
from pygame.locals import *
import data

from scene import Scene
from actions import *
from menu import Menu

import view
import options
import main_menu

DADDY_FALL = 8000 # milliseconds

class Intro(Scene):
    
    def __init__(self, world, menuEnable=0):
        Scene.__init__(self, world)

        self.root_node.background_color = view.CELESTE_CIELO

        clouds = self.createClouds()
        clouds2 = self.createClouds2()
        clouds3 = self.createClouds3()
        plane = self.createAirplane()
        devil = self.createDevil()
        jesus = self.createJesus()
        alien = self.createAlien()
        dad = self.createDad()
        varita = self.createVarita()

        self.accept()

        self.initMenus(menuEnable)

        self.actionManager = Manager()
        # cloud (background)
        self.actionManager.do( clouds, 
            delay(DADDY_FALL) +
            repeat( 
                call( lambda: setattr( clouds,"translate", Point3(random.randint(-100,100),-200,0) ) ) +
                move(Point3(0,1600,0),duration=18000) +
                random_delay(2000,4000) ) )

        self.actionManager.do( clouds2, 
            delay(DADDY_FALL) +
            repeat( 
                call( lambda: setattr( clouds2,"translate", Point3(random.randint(-100,100),-200,0) ) ) +
                move(Point3(0,1600,0),duration=24000) +
                random_delay(2000,5000) ) )

        self.actionManager.do( clouds3, 
            delay(DADDY_FALL) +
            repeat( 
                random_delay(2000,6000) +
                call( lambda: setattr( clouds3,"translate", Point3(random.randint(-100,100),-200,0) ) ) +
                move(Point3(0,1600,0),duration=12000) ) )

        # airplane
        self.actionManager.do( plane, 
            repeat( 
                random_delay(40000,45000) +
                call( lambda: setattr( plane,"translate", Point3(600,random.randint(-300,300),0) ) ) +
                move((-1500,0,0),duration=3000) ) )

        # devil
        self.actionManager.do( devil,
            repeat( random_delay(50000,80000) +
                call( lambda: setattr( devil,"translate", Point3(random.randint(-380,0),-600,0) ) ) +
                call( lambda: setattr( devil,"scale", Point3(0.75,0.75,1) ) ) +
                move((0,1500,0),duration=30000) ) )

        # jesus 
        self.actionManager.do( jesus,
            repeat( random_delay(30000,70000) +
                call( lambda: setattr( jesus,"translate", Point3(random.randint(0,380),-600,0) ) ) +
                call( lambda: setattr( jesus,"scale", Point3(0.6,0.6,1) ) ) +
                move((0,1500,0),duration=35000) ) )

        # alien 
        self.actionManager.do( alien,
            repeat( random_delay(40000,50000) +
                call( lambda: setattr( alien,"translate", Point3(random.randint(-400,400),600,0) ) ) +
                call( lambda: setattr( alien,"scale", Point3(0.9,0.9,1) ) ) +
                move((0,-1500,0),duration=30000) ) )
                    

        # daddy
        action_fall = goto(Point3(0,0,0), duration=DADDY_FALL)
        action_rot = rotate(1080,duration=DADDY_FALL)
        action_rot2 = repeat( rotate(360,duration=16000/3) )
        self.actionManager.do( dad, action_fall )
        self.actionManager.do( dad, call(self.playFreeFall) + delay(18000) + call(self.showMenu) + move( (0,-110,0), duration=2000 ) )
        self.actionManager.do( dad, action_rot + call(self.playMusic) + action_rot2 ) 

        
        # varita
        self.actionManager.do( varita,
            repeat( random_delay(20000,30000) +
                call( lambda: setattr( varita,"translate", Point3(random.randint(-400,400),600,0) ) ) +
                move((0,-1200,0),duration=15000) ) )
        self.actionManager.do( varita, repeat( rotate(-360,duration=2000 ) ) )
        
    ### Sky
    def createCloud( self, imageName, initialPos, size ):
        skyGroup = qgl.scene.Group()
        skyTexture = qgl.scene.state.Texture(data.filepath(imageName))
        skyQuad = qgl.scene.state.Quad( size )
        skyGroup.add(skyTexture)
        skyGroup.add(skyQuad)
        skyGroup.axis = (0,0,1)
        skyGroup.angle = 0
        skyGroup.translate = initialPos
        return skyGroup

    def createClouds( self ):
        clouds = qgl.scene.Group()
        c1 = self.createCloud( "cloud1.png", (-200,-800,0), (345,189) )
        c3 = self.createCloud( "cloud3.png", ( 250,-200,0), (284/2,104/2) )
        clouds.add(c1)
        clouds.add(c3)
        clouds.axis = (0,0,1)
        clouds.angle = 0
        clouds.translate = (0,-200,0)
        self.add_group(clouds)
        return clouds

    def createClouds2( self ):
        clouds = qgl.scene.Group()
        c2 = self.createCloud( "cloud2.png", ( 0,-300,0), (527,221) )
        c3 = self.createCloud( "cloud3.png", ( -250,-200,0), (284/2,104/3) )
        clouds.add(c2)
        clouds.add(c3)
        clouds.axis = (0,0,1)
        clouds.angle = 0
        clouds.translate = (0,-200,0)
        self.add_group(clouds)
        return clouds

    def createClouds3( self ):
        clouds = qgl.scene.Group()
        c1 = self.createCloud( "cloud1.png", (-200,-800,0), (345/2,189/2) )
        c2 = self.createCloud( "cloud2.png", ( 150,-300,0), (527/2,221/2) )
        clouds.add(c1)
        clouds.add(c2)
        clouds.axis = (0,0,1)
        clouds.angle = 0
        clouds.translate = (0,-200,0)
        self.add_group(clouds)
        return clouds

    ### Airplane
    def createAirplane( self ):
        plane = qgl.scene.Group()
        planeTexture = qgl.scene.state.Texture(data.filepath("biplane.png"))
        planeQuad = qgl.scene.state.Quad((100,46))
        plane.add(planeTexture)
        plane.add(planeQuad)
        plane.axis = (0,0,1)
        plane.angle = 0
        plane.translate = (600,0,0)
        self.add_group(plane)
        return plane 

    ### People
    def createPerson(self, imageName, initialPos, size=(64,128) ):
        personGroup = qgl.scene.Group()
        dadTexture = qgl.scene.state.Texture(data.filepath(imageName))
        dadQuad = qgl.scene.state.Quad(size)
        personGroup.add(dadTexture)
        personGroup.add(dadQuad)
        personGroup.axis = (0,0,1)
        personGroup.angle = 0
        personGroup.translate = initialPos
        return personGroup

    def createDad(self):
        dad = self.createPerson( "dad-handsup-mouth.gif", (0,500,0) )
        self.add_group(dad)
        return dad

    def createDevil(self):
        devil = qgl.scene.Group()
        body = self.createPerson("body_diablo.png", (0,0,0), (49,118) )
        c2 = self.createCloud( "cloud2.png", ( 0,-50,0), (527/2,221/2) )
        devil.add(body)
        devil.add(c2)
        devil.axis = (0,0,1)
        devil.angle = 0
        devil.translate = (0,-600,0)
        self.add_group(devil)
        return devil

    def createJesus(self):
        jesus = qgl.scene.Group()
        body = self.createPerson("body_jesus.png", (0,0,0),(49,118) )
        c2 = self.createCloud( "cloud2.png", ( 0,-50,0), (527/2,221/2) )
        jesus.add(body)
        jesus.add(c2)
        jesus.axis = (0,0,1)
        jesus.angle = 0
        jesus.translate = (0,-600,0)
        self.add_group(jesus)
        return jesus 

    def createAlien(self):
        alien = self.createPerson("alien_brazos_arriba.png", (0,600,0) )
        alien.angle = 180
        self.add_group(alien)
        return alien 

    ### Objects
    def createVarita(self):
        varita = self.createPerson("varita.png", (1200,0,0), (32,64) )
        self.add_group(varita)
        return varita 

    ### Menu
    def initMenus(self,menuEnable):
        self.menuOn = menuEnable 
        self.optionsMenu = options.Options(self,self.game)
        self.mainMenu = main_menu.MainMenu(self,self.game)
        self.levelsMenu = main_menu.LevelsMenu(self,self.game)
        self.optionsMenu.disable()
        self.optionsMenuEnabled = False
        self.levelsMenu.disable()
        self.levelsMenuEnabled = False
        if not self.menuOn:
            self.mainMenuEnabled = False
            self.mainMenu.disable()
        else:
            self.mainMenuEnabled = True
            self.mainMenu.enable()


    def update(self, dt):
        if dt>1000:
            return
        self.actionManager.loop(dt)
        if self.mainMenuEnabled:
            self.mainMenu.update(dt)
        elif self.optionsMenuEnabled:
            self.optionsMenu.update(dt)
        elif self.levelsMenuEnabled:
            self.levelsMenu.update(dt)

    def update_event(self, event):
        if self.mainMenuEnabled:
            self.mainMenu.update_event(event)
        elif self.optionsMenuEnabled:
            self.optionsMenu.update_event(event)
        elif self.levelsMenuEnabled:
            self.levelsMenu.update_event(event)
        if event.type == KEYDOWN:
            if self.menuOn == False:
                self.menuOn = True
                self.mainMenuEnabled = True
                self.mainMenu.enable()

    # Handlers 
    def showMenu( self ):
        if not self.menuOn:
            self.menuOn = True
            self.mainMenuEnabled = True
            self.mainMenu.enable()
            
    def playFreeFall( self ):
        pygame.mixer.music.load( data.filepath("sonidos/freefall.ogg") )
        pygame.mixer.music.play()

    def playMusic( self ):
        pygame.mixer.music.load( data.filepath("music/01 - Songe Original mix.ogg") )
        pygame.mixer.music.play()
        
    def on_quit(self):
        self.game.quit = True
