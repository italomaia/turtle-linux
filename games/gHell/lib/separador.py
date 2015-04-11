import qgl
import pygame
from pygame.locals import *
import data

from scene import Scene
from actions import *

import pygame
import view
import main_menu
import leafs
from data import filepath

from intro import Intro

DADDY_FALL = 10000 # milliseconds
ROJO_SANGRE = (0.8, 0.1, 0.05, 0)

class Separador(Scene):
    def update_event(self, event):
        if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
            self.game.change_scene(Intro(self.game,True))
            
    def __init__(self, world, score=0):
        Scene.__init__(self, world)
        self.score = score

        self.root_node.background_color = view.CELESTE_CIELO
        am = self.actionManager = Manager()
        am.do( None,
            delay(10) +
            call(self.next)        
            )
            
    def next(self):
        self.game.change_scene( _Separador( self.game, self.score ) )
    
    def update(self, dt):
        if dt>1000:
            return
        self.actionManager.loop(dt)
        
class _Separador(Scene):
    def update_event(self, event):
        if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
            self.game.change_scene(Intro(self.game, True))
            
    def __init__(self, world, score=0):
        Scene.__init__(self, world)
        self.score = score

        self.root_node.background_color = view.CELESTE_CIELO
        self.font = filepath('You Are Loved.ttf')

        import sound
        self.initializeMusic()
        clouds = self.createClouds()
        clouds3 = self.createClouds()
        dad = self.createDad()
        clouds2 = self.createClouds()
        
        self.accept()
        
        diedline = self.diedline()
        scoretext = self.scoreline()
        scoretext.disable()
        diedline.disable()
        
        am = self.actionManager = Manager()
        am.do( clouds, place( Point3(-200,200,0) ) )        
        
        dad.scale = Vector3(0.1,0.1,1)
        am.do( dad, place( Point3(0,0,0) ) ) 
        am.do( dad, repeat( rotate(360, duration=2100) ) )
        
        am.do( dad, 
            scale( 10, duration=10000  )  +
            spawn( call( scoretext.enable ) ) +
            delay( 4000 ) + 
            scale( 10, duration=5000  ) +
            call(lambda: sound.playMusicSound( self.crash, 1 ) ) +
            call(lambda: 
                setattr(self.root_node, "background_color",ROJO_SANGRE) ) +
            call( diedline.enable ) + 
            place(Point3(-2000,-2000,0))
            )
               
        clouds2.scale = Vector3(20,20,1)       
        am.do( clouds2, place( Point3(-5500,3500,0) ) ) 
        am.do( clouds2, goto( Point3(-600,400,0), duration=10000 ) ) 
               
        am.do( clouds2, 
            scale( 1.0/10, duration=10000 ) +
            place( Point3(-1000, -1000, 0) )
            )
        
        clouds.scale = Vector3(2,2,1)       

        am.do( clouds, 
            place( Point3(-1000, -1000, 0) ) +
            delay ( 10000 ) +
            place( Point3(-600,400,0) ) +
            delay( 4000 ) +
            spawn(goto( Point3(-60,40,0), duration=5000 )) +
            scale( 1.0/10, duration=5000 ) +
            place( Point3(-1000, -1000, 0) ) 

            )
            
        clouds3.scale = Vector3(5,5,1)       

        am.do( clouds3, 
            place( Point3(2000, -2000, 0) ) +
            delay ( 10000 ) +
            delay( 4000 ) +
            spawn(goto( Point3(200,-200,0), duration=5000 )) +
            scale( 1.0/10, duration=5000 ) +
            place( Point3(2000, -2000, 0) ) 
            
            )    
            
        
        sound.playSoundFile("freefall.ogg",1)
        
    def scoreline(self):
        t = self.create_text("you made %i points..."%self.score)
        self.add_group(t)
        self.accept()
        p = t.translate
        t.translate = Point3(p[0], 200, p[2])
        return t
   
    def diedline(self):
        t = self.create_text("and then died.")
        self.add_group(t)
        self.accept()
        p = t.translate
        t.translate = Point3(p[0], -200, p[2])
        return t 
        
    def create_text(self, text):
        f = leafs.TextoAlineado(text, self.font, size=1000, alignx=0.5, aligny=0.5)
        group = qgl.scene.Group()
        group.add(f)
        return group
        
        
    ### Music
    def initializeMusic(self):
        import sound
        self.music = sound.initMusicFile("01 - Songe Original mix.ogg")
        self.crash = sound.initMusicFile("../sonidos/crash.wav")
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
        dad = self.createPerson( "dad-handsup-mouth.gif", (0,700,0) )
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
        jesus = self.createPerson("body_jesus.png", (200,200,0) )
        self.add_group(dad)
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

    def update(self, dt):
        if dt>1000:
            return
        self.actionManager.loop(dt)

        

    # Handlers 
    def playMusic( self ):
        import sound
        sound.playMusicSound(self.music,1)
        
