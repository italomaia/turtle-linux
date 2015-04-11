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
from Menu import *

USE_ANTIALIAS = True


class Game:

    def __init__(self, screen):

        self.screen = screen
        self.sprites = Group()
        self.clearables = Group()
        self.asteroids = Group()
        self.ufos = Group()
        self.shots = Group()
        self.enemyshots = Group()
        self.particles = Group()

        Ship.containers = self.sprites
        Shot.containers = self.sprites, self.shots, self.clearables
        EnemyShot.containers = self.sprites, self.enemyshots, self.clearables
        Asteroid.containers = self.sprites, self.asteroids, self.clearables
        Ufo.containers = self.sprites, self.ufos, self.clearables
        Exhaust.containers = self.sprites, self.particles
        Particle.containers = self.sprites, self.particles

        self.ship = Ship()
        Asteroid(GeneratePos())
        self.paused = False

        self.clock = pygame.time.Clock()
        self.events = []

        self.level = 1
        self.score = 0
        self.lives = 5
        self.done = False
        self.highscore = load_highscore()

        self.font = load_font("nasaliza.ttf", 12)
        self.font2 = load_font("nasaliza.ttf", 60)
        self.font3 = load_font("nasaliza.ttf", 30)
        load_sounds()
        play_bg()

    def __clearSprites(self):
        for s in self.clearables:
            pygame.sprite.Sprite.kill(s)
        
    def __collisionDetect(self):

        for a in self.asteroids:
            for s in self.shots:
                if Collision(a.drawpoints, s.drawpoints):
                    a.hit()
                    s.kill()
                    play_boom()
                    self.score += 75*a.scale

        for a in self.asteroids:
            if Collision(a.drawpoints, self.ship.drawpoints):
                if self.ship.alive():
                    self.ship.kill()
                    play_boom()
                    self.lives -= 1
                    self.__clearSprites()


        for s in self.enemyshots:
            if Collision(s.drawpoints, self.ship.drawpoints):
                if self.ship.alive():
                    self.ship.kill()
                    play_boom()
                    self.lives -= 1
                    self.__clearSprites()

        for u in self.ufos:
            for s in self.shots:
                if Collision(u.drawpoints, s.drawpoints):
                    s.kill()
                    u.kill()
                    self.score += 125
                    play_boom()


    def __drawScene(self):
        self.screen.fill((0, 0, 0))
        for star in Stars():
            self.screen.set_at(star, (200, 200, 200))
        self.sprites.draw(self.screen)
        render_text(self.screen, "Score: %05d" % self.score, self.font, (10, 10))
        render_text(self.screen, "High: %05d" % self.highscore, self.font, (10, 25))
        render_text(self.screen, "Level: %d" % self.level, self.font, (10, 40))
        render_text(self.screen, "Lives x%d" % self.lives, self.font, (10, 55))
        render_text(self.screen, "FPS: %02d" % self.clock.get_fps(), self.font, (10, 70))
        if self.lives <= 0 and not self.particles:
            render_text(self.screen, "Game Over!", self.font2, (320, 225), True)
            render_text(self.screen, "Press Escape to Exit", self.font3, (320, 270), True)
        pygame.display.flip()

    def __gameInput(self):
        self.events = pygame.event.get()
        for e in self.events:
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.done = True
                if e.key == K_a:
                    global USE_ANTIALIAS
                    USE_ANTIALIAS ^= 1
                if e.key == K_p:
                    self.paused ^= 1
            if e.type == ACTIVEEVENT:
                if (e.state == 2 and e.gain == 0) or (e.state == 6 and e.gain == 0):
                    self.paused = True
                elif e.state == 6 and e.gain == 1:
                    self.paused = False

    def __playerInput(self):
        for e in self.events:
            if e.type == KEYDOWN:
                if e.key not in (K_LEFT, K_RIGHT, K_UP, K_DOWN, K_ESCAPE, K_p, K_a) and self.ship.alive():
                    Shot(self.ship.pos, self.ship.angle)
                    play_shoot()

    def __updateGame(self):
        for s in self.sprites:
            s.use_antialias = USE_ANTIALIAS
        if not self.ship.alive() and not self.particles and self.lives > 0:
            self.ship = Ship()
            for i in range(self.level):
                Asteroid(GeneratePos())
        
        if not self.asteroids and self.ship.alive():
            self.__clearSprites()
            self.level += 1
            self.ship.pos = [320, 240]
            self.ship.velocity = [0, 0]
            for i in range(self.level):
                Asteroid(GeneratePos())

        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(int(self.highscore))

        for u in self.ufos:
            if not random.randrange(30) and self.ship.alive():
                EnemyShot(u.pos, AngleToTarget(u.pos, self.ship.pos))
                play_ufo()
        if not random.randrange(850) and not self.ufos and self.ship.alive():
            Ufo()

    def __mainLoop(self):
        
        while not self.done:

            self.clock.tick(60)
            self.sprites.update()

            while self.paused: self.__gameInput()
            self.__gameInput()
            self.__playerInput()
            self.__collisionDetect()
            self.__updateGame()
            self.__drawScene()

    def Run(self):
        self.__mainLoop()
