"""
Conch.py, a music toolkit.
By Kris Schnee, borrowing heavily from Pygame's docs and examples.
 
License: Free software; use as you please. Credit appreciated.
Requirements: Just Python and Pygame. Put all sound and music files
in subdirectories called "sound" and "music".
Notes: These are easy functions for using music and sound in Python/Pygame,
just wrappers around Pygame's functions. The Jukebox class keeps track of a
set of loaded sound effects and paths for songs, with keys so you can just
call 'j.PlaySong("Battle Music")' to access an obscurely named song file
neatly stored in a subdirectory. So, to use this code you just LoadSong for
whatever songs you like, giving the filename and a nickname, then PlaySong
to play. Same for sound effects, though behind the scenes the sounds are
actually loaded once and kept in memory instead of just the paths.
 
Example:
j = Jukebox()
j.LoadSong("battle00.mid","Battle Music")
j.PlaySong("Battle Music")
j.StopMusic()
"""
 
 
import pygame ## Pygame toolkit for sound (and many other things); pygame.org
import os     ## File system
import time

try:
    pygame.mixer.init()
except Exception, e:
    print e
    print "Warning: sound disabled"

MODULE_NAME = "Conch"
MODULE_VERSION = "2006.8.9"
 
DEFAULT_MUSIC_EXTENSION = ".mp3"
DEFAULT_SOUND_EXTENSION = ".wav"
SOUND_DIRECTORY = "sfx"
MUSIC_DIRECTORY = "music"
 
JUKEBOX_COMMENTS = False
 
## You can change these options to have sound/music muted by default.
MUSIC_ON = True
SOUND_ON = True
 
 
class Jukebox:
    def __init__(self,dir=MUSIC_DIRECTORY):
        """Load and play sounds and music, referenced by name.
        Create one of these to put audio in your game.
        One is created automatically when the module loads, so
        there's not really a need to make another."""
        self.name = "Jukebox"
        self.comments = JUKEBOX_COMMENTS
 
        self.music_on = MUSIC_ON
        self.sound_on = SOUND_ON
 
        self.songs = {} ## eg. {"Battle Theme":"battle01.ogg"}
 
        self.music_directory = MUSIC_DIRECTORY
        self.sound_directory = SOUND_DIRECTORY
 
        self.sounds = {}
 
    def Comment(self,what):
        if self.comments:
            print "["+self.name+"] " + str(what)
 
    def ToggleMusic(self,on=True):
        self.music_on = on
 
    def ToggleSound(self,on=True):
        self.sound_on = on
 
    def StopMusic(self):
        """Stops music without turning it off; another song may get cued."""
        if not pygame.mixer.get_init():
            return
        pygame.mixer.music.stop()
 
    def QuitMusic(self):
        """Shuts off Pygame's music code.
        This probably isn't necessary."""
        pygame.mixer.music.stop()
        pygame.mixer.quit()

    def MusicGetPos(self):
        if pygame.mixer.get_init():
            return pygame.mixer.music.get_pos()
        return 0

    def MusicVol(self, vol):
        try:
            pygame.mixer.music.set_volume(vol)
        except:
            pass
 
    def LoadSong(self,songname,key=""):
        """Add name, including directory location, to songlist.
        You can give the song a key, too, for easy reference.
        Note that rather than actually loading the song, we store only
        the path to it. Contrast with sound loading."""
        new_song_path = os.path.join(self.music_directory,songname)
        if key:
            self.songs[ key ] = new_song_path
 
    def ResetSongData(self):
        self.songs = {}
 
    def PlaySong(self,cue_name,loops = 0, vol= 1.0, interrupt=False):
        """Cue this song. If interrupt, the song will start even
        if one is already playing."""
        if not pygame.mixer.get_init():
            return
        path = self.songs.get( cue_name )
        if path:
            if not self.music_on:
                return ## Never mind.
 
            if not interrupt:
                if pygame.mixer.music.get_busy():
                    return ## It's busy; go away.
 
            ## OK, we can play. First stop whatever's playing.
            pygame.mixer.music.stop()
 
            ## Now load and play.
            try:
                pygame.mixer.music.load(path)
            except:
                print "Couldn't load song '"+cue_name+"'."
                return
            try:
                pygame.mixer.music.set_volume(vol)
                pygame.mixer.music.play(loops)
                self.Comment("Cue music: '"+cue_name+"'")
            except:
                print "Couldn't play song '"+cue_name+"'."
 
    def FadeoutMusic(self, time):
        if not pygame.mixer.get_init():
            return
        pygame.mixer.music.fadeout(time)
    def LoadSound(self,filename,cue_name=None):
        """Load a sound into memory, not just its name, for quick use."""
        if not pygame.mixer.get_init():
            return
        if not "." in filename:
            filename += DEFAULT_SOUND_EXTENSION
        new_sound = pygame.mixer.Sound( os.path.join(SOUND_DIRECTORY,filename) )
        if not cue_name:
            cue_name = filename
        self.sounds[ cue_name ] = new_sound
 
    def PlaySound(self,cue_name):
        ## How to check whether sound player is busy?
        if not pygame.mixer:
            return

        if self.sounds.has_key( cue_name ):
            a =  self.sounds[ cue_name ].play()
            if cue_name == "Explode":
                while not a:
                    time.sleep(0.1)
                    a = self.sounds[ cue_name ].play()
        else:
            self.Comment("Tried to play sound '"+cue_name+"' without loading it.")
            pass
 
 
##### AUTORUN #####
if __name__ == '__main__':
    ## This code runs if this file is run by itself.
    print "Running "+MODULE_NAME+", v"+MODULE_VERSION+"."
 
else:
    print "Loaded: "+MODULE_NAME
 
    j = Jukebox() ## You can now just refer to "j" in your own program. 
