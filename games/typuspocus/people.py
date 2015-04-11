import os, re, time
import pygame
from random import Random
from pygame.locals import *
from engine import Game, Scene
SCREEN_SIZE=(800,600)
PPLSIZE = (55, 119)
filasx, filasy = (800/55,600/119)

random = Random()
def resetRandom(level_number):
    global random
    random.seed(int(time.time()/60/15)+level_number*100)

states = normal, amboslevantados = range(2)

iStates = states

class SampleScene(Scene):
    """simply makes a lot of people"""
    def init(self, nombre, wardrobes, level=1):
        self.nombre = nombre
        self.goscene = False
        self.finalizar = False
        self.wardrobes = wardrobes
        self.pool = []
        self.level=level
        
        for i in range(30):
            some = Individual(random.choice(self.wardrobes))
            some.random(level=self.level) #level between 1 and ..
            self.pool.append(some)
        
        background = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA|pygame.HWSURFACE)
        self.background = background
        for y in range(filasy):
            for x in range(filasx):
                some = Individual(random.choice(self.wardrobes))
                some.random(level=self.level)
                self.putIndividualAt(some, x, y)
                
    def putIndividualAt(self, individual, x, y):
        sx,sy = PPLSIZE
        dx = (y%2) * sx/2 - sx/2
        img = individual.render()[random.randint(0,1)]
        self.background.blit(img,(sx*x+dx, sy/2*y)) 
    
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
            retorno = self.runScene( 
                        SampleScene(self.game, self.nombre+" hijo ") )
            self.goscene = False
        if self.finalizar:
            self.end( self.nombre )
                    
    def update(self):
        x,y = random.randint(0,filasx-1), random.randint(0,filasy-1)
        self.putIndividualAt(self.pool[random.randint(0,29)], x,y)
        
        self.game.screen.blit(self.background, (0,0))
        font = pygame.font.SysFont("Times New Roman",30)
        s = font.render(self.nombre,True,(0,255,255))
        self.game.screen.blit(s, (0,0))

AnyPublic, PG18, Exibisionist = range(3)
BehaviourDatas = {
    AnyPublic: {
        "behind":0.5, 
        "body":0.999, 
        "hair":0.9,
        "underware":0.8,
        "tops":1,
        "bottoms":1,
        "shoes":1,
        "jackets":0.1,
        "hats":0.1,
        "infront":0.15},
    PG18: {
        "behind":0.5, 
        "body":0.95, 
        "hair":0.7,
        "underware":0.4,
        "tops":0.9,
        "bottoms":0.9,
        "shoes":0.8,
        "jackets":0.7,
        "hats":0.5,
        "infront":0.3},
    Exibisionist: {
        "behind":0.8, 
        "body":0.90, 
        "hair":0.7,
        "underware":0.2,
        "tops":0.05,
        "bottoms":0.05,
        "shoes":0.7,
        "jackets":0.3,
        "hats":0.5,
        "infront":0.3}
    }

class Individual:

    def __init__(self, wardrobe):
        """Each person must have a wardrobe, Ha!"""
        self.wardrobe=wardrobe
        self.layers={}
    
    def random(self, level=1, clothinBehavior=BehaviourDatas[AnyPublic]):
        #choose some layers by it's probe
        sl=[]
        for layer in self.wardrobe.getLayers():
            if random.random()<clothinBehavior[layer]:
                sl.append(layer)
        
        #if this individual is not going to have a body
        #at least let him be well clothed, for its health!        
        if not 'body' in sl:
            sl=clothinBehavior.keys()
            sl.remove('body')
        
        #let's wardrobe calculate weights for this level
        self.wardrobe.adjustProbForLevel(level)
        
        #choose clothes, please!!
        for layer in sl:
            if not self.wardrobe.articles.has_key(layer):
                continue
            r = random.random()
            s = 0
            for art in self.wardrobe.articles[layer]:
                s += art.absProb(level)
                if r<s or s==1:
                    self.layers[layer]=art
                    break
                
    def __repr__(self):
        return repr(self.layers)

    def render(self, state):
        LayerHandsUp = ['body', "tops", "shoes", "bottoms", 'jackets']
        layerorder = self.wardrobe.getLayerorder()
        order = layerorder.keys()
        order.sort()
        MAGENTO = (254,0,254)
        
        img = None
        for k in order:
            layername=layerorder[k]
            if layername in self.layers.keys():
                #we use that layer!
                article = self.layers[layername]
                #check variants:
                if state==amboslevantados and layername in LayerHandsUp:
                    xname = article.name
                    try:
                        nname=article.name[:-4]+'_brazos_arriba.gif'
                        article = self.wardrobe.all[nname]
                    except:
                        pass
                if img==None:
                    #img = pygame.image.load('escenario/sinbutaca.png')
                    img = pygame.Surface((91, 139))
                    img.fill(MAGENTO)
                    nx,ny = article.SnapPos()
                    img.blit(article.getImage(), article.SnapPos())
                    x,y=img.get_size()
                else:
                    nimg = article.getImage()
                    x, y = article.SnapPos()
                    xsize, ysize = img.get_size()
                    img.blit(nimg, (x,y))
        img = img.convert()
        img.set_colorkey(MAGENTO)
        return img
        


BasicFieldList = """"0"     "id"
"1"     "imageName"
"2"     "category"
"3"     "layer"
"4"     "snapPosX"
"5"     "snapPosY"
"6" "wearing"
"7" "waldrobe" """.split('\n')

class FieldSet:
    RE = re.compile(r'"(.*)"[ \t]*"(.*)".*')
    def __init__(self, fields=BasicFieldList):
        for f in fields:
            g = FieldSet.RE.match(f)
            if not g:
                raise Exception('Invalid fields "%s"'%repr(f))
            k,v=g.groups()
            setattr(self,v.lower(),int(k))

