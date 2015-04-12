import pygame, sys, math, time, random
from pygame.locals import *

sys.stderr = file("zerrors.log", "w")
        
def add(p1, p2):
    return [p1[0] + p2[0], p1[1] + p2[1]]

def figurAt(fields, pos):
    if pos[0] >= len(fields) or pos[1] >= len(fields[0]) or pos[0] < 0 or pos[1] < 0:
        raise IndexOutOfRangeException
    return fields[pos[0]][pos[1]]

def materialVergleich(fields):
    punkte = {"Bauer" : 1, "Laufer" : 3, "Springer" : 3, "Turm" : 4.5, "Dame" : 9}
    material = [0, 0]
    for line in fields:
        for figur in line:
            if figur and figur.type != "Koenig":
                material[figur.farbe] += punkte[figur.type]
    if int(material[0]) == material[0]:
        material[0] = int(material[0])
    if int(material[1]) == material[1]:
        material[1] = int(material[1])
    material = [str(material[0]), str(material[1])]
    return material

##def isMatt(fields, farbe):
##    koenig = False
##    for line in fields:
##        if koenig: break
##        for figur in line:
##            if figur and figur.type == "Koenig" and figur.farbe == farbe:
##                koenig = figur
##                break
##    freeFields = koenig.findFields(fields)
##    matt = True
##    for f in freeFields:
##        free = True
##        for line in fields:
##            for figur in line:
##                if figur and figur.farbe != farbe and (list(f) in figur.findFields(fields)):
##                    free = False
##                    break
##            if not free:
##                break
##        if free:
##            matt = False
##            break
##    return matt

def isSchach(fields, farbe):
    koenig = False
    for line in fields:
        if koenig: break
        for figur in line:
            if figur and figur.type == "Koenig" and figur.farbe == farbe:
                koenig = figur
                break
    for line in fields:
        for figur in line:
            if figur and figur.farbe != farbe and (list(koenig.pos) in figur.findFields(fields)):
                return True
    return False

def walk(fields, movelist, pos, farbe):
    freeFields = []
    for m in movelist:
        p = pos
        while True:
            p = add(p, m)
            try:
                figur = figurAt(fields, p)
            except:
                break
            if figur:
                if figur.farbe == (not farbe):
                    freeFields.append(p)
                break
            freeFields.append(p)
    return freeFields

class Figur:
    def __init__(self, pos, farbe):
        self.pos = pos
        self.farbe = farbe

class Bauer(Figur):
    def __init__(self, pos, farbe):
        Figur.__init__(self, pos, farbe)
        self.type = "Bauer"

    def findFields(self, fields):
        freeFields = []
        if self.farbe:
            f = figurAt(fields, add(self.pos, [0, 1]))
            if not f:
                freeFields.append(add(self.pos, [0, 1]))
                if self.pos[1] == 1:
                    f2 = figurAt(fields, add(self.pos, [0, 2]))
                    if not f2:
                        freeFields.append(add(self.pos, [0, 2]))
        else:
            f = figurAt(fields, add(self.pos, [0, -1]))
            if not f:
                freeFields.append(add(self.pos, [0, -1]))
                if self.pos[1] == 6:
                    f2 = figurAt(fields, add(self.pos, [0, -2]))
                    if not f2:
                        freeFields.append(add(self.pos, [0, -2]))
                
        schlagfelder = [add(self.pos, [1, -1 + (self.farbe * 2)])]
        schlagfelder.append(add(self.pos, [-1, -1 + (self.farbe * 2)]))
        for feld in schlagfelder:
            try:
                figur = figurAt(fields, feld)
            except:
                continue
            if figur and figur.farbe == (not self.farbe):
                freeFields.append(feld)
        return freeFields
    def draw(self, screen, width, height):
        add = "gau/" * (not (((self.pos[0] % 2) + (self.pos[1] % 2)) % 2))
        img = pygame.image.load(add + "bauer" + "_schwarz" * (self.farbe == False) + ".bmp")
        screen.blit(img, [self.pos[0] * (width / 8), self.pos[1] * (height / 8)])

