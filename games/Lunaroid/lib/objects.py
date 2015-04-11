import pygame, random
import retrogamelib as rgl
rgl.util.set_global_sound_volume(0.5)

def flip_images(images):
    new = []
    for i in images:
        new.append(pygame.transform.flip(i, 1, 0))
    return new

def scale_images(images, scale):
    new = []
    for i in images:
        new.append(pygame.transform.scale(i, (int(i.get_width()*scale), int(i.get_height()*scale))))
    return new

class Object(rgl.gameobject.Object):
    
    def __init__(self, engine):
        rgl.gameobject.Object.__init__(self, self.groups)
        self.engine = engine
        self.offset = (0, 0)
    
    def move(self, dx, dy):
        if dx != 0:
            self.move_one_axis(dx, 0)
        if dy != 0:
            self.move_one_axis(0, dy)

    # Move one axis and check for collisions
    def move_one_axis(self, dx, dy):
        
        # Raise an error if you try to move both the axes
        if dx != 0 and dy != 0:
            raise SystemExit, "You may only move one axis at a time."
        
        # Move the rect
        self.rect.move_ip(dx, dy)
        
        # Get all the tiles you're colliding with
        tiles = self.check_collisions()
        
        # Collision response
        for t in tiles:
            if t.rect.colliderect(self.rect):
                self.on_collision(dx, dy, t)
    
    # Called when a collision occurs
    def on_collision(self, dx, dy, tile):
        self.respond(dx, dy, tile)
    
    def respond(self, dx, dy, t):
        if dx > 0:
            self.rect.right = t.rect.left
        if dx < 0:
            self.rect.left = t.rect.right
        if dy > 0:
            self.rect.bottom = t.rect.top
        if dy < 0:
            self.rect.top = t.rect.bottom
    
    def draw(self, surface):
        surface.blit(self.image, self.rect.move(*self.offset))
        
    def check_collisions(self):
        tiles = self.engine.tiles
        collide_tiles = []
        
        #size = 16x16
        pos_tile = int(self.rect.centerx / 16), int(self.rect.bottom/16)
      
        #This causes the top half of the player to not register a hit, if you want that, then
        #do pos_tile +/- 2
        for x in xrange(pos_tile[0]-2, pos_tile[0]+2):
            for y in xrange(pos_tile[1]-2, pos_tile[1]+2):
                if x < 0 or x >= len(tiles[0]) or\
                   y < 0 or y >= len(tiles):
                    continue

                tile = tiles[y][x]
                if not tile:
                    continue
                if tile.rect.colliderect(self.rect):
                    collide_tiles.append(tile)
        
        return collide_tiles

