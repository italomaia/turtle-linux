# $Id$
import data
import pygame, random, os
pygame.mixer.pre_init(44100, -16, False, 1024)
pygame.mixer.set_reserved(1)

def buildSounds():
    ret = []
    negras = [1, 3, 6, 8, 10]
    for n in range(12*4):
        if n%12 in negras:
            filename = data.filepath("sonidos/tonos%03d.ogg"%n)
            ret.append(pygame.mixer.Sound(filename))
    return ret

def buildMusic():
    ret = []
    for filename in os.listdir(data.filepath("music/")):
            if filename[-4:]==".ogg":
                ret.append(data.filepath("music/"+filename))
    return ret

sounds = buildSounds()
themes = buildMusic()

def playRandomSong():
    pygame.mixer.music.load( random.choice( themes) )
    pygame.mixer.music.play()
    
def playSound(n, vol):
    n = int(n*len(sounds))%len(sounds)
    chan = pygame.mixer.find_channel(True)
    chan.play(sounds[n])
    # podriamos Jugar con el stereo!
    chan.set_volume(vol)

def playSoundFile(filename, vol):
    chan = pygame.mixer.find_channel(True)
    chan.play( pygame.mixer.Sound( data.filepath("sonidos/%s" % filename ) ) )
    # podriamos Jugar con el stereo!
    chan.set_volume(vol)

def initMusicFile(filename):
    return pygame.mixer.Sound( data.filepath("music/%s" % filename ) )

def stopMusic():
    pygame.mixer.Channel(0).stop()
    
def playMusicSound(sound, vol):
    chan = pygame.mixer.Channel(pygame.mixer.get_num_channels()-1)
    chan.play( sound )
    # podriamos Jugar con el stereo!
    chan.set_volume(vol)
