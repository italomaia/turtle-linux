#! /usr/bin/env python

# Zombii - A Top-Down Shooter
# Copyright (C) 2009  <pymike93@gmail.com>
# Released under the GNU LGPL

import sys, os

import pygame
from pygame.locals import *

from gamelib.Objects import *
from gamelib.Utilities import *

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

Screen = (400, 320)
pygame.display.set_caption("Zombii by pymike")
Surface = pygame.display.set_mode(Screen)
pygame.mouse.set_visible(0)

Objects = Group()
Trees = Group()
Shots = Group()
Zombies = Group()
HPups = Group()
PLups = Group()
ROups = Group()
Explosions = Group()

Player.groups = [Objects]
Shot.groups = [Objects, Shots]
Tree.groups = [Objects, Trees]
Zombie.groups = [Objects, Zombies]
Explosion.groups = [Objects]
Flash.groups = [Objects]
Health.groups = [Objects, HPups]
Plasma.groups = [Objects, PLups]
Rocket.groups = [Objects, ROups]
BigExplosion.groups = [Objects, Explosions]

Map = [
"...............ZZZ........T........H",
"..T.....T.....T....T......ZZZ..T....",
"........Z...ZZ........H..T........T.",
"....T.....T.....T.....Z....TZ..T.Z..",
".T.....T.....T...ZZ..ZZ.T.....Z....R",
"..Z..Z....Z.....Z.P.........Z...T...",
".....Z.......Z..T..ZZT....T......T..",
"..T.....T.ZZ..T.......Z.....ZZZZZZ..",
".ZZ..Z.Z....ZZ.....T.Z.........T....",
".Z..T.....T.....T......Z..T........H",
".T.....T.....T.....R..........Z..T..",
"....Z.....ZZTZZ.T.....ZZ....T.......",
"T..ZZZ..P.ZZ.ZZ...H.T....T.......T..",
".P.T.........T........ZZZZZ.....ZZZ.",
"H..ZZZ..T.....Z...T...ZZ.ZZ...T.....",
".Z..............T.........T..ZZ..T..",
"..T...T..ZZZZ....ZZ....T............",
"..............T....T.ZZZZ...T...ZZZ.",
"ZZZZZZ.....Z...ZZ..................H",
]

Clock = pygame.time.Clock()
player = Player()
Font = pygame.font.Font(os.path.join("data", "FreeMono.ttf"), 24)
Score = 0
High = 1000
camera = Camera(player, (len(Map[0])*64, len(Map)*64))
Sounds["shoot"] = LoadSound("shoot.ogg")
Sounds["hurt"] = LoadSound("hurt.ogg")
Sounds["zombie-die"] = LoadSound("zombie-die.ogg")
Sounds["zombie-hurt"] = LoadSound("zombie-hurt.ogg")
Sounds["hp"] = LoadSound("hp.ogg")
Sounds["explosion"] = LoadSound("explosion.ogg")
pygame.mixer.music.load(os.path.join("data", "music.ogg"))
pygame.mixer.music.play(-1)
HowTo = LoadImage("howto.png")

x = y = 0
for row in Map:
    for col in row:
        if col == "T":
            Tree((x, y))
        if col == "Z":
            Zombie((x, y))
        if col == "H":
            Health((x, y))
        if col == "P":
            Plasma((x, y))
        if col == "R":
            Rocket((x, y))
        x += 64
    y += 64
    x = 0

