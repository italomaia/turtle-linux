import qgl
import pygame
from pygame.locals import *

from menu import Menu
from scene import Scene
import levels

class MainMenu:
    
    def __init__(self, scene, world, initial_option=0):

        items = [
                 ("Start new game", self.on_new_game),
                 ("Options", self.on_options),
                 ("Credits", self.on_credits),
                 ("Quit", self.on_quit),
                 ]

        self.scene = scene
        self.menu = Menu(scene, items, initial_option)

    def update(self, dt):
        self.menu.update()

    def update_event(self, event):
        self.menu.update_event(event)
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.on_quit()

    # Handlers 
    def on_new_game(self):        
        self.scene.mainMenu.disable()
        self.scene.mainMenuEnabled = False
        self.scene.levelsMenu.enable()
        self.scene.levelsMenuEnabled = True 

    def on_credits(self):
        import separador
        self.scene.game.change_scene(separador.Credits( self.scene.game ) )

    def on_quit(self):
        self.scene.game.quit = True

    def on_options(self):
        self.scene.mainMenu.disable()
        self.scene.mainMenuEnabled = False
        self.scene.optionsMenu.enable()
        self.scene.optionsMenuEnabled = True 

    def enable( self ):
        self.menu.enable()

    def disable( self ):
        self.menu.disable()

def runner(g, level):
    def f( ) :
        g.new_game()
        g.change_scene(level(g))
    return f

class LevelsMenu(Scene):
    def __init__(self, scene, world, initial_option=0):
        self.scene = scene
        items=[]
        for level in levels.levels:
            items.append( (level.name, runner(world, level) ) )
        items.append( ("back", self.on_return) )
        self.menu = Menu(scene, items, initial_option)
        
    def update(self, dt):
        self.menu.update()

    def update_event(self, event):
        self.menu.update_event(event)
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.on_return()

    def enable( self ):
        self.menu.enable()

    def disable( self ):
        self.menu.disable()

    # Handlers 
    def on_return(self):
        self.scene.mainMenu.enable()
        self.scene.mainMenuEnabled = True 
        self.scene.levelsMenu.disable()
        self.scene.levelsMenuEnabled = False
