#
# Sokoban in PyGame
#
# by Jordan Trudgett; started 5th Sep, 07
#

import pygame, sys, time, random
from pygame.locals import *
from Conch import *

def get_coords(file):
    source = [x.rstrip() for x in open(file, "r").readlines()]
    longlen = 0
    for i in range(len(source)):
        if longlen < len(source[i]):
            longlen = len(source[i])
    return longlen, len(source)

def make_level_from_file(file):
    array = []
    conv = {".": 0,
            "#": 1,
            "o": 2,
            "*": 3,
            "@": 4,
            "s": 5,
            " ": 1
            }
    source = [x.rstrip() for x in open(file, "r").readlines()]
    for line in source:
        array.append([])
        for unit in line:
            array[-1].append(conv[unit])
    return array

def HighScores(screen, newscore, set):
    global SText, clock, soundbox, myname, IMAGES
    darkness = 10
    if set == None or newscore == None:
        set = ""
        darkness += 10
    if set:
        HS_TITLE, HS_RECT = IMAGES.highscores
    else:
        HS_TITLE, HS_RECT = IMAGES.highscores2
    DSE = IMAGES.DSE
    f = open(".hs"+str(set), "r")
    data = [x.strip().split(", ") for x in f.readlines()]
    while [''] in data:
        data.remove([''])
    for i in range(len(data)):
        data[i][0] = int(data[i][0])
    data.sort()
    if newscore:
        GotPlace = True
        if newscore >= data[-1][0] and len(data) == 10:
            GotPlace = False
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()/2)
        if GotPlace:
            soundbox.PlaySound("BigApplause")
    else:
        GotPlace = False
    for x in range(darkness):
        screen.blit(DSE, (0,0))
        pygame.display.flip()
        time.sleep(0.05)
    time.sleep(0.1)
    dr = screen.blit(HS_TITLE, (512 - (HS_RECT[2]/2), 20))
    pygame.display.update(dr)
    PLAYER = ""
    Returned = False
    if myname:
        PLAYER = myname
    if GotPlace and not myname:
        namep = SText.render("Please enter your name: ", 1, (240, 180, 40))
        namerect = namep.get_rect()
        dr = screen.blit(namep, (512 - namerect[2]/2, HS_RECT[3]+25))
        pygame.display.update(dr)
        while not Returned:
            clock.tick(30)
            for Event in pygame.event.get():
                if Event.type == KEYDOWN:
                    Key = Event.key
                    if Key == K_RETURN:
                        if len(PLAYER) == 0:
                            soundbox.PlaySound("Bling")
                        else:
                            soundbox.PlaySound("Choose")
                            Returned = True
                    elif Key == K_BACKSPACE:
                        PLAYER = PLAYER[:-1]
                    elif len(PLAYER) < 10:
                        getk = pygame.key.name(Key)
                        if (len(getk) == 1 and getk.isalpha() or getk.isdigit()) or getk == "space":
                            if pygame.key.get_mods() and (KMOD_CAPS or KMOD_SHIFT):
                                if getk == "space":
                                    getk = " "
                                PLAYER += getk.upper()
                            else:
                                if getk == "space":
                                    getk = " "
                                PLAYER += getk
                    else:
                        soundbox.PlaySound("Bling")
            dr3 = screen.fill((0,0,0), pygame.rect.Rect(0, HS_RECT[3] + 55, 1024, 30))
            namep2 = SText.render(PLAYER, 1, (240, 180, 40))
            namerect2 = namep2.get_rect()
            dr2 = screen.blit(namep2, (512 - namerect2[2]/2, HS_RECT[3]+55))
            pygame.display.update([dr2, dr3])
        myname = PLAYER
        
    if GotPlace:
        for i in range(len(data)):
            if data[i][0] > newscore:
                data.insert(i, [newscore, PLAYER])
                break
        nhs = open(".hs"+str(set), "w")
        for i in range(len(data[:10])):
            nhs.write(str(data[i][0]) + ", " + data[i][1]+"\n")

    for x in range(len(data[:10])):
        entry = data[x]
        if entry[1].lower() == PLAYER.lower():
            entryt = SText.render(str(entry[0]) + " -- " + entry[1], 1, (50, 250, 255))
        else:
            entryt = SText.render(str(entry[0]) + " -- " + entry[1], 1, (255-(x*10), 140+(x*10), 40))
        entryrect = entryt.get_rect()
        dr = screen.blit(entryt, (512 - entryrect[2]/2, 215 + x * 50))
        pygame.display.update(dr)
        time.sleep(.2)
    rt = SText.render("Press Return to continue", 1, (255, 193, 46))
    rrect = rt.get_rect()
    dr = screen.blit(rt, (512 - rrect[2]/2, 260 + x * 50))
    pygame.display.update(dr)
    In = True
    while In:
        clock.tick(30)
        for Event in pygame.event.get():
            if Event.type == KEYDOWN:
                Key = Event.key
                if Key == K_RETURN:
                    In = False