class Article:
    RE = re.compile('"(.*)" *'*7 + '.*')    
    def __init__(self, dataline, fieldset, path=''):
        self.fieldset = fieldset
        m = Article.RE.match(dataline)
        if not m : raise Exception('Invalid article data "%s"'%repr(dataline))    
        self.data = m.groups()
        self.image = None
        self.path = path
        
        self.probByLevel = map(lambda s:float(s), 
                            self.getSome('wearing').split(':') )
        self.probLevels = len(self.probByLevel)
        self.absProbL={}
        
    def absProb(self, level):
        return self.absProbL[level]
        
    def setAbsProbForLevel(self, level, prob):
        self.absProbL[level]=prob
        
    def probLevel(self, level):
        if level>self.probLevels:
            level=self.probLevels
        return self.probByLevel[level-1]
        
    def __repr__(self):
        return self.name

    def getSome(self,some):
        return self.data[getattr(self.fieldset,some)]
    def getLayer(self):
        return self.getSome('layer')
    def getName(self):
        return self.getSome('imagename')
        
    def getImage(self):
        if self.image==None:
            self.image=pygame.image.load(self.path+self.name).convert_alpha()
        return self.image
    def SnapPos(self):
        return int(self.getSome('snapposx')),int(self.getSome('snapposy'))
    layer=property(getLayer)
    name=property(getName)
    
class Wardrobe:
    def __init__(self, path, articles_txt="articles.txt", behaviour=BehaviourDatas[AnyPublic] ):
        self.behaviour = behaviour
        self.articles_txt = articles_txt
        self.articles={}
        self.weights={}
        self.calculatedLevels = {}
        self.layers = {}
        self.all = {}
        self.parseConfig(path)
        self.parseArticles(path)
        
    def add(self, article):
        layer = article.layer
        self.layers [ layer ] = None        
        artlist = self.articles.setdefault(layer, [])
        artlist.append(article)
        self.articles[layer]=artlist
        self.all[article.name]=article
        
    def adjustProbForLevel(self, level):
        if self.calculatedLevels.has_key(level):
            #skip if we made calculations beore
            return
            
        for layer in self.layers.keys():
            if not self.articles.has_key(layer): continue
            ##count probability definition
            ## -1: same as any other article with -1 
            ##          (let's call the quantity: standardCount)
            ## x :  0<=x<=1 set x as probability 
            ##          (let's call its sum: absolute total)
            standardCount, absoluteTotal = 0, 0
            for article in self.articles[layer]:
                probDef = article.probLevel(level)
                if probDef == -1: standardCount += 1
                else:  absoluteTotal += probDef
            
            if standardCount != 0:
                #so the articles with standard probe will have
                # (1-absoluteTotal)/standardCount probability eachone           
                standardArtProb = (1.0-absoluteTotal)/standardCount
            else:
                standardArtProb = 0
            
            #now, take articles with standard prob. and setup them
            # with anabsolute Probability!
            for article in self.articles[layer]:
                prob = article.probLevel(level)
                if prob==-1:
                    article.setAbsProbForLevel(level, standardArtProb)
                else:
                    article.setAbsProbForLevel(level, prob)
        #calculation complete
        self.calculatedLevels[level]=None
            
    def getLayers(self):
        return self.articles.keys()
    
    def getLayerorder(self):
        return self.ordered
        
    def parseConfig(self,path):
        """get layers"""
        R = re.compile(r'"layer(.*)" *"(.*)".*')
        self.layers={}
        self.ordered = {}
        f = open(path+'config.txt')
        for l in f:
            if l[0]=='#': continue
            m = R.match(l)
            if m:
                k,v = m.groups()
                self.layers[v]=int(k)
                self.ordered[int(k)]=v
        f.close()
    
    def parseArticles(self, path):
        articlelist=[]
        self.fieldlist=[]
        buscando, leyendoFields, leyendoArticles, listo = range(4)
        status = buscando
        fpath=path+r'/data/'
        f = open(path+'/'+self.articles_txt)
        for l in f:
            l = l.strip('\n')
            if status==buscando:
                self.fieldset = FieldSet() #basic default fieldset
                if l.startswith('HCDataSetFile_fields'):
                    status=leyendoFields
                    
            elif status==leyendoFields:
                if l.startswith('HCDataSetFile_data'):
                    self.fieldset = FieldSet(self.fieldlist)
                    status=leyendoArticles
                elif l.startswith('#'): pass
                elif l.startswith('"'):
                    self.fieldlist.append(l)
                    
            elif status==leyendoArticles:
                if l.startswith('"'):
                    self.add(Article(l, self.fieldset, path+'/data/'))
                elif l.startswith('#'):
                    pass
                else: pass
            elif status==listo:
                break
        f.close()
    
def getAllWardrobes():
    return [
        Wardrobe('audiencia/boy/'),
        Wardrobe('audiencia/girl/'),
        Wardrobe('audiencia/fashion_boy/'),
        Wardrobe('audiencia/fashion_girl/'),
        Wardrobe('audiencia/goth/'),
    ]

all_wardrobes = getAllWardrobes()
def buildIndividual(level, wardrobes):
    if wardrobes is None:
        wardrobes = all_wardrobes
    wd=random.choice(wardrobes)
    i= Individual(wd)
    i.random(level=level+1, clothinBehavior=wd.behaviour)
    return i
    
if __name__ == "__main__":
    wardrobes = getAllWardrobes() # x,y
    g = Game(*SCREEN_SIZE, **{'framerate': 200})
    g.run( SampleScene(g, "Scene1", wardrobes, level=6) )
    
    