class Springer(Figur):
    def __init__(self, pos, farbe):
        Figur.__init__(self, pos, farbe)
        self.type = "Springer"

    def findFields(self, fields):
        freeFields = []
        freeFields.append(add(self.pos, [2, 1]))
        freeFields.append(add(self.pos, [-2, 1]))
        freeFields.append(add(self.pos, [2, -1]))
        freeFields.append(add(self.pos, [-2, -1]))
        freeFields.append(add(self.pos, [1, 2]))
        freeFields.append(add(self.pos, [-1, 2]))
        freeFields.append(add(self.pos, [1, -2]))
        freeFields.append(add(self.pos, [-1, -2]))
        deleteList = []
        for field in freeFields:
            try:
                figur = figurAt(fields, field)
            except:
                deleteList.append(field)
                continue
            if figur and figur.farbe == self.farbe:
                deleteList.append(field)
        for f in deleteList:
            freeFields.remove(f)
        return freeFields
    
    def draw(self, screen, width, height):
        add = "gau/" * (not (((self.pos[0] % 2) + (self.pos[1] % 2)) % 2))
        img = pygame.image.load(add + "springer" + "_schwarz" * (self.farbe == False) + ".bmp")
        screen.blit(img, [self.pos[0] * (width / 8), self.pos[1] * (height / 8)])

class Turm(Figur):
    def __init__(self, pos, farbe):
        Figur.__init__(self, pos, farbe)
        self.type = "Turm"

    def findFields(self, fields):
        return walk(fields, [[0, 1], [0, -1], [1, 0], [-1, 0]], self.pos, self.farbe)
    
    def draw(self, screen, width, height):
        add = "gau/" * (not (((self.pos[0] % 2) + (self.pos[1] % 2)) % 2))
        img = pygame.image.load(add + "turm" + "_schwarz" * (self.farbe == False) + ".bmp")
        screen.blit(img, [self.pos[0] * (width / 8), self.pos[1] * (height / 8)])

class Laufer(Figur):
    def __init__(self, pos, farbe):
        Figur.__init__(self, pos, farbe)
        self.type = "Laufer"

    def findFields(self, fields):
        return walk(fields, [[1, 1], [1, -1], [-1, 1], [-1, -1]], self.pos, self.farbe)
    
    def draw(self, screen, width, height):
        add = "gau/" * (not (((self.pos[0] % 2) + (self.pos[1] % 2)) % 2))
        img = pygame.image.load(add + "laufer" + "_schwarz" * (self.farbe == False) + ".bmp")
        screen.blit(img, [self.pos[0] * (width / 8), self.pos[1] * (height / 8)])

class Dame(Figur):
    def __init__(self, pos, farbe):
        Figur.__init__(self, pos, farbe)
        self.type = "Dame"
        

    def findFields(self, fields):
        return walk(fields, [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]], self.pos, self.farbe)
    
    def draw(self, screen, width, height):
        add = "gau/" * (not (((self.pos[0] % 2) + (self.pos[1] % 2)) % 2))
        img = pygame.image.load(add + "dame" + "_schwarz" * (self.farbe == False) + ".bmp")
        screen.blit(img, [self.pos[0] * (width / 8), self.pos[1] * (height / 8)])

class Koenig(Figur):
    def __init__(self, pos, farbe):
        Figur.__init__(self, pos, farbe)
        self.type = "Koenig"

    def findFields(self, fields):
        freeFields = [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]
        for i in range(len(freeFields)):
            freeFields[i] = add(self.pos, freeFields[i])
        deleteList = []
        for field in freeFields:
            try:
                figur = figurAt(fields, field)
            except:
                deleteList.append(field)
                continue
            if figur and figur.farbe == self.farbe:
                deleteList.append(field)
        for f in deleteList:
            freeFields.remove(f)
        return freeFields
    def draw(self, screen, width, height):
        add = "gau/" * (not (((self.pos[0] % 2) + (self.pos[1] % 2)) % 2))
        img = pygame.image.load(add + "koenig" + "_schwarz" * (self.farbe == False) + ".bmp")
        screen.blit(img, [self.pos[0] * (width / 8), self.pos[1] * (height / 8)])
