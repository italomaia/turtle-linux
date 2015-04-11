from world import *
from player import Player
from options import *
import pygame, os, time, random, datetime, sys,pickle,gzip,copy

class Game(object):
    def __init__(self):
        # init pygame
        pygame.mixer.init(44100, -16, 2, 512)
        pygame.display.init()
        pygame.font.init()
        
        pygame.mixer.set_reserved(0)
        pygame.mixer.set_reserved(1)
        
        # create screen
        size = (640, 480)
        self.screen = pygame.display.set_mode(size)
        self.main_screen=pygame.Surface((384,384))
        self.gui_screen=pygame.Surface((232,384))
        self.message_screen=pygame.Surface((384,72))
        self.key_screen=pygame.Surface((232,72))
        
        self.message_scroller=MessageScroller()
        pygame.display.set_caption("Curse of the Keys - A C64-Remake")
        
        # create gui
        self.gui=gui(self)
        
        # flags
        self.rumour=False
        self.enc=False
        self.loot=False
        self.all_keys=False
        self.abort=False
        
        self.clock = pygame.time.Clock()

        self.music=pygame.mixer.music
        
        self.music.load(os.path.join('..', 'sounds', 'roleplay.xm'))
        self.music.play(-1)
        # load sounds and graphics
        self.preload()
        
        # setting up time
        month=random.randrange(1, 13)
        
        self.flags={'fog_time':0,
                    'winter_time':0,
                    'time':datetime.date(1233, month, 1),
                    'music_playing':1}
        

        #self.start_fighting_music()
        
        pln, diff, title=self.ask_player()
        
        if diff:
            x=random.randrange(0, 2)
            y=0
            self.world=World([[m1, m4, m7], [m2, m5, m8], [m3, m6, m9]], FM, self.map_tiles, x, y)
            self.player=Player(pln, self.world.get(x, y), self, title)
            self.playerpower=6-int(diff)
            self.flags['pw']=self.playerpower
        else:
            FILE=gzip.open(os.path.join('..',pln+'cs'), 'r', 2)
            self.player,self.world,self.flags=pickle.load(FILE)
            self.playerpower=self.flags['pw']
            FILE.close()
            self.player.re_init(self)
            for row in self.world.data:
                for map in row:
                    map.update(False,self.map_tiles)
            self.world.finalmap.update(False,self.map_tiles)
        
        self.update_key_screen()
        self.state=STATE_RUNNING
        
    def update_key_screen(self):
        if self.player.key3:
            self.key_screen.blit(self.smallkey, (160, 10))
        
        if self.player.key2:
            self.key_screen.blit(self.smallkey, (85, 10))
        
        if self.player.key1:
            self.key_screen.blit(self.smallkey, (10, 10))
        self.screen.blit(self.key_screen,(8+8+384,8+8+384))  
    def save(self):
        p=copy.copy(self.player)
        FILE=gzip.open(os.path.join('..',p.name+'cs'), 'w')
        p.game=None
        pickle.dump((p,self.world,self.flags), FILE, 2)
        FILE.close()
        #print "saved"
        #print os.path.join('..',p.name+'cs')
    def new_game(self, n):
        back=pygame.image.load(os.path.join('..', 'backs', 'title.png'))
        t=self.draw_line
        self.screen.blit(back,(0,0))
        
        t('How strong do you think you are?', 50, 130)
        t('1 - I am still a child', 55, 150)
        t('2 - Please don\'t hurt me', 55, 165)
        t('3 - I am a real man', 55, 180)
        t('4 - I like the pain', 55, 195)
        t('5 - I am a god', 55, 210)
        pygame.display.flip()
        diff = 0
        while not diff:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.display.toggle_fullscreen()
                    
                    if e.unicode in '12345':
                        diff = e.unicode
                    
                
            
        self.screen.blit(back,(0,0))

        #Titles=['Warrior', 'Priest', 'Cleric', 'Lord', 'Nobleman']
        t('So, what is your profession?', 50, 130)
        t('p - I am a PRIEST of the elder gods', 55, 150)
        t('w - I am the bravest WARRIOR', 55, 165)
        t('c - I serve the gods as a CLERIC', 55, 180)
        t('l - I am LORD %s' % (n), 55, 195)
        t('n - I am a NOBLEMAN', 55, 210)
        pygame.display.flip()
        title = 0
        while not title:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.display.toggle_fullscreen()
                    
                    if e.unicode in 'pwcln':
                        title = e.unicode
                    
                
            
        
        if title == 'p':
            title = 'Priest'
        
        if title == 'w':
            title = 'Warrior'
        
        if title == 'c':
            title = 'Cleric'
        
        if title == 'l':
            title = 'Lord'
        
        if title == 'n':
            title = 'Nobleman'
        
        return title, diff

    def preload(self):
        
        back=pygame.image.load(os.path.join('..', 'backs', 'title.png'))
        
        self.preload_print_message(back, "preloading sounds....")
        
        self.preload_sound()
                
        self.preload_print_message(back, "preloading images....")
        
        self.preload_images()

       
        
    def preload_images(self):
        self.map_tiles = Resource(os.path.join('..', 'tiles', 'tile.bmp'), TILESIZE)
        self.foe_tiles = Resource(os.path.join('..', 'tiles', 'foes.png'), TILESIZE)
        self.fogs=[]
        self.fog_image = pygame.image.load(os.path.join('..', 'backs', 'fog.png'))
        self.player_images = {}
        for title in Titles:
            self.player_images[title] = pygame.image.load(os.path.join('..', 'tiles', title + '.png'))
        self.borders = {'vert': pygame.image.load(os.path.join('..', 'backs', 'verti.png')),
                        'hori': pygame.image.load(os.path.join('..', 'backs', 'hori.png')),
                         'right': pygame.image.load(os.path.join('..', 'backs', 'right.png')),
                          'left': pygame.image.load(os.path.join('..', 'backs', 'left.png')),
                           'up': pygame.image.load(os.path.join('..', 'backs', 'up.png')),
                            'down': pygame.image.load(os.path.join('..', 'backs', 'down.png')),
                             'frame': pygame.image.load(os.path.join('..', 'backs', 'big_frame.png'))}
        self.backgrounds = {FORTRESS: pygame.image.load(os.path.join('..', 'backs', 'fortress.png')), SETTLE: pygame.image.load(os.path.join('..', 'backs', 'settlement.png')), VILLAGE: pygame.image.load(os.path.join('..', 'backs', 'village.png')), CAPITAL: pygame.image.load(os.path.join('..', 'backs', 'capital.png')), OUTPOST: pygame.image.load(os.path.join('..', 'backs', 'outpost.png')), BUILD_OUTPOST: pygame.image.load(os.path.join('..', 'backs', 'outpost.png')), RUIN: pygame.image.load(os.path.join('..', 'backs', 'ruin.png')), FINAL: pygame.image.load(os.path.join('..', 'backs', 'final.png')), WIN: pygame.image.load(os.path.join('..', 'backs', 'win.png')), LOSE: pygame.image.load(os.path.join('..', 'backs', 'lost.png'))}
        self.key_image = pygame.image.load(os.path.join('..', 'backs', 'key.png'))
        self.gui_back = pygame.image.load(os.path.join('..', 'backs', 'key_tr2.png'))
        self.smallkey=pygame.image.load(os.path.join('..', 'backs', 'small_key.png'))
        self.smallkeygrey=pygame.image.load(os.path.join('..', 'backs', 'small_key_grey.png'))
        self.key_screen.blit(self.smallkeygrey,(10,10))
        self.key_screen.blit(self.smallkeygrey,(85,10))
        self.key_screen.blit(self.smallkeygrey,(160,10))
        
    def preload_sound(self):
        self.sounds = {'hit1': pygame.mixer.Sound(os.path.join('..', 'sounds', 'hit1.ogg')), 'hit2': pygame.mixer.Sound(os.path.join('..', 'sounds', 'hit2.ogg')), 'hit3': pygame.mixer.Sound(os.path.join('..', 'sounds', 'hit3.ogg')), 'hit4': pygame.mixer.Sound(os.path.join('..', 'sounds', 'hit4.ogg')), 'win': pygame.mixer.Sound(os.path.join('..', 'sounds', 'win.ogg')), 'loss': pygame.mixer.Sound(os.path.join('..', 'sounds', 'lost.ogg')), 'key': pygame.mixer.Sound(os.path.join('..', 'sounds', 'found_a_key.ogg')), 'encounter': pygame.mixer.Sound(os.path.join('..', 'sounds', 'encounter.ogg')), 'wizard': pygame.mixer.Sound(os.path.join('..', 'sounds', 'wizard.ogg')), 'fighting': pygame.mixer.Sound(os.path.join('..', 'sounds', 'fight_music.ogg'))}
        self.tracks = {STATE_RUNNING: os.path.join('..', 'sounds', 'roleplay.xm')}


    def preload_print_message(self, back, text):
        self.screen.blit(back, (0, 0))
        self.draw_line(text, 16, 450)
        pygame.display.flip()


    def generate_new_prices(self):
        prices = {'Warrior': random.randrange(8, 13), 'Rations': random.randrange(1, 4), 'Scout': random.randrange(48, 64), 'Carrier': random.randrange(25, 45), 'Healer': random.randrange(50, 61), 'Wizard': random.randrange(92, 100), 'Navigator': random.randrange(45, 65), 'Ship': random.randrange(55, 75)}
        return prices

    def enter_final(self, prices):
        self.state = STATE_FINAL
        caption = "You enter the castle"
        text = ["As you enter the castle of", "the evil wizard, a dark voice", "speaks to you:", "", "Haha, so here you are!", "Another soul that will perish!", "", "You see a huge iron gate open,", "as a horde of dragon guardians", "attack you!!", "", "SPACE - Go on"]
        self.enc = FINAL
        return text, caption, 0, 0


    def enter_capital(self, prices):
        self.state = STATE_CAPITAL
        r = self.player.rations
        w = self.player.warriors
        g = self.player.gold
        if r > 20:
            rt = "You seem to have enough rations."
            rg = 0
        else:
            rg = random.randrange(5, 15)
            rt = "Take these %i rations." % (rg)
            self.player.rations += rg
        if w > 10:
            wt = "You seem to have enough men for"
        else:
            wg = random.randrange(6, 11)
            wt = "These %i brave men will join" % (wg)
            self.player.warriors += wg
        if g > 10:
            gt = "You seem to have gold."
        else:
            gg = random.randrange(10, 20)
            gt = "These %i goldpieces will help you." % (gg)
            self.player.gold += gg
        caption = "You enter the capital city"
        text = ["As you enter, the major", "welcomes you:", "", wt, "your quest.", "", rt, '', gt, "", "SPACE - Leave the capital"]
        return text, caption, 0, 0


    def enter_settlement(self, prices):
        prices['Warrior'] += 2
        prices['Rations'] += 2
        self.state = STATE_BUYING_SETTLEMENT
        text = ["r - Buy rations      : %i g" % (prices['Rations']), "w - Hire new warriors: %i g" % (prices['Warrior']), "s - Hire a scout     : %i g" % (prices['Scout']), "c - Hire a carrier   : %i g" % (prices['Carrier']), "h - Hire a healer    : %i g" % (prices['Healer']), "z - Hire a wizard    : %i g" % (prices['Wizard']), "n - Hire a navigator : %i g" % (prices['Navigator']), "i - Buy a ship       : %i g" % (prices['Ship']), '', "m - Ask for rumour", '', "SPACE - Leave the settlement"]
        caption = "You enter a nomad settlement"
        return text, caption, 0, 0


    def enter_outpost(self, prices):
        self.state = STATE_OUTPOST
        caption = "You enterd your outpost"
        depot, war = self.player.map.outposts[self.player.pos]
        text = ["g - Hide 5 gold",
                "t - Take 5 gold (%i stored)" % (depot),
                "s - Leave 5 guards (max 5)",
                "w - Take 5 guards (%i are here)" % (war),
                "",
                "F1 - Save game: 10g",
                "",
                 "SPACE - Move on"]
        return text, caption, depot, war


    def enter_build_outpost(self, prices):
        self.state = STATE_BUILDING_OUTPOST
        caption = "Building an outpost"
        text = ["b - Build an outpost: 50 g", "", "SPACE - Move on"]
        return text, caption, 0, 0


    def enter_village(self, prices):
        self.state = STATE_BUYING_CITY
        text = ["r - Buy rations      : %i g" % (prices['Rations']), "w - Hire new warriors: %i g" % (prices['Warrior']), "m - Ask for rumour", '', "SPACE - Leave the village"]
        caption = "You enter a village"
        return text, caption, 0, 0


    def enter_fortress(self, prices):
        self.state = STATE_FORTRESS
        text = []
        r = random.randrange(0, 100)
        caption = "You enter an old fortress"
        if r < 10:
            w = random.randrange(1, 5)
            text = ['As you investigate the old fortress,', 'you come across a group of former', 'warriors that protect the castle.', '', 'After a long night of mead and', 'storytelling, they decide to join', 'you on your quest!', '', '%i new brave men will follow you!' % (w), '', '', 'SPACE - Leave the fortress']
            self.play_sound('win')
            self.player.warriors += w
        elif r >= 10 and r < 20 and self.player.warriors > 0:
            self.enc = Foes[0]
            text = ['As you investigate the old fortress,', 'you notice that it is not abandoned.', '', 'Your men hear strange sounds in the', 'night and find scraps all around.', '', 'As you were going to leave, you are', 'suprised by a bunch of foes which', 'were lurking at a dark corner of', 'the fortress!', '', '', 'SPACE - Go on']
        elif r >= 20 and r < 30:
            self.loot = True
            text = ['As you investigate the old fortress,', 'you notice that it is abandoned.', '', 'You decide to search through the', 'entire fortress', '', 'As you were going to leave, you', 'find the secret treasure chamber!', '', '', 'SPACE - Take the treasure']
        elif r >= 30 and r < 40 and self.player.warriors > 0:
            w = random.randrange(2, 5)
            text = ['As you investigate the old fortress,', 'you notice that it is abandoned.', '', 'You decide to search through the', 'entire fortress', '', 'As you were going to leave, one', 'man triggers a deadly trap and', '%i warriors are impaled to death!' % (w), '', '', 'SPACE - Go on']
            self.play_sound('loss')
            self.player.warriors -= w
        else:
            text = ['Nothing happens', '', 'SPACE - Leave the fortress']
        return text, caption, 0, 0


    def enter_ruin(self, prices):
        self.state = STATE_RUIN
        text = []
        r = random.randrange(0, 100)
        caption = "You search an abandoned ruin"
        if r < 10:
            self.enc = Foes[4]
            text = ['Slowly you enter the old ruin.', 'The stench of death is in the air.', 'Rats are everywere.', '', 'After a long path that leads', 'beneath the surface, you face', 'an ancient dragon!', '', '', 'SPACE - Leave the fortress']
        elif r >= 30 and r < 40 and self.player.warriors > 0:
            w = random.randrange(2, 5)
            text = ['As you investigate the old ruin,', 'you notice that it is abandoned.', '', 'You decide to search through the', 'entire ruin', '', 'As you were going to leave, one', 'man triggers a deadly trap and', '%i warriors are impaled to death!' % (w), '', '', 'SPACE - Go on']
            self.play_sound('loss')
            self.player.warriors -= w
        else:
            text = ['Nothing happens', '', 'SPACE - Leave the ruin']
        return text, caption, 0, 0


    def player_loot_world(self):
        self.loot = False
        rations = random.randrange(2, 45)
        gold = random.randrange(15, 55)
        self.player.mes1 = random.choice(["You are lucky!", "The gods are with you!"])
        self.player.mes2 = random.choice(["You find:", "You looted", "You took"])
        self.player.mes3 = "%i rations and %i Gold!!" % (rations, gold)
        self.player.mes4 = ""
        self.play_sound('win')
        self.player.loot(gold, rations)

    def start_fighting_music(self):
        self.music.pause()
        pygame.mixer.Channel(0).play(self.sounds['fighting'])

    def end_fighting_music(self):
        
        pygame.mixer.Channel(0).fadeout(200)
        if self.flags['music_playing']:
            self.music.unpause()

    def player_changed_map(self):
        
        if self.flags['fog_time']:
            self.create_new_fog()
        
    def create_new_fog(self):
        self.fogs=[]
        for x in range(1, 3):
            self.fogs.append(Fog(self.fog_image, x * random.randrange(10, 30), x * random.randrange(10, 30)))
        
        for x in range(4, 8):
            self.fogs.append(Fog(self.fog_image, x * random.randrange(10, 30), x * random.randrange(30, 57)))
        
        return x

    def ask_player(self):
        
        back=pygame.image.load(os.path.join('..', 'backs', 'title.png'))
        s=self.screen
        t=self.draw_line
        n=''
        enter=0
        
        while not enter:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key== pygame.K_ESCAPE:
                        pygame.display.toggle_fullscreen()
                    if e.unicode in 'abcdefghijklmnopqrstuvwxyzQWERTZUIOPLKJHGFDSAYXCVBNM':
                        if n.__len__()<14:
                            n=n+e.unicode
                    if e.key==pygame.K_BACKSPACE:
                        n=n[:-1]
                    if e.key==pygame.K_RETURN and n:
                        enter=1
            self.screen.fill((0, 0, 0))
            s.blit(back, (0, 0))
            
            t('Adventurer, what is your name?', 50, 130)
            t(n, 50, 150)
            pygame.display.flip()
        
        #check for saved game:
        if os.path.exists(os.path.join('..',(n+'cs'))):
            return n,None,None
        else:    
            title , diff = self.new_game(n)
        return n, diff, title
    
    def draw_line(self, text, x, y):    
        f=self.gui.Font_text
        s=self.screen
        s.blit(f.render(text, 1, BLACK), (x+1, y+1))
        s.blit(f.render(text, 1, WHITE), (x, y))
    def switch_screens(self, old_screen, new_screen, mode=0):
        h=384
        w=384
        
        if mode==0:
            #tile by tile
            tilesize=16
            tile = pygame.Surface((tilesize, tilesize), depth=new_screen)
            
            for y in range(0, h/tilesize):
                for x in range(0, w/tilesize):
                    chop_rect=(x*tilesize, y*tilesize, tilesize, tilesize)
                    tile.blit(new_screen, (0, 0), chop_rect)
                    self.main_screen.blit(tile, (x*tilesize, y*tilesize))
                    self.draw_world(True,True,True)
        
        elif mode==1:
            #rows to side
            rowc=12
            rows=[]
            steps=h/rowc
            y=0
            for row in range(0, rowc):
                r=pygame.Surface((w, steps), depth=new_screen)
                rows.append(r)
                chop_rect=(0, y, w, steps);r.blit(old_screen, (0, 0), chop_rect);y+=steps
            
            for x in range(0, 80):
                self.main_screen.blit(new_screen, (0,0))
                c=0
                for row in rows:
                    if c%2:
                        ax=x
                    else:
                        ax=-x
                    self.main_screen.blit(row, (ax*5, steps*c))
                    c+=1
                self.draw_world(True,True,True)
        
        
        elif mode==2:
            #zoom in
            size=0
            while size<384:
                tile=pygame.transform.scale(new_screen, (size, size))
                size+=2
                if size==384:
                    tile=new_screen
                self.main_screen.blit(tile,(192-size/2, 192-size/2))
                self.draw_world(True,True,True)
        
        elif mode==3:
            #zoom out
            size=384
            while size>=0:
                tile=pygame.transform.scale(old_screen, (size, size))
                size-=2
                self.main_screen.blit(new_screen, (0,0))
                self.main_screen.blit(tile, (192-size/2, 192-+size/2))
                self.draw_world(True,True,True)
                
        pygame.event.clear()
    def draw_fight(self, background_sprite, number_of_warriors, number_of_foes, foe_name, player_sprite, player_sprite_x, foe_sprite, foe_sprite_x):
        #elf.draw_text(text, caption, background_sprite, BLACK,True,True,47,75)
        self.main_screen.fill(BLACK)
        self.main_screen.blit(background_sprite, (47, 75))
        self.main_screen.blit(player_sprite, (player_sprite_x, 220))
        self.main_screen.blit(foe_sprite, (foe_sprite_x, 220))
        self.main_screen.blit(self.gui.Font_text.render("Warriors: %i" % (number_of_warriors), 1, WHITE), (80, 300))
        self.main_screen.blit(self.gui.Font_text.render("%s: %i" % (foe_name, number_of_foes), 1, WHITE), (220, 300))
        self.draw_world(True, False, True)
        
    def set_music(self, state):
        pygame.mixer.music.load(self.tracks[state])
        if self.flags['music_playing']:
            self.music.play(-1)
            

        
    def found_a_key(self):
        tmpscreen=self.main_screen
        
        if self.player.key2:
            self.player.key3=1
            
            self.all_keys=True
        elif self.player.key1:
            self.player.key2=1
            
        else:
            self.player.key1=1
            
        
        self.update_key_screen()
        self.screen.blit(self.key_screen,(8+8+384,8+8+384))
        
        self.player.map.key=False
        
        back_image=self.key_image
        self.screen.blit(back_image, (0, 0))
        self.screen.blit(self.gui.Font_italic_big.render("You found a key!!!", 1, BLACK), (51, 301))
        self.screen.blit(self.gui.Font_italic_big.render("You found a key!!!", 1, WHITE), (50, 300))
        self.gui.draw(self.player)
        self.draw_border(True)
        pygame.display.flip()
        pygame.mixer.music.pause()
        l=self.play_sound('key')
        time.sleep(l)
        
        if self.flags['music_playing']:
            pygame.mixer.music.play(-1)
        
        self.player.clear_mes()
        self.player.mes1="PRESS ANY KEY"
        self.gui.draw(self.player)
        self.draw_border(True)
        pygame.display.flip()
        
        self.wait_for_space()
        self.player.clear_mes()
        
        self.screen.blit(tmpscreen, (OFFSET, OFFSET))
    
    def draw_text(self, text, caption, back, preview=False):
        
        if preview:
            s=pygame.Surface((384, 384))
        
        else:
            s=self.main_screen
        
        
        s.blit(back, (47, 75))
        
        s.blit(self.gui.Font_Caption.render(caption, 1, BLACK), (51, 51))
        s.blit(self.gui.Font_Caption.render(caption, 1, WHITE), (50, 50))
        
        x = 0
        for line in text:
            s.blit(self.gui.Font_text.render(line, 1, BLACK), (51, 86 + x))
            s.blit(self.gui.Font_text.render(line, 1, WHITE), (50, 85 + x))
            x += 13
        
        return s
        
        
    def play_sound(self, sound):
        channel = self.sounds[sound].play()
        if channel is not None:
            channel.set_volume(1.0, 1.0)
        return self.sounds[sound].get_length()
    
    def fight(self, final=False):
        c=pygame.mixer.Channel(1)
        self.start_fighting_music()

        x, y=self.player.pos
        background_image_name=self.player.map.get(self.player.map.data[x][y])['image']
        
        background_sprite=pygame.image.load(os.path.join('..', 'backs', background_image_name+'.png'))       
        
        fallen_warriors=0

        self.state=STATE_FIGHTING
           
        number_of_warriors=self.player.warriors
        number_of_foes=self.player.foe['count']
        org_number_of_foes=number_of_foes
        foe_name=self.player.foe['s_Name']
        foe_strength=self.player.foe['Str']
        
        player_sprite=pygame.transform.scale2x(self.player.image)
        #player_sprite=pygame.transform.scale(self.player.image, (TILESIZE*2, TILESIZE*2))
        player_sprite_x_start=120
        player_sprite_x_stop=150
        player_sprite_x=player_sprite_x_start
        ATTACK_STATE=0
        foe_sprite=pygame.transform.scale2x(self.foe_tiles.get(self.player.foe['TileNo']))
        #foe_sprite=pygame.transform.scale(self.foe_tiles.get(self.player.foe['TileNo']), (TILESIZE*2, TILESIZE*2))
        foe_sprite_x_start=220
        foe_sprite_x_stop=190
        foe_sprite_x=foe_sprite_x_start

        olds=self.main_screen.copy()

        ns=pygame.Surface((384, 384))
        ns.blit(background_sprite, (47, 75))
        ns.blit(player_sprite, (player_sprite_x, 220))
        ns.blit(foe_sprite, (foe_sprite_x, 220))
        ns.blit(self.gui.Font_text.render("Warriors: %i" % (number_of_warriors), 1, WHITE), (80, 300))
        ns.blit(self.gui.Font_text.render("%s: %i" % (foe_name, number_of_foes), 1, WHITE), (220, 300))
        
        self.switch_screens(olds, ns, 1)
   
        while self.state == STATE_FIGHTING:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_ESCAPE:
                        pygame.display.toggle_fullscreen()
                        
            if number_of_warriors and ATTACK_STATE==AT_NEW_ROUND:
                ATTACK_STATE=AT_PLAYER_ATTACK
                c.play(self.sounds[random.choice(['hit1', 'hit2', 'hit3', 'hit4'])])
                
            
            if number_of_warriors==0:
                ATTACK_STATE=AT_PLAYER_DEFEAT
                
            if ATTACK_STATE==AT_PLAYER_ATTACK:
                if player_sprite_x<player_sprite_x_stop:
                    player_sprite_x+=ATTACK_SPEED
                else:
                    player_sprite_x-=ATTACK_SPEED
                    ATTACK_STATE=AT_PLAYER_GO_BACK
            elif ATTACK_STATE==AT_PLAYER_GO_BACK:
                if player_sprite_x>player_sprite_x_start:
                    player_sprite_x-=ATTACK_SPEED
                else:
                    ATTACK_STATE=AT_PLAYER_FINISHED
                    number_of_warriors=self.player.warriors
                    number_of_foes=self.player.foe['count']
                    
                    # playerpower
                    PlayerPower=number_of_warriors/5+self.playerpower
                    
                    # foe defense
                    FoeDefense=(number_of_foes+5)/(10-foe_strength)+foe_strength
                    
                    #wizard
                    if self.player.wizard:
                        if random.randrange(100)>90:
                            self.play_sound('wizard')
                            damage=random.randrange(1, 7)
                            self.player.foe['count']-=damage
                            if self.player.foe['count']<0:
                                self.player.foe['count']=0
                            number_of_foes=self.player.foe['count']
                            time.sleep(2)

                    #hit?
                    hit=random.randrange(0, 11)
                    if VERBOSE:
                        print 'Player: rolls %i; Power %i Foe-Defense %i'%(hit, PlayerPower, FoeDefense)
                    if hit>0 and (hit+PlayerPower>FoeDefense or hit>8):
                        r=random.randrange(-1, 3)
                        damage=PlayerPower-FoeDefense+r
                        if damage<1:
                            damage=1
                        if damage>3:
                            damage=3
                        self.player.foe['count']-=damage
                        if self.player.foe['count']<0:
                            self.player.foe['count']=0
                        number_of_foes=self.player.foe['count']
                   
            if number_of_foes>0 and ATTACK_STATE==AT_PLAYER_FINISHED:
                ATTACK_STATE=AT_FOE_ATTACK
                c.play(self.sounds[random.choice(['hit1', 'hit2', 'hit3', 'hit4'])])
                
            if number_of_foes == 0:
                ATTACK_STATE=AT_PLAYER_VICTORY
                  
            if ATTACK_STATE==AT_FOE_ATTACK:
                if foe_sprite_x>foe_sprite_x_stop:
                    foe_sprite_x-=ATTACK_SPEED
                else:
                    foe_sprite_x+=ATTACK_SPEED
                    ATTACK_STATE=AT_FOE_GO_BACK
            elif ATTACK_STATE==AT_FOE_GO_BACK:
                if foe_sprite_x<foe_sprite_x_start:
                    foe_sprite_x+=ATTACK_SPEED
                else:
                    ATTACK_STATE=AT_NEW_ROUND
                    number_of_warriors=self.player.warriors
                    number_of_foes=self.player.foe['count']
                    
                    # playerpower
                    FoePower=number_of_foes/5+foe_strength
                    
                    # foe defense
                    PlayerDefense=(number_of_warriors+5)/(10-self.playerpower)+self.playerpower
                    
                    
                    
                    #hit?
                    hit=random.randrange(0, 11)
                    #print "h:%i fp:%i pd%i"%(hit,FoePower,PlayerDefense)
                    #print 'Foe:%i - %i'%(hit+FoePower,PlayerDefense)
                    if VERBOSE:
                        print 'Foe: rolls %i; power %i playerdefense:%i'%(hit, FoePower, PlayerDefense)
                    if hit>0 and (hit+FoePower>PlayerDefense or hit>8):
                        #print "hit"
                        r=random.randrange(-1, 3)
                        damage=FoePower-PlayerDefense+r
                        if damage<1:
                            damage=1
                        if damage>3:
                            damage=3
                        self.player.warriors-=damage
                        fallen_warriors+=damage
                        if self.player.warriors<0:
                            self.player.warriors=0
                        number_of_warriors=self.player.warriors
            
                
                
            if ATTACK_STATE==AT_PLAYER_VICTORY:
                if final:
                    self.win()
                
                self.play_sound('win')
                
                rations=random.randrange(2, (fallen_warriors+2)*2)
                gold=random.randrange(org_number_of_foes, org_number_of_foes*3+20)
                self.player.clear_mes()       
                self.player.victory+=1
                self.player.mes1=random.choice(["You won!", "Victory is yours!", "You defeated the enemy!"])
                self.player.mes2=random.choice(["You find:", "You looted", "You took"])
                self.player.mes3="%i rations and %i Gold!!"%(rations, gold)
                self.player.mes4="PRESS ANY KEY"
                
                #self.player.clear_mes()
                if self.player.miraclehealer and random.randrange(100)>20 and fallen_warriors>1:
                    self.draw_fight(background_sprite, number_of_warriors, number_of_foes, foe_name, player_sprite, player_sprite_x, foe_sprite, foe_sprite_x)
                    self.wait_for_space()
                    heal=random.randrange(1, fallen_warriors)
                    self.play_sound('win')
                    self.player.mes2="The miracle healer"
                    self.player.mes3="revived %i warriors!"%(heal)
                    self.player.mes4="PRESS ANY KEY"
                    self.player.warriors+=heal
                    self.draw_fight(background_sprite, number_of_warriors, number_of_foes, foe_name, player_sprite, player_sprite_x, foe_sprite, foe_sprite_x)
                
                self.player.loot(gold, rations)
                self.draw_fight(background_sprite, number_of_warriors, number_of_foes, foe_name, player_sprite, player_sprite_x, foe_sprite, foe_sprite_x)
                pygame.display.flip()   
                self.wait_for_space()
                self.player.clear_mes()
                self.state=STATE_RUNNING
                
                olds2=self.main_screen.copy()
                self.switch_screens(olds2, olds, 1)
                self.end_fighting_music()
                self.player.foe=None
                break
            
            if ATTACK_STATE==AT_PLAYER_DEFEAT:
                if final:
                    self.loss()
                self.play_sound('loss')
                self.state=STATE_RUNNING         
                self.player.clear_mes()       
                self.player.defeat+=1
                if self.player.carrier:
                    self.player.gold=self.player.gold/2
                    self.player.rations=self.player.rations/2
                else:
                    self.player.gold=0
                    self.player.rations=0
                
                old_screen=self.main_screen.copy()
                new_screen=olds
                self.switch_screens(old_screen, new_screen, 1)
                self.end_fighting_music()
                self.player.foe=None
                break
            
            self.clock.tick(50)
            self.draw_fight(background_sprite, number_of_warriors, number_of_foes, foe_name, player_sprite, player_sprite_x, foe_sprite, foe_sprite_x)

    def wait_for_space(self):
        OK=0
        while not OK:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type==pygame.KEYDOWN:
                    OK=1
        
    def run(self):
        
        while not self.abort:
            
            if self.all_keys:
                self.player.map=self.world.finalmap
                self.player.pos=(5, 8)
                self.all_keys=False
                
            if self.enc:
                if self.enc!=FINAL:
                    self.player.encounter(self.enc)
                    self.enc=False
                else:
                    g=Guardians
                    g['count']=random.randrange(g['Min'], g['Max']+1)
                    self.player.foe=g
                    self.fight(True)
                
            if self.loot:
                self.player_loot_world()
                
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key==pygame.K_ESCAPE:
                        pygame.display.toggle_fullscreen()
                    if self.state==STATE_RUNNING:
                        if e.key == pygame.K_DOWN:
                            self.player.move((0, 1))
                        if e.key == pygame.K_UP:
                            self.player.move((0, -1))
                        if e.key == pygame.K_RIGHT:
                            self.player.move((1, 0))
                        if e.key == pygame.K_LEFT:
                            self.player.move((-1, 0))
                        if e.key == pygame.K_SPACE:
                            self.player.enter()
                        if e.key == pygame.K_s:
                            if self.flags['music_playing']:
                                self.music.pause()
                                self.flags['music_playing']=0
                            else:
                                self.music.play(-1)
                                self.flags['music_playing']=1
                    elif self.state==STATE_ASK_FOR_EVADE:
                        if e.key == pygame.K_f:
                            self.fight()
                        if e.key == pygame.K_e:
                            if random.randrange(0, 100)>40:
                                self.player.clear_mes()
                                self.state=STATE_RUNNING
                            else:
                                if self.player.warriors<=5:
                                    self.player.mes1="You failed"
                                    self.player.mes2="to run away!"
                                    self.player.mes3=""
                                    self.player.mes4=""
                                    self.fight()
                                else:
                                    self.state=STATE_ASK_FOR_SAC
                                    self.player.mes1="You're surrounded!"
                                    self.player.mes2="Sacrifice 5 men"
                                    self.player.mes3="to escape?"
                                    self.player.mes4="(E)scape - (F)ight"
                                                                        
                    elif self.state==STATE_ASK_FOR_SAC:
                        if e.key == pygame.K_f:
                            self.fight()
                        if e.key ==pygame. K_e:
                            self.player.warriors-=5
                            self.state=STATE_RUNNING
                            self.player.mes1="5 brave men stopped"
                            self.player.mes2="them for you to flee."
                            self.player.mes3=""
                            self.player.mes4="You escaped"
        
            
            
            self.draw_world()

    def get_flavor_text(self,b):
        text=['']
        if b==0 and random.randrange(0,10)>5:
            # now message in queue
            text=random.choice(GENERIC_TEXT)
        elif b==0:
            px, py=self.player.pos
            if self.flags['winter_time']:
                text=self.player.map.get(self.player.map.data[px][py])['wintertext']
            else:
                text=self.player.map.get(self.player.map.data[px][py])['summertext']

        return text
    def draw_border(self, no_arrows=False):
        
        
        self.screen.blit(self.borders['frame'], (0, 0))
        
        self.screen.blit(self.borders['vert'], (OFFSET+12*TILESIZE, OFFSET))
        self.screen.blit(self.borders['hori'], (OFFSET, OFFSET+12*TILESIZE))
        
        if not no_arrows:
            if self.world.can_move_up(self.player.map):
                self.screen.blit(self.borders['up'], (OFFSET, 0))
            
            if self.world.can_move_down(self.player.map):
                self.screen.blit(self.borders['down'], (OFFSET, OFFSET+12*TILESIZE))
         
            if self.world.can_move_left(self.player.map):
                self.screen.blit(self.borders['left'], (0, OFFSET))    
           
            if self.world.can_move_right(self.player.map):
                self.screen.blit(self.borders['right'], (OFFSET+12*TILESIZE, OFFSET))
                
    def draw_world(self,no_map=False,no_gui=False,no_border=False):

        if not no_map and self.state in [STATE_RUNNING, STATE_ASK_FOR_EVADE, STATE_ASK_FOR_SAC]:
            
            self.message_scroller.action=\
            self.message_scroller.update\
            (self.get_flavor_text(self.message_scroller.action))
            self.message_screen=self.message_scroller.get_surface()
        
            if self.flags['winter_time']:
                image=self.player.map.winter_image
            else:
                image=self.player.map.image
            # draw map and player
            self.main_screen=image.copy()
            #self.screen.blit(image, (OFFSET, OFFSET))
            x, y=self.player.pos
            self.main_screen.blit(self.player.image, (x*TILESIZE, y*TILESIZE))
            for fog in self.fogs:
                fog.draw(self.screen)
        
        if not no_gui:
            self.gui.draw(self.player)
            self.screen.blit(self.gui_screen,(384+8+8,8))
        
        
        if not no_border:
            self.draw_border()

        
        self.screen.blit(self.message_screen,(8,8+384+8))
        
        self.screen.blit(self.main_screen,(8,8))
        
        pygame.display.flip()      

    def enter(self, loc):
       
        self.rumour=False

        background_sprite=self.backgrounds[loc]
              
        prices = self.generate_new_prices()
        
        enter_method = getattr(self, 'enter_'+loc)
        text , caption , depot, war=enter_method(prices)
        
        olds=self.main_screen.copy()
        ns=self.draw_text(text, caption, background_sprite, True)
        
        self.switch_screens(olds, ns, 2)
        
        self.draw_text(text, caption, background_sprite)
        while self.state != STATE_RUNNING:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key==pygame.K_ESCAPE:
                        pygame.display.toggle_fullscreen()
                    if e.unicode == ' ':
                        self.state=STATE_RUNNING
                    
                    if e.unicode == 'm' and self.state not in [STATE_CAPITAL, STATE_RUIN, STATE_FORTRESS]:
                        self.get_rumour()
                    
                    if self.state==STATE_OUTPOST:
                        if e.unicode == 'g':
                            #hide gold
                            if self.player.gold>=5:
                                self.player.gold-=5
                                self.player.map.outposts[self.player.pos]=(depot+5, war)
                        if e.unicode == 't':
                            #take gold
                            if depot>=5:
                                self.player.gold+=5
                                self.player.map.outposts[self.player.pos]=depot-5, war
                        if e.unicode == 's':
                            #leave w
                            if self.player.warriors>=5 and war==0:
                                self.player.warriors-=5
                                self.player.map.outposts[self.player.pos]=(depot, war+5)
                        if e.unicode == 'w':
                            #take w
                            if war==5:
                                self.player.warriors+=5
                                self.player.map.outposts[self.player.pos]=depot, 0
                        if e.key == pygame.K_F1:
                            if self.player.gold>=10:
                                self.player.gold-=10
                                self.save()
                        depot, war=self.player.map.outposts[self.player.pos]
                        text=["g - Hide 5 gold",
                          "t - Take 5 gold (%i stored)"%(depot),
                          "s - Leave 5 guards (max 5)",
                          "w - Take 5 guards (%i are here)"%(war),
                          "",
                          "F1 - Save game: 10g",
                          "",
                          "SPACE - Move on"]
                        
                    if e.unicode == 'b' and self.state==STATE_BUILDING_OUTPOST:
                        if self.player.gold>=50:
                            self.player.gold-=50
                            x, y=self.player.pos
                            self.player.map.data[x][y]='O'
                            self.state=STATE_RUNNING
                            self.player.map.update()
                            self.player.map.outposts[self.player.pos]=0, 0
                            
                    if e.unicode == 'r' and (self.state==STATE_BUYING_CITY or self.state==STATE_BUYING_SETTLEMENT): 
                        if self.player.gold>=prices['Rations']:
                            self.player.gold-=prices['Rations'];self.player.rations+=1
                    if e.unicode == 'w' and (self.state==STATE_BUYING_CITY or self.state==STATE_BUYING_SETTLEMENT):
                        if self.player.gold>=prices['Warrior']:
                            self.player.gold-=prices['Warrior'];self.player.warriors+=1    
                    if e.unicode == 's' and self.state==STATE_BUYING_SETTLEMENT: 
                        if self.player.gold>=prices['Scout'] and self.player.scout==0:
                            self.player.gold-=prices['Scout'];self.player.scout=1
                    if e.unicode == 'c' and self.state==STATE_BUYING_SETTLEMENT: 
                        if self.player.gold>=prices['Carrier'] and self.player.carrier==0:
                            self.player.gold-=prices['Carrier'];self.player.carrier=1
                    if e.unicode == 'h' and self.state==STATE_BUYING_SETTLEMENT: 
                        if self.player.gold>=prices['Healer'] and self.player.miraclehealer==0:
                            self.player.gold-=prices['Healer'];self.player.miraclehealer=1
                    if e.unicode == 'z' and self.state==STATE_BUYING_SETTLEMENT: 
                        if self.player.gold>=prices['Wizard'] and self.player.wizard==0:
                            self.player.gold-=prices['Wizard'];self.player.wizard=1        
                    if e.unicode == 'n' and self.state==STATE_BUYING_SETTLEMENT: 
                        if self.player.gold>=prices['Navigator'] and self.player.navigator==0:
                            self.player.gold-=prices['Navigator'];self.player.navigator=1
                    if e.unicode == 'i' and self.state==STATE_BUYING_SETTLEMENT: 
                        if self.player.gold>=prices['Ship'] and self.player.ship==0:
                            self.player.gold-=prices['Ship'];self.player.ship=1
                
                
                self.draw_world(True, False, True)
                
        ns=self.main_screen.copy()
        self.switch_screens(ns, olds, 3)   
        
    def time_taken(self, days):
        m=self.flags['time'].month
        self.flags['time']+=datetime.timedelta(days)
        if m!=self.flags['time'].month:
            self.player.time_to_eat()
            for outpost in self.player.map.outposts:
                g, w=self.player.map.outposts[outpost]
                if g>2:
                    g-=2
                self.player.map.outposts[outpost]=g, w
            
            if self.flags['time'].month in [9, 10, 11]:
                if not self.flags['fog_time']:
                    self.flags['fog_time']=1
                    self.create_new_fog()
            else:
                self.flags['fog_time']=0
                self.fogs=[]
                
            if self.flags['time'].month in [1, 2, 11, 12]:
                if self.flags['winter_time']==0:
                    self.message_scroller.update(['Oh, winter is here!','Thats no good...'])
                
                self.flags['winter_time']=1
            else:
                if self.flags['winter_time']==1:
                    self.message_scroller.update(['Ah, spring is back!','Finally......'])
                self.flags['winter_time']=0 
    
    def get_rumour(self):
        if not self.rumour:
            self.rumour=True
            r=random.choice(romours)
            self.player.mes1=r[0]
            self.player.mes2=r[1]
            self.player.mes3=r[2]
            self.player.mes4=r[3]
     
    def win(self):
        caption="You saved the kingdom of Kurzur!"
        text=["After a long and dangerous battle, you finally",
            "defeat the dragon guardians. The nameless wizard",
            "screams in anger:", "",
            "No, you fool, what have you done?",
            "How is this possible?",
            "",
            "as you strike him down with a fast blow.",
            "Now, Kurzur is save and the people of Kurzur",
            "celebrtae a new hero....", "",
            "YOU!!"]
            
        s=self.screen
        s.fill((BLACK))
        self.draw_text(text, caption, self.backgrounds[WIN])
        self.draw_border()
        pygame.display.flip()
        pygame.mixer.music.pause()
        l=self.play_sound('key')
        time.sleep(l)
        self.wait_for_space()
        sys.exit()
     
    def loss(self):
        caption="You failed !!"
        text=["After a long and dangerous battle, you sense",
            "the smell of death as you and your men",
            "where surrounded by the dragon guardians", "",
            "So, you fool, you think you can beat me?",
            "",
            "the nameless wizard says. He rises his arms",
            "as you fell your body crumbling under his",
            "magical powers. You fade away...", "",
            "Now, Kurzur belongs to me!", "",
            "are the last words you ever hear..."]
            
        s=self.screen
        s.fill((BLACK))
        self.draw_text(text, caption, self.backgrounds[LOSE])
        self.draw_border()
        pygame.display.flip()
        pygame.mixer.music.pause()
        l=self.play_sound('loss')
        time.sleep(l)
        self.wait_for_space()
        sys.exit()
        