def GetInput():
    key = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT or key[K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            x = 0
            for k in [K_UP, K_LEFT, K_DOWN, K_RIGHT]:
                if event.key == k:
                    player.pressed = [0, 0, 0, 0]
                    player.pressed[x] = 1
                x += 1
            if event.key == K_s:
                pygame.image.save(Surface, "screenie.png")
        if event.type == KEYUP:
            x = 0
            for k in [K_UP, K_LEFT, K_DOWN, K_RIGHT]:
                if event.key == k:
                    player.pressed = [0, 0, 0, 0]
                x += 1

def Update():
    Clock.tick(30)
    if Zombies:
        Objects.update()
    for t in Trees:
        player.collide(t.rect)
    for s in Shots:
        for t in Trees:
            if s.rect.colliderect(t.rect):
                s.kill()
        r = camera.Rect(s)
        if not r.left > 0 or not r.right < 400 or not r.top > 0 or not r.bottom < 320:
            s.kill()
        for z in Zombies:
            if s.rect.colliderect(z.rect):
                s.kill()
                z.hit(s.damage)
                Flash(s.rect.center)
                if not z.alive():
                    global Score
                    Score += 10
                    Sounds["zombie-die"].play()
                else:
                    Sounds["zombie-hurt"].play()
    for z in Zombies:
        z.move(player, camera)
        if player.rect.colliderect(z.rect) and player.hit_timer <= 0 and player.hp > 0:
            Sounds["hurt"].play()
            player.hp -= 1
            player.hit_timer = 10
        for e in Explosions:
            if e.rect.colliderect(z.rect):
                while z.alive():
                    z.hit()
                Score += 10
    for h in HPups:
        if player.rect.colliderect(h.rect) and player.alive() and not h.dead:
            player.hp += 5
            if player.hp > 10:
                player.hp = 10
            Sounds["hp"].play()
            h.dead = True
    for p in PLups:
        if player.rect.colliderect(p.rect) and player.alive() and not p.dead:
            player.powerup = 300
            player.ptype = "plasma"
            Sounds["hp"].play()
            p.dead = True
    for p in ROups:
        if player.rect.colliderect(p.rect) and player.alive() and not p.dead:
            player.powerup = 300
            player.ptype = "rocket"
            Sounds["hp"].play()
            p.dead = True
    if player.hp <= 0:
        if player.alive():
            Explosion(player.rect.center)
        player.kill()
        player.hit_timer = 0
        player.hp = 0
    player.rect.clamp_ip(camera.world)
    camera.update()

def Draw():
    Surface.fill(BackgroundColor)
    Objects.draw(Surface, camera)
    ren = Font.render("Score: %06d" % Score, 0, (127, 255, 127))
    Surface.blit(ren, (10, 10))
    ren = Font.render("HP: %02d/10" % player.hp, 0, (127, 255, 127))
    Surface.blit(ren, (390 - ren.get_width(), 10))
    if player.hit_timer > 0:
        if player.hit_timer > 8:
            Surface.blit(Pixelize(Surface, 80), (0, 0))
        if player.hit_timer > 6:
            Surface.blit(Pixelize(Surface, 40), (0, 0))
        if player.hit_timer > 4:
            Surface.blit(Pixelize(Surface, 20), (0, 0))
        if player.hit_timer > 2:
            Surface.blit(Pixelize(Surface, 10), (0, 0))
    if not player.alive():
        ren = Font.render("Game Over!", 0, (127, 255, 127))
        Surface.blit(ren, (200 - ren.get_width()/2, 160 - ren.get_height()/2))
        ren = Font.render("Your Score: %06d" % Score, 0, (127, 255, 127))
        Surface.blit(ren, (200 - ren.get_width()/2, 180 - ren.get_height()/2))
    elif not Zombies:
        ren = Font.render("You Win!", 0, (127, 255, 127))
        Surface.blit(ren, (200 - ren.get_width()/2, 160 - ren.get_height()/2))
        ren = Font.render("Your Score: %06d" % Score, 0, (127, 255, 127))
        Surface.blit(ren, (200 - ren.get_width()/2, 180 - ren.get_height()/2))
    pygame.draw.rect(Surface, [105, 211, 105], [9, 39, len(Map[0])*2 + 2, len(Map)*2 + 2])
    pygame.draw.rect(Surface, [59, 119, 59], [10, 40, len(Map[0])*2, len(Map)*2])
    for z in Zombies:
        Surface.set_at([int(z.rect.x/64)*2 + 10, int(z.rect.y/64)*2 + 40], [105, 211, 105])
    Surface.set_at([int(player.rect.x/64)*2 + 10, int(player.rect.y/64)*2 + 40], [255, 255, 255])
    pygame.draw.rect(Surface, [127, 255, 127], [10, 250, 30, -150], 1)
    pygame.draw.rect(Surface, [127, 255, 127], [10, 250, 30, -player.powerup/2])
    pygame.display.flip()

def main():
    stop = False
    while not stop:
        key = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type == QUIT or key[K_ESCAPE]:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_SPACE:
                stop = True
        Surface.fill((34, 69, 34))
        Surface.blit(HowTo, (0, 0))
        pygame.display.flip()
    while True:
        GetInput()
        Update()
        Draw()

if __name__ == '__main__':
    main()
