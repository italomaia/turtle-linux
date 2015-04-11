import pygame
from pygame.locals import *
from config import *
import math
import random

class Wheather(pygame.sprite.Sprite):
    gray_scale = range(70,255)

    functions = [lambda x: 20*math.sin(x/4),
                 lambda x: 20*math.cos(x/2)]

    max_velocity = 12
    min_velocity = 2

    def __init__(self,min_radius, max_radius):
        pygame.sprite.Sprite.__init__(self)

        radius = random.choice(range(min_radius,max_radius))

        cordenates = range(700)
        self.x = random.choice(cordenates)
        self.y= random.choice(cordenates)

        surface_size = (8,8)
        pos = (4,4)
        self.image = pygame.Surface(surface_size)
        black = (0,0,0)
        self.image.set_colorkey(black)
        color = random.choice(self.gray_scale)
        gray_color = (color,color,color)
        pygame.draw.circle(self.image, gray_color, pos, radius)

        self.rect = self.image.get_rect()
        self.num = self.count()
        self.func_x = random.choice(self.functions)

    def update(self):
        num = self.num.next()
        num = math.radians(num)
        func_y = 10*num

        pos = (self.func_x(num) + self.x, func_y + self.y)
        self.rect.center = pos
        if self.rect.center[1] > HEIGHT:
            self.rect.center = (0,pos[1])
            self.num = self.count()
            self.y = 0

    def count(self):
        i = random.randrange(self.min_velocity,self.max_velocity)
        x = 0
        while 1:
            x = x+i
            yield x

if __name__ == '__main__':
    import sys
    print 'main'
    pygame.init()
    size = (700,550)
    screen = pygame.display.set_mode(size)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    sprites = []
    group = pygame.sprite.Group()

    for x in range(150):
        sprite = Wheather(1,5)
        group.add(sprite)

    allsprites = pygame.sprite.RenderPlain(group)

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        allsprites.update()

        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()
