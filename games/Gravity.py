import pygame
from pygame.locals import *
import random, math, sys

pygame.init()

while True:
    ParticleNumber = raw_input("Enter how many particles to draw: ")
    try:
        ParticleNumber = int(ParticleNumber)
        break
    except:
        print "\nWell, now.  Let's try that again."

Surface = pygame.display.set_mode((800,600))

Particles = []
class Particle:
    def __init__(self):
        self.x = random.randint(10,790)
        self.y = random.randint(10,590)
        self.speedx = 0.0
        self.speedy = 0.0
        self.mass = 4
        self.radius = math.sqrt(self.mass)
for x in range(ParticleNumber):
    Particles.append(Particle())
def Move():
    for P in Particles:
        for P2 in Particles:
            if P != P2:
                XDiff = P.x - P2.x
                YDiff = P.y - P2.y
                Distance = math.sqrt((XDiff**2)+(YDiff**2))
                if Distance < 10: Distance = 10
                #F = (G*M*M)/(R**2)
                Force = 0.125*(P.mass*P2.mass)/(Distance**2)
                #F = M*A  ->  A = F/M
                Acceleration = Force / P.mass
                XComponent = XDiff/Distance
                YComponent = YDiff/Distance
                P.speedx -= Acceleration * XComponent
                P.speedy -= Acceleration * YComponent
    for P in Particles:
        P.x += P.speedx
        P.y += P.speedy
def CollisionDetect():
    for P in Particles:
        if P.x > 800-P.radius:   P.x = 800-P.radius;  P.speedx *= -1
        if P.x < 0+P.radius:     P.x = 0+P.radius;    P.speedx *= -1
        if P.y > 600-P.radius:   P.y = 600-P.radius;  P.speedy *= -1
        if P.y < 0+P.radius:     P.y = 0+P.radius;    P.speedy *= -1
        for P2 in Particles:
            if P != P2:
                Distance = math.sqrt(  ((P.x-P2.x)**2)  +  ((P.y-P2.y)**2)  )
                if Distance < (P.radius+P2.radius):
                    P.speedx = ((P.mass*P.speedx)+(P2.mass*P2.speedx))/(P.mass+P2.mass)
                    P.speedy = ((P.mass*P.speedy)+(P2.mass*P2.speedy))/(P.mass+P2.mass)
                    P.x = ((P.mass*P.x)+(P2.mass*P2.x))/(P.mass+P2.mass)
                    P.y = ((P.mass*P.y)+(P2.mass*P2.y))/(P.mass+P2.mass)
                    P.mass += P2.mass
                    P.radius = math.sqrt(P.mass)
                    Particles.remove(P2)
def Draw():
    Surface.fill((25,0,0))
    for P in Particles:
        pygame.draw.circle(Surface, (255,255,255), (int(P.x),int(600-P.y)), int(round(P.radius)))
##        Surface.set_at((int(P.x),int(600-P.y)),(255,255,255))
    pygame.display.flip()
def GetInput():
    keystate = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT or keystate[K_ESCAPE]:
            pygame.quit(); sys.exit()
def main():
    while True:
        GetInput()
        Move()
        CollisionDetect()
        Draw()
if __name__ == '__main__': main()
