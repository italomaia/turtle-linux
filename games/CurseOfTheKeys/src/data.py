TILESIZE=32
MAPSIZE=12

ATTACK_SPEED=4

WHITE=(255,255,255)        
GREY=(155,155,155)  
RED=(255,0,0)  
BLACK=(0,0,0)    
OFFSET=8

NOTHING=0
VILLAGE='village'
CAPITAL='capital'
SETTLE='settlement'
RUIN='ruin'
FORTRESS='fortress'
FINAL='final'
WIN=7
LOSE=8
BUILD_OUTPOST='build_outpost'
OUTPOST='outpost'

OUT_OF_WOLRD=0
SAME_WOLRD=-1

AT_PLAYER_VICTORY=4
AT_PLAYER_DEFEAT=-4        
AT_NEW_ROUND=0
AT_PLAYER_ATTACK=1
AT_PLAYER_GO_BACK=-1 
AT_PLAYER_FINISHED=2
AT_FOE_ATTACK=3
AT_FOE_GO_BACK=-2

STATE_RUNNING=0
STATE_ASK_FOR_EVADE=1
STATE_FIGHTING=2
STATE_BUYING_CITY=3
STATE_BUYING_SETTLEMENT=4
STATE_RUIN=5
STATE_FORTRESS=6
STATE_CAPITAL=10
STATE_FINAL=11
STATE_BUILDING_OUTPOST=12
STATE_OUTPOST=13
STATE_ASK_FOR_SAC=14

romours=[("They say you","should avoid","the gnomes!",""),
         ("They say you","should re-enter","a village","for lower prices!"),
         ("They say you","are asking","to much",""),
         ("Did you know","this is just","a remake of","a C64-Game?"),
         ("Majority is the","key to win battles!","",""),
         ("Press s on the","world map to","turn of the music!",""),
         ("They say you","are playing","to much!",""),
         ("Have you met","the dragon already?","",""),
         ("You think the tiles","are ugly??","Contact me!","Look at the README for email"),
         ("They say you","should have many","warriors before","facing the wizard")
         ]

Titles=['Warrior', 'Priest', 'Cleric', 'Lord', 'Nobleman']

MONTH=['January','Februrary','March','April','May','June','July','August','September',
         'October','November','December']

Bandits={'Name':'a group of bandits',
         's_Name':'Bandits',
         'TileNo':101,
         'Min':2,
         'Max':20,
         'Str':1}

Trolls={'Name':'a bunch of trolls',
         's_Name':'Trolls',
         'TileNo':192,
         'Min':2,
         'Max':10,
         'Str':3}

Gnomes={'Name':'a horde of gnomes',
         's_Name':'Gnomes',
         'TileNo':292,
         'Min':15,
         'Max':40,
         'Str':3}

Hillgiants={'Name':'a group of Hillgiants',
         's_Name':'Hillgiants',
         'TileNo':173,
         'Min':2,
         'Max':5,
         'Str':6}

Wolves={'Name':'a pack of wolves',
         's_Name':'Wolves',
         'TileNo':267,
         'Min':5,
         'Max':15,
         'Str':2}

Dragon={'Name':'a dragon',
         's_Name':'Dragon',
         'TileNo':20,
         'Min':1,
         'Max':1,
         'Str':14}

Seaserpents={'Name':'a group of seaserpents',
         's_Name':'Seaserpents',
         'TileNo':186,
         'Min':2,
         'Max':5,
         'Str':3}

Pirates={'Name':'a crew of pirates',
         's_Name':'Pirates',
         'TileNo':64,
         'Min':5,
         'Max':15,
         'Str':2}

Giantoctopus={'Name':'a giant octopus',
         's_Name':'Giantoctopus',
         'TileNo':150,
         'Min':1,
         'Max':1,
         'Str':8}

Guardians={'Name':'the dragons',
         's_Name':"Guardians",
         'TileNo':126,
         'Min':22,
         'Max':25,
         'Str':8}


Foes=[(Bandits,Trolls,Gnomes,Hillgiants),#0
      (Wolves,Bandits,Trolls),#1
      (Hillgiants,Gnomes,Trolls),#2
      (Seaserpents,Pirates,Giantoctopus),#3
      (Dragon,Dragon)]

Plains={'Name':'the plains',
        'Move':4,
        'TileNo':3,
        'wTileNo':41,
        'Ship':0,
        'OnEnter':BUILD_OUTPOST,
        'Symbol':'p',
        'Foes':Foes[0],
        'image':'plains',
        'can_key':False,
        'wintertext':['You freeze as you walk through the ice-cold',
                       'plains of Kurzur. This winter seems to be be',
                       'the hardest of all times. You begin to remem-',
                       'ber your treasured childhood.',
                       ' ',
                       'Never you thought about beeing a leader of',
                       'a small group of brave warriors, but then',
                       'your fate called you out for your quest',
                       ' ',
                      'All you and your men see is white snow.',
                       '',
                       'But you are aware that evil forces are',
                       'lurking out there. You get tired from',
                       'wading the knee-deep snow.'],
        
        'summertext':['Ok, now it is summer',
                      'maybe I have no more ideas?']}

