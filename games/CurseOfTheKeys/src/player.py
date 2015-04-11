from world import *

class Player:        
    def __init__(self, name, map, game,title):
        #pygame.sprite.Sprite.__init__(self) 
        self.name=name
        self.title=title
        self.image=game.player_images[title]
        self.org_image=self.image
        self.ship_image=pygame.image.load(os.path.join('..','tiles', 'ship.png'))
        
        self.game=game
        
        self.gold=150
        self.rations=150
        self.warriors=15
        self.victory=0
        self.defeat=0
        
        self.ship=0
        self.scout=0
        self.carrier=0
        self.miraclehealer=0
        self.wizard=0
        self.navigator=0
        
        self.key1=0
        self.key2=0
        self.key3=0
        
        self.map=map
        
        self.pos=self.map.get_capital()
        
        self.mes1=None
        self.mes2=None
        self.mes3=None
        self.mes4=None
        
        self.foe=None
        #Titles=['Warrior', 'Priest', 'Cleric', 'Lord', 'Nobleman']
        if self.title=='Warrior':
            self.warriors+=5
        if self.title=='Priest':
            self.scout=1
        if self.title=='Cleric':
            self.miraclehealer=1
        if self.title=='Lord':
            self.ship=1
        if self.title=='Nobleman':
            self.gold+=50
            self.rations+=50
            
    def re_init(self,game):    
        self.image=game.player_images[self.title]
        self.org_image=self.image
        self.ship_image=pygame.image.load(os.path.join('..','tiles', 'ship.png'))
        self.game=game
       
    def move(self, co):
        """Moves the player.
        (1,0)  = move right
        (-1,0) = move left
        (0,1)  = move up
        (0.-1) = move down"""
        
        # Clear messages
        self.clear_mes()
        
        # Calculate new coordinates
        mx, my=co
        x, y=self.pos
        nx, ny=x+mx, y+my
        
        new_map=SAME_WOLRD
        
        # check for leaving the map on x-axis
        if nx<0:
            new_map=self.game.world.move((1, 0), self.map)
        elif nx>11:
            new_map=self.game.world.move((-1, 0), self.map)
        
        # check for leaving the map on y-axis        
        if ny<0:
            new_map=self.game.world.move((0, 1), self.map)
        elif ny>11:
            new_map=self.game.world.move((0, -1), self.map)
            
        # check if map has changed and not out of world
        if new_map!=SAME_WOLRD and new_map!=OUT_OF_WOLRD:
            # change the map
            self.map=new_map
            self.game.player_changed_map()
            # calculate new coordinates when changing map
            if mx==1:
                self.pos=(0, ny)
            elif mx==-1:
                self.pos=(11, ny)
                
            if my==1:
                self.pos=(nx, 0)
            elif my==-1:
                self.pos=(nx, 11)
            
            self.game.time_taken(self.get_move_time())       
        # if we don't changed the map, move around
        elif new_map==SAME_WOLRD:
            # check if a ship is needed to enter the tile    
            if self.map.get(self.map.data[nx][ny])['Ship'] and not self.ship:
                return False
            elif self.map.get(self.map.data[nx][ny])['Ship']:
                self.image=self.ship_image
            else:
                self.image=self.org_image
            # move
            self.pos=(nx, ny)
            self.game.time_taken(self.get_move_time())        
            if random.randrange(0, 100) < 20 and self.warriors>0:
                self.encounter()
            
            
        
            
    def encounter(self, Foes=NOTHING):
            # check for random encounter
            nx, ny=self.pos
            if not Foes:
                Foes=self.map.get(self.map.data[nx][ny])['Foes']
                
            if Foes:
                self.game.play_sound('encounter')
                Foe=random.choice(Foes)
                foename=Foe['Name']
                foenumber=random.randrange(Foe['Min'], Foe['Max']+1)
                self.mes1 = random.choice(["You are attacked by", "Encountering ...", "You see ..."])
                self.mes2 = "%s!"%(foename)
                self.mes3 = "You see %i of them!"%(foenumber)
                self.mes4 = "(F)ight or (E)vade?"
                self.game.state=STATE_ASK_FOR_EVADE
                Foe['count']=foenumber
                self.foe=Foe
                self.game.enc=False
                
    def get_move_time(self):
        nx,ny=self.pos
        ttm=self.map.get(self.map.data[nx][ny])['Move']
        
        if self.map.get(self.map.data[nx][ny])['Ship']:
            if self.navigator:
                ttm-=2
        elif self.scout:
            ttm-=2
        return ttm
    
    def enter(self):
        if self.map.key==self.pos:
            self.game.found_a_key()
        e = self.map.get(self.map.data[self.pos[0]][self.pos[1]])['OnEnter']
        if e:
            self.game.time_taken(self.get_move_time()) 
            self.game.enter(e)
    
    def loot(self, gold, rations):
        """Add gold and rations to the player"""
        self.gold+=gold
        self.rations+=rations
    
    def time_to_eat(self):
        needed=random.randrange(self.warriors/2,self.warriors+1)
        if self.rations<needed:
            diff=self.warriors-needed
            self.rations=0
            if diff<2:
                diff=2
            starve=random.randrange(1,diff+1)
            if starve>self.warriors:
                starve=self.warriors
            self.warriors-=starve
            self.mes1="You are not able"
            self.mes2="to take care of"
            self.mes3="your men!"
            self.mes4="%i straved!"%(starve)
            self.game.play_sound('loss')
        else:
            self.rations-=needed
            
    def clear_mes(self):
        """Clear all messages"""
        self.mes1=None
        self.mes2=None
        self.mes3=None
        self.mes4=None
        