class Interlude(_Separador):
    def __init__(self, nextScene, text="press enter...", *a):

        Scene.__init__(self, *a)
        self.nextScene = nextScene
        


        self.root_node.background_color = view.CELESTE_CIELO
        am = self.actionManager = Manager()
        
        clouds = self.createClouds()
        clouds.translate = (100,0,0)
        clouds2 = self.createClouds2()
        clouds2.translate = (-100,300, 0)
        clouds3 = self.createClouds3()
        clouds3.translate = (50,100,0)
        
        dads = []
        basetime = 2500.0
        for d in range(10):
            dad = self.createDad()
            dad.translate = Point3(-300+60*d, -600, 0)
            if d != 0:
                am.do( dad,
                    delay( sum([ (basetime/(r+1)) for r in range(d)] ) - basetime ) +
                    move((0,1200,0), duration=basetime/(d+1))
                    )
            dads.append( dad )
            
        varita = self.createVarita()

        font = data.filepath('You Are Loved.ttf')
        figure = leafs.TextoAlineado(text, font, size=1000, alignx=0.5, aligny=0.5)
        group = qgl.scene.Group()
        group.add(figure)
        group.translate = (0, 240,0)
        
        self.group.add(group)
        self.accept()
        
        
    def createDad(self):
        dad = self.createPerson( "dad-fly.gif", (0,700,0) )
        self.add_group(dad)
        return dad
        
        
    def update_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.game.change_scene(Intro(self.game, True))
        elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
            self.game.change_scene(self.nextScene(self.game))

def musique(what):
    import data
    pygame.mixer.music.load( data.filepath("sonidos/"+what) )
    pygame.mixer.music.play()

