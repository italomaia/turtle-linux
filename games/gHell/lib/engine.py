import sys
import pygame
from pygame.locals import *
import string
DEBUG = 0


class Game:
    def __init__(self, x_size, y_size, framerate=30, title=None, icon=None):
        pygame.mixer.pre_init(44100, -16, False)
        pygame.init()
        pygame.mixer.init()
        self.screen_size = x_size, y_size
        self.x_size = x_size
        self.y_size = y_size
        if icon:
            icon = pygame.image.load(icon)
            icon.set_colorkey((255,0,255))
            pygame.display.set_icon( icon ) 
        self.screen = pygame.display.set_mode((x_size, y_size))
        if title:
            pygame.display.set_caption( title ) 
        pygame.mixer.set_reserved(3)
        self.framerate = framerate   
        self.clock = pygame.time.Clock()
        
    def run(self, scene):
        scene.run( )
        if DEBUG: print "FPS:", self.clock.get_fps()
        
    def tick(self):
        return self.clock.tick(self.framerate)

   
        
class SceneExit(Exception):
    pass
    
class Scene:
    bg_color = (0,0,0)
    log_font_size = 16
    @property 
    def background(self):
        if self._background is None:
            self._background = pygame.Surface(self.game.screen.get_size()).convert()
            self._background.fill(self.bg_color)
        return self._background
        
    def __init__(self, game, *args, **kwargs):
        self.game = game
        self._background = None
        self.subscenes = []
	self.logpos = 0
	self.logfont = pygame.font.Font(None, self.log_font_size)
        self.init(*args, **kwargs)
        
    def init(self): pass
        
    def end(self, value=None):
        self.return_value = value
        raise SceneExit()
        
    def runScene(self, scene):
        ret = scene.run()
        if DEBUG: print "Left Scene", str(scene), "with", ret
        self.paint()
        return ret
        
    def run(self):
        if DEBUG: print "Entering Scene:", str(self)
        self.game.screen.blit(self.background, (0,0))
        for s in self.subscenes: s.paint()
        self.paint()
        pygame.display.flip()
        while 1:
            delta = self.game.tick()
	    self.logpos = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                else:
                    try:
                        self.event(event)
                    except SceneExit:
                        return self.return_value
                    
            try:
                self.loop(delta)
                for s in self.subscenes: s.loop(delta)
            except SceneExit:
                return self.return_value
            for s in self.subscenes: s.update()
            self.update()
            pygame.display.flip()
        
    def log(self, text):
        surf = self.logfont.render(text, 1, (255,255,255))
        self.logpos += surf.get_height()
        self.game.screen.blit( surf, (3, self.logpos) )
        
    def event(self, evt):
        pass
        
    def loop(self, delta):
        pass
        
    def update(self):
        pass
        
    def paint(self):
        self.update()
        
class View:
    def __init__(self, game, x_center, y_center, view_scale):
        self.game = game
        self.x_center = x_center
        self.y_center = y_center
        self.view_scale = view_scale
        
    def scale_to_screen(self, distance):
        return distance*self.view_scale

    def scale(self, scale):
        self.view_scale *= scale
        
    def scale_to(self, scale):
        self.view_scale = scale
                
        
    def to_screen(self, (x, y)):
        screen_x_center = self.game.x_size/2
        screen_y_center = self.game.y_size/2
        dx = x - self.x_center
        dy = -y - self.y_center
        nx = dx*self.view_scale
        ny = dy*self.view_scale
        return (int(nx+screen_x_center), int(ny+screen_y_center))
                
    def from_screen(self, (x,y)):
        screen_x_center = self.game.x_size/2
        screen_y_center = self.game.y_size/2
        dx = x-screen_x_center
        dy = -y+screen_y_center
        nx = dx/self.view_scale
        ny = dy/self.view_scale
        dx = nx + self.x_center
        dy = ny + self.y_center
        return (int(nx), int(ny))
        
        
def main():
    g = Game(800, 600, framerate = 20, title = "Dasher Clone")
    g.run( space(g) ) 
    
if __name__ == "__main__":
    main()    

     