class MessageScroller:
    def __init__(self):
        self.surface=pygame.Surface((384,480-384-8-8-8))
        self.text_objects=[]
        self.last_text=[]
        self.c=0
        font="DoradoHeadline.ttf"
        self.f=pygame.font.Font(os.path.join('..', 'font',font), 14)
        self.image=pygame.image.load(os.path.join('..','backs','scroller.png'))
        self.action=0
    def clear(self):
        self.surface.fill(BLACK)
        self.text_objects=[]
        self.last_text=[]
    
    def update(self,text):        

        if text!=[''] and text!=self.last_text:
            self.last_text=text
            #new text
            
            #delete all text thats not scrolling already
            c=0
            for text_o in self.text_objects:
                if text_o[1] > 80:
                    del self.text_objects[c:]
                c+=1
            # add new text.objects
            c=self.text_objects.__len__()
           
            for line in text:
                if line!='':
                    self.text_objects.append(self.create_text(line,c))
                    c+=1
        self.scroll()
        if self.text_objects.__len__()==0:
            return 0
        else:
            return 1
        
    def scroll(self):
        self.c+=1
        if self.c==5:
        #pump
            self.c=0
            #self.y-=1
        
            c=0
            for text_o in self.text_objects:
                ny=text_o[1]-1
                if not ny <-20:
                    self.surface.blit(text_o[0],(0,ny))
                    self.text_objects[c]=(text_o[0],ny,text_o[2])
                else:
                    self.text_objects.remove(text_o)
                c+=1
            self.surface.blit(self.image,(0,0))
            
    def create_text(self, text,count):   
        s=pygame.Surface((384,20))
        s.blit(self.f.render(text, 1, BLACK), (1, 1))
        s.blit(self.f.render(text, 1, WHITE), (0, 0))
        return (s,75+count*20,text)

    def get_surface(self):
        return self.surface
    
