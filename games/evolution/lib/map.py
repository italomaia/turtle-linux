# OPTIMISE: draw all lines at once
# OPTIMISE: reduce drawing due to meshes
# OPTIMISE: draw all meshes at once as stencil etc.

import math
import random
import operator

import pygame
from OpenGL.GL import *

import textures
import data
import items
from euclid import *

SCALE=128


class EdgePoint:
    angle = None
    def __init__(self, a, b, upright):
        self.a = a
        self.b = b
        ax, ay = a.bottomleft
        bx, by = b.bottomleft
        self.mid = ((ax + bx)/2 + SCALE/2, (ay + by)/2 + SCALE/2)

    def __repr__(self):
        return '<EdgePoint %r&%r @%r,%s deg>'%(self.a.location,
            self.b.location, self.mid, self.angle)

class Map:

    player_start = (0, 0)
    def __init__(self, mapname):
        self.fg = {}
        self.bg = {}
        self.items = []
        self.puffs = []
        self.animated_items = []
        self.spawn = []

        # load background
        filename = data.filepath(mapname + '-bg.png', 'lvl')
        img = pygame.image.load(filename)
        self.w, self.h = img.get_width(),img.get_height()
        for j in range(0, self.h):
            # flip vertically
            fj = self.h - j - 1
            for i in range(0, self.w):
                cell = img.get_at((i, j))
                klass = celltypes[cell]
                self.bg[(i, fj)] = klass((i, fj), self)

        # load foreground
        filename = data.filepath(mapname + '-fg.png', 'lvl')
        img = pygame.image.load(filename)
        assert (self.w, self.h) == (img.get_width(), img.get_height())
        for j in range(0, self.h):
            fj = self.h - j - 1
            for i in range(0, self.w):
                cell = img.get_at((i, j))
                klass = celltypes[cell]
                self.fg[(i, fj)] = klass((i, fj), self)

        # now figure neighbors
        for j in range(0, self.h):
            for i in range(0, self.w):
                cell = self.fg[(i, j)]
                if i > 0: cell.to_left = self.fg[(i - 1, j)]
                if i < self.w - 1: cell.to_right = self.fg[(i + 1, j)]
                if j > 0: cell.to_bottom = self.fg[(i, j - 1)]
                if j < self.h - 1: cell.to_top = self.fg[(i, j + 1)]

        # find shared edges that will create curves
        edges = set()
        for j in range(0, self.h):
            for i in range(0, self.w):
                cell = self.fg[(i, j)]
                if not cell.is_ground: continue
                l = cell.to_left; t = cell.to_top
                r = cell.to_right; b = cell.to_bottom
                tl = t.to_left; tr = t.to_right
                bl = b.to_left; br = b.to_right

                if t.is_open or b.is_open:
                    if r.is_ground:
                        edges.add((cell.location, r.location, b.is_open))
                    if l.is_ground:
                        edges.add((l.location, cell.location, b.is_open))
                if r.is_open or l.is_open:
                    if t.is_ground:
                        edges.add((cell.location, t.location, l.is_open))
                    if b.is_ground:
                        edges.add((b.location, cell.location, l.is_open))

        # given the shared edges we just found, create an EdgePoint
        cell_edges = []
        for a, b, upright in list(edges):
            # order A and B reliably
            if a > b: a, b = b, a
            a = self.fg[a]
            b = self.fg[b]
            p = EdgePoint(a, b, upright)
            cell_edges.append(p)
            for cell in a, b:
                if not cell.edges: cell.edges = []
                cell.edges.append(p)

        # figure the vector through each EdgePoint
        for p in cell_edges:
            l = p.a.edges[0]
            if l == p: l = p.a.edges[1]
            r = p.b.edges[0]
            if r == p: r = p.b.edges[1]

            v = Point2(*r.mid) - Point2(*l.mid)
            v.normalize()

            # v points into b
            p.v = v

            # randomise
            r = random.random()-.5
            v.x += r
            v.y += r

        # now create the curves
        for j in range(0, self.h):
            for i in range(0, self.w):
                o = self.fg[(i, j)]
                if o.is_ground and o.edges:
                    c = self.fg[(i, j)] = CurveGround((i, j), self)
                    c.edges = o.edges
                    # fix links
                    o.to_top.to_bottom = c; o.to_left.to_right = c
                    o.to_right.to_left = c; o.to_bottom.to_top = c
                    c.to_left = o.to_left; c.to_right = o.to_right
                    c.to_top = o.to_top; c.to_bottom = o.to_bottom
                    c.createCurve()

        # LOAD ITEMS
        filename = data.filepath(mapname + '-items.png', 'lvl')
        img = pygame.image.load(filename)
        for j in range(0, self.h):
            fj = self.h - j - 1
            for i in range(0, self.w):
                r, g, b, a = img.get_at((i, j))
                if a != 0:
                    # flip vertically
                    x, y = i*SCALE, fj*SCALE
                    r = items.itemtypes[(r, g, b)](self, (x, y))
                    if r is None:
                        continue
                    if isinstance(r, list):
                        self.items.extend(r)
                    else:
                        self.items.append(r)

    def get_fg(self, x, y):
        i, j = x // SCALE, y // SCALE
        return self.fg[(i, j)]

    def get_bg(self, x, y):
        i, j = x // SCALE, y // SCALE
        return self.bg[(i, j)]

    def destroy(self):
        for j in range(0, self.h):
            for i in range(0, self.w):
                cell = self.fg[(i, j)]
                cell.to_left = cell.to_right = None
                cell.to_bottom = cell.to_top = None
                cell.edges = None

    def animate(self, dt):
        items.Coin.animate(dt)
        items.Starguy.animate(dt)
        items.Baddie.animate(dt)
        for puff in list(self.puffs):
            puff.animate(dt)
            if puff.done: self.puffs.remove(puff)

    def render(self, bx, by, vw, vh, debug=False):
        sx = int(bx/SCALE)
        sy = int(by/SCALE)

        # bg
        d = {}
        for x in range(sx, sx + vw/SCALE + 1):
            for y in range(sy, sy + vh/SCALE + 1):
                c = self.bg[(x, y)]
                d.setdefault(c.__class__, []).append(c)
        for c, l in d.items(): c.renderMany(l)

        # items
        d = {}
        tx, ty = bx + vw, by + vh
        onscreen_items = []
        for item in self.items:
            if item.inScreen(bx, by, tx, ty):
                onscreen_items.append(item)
                d.setdefault(item.__class__, []).append(item)
        l = d.items()
        l.sort(lambda a,b: cmp(a[0].order, b[0].order))
        for item, i in l:
            item.renderMany(i)

        # animated items
        d = {}
        for item in self.animated_items:
            if item.inScreen(bx, by, tx, ty):
                d.setdefault(item.__class__, []).append(item)
        for item, l in d.items():
            item.renderMany(l)

        # fg
        d = {}
        for x in range(sx, sx + vw/SCALE + 1):
            for y in range(sy, sy + vh/SCALE + 1):
                c = self.fg[(x, y)]
                d.setdefault(c.__class__, []).append(c)
        for c, l in d.items(): c.renderMany(l, debug=debug)

        # puffs
        if self.puffs:
            self.puffs[0].renderMany(self.puffs)

        # convenience
        return onscreen_items

    def focus(self, fx, fy, vw, vh):
        xoff = -vw/2
        yoff = -vh/2
        x, y = fx + xoff, fy + yoff
        if x < SCALE: x = SCALE
        if y < SCALE: y = SCALE
        if x + vw > (self.w-1) * SCALE:
            x = (self.w-1) * SCALE - vw
        if y + vh > (self.h-1) * SCALE:
            y = (self.h-1) * SCALE - vh
        return x, y

