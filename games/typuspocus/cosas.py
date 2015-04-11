import pygame
import os
base = "escenario/cosas/"

all = []
for i in os.listdir(base):
    if i[-3:] in ["png", "bmp", "gif"]:
        locals()[i.split(".")[0]] = pygame.image.load(base + i)
        all.append( locals()[i.split(".")[0]])
        
del os
del pygame
del base