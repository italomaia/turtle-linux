
import pygame
from OpenGL.GL import *

import textures
import data
import sprite
import items
import puff
from euclid import *

WORM_SPEED = 5/33.
WALK_SPEED = 10/33.
JUMP_SPEED = 32/33.
SWIM_SPEED = 10/33.
LEAP_SPEED = 30/33.
FLY_SPEED = 10/33.
GRAVITY = Vector2(0, -1./16)

# number of seconds (*1000) required worming around before change
WALK_CHANGE_THRESHOLD = 10000

# number of seconds (*1000) required under water before change
WATER_CHANGE_THRESHOLD = 2000

# number of jumps required to change
JUMP_CHANGE_THRESHOLD = 10

def rp(x, y):
    v = glReadPixels(int(x), int(y), 1, 1, GL_STENCIL_INDEX,
        GL_UNSIGNED_BYTE)
    if isinstance(v, str):
        return ord(v[0])
    # numpy.ndarray
    return v[0][0]

class Player(sprite.Sprite):

    def __init__(self, position):
        self.textures = {}
        self.texture = None

        # animation textures
        for name in 'wormy walking swimming flying flying-landing map map-overlay'.split():
            path = data.filepath(name + '.png')
            self.textures[name] = textures.TextureGrid(path, 64, 64)

        # numebrs - different grid size
        path = data.filepath('numbers.png')
        self.textures['numbers'] = textures.TextureGrid(path, 20, 32)

        # basic textures
        for name in 'light radar'.split():
            path = data.filepath(name + '.png')
            self.textures[name] = textures.Texture(path)

        self.sounds = {}
        for name in 'component landing star coin step1 step2 step3 wingbeat'.split():
            path = data.filepath('%s.ogg'%name, 'sfx')
            self.sounds[name] = pygame.mixer.Sound(path)

        #self.setForm(self.FORM_WORM)
        self.setMode(self.MODE_WORM)

        sprite.Sprite.__init__(self, self.texture)
        self.width = 64
        self.height = 64
        self.x, self.y = position
        self.impulse = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.gravity = Vector2(0, 0)
        self.frame = 0
        self.framecount = 0.00
        self.direction = 1
        self.angle = 0
        self.coins = 0
        self.health = 2
        self.components = []
        self.puffs = []

        self.offset = 44        # horizontal offset to center of worm

    def get_center_top(self):
        return (self.x, self.y + self.height)
    center_top = property(get_center_top)
    def get_center(self):
        return (self.x, self.y + self.height / 2)
    center = property(get_center)
    def get_center_bottom(self):
        return (self.x, self.y)
    center_bottom = property(get_center_bottom)

    def get_position(self):
        return Point2(self.x, self.y)
    def set_position(self, position):
        self.x, self.y = position
    position = property(get_position, set_position)

    def get_ox(self):
        if self.direction > 0:
            return self.x - self.offset
        else:
            return self.x - self.offset/2
    def set_ox(self, x):
        self.x = x + self.offset# * self.direction
    ox = property(get_ox, set_ox)

    def get_left(self): return self.ox
    def set_left(self, x): self.ox = x
    left = property(get_left, set_left)
    def get_right(self): return self.ox + self.width
    def set_right(self, x): self.ox = x - self.width
    right = property(get_right, set_right)
    def get_bottom(self): return self.y
    def set_bottom(self, y): self.y = y
    bottom = property(get_bottom, set_bottom)
    def get_top(self): return self.y + self.height
    def set_top(self, y): self.y = y - self.height
    top = property(get_top, set_top)

    def get_topleft(self): return self.ox, self.y + self.height
    def set_topleft(self, x, y): self.ox = x
    topleft = property(get_topleft, set_topleft)
    def get_bottomleft(self): return self.ox, self.y
    def set_bottomleft(self, x, y): self.ox = x; self.y = y
    bottomleft = property(get_bottomleft, set_bottomleft)
    def get_topright(self): return self.ox + self.width, self.y + self.height
    def set_topright(self, x, y): self.ox = x-self.width; self.y = y-self.height
    topright = property(get_topright, set_topright)
    def get_bottomright(self): return self.ox + self.width, self.y
    def set_bottomright(self, x, y): self.ox = x - self.width; self.y = y
    bottomright = property(get_bottomright, set_bottomright)

    MODE_WORM = 'wormy'
    MODE_WORM_JUMPING = 'worm-jump'
    MODE_WORM_JUMPING_TAKEOFF = 'worm-jump-takeoff'
    MODE_WORM_JUMPING_LANDING = 'work-jump-landing'

    MODE_WALK = 'walking'
    MODE_WALK_JUMPING = 'walk-jump'
    MODE_WALK_JUMPING_TAKEOFF = 'walk-jump-takeoff'
    MODE_WALK_JUMPING_LANDING = 'walk-jump-landing'

    MODE_FLYING = 'flying'
    MODE_FLYING_WALK = 'flying-walk'
    MODE_FLYING_TAKEOFF = 'flying-takeoff'
    MODE_FLYING_LANDING = 'flying-landing'

    MODE_SWIMMING = 'swimming'
    MODE_SWIMMING_WALK = 'swimming-walk'
    MODE_SWIMMING_JUMPING = 'swimming-jump'

    cycle = True
    def setMode(self, mode):
        self.cycle = False
        self.frame = 0
        if mode in (self.MODE_WORM, self.MODE_WORM_JUMPING):
            self.texture = self.textures['wormy'].row(3)
        elif mode == self.MODE_WORM_JUMPING_TAKEOFF:
            self.texture = self.textures['wormy'].row(2)
        elif mode == self.MODE_WORM_JUMPING_LANDING:
            self.texture = self.textures['wormy'].row(1)
        if mode in (self.MODE_WALK, self.MODE_WALK_JUMPING):
            self.texture = self.textures['walking'].row(3)
        elif mode == self.MODE_WALK_JUMPING_TAKEOFF:
            self.texture = self.textures['walking'].row(2)
        elif mode == self.MODE_WALK_JUMPING_LANDING:
            self.texture = self.textures['walking'].row(1)
        elif mode == self.MODE_FLYING:
            self.texture = self.textures['flying'].row(1)
        elif mode == self.MODE_FLYING_WALK:
            self.texture = self.textures['flying'].row(0)
        elif mode in (self.MODE_FLYING_LANDING, self.MODE_FLYING_TAKEOFF):
            self.texture = self.textures['flying-landing'].row(0)
        elif mode == self.MODE_SWIMMING:
            self.texture = self.textures['swimming'].row(1)
        elif mode in (self.MODE_SWIMMING_WALK, self.MODE_SWIMMING_JUMPING):
            self.texture = self.textures['swimming'].row(0)
        self.mode = mode

    def isWorm(self):
        return self.mode in (self.MODE_WORM, self.MODE_WORM_JUMPING,
            self.MODE_WORM_JUMPING_TAKEOFF, self.MODE_WORM_JUMPING_LANDING)

    def isWalking(self):
        return self.mode in (self.MODE_WALK, self.MODE_WALK_JUMPING,
            self.MODE_WALK_JUMPING_TAKEOFF, self.MODE_WALK_JUMPING_LANDING)

    def isFlying(self):
        return self.mode in (self.MODE_FLYING, self.MODE_FLYING_LANDING,
            self.MODE_FLYING_TAKEOFF, self.MODE_FLYING_WALK)

    def isSwimming(self):
        return self.mode in (self.MODE_SWIMMING, self.MODE_SWIMMING_WALK,
            self.MODE_SWIMMING_JUMPING)

    def isGroundMode(self):
        return self.mode in (self.MODE_WORM, self.MODE_WORM_JUMPING,
            self.MODE_WORM_JUMPING_TAKEOFF, self.MODE_WORM_JUMPING_LANDING,
            self.MODE_WALK, self.MODE_WALK_JUMPING,
            self.MODE_WALK_JUMPING_TAKEOFF, self.MODE_WALK_JUMPING_LANDING,
            self.MODE_FLYING_LANDING, self.MODE_FLYING_TAKEOFF,
            self.MODE_FLYING_WALK, self.MODE_SWIMMING_WALK)

    def isInCave(self, map, pos=None):
        if pos is None: pos = self.center_bottom
        return map.get_bg(*pos).is_cave

    def isUnderWater(self, map, pos=None):
        if pos is None: pos = self.center_bottom
        return map.get_bg(*pos).is_water

    under_water = 0
    number_jumps = 0
    time_worming = 0
    def runWalk(self, game, dt, k_left, k_right, k_up, k_down):
        remember_frame = self.frame
        if k_left:
            self.direction = -1
        elif k_right:
            self.direction = 1
        else:
            self.frame = 0

        if self.cycle:
            if self.isWorm():
                self.texture = self.textures['wormy'].row(3)
            elif self.isFlying():
                self.sounds['step2'].play()
                self.texture = self.textures['flying'].row(0)
            elif self.isSwimming():
                self.sounds['step3'].play()
                self.texture = self.textures['swimming'].row(0)
            else:
                self.sounds['step1'].play()
                self.texture = self.textures['walking'].row(3)

        # feeble attempt at stopping going thru walls
        if self.direction < 0 and self.angle < -75:
            self.velocity *= 0
        elif self.direction > 0 and self.angle > 75:
            self.velocity *= 0

        # right, where are we?
        cx, cy = self.center

        # WALKING UNDER WATER
        if self.isUnderWater(game.map, (cx, cy)):
            if self.isSwimming():
                self.frame = 0
                self.angle = 0
                self.setMode(self.MODE_SWIMMING)
                return

            if self.isFlying():
                self.frame = 0
                self.angle = 0
                self.setMode(self.MODE_FLYING)
                return

            cy += self.height
            # CHANGE FORM?
            if self.isUnderWater(game.map, (cx, cy)):
                self.under_water += dt
                if self.under_water > WATER_CHANGE_THRESHOLD:
                    self.frame = 0
                    self.angle = 0
                    self.setMode(self.MODE_SWIMMING)
                    return
            else:
                self.under_water = 0

            # float to surface
            self.angle = 0
            self.velocity *= .75
            self.velocity -= (GRAVITY * dt)/2
            if k_up or k_down:
                self.frame = remember_frame

            # move in water
            v = Vector2(k_right - k_left, k_up - k_down) * WORM_SPEED/4 * dt
            self.velocity += v
            self.stopFlight(game, k_left, k_right, k_up, k_down)

            return
        else:
            self.under_water = 0

        if not self.isWalking() and (k_left or k_right):
            self.time_worming += dt
            if self.time_worming > WALK_CHANGE_THRESHOLD:
                if self.isSwimming() or self.isFlying():
                    self.setMode(self.MODE_WORM)
                else:
                    self.setMode(self.MODE_WALK)
                self.time_worming = 0

        # try moving
        r = Matrix3.new_rotate(math.radians(self.angle))
        if self.isWalking():
            speed = WALK_SPEED* dt
            v = self.velocity + r * Vector2((k_right - k_left) * speed, 0)
        else:
            speed = WORM_SPEED* dt
            v = self.velocity + r * Vector2((k_right - k_left) * speed, 0)

        # see if we can move in that direction
        p = Point2(*self.center_bottom)
        x, y = p + v
        cell = game.map.get_fg(x, y)
        ground, stop = self.isOnGround(cell)

        if not ground:
            self.velocity = self.velocity + GRAVITY * dt
            return

        if stop:
            self.velocity *= 0
        else:
            # include some friction
            self.velocity = v  * .5

        # allow jump
        if k_up and not self.isSwimming():
            self.frame = 0
            self.cycle = False
            if self.isFlying() or self.number_jumps == JUMP_CHANGE_THRESHOLD:
                # FLY!
                self.number_jumps = 0
                self.angle = 0
                self.setMode(self.MODE_FLYING_TAKEOFF)
                self.velocity = Vector2(0, 4)
                self.target_y = self.y + 64
                return
            self.number_jumps += 1

            if k_left or k_right:
                self.jump_angle = self.angle + (k_left - k_right) * 30
            else:
                # <rj> don't use the ground angle for takeoff, it's just
                # annoying
                self.jump_angle = 0

            self.jumped = False
            if self.isWorm():
                self.angle = 0
                self.setMode(self.MODE_WORM_JUMPING_TAKEOFF)
            else:
                self.angle = 0
                self.setMode(self.MODE_WALK_JUMPING_TAKEOFF)

    def runJumping(self, game, dt, k_left, k_right, k_up, k_down):
        if k_left: self.direction = -1
        elif k_right: self.direction = 1
        self.frame = 0

        # TODO: move in mid-air!
        #self.impulse.x = (k_right - k_left) * self.speed * dt

        if self.testLanding(game, dt, k_left, k_right, k_up, k_down):
            if self.isWorm():
                self.setMode(self.MODE_WORM_JUMPING_LANDING)
            elif self.isWalking():
                self.setMode(self.MODE_WALK_JUMPING_LANDING)
            elif self.isSwimming():
                self.setMode(self.MODE_SWIMMING_WALK)

    def testLanding(self, game, dt, k_left, k_right, k_up, k_down):
        # hit the ground?
        cx, cy = self.center_bottom

        cell = game.map.get_fg(cx, cy)

       # print cell

        ground, stop = self.isOnGround(cell)
        if ground:
            self.velocity *= 0
            return True

        cell = game.map.get_bg(cx, cy)
        v = self.velocity.normalized()
        if cell.is_water and v.y < 0:
            self.velocity += v * -4
            # bouyancy
            self.gravity -= GRAVITY * dt
            if self.isWorm():
                self.setMode(self.MODE_WORM)
            elif self.isWalking():
                self.setMode(self.MODE_WALK)
            elif self.isSwimming():
                self.setMode(self.MODE_SWIMMING)
            return

        self.velocity += GRAVITY * dt

        return self.stopFreefall(game)

    lx, ly = 0, 0
    def isOnGround(self, cell):
        if not cell.is_surface:
            return False, False
        angle = self.angle
        cx, cy = self.center_bottom

       # print 'CURRENT CELL IS', cell.location

        if cell.is_ground and not cell.is_surface and cell.to_top.is_surface:
            # we've snuck through a crack
            cell = cell.to_top

       # print 'EXAMINED CELL IS', cell.location

        angle, lx, ly = cell.getSurfacePosition(cx, cy)

       # print (angle, (cx, cy), (lx, ly))

        self.lx, self.ly = lx, ly
        if angle is None or cy > ly:
            return False, False

       # print 'MADE IT HERE'

        stop = False
        if cy < ly - 64:
           # print 'TOTAL STOP'
            # too big a jump - ignore
            lx, ly = cell.getClosestPosition(cx, cy)
            stop = True
            angle = self.angle

       # print 'STOP FALL'
        self.y = ly
        self.angle = angle
        return True, stop

    def stopFreefall(self, game):
        # TODO: use ARB_occlusion_query if it's available
        tx, ty = int(game.tx), int(game.ty)
        x, y = self.topleft
        tl = rp(x-tx, y-ty)
        x, y = self.topright
        tr = rp(x-tx, y-ty)
        x, y = self.bottomleft
        bl = rp(x-tx, y-ty)
        x, y = self.bottomright
        br = rp(x-tx, y-ty)
        x, y = self.position
        p = rp(x-tx, y-ty)
        r = False
        # TODO only calc the ones we need
        v = self.velocity
        if (v.y > 0 and (tl or tr)) or (v.y < 0 and (bl or br)):
            self.velocity.y = 0
            r = True
        if (v.x > 0 and (br or tr)) or (v.x < 0 and (bl or tl)):
            self.velocity.x = 0
            r = True
        return r

    jumped = False
    def runJumpingTakeoff(self, game, dt, k_left, k_right, k_up, k_down):
        if self.cycle:
            if self.isWorm():
                self.setMode(self.MODE_WORM_JUMPING)
            else:
                self.setMode(self.MODE_WALK_JUMPING)
        elif self.frame == 7:
            if not self.jumped:
                r = Matrix3.new_rotate(math.radians(self.jump_angle))
                if self.isWalking():
                    self.velocity += r*Vector2(0, JUMP_SPEED * dt * 1.5)
                else:
                    self.velocity += r*Vector2(0, JUMP_SPEED * dt)
                self.jumped = True
        elif self.frame > 7:
            self.velocity += GRAVITY * dt
            self.testLanding(game, dt, k_left, k_right, k_up, k_down)

    def runJumpingLanding(self, game, dt, k_left, k_right, k_up, k_down):
        self.velocity *= 0
        if self.isWorm():
            self.setMode(self.MODE_WORM)
        else:
            self.setMode(self.MODE_WALK)

        # <rj> disabled landing animations as they're not integrating well
        #self.frame = 0
        #if self.isWorm():
            #self.texture = self.textures['wormy'].row(1)
        #else:
            #self.texture = self.textures['walking'].row(1)


    # SWIMMING
    under_water = False
    def runSwimming(self, game, dt, k_left, k_right, k_up, k_down):
        if k_left:
            self.direction = -1
        elif k_right:
            self.direction = 1

        cx, cy = self.center
        uw = self.isUnderWater(game.map, (cx, cy))

        if uw:
            self.velocity = Vector2(k_right-k_left, k_up-k_down)*SWIM_SPEED*dt
        elif self.under_water:
            self.velocity = Vector2(k_right-k_left, k_up-k_down)*LEAP_SPEED*dt
            self.setMode(self.MODE_SWIMMING_JUMPING)
        else:
            self.velocity += GRAVITY * dt

        self.under_water = uw

        self.stopFlight(game, k_left, k_right, k_up, k_down)


    # FLYING
    def runFlying(self, game, dt, k_left, k_right, k_up, k_down):
        if k_left:
            self.direction = -1
        elif k_right:
            self.direction = 1

        if self.cycle:
            self.sounds['wingbeat'].play()

        v = Vector2(k_right - k_left, k_up - k_down)
        v *= FLY_SPEED * dt
        self.velocity = v

        if self.isUnderWater(game.map):
            self.velocity *= .5
            self.under_water += dt
            if self.under_water > WATER_CHANGE_THRESHOLD:
                self.frame = 0
                self.setMode(self.MODE_SWIMMING)
        else:
            self.under_water = 0

        self.stopFlight(game, k_left, k_right, k_up, k_down)

    def stopFlight(self, game, k_left, k_right, k_up, k_down):
        # TODO: use ARB_occlusion_query if it's available
        tx, ty = int(game.tx), int(game.ty)
        if k_up or k_left:
            x, y = self.topleft
            tl = rp(x-tx, y-ty)
        if k_up or k_right:
            x, y = self.topright
            tr = rp(x-tx, y-ty)
        if k_down or k_left:
            x, y = self.bottomleft
            bl = rp(x-tx, y-ty)
        if k_down or k_right:
            x, y = self.bottomright
            br = rp(x-tx, y-ty)

        # above water
        if k_down and (bl or br):
            x, y = self.position
            p = rp(x-tx, y-ty)
            if rp(x-tx, y-ty):
                if not self.isUnderWater(game.map):
                    self.velocity *= 0
                    self.setMode(self.MODE_FLYING_LANDING)
                    self.frame = 1
                else:
                    self.velocity.y = 0

        if k_up and (tl or tr):
            self.velocity.y = 0
        if k_right and (br or tr):
            self.velocity.x = 0
        if k_left and (bl or tl):
            self.velocity.x = 0

    def runTakeoff(self, game, dt, *args):
        self.angle = 0
        if self.frame == 0:
            self.sounds['wingbeat'].play()
        if self.cycle:
            self.setMode(self.MODE_FLYING)

    def runFlyingLanding(self, game, dt, k_left, k_right, k_up, k_down):
        self.velocity *= 0
        self.angle = 0
        if self.frame == 0:
            self.setMode(self.MODE_FLYING_WALK)

    handlers = {
        MODE_WORM: runWalk,
        MODE_WORM_JUMPING: runJumping,
        MODE_WORM_JUMPING_LANDING: runJumpingLanding,
        MODE_WORM_JUMPING_TAKEOFF: runJumpingTakeoff,
        MODE_WALK: runWalk,
        MODE_WALK_JUMPING: runJumping,
        MODE_WALK_JUMPING_LANDING: runJumpingLanding,
        MODE_WALK_JUMPING_TAKEOFF: runJumpingTakeoff,
        MODE_SWIMMING: runSwimming,
        MODE_SWIMMING_WALK: runWalk,
        MODE_SWIMMING_JUMPING: runJumping,
        MODE_FLYING: runFlying,
        MODE_FLYING_LANDING: runFlyingLanding,
        MODE_FLYING_TAKEOFF: runTakeoff,
        MODE_FLYING_WALK: runWalk,
    }

    def run(self, game, dt, k_left, k_right, k_up, k_down):
        self.handlers[self.mode](self, game, dt, k_left, k_right, k_up, k_down)

        # stuff everything does
        self.position += self.velocity
        self.framecount += dt
        self.cycle = False
        if self.framecount > 25:
            self.framecount = 0.00
            self.frame += 1
            if self.frame >= 1024/64:
                self.cycle = True
                self.frame = 0

    def overlaps(self, other):
        '''Return True if this sprite overlaps the other rect.

        A rect is an object that has an origin .x, .y and size .width,
        .height.
        '''
        other = other.hitbox

        # we avoid using .right and .top properties here to speed things up
        if (self.left + 8) > other.right: return False
        if (self.right - 8) < other.left: return False
        if self.bottom > other.top: return False
        if (self.top - 8) < other.bottom: return False
        return True

    invulnerable = 0

    def hitItems(self, game, onscreen_items, dt):
        map = game.map

        if self.invulnerable > 0:
            self.invulnerable -= dt
        else:
            self.invulnerable = 0

        for p in self.puffs:
            p.animate(dt)
            if p.done: self.puffs.remove(p)

        # only check the on-screen items
        for item in onscreen_items:
            if isinstance(item, items.Tree):
                continue
            # TODO visual effects here
            if self.overlaps(item):
                if isinstance(item, items.Coin):
                    self.sounds['coin'].play()
                    self.coins += 1
                    map.puffs.append(puff.Puff(item.center, (1, 1, 0, 1),
                    gravity=-.5))
                    if not self.coins%30:
                        pos = (self.health*64 + items.Starguy.fw/2,
                            game.vh - (items.Starguy.fh/2 + items.Coin.fh))
                        self.health += 1
                        self.sounds['star'].play()
                    map.items.remove(item)
                elif isinstance(item, items.Component):
                    # item repositioned on the map by the item's key_pos
                    self.sounds['component'].play()
                    map.puffs.append(puff.Puff(item.center, (1, 1, 1, 1),
                        50, 5, gravity=0))
                    item.bottomleft = item.key_pos
                    x, y = item.key_pos
                    x += (1024 - 256 + 32)   # XXX HAX HAX OMG WTF BBQ HAX
                    y += (768 - 256 + 32)    # XXX HAX HAX OMG WTF BBQ HAX
                    self.puffs.append(puff.Puff((x, y), (1, 1, 1, 1),
                        50, 5, gravity=0))
                    self.components.append(item)
                    map.items.remove(item)
                elif isinstance(item, items.Starguy):
                    pos = (self.health*64 + items.Starguy.fw/2,
                        game.vh - (items.Starguy.fh/2 + items.Coin.fh))
                    self.puffs.append(puff.Puff(pos, (1, 1, 0, 1), gravity=0))
                    self.health += 1
                    self.sounds['star'].play()
                    map.puffs.append(puff.Puff(item.center, (1, 1, 0, 1),
                        gravity=0))
                    map.items.remove(item)
                elif isinstance(item, items.Baddie):
                    self.health -= 1
                    map.puffs.append(puff.Puff(item.center, (0, 0, 0, 1),
                        50, 1, fade=.025, gravity=-.2))
                    self.sounds['landing'].play()
                    self.invulnerable = 2000
                    map.items.remove(item)

    def render(self, debug=False):
        glPushMatrix()
        glTranslatef(self.x - (self.direction * self.offset), self.y, 0)

        # rotate about basepoint
        if not self.isWalking():
            glTranslatef(self.direction * self.offset, 0, 0)
            glRotatef(self.angle, 0, 0, 1)
            glTranslatef(self.direction * -self.offset, 0, 0)

        glScalef(self.direction, 1, 1)

        if (int(self.invulnerable) / 100) % 2:
            glColor(1, 1, 1, .5)
        else:
            glColor(1, 1, 1, 1)

        self.texture.render(self.frame)

        glPopMatrix()

        if debug:
            glPointSize(5)
            glBegin(GL_POINTS)
            glColor(1, 0, 0, 1)
            glVertex2f(*self.center_bottom)
            if self.ly is not None:
                glColor(0, 0, 1, 1)
                glVertex2f(self.lx, self.ly)
            glColor(1, 0, 1, 1)
            glVertex2f(*self.bottomleft)
            glVertex2f(*self.bottomright)
            glVertex2f(*self.topleft)
            glVertex2f(*self.topright)
            glEnd()

    def renderLight(self, tx, ty, vw, vh):
        cx, cy = self.center
        glPushMatrix()
        t = self.textures['light']
        glTranslatef(cx - 256, cy - 256, 0)
        glScalef(4, 4, 1)
        glColor(1, 1, 1, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_ZERO, GL_SRC_COLOR)
        t.render()
        glDisable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPopMatrix()

        # fill in borders
        l = (cx - 256) - tx
        r = (cx + 256) - tx
        t = (cy + 256) - ty
        b = (cy - 256) - ty

        glPushMatrix()
        glTranslatef(tx, ty, 0)
        glColor(0, 0, 0, 1)
        glBegin(GL_QUADS)
        if l > 0:
            glVertex(0, b); glVertex(l, b); glVertex(l, t); glVertex(0, t)
        if r < vw:
            glVertex(r, b); glVertex(vw, b); glVertex(vw, t); glVertex(r, t)
        if b > 0:
            glVertex(0, 0); glVertex(vw, 0); glVertex(vw, b); glVertex(0, b)
        if t < vh:
            glVertex(0, t); glVertex(vw, t); glVertex(vw, vh); glVertex(0, vh)
        glEnd()
        glPopMatrix()


    def renderRadar(self, game):
        glEnable(GL_BLEND)
        p = Point2(*self.center)
        t = self.textures['radar']
        for item in game.map.items:
            if isinstance(item, items.Component):
                v = Point2(*item.center) - p
                alpha = 1. - (abs(v) / (128 * 128))
                glColor(1, .5, 1, alpha)
                angle = math.atan2(v.y, v.x)
                glPushMatrix()
                glTranslatef(p.x, p.y + t.height/2, 0)
                glRotate(math.degrees(angle), 0, 0, 1)
                glTranslatef(0, -t.height/2, 0)
                t.render()
                glPopMatrix()
        glDisable(GL_BLEND)


    def renderHUD(self, game):
        glColor(1, 1, 1, 1)

        # COMPONENTS MAP
        t = self.textures['map']
        glPushMatrix()
        glTranslatef(game.vw - t.width, game.vh - t.height, 0)
        glEnable(GL_BLEND)
        t.render()
        glDisable(GL_BLEND)

        # highlight retrieved components
        for item in self.components:
            # item positioned by the item's new (key_pos) position
            item.render()
        glPopMatrix()

        # COINS COLLECTED
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        t = items.Coin.texture
        glBindTexture(GL_TEXTURE_2D, t.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glBegin(GL_QUADS)
        x, y = 0, game.vh - items.Coin.fw
        su, sv = float(items.Coin.frame * items.Coin.fw) / t.width, 0
        eu, ev = float((items.Coin.frame + 1) * items.Coin.fw) / t.width, 1
        glTexCoord2f(su, sv)
        glVertex2f(x, y)
        glTexCoord2f(eu, sv)
        glVertex2f(x+items.Coin.fw, y)
        glTexCoord2f(eu, ev)
        glVertex2f(x+items.Coin.fw, y+items.Coin.fh)
        glTexCoord2f(su, ev)
        glVertex2f(x, y+items.Coin.fh)
        glEnd()
        glDisable(GL_TEXTURE_2D)

        glEnable(GL_BLEND)
        glPushMatrix()
        n = self.textures['numbers']
        glTranslatef(items.Coin.fw + 8, game.vh - n.height, 0)
        # TODO: finish this (and optimise it
        for c in str(self.coins):
            n.row(0).render('0123456789'.index(c))
            glTranslatef(22, 0, 0)
        glPopMatrix()

        # HEALTH COLLECTED
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        sg = items.Starguy
        t = sg.texture
        glBindTexture(GL_TEXTURE_2D, t.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glBegin(GL_QUADS)
        for i in range(self.health):
            x, y = i*64, game.vh - (sg.fw + items.Coin.fh)
            su, sv = float(sg.frame * sg.fw) / t.width, 0
            eu, ev = float((sg.frame + 1) * sg.fw) / t.width, 1
            glTexCoord2f(su, sv)
            glVertex2f(x, y)
            glTexCoord2f(eu, sv)
            glVertex2f(x+sg.fw, y)
            glTexCoord2f(eu, ev)
            glVertex2f(x+sg.fw, y+sg.fh)
            glTexCoord2f(su, ev)
            glVertex2f(x, y+sg.fh)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

        if self.puffs:
            self.puffs[0].renderMany(self.puffs)

        glColor(1, 1, 1, 1)