class Cell:
    is_open = False
    is_ground = False
    is_surface = False
    is_blocker = False
    is_water = False
    is_cave = False

    to_left = None
    to_right = None
    to_top = None
    to_bottom = None

    point = False

    texture_file = None
    texture = None
    internal_format = GL_RGB
    wrap_s = GL_REPEAT
    wrap_t = GL_REPEAT
    fixed = True

    gradient = None

    def __init__(self, location, map=None):
        i, j = self.location = location
        x, y = self.bottomleft = i * SCALE, j * SCALE
        self.left = x
        self.right = x + SCALE
        self.bottom = y
        self.top = y + SCALE
        self.topright = x + SCALE, y + SCALE
        self.bottomright = x + SCALE, y
        self.center = x + SCALE/2, y + SCALE/2

        if self.texture_file is None:
            return

        if self.texture is None:
            filename = data.filepath(self.texture_file)
            t = self.__class__.texture = textures.Texture(filename,
                internal_format=self.internal_format)
            # display list for quad rendering
            self.__class__.quad_list = glGenLists(1)
            glNewList(self.__class__.quad_list, GL_COMPILE)
            su, sv = 0, 0
            eu, ev = SCALE/float(t.width), SCALE/float(t.height)
            glBegin(GL_QUADS)
            glTexCoord2f(su, sv)
            glVertex3f(0, 0, 0)
            glTexCoord2f(eu, sv)
            glVertex3f(SCALE, 0, 0)
            glTexCoord2f(eu, ev)
            glVertex3f(SCALE, SCALE, 0)
            glTexCoord2f(su, ev)
            glVertex3f(0, SCALE, 0)
            glEnd()
            glEndList()

        if self.gradient is None:
            filename = data.filepath('gradient.png')
            Cell.gradient = textures.Texture(filename,
                internal_format=GL_LUMINANCE)

    @classmethod
    def renderMany(cls, cells, debug=False):
        if cls.texture_file is None:
            return

        glBindTexture(GL_TEXTURE_2D, cls.texture.texture_id)
        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, cls.wrap_s)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, cls.wrap_t)

        glPushMatrix()
        glColor(1, 1, 1, 1)
        ox, oy = 0, 0
        t = cls.texture
        for cell in cells:
            x, y = cell.bottomleft
            glTranslatef(x - ox, y - oy, 0)
            ox, oy = x, y

            # translate texture
            glMatrixMode(GL_TEXTURE)
            glLoadIdentity()
            su, sv = x/float(t.width), y/float(t.height)
            glTranslatef(su, sv, 0)
            glMatrixMode(GL_MODELVIEW)

            glCallList(cls.quad_list)
        glPopMatrix()

        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)

        glDisable(GL_TEXTURE_2D)

    def render(self, position=None):
        if self.texture_file is None:
            return

        if position is None:
            x, y = self.bottomleft
        else:
            x, y = position
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.wrap_s)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.wrap_t)
        glBegin(GL_QUADS)
        glColor(1, 1, 1, 1)
        t = self.texture
        if self.fixed:
            su, sv = 0, 0
            eu, ev = float(SCALE)/t.width, float(SCALE)/t.width
        else:
            su, sv = float(x)/t.width, float(y)/t.height
            eu, ev = float(x + SCALE)/t.width, float(y + SCALE)/t.height
        glTexCoord2f(su, sv)
        glVertex2f(x, y)
        glTexCoord2f(eu, sv)
        glVertex2f(x+SCALE, y)
        glTexCoord2f(eu, ev)
        glVertex2f(x+SCALE, y+SCALE)
        glTexCoord2f(su, ev)
        glVertex2f(x, y+SCALE)
        glEnd()
        glDisable(GL_TEXTURE_2D)

        '''
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x+SCALE, y)
        glVertex2f(x+SCALE, y+SCALE)
        glVertex2f(x, y+SCALE)
        glEnd()
        '''


    def __str__(self):
        return '%s%s%s\n%s%s%s\n%s%s%s'%(
            self.to_top.to_left.__class__.__name__[0],
            self.to_top.__class__.__name__[0],
            self.to_top.to_right.__class__.__name__[0],
            self.to_left.__class__.__name__[0],
            self.__class__.__name__[0],
            self.to_right.__class__.__name__[0],
            self.to_bottom.to_left.__class__.__name__[0],
            self.to_bottom.__class__.__name__[0],
            self.to_bottom.to_right.__class__.__name__[0],
        )

    def __repr__(self):
        return '<%s %r>'%(self.__class__.__name__, self.location)