Forest={'Name':'a forest',
        'Move':7,
        'TileNo':1,
        'wTileNo':2,
        'Ship':0,
        'OnEnter':BUILD_OUTPOST,
        'Symbol':'f',
        'Foes':Foes[1],
        'image':'forest',
        'key':False,
        'can_key':False,
        'wintertext':[''],
        'summertext':['']
        }

Mountain={'Name':'the mountains',
        'Move':9,
        'TileNo':61,
        'wTileNo':47,
        'Ship':0,
        'OnEnter':BUILD_OUTPOST,
        'Symbol':'m',
        'Foes':Foes[2],
        'image':'mountain',
        'can_key':False,
        'wintertext':['Mountains are cold in wintertime',
                      'you now??'],
        'summertext':['Summer and Mountains...',
                      'Ah, i like that.']
        }

Water={'Name':'the sea',
        'Move':7,
        'TileNo':0,
        'wTileNo':165,
        'Ship':1,
        'OnEnter':NOTHING,
        'Symbol':'w',
        'Foes':Foes[3],
        'image':'water',
        'can_key':False,
        'wintertext':[''],
        'summertext':['']}

Village={'Name':'a village',
        'Move':5,
        'TileNo':108,
        'wTileNo':124,
        'Ship':0,
        'OnEnter':VILLAGE,
        'Symbol':'c',
        'Foes':NOTHING,
        'image':'village',
        'can_key':True,
        'wintertext':[''],
        'summertext':['']}

Capital={'Name':'the city',
        'Move':7,
        'TileNo':109,
        'wTileNo':125,
        'Ship':0,
        'OnEnter':CAPITAL,
        'Symbol':'C',
        'Foes':NOTHING,
        'image':'capital',
        'can_key':True,
        'wintertext':[''],
        'summertext':['']}

Settlement={'Name':'a settlement',
        'Move':5,
        'TileNo':94,
        'wTileNo':95,
        'Ship':0,
        'OnEnter':SETTLE,
        'Symbol':'S',
        'Foes':NOTHING,
        'image':'settlement',
        'can_key':True,
        'wintertext':[''],
        'summertext':['']}

Ruin={'Name':'an old ruin',
        'Move':7,
        'TileNo':104,
        'wTileNo':106,
        'Ship':0,
        'OnEnter':RUIN,
        'Symbol':'r',
        'Foes':NOTHING,
        'image':'castle',
        'can_key':True,
        'wintertext':[''],
        'summertext':['']}

Fortress={'Name':'a fortress',
        'Move':7,
        'TileNo':132,
        'wTileNo':134,
        'Ship':0,
        'OnEnter':FORTRESS,
        'Symbol':'A',
        'Foes':NOTHING,
        'image':'castle',
        'can_key':True,
        'wintertext':[''],
        'summertext':['']}

Castle={'Name':'the castle',
        'Move':7,
        'TileNo':132,
        'wTileNo':134,
        'Ship':0,
        'OnEnter':FINAL,
        'Symbol':'X',
        'Foes':NOTHING,
        'image':'castle',
        'can_key':False,
        'wintertext':[''],
        'summertext':['']}

Outpost={'Name':'an outpost',
        'Move':3,
        'TileNo':150,
        'wTileNo':142,
        'Ship':0,
        'OnEnter':OUTPOST,
        'Symbol':'O',
        'Foes':NOTHING,
        'image':'outpost',
        'can_key':False,
        'wintertext':[''],
        'summertext':['']}

Terrain=[Plains,Forest,Mountain,Water,Village,Capital,Settlement,Ruin,Fortress,Castle,Outpost]
GENERIC_TEXT=[['You hear the birds cry.',
               'You like that sound....'],
               ['The nights are could, but you',
                'don\' want to set up a fire.',
                'The minions of the nameless',
                'are everywhere...'],
                ['If you like this game, and you',
                 'want help me working on it,',
                 'feel free to contact me!'],
                 ['You have a strange feeling...',
                  'Don\'t you?'],
                  ['One of your man says:',
                   'When I return home, I finally',
                   'will marry my  puppy love!',
                   ' ',
                   'Or not?']
                ]
NW=['ppppppfffppp',
    'pppppppppppp',
    'pppmmppppppp',
    'pppmmpppfcpp',
    'ppmmppffffww',
    'pmrmpffffwwp',
    'mmmpppffwwff',
    'mppppppwwffp',
    'ppCpppwwfffp',
    'ppppmpwwppfp',
    'pppmmmwSpppp',
    'ppppAmmpppAp']