class History(_Separador):
    def __init__(self, game):

        Scene.__init__(self, game)
        import sound

        self.root_node.background_color = (0,0,0,0)
        am = self.actionManager = Manager()
        
        luz = self.create_image("dad.png")
        luz.translate = Point3(60,-10,0)
        luz.scale = (12,4.5,0)
        
        dad_hi = self.createDad()
        dad_hi.translate = Point3(150, -150, 0)
        
        script = [
                ("- hey...", 800),
                ("where am I?", 1800),
                ("this is not home!", 2000),
                ("my teleport spell must have failed", 2000),
                ("lets try again...", 2000),
                (" ", 2000),
                ("ouch!", 1700),                
                ("this didn't work", 2000),                
                ("I'll get help from above", 2300),
                ("I'm going up!", 2000),                
            ]
            
        offset = 0
        lines = []
        for line, duration in script:
            l = self.create_line(line)
            lines.append( ( l, offset, duration) )
            offset += duration
        
        nube =  [ self.create_image("nube%i.png"%i) for i in range(1, 6) ]
        [ setattr(n, "translate", Point3(150, -150,0)) for n in nube ]
        
        
        dad = self.create_image("dad.gif")
        dad.translate = Point3(-350, -150, 0)
        
        self.accept()
        dad_hi.disable()
        luz.disable()
        [ n.disable() for n in nube ]
        [ n.disable() for (n,a,x) in lines ] 
        
        def enable(what):
            def doit():
                what.enable()
            return doit
        def disable(what):
            def doit():
                what.disable()
            return doit
            
        am.do( None,
            delay(20000)+
            call(lambda: musique("grossini talking 1.ogg") ) +
            delay(10600)+
            call(lambda: musique("grossini talking 2.ogg") ) 
            )   
        am.do( dad,
            goto(  Point3(150, -150, 0), duration=5000 ) +
            call(lambda: luz.enable() ) + 
            call(lambda: sound.playSoundFile("farol.wav",1) ) + 
            delay(1500) + 
            call(lambda: musique("Applause.wav") ) +
            delay(2500) + 
            call(lambda: dad.disable()) +
            call(lambda: dad_hi.enable()) +
            delay(6000) +
            call(lambda: sound.playSoundFile("MagiaOK.wav",1) ) +
            call(lambda: dad_hi.disable()) +
            delay(3000) +
            call(lambda: luz.disable() ) + 
            call(lambda: sound.playSoundFile("farol.wav",1) ) 
            )
            
        for (line, start, duration) in lines:
            am.do( line,
                delay(20000)+
                delay(start)+
                call(enable(line))+
                delay(duration)+
                call(disable(line))
                )
        am.do( None,
            delay(20000+4*2000)+
            call(lambda: sound.playSoundFile("tomato.wav",1) ) 
            )
        am.do( None,
            delay(20000+5*2000)+
            call(lambda:setattr(self.root_node, "background_color", (1,1,1,0)))+
            delay(100)+
            call(lambda:setattr(self.root_node, "background_color", (0,0,0,0)))+
            delay(100)+
            call(lambda:setattr(self.root_node, "background_color", (1,1,1,0)))+
            delay(100)+
            call(lambda:setattr(self.root_node, "background_color", (0,0,0,0)))+
            delay(100)
            )
            
        am.do( None, 
            delay( 20000 + duration+start) + 
            call(lambda: self.game.change_scene(Intro(self.game, False)))
            )
        def enable(what):
            def doit():
                what.enable()
            return doit
        def disable(what):
            def doit():
                what.disable()
            return doit
                
      
        for i,n in enumerate(nube):
            am.do( n,
                delay(15500) +
                delay(400*i) +
                call(enable(n)) +
                delay(400) +
                call(disable(n)) 
                )
                
        
    def createDad(self):
        dad = self.createPerson( "dad-wave.gif", (0,700,0) )
        self.add_group(dad)
        return dad
        
    def create_image(self, path):
        dad = self.createPerson( path, (0,700,0) )
        self.add_group(dad)
        return dad
      
    def create_line(self, text): 
        font = data.filepath('MagicSchoolOne.ttf')
        figure = leafs.TextoAlineado(text, font, size=1000, alignx=0.5, aligny=0.5)
        group = qgl.scene.Group()
        group.add(figure)
        group.translate = (0, 0,0)
        
        self.group.add(group)
        return group

    def update_event(self, event):
        if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
            self.game.change_scene(Intro(self.game, False))

class Credits(_Separador):
    def __init__(self, game):

        Scene.__init__(self, game)
        import sound

        self.root_node.background_color = (0,0,0,0)
        am = self.actionManager = Manager()
        
        def enable(what):
            def doit():
                what.enable()
            return doit
        def disable(what):
            def doit():
                what.disable()
            return doit
        
        
        script = [
                ("Divine Inspiration", "David"),
                ("Magic", "Great Grossini"),
                ("Hosting", "leito"),
                ("Hosting", "alecu"),
                ("coding", "dave"),
                ("coding", "riq"),
                ("coding", "alecu"),
                ("coding", "hugo"),
                ("coding", "lucio"),
                ("Music", "Ricardo Vecchio"),
                
            ]
            
        offset = 0
        lines = []
        for cargo, nombre in script:
            l1 = self.create_line(cargo)
            
            l2 = self.create_line(nombre)
            l2.translate = (0,-00,0)
            lines.append( ( l1, l2 ) )


        self.accept()
        [ (l1.disable(), l2.disable()) for (l1,l2) in lines ] 

        def make_title(line):
            l1, l2 = line
            do_title = (
                delay(100)+
                call(lambda: sound.playSoundFile("tomato.wav",1) ) +
                delay(2000)+
                call(lambda:setattr(self.root_node, "background_color", (1,1,1,0)))+
                delay(100)+
                call(lambda:setattr(self.root_node, "background_color", (0,0,0,0)))+
                delay(100)+
                call(lambda:setattr(self.root_node, "background_color", (1,1,1,0)))+
                delay(100)+
                call(lambda:setattr(self.root_node, "background_color", (0,0,0,0)))+
                delay(100)+
                call(lambda:setattr(l2,'translate',Point3(0,00,0)))+
                call(lambda:setattr(l1,'translate',Point3(0,100,0)))+
                call(lambda:setattr(l2,'angle',0))+
                call(lambda:setattr(l1,'angle',0))+

                call(lambda: l1.enable()) +
                call(lambda: l2.enable()) +
                delay(1500)+
                spawn(move(Point3(0,-600,0), duration=1000), target=l1)+
                spawn(move(Point3(0,-600,0), duration=1000), target=l2)+
                spawn(rotate(45, duration=1000), target=l1)+
                spawn(rotate(-45, duration=1000), target=l2)+

                delay(2500)+
                call(lambda: l1.disable()) +
                call(lambda: l2.disable())            
                            
                )        
            return do_title
            
        am.do(None, random_repeat( [ make_title(line) for line in lines ] ))
                
    def createDad(self):
        dad = self.createPerson( "dad-fly.gif", (0,700,0) )
        self.add_group(dad)
        return dad
        
    def create_image(self, path):
        dad = self.createPerson( path, (0,700,0) )
        self.add_group(dad)
        return dad
      
    def create_line(self, text): 
        font = data.filepath('MagicSchoolOne.ttf')
        figure = leafs.TextoAlineado(text, font, size=3000, alignx=0.5, aligny=0.5)
        group = qgl.scene.Group()
        group.add(figure)
        group.translate = (150, 200,0)
        
        self.group.add(group)
        return group

    def update_event(self, event):
        if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
            self.game.change_scene(Intro(self.game, True))
            