class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 640, 640
        self.window = pygame.display.set_mode((self.WIDTH, 60 + self.HEIGHT))
        pygame.display.set_caption("Schach")
        pygame.mouse.set_visible(1) ### Maus sichtbar
        self.screen = pygame.display.get_surface()
        self.keyslist = []
        self.fields = [[False for x in range(8)] for y in range(8)]
        for i in range(8):
            self.fields[i][1] = Bauer([i, 1], True)
        for i in range(8):
            self.fields[i][6] = Bauer([i, 6], False)
        self.fields[0][0] = Turm([0, 0], True)
        self.fields[7][0] = Turm([7, 0], True)
        self.fields[0][7] = Turm([0, 7], False)
        self.fields[7][7] = Turm([7, 7], False)
        
        self.fields[2][0] = Laufer([2, 0], True)
        self.fields[5][0] = Laufer([5, 0], True)
        self.fields[2][7] = Laufer([2, 7], False)
        self.fields[5][7] = Laufer([5, 7], False)
        
        self.fields[1][0] = Springer([1, 0], True)
        self.fields[6][0] = Springer([6, 0], True)
        self.fields[1][7] = Springer([1, 7], False)
        self.fields[6][7] = Springer([6, 7], False)
        
        self.fields[3][0] = Dame([3, 0], True)
        self.fields[4][0] = Koenig([4, 0], True)
        self.fields[4][7] = Dame([4, 7], False)
        self.fields[3][7] = Koenig([3, 7], False)

        self.blackimg = pygame.image.load("black.gif")
        self.clickfield = False
        self.turnfarbe = True
        self.font = pygame.font.Font( None, 30)
        self.mainloop()
        
    def controler(self):
        mp = pygame.mouse.get_pos() # Mausposition
        for event in pygame.event.get():
            if event.type == QUIT: # X Oben rechts
                sys.exit(0) # Beenden
                
            if event.type == KEYDOWN: # Taste gedrueckt?
                
                self.keyslist.append(event.key) # Taste an Liste anhaengen

            if event.type == KEYUP: # Taste losgelassen?
                self.keyslist.remove(event.key)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if mp[1] < 640:
                        feld = int(mp[0] / float(self.WIDTH) * 8.0), int(mp[1] / float(self.HEIGHT) * 8.0)
                        if not self.clickfield:
                            if figurAt(self.fields, feld):
                                self.clickfield = feld
                        else:
                            f = figurAt(self.fields, self.clickfield)
                            if list(feld) in f.findFields(self.fields) and f.farbe == self.turnfarbe:
                                #if type(f) == Bauer:
                                #    print "hallo"
                                #    f = [Springer(f.pos, f.farbe), Laufer(f.pos, f.farbe), Turm(f.pos, f.farbe),Dame(f.pos, f.farbe)][int(raw_input("1 Springer, 2 Laeufer, 3 Turm, 4 DAme")) + 1]
                                remember = [figurAt(self.fields, self.clickfield), figurAt(self.fields, feld)]
                                self.fields[feld[0]][feld[1]] = f
                                self.fields[self.clickfield[0]][self.clickfield[1]] = False
                                rempos = f.pos[:]
                                f.pos = feld
                                if isSchach(self.fields, self.turnfarbe):
                                    f.pos = rempos
                                    self.fields[self.clickfield[0]][self.clickfield[1]] = remember[0]
                                    self.fields[feld[0]][feld[1]] = remember[1]
                                else:
                                    self.turnfarbe = not self.turnfarbe
                            self.clickfield = False
                    self.keyslist.append(event.button)
                
            if event.type == MOUSEBUTTONUP:
                try:
                    self.keyslist.remove(event.button)
                except:
                    pass
        if mp[1] < 640:
            feld = int(mp[0] / float(self.WIDTH) * 8.0), int(mp[1] / float(self.HEIGHT) * 8.0)
            f = figurAt(self.fields, feld)
            if f:
                for field in f.findFields(self.fields):
                    pygame.draw.circle(self.screen, (0, 0, 255), [field[0] * 80 + 40, field[1] * 80 + 40], 3)
    def mainloop(self):
        while True:
            self.screen.fill((255, 255, 255))
            material = materialVergleich(self.fields)
            img = self.font.render("Weiss: " + material[1], True, (self.turnfarbe * 255, 0, 0))
            img2 = self.font.render("Schwarz: " + material[0], True, ((not self.turnfarbe) * 255, 0, 0))
            self.screen.blit(img, [180, 645])
            self.screen.blit(img2, [300, 645])
            if isSchach(self.fields, True):
                img = self.font.render("SCHACH!", True, (0, 0, 0))
                self.screen.blit(img, [180, 675])
            if isSchach(self.fields, False):
                img = self.font.render("SCHACH!", True, (0, 0, 0))
                self.screen.blit(img, [300, 675])
            pygame.draw.aaline(self.screen, (0, 0, 0), (0, 640), (640, 640))
            for i in range(8):
                for j in range(8):
                    if ((i % 2) + (j % 2)) % 2 == 0:
                        self.screen.blit(self.blackimg, [i * 80, j * 80])
            for line in self.fields:
                for figur in line:
                    if figur:
                        figur.draw(self.screen, self.WIDTH, self.HEIGHT)
            self.controler()
            pygame.display.flip()
            
start = Game()
