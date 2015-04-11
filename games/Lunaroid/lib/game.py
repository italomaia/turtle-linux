import retrogamelib as rgl
import sys
from retrogamelib.constants import *
from objects import *
from engine import *

class Game(object):
    
    def __init__(self):
        
        # Setup the display
        rgl.display.init(2.0, "Lunaroid")
        
        # Create some groups to hold objects
        self.objects = rgl.gameobject.Group()
        self.shots = rgl.gameobject.Group()
        self.badshots = rgl.gameobject.Group()
        self.baddies = rgl.gameobject.Group()
        self.powerups = rgl.gameobject.Group()
        self.missiles = rgl.gameobject.Group()
        self.bosses = rgl.gameobject.Group()
        self.explosions = rgl.gameobject.Group()
        
        # Assign some groups to the global objects' `groups` attributes
        Player.groups = [self.objects]
        Wall.groups = [self.objects]
        Shot.groups = [self.objects, self.shots]
        BadShot.groups = [self.objects, self.badshots]
        Rusher.groups = [self.objects, self.baddies]
        Bat.groups = [self.objects, self.baddies]
        Crawly.groups = [self.objects, self.baddies]
        Explosion.groups = [self.objects, self.explosions]
        Squatter.groups = [self.objects, self.baddies]
        HealthUp.groups = [self.objects, self.powerups]
        Door.groups = [self.objects]
        Missile.groups = [self.objects, self.missiles]
        Boss.groups = [self.objects, self.baddies, self.bosses]
        
        # Create some starting objects
        self.engine = Engine(self)
        self.player = Player(self.engine)
        self.engine.parse_level()
        self.font = rgl.font.Font(NES_FONT, (255, 255, 255))
        rgl.util.play_music("data/metroid.mod", -1)
        self.boss_mode = False
        self.move_view(0, 0)
    
    def move_view(self, dx, dy):
        for obj in self.objects:
            if obj != self.player:
                obj.kill()
        self.engine.pos[0] += dx
        self.engine.pos[1] += dy
        self.engine.parse_level()
        if len(self.bosses) == 1:
            self.boss_mode = True
        else:
            self.boss_mode = False
    
    def loop(self):
        while 1:
            
            # Update and cap framerate
            rgl.clock.tick()
            self.update()
            
            # Handle input
            self.handle_input()
            
            # Drawing
            self.draw()
    
    def update(self):
        for obj in self.objects:
            obj.update()
        for baddie in self.baddies:
            baddie.do_ai(self.player)
            if baddie.rect.colliderect(self.player.rect):
                self.player.hit()
        for s in self.shots:
            for b in self.baddies:
                if s.rect.colliderect(b.rect):
                    b.hit()
                    s.kill()
        for s in self.badshots:
            if s.rect.colliderect(self.player.rect):
                s.kill()
                self.player.hit()
        for p in self.powerups:
            if self.player.rect.colliderect(p.rect):
                p.kill()
                self.player.energy += 15
                if self.player.energy > 100:
                    self.player.energy = 100
                rgl.util.play_sound("data/health.ogg")
        for m in self.missiles:
            if self.player.rect.colliderect(m.rect):
                m.kill()
                rgl.util.play_sound("data/missiles.ogg")
                self.player.has_missile = True
    
    def handle_input(self):
        
        # Have rgl check and handle the input for us
        rgl.button.handle_input()
        
        # Reset some of the player's variables
        self.player.moving = False
        self.player.lookup = False
        
        # Move around
        if self.player.alive():
            if rgl.button.is_held(LEFT):
                self.player.move(-3, 0)
            if rgl.button.is_held(RIGHT):
                self.player.move(3, 0)
            if rgl.button.is_held(UP):
                self.player.lookup = True
            
            # Make the player jump if you press the A Button/Z Key
            if rgl.button.is_pressed(A_BUTTON):
                self.player.jump()
            if rgl.button.is_held(A_BUTTON):
                self.player.jump_accel = self.player.jump_accel_slow
            else:
                self.player.jump_accel = self.player.jump_accel_fast
        
            # Shoot if you press the B Button/X key
            if rgl.button.is_pressed(B_BUTTON):
                self.player.shoot()
    
        # Create a new area if you go off the screen
        if self.player.rect.right > 256:
            self.player.rect.left = 16
            self.move_view(1, 0)
        if self.player.rect.left < 0:
            self.player.rect.right = 240
            self.move_view(-1, 0)
        if self.player.rect.bottom > 240:
            self.player.rect.top = 0
            self.move_view(0, 1)
        if self.player.rect.top < 0:
            self.player.rect.bottom = 240
            self.move_view(0, -1)
    
    def draw(self):
        
        # Get the surface to draw to
        surface = rgl.display.get_surface()
        
        # Do basic pygame drawing
        surface.fill((0, 0, 0))
        
        # Draw all the objects
        for obj in self.objects:
            obj.draw(surface)
        
        ren = self.font.render("Energy %02d" % self.player.energy)
        surface.blit(ren, (10, 10))
        
        if not self.player.alive():
            ren = self.font.render("game over")
            surface.blit(ren, (128 - ren.get_width()/2, 120 - ren.get_height()/2))
        if self.boss_mode and len(self.bosses) <= 0 and len(self.explosions) <= 0:
            for obj in self.objects:
                obj.draw(surface)
                obj.update()
            pygame.time.wait(1000)
            surface.fill((0, 0, 0))
            ren = self.font.render("you defeated the")
            surface.blit(ren, (128 - ren.get_width()/2, 110 - ren.get_height()/2))
            ren = self.font.render("mama brain")
            surface.blit(ren, (128 - ren.get_width()/2, 120 - ren.get_height()/2))
            ren = self.font.render("and escaped from the moon")
            surface.blit(ren, (128 - ren.get_width()/2, 140 - ren.get_height()/2))
            ren = self.font.render("riding it piggy back")
            surface.blit(ren, (128 - ren.get_width()/2, 150 - ren.get_height()/2))
            rgl.display.update()
            pygame.time.wait(4000)
            surface = rgl.display.get_surface()
            surface.fill((0, 0, 0))
            ren = self.font.render("the end!")
            surface.blit(ren, (128 - ren.get_width()/2, 120 - ren.get_height()/2))
            rgl.display.update()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()
        
        # Update the display
        rgl.display.update()