class Player(Object):
    
    def __init__(self, engine):
        Object.__init__(self, engine)
        li = rgl.util.load_image
        
        self.right_legs = [li("data/spaceman-legs-%d.png" % i) for i in range(1, 6)]
        self.left_legs = flip_images(self.right_legs)
        self.right_tops = [li("data/spaceman-top-%d.png" % i) for i in range(1, 3)]
        self.left_tops = flip_images(self.right_tops)
        self.legs = self.right_legs
        self.tops = self.right_tops
        
        self.top_image = self.tops[0]
        self.legs_image = self.legs[0]
        self.rect = pygame.Rect(0, 0, 10, 28)
        self.rect.midtop = (128, 16)
        self.offset = (-11, -4)
        self.z = 1
        self.energy = 100
        self.flicker = 50
        
        self.jump_speed = 0.0
        self.jump_accel_slow = 0.35
        self.jump_accel_fast = 0.9
        self.jump_accel = self.jump_accel_slow
        self.max_fall = 8.0
        self.jump_force = 8.0
        self.jumping = True
        
        self.facing = 1
        self.frame = 0
        self.moving = False
        self.lookup = False
        self.has_missile = False
        
    def draw(self, surface):
        if self.flicker <= 0:
            self.draw_imgs(surface)
        else:
            if self.flicker % 3 < 2:
                self.draw_imgs(surface)
    
    def draw_imgs(self, surface):
        surface.blit(self.legs_image, self.rect.move(self.offset))
        surface.blit(self.top_image, self.rect.move(self.offset[0], self.offset[1]-14))
    
    def hit(self, damage=5):
        if self.flicker <= 0:
            self.flicker = 10
            self.energy -= damage
            rgl.util.play_sound("data/hit.ogg")
            if self.energy <= 0:
                self.kill()
                Explosion(self.engine, self.rect.center, 1.5)
        
    def update(self):
        
        # Increase the animation frame
        self.frame += 1
        
        # Move the Y axis by the jump speed, and apply gravity
        if self.jump_speed < self.max_fall:
            self.jump_speed += self.jump_accel
        self.move(0, self.jump_speed)
        
        # If our jump velocity is greater than a certain amount, we must
        # have fallen off a cliff - so set the jumping value to true.
        if self.jump_speed > self.jump_accel:
            self.jumping = True
        
        # Set the images value to left or right depending on which way we're facing
        if self.facing > 0:
            self.legs = self.right_legs
            self.tops = self.right_tops
        else:
            self.legs = self.left_legs
            self.tops = self.left_tops
        
        # Set the default frame to zero
        frame = 0
        
        # If we're moving, set the frame to the moving animation frame
        if self.moving:
            frame = self.frame/2%3 + 1
        
        # If we're jumping, override the previous moving animation and set 
        # the frame to the jump one.
        if self.jumping:
            frame = 4
        
        # Set the image to the animation frame
        self.legs_image = self.legs[frame]
        self.top_image = self.tops[0]
        if self.lookup:
            self.top_image = self.tops[1]
    
        self.flicker -= 1
    
    def on_collision(self, dx, dy, tile):
        if isinstance(tile, Door):
            if tile.open == False:
                self.respond(dx, dy, tile)
        else:
            self.respond(dx, dy, tile)
        if dy > 0:
            self.jump_speed = 0
            self.jumping = False
        if dy < 0:
            self.jump_speed = 0

    def jump(self):
        if not self.jumping:
            rgl.util.play_sound("data/jump.ogg")
            self.jumping = True
            self.jump_speed = -self.jump_force
    
    def shoot(self):
        if self.lookup:
            Shot(self.engine, self.rect.midtop, 0, self.has_missile)
        else:
            y = self.rect.top + 7
            if self.facing > 0:
                Shot(self.engine, (self.rect.centerx, y), 90, self.has_missile)
            else:
                Shot(self.engine, (self.rect.centerx, y), 270, self.has_missile)
    
    def move(self, dx, dy):
        Object.move(self, dx, dy)
        if dx != 0:
            self.moving = True
        if dx < 0:
            self.facing = -1
        elif dx > 0:
            self.facing = 1

