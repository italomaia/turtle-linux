#! /usr/bin/env python

# Vectorpods 2 - A arcade space shooter programmed by PyMike
# Copyright (C) 2007  PyMike
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import sys, os
import math, random

import pygame
from pygame.locals import *

from Engine import *
from GameObjects import *
import Game


class MenuOption:

    def __init__(self, text, font, pos, command):

        self.text = text
        self.font = font
        self.pos = list(pos)
        ren = self.font.render(text, 1, (255, 255, 255))
        self.pos[0] -= ren.get_width()/2
        self.cmd = command
        self.selected = False

    def command(self):
        if self.cmd: self.cmd()

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def render(self, screen):
        if self.selected:
            ren = self.font.render(self.text, 1, (255, 255, 255))
        else:
            ren = self.font.render(self.text, 1, (175, 175, 175))
        screen.blit(ren, self.pos)


class Options:

    def __init__(self, screen, all):

        self.screen = screen
        self.options = []
        self.font = load_font("nasaliza.ttf", 30)
        self.font2 = load_font("nasaliza.ttf", 70)
        self.font3 = load_font("nasaliza.ttf", 20)
        self.AddOption("Delete Highscore", self.deleteHigh)
        self.AddOption("Graphics: High", self.togglaAA)
        self.AddOption("Back", self.back)
        self.options[0].select()
        self.option = 1
        self.done = False
        if Game.USE_ANTIALIAS:
            self.options[1].text = "Graphics: High"
        if not Game.USE_ANTIALIAS:
            self.options[1].text = "Graphics: Low"
        self.all = all
        Asteroid.containers = self.all
        self.clock = pygame.time.Clock()

    def deleteHigh(self):
        save_highscore(0)

    def togglaAA(self):
        Game.USE_ANTIALIAS ^= 1
        if Game.USE_ANTIALIAS:
            self.options[1].text = "Graphics: High"
        if not Game.USE_ANTIALIAS:
            self.options[1].text = "Graphics: Low"

    def back(self):
        self.done = True

    def AddOption(self, text, command):
        pos = (320, 300 + len(self.options)*self.font.get_height())
        option = MenuOption(text, self.font, pos, command)
        self.options.append(option)

    def __moveDown(self):
        for o in self.options:
            o.selected = False
        self.option += 1
        if self.option > len(self.options):
            self.option = 1
        self.options[self.option-1].select()

    def __moveUp(self):
        for o in self.options:
            o.selected = False
        self.option -= 1
        if self.option < 0:
            self.option = len(self.options)-1
        self.options[self.option-1].select()

    def __menuInput(self):
        self.events = pygame.event.get()
        for e in self.events:
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.done = True
                if e.key == K_UP:
                    self.__moveUp()
                if e.key == K_DOWN:
                    self.__moveDown()
                if e.key == K_RETURN:
                    self.options[self.option-1].command()
            
    def __drawScene(self):
        self.screen.fill((0, 0, 0))
        self.all.draw(self.screen)
        for star in Stars():
            self.screen.set_at(star, (200, 200, 200))
        for o in self.options:
            o.render(self.screen)
        render_text(self.screen, "Options", self.font2, (320, 100), True)
        render_text(self.screen, "Change your options below", self.font3, (320, 212), True)
        pygame.display.flip()

    def loop(self):
        
        while not self.done:
            self.clock.tick(60)
            self.all.update()
            self.__menuInput()
            self.__drawScene()

    def Run(self):
        self.loop()