def load_image(name, colorkey=None, blur = False):
    fullname = os.path.join('gfx', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    if blur:
        image.set_alpha(blur, RLEACCEL)
#    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    image = image.convert_alpha()
    return image, image.get_rect()

def Img_Load(image, colkey = None, blur = False):
    return load_image(image, colkey, blur)

class DataStorage:
    def __init__(self):
        self.char, self.charrect = Img_Load("Catgirl22.png", -1)
        self.wood = Img_Load("Ground.png", -1)[0]
        self.water = Img_Load("Water.png", -1)[0]
        self.darkwater = Img_Load("DarkWater.png", -1)[0]
        self.goalblock = Img_Load("Goalground.png", -1)[0]
        self.gem = Img_Load("Gem.png")[0]
        self.greengem = Img_Load("GreenGem.png")[0]
        self.highscores = Img_Load("High_Scores.png")
        self.highscores2 = Img_Load("High_Scores2.png")
        self.DSE = Img_Load("Darkscreeneffect.png")[0]
        self.menu_bg = Img_Load("menubg.png")[0]
        self.Main_Menu = Img_Load("title.png")
        self.Play = Img_Load("newgame.png"), Img_Load("newgamein.png")
        self.Jumpto = Img_Load("jumpto.png"), Img_Load("jumptoin.png")
        self.Password = Img_Load("password.png"), Img_Load("passwordin.png")
        self.Highscores = Img_Load("highscores.png"), Img_Load("highscoresin.png")
        self.Help = Img_Load("help.png"), Img_Load("helpin.png")
        self.Quit = Img_Load("quit.png"), Img_Load("quitin.png")
        self.Congrats, self.Congrats_Rect = Img_Load("Congratulations.png")
        self.HELP = Img_Load("helpimage.png")[0]
        self.bye, self.byerect = Img_Load("bye.png")
        self.blink = Img_Load("blink.png")[0]
        self.lbgs = ["bg1.png",
                     "bg2.png",
                     "bg3.png",
                     "bg4.png",
                     "bg5.png"
                     ]

        self.tile = {"Wood": self.wood,
                     "Water": self.water,
                     "DarkWater": self.darkwater,
                     "Goalblock": self.goalblock,
                     }
        self.smalltile = {}
        self.small_gem = pygame.transform.scale(self.gem, (20, 38))
        self.small_greengem = pygame.transform.scale(self.greengem, (20, 38))
        self.small_char = pygame.transform.scale(self.char, (20, 38))
        for key in self.tile.keys():
            self.smalltile[key] = pygame.transform.scale(self.tile[key], (20, 38))

class Menu_Item:
    def __init__(self, image, image2):
        self.name = ''
        self.image, self.rect = image
        self.selectedimage, self.selectedimagerect = image2
        self.crect = pygame.rect.Rect(0,0,0,0)

class Tile:
    def __init__(self, height, gtype = "Wood"):
        global IMAGES
        self.tiletype = gtype
        self.gem = False
        self.goal = False
        self.image = IMAGES.tile[gtype]
        self.gemimage = IMAGES.gem
        self.greengemimage = IMAGES.greengem
        self.height = height

class Level:
    def __init__(self, disp, bg, x, y):
        global IMAGES
        self.x = x
        self.y = y
        self.base = y * [x * [Tile(0, "Wood")]]
        self.screen = disp
        self.bg = Img_Load(bg)[0]
        self.char, self.crect = IMAGES.char, IMAGES.charrect
        self.px = 1
        self.py = 1
        self.gemimage = IMAGES.gem
        self.history = []
        self.lastsec = -1

    def level_to_tile(self, levelmap):
        ctype = {0: "Wood",
                 1: "Water",
                 2: "Goalblock",
                 3: "Wood",
                 4: "Goalblock",
                 5: "Wood"}
        for i in range(len(levelmap)):
            row = levelmap[i]
            for j in range(len(row)):
                unit = row[j]
                if levelmap[i][j] == 1 and (i == 0 or j == 0 or i == len(levelmap)-1 or j == len(row) - 1):
                    at = Tile(1, "DarkWater")
                else:
                    at = Tile(1, ctype[levelmap[i][j]])
                if levelmap[i][j] == 2:
                    at.goal = True
                elif levelmap[i][j] == 3:
                    at.gem = True
                elif levelmap[i][j] == 4:
                    at.gem = True
                    at.goal = True
                elif levelmap[i][j] == 5:
                    self.px = j
                    self.py = i
                levelmap[i][j] = at
        return levelmap
    def makepass(self, lev, steps, ts):
        lev = str(lev)
        steps = str(abs(steps))
        ts = str(ts)
        cp = []
        password = ''

        while len(lev) < 3:
            lev = "0" + lev
        while len(steps) < 4:
            steps = "0" + steps
        while len(ts) < 5:
            ts = "0" + ts
        for x in range(3):
            cp.append(lev[x])
        for x in range(4):
            cp.append(steps[x])
        for x in range(5):
            cp.append(ts[x])
        for y in range(3):
            password += chr(65 + y + 2*int(cp[y]))
        for y in range(4):
            password += chr(70 - y + 2*int(cp[y+3]))
        for y in range(5):
            password += chr(68 + y + 2*int(cp[y+7]))
        npass = ""
        for z in range(6):
            npass += password[z*2+1] + password[z*2]
        self.password = npass
    def start(self, level, steps, cl, music, ts, nohigh):
        global clock, soundbox

        pygame.mouse.set_visible(False)
        self.level = cl
        self.nh = nohigh
        if not nohigh:
            self.makepass(cl, steps, ts)
        else:
            self.password = "None"
        self.tSteps = steps
        self.Steps = 0
        self.csong = music
        self.xpad, self.ypad = self.calc_mid(self.base)
        self.blitbg()
        pygame.display.flip()
        while [] in level:
            level.remove([])
        level = self.level_to_tile(level)
        self.array = level
        self.render_tiles_slow()
        self.place_char()
        pygame.event.get()
        while True:
            clock.tick(20)
            cmd = self.get_input()
            mre = None
            if cmd == "Quit":
                soundbox.PlaySound("Blip")
                return False, 0
            elif cmd == "Up":
                mre = self.movep(0,-1)
            elif cmd == "Down":
                mre = self.movep(0,1)
            elif cmd == "Left":
                mre = self.movep(-1,0)
            elif cmd == "Right":
                mre = self.movep(1,0)
            elif cmd == "Undo":
                if len(self.history) > 0:
                    self.moveback(self.history[-1])
                    self.history = self.history[:-1]
                    self.Steps -= 1
            elif cmd == "Restart":
                return "Restart", 0
            if mre:
                self.Steps += 1
            self.blitbg()
            if self.checkwin():
                self.blit_tiles()
                self.place_char()
                return True, self.Steps


    def moveback(self, data):
        global soundbox
        x = data[0]
        y = data[1]
        blockshift = data[2]
        pbx = self.px + x
        pby = self.py + y
        if blockshift:
            self.array[pby][pbx].gem = False
            self.array[self.py][self.px].gem = True
            soundbox.PlaySound("Slide")
        self.px -= x
        self.py -= y
        self.place_char()            

    def checkwin(self):
        for row in self.array:
            for tile in row:
                if tile.goal == True and tile.gem == False:
                    return False
        return True
    def inspect(self, atu, x, y):
        return atu[y][x]

    def dotrack(self, atu, x, y):
        isquare = self.inspect(atu, x, y)
        if isquare.tiletype[-5:] == "Water":
            return False
        if isquare.gem == True:
            return False
        return True

    def movep(self, x, y):
        global soundbox
        inspection = self.inspect(self.array, self.px + x, self.py + y)
        if inspection.tiletype[-5:] == "Water":
            return
        if inspection.gem == False:
            bpx = self.px
            bpy = self.py
            for i in range(5):
                self.px += float(x)/5
                self.py += float(y)/5
                self.place_char()
                time.sleep(0.01)
            self.px = bpx + x
            self.py = bpy + y
            self.history.append([x, y, False])
            return True
        else:
            if self.dotrack(self.array, self.px + (2*x), self.py + (2*y)):
                bpx = self.px
                bpy = self.py
                self.array[self.py+y][self.px+x].gem = False
                self.blitbg()
                soundbox.PlaySound("Slide")
                ox = self.px
                oy = self.py
                for i in range(12):
                    r1 = pygame.rect.Rect(0,0,0,0)
                    r2 = pygame.rect.Rect(0,0,0,0)

                    self.px += float(x)/(9 + [0, 3][y==-1])
                    self.py += float(y)/(9 + [0, 3][y==-1])

                    if i < 9:
                        ntb = self.blit_tiles()
                        for u in range(len(ntb)):
                            self.screen.blit(ntb[u][0], ntb[u][1])
                        r1 = self.place_char(True)
                    elif y != -1:
                        r1 = self.place_char(True, ox + x, oy + y)
                    if y != -1:
                        r2 = self.gem_follow(x, y, ox, oy, i)
                    else:
                        r2 = self.gem_follow(x, y, x, y, 20)
                        r1 = self.place_char(True)
                    pygame.display.update([r1.inflate(30,30), r2.inflate(30,30)])
                    time.sleep(0.005)
                self.px = bpx + x
                self.py = bpy + y
                self.array[self.py+y][self.px+x].gem = True
                self.place_char()
                self.history.append([x, y, True])
                return True
        return False

#    def blit_goals(self):
#        rects = []
#        for row in range(len(self.array)):
#            for col in range(len(self.array[row])):
#                y = self.array[row][col]
#                if y.goal == True:
#                    ar = self.screen.blit(y.goalimage, (col*50 + self.xpad,(row*41 + self.ypad - 31) - 40 * y.height))
#                    rects.append(ar)
#        return rects

    def gem_follow(self, x, y, ox, oy, i):
        dr = pygame.rect.Rect
        if i < 3:
            xtu = ox
            ytu = oy
            gxpad = 0
            gypad = 0
        else:
            xtu = self.px
            ytu = self.py
            gxpad = 16
            gypad = 13
        if x > 0:
            dr = self.screen.blit(self.gemimage, ((xtu+1)*50 + self.xpad - gxpad, (ytu-1)*41 + self.ypad - 50))
        elif x < 0:
            dr = self.screen.blit(self.gemimage, ((xtu-1)*50 + self.xpad + gxpad, (ytu-1)*41 + self.ypad - 50))
        elif y > 0:
            dr = self.screen.blit(self.gemimage, (xtu*50 + self.xpad, ytu*41 + self.ypad - 50 - gypad))
        elif y < 0:
            dr = self.screen.blit(self.gemimage, (xtu*50 + self.xpad, (ytu-2)*41 + self.ypad - 50))
        return dr

    def get_input(self):
        global soundbox
        for Event in pygame.event.get():
            if Event.type == QUIT:
                return "Quit"
            elif Event.type == KEYDOWN:
                Key = Event.key
                if Key == K_q or Key == K_ESCAPE:
                    return "Quit"
                elif Key == K_w:
                    return "Win"
                elif Key == K_DOWN:
                    return "Down"
                elif Key == K_UP:
                    return "Up"
                elif Key == K_LEFT:
                    return "Left"
                elif Key == K_RIGHT:
                    return "Right"
                elif Key == K_r:
                    return "Restart"
                elif Key == K_u:
                    return "Undo"
    def blitbg(self):
        global Text, SText, LEVEL_NOTICE, soundbox
        self.screen.blit(self.bg, (0,0))
        notice = Text.render(LEVEL_NOTICE, 1, (255, 255, 255))
        noticerect = notice.get_rect()
        self.screen.blit(notice, (512 - noticerect[2]/2, 740))
        dr, dr2, dr3, dr5 = 4 * [pygame.rect.Rect(0,0,0,0)]
        if not self.nh:
            stepc2 = SText.render("Steps this set: " + str(self.tSteps + self.Steps) + "     ", 1, (240, 180, 40))
            passw = SText.render("Password: " + self.password, 1, (250, 250, 250))
            stepc2rect = stepc2.get_rect()
            passwrect = passw.get_rect()
            dr2 = self.screen.blit(stepc2, (10, 40))
            dr3 = self.screen.blit(passw, (1000 - passwrect[2], 10))

        stepc = SText.render("Steps: " + str(self.Steps) + "     ", 1, (240, 180, 40))
        dr = self.screen.blit(stepc, (10, 10))
        stepcrect = stepc.get_rect()

        leveln = SText.render("Level " + str(self.level), 1, (255, 255, 255))
        sms = soundbox.MusicGetPos()
        ssec = str((sms/1000)%60)
        
        levelrect = leveln.get_rect()

        dr4 = self.screen.blit(leveln, (512 - levelrect[2]/2, 10))
        smin = str(sms/60000)
        while len(smin) < 2:
            smin = "0" + smin
        while len(ssec) < 2:
            ssec = "0" + ssec
        stime = smin + ":" + ssec
        musiclabel = Text.render("Song: " + self.csong + ' - ' + stime, 1, (255,255,255))
        dr5 = self.screen.blit(musiclabel, (10, 80))

        pygame.display.update([dr, dr2, dr3, dr4, dr5])

    def place_char(self, notdraw = False, usex = None, usey = None):
        self.blitbg()
#        self.blit_tiles(self.base)
        ntb = self.blit_tiles()

        for x in range(len(ntb)):
            self.screen.blit(ntb[x][0], ntb[x][1])
        if not usex:
            drect = self.screen.blit(self.char, (self.px * 50 +self.xpad, self.py * 41 + self.ypad - 90))
        else:
            drect = self.screen.blit(self.char, (usex * 50 +self.xpad, usey * 41 + self.ypad - 90))
        if notdraw:
            return drect
        pygame.display.update([drect.inflate(200,170)])

    def blit_tiles(self, atu = None):
        end = []
        ntb = []
        if not atu:
            atu = self.array
        row = -1
        for trow in atu:
            row += 1
            col = -1
            for tile in trow:
                col += 1
                if tile.tiletype[-5:] == "Water":
                    rheight = 0.5
                else:
                    rheight = 2
                self.screen.blit(tile.image, (col*50 + self.xpad,(row*41 + self.ypad - 31) - 20 * rheight))
                if tile.gem and not tile.goal:
                    ntb.append((tile.gemimage, (col*50 + self.xpad,(row*41 + self.ypad - 71) - 20 * tile.height)))
                if tile.gem and tile.goal:
                    ntb.append((tile.greengemimage, (col*50 + self.xpad,(row*41 + self.ypad - 71) - 20 * tile.height)))
#                if tile.goal:
#                    ntb.append((tile.goalimage, (col*50 + self.xpad,(row*41 + self.ypad - 71) - 20 * tile.height)))
        if end:
            ntb.extend(end)
        return ntb

    def render_tiles_slow(self, atu = None):
        end = []
        if not atu:
            atu = self.array
        row = -1
        for trow in atu:
            row += 1
            col = -1
            for tile in trow:
                col += 1
                if tile.tiletype[-5:] == "Water":
                    rheight = 0.5
                else:
                    rheight = 2
                updrect = self.screen.blit(tile.image, (col*50 + self.xpad,(row*41 + self.ypad - 31) - 20 * rheight))
                if tile.gem and not tile.goal:
                    updrect2 = self.screen.blit(tile.gemimage, (col*50 + self.xpad,(row*41 + self.ypad - 71) - 20 * tile.height))
                if tile.gem and tile.goal:
                    updrect2 = self.screen.blit(tile.greengemimage, (col*50 + self.xpad,(row*41 + self.ypad - 71) - 20 * tile.height))
#                if tile.goal:
#                    updrect3 = self.screen.blit(tile.goalimage, (col*50 + self.xpad,(row*41 + self.ypad - 71) - 20 * tile.height))
                time.sleep(0.005)
                if not tile.gem and not tile.goal:
                    toupd = [updrect] + end
                    pygame.display.update(toupd)
                elif tile.gem and not tile.goal:
                    toupd = [updrect, updrect2] + end
                    pygame.display.update(toupd)
                elif not tile.gem and tile.goal:
                    toupd = [updrect] + end
                    pygame.display.update(toupd)
                else:
                    toupd = [updrect, updrect2] + end
                    pygame.display.update(toupd)

    def calc_mid(self, atu):
        spacex = 1024 - len(atu[0] * 50)
        spacey = 768 - len(atu * 42)
        return spacex/2, spacey/2

class MainMenu:
    def __init__(self, title_image, default_display):
        global IMAGES
        self.count = 0
        self.blinkrect = None
        self.titleimage, self.titlerect = title_image
        self.menuitems = []
        self.selected = 0
        self.bg = IMAGES.menu_bg
        self.screen = default_display
        self.wait = 0
        self.DSE = IMAGES.DSE
        self.blinkimage = IMAGES.blink
        self.NOTICE = "Sokoban by Jordan Trudgett - version 1.00 - 21/09/07 - Written in Python - Powered by Pygame - This game is open-source. Special thanks to Amy for her artistic contribution! Also thanks to various Sokoban level creators for most harder levels!"
        self.noticex = 1024
    def Step_Instruction(self):
        global soundbox
        soundbox.PlaySound("Blip")
    def display_help(self):
        global IMAGES, clock, soundbox
        for x in range(15):
            self.screen.blit(self.DSE, (0,0))
            soundbox.MusicVol(1-x/17.0)
            pygame.display.flip()
        self.screen.blit(IMAGES.HELP, (0,0))
        self.screen.blit(IMAGES.char, (451,180))
        pygame.display.flip()
        In = True
        while In:
            clock.tick(20)
            for Event in pygame.event.get():
                if Event.type == KEYDOWN:
                    Key = Event.key
                    if Key == K_RETURN:
                        In = False
                        soundbox.PlaySound("Blip")
                        break
        for x in range(15):
            soundbox.MusicVol(.882 + x/17.0)
            time.sleep(0.01)
        soundbox.MusicVol(1)

    def blitbg(self):
        self.screen.blit(self.bg, (0,0))

    def levelpreview(self, level):
        lfile = level
        tileconv = {" ": "Water",
                    "#": "Water",
                    "s": "Wood",
                    "o": "Goalblock",
                    "*": "Wood",
                    ".": "Wood",
                    "@": "Goalblock"}
        try:
            level = [x.rstrip() for x in open(os.path.join("levels","level"+str(level)+".map"), "r").readlines()]
        except Exception, e:
            return False
        y = 0
        torefresh = []
        rows, cols = get_coords(os.path.join("levels","level"+str(lfile)+".map"))
        xpad = (1024 - rows * 20)/2 - 10
        ypad = 250 + (512 - cols * 16)/2 - 8
        torefresh.append(self.screen.fill((0,0,0), pygame.rect.Rect(300, 410, 424, 280)))               
        for row in level:
            y += 1
            x = 0
            for unit in row:
                x += 1
                dr = self.screen.blit(IMAGES.smalltile[tileconv[unit]], (xpad + x*20, ypad + y*16))
                if unit == "*":
                    self.screen.blit(IMAGES.small_gem, (xpad + x*20, ypad + y*16 - 7))
                elif unit == "@":
                    self.screen.blit(IMAGES.small_greengem, (xpad + x*20, ypad + y*16 - 7))
                elif unit == "s":
                    self.screen.blit(IMAGES.small_char, (xpad + x*20, ypad + y*16 - 7))
                torefresh.append(dr)
        return torefresh

    def level_entry(self):
        global SText, soundbox, clock
        pygame.key.set_repeat(50)
        level = '1'
        levt = SText.render(level, 1, (255, 255, 255))
        levr = levt.get_rect()

        last = None

        Entering = True
        for x in range(15):
            self.screen.blit(self.DSE, (0,0))
            pygame.display.flip()
            time.sleep(0.01)
        ptext = SText.render("Type the level number or use Left and Right to select.", 1, (255,255,255))
        ptrect = ptext.get_rect()
        dr2 = self.screen.blit(ptext, (512 - ptrect[2]/2, 250))
        dr = screen.fill((70,70,70), pygame.rect.Rect(480, 379 - levr[3]/2, 64, levr[3] + 10))
        self.screen.blit(levt, (512 - levr[2]/2, 384 - levr[3]/2))
        updrect = self.levelpreview(int(level))
        pygame.display.update(updrect)
        pygame.display.update([dr, dr2])
        while Entering:
            clock.tick(20)
            events = self.get_input(True)
            for event in events:
                if event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        soundbox.PlaySound("Blip")
                        if level == '':
                            level = "1"
                        else:
                            level = str(int(level)+1)
                    elif event.key == K_LEFT:
                        if level == '':
                            soundbox.PlaySound("Blip")
                            level = "1"
                        elif int(level) > 1:
                            soundbox.PlaySound("Blip")
                            level = str(int(level)-1)
                    elif event.key == K_ESCAPE:
                        pygame.key.set_repeat(0)
                        return False
                    k = pygame.key.name(event.key)
                    if len(k) == 1 and k.isdigit() and len(level) < 4 :
                        level += k
                        soundbox.PlaySound("Blip")
                    elif k == "backspace":
                        level = level[:-1]
                        soundbox.PlaySound("Blip")
                    elif k == "return":
                        Entering = False
                        break
                    levt = SText.render(level, 1, (255, 255, 255))
                    levr = levt.get_rect()
                    dr = screen.fill((70,70,70), pygame.rect.Rect(480, 379-levr[3]/2, 64, levr[3]+10))
                    self.screen.blit(levt, (512 - levr[2]/2, 384 - levr[3]/2))
                    pygame.display.update(dr)
                    if level == "":
                        pass
                    elif int(level) != last:
                        updrect = self.levelpreview(int(level))
                        if updrect is False:
                            level = str(last)
                            levt = SText.render(level, 1, (255, 255, 255))
                            levr = levt.get_rect()
                            dr = screen.fill((70,70,70), pygame.rect.Rect(480, 379-levr[3]/2, 64, levr[3]+10))
                            self.screen.blit(levt, (512 - levr[2]/2, 384 - levr[3]/2))
                            pygame.display.update(dr)
                        else:
                            pygame.display.update(updrect)
                            last = int(level)
        pygame.key.set_repeat(0)
        if level: return int(level)
        else: return False
                                                     
    def password_entry(self):
        global SText, soundbox
        cpass = ''
        entp = SText.render("Password: (Press escape to cancel)", 1, (255, 255, 255))
        er = entp.get_rect()
        passw = SText.render(len(cpass) * "#", 1, (255, 255, 255))
        pr = passw.get_rect()

        Entering = True
        for x in range(15):
            self.screen.blit(self.DSE, (0,0))
            pygame.display.flip()
            time.sleep(0.01)
        dr3 = screen.fill((70,70,70), pygame.rect.Rect(362, 379-pr[3]/2, 300, pr[3]+10))
        pygame.display.update(dr3)

        dr = self.screen.blit(entp, (512 - er[2]/2, 334 - er[3]/2))
        pygame.display.flip()

        while Entering:

            if len(cpass) >= 12:
                cpass = cpass[:12]
                break
            events = self.get_input(True)
            for event in events:
                if event.type == KEYDOWN:
                    k = pygame.key.name(event.key)
                    if len(k) == 1 and k.isalpha():
                        cpass += k.upper()
                        soundbox.PlaySound("Blip")
                    elif k == "backspace":
                        cpass = cpass[:-1]
                        soundbox.PlaySound("Blip")
                    elif k == "escape":
                        return False, False, False
                    passw = SText.render(len(cpass) * "#", 1, (255, 255, 255))
                    pr = passw.get_rect()
                    dr3 = screen.fill((70,70,70), pygame.rect.Rect(362, 379-pr[3]/2, 300, pr[3]+10))
                    self.screen.blit(passw, (512 - pr[2]/2, 384 - pr[3]/2))
                    pygame.display.update(dr3)
        np = ""
        for x in range(6):
            np += cpass[x*2+1] + cpass[x*2]
        dc = ""
        decoder = [65, 66, 67, 70, 69, 68, 67, 68, 69, 70, 71, 72]
        for x in range(12):
            temp = float(ord(np[x]) - decoder[x])/2
            if int(temp)*2 != int(temp*2):
                return False, False, False
            dc += str(int(temp))
        try:
            return int(dc[:3]), int(dc[3:7]), int(dc[7:])
        except:
            return False, False, False

    def notice_scroll(self, Dotick = True):
        global SText
        noticetext = SText.render(self.NOTICE, 1, (255,255,255))
        noticerect = noticetext.get_rect()
        dr = self.screen.fill((0,0,0), pygame.rect.Rect(0, 720, 1024, noticerect[3]+30))
        self.screen.blit(noticetext, (self.noticex, 732))
        if self.noticex < -noticerect[2]:
            self.noticex = 1024
        if Dotick:
            self.noticex -= 2
            return dr
                         
    def operate(self):
        In = True
        shown = False
        rv = 2
        self.blitbg()
        while In:
            if not self.blinkrect: self.blinkrect = pygame.rect.Rect(830,115,100,100)
            if not self.count % 120 or not (self.count-5) % 120:
                dr2 = self.screen.blit([self.blinkimage,self.bg][self.count % 120 > 0], (0,0))
                pygame.display.update(self.blinkrect)
            dr = self.notice_scroll()
            pygame.display.update(dr)
            if rv == 1:
                self.blitbg()
                self.Step_Instruction()
                self.screen.blit(self.titleimage, (512-(self.titlerect[2])/2,50))
                ay = self.titlerect[3], 800-self.titlerect[3]
                for j in range(len(self.menuitems)):
                    item = self.menuitems[j]
                    imagetoblit = [item.image, item.selectedimage][self.selected==j]
                    rect = [item.rect, item.selectedimagerect][self.selected==j]

                    x = 512 - (rect[2] - rect[0])/2
                    cypos = ((ay[1] / (len(self.menuitems)+1)) * (j+1)) + ay[0]
                    cypos -= (rect[3] - rect[1])/2
                    item.crect[0] = x
                    item.crect[1] = cypos
                    item.crect[2] = item.rect[2]
                    item.crect[3] = item.rect[3]
                    self.screen.blit(imagetoblit, (x,cypos))
                self.notice_scroll(False)
                pygame.display.flip()
            if not shown:
                self.screen.blit(self.titleimage, (512-(self.titlerect[2])/2,50))
                ay = self.titlerect[3], 800-self.titlerect[3]
                for j in range(len(self.menuitems)):
                    item = self.menuitems[j]
                    imagetoblit = [item.image, item.selectedimage][self.selected==j]
                    rect = [item.rect, item.selectedimagerect][self.selected==j]

                    x = 512 - (rect[2] - rect[0])/2
                    cypos = ((ay[1] / (len(self.menuitems)+1)) * (j+1)) + ay[0]
                    cypos -= (rect[3] - rect[1])/2
                    item.crect[0] = x
                    item.crect[1] = cypos
                    item.crect[2] = item.rect[2]
                    item.crect[3] = item.rect[3]
                    self.screen.blit(imagetoblit, (x,cypos))
                self.notice_scroll(False)
                pygame.display.flip()
                shown = True
            elif rv == 0:
                soundbox.PlaySound("Choose")
                return self.selected
                break
            rv = self.get_input()
            clock.tick(40)



    def get_input(self, raw= False):
        global soundbox
        self.count += 1
        if raw:
            return pygame.event.get()
        self.wait += 1
        for Event in pygame.event.get():
            self.wait = 0
            if Event.type == QUIT:
                self.selected = 3
                return 0
            elif Event.type == MOUSEMOTION:
                x = 0
                for item in self.menuitems:
                    if item.crect.collidepoint(Event.pos[0], Event.pos[1]):
                        if x != self.selected:
                            self.selected = x
                            return 1
                        else:
                            break
                    x += 1
            elif Event.type == KEYDOWN:
                Key = Event.key
                if Key == K_q or Key == K_ESCAPE:
                    self.selected = 5
                    return 0
                elif Key == K_DOWN:
                    if self.selected < len(self.menuitems)-1:
                        self.selected += 1
                        return 1
                elif Key == K_UP:
                    if self.selected > 0:
                        self.selected -= 1
                        return 1
                elif Key == K_RETURN:
                    return 0
            elif Event.type == MOUSEBUTTONDOWN:
                return 0
        


# INIT

width = 1024
height = 768

LEVEL_NOTICE = "Arrow keys: Movement. Press 'Q' for menu, 'R' to restart this level or 'U' to undo a step."

Status = pygame.init()
pygame.mouse.set_visible(False)
windowset = False

if len(sys.argv) > 1:
    if sys.argv[1] == "-w":
        window = pygame.display.set_mode((width, height))
        windowset = True

if not windowset:
    window = pygame.display.set_mode((width, height), pygame.FULLSCREEN)

screen = pygame.display.get_surface()

ufont = pygame.font.match_font('bitstreamverasans', 'mgopencanonica', 'bitstreamcourier')

Text = pygame.font.Font(ufont, 20)
SText = pygame.font.Font(ufont, 25)
SuperSmallText = pygame.font.Font(ufont, 12)

screen.fill((0,0,0))
Loadingtext = SText.render("Loading, please wait!", 1, (255,255,255))
Dedic = SuperSmallText.render("Sokoban is precaching resources...", 1, (255,255,255))
lrect = Loadingtext.get_rect()
drect = Dedic.get_rect()
dr = screen.blit(Loadingtext, (512 - lrect[2]/2, 384 - lrect[3]/2))
dr2 = screen.blit(Dedic, (512 - drect[2]/2, 384 - drect[3]/2 + 30))
pygame.display.flip()

IMAGES = DataStorage()

Main_Menu = MainMenu(IMAGES.Main_Menu, screen)
Play = Menu_Item(IMAGES.Play[0], IMAGES.Play[1])
Jumpto = Menu_Item(IMAGES.Jumpto[0], IMAGES.Jumpto[1])
Password = Menu_Item(IMAGES.Password[0], IMAGES.Password[1])
Highscores = Menu_Item(IMAGES.Highscores[0], IMAGES.Highscores[1])
Help = Menu_Item(IMAGES.Help[0], IMAGES.Help[1])
Quit = Menu_Item(IMAGES.Quit[0], IMAGES.Quit[1])
Congrats, Congrats_Rect = IMAGES.Congrats, IMAGES.Congrats_Rect
Main_Menu.menuitems.append(Play)
Main_Menu.menuitems.append(Jumpto)
Main_Menu.menuitems.append(Password)
Main_Menu.menuitems.append(Highscores)
Main_Menu.menuitems.append(Help)
Main_Menu.menuitems.append(Quit)
clock = pygame.time.Clock()
soundbox = Jukebox()
soundbox.LoadSong("Loop_One.ogg", "Loop1")
soundbox.LoadSong("Loop_Two.ogg", "Loop2")
soundbox.LoadSong("Loop_Three.ogg", "Loop3")
soundbox.LoadSong("Loop_Menu.ogg", "Menu")
soundbox.LoadSound("Bling.ogg", "Blip")
soundbox.LoadSound("Big_Applause.ogg", "BigApplause")
soundbox.LoadSound("Blip.ogg", "Bling")
soundbox.LoadSound("Slide.ogg", "Slide")
soundbox.LoadSound("Applause_01.ogg", "Applause")
soundbox.LoadSound("ShortAppreg.ogg", "Choose")

Playlist = ["Loop1", "Loop2", "Loop3"]
Playnames = ["Hill-Side Slide - Slippery Remix (Jordan Trudgett)",
             "Dimly-lit (Jordan Trudgett)",
             "Bounce with me! (Jordan Trudgett)"]
passskip = False
myname = ""

lbgs = IMAGES.lbgs

while True:
    pygame.mouse.set_visible(True)
    pygame.event.get()
    soundbox.PlaySong("Menu", -1)
    if not passskip:
        Choice = Main_Menu.operate()
        lev = 1
        Steps = 0
        TotalSteps = 0
        nohigh = False

    song = ((lev-1)/4)%len(Playlist)
    if Choice == 0:
        soundbox.StopMusic()
        In = True
        myname = ""

        while In:
            try:
                x, y = get_coords(os.path.join("levels","level"+str(lev)+".map"))
            except:
                if not passskip:
                    soundbox.FadeoutMusic(800)
                    time.sleep(1)
                    if not nohigh:
                        HighScores(screen, TotalSteps, None)
                else:
                    passskip = False
                break
            passskip = False            
            NewLevel = Level(screen, lbgs[(lev-1)%len(lbgs)], x, y)
            soundbox.PlaySong(Playlist[song%len(Playlist)], -1)
            result, ads = NewLevel.start(make_level_from_file(os.path.join("levels","level"+str(lev)+".map")),Steps, lev,\
                                         Playnames[song%len(Playlist)], TotalSteps, nohigh)
            Steps += ads
            if result == "Restart":
                continue
            if not result:
                soundbox.FadeoutMusic(800)
                time.sleep(1)
                break
            time.sleep(0.2)
            soundbox.PlaySound("Applause")
            dr = screen.blit(Congrats, (512-Congrats_Rect[2]/2, 384-Congrats_Rect[3]/2))
            pygame.display.update(dr)
            if not lev%4:
                song += 1
                soundbox.FadeoutMusic(1500)
                time.sleep(.6)
            time.sleep(2)

            if not lev%10:
                if not nohigh:
                    TotalSteps += Steps
                    soundbox.FadeoutMusic(800)
                    time.sleep(1)
                    HighScores(screen, Steps, lev/10)
                Steps = 0
            lev += 1
    elif Choice == 1:
        level = Main_Menu.level_entry()
        if level:
            lev = level
            Steps = 0
            Choice = 0
            passskip = True
            nohigh = True
    elif Choice == 2:
        level, steps, TotalSteps = Main_Menu.password_entry()
        if level:
            soundbox.PlaySound("Choose")
            lev = level
            Steps = abs(steps)
            Choice = 0
            passskip = True
    elif Choice == 3:
        HighScores(screen, None, 1)
    elif Choice == 4:
        Main_Menu.display_help()
    elif Choice == 5:
        for x in range(12): screen.blit(IMAGES.DSE, (0,0))
        dr = screen.blit(IMAGES.bye, (512-IMAGES.byerect[2]/2, 384-IMAGES.byerect[3]/2))
        pygame.display.flip()
        soundbox.FadeoutMusic(1500)
        time.sleep(1.5)
        pygame.mouse.set_visible(True)
        sys.exit(0)