SW=['pppfffpppppp',
    'ppffrffppppp',
    'pcpffffSppwp',
    'ppmmffmmpwww',
    'pmmrfmmmpwww',
    'mmmmmmmppwww',
    'ppmmpmpppcpp',
    'pppppppppppp',
    'pppCpppppppm',
    'ppppppAmppff',
    'ppppppmmmfff',
    'ppppmmmmmfff']

NE=['pppppppppfff',
    'ppppppppffff',
    'pppwwwpppfff',
    'pwwwwwwpSpfp',
    'wwAwwwwwpppp',
    'ppmmwwwwpppp',
    'pmmmpwwpppCp',
    'pmmppppppfpp',
    'ppppppppffpp',
    'ppcppfffffpp',
    'pcpcppfrfppp',
    'pppppppfpppp']

SE=['pppppppppppp',
    'pffpppmmpmmm',
    'fcffppmwAwwm',
    'wwfppmwwwwmm',
    'wwwSpmmmmmmp',
    'wppppppppppp',
    'ppmmpfppCppp',
    'pmmmffpppppp',
    'mmmmfffppcpp',
    'mmmffrfmmmmm',
    'fffffppppppp',
    'fffffffppppp']

FM=['mmmmmmmmmmmm',
    'mmmmmpppppmm',
    'ppmwwpwmppmm',
    'ppmwwXwmfffm',
    'ppmwwwwmpppp',
    'ppmmmmmmpppp',
    'pppppmmpSppp',
    'ppppppppppcp',
    'pppppppppwwp',
    'ppppppppwwwp',
    'pppfffpppppp',
    'pffffffffppp']

m1=['mmmmmmmmmppp',
    'mmmmmmpppppp',
    'mmmmpppppppp',
    'mmmmppCppppp',
    'ppcppppppppp',
    'pppppprpcppp',
    'pppppppppppp',
    'ppppSppppppp',
    'ppppppffffpp',
    'ppppffffpppp',
    'wwwfffffwwww',
    'wwwwwwwwwwww']

m2=['pppppffffmmm',
    'ppffffmmmmmm',
    'pffAffffrmmm',
    'pppppfffppww',
    'ppcppppppwww',
    'ppffffppwwff',
    'pppffffpwwff',
    'ppppCppwwwrf',
    'ppppppwwwwff',
    'pppAwwwwwwff',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww']

m3=['mmmwwwmmmmmm',
    'mmmwwwmfffmm',
    'rpwwwfffrmmm',
    'wwwwpfffpppp',
    'wpcppppppcpp',
    'ffffpppppppp',
    'fffpppCppppp',
    'ffAppppffppp',
    'ffppppffffpp',
    'fppppppffppp',
    'wwwwwSpcpwww',
    'wwwwwwwwwwww']

m4=['wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwpppwwww',
    'wwwwppCpwwww',
    'wwwwwppppwww',
    'wwwwwSppwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww']

m5=['wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwpffpww',
    'wwwwwwwwrfww',
    'wwwwwwwfffww',
    'wwwwwwwwpwww',
    'wwwwwwwpppww',
    'wwwwwwwwwwww',
    'wwwwpSwwwwww',
    'wwwppwwwwwww',
    'wwwwwwwwwwww']

m6=['wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwmmmwww',
    'wwwmmmAmwwww',
    'wwwwmmmmwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww']

m7=['wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwpppAwwwpp',
    'pppppppppppp',
    'pppppppppppp',
    'pppffffppppp',
    'ppfffrpppppp',
    'pppffffppppp',
    'pppppppppppp',
    'pppppppCpppp',
    'pppppppppppp',]

m8=['wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'ppprwwwwwppp',
    'pppppwwwwppp',
    'ppppppwwrppp',
    'ppppppwwpppp',
    'ppcppwwcpppp',
    'pppppwwppppp',
    'pppcwwwmprpp',
    'ppppwwwmpppp',
    'pppwwwmppppp',]

m9=['wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'wwwwwwwwwwww',
    'ppwwwwppwwpp',
    'pppwwpppAppp',
    'pppcpppmmmmp',
    'pppppmmmmppp',
    'ppfffffppcpp',
    'pmmmppCppppp',
    'ppmmmmmppppp',
    'ppppcppppprp',
    'pppppmmmmmmm',]
    
    
#        blackrect=pygame.Surface((260,20))
#        text=['A long, long time ago...',
#              '',
#              'A vicious wizard attacks the once',
#              'peacefull kingdom of Kurzur.',
#              '',
#              'His minions depredate the country',
#              'and chaos rises in these dark times.',
#              '',
#              'As you sleep, the elder gods speak to you:',
#              '',
#              'Only you can defeat the evil wizard.',
#              'Search for the three cursed keys which',
#              'where once created to detain the nameless',
#              'wizard, but his power has now become to',
#              'intense. Once you got all keys, you will',
#              'find the nameless one.',
#              '',
#              'The bravest men will follow you on your',
#              'holy quest to save the kingdom!']
        
        #self.draw_text(text, 'The Curse Of The Keys',back, BLACK,False)
        #self.draw_border(False, True)