class Blocker(Cell):
    is_blocker = True
    texture_file = None

class Empty(Cell):
    is_open = True
    texture_file = None

class Ground(Cell):
    is_ground = True
    texture_file = 'ground.png'
    edges = None

class CurveGround(Cell):
    is_ground = True
    is_surface = True

    texture_file = 'ground.png'

    edges = None
    curve_list = None

    @classmethod
    def renderMany(cls, cells, debug=False):
        l = []
        for cell in cells:
            if cell.curve_list is not None:
                glCallList(cell.curve_list)
            else:
                l.append(cell)

        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)

        if debug:
            glColor4f(1, 1, 1, 1)
            for cell in cells:
                x1, y1 = cell.bottomleft
                x2, y2 = cell.topright
                glBegin(GL_LINE_LOOP)
                glVertex2f(x1, y1)
                glVertex2f(x2, y1)
                glVertex2f(x2, y2)
                glVertex2f(x1, y2)
                glEnd()


    def createCurve(self):
        # edge 1
        x1, y1 = self.edges[0].mid
        # vector from center to mid to make sure edge vector
        # points correct way
        cmvec = Point2(*self.center) - Point2(x1, y1)
        v = self.edges[0].v
        if cmvec.dot(v) < 0: vx1, vy1 = -v
        else: vx1, vy1 = v

        # edge 2
        x2, y2 = self.edges[1].mid
        cmvec = Point2(*self.center) - Point2(x2, y2)
        v = self.edges[1].v
        if cmvec.dot(v) < 0: vx2, vy2 = -v
        else: vx2, vy2 = v

        # control points along vector
        S = SCALE*.3
        cx1, cy1 = x1 + vx1 * S, y1 + vy1 * S
        cx2, cy2 = x2 + vx2 * S, y2 + vy2 * S

        # CURVE
        curve = [(x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2)]

        # now determine the base for filling - this depends on the
        # open sides

        mx, my = self.center

        t = self.to_top.is_open
        b = self.to_bottom.is_open
        l = self.to_left.is_open
        r = self.to_right.is_open
        tl = self.to_top.to_left.is_open
        tr = self.to_top.to_right.is_open
        bl = self.to_bottom.to_left.is_open
        br = self.to_bottom.to_right.is_open

        # horizontal line
        bx, by = self.bottomleft
        fill = None
        if abs(x1 - x2) == SCALE:
            if t:
                flat = [(x1, by), (x1, by), (x2, by), (x2, by)]
            else:
                y = by + SCALE
                flat = [(x1, y), (x1, y), (x2, y), (x2, y)]

        elif abs(y1 - y2) == SCALE:
            if r:
                flat = [(bx, y1), (bx, y1), (bx, y2), (bx, y2)]
            else:
                x = bx + SCALE
                flat = [(x, y1), (x, y1), (x, y2), (x, y2)]

        elif l != r:
            if self.to_bottom.is_open:
                # obl corner
                y = by + SCALE
            elif self.to_top.is_open:
                # otl corner
                y = by
            else:
                raise ValueError('barf at %r'%(self.location,))
            flat = [(x1, y), (x1, y), (x2, y), (x2, y)]

        elif (bl and not (l|b)) or (br and not (r|b)):
            y = by + SCALE
            if x1 > x2:
                flat = [(bx+SCALE, y), (bx+SCALE, y), (bx, y), (bx, y)]
            else:
                flat = [(bx, y), (bx, y), (bx+SCALE, y), (bx+SCALE, y)]
            if bl:
                x = bx+SCALE
                fill = [(x, y), (x, by), (x-SCALE/2, by)]
            else: # tr
                fill = [(bx, y), (bx, by), (bx+SCALE/2, by)]

        elif (tl and not (l|b)) or (tr and not (r|b)):
            y = by
            if x1 > x2:
                flat = [(bx+SCALE, y), (bx+SCALE, y), (bx, y), (bx, y)]
            else:
                flat = [(bx, y), (bx, y), (bx+SCALE, y), (bx+SCALE, y)]
            if tl:
                x = bx+SCALE
                fill = [(x, y), (x, y+SCALE), (x-SCALE/2, y+SCALE)]
            else: # tr
                fill = [(bx, y), (bx, y+SCALE), (bx+SCALE/2, y+SCALE)]

        else:
            raise ValueError, 'argh'

        # XXX handle cells with one side?

        points = curve

        self.curve_list = glGenLists(1)
        glNewList(self.curve_list, GL_COMPILE)

        # figure curve
        self.curve_line = []

        # draw shape to stencil buffer
        glDisable(GL_BLEND)
        glEnable(GL_STENCIL_TEST)

        glColor4f(1, 1, 1, 1)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)

        # <rj> not blending with gradient until gradient can be applied
        # reasonably
        #glBindTexture(GL_TEXTURE_2D, self.gradient.texture_id)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        #glColor4f(.5, .5, .5, .5)
        #tex_coords = [
        #    [(0., 0.), (0., 1.)],
        #    [(1., 0.), (1., 1.)],
        #]
        #glMap2f(GL_MAP2_TEXTURE_COORD_2, 0, 1, 0, 1, tex_coords)
        #glEnable(GL_MAP2_TEXTURE_COORD_2)

        glStencilFunc(GL_ALWAYS, 1, 1)
        glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)
        glEnable(GL_MAP2_VERTEX_3)
        zpoints = [(x, y, 0) for x, y in points]
        flat = [(x, y, 0) for x, y in flat]
        glMap2f(GL_MAP2_VERTEX_3, 0, 1, 0, 1, [zpoints, flat])
        glMapGrid2f(15, 0.0, 1.0, 15, 0.0, 1.0)

        glEvalMesh2(GL_FILL, 0, 15, 0, 15)
        if fill:
            glBegin(GL_TRIANGLES)
            for v in fill:
                glVertex(*v)
            glEnd()

        # now draw texture over top

        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glColor4f(1., 1., 1., 1.)

        glStencilFunc(GL_EQUAL, 1, 1)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
        glEnable(GL_TEXTURE_2D)
        t = self.texture
        glBindTexture(GL_TEXTURE_2D, t.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        #glEnable(GL_BLEND)
        #glBlendFunc(GL_SRC_COLOR, GL_ONE_MINUS_DST_COLOR)

        glPushMatrix()
        x, y = self.bottomleft
        glTranslatef(x, y, 0)

        # translate texture
        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        su, sv = x/float(t.width), y/float(t.height)
        glTranslatef(su, sv, 0)
        glMatrixMode(GL_MODELVIEW)
        glCallList(self.quad_list)

        # reset texture matrix
        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)

        glPopMatrix()

        glDisable(GL_STENCIL_TEST)

        glLineWidth(2)
        glColor(0, 0, 0, 1)
        glEnable(GL_LINE_SMOOTH)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if points[0][0] > points[3][0]:
            cx, cy = points[3]
            x1, y1 = points[2]
            x2, y2 = points[1]
            x, y = points[0]
        else:
            cx, cy = points[0]
            x1, y1 = points[1]
            x2, y2 = points[2]
            x, y = points[3]
        t = 0
        x1 *= 3; x2 *= 3
        y1 *= 3; y2 *= 3

        glBegin(GL_LINE_STRIP)
        while t <= 1.01:
            a = t; a2 = a**2; a3 = a**3
            b = 1 - t; b2 = b**2; b3 = b**3
            px = cx*b3 + x1*b2*a + x2*b*a2 + x*a3
            py = cy*b3 + y1*b2*a + y2*b*a2 + y*a3
            self.curve_line.append((px, py))
            glVertex2f(px, py)
            # TODO: reduce this number, but we'd need to interpolate
            # self.line if we do
            t += .01
        glEnd()

        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_BLEND)

        glEndList()

    def render(self):
        if self.curve is None:
            Cell.render(self)
            return

        #self.background.render()

        glCallList(self.curve.display_list)

    def getSurfacePosition(self, x, y):
        # TODO use both x and y
       # print 'LINE', x, 'vs', self.curve_line[0][0], 'to', self.curve_line[-1][0]
        for i, (lx, ly) in enumerate(self.curve_line):
            if lx < x: continue
            try:
                adjacent = self.curve_line[i+1]
                v = Point2(*adjacent) - Point2(lx, ly)
            except:
                adjacent = self.curve_line[i-1]
                v = Point2(lx, ly) - Point2(*adjacent)
            v.normalize()
            angle = math.degrees(math.atan2(v.y, v.x))
           # print 'HIT', (lx, ly)
            return angle, lx, ly
       # print 'NOT IN RANGE'
        return None, None, None

    def getClosestPosition(self, x, y):
        l = []
        p = Point2(x, y)
        for lx, ly in self.curve_line:
            l.append((abs(p - Point2(lx, ly)), (lx, ly)))
        l.sort()
        return l[0][1]

