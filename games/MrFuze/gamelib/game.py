#! /usr/bin/env python

import sys, os
import random

import pygame
from pygame.locals import *

from cutscenes import *
from data import *
from sprites import *
from level import *

def RelRect(actor, camera):
    return Rect(actor.rect.x-camera.rect.x, actor.rect.y-camera.rect.y, actor.rect.w, actor.rect.h)

class Camera(object):
    def __init__(self, player, width):
        self.player = player
        self.rect = pygame.display.get_surface().get_rect()
        self.world = Rect(0, 0, width, 480)
        self.rect.center = self.player.rect.center
    def update(self):
        if self.player.rect.centerx > self.rect.centerx+64:
            self.rect.centerx = self.player.rect.centerx-64
        if self.player.rect.centerx < self.rect.centerx-64:
            self.rect.centerx = self.player.rect.centerx+64
        if self.player.rect.centery > self.rect.centery+64:
            self.rect.centery = self.player.rect.centery-64
        if self.player.rect.centery < self.rect.centery-64:
            self.rect.centery = self.player.rect.centery+64
        self.rect.clamp_ip(self.world)
    def draw_sprites(self, surf, sprites):
        for s in sprites:
            if s.rect.colliderect(self.rect):
                surf.blit(s.image, RelRect(s, self))

def save_level(lvl):
    open(filepath("prog.sav"), "w").write(str(lvl))

def get_saved_level():
    try:
        return int(open(filepath("prog.sav")).read())
    except:
        open(filepath("prog.sav"),  "w").write(str(1))
        return 1

