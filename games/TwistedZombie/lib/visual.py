import sys
import pygame
from pygame.locals import *

class Visual(object):
    def __init__(self, screen, images, times, func=None):
        self.screen = screen
        self.images = images
        if times == -1:
            self.times = -1
        else:
            self.times = [x*1000 for x in times]
        self.func = func    #father function
        

    def loop(self):
        if self.times == -1:
            self.screen.blit(self.images, (0,0))
            pygame.display.flip()
            while True:
                pygame.event.clear()
                event = pygame.event.wait()
                if (event.type == QUIT):
                    sys.exit(0)
                elif (pygame.key.get_pressed()[K_RETURN]) or (pygame.key.get_pressed()[K_ESCAPE]):
                    pygame.event.clear()
                    break
            return self.func
        else:
            for image, time_sleep in zip(self.images, self.times):
                self.screen.blit(image, (0,0))
                pygame.display.flip()
                i = 1
                while i < time_sleep:
                    pygame.time.delay(1)
                    i += 1
                    if pygame.event.peek([KEYDOWN, KEYUP, QUIT]):
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                sys.exit(0)
                            if event.type == KEYDOWN and \
                                (event.key in [K_ESCAPE, K_RETURN, K_KP_ENTER]):
                                return self.func
        return self.func

if __name__ == '__main__':
    print 'main'
    def prueba():
        print 'funcion devuelta'

    pygame.init()
    size = (700,550)
    screen = pygame.display.set_mode(size)
    fill = [(0,0,0), (255,255,255), (127,127,127), (50,50,50)]
    images = []
    for x in range(4):
        image = pygame.Surface(screen.get_size())
        image = image.convert()
        image.fill(fill[x])
        images.append(image)
    # time in milisecons
    times = [950,700,650,800]
    visual = Visual(screen, images, times, prueba)
    func = visual.loop()
    func()
