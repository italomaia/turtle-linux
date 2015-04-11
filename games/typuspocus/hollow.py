#!/usr/bin/env python
# Hollow/Outline text module 
# based on code by: Pete Shinners
# http://www.pygame.org/pcr/hollow_outline/index.php

"""
two text rendering styles. outlined and hollow. both
use a single pixel border around the text. you might be
able to cheat a bigger border by fooling with it some.
"""
import os, sys, pygame, pygame.font, pygame.image
from pygame.locals import *

def textOutline(font, message, fontcolor, outlinecolor):
    borde = font.render(message, 1, outlinecolor)
    base = font.render(message, 1, fontcolor)
    img = pygame.Surface( base.get_rect().inflate(2,2).size, 0, base )
    for x in 0,2:
        for y in 0,2:
            img.blit(borde, (x,y) )
    img.blit(base, (1, 1))
    return img


entry_info2 = 'Outlined, by alecu'

#this code will display our work, if the script is run...
if __name__ == '__main__':
    pygame.init()

    #create our fancy text
    white = 255, 255, 255
    grey = 100, 100, 100
    bigfont = pygame.font.Font(None, 60)
    text2 = textOutline(bigfont, entry_info2, grey, white)

    #create a window the correct size
    width, height = text2.get_rect().inflate(10,10).size
    win = pygame.display.set_mode((width, height))
    win.fill((20, 20, 80), (0, 0, width, 30))
    win.fill((80, 20, 80), (0, height-30, width, 30))

    win.blit(text2, text2.get_rect(center=win.get_rect().center))
    pygame.display.flip()
    
    #wait for the finish
    while 1:
        event = pygame.event.wait()
        if event.type is KEYDOWN and event.key == K_s: #save it
            name = os.path.splitext(sys.argv[0])[0] + '.bmp'
            print 'Saving image to:', name
            pygame.image.save(win, name)
        elif event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
            break