class Win(_Separador):
    def __init__(self, game):

        Scene.__init__(self, game)
        import sound

        self.root_node.background_color = view.CELESTE_CIELO
        am = self.actionManager = Manager()
        
        def enable(what):
            def doit():
                what.enable()
            return doit
        def disable(what):
            def doit():
                what.disable()
            return doit
        
        g1 = self.create_image("gift.png")
        g1.translate = Point3(200, -160, 0)

        g2 = self.create_image("gift.png")
        g2.translate = Point3(300, -160, 0)
        
        dad_hi = self.createDad()
        dad_hi.translate = Point3(250, -150, 0)
        
        dad = self.create_image("dad.gif")
        dad.translate = Point3(250, -150, 0)
        
       

        god = self.create_image("god.png")
        god.scale = (6,2,0)
        god.translate = Point3(-200,145,0)        
        
        clouds = self.createClouds()
        clouds.translate = Point3(-540,380,0)
        clouds.scale = (3,3,0)
        clouds3 = self.createClouds2()
        clouds3.translate = Point3(-200,300,0)        
        
        script = [
                ("- hi god!", 2000),
                (" nice to see", 2000),
                (" you are having fun", 2000),
                (" help me!", 2000),
                (" ", 3000),
                (" thanks!", 2000),
            ]
            
        offset = 0
        lines = []
        for line, duration in script:
            l = self.create_line(line)
            lines.append( ( l, offset, duration) )
            offset += duration

        self.accept()
        [ n.disable() for (n,a,x) in lines ] 
        dad_hi.disable()
        g1.disable()
        g2.disable()
        
        am.do( dad,
            delay(5000) +
            call(enable(dad_hi)) +
            call(disable(dad)) +
            delay(2000) +
            call(disable(dad_hi)) +
            call(enable(dad)) +
            delay(8000)+
            call(enable(g1)) +
            call(enable(g2)) 
            
            )
            
        for (line, start, duration) in lines:
            am.do( line,
                delay(5000)+
                delay(start)+
                call(enable(line))+
                delay(duration)+
                call(disable(line))
                )
        
                
    def createDad(self):
        dad = self.createPerson( "dad-fly.gif", (0,700,0) )
        self.add_group(dad)
        return dad
        
    def create_image(self, path):
        dad = self.createPerson( path, (0,700,0) )
        self.add_group(dad)
        return dad
      
    def create_line(self, text): 
        font = data.filepath('MagicSchoolOne.ttf')
        figure = leafs.TextoAlineado(text, font, size=1000, alignx=0.5, aligny=0.5)
        group = qgl.scene.Group()
        group.add(figure)
        group.translate = (170, 0,0)
        
        self.group.add(group)
        return group

    def update_event(self, event):
        if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
            self.game.change_scene(Intro(self.game, True))