class Game(object):

    def __init__(self, screen, continuing=False):

        self.screen = screen
        self.sprites = pygame.sprite.OrderedUpdates()
        self.players = pygame.sprite.OrderedUpdates()
        self.platforms = pygame.sprite.OrderedUpdates()
        self.movingplatforms = pygame.sprite.OrderedUpdates()
        self.string = pygame.sprite.OrderedUpdates()
        self.baddies = pygame.sprite.OrderedUpdates()
        self.nomoveplatforms = pygame.sprite.OrderedUpdates()
        self.coins = pygame.sprite.OrderedUpdates()
        self.playerdying = pygame.sprite.OrderedUpdates()
        self.bombs = pygame.sprite.OrderedUpdates()
        self.explosions = pygame.sprite.OrderedUpdates()
        self.spikes = pygame.sprite.OrderedUpdates()
        self.shots = pygame.sprite.OrderedUpdates()
        self.springs = pygame.sprite.OrderedUpdates()
        self.bosses = pygame.sprite.OrderedUpdates()
        
        Player.right_images = [load_image("hero1.png"), load_image("hero2.png"), load_image("hero3.png")]
        Platform.images = {"platform-top.png": load_image("platform-top.png"), "platform-middle.png": load_image("platform-middle.png")}
        MovingPlatform.image = load_image("moving-platform.png")
        Stringer.image = load_image("string.png")
        Baddie.left_images1 = [load_image("monster%d.png" % i) for i in range(1, 3)]
        Baddie.left_images2 = [load_image("slub%d.png" % i) for i in range(1, 3)]
        Baddie.left_images3 = [load_image("squidge%d.png" % i) for i in range(1, 3)]
        BaddieBoom.left_images1 = [load_image("monster2.png"), load_image("monster3.png"), load_image("exp1.png"), load_image("exp2.png"), load_image("exp3.png")]
        BaddieBoom.left_images2 = [load_image("slub2.png"), load_image("slub3.png"), load_image("exp1.png"), load_image("exp2.png"), load_image("exp3.png")]
        BaddieBoom.left_images3 = [load_image("squidge2.png"), load_image("squidge3.png"), load_image("exp1.png"), load_image("exp2.png"), load_image("exp3.png")]
        Coin.images = [load_image("coin%s.png" % i) for i in range(1, 5)]
        CoinDie.images = [load_image("exp2-%d.png" % i) for i in range(1, 4)]
        PlayerDie.right_images = [load_image("hero4.png"), load_image("hero5.png"), load_image("exp2-1.png"), load_image("exp2-2.png"), load_image("exp2-3.png")]
        Bomb.images = [load_image("bomb1.png"), load_image("bomb2.png")]
        Spikes.image = load_image("spikes.png")
        BaddieShot.image = load_image("shot.png")
        Spring.images = [load_image("spring1.png"), load_image("spring2.png")]
        AirPlatform.image = load_image("airplatform.png")
        Boss.left_images = [load_image("boss1.png"), load_image("boss2.png"), load_image("boss3.png")]

        Player.groups = self.sprites, self.players
        Platform.groups = self.sprites, self.platforms, self.nomoveplatforms
        MovingPlatform.groups = self.sprites, self.platforms, self.movingplatforms
        Stringer.groups = self.sprites, self.string
        Baddie.groups = self.sprites, self.baddies
        BaddieBoom.groups = self.sprites
        Coin.groups = self.sprites, self.coins
        CoinDie.groups = self.sprites
        PlayerDie.groups = self.sprites, self.playerdying
        Bomb.groups = self.sprites, self.bombs
        Explosion.groups = self.sprites, self.explosions
        Spikes.groups = self.sprites, self.spikes
        BaddieShot.groups = self.sprites, self.shots
        Spring.groups = self.sprites, self.springs
        AirPlatform.groups = self.sprites, self.platforms, self.nomoveplatforms
        Boss.groups = self.sprites, self.bosses

        self.score = 0
        self.lives = 5
        self.lvl   = 1
        if continuing:
            self.lvl = get_saved_level()
        self.player = Player((0, 0))
        self.clock = pygame.time.Clock()
        self.bg = load_image("bg.png")
        self.level = Level(self.lvl)
        self.camera = Camera(self.player, self.level.get_size()[0])
        self.font = pygame.font.Font(filepath("font.ttf"), 16)
        self.heart1 = load_image("heart-full.png")
        self.heart2 = load_image("heart-empty.png")
        self.heroimg = load_image("hero1.png")
        self.coin_sound = load_sound("coin.ogg")
        self.running = 1
        self.booming = False
        self.boom_timer = 0
        self.music = "gameloop.ogg"
        if self.lvl == 10:
            self.music = "boss.ogg"
        
        if not continuing:
            play_music("intro.ogg")
            cutscene(self.screen, [
            "A long time ago in the not",
            "so distant future..."])
            cutscene(self.screen, [
            "An evil professor, one Dr. Bobmer",
            "by name, will attempt to destroy",
            "the world if President Bushwacker",
            "does not surrender his political",
            "throne, and reduce America to",
            "a dictatorship..."])
            cutscene(self.screen, [
            "Desperate, the President decides",
            "to call upon a strange little man",
            "called Mr. Fuze to stop the mad",
            "scientist from destroying the world!"])
            cutscene(self.screen, [
            "But, unfortunately, Dr. Bobmer heard",
            "of the President's plans, and in a",
            "rage he set the bombs all over the",
            "world, then he did the most dastardly",
            "crime of his life..."])
            cutscene(self.screen, [
            "HE LIT THE FUSES!"])
            cutscene(self.screen, [
            "The daring Mr. Fuze then set out to",
            "extinguish the burning fuses, but",
            "the cunning Dr. Bobmer let loose his",
            "mutated Truant Officers on him!"])
            cutscene(self.screen, [
            "Luckily, Mr. Fuze has his trusty",
            "string electrocutifier to",
            "discombobulatify the Truant Officers!"])
            cutscene(self.screen, [
            "The clock is ticking... the fuses are",
            "burning... Can Mr. Fuze save the day?",
            "",
            "Press enter to find out."])
            stop_music()
        
        self.intro_level()
        self.boom_sound = load_sound("boom.ogg")
        self.main_loop()
        
    def end(self):
        self.running = 0
        
    def intro_level(self):
        stop_music()
        self.screen.fill((0, 0, 0))
        self.draw_stats()
        ren = self.font.render("Level %d" % self.lvl, 1, (255, 255, 255))
        self.screen.blit(ren, (320-ren.get_width()/2, 230))
        ren = self.font.render("Lives x%d" % self.lives, 1, (255, 255, 255))
        self.screen.blit(ren, (320-ren.get_width()/2, 255))
        pygame.display.flip()
        pygame.time.wait(2500)
        play_music(self.music)
        if self.lvl == 10:
            cutscene(self.screen,
            ['"Mr. Fuze?"'])
            cutscene(self.screen,
            ['"Do you copy?"'])
            cutscene(self.screen,
            ['"We have information from',
            'an unreliable source that',
            'Dr. Bobmer may be in the',
            'area you are approaching."'])
            cutscene(self.screen,
            ['"If you encounter him, he..\'s',
            'wha... t... do..."'])
            cutscene(self.screen,
            ['Oh no! You lost your connection!'])
            cutscene(self.screen,
            ['I TOLD you you needed to get a',
            'better wireless card...'])
            cutscene(self.screen,
            ['If you can\'t figure out how to',
            'beat this guy, don\'t say I',
            'didn\'t warn ya!'])
        
    def next_level(self):
        stop_music()
        self.booming = False
        self.boom_timer = 0
        try:
            self.lvl += 1
            if self.lvl == 10:
                self.music = "boss.ogg"
            self.clear_sprites()
            self.level = Level(self.lvl)
            self.player = Player((0, 0))
            self.camera = Camera(self.player, self.level.get_size()[0])
            save_level(self.lvl)
            self.intro_level()
        except:
            if self.lives == 0: #HACK MUST FIX LOL
                self.lives += 1
            cutscene(self.screen,
            ["From the Desk of the President..."])
            play_music("congratulations.ogg", volume=1)
            cutscene(self.screen,
            ['"CONGRATUFICATIONS!"'])
            cutscene(self.screen,
            ['"You have saved the world from being',
            'DESTRUCTIFIED!"'])
            cutscene(self.screen,
            ['"The world needs more',
            'de-destructificators like you!"'])
            cutscene(self.screen,
            ['"You have my most sincere thanks',
            'and appreciation. I might even give',
            'you a cut on your taxes this year!"'])
            cutscene(self.screen,
            ['"Your humblified servant,',
            ' - W.G. Bushwacker"'])
            cutscene(self.screen,
            ['"P.S."'])
            cutscene(self.screen,
            ['"Press Enter to Endify the Game."'])
            self.end()
                
    def redo_level(self):
        self.booming = False
        self.boom_timer = 0
        if self.running:
            self.clear_sprites()
            self.level = Level(self.lvl)
            self.player = Player((0, 0))
            self.camera = Camera(self.player, self.level.get_size()[0])
            #play_music("gameloop.ogg")
            
    def boom(self):
        if not self.booming:
            stop_music()
            self.lives -= 1
            self.booming = True
            self.boom_timer = 200
            
    def show_boomed(self):
        cutscene(self.screen, ["THE WORLD HAS GONE BLOOEY!"])
        if self.lives <= 0:
            self.gameover_screen()
        else:
            self.intro_level()
            play_music(self.music)
        
    def show_death(self):
        ren = self.font.render("YOU HAVE BEEN DEADIFIED!", 1, (255, 255, 255))
        self.screen.blit(ren, (320-ren.get_width()/2, 235))
        pygame.display.flip()
        pygame.time.wait(2500)
        
    def gameover_screen(self):
        stop_music()
        play_music("gameover.ogg")
        cutscene(self.screen, ["This is what you call", "GAME OVERFICATION!"])
        self.end()      
    def bomb_deactivate(self):
        self.draw_stats()
        ren = self.font.render("YAY! THE BOMB WAS DEACTIVICATED!", 1, (255, 255, 255), (0, 0, 0))
        self.screen.blit(ren, (320-ren.get_width()/2, 235))
        pygame.display.flip()
        pygame.time.wait(2500)
          
    def clear_sprites(self):
        for s in self.sprites:
            pygame.sprite.Sprite.kill(s)

    def main_loop(self):

        while self.running:
            BaddieShot.player = self.player
            if not self.running:
                return
            
            self.boom_timer -= 1

            self.clock.tick(60)
            self.camera.update()
            if self.boom_timer <= 0:
                for s in self.sprites:
                    s.update()
            else:
                Explosion((random.randrange(640) + self.camera.rect.x, random.randrange(480) + self.camera.rect.y))
                if not random.randrange(4):
                    self.boom_sound.play()
                for e in self.explosions:
                    e.update()
            self.player.collide(self.platforms)
            self.player.collide(self.springs)
            self.player.collide(self.spikes)
            if self.booming and self.boom_timer <= 0:
                self.show_boomed()
                self.redo_level()
            for b in self.bombs:
                if self.player.rect.colliderect(b.rect):
                    self.bomb_deactivate()
                    self.next_level()
                if b.explode_time <= 0:
                    self.boom()
            for s in self.shots:
                if not s.rect.colliderect(self.camera.rect):
                    s.kill()
                if s.rect.colliderect(self.player.rect):
                    self.player.hit()
                    s.kill()
            if self.booming and self.boom_timer <= 0:
                self.show_boomed()
                self.redo_level()
            for c in self.coins:
                if self.player.rect.colliderect(c.rect):
                    c.kill()
                    self.coin_sound.play()
                    CoinDie(c.rect.center)
                    self.score += 25
            for p in self.movingplatforms:
                p.collide(self.players)
                for p2 in self.platforms:
                    if p != p2:
                        p.collide_with_platforms(p2)
            for b in self.baddies:
                if b.rect.colliderect(self.camera.rect):
                    if b.type == "squidge":
                        if not random.randrange(70):
                            BaddieShot(b.rect.center)
                if self.player.rect.colliderect(b.rect):
                    self.player.hit()
                if b.type != "squidge":
                    b.collide(self.nomoveplatforms)
                    b.collide(self.spikes)
                    b.collide(self.springs)
                for s in self.string:
                    if s.rect.colliderect(b.rect):
                        b.kill()
                        BaddieBoom(b.rect.center, b.speed, b.type)
                        self.score += 100
                        for s in self.string:
                            s.life = 36
                        self.player.stop_attacking()
            for b in self.bosses:
                if self.player.rect.colliderect(b.rect) and not b.dead:
                    self.player.hit()
                if b.die_time <= 0 and b.dead and not self.explosions:
                    pygame.sprite.Sprite.kill(b)
                    self.next_level()
                if b.die_time > 0:
                    for s in self.shots:
                        s.kill()
                    if not random.randrange(4):
                        self.boom_sound.play()  
                    for b2 in self.baddies:
                        b2.kill()
                        BaddieBoom(b2.rect.center, b2.speed, b2.type)
                for s in self.string:
                    if s.rect.colliderect(b.rect):
                        b.hit()
                b.collide(self.nomoveplatforms)
                if not random.randrange(50) and not b.dead:
                    BaddieShot(b.rect.center)

            if self.player.rect.right > self.camera.world.w:
                if not self.bombs and self.lvl < 10:
                    self.next_level()
                else:
                    self.player.rect.right = self.camera.world.w

            for e in pygame.event.get():
                if e.type == QUIT:
                    sys.exit()
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.end()
                    if e.key == K_z:
                        self.player.jump()
                    if e.key == K_x:
                        self.player.shoot()
              
            if not self.running:
                return
            self.screen.blit(self.bg, ((-self.camera.rect.x/2)%640, 0))
            self.screen.blit(self.bg, ((-self.camera.rect.x/2)%640 + 640, 0))
            self.screen.blit(self.bg, ((-self.camera.rect.x/2)%640 - 640, 0))
            self.camera.draw_sprites(self.screen, self.sprites)
            self.draw_stats()
            for b in self.bosses:
                pygame.draw.rect(self.screen, (255, 0, 0), (170, 64, b.hp*60, 32))
                pygame.draw.rect(self.screen, (0, 0, 0), (170, 64, 300, 32), 1)
            for b in self.bombs:
                pygame.draw.rect(self.screen, (255, 255, 0), (16, 96 + 200, 32, -b.explode_time/10))
                pygame.draw.rect(self.screen, (0, 0, 0), (16, 96 + 200, 32, -200), 1)
            if not self.player.alive() and not self.playerdying:
                if self.lives <= 0:
                    self.gameover_screen()
                else:
                    self.show_death()
                    self.lives -= 1
                    self.redo_level()
            pygame.display.flip()
            if not self.running:
                return

    def draw_stats(self):
        for i in range(5):
            self.screen.blit(self.heart2, (16 + i*34, 16))
        for i in range(self.player.hp):
            self.screen.blit(self.heart1, (16 + i*34, 16))
        self.screen.blit(self.heroimg, (288, 16))
        lives = self.lives
        if lives < 0:
            lives = 0
        ren = self.font.render("%09d" % self.score, 1, (255, 255, 255))
        self.screen.blit(ren, (624-ren.get_width(), 16))
        ren = self.font.render("x%d" % lives, 1, (255, 255, 255))
        self.screen.blit(ren, (288+34, 24))