class Wall(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/wall.png")
        self.rect = self.image.get_rect(topleft=pos)
        self.on_end = [False, False, False, False]

class Missile(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/missile.png")
        self.rect = self.image.get_rect(topleft=pos)

class Door(Object):
    
    def __init__(self, engine, pos, facing, hard=False):
        Object.__init__(self, engine)
        if not hard:
            self.images = [rgl.util.load_image("data/door-%d.png" % i) for i in range(1, 5)]
        else:
            self.images = [rgl.util.load_image("data/door-hard-%d.png" % i) for i in range(1, 5)]
        self.facing = facing
        if self.facing > 0:
            self.images = flip_images(self.images)
        self.image = self.images[0]
        self.offset = (-4*facing, 0)
        self.frame = 0
        self.rect = self.image.get_rect(topleft=pos)
        self.on_end = [False, False, True, True]
        self.open = False
        self.z = 2
        self.hard = hard
    
    def hit(self):
        self.open = True
    
    def update(self):
        if self.open and self.frame < 4:
            self.image = self.images[self.frame]
            self.frame += 1
        if self.open and self.frame >= 4:
            self.image = self.images[3]
            self.frame = 4

class Shot(Object):
    
    def __init__(self, engine, pos, angle, missile=0):
        Object.__init__(self, engine)
        if missile:
            self.image = rgl.util.load_image("data/missile.png")
        else:
            self.image = rgl.util.load_image("data/shot.png")
        self.rect = self.image.get_rect(center=pos)
        self.missile = missile
        self.dx = self.dy = 0
        if angle == 0:
            self.dy = -1
        elif angle == 90:
            self.dx = 1
        elif angle == 270:
            self.dx = -1
        if angle == 0:
            angle = 180
        self.image = pygame.transform.rotate(self.image, angle-90)
        self.rect = self.image.get_rect(center = self.rect.center)
        self.rect.x += 16*self.dx
        self.rect.y += 16*self.dy
        self.speed = 8
        self.life = 10
        self.move(0.1, 0)
        if not self.missile:
            rgl.util.play_sound("data/shoot.ogg")
        else:
            rgl.util.play_sound("data/missile.ogg")
    
    def update(self):
        self.move(self.dx*self.speed, self.dy*self.speed)
        self.life -= 1
        if self.life <= 0:
            self.kill()
    
    def on_collision(self, dx, dy, tile):
        self.kill()
        if isinstance(tile, Door):
            if tile.hard:
                if self.missile == True:
                    tile.hit()
            else:
                tile.hit()

class Rusher(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.left_images = [rgl.util.load_image("data/rusher-%d.png" % i) for i in range(1, 4)]
        self.right_images = flip_images(self.left_images)
        self.images = self.left_images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.dx = random.choice([-1, 1])
        if self.dx > 0:
            self.images = flip_images(self.images)
        self.speed = 1
        self.frame = 0
        self.hitframe = 0
        self.hp = 3
    
    def update(self):
        self.hitframe -= 1
        if self.hitframe <= 0:
            self.move(self.dx*self.speed, 4)
        self.image = self.images[self.frame/4%2]
        if self.hitframe > 0:
            self.image = self.images[2]
        if self.dx > 0:
            self.images = self.right_images
        else:
            self.images = self.left_images
        self.frame += 1
    
    def on_collision(self, dx, dy, tile):
        self.respond(dx, dy, tile)
        start_dx = self.dx
        if self.rect.bottom >= tile.rect.top and dy > 0:
            if tile.on_end[2] == True and self.rect.left <= tile.rect.left:
                self.dx = abs(start_dx)
            elif tile.on_end[3] == True and self.rect.right >= tile.rect.right:
                self.dx = -abs(start_dx)
        else:
            if tile.on_end[2] or tile.on_end[3] and dx != 0:
                if self.rect.centerx < tile.rect.centerx:
                    self.dx = -abs(start_dx)
                    self.rect.right = tile.rect.left
                elif self.rect.centerx > tile.rect.centerx:
                    self.dx = abs(start_dx)
                    self.rect.left = tile.rect.right

    def hit(self):
        if self.hitframe <= 0:
            self.hitframe = 3
            self.hp -= 1
            rgl.util.play_sound("data/hit.ogg")
            if self.hp <= 0:
                self.kill()
                if not random.randrange(5):
                    HealthUp(self.engine, self.rect.center)
                Explosion(self.engine, self.rect.center, 1.5)
    
    def do_ai(self, player):
        pass

class Bat(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.images = [rgl.util.load_image("data/bat-%d.png" % i) for i in range(1, 5)]
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.frame = 0
        self.hitframe = 0
        self.hp = 3
        self.dy = 0
    
    def update(self):
        self.hitframe -= 1
        if self.hitframe <= 0:
            self.move(0, self.dy)
        self.image = self.images[self.frame/4%2 + 1]
        if self.dy == 0:
            self.image = self.images[0]
        if self.hitframe > 0:
            self.image = self.images[3]
        self.frame += 1
    
    def on_collision(self, dx, dy, tile):
        self.respond(dx, dy, tile)
        self.dy = 0

    def hit(self):
        if self.hitframe <= 0:
            self.hitframe = 3
            self.hp -= 1
            rgl.util.play_sound("data/hit.ogg")
            if self.hp <= 0:
                self.kill()
                if not random.randrange(125):
                    HealthUp(self.engine, self.rect.center)
                Explosion(self.engine, self.rect.center)

    def do_ai(self, player):
        if player.rect.left < self.rect.right and player.rect.right > self.rect.left:
            self.dy = 5

class Crawly(Object):
    
    def __init__(self, engine, pos, side):
        Object.__init__(self, engine)
        self.left_images = [rgl.util.load_image("data/crawly-%d.png" % i) for i in range(1, 4)]
        self.right_images = flip_images(self.left_images)
        self.images = self.left_images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.dy = random.choice([-1, 1])
        self.speed = 1
        self.frame = 0
        self.hitframe = 0
        self.hp = 3
        self.side = side
    
    def update(self):
        self.hitframe -= 1
        if self.hitframe <= 0:
            self.move(1*self.side, self.dy*self.speed)
        self.image = self.images[self.frame/4%2]
        if self.hitframe > 0:
            self.image = self.images[2]
        if self.side > 0:
            self.images = self.right_images
        else:
            self.images = self.left_images
        self.frame += 1
    
    def on_collision(self, dx, dy, tile):
        self.respond(dx, dy, tile)
        start_dy = self.dy
        if dx != 0:
            if tile.on_end[0] and self.rect.top <= tile.rect.top+1:
                self.dy = abs(start_dy)
            elif tile.on_end[1]:
                self.dy = -abs(start_dy)
        else:
            if tile.on_end[0] or tile.on_end[1] and dy != 0:
                if self.rect.centery < tile.rect.centery:
                    self.dy = -abs(start_dy)
                    self.rect.bottom = tile.rect.top
                elif self.rect.centery > tile.rect.centery:
                    self.dy = abs(start_dy)
                    self.rect.top = tile.rect.bottom

    def hit(self):
        if self.hitframe <= 0:
            self.hitframe = 3
            self.hp -= 1
            rgl.util.play_sound("data/hit.ogg")
            if self.hp <= 0:
                if not random.randrange(5):
                    HealthUp(self.engine, self.rect.center)
                self.kill()
                Explosion(self.engine, self.rect.center)
    
    def do_ai(self, player):
        pass

class Explosion(Object):
    
    def __init__(self, engine, pos, scale=1.0):
        Object.__init__(self, engine)
        self.images = [rgl.util.load_image("data/cloud-%d.png" % i) for i in range(1, 5)]
        self.images = scale_images(self.images, scale)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.frame = 0
        rgl.util.play_sound("data/explode.ogg")
    
    def update(self):
        self.image = self.images[self.frame/2%4]
        self.frame += 1
        if self.frame > 8:
            self.kill()

class BadShot(Object):
    
    def __init__(self, engine, pos, angle):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/shot.png")
        self.rect = self.image.get_rect(center=pos)
        self.dx = self.dy = 0
        if angle == 0:
            self.dy = -1
        elif angle == 90:
            self.dx = 1
        elif angle == 270:
            self.dx = -1
        self.rect.x += 16*self.dx
        self.rect.y += 16*self.dy
        self.speed = 8
        self.life = 10
        self.move(0.1, 0)
    
    def update(self):
        self.move(self.dx*self.speed, self.dy*self.speed)
        self.life -= 1
        if self.life <= 0:
            self.kill()
    
    def on_collision(self, dx, dy, tile):
        self.kill()

class HealthUp(Object):
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.reg_image = pygame.Surface((13, 13)).convert()
        self.blink_image = self.reg_image.copy()
        self.reg_image.fill((255,0,0))
        self.image = self.reg_image
        self.rect = self.image.get_rect(center = pos)

        self.life = 150

    def update(self):
        self.life -= 1
        if self.life < 50:
            if self.life % 5 == 0:
                if self.image == self.reg_image:
                    self.image = self.blink_image
                else:
                    self.image = self.reg_image
        if self.life <= 0:
            self.kill()

    def on_collision(self, dx, dy, tile):
        self.kill()

class Squatter(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.images = [rgl.util.load_image("data/squatter-%d.png" % i) for i in range(1, 5)]
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.frame = 0
        self.hitframe = 0
        self.hp = 3
        self.dy = 0

        self.shot_count = 0
    
    def update(self):
        self.hitframe -= 1
        self.image = self.images[self.frame/8%2]
        if self.hitframe > 0:
            self.image = self.images[3]
        self.frame += 1
    
    def on_collision(self, dx, dy, tile):
        self.respond(dx, dy, tile)
        self.dy = 0

    def hit(self):
        if self.hitframe <= 0:
            self.hitframe = 3
            self.hp -= 1
            rgl.util.play_sound("data/hit.ogg")
            if self.hp <= 0:
                if not random.randrange(5):
                    HealthUp(self.engine, self.rect.center)
                self.kill()

    def do_ai(self, player):
        if self.rect.colliderect(player.rect.move(self.rect.left-player.rect.left, 0)):
            self.shot_count += 1
            if self.shot_count >= 15:
                self.shot_count = 0
                if self.rect.centerx < player.rect.centerx:
                    angle = 90
                else:
                    angle = 270
                BadShot(self.engine, self.rect.center, angle)
        else:
            self.shot_count = 0

class Boss(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.images = [rgl.util.load_image("data/boss-%d.png" % i) for i in range(1, 4)]
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.frame = 0
        self.hitframe = 0
        self.hp = 20
        self.dy = 0

        self.shot_count = 0
    
    def update(self):
        self.hitframe -= 1
        self.image = self.images[self.frame/8%2]
        if self.hitframe > 0:
            self.image = self.images[2]
        self.frame += 1
    
    def on_collision(self, dx, dy, tile):
        self.respond(dx, dy, tile)
        self.dy = 0

    def hit(self):
        if self.hitframe <= 0:
            self.hitframe = 3
            self.hp -= 1
            rgl.util.play_sound("data/hit.ogg")
            if self.hp <= 0:
                self.kill()
                Explosion(self.engine, self.rect.center, 3.0)

    def do_ai(self, player):
        if self.rect.colliderect(player.rect.inflate(10,10).move(self.rect.left-player.rect.left, 0)):
            self.shot_count += 1
            if self.shot_count >= 20:
                self.shot_count = 0
                if self.rect.centerx < player.rect.centerx:
                    angle = 90
                else:
                    angle = 270
                for x in xrange(5):
                    BadShot(self.engine, (self.rect.centerx, self.rect.top+16+x*8), angle)
        else:
            self.shot_count = 0