class gui:
    def __init__(self, game):
        self.screen=game.gui_screen
        self.game=game
        #self.Font_italic_big = pygame.font.Font(os.path.join('..', 'font', "SF Burlington Script SC.ttf"), 48, bold=True)
        #self.Font_italic_small = pygame.font.Font(os.path.join('..', 'font', "SF Burlington Script SC.ttf"), 28, bold=True)
        self.Font_italic_big = pygame.font.Font(os.path.join('..', 'font', "beneg___.ttf"), 52, bold=True)
        self.Font_italic_small = pygame.font.Font(os.path.join('..', 'font', "beneg___.ttf"), 28, bold=True)
        font="DoradoHeadline.ttf"
        self.Font_gui_small = pygame.font.Font(os.path.join('..', 'font',font), 12)
        self.Font_player_name = pygame.font.Font(os.path.join('..', 'font',font), 17)
        self.Font_text = pygame.font.Font(os.path.join('..', 'font',font), 14)
        self.Font_player_title = pygame.font.Font(os.path.join('..', 'font',font), 14)        
        self.Font_Caption = pygame.font.Font(os.path.join('..', 'font',font), 17, bold=True)
        
#        self.Font_gui_small = pygame.font.SysFont("courier", 12, bold=True)
#        self.Font_player_name = pygame.font.SysFont("courier", 16)
#        self.Font_text = pygame.font.SysFont("courier", 15, bold=True)
#        self.Font_player_title = pygame.font.SysFont("courier", 14)        
#        self.Font_Caption = pygame.font.SysFont("courier", 16, bold=True)
        self.cache={}

    def draw(self, player):
        self.screen.fill((BLACK))

        if not player.scout: scout = (self.Font_gui_small, "Scout", 1, GREY)
        else: scout = (self.Font_gui_small, "Scout", 1, WHITE)
        
        if not player.carrier:  carrier= (self.Font_gui_small, "Carrier", 1, GREY)
        else: carrier = (self.Font_gui_small, "Carrier", 1, WHITE)

        if not player.miraclehealer:  miraclehealer= (self.Font_gui_small, "Miracle Healer", 1, GREY)
        else:  miraclehealer= (self.Font_gui_small, "Miracle Healer", 1, WHITE)
        
        if not player.wizard:  wizard= (self.Font_gui_small, "Wizard", 1, GREY)
        else:  wizard= (self.Font_gui_small, "Wizard", 1, WHITE)
        
        if not player.navigator: navigator = (self.Font_gui_small, "+ Navigator", 1, GREY)
        else: navigator = (self.Font_gui_small, "+ Navigator", 1, WHITE)
        
        if not player.ship: ship = (self.Font_gui_small, "Ship", 1, GREY)
        else: ship = (self.Font_gui_small, "Ship", 1, WHITE)
        
        if not player.key1: key1 = (self.Font_gui_small, "Key No. 1", 1, GREY)
        else: key1 = (self.Font_gui_small, "Key No. 1", 1, WHITE)
        
        if not player.key2: key2 = (self.Font_gui_small, "Key No. 2", 1, GREY)
        else: key2 = (self.Font_gui_small, "Key No. 2", 1, WHITE)
        
        if not player.key3: key3 = (self.Font_gui_small, "Key No. 3", 1, GREY)
        else: key3 = (self.Font_gui_small, "Key No. 3", 1, WHITE)
        
        m=player.game.flags['time'].month
        d=player.game.flags['time'].day
        gamedate=(self.Font_gui_small, "%s, the %i"%(MONTH[m-1], d), 1, WHITE)
      
        x=10
        y=-10
        
        self.screen.blit(self.game.gui_back, (x, y+10))
        
        self.text((self.Font_italic_big, "Curse", 1, WHITE), (10, y+15))
        self.text((self.Font_italic_small, "of", 1, WHITE), (80, y+30))
        self.text((self.Font_italic_small, "the", 1, WHITE), (80, y+50))
        self.text((self.Font_italic_big, "Keys", 1, WHITE), (100, y+35))
  
        self.text((self.Font_player_title, player.title, 1, WHITE), (x, y+95))
        self.text((self.Font_player_name, player.name, 1, WHITE), (x, y+110))
      
        self.text((self.Font_gui_small, "Gold: ", 1, WHITE), (x, y+140))
        self.text((self.Font_gui_small, str(player.gold), 1, WHITE), (x+80, y+140))
        
        self.text((self.Font_gui_small, "Rations: ", 1, WHITE), (x, y+150))
        self.text((self.Font_gui_small, str(player.rations), 1, WHITE), (x+80, y+150))
        
        self.text((self.Font_gui_small, "Warriors: ", 1, WHITE), (x, y+160))
        self.text((self.Font_gui_small, str(player.warriors), 1, WHITE), (x+80, y+160))
        
        self.text((self.Font_gui_small, "Victories: ", 1, WHITE), (x, y+180))
        self.text((self.Font_gui_small, str(player.victory), 1, WHITE), (x+80, y+180))
        
        self.text((self.Font_gui_small, "Defeats: ", 1, WHITE), (x, y+190))
        self.text((self.Font_gui_small, str(player.defeat), 1, WHITE), (x+80, y+190))
        
        self.text((self.Font_gui_small, "Your followers:", 1, WHITE), (x, y+210))
        self.text(scout, (x+5, y+220))
        self.text(carrier, (x+5,y+ 230))
        self.text(miraclehealer, (x+5, y+240))
        self.text(wizard, (x+5, y+250))
        self.text(ship, (x+5, y+260))
        self.text(navigator, (x+40, y+260))
        
        self.text((self.Font_gui_small, "Your keys:", 1, WHITE), (x, y+280))
        self.text(key1, (x+5, y+290))
        self.text(key2, (x+5, y+300))
        self.text(key3, (x+5, y+310))
        
        self.text(gamedate, (x, y+325))
        
        if not player.mes1:
            px, py=player.pos
            self.text((self.Font_gui_small, "You roam ", 1, WHITE), (x, y+350))
            self.text((self.Font_gui_small, player.map.get(player.map.data[px][py])['Name'], 1, WHITE), (x+75, y+350))
        else:
            self.text((self.Font_gui_small, player.mes1, 1, WHITE), (x, y+340))
            self.text((self.Font_gui_small, player.mes2, 1, WHITE), (x, y+350))
            self.text((self.Font_gui_small, player.mes3, 1, WHITE), (x, y+360))
            self.text((self.Font_gui_small, player.mes4, 1, WHITE), (x, y+370))
    
    def text(self, font, pos):
        x, y=pos
        if not self.cache.has_key((font[1],font[3])) or NO_FONT_CACHE:
            pyfont=font[0]
            text=pyfont.render(font[1], font[2], font[3])
            text_s=pyfont.render(font[1], font[2], BLACK)
            x, y=pos
            self.screen.blit(text_s, (x+1, y+1))
            self.screen.blit(text, (pos))
            self.cache[font[1]]=(text, text_s)
            
        else:
            data=self.cache[(font[1],font[3])]
            self.screen.blit(data[1], (x+1, y+1))
            self.screen.blit(data[0], (x, y))
            

