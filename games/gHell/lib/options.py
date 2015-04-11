from scene import Scene
from menu import Menu
from common import *
from main_menu import MainMenu

class Options:

    def __init__(self, scene, world):
        self.scene = scene
        items = [
                ("Fullscreen", world.fullscreen),
                ("Return", self.on_return)
                ]
        self.menu = Menu(scene, items, 0)
    
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

    def on_return( self ):
        self.scene.mainMenu.enable()
        self.scene.mainMenuEnabled = True 
        self.scene.optionsMenu.disable()
        self.scene.optionsMenuEnabled = False
