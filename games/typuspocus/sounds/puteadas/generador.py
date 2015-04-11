import random
import pygame
pygame.init()
pygame.display.init()
raices=["forr", "bolud", "pelotud", "conchud", "pajer", "culiad", "put"]
desinencias=["o", "a", "isimo", "isima", "ongo", "onga", "ote", "ota", "ito", "ita", "azo", "aza"]
#finales=["", " del orto", " de mierda", " del carajo"]

insultos=[(r,d) for r in raices for d in desinencias]
random.shuffle(insultos)

clock=pygame.time.Clock()
#channel = pygame.mixer.Channel(pygame.mixer.find_channel())
channel = pygame.mixer.Channel(1)
finish = False
while not finish:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    if not channel.get_busy():
        if len(insultos) > 0:
            r,d = insultos.pop()
            try:
                rs = pygame.mixer.Sound(r+".ogg")
                ds = pygame.mixer.Sound(d+".ogg")
                channel.play(rs)
                channel.queue(ds)
            except:
                print "problema con:", r, d
        
        else:
            finish = True


