'''score releted stuff'''

import os
import pickle
import sys
import math

from config import *
import utils
import pygame
from pygame.locals import *
import music

MAX = 7 # max players number in highscore screen - magical number
CPL = 15 # max char per line

class HighScores(object):

    def __init__(self, screen, father=None, score=-1):
        self.screen = screen
        self.father = father
        self.score = score
        self.top_scores = []
        self.font1 = pygame.font.Font(FONT2, 40)
        self.font2 = pygame.font.Font(FONT2, 30)

    def loop(self):
        music.stop_music()
        if (not os.path.exists(HISCORES)) and (self.score <= 0):
            text_list=["HIGH SCORE","I\'m sorry","Nobody has been saved.","Nobody has stopped being zombie"]
            music.play_music(PLAYMUSIC)
            self.draw_screen(text_list)
            return self._waitKey()
        else:
            self.top_scores = self._load_score()
            if self.score > 0:
                self._add()
            text_list = self._convert()
            text_list[0:0]=['HIGH SCORES']
            music.play_music(PLAYMUSIC)
            self.draw_screen(text_list)
            return self._waitKey()

    def _add(self):
        #Check minor_value before adding
        top = self.top_scores
        for i in range(MAX):
            if self.score > top[i][1]:
                name = InputPanel(self.screen,self.score).loop()
                self.top_scores = top[:i] + [(name, self.score)] + top[i:-1]
                break
        f = file(HISCORES, 'w')
        pickle.dump(self.top_scores,f)

    def _load_score(self):
        top_scores = []
        if not os.path.exists(HISCORES):
            top_scores = [("", 0),
                            ("", 0),
                            ("", 0),
                            ("", 0),
                            ("", 0),
                            ("", 0),
                            ("", 0)]
            f = file(HISCORES, 'w')
            pickle.dump(top_scores, f)
        else:
            f = file(HISCORES)
            top_scores = pickle.load(f)
        return top_scores

    def _convert(self):
        top7 = []
        for i,element in enumerate(self.top_scores):
            if element[1] != 0:
                if element[1] >= SCORE_HUMAN:
                    kind=" (HUMAN)"
                elif element[1] >= SCORE_DEAD:
                    kind=" (HAPPY DEAD)"
                else:
                    kind=" (you are in the limb)"
                top7.append(str(i+1) + " " + element[0] + "  " + str(element[1]) + kind)
        return top7

    def draw_screen(self, text_list):

        pygame.display.set_caption(WINDOW_TITLE)
        background = utils.load_image(SCOREIMAGE)

        clock = pygame.time.Clock()
        separator = 3

        title = text_list[0]
        text_list.remove(title)

        title_img = self.font1.render(title, True, WHITE)
        title_img2 = self.font1.render(title, True, BLACK)
        topleft = (background.get_rect().width - title_img.get_rect().width) / 2, 25
        topleft2 = (background.get_rect().width - title_img.get_rect().width) / 2-separator, 25-separator
        background.blit(title_img2, topleft2)
        background.blit(title_img, topleft)
        bg = background.copy()

        self.screen.blit(background, (0, 0))
        pygame.display.flip()

        hor_step = self.font2.get_height()
        done = False
        timeloop = 0
        state = 0

        while not done:
            clock.tick(CLOCK_TICS)
            pygame.display.flip()
            self.screen.blit(background, (0, 0))
            y = hor_step + 80

            timeloop += 1
            if timeloop == CLOCK_TICS:
                state = 1
                done = True

            for i,text_item in enumerate(text_list):
                img = self.font2.render(text_item, True, WHITE)
                img2 = self.font2.render(text_item, True, BLACK)
                x2 = self.screen.get_width()/2
                if (state == 0) and (i%2 == 0):
                    x1 = x2 - ((WIDTH * 0.86) * (50 - timeloop) / 50)
                elif (state == 0) and (i%2 == 1):
                    x1 = x2 + ((WIDTH * 0.86) * (50 - timeloop) / 50)
                else:
                    x1=x2
                x = (x1+(x2-x1)*(1-math.exp(-timeloop/20.0)))
                x -= img.get_width()/2
                self.screen.blit(img2, (x-separator, y-separator))
                self.screen.blit(img, (x, y))
                if x1 == x2:
                    bg.blit(img, (x, y))
                y += hor_step + 10

        return bg

    def _waitKey(self):
        while True:
            pygame.event.clear()
            event = pygame.event.wait()
            if (event.type == QUIT):
                sys.exit(0)
            elif (pygame.key.get_pressed()[K_RETURN]) or (pygame.key.get_pressed()[K_ESCAPE]):
                music.stop_music()
                return self.father

class InputPanel(object):
    '''A generic input panel.'''

    def __init__(self, screen, score):
        music.play_music(MENUMUSIC)
        self.screen = screen
        self.cursor = '!'
        self.text = ""
        self.done = False
        self.font1 = pygame.font.Font(FONT3, 50)
        self.clock = pygame.time.Clock()

        score_text="Your score is "+str(score)
        text_list=["CONGRATULATION !!!","WELCOME TO THE \"HALL OF FAME\"","Please, introduces your name","  ",score_text]
        self.background = HighScores(screen).draw_screen(text_list)
        pygame.display.flip()
        
        self._draw_text()

    def loop(self):
        while not self.done:
            self.clock.tick(CLOCK_TICS)
            self.screen.blit(self.background, (0,0))    

            for event in pygame.event.get():
                self.control(event)

            self._draw_text()
            pygame.display.flip()
        music.stop_music()
        return self.text

    def control(self, event):
        if event.type == QUIT:
            sys.exit(0)
        if event.type == KEYDOWN:
            if event.key in (K_RETURN, K_KP_ENTER):
                self.enter()
            else:
                char = event.unicode
                if (self.valid_char(char)) and (len(self.text) < CPL):
                    self.text += char
                    self._draw_text()
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                    self._draw_text()

    def valid_char(self, char):
        if char:
            if char in u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ1234567890":
                return True
        return False
               
    def enter(self):
        self.done = True

    def _draw_text(self):
        y = 300 # Tune this value as you need
        separator = 2
        text_img = self.font1.render(self.text + self.cursor, True, WHITE)
        text_img2 = self.font1.render(self.text + self.cursor, True, BLUE)
        x = (self.screen.get_width() - text_img.get_width()) / 2
        self.screen.blit(text_img2, (x-separator,y-separator))
        self.screen.blit(text_img, (x,y))