class Sky(Cell):
    is_open = True
    texture_file = 'sky.png'
    @classmethod
    def renderMany(cls, cells, debug=False):
        pass
    def render(self, *args):
        pass

class Water(Cell):
    is_open = True
    is_water = True
    texture_file = 'water.png'

class Cave(Cell):
    is_open = True
    is_cave = True
    texture_file = 'cave.png'

class CaveEdge(Cell):
    is_open = True
    texture_file = 'cave-edge.png'
    internal_format = GL_RGBA
    wrap_s = GL_CLAMP
    fixed = True
    is_right = False

    @classmethod
    def renderMany(cls, cells, debug=False):
        for cell in cells:
            cell.render()

    def render(self, position=None):
        texture = self.texture
        self.texture = Sky.texture
        Cell.render(self, position or self.bottomleft)
        self.texture = texture
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        if self.is_right:
            glPushMatrix()
            glScalef(-1, 1, 1)
        Cell.render(self, position or self.bottomleft)
        if self.is_right:
            glPopMatrix()
        glDisable(GL_BLEND)

class CaveEdgeRight(CaveEdge):
    is_right = True

celltypes = {
     (0, 0, 0, 255): Blocker,
     (0, 0, 0, 0): Empty,
     (0, 255, 0, 255): Ground,
     (0, 255, 255, 255): Sky,
     (0, 0, 255, 255): Water,
     (72, 56, 56, 255): Cave,
     (136, 96, 166, 255): CaveEdge,
     (120, 116, 140, 255): CaveEdgeRight,
}
