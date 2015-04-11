# Python imports
import pygame
import data

# Game-related imports
from constants import Constants
from game_object import GameObject

class Girl(GameObject):
    """ This is our main player object, which inherits from the
        generic GameObject class. """
    def __init__(self):
        GameObject.__init__(self)
        self.load_anims("girl", 5)
        self.magic_box = pygame.rect.Rect((18, 2), (18, 46))
        self.delay = Constants.GIRL_WAIT
        
        # Are there any modifiers affecting the behavior of the object?
        # 0 - normal, 1 - anti-gravity, 2 - ice, 4 - fire
        self.modifier = 0
        self.modifier_timer = 0
        
        # This is needed for providing sounds for player effects
        self.sound_player = None
        
    def check_ceiling(self, mask):
        """ Probably should also check the ceiling to make sure that the player
            hitting something bad causes something bad. Just a thought. """
        # Get the starting x position, the middle x position, and the ending x position
        sx = self.rect.left + self.magic_box.left
        mx = self.rect.left + self.magic_box.left + (self.magic_box.width / 2)
        ex = self.rect.left + self.magic_box.right
        # Antigravity or not?
        if self.modifier & Constants.ANTIGRAVITY == Constants.ANTIGRAVITY:
            y = self.rect.top + self.magic_box.top + self.magic_box.height + 10
        else:
            y = self.rect.top + self.magic_box.top - 10
        if (sx >= 0 and ex < 600 and y >= 0 and y < 600):
            r1 = (int)(mask.get_at((sx, y)) != (0, 0, 0, 255))
            r2 = (int)(mask.get_at((mx, y)) != (0, 0, 0, 255))
            r3 = (int)(mask.get_at((ex, y)) != (0, 0, 0, 255))
            if (r1, r2, r3) != (0, 0, 0):
                for x in (sx, ex, mx):
                    (r, g, b, a) = mask.get_at((x, y))
                    if (r < 50 and g >= 200 and b < 50):
                        # Spikes/harmful floor (green floor)
                        self.living = False
                        break
                    elif (r >= 225 and g < 50 and b >= 225):
                        # Stage Exit (magenta (Seriously, T-Mobile. What ze crap.))
                        self.done = True
                    elif (r >= 225 and g >= 225 and b < 50):
                        # Play a wooosh sound
                        self.sound_player.play_swoosh()
                        # Anti-gravity (yellow)
                        if self.modifier & Constants.ANTIGRAVITY == Constants.ANTIGRAVITY:
                            self.modifier ^= Constants.ANTIGRAVITY
                            self.rect.top -= 35
                            break
                        else:
                            self.rect.top += 35
                            self.modifier |= Constants.ANTIGRAVITY
                            break
                    else:
                        # Probably floor. We can't push the player down 10 if
                        # there is floor 10 spaces below, so check that first
                        if self.modifier & Constants.ANTIGRAVITY == Constants.ANTIGRAVITY:
                            cy = self.rect.top + self.magic_box.top
                            my = -10
                        else:
                            cy = self.rect.top + self.magic_box.bottom
                            my = +10
                        try:
                            (r, g, b, a) = mask.get_at((mx, cy + my))
                            if (r < 50 and g < 50 and b < 50):
                                self.rect.top += my
                                break
                        except:
                            # Don't really need to do anything here; just keep
                            # the exception from halting gameplay.
                            pass
        else:
            if ((self.rect.top + self.magic_box.top) >= 600) or (self.rect.bottom <= 0):
                self.living = False

    def find_walkable(self, mask):
        """ This method checks to see if there is a walkable mask beneath the
            object. It checks at the start of the magic_box, checks the middle
            of the magic box, and then checks the end of the magic box. """
        # Get the starting x position, the middle x position, and the ending x position
        (sx, ex, mx) = (self.rect.left + self.magic_box.left, self.rect.left + self.magic_box.left +  self.magic_box.width, self.rect.left + self.magic_box.left + (self.magic_box.width / 2))
        # Get the y position
        # OH SNAP ANTIGRAVITY AGAIN
        if self.modifier & Constants.ANTIGRAVITY == Constants.ANTIGRAVITY:
            y = self.rect.top + self.magic_box.top - 1
            extra = +20
        else:
            y = self.rect.top + self.magic_box.top + self.magic_box.height + 1
            extra = -20
        # Make sure we're not trying to check out some non-existant pixels.
        if (sx >= 0 and ex < 600 and y >= 0 and y < 600):
            # This is something I did to make my life easier; if it's a black
            # pixel on the mask, then treat it as nothing.
            r1 = (int)(mask.get_at((sx, y)) != (0, 0, 0, 255))
            r2 = (int)(mask.get_at((mx, y)) != (0, 0, 0, 255))
            r3 = (int)(mask.get_at((ex, y)) != (0, 0, 0, 255))
            
            rb1 = (int)(mask.get_at((sx, y + extra)) != (0, 0, 0, 255))
            rb2 = (int)(mask.get_at((mx, y + extra)) != (0, 0, 0, 255))
            rb3 = (int)(mask.get_at((ex, y + extra)) != (0, 0, 0, 255))
            if ((r1, r2, r3) == (0, 0, 0) and (rb1, rb2, rb3) == (0, 0, 0)):
                if self.yvel >= 1:
                    # This allows a gradual falling instead of an instant
                    # 7-space fall and fixes a bug with the player randomly
                    # falling through the floor
                    self.yvel += 1
                    if self.yvel > Constants.GRAVITY:
                        # Let's make sure our player doesn't fall tooooo fast.
                        self.yvel = Constants.GRAVITY
                    # GRAVITY: BEHOLD
                    self.fall_height += self.yvel
                else:
                    # Reset to a happy falling value
                    self.yvel = 1
            else:
                # Ok, we're not going to fall here.
                self.yvel = 0
                # If we've fallen from too high up or fallen through the floor,
                # then it's time to die.
                if self.fall_height > 200 or (self.rect.top + self.magic_box.top) >= 600:
                    self.living = False
                # If we've fallen by more than 10, make a thud noise
                if self.fall_height >= 10:
                    self.sound_player.play_thud()
                # Reset the fall height.
                self.fall_height = 0
                # Check to see if we need to adjust the player's height and
                # make them travel upwards.
                color = mask.get_at((mx, y))
                while color != (0, 0, 0, 255):
                    # Put the conditions for different floor tiles here
                    (r, g, b, a) = color
                    if (r < 50 and g >= 225 and b < 50):
                        # Spikes/harmful floor (green floor)
                        self.living = False
                    elif (r >= 225 and g < 50 and b >= 225):
                        # Stage Exit (magenta (Seriously, T-Mobile. What ze crap.))
                        self.done = True
                    elif (r < 50 and g < 50 and b >= 200):
                        # Play an ice noise
                        self.sound_player.play_swoosh()
                        # Ice on the ground (blue)
                        self.modifier |= Constants.ICE
                    elif (r >= 225 and g < 50 and b < 50):
                        # Play a fire noise
                        self.sound_player.play_fire()
                        # Fire on the ground (red)
                        self.modifier |= Constants.FIRE
                        self.modifier_timer = 10
                        self.rect.top -= 32
                        break
                    elif (r >= 225 and g >= 225 and b < 50):
                        # Play a wooosh sound
                        self.sound_player.play_swoosh()
                        # Anti-gravity (yellow)
                        if self.modifier & Constants.ANTIGRAVITY == Constants.ANTIGRAVITY:
                            self.modifier ^= Constants.ANTIGRAVITY
                            self.rect.top += 35
                            break
                        else:
                            self.rect.top -= 35
                            self.modifier |= Constants.ANTIGRAVITY
                            break
                    elif (r >= 225 and g >= 225 and b >= 225):
                        # Regular floor (white)
                        if self.modifier & Constants.ICE == Constants.ICE:
                            # Ice -> Regular
                            self.modifier ^= Constants.ICE
                    if self.modifier & Constants.ANTIGRAVITY == Constants.ANTIGRAVITY:
                        y += 1
                    else:
                        y -= 1
                    self.yvel -= 1
                    color = mask.get_at((mx, y))
        else:
            # We may have fallen through the floor. TIME TO DIE.
            if ((self.rect.top + self.magic_box.top) >= 600) or (self.rect.bottom <= 0) :
                self.living = False

    def find_wall(self, mask):
        """ Determine if we're walking into something and should turn around,
            or if we're walking into spikes or an exit for the stage. """
        if self.direction == 0:
            # We're walking right, so check the right-most spot
            x = self.rect.left + self.magic_box.left + self.magic_box.width + 1
        else:
            # We're walking left, so check the left-most spot
            x = self.rect.left + self.magic_box.left - 1
        if self.modifier & Constants.ANTIGRAVITY == Constants.ANTIGRAVITY:
            sy = self.rect.top + self.magic_box.top + self.magic_box.height
            my = (int)(self.rect.top + self.magic_box.top + (self.magic_box.height / 1.5))
            ey = self.rect.top + self.magic_box.top + (self.magic_box.height / 2)
        else:
            sy = self.rect.top + self.magic_box.top
            my = self.rect.top + self.magic_box.top + (self.magic_box.height / 4)
            ey = self.rect.top + self.magic_box.top + (self.magic_box.height / 2)
        # Create a tuple of the y positions to check and loop through them
        y_positions = (sy, my, ey)
        for y in y_positions:
            # Let's not check beyond where we can
            if (x >= 0 and x < mask.get_rect().width) and (y >= 0 and y < mask.get_rect().height):
                if mask.get_at((x, y)) != (0, 0, 0, 255):
                    (r, g, b, a) = mask.get_at((x, y))
                    if (r >= 225 and g < 50 and b >= 225):
                        # Doorway (magenta color (T-mobile, don't sue me!))
                        self.done = True
                    elif (r < 50 and g >= 200 and b < 50):
                        # Spikes/harmful objects (green color)
                        self.living = False
                    else:
                        # Unspecified object (likely a wall), reverse direction
                        self.direction = (int)(not self.direction)

    def update(self, mask):
        """ Update the animations/position of the player object. """
        if self.delay > 0:
            self.delay -= 1
            return
        self.check_ceiling(mask)
        self.find_walkable(mask)
        self.find_wall(mask)
        # Move in the appropriate direction.
        if self.direction == 0:
            self.rect.left += Constants.GIRL_SPEED
            if self.rect.right >= Constants.SCREEN_WIDTH:
                # Hit the side of the screen, change directions!
                self.direction = 1
        else:
            self.rect.left -= Constants.GIRL_SPEED
            if self.rect.left <= 0:
                # Hit the side of the screen, change directions!
                self.direction = 0
        # Fall/climb
        # GRAVITY MODIFIER (rock on)
        yvel = self.yvel
        # FIRE MODIFIER (flame on)
        if self.modifier & Constants.FIRE == Constants.FIRE:
            yvel -= 10 + (10 - self.modifier_timer)
            self.modifier_timer -= 1
            if self.modifier_timer <= 0:
                self.modifier ^= Constants.FIRE
        if self.modifier & Constants.ANTIGRAVITY == Constants.ANTIGRAVITY:
            yvel *= -1
        self.rect.top += yvel
        # ICE MODIFIER (...freeze on?)
        if self.modifier & Constants.ICE == Constants.ICE:
            if self.direction == 0:
                self.rect.left += 10
            else:
                self.rect.left -= 10
            self.image = self.animations[0]
        else:
            # Animate
            self.frame += 1
            if self.frame >= 20:
                self.frame = 0
            self.image = self.animations[(self.frame + 5) / 5]
        # We need to flip the image horizontally depending on what direction
        # we're moving in; the animations all face right.
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.modifier & Constants.ANTIGRAVITY == Constants.ANTIGRAVITY:
            self.image = pygame.transform.flip(self.image, False, True)
