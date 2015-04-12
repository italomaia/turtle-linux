from __future__ import division

import os

import data
from content import levels
from common import *

class GameState(object):
    def __init__(self, profile=None):
        if not profile:
            self.start_game()
        else:
            self.score = profile['score']
            self.current_max_level = profile['current_max_level']
            self.best_swags = profile['best_swags']
            self.stats = profile['stats']
        self._loaded_level = None
        self._loaded_stage = None
        self.current_level = 0
        self.current_retry_level = None
        self.advance = False
        
    def __repr__(self):
        string = 'score = %r\n' % (self.score,)
        string += 'current_max_level = %r\n' % (self.current_max_level,)
        string += 'best_swags = %r\n' % (self.best_swags,)
        string += 'stats = %r\n' % (self.stats,)
        return string
        
    def start_game(self):
        self.score = 0
        self.current_max_level = 0
        self.best_swags = {}
        self.stats = {}
        
    def start_level(self, n, control):
        import swag
        self.current_level = n
        self.swag_val = 0
        self.level_score = 0
        self.level_swags = 0
        self.level_collected_swag = {}
        if n >= len(levels.levels):
            control.switch_handler('menu')
        elif levels.levels[n][0].endswith('.stage'):
            control.switch_handler('game')
            for a in self.current_stage['actors']:
                if isinstance(a, swag.Swag):
                    self.swag_val += a.value
            if levels.levels[n][2] is not None:
                control.music.start_song(levels.levels[n][2])
        else:
            control.switch_handler('cutscene')
            if levels.levels[n][2] is not None:
                control.music.start_song(levels.levels[n][2])
        self.current_retry_level = n
        
    def score_swag(self, swag):
        self.level_score += swag.value
        self.score += swag.value
        self.level_collected_swag[swag.name] = self.level_collected_swag.get(swag.name, 0) + 1
        self.level_swags += 1
    
    def finish_level(self, control):
        self.advance = False
        if self.swag_val:
            percent = 100 * self.level_score / self.swag_val
            if self.current_level not in self.best_swags or self.best_swags[self.current_level][0] < percent:
                self.best_swags[self.current_level] = (percent, self.level_collected_swag)
        menu_state = "continue"
        if levels.levels[self.current_level][0].endswith(".scene"):
            menu_state = "levels"
        self.current_level += 1
        if self.current_level > self.current_max_level:
            self.current_max_level = self.current_level
            self.advance = True
        del self.current_frames
        data.save_profile('main.profile', self)
            
    def win_level(self):
        pass
    
    def fail_level(self, control):
        control.switch_handler('menu', 'death')
        
    @property
    def game_completed(self):
        return self.current_level >= len(levels.levels)

    @property
    def current_stage(self):
        if self._loaded_level == self.current_level:
            return self._loaded_stage
            
        self._loaded_stage = data.load_stage(levels.levels[self.current_level][0])
        return self._loaded_stage

    @property
    def current_level_name(self):
        return levels.levels[self.current_level][1]
        return "Unnamed level"
    
    @cached
    def current_frames(self):
        return data.load_scene(levels.levels[self.current_level][0])
