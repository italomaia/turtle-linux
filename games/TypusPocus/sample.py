import pygame
from pygame.locals import *
from engine import Game, Scene

class SampleScene(Scene):
    def init(self, nombre):
        self.nombre = nombre
        self.goscene=False
        self.finalizar = False
        
    def event(self, evt):
        if evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                self.end()
            elif evt.key == K_SPACE:
                self.goscene = True
            elif evt.key == K_RETURN:
                self.finalizar = True
    
    def loop(self):
        # aca updateamos el mundo cada paso
        if self.goscene:
            retorno = self.runScene( SampleScene(self.game, self.nombre + " hijo ") )
            self.goscene = False
            print "devolvio", retorno
        if self.finalizar:
            self.end( self.nombre )
                    
    def update(self):
        self.game.screen.blit(self.background, (0,0))
        font = pygame.font.SysFont("Times New Roman",30)
        s = font.render(self.nombre,True,(0,255,255))
        self.game.screen.blit(s, (0,0))
    
    
if __name__ == "__main__":
    g = Game(800, 600, framerate = 200)
    g.run( SampleScene(g, "Scene1") )