import random
from OpenGL.GL import *
from euclid import *

def draw_trunk(bl, tr):
    '''
        - bottom & top control points at same point
        - may vary from close to bottom to half way
        - may vary from either side to other side
    '''
    x1, y1 = bl
    y1 -= 64            # XXX OMG HAX HAX OMG SUXX0R HAX!!!1111111!1one1!!1
    x2, y2 = tr
    hy = (y2-y1)/2.
    lx = x1 + (x2-x1) * (random.random()-.5)
    rx = x2 + (x2-x1) * (random.random()-.5)
    lhy = hy + hy * (random.random()-.5)
    rhy = hy + hy * (random.random()-.5)

    points = [
        [(x1, y1, 0), (lx, y1+lhy, 0), (lx, y1+lhy, 0), (x1, y2, 0)],
        [(x2, y1, 0), (rx, y1+rhy, 0), (rx, y1+rhy, 0), (x2, y2, 0)],
    ]
    glColor(151/255., 123/255., 49/255., 1)
    glMap2f(GL_MAP2_VERTEX_3, 0, 1, 0, 1, points)
    glMapGrid2f(12, 0.0, 1.0, 12, 0.0, 1.0)
    glEvalMesh2(GL_FILL, 0, 12, 0, 12)

def draw_pointy(bl, tr):
    '''
        - triangle with base 1/3 width of height
        - control points in direction of opposite points, half length or less,
          varying either way from base line by up to +/- half point inside
          angle
    '''
    x1, y1 = bl
    x2, y2 = tr
    hx = (x2-x1)/2.
    fy = (y2-y1)/3.
    draw_trunk((x1 + hx - hx/4, y1), (x1 + hx + hx/4, y1 + fy))

    y1 += fy/2

    # re-calc
    x1 += hx * random.random() *.3
    x2 -= hx * random.random() *.3
    hx = (x2-x1)/2.
    hy = (y2-y1)/2.

    p1 = Point2(x1, y1)
    p2 = Point2(x2, y1)
    p3 = Point2(x1 + hx, y2)

    # left side
    mp = Point2(x1+hx/2, y1+hy)
    v1 = p3 - p1
    r = Matrix3.new_rotate(math.pi/2)
    vp = r * v1.normalized() * ((random.random()-.5) * hx)
    mp1 = mp + vp

    points = [
       [(p1.x, p1.y, 0), (mp1.x, mp1.y, 0), (mp1.x, mp1.y, 0), (p3.x, p3.y, 0)],
       [(p1.x, p1.y, 0), (p1.x, p1.y, 0), (x1+hx, y1+hy, 0), (x1+hx, y1+hy, 0)],
    ]

    glColor(123/255., 191/255., 49/255., 1)
    glMap2f(GL_MAP2_VERTEX_3, 0, 1, 0, 1, points)
    glMapGrid2f(12, 0.0, 1.0, 12, 0.0, 1.0)
    glEvalMesh2(GL_FILL, 0, 12, 0, 12)

    # right side
    mp = Point2(x2-hx/2, y1+hy)
    v1 = p3 - p1
    r = Matrix3.new_rotate(math.pi/2)
    vp = r * v1.normalized() * ((random.random()-.5) * hx)
    mp1 = mp + vp

    points = [
       [(p2.x, p2.y, 0), (mp1.x, mp1.y, 0), (mp1.x, mp1.y, 0), (p3.x, p3.y, 0)],
       [(p2.x, p2.y, 0), (p2.x, p2.y, 0), (x1+hx, y1+hy, 0), (x1+hx, y1+hy, 0)],
    ]

    glColor(123/255., 191/255., 49/255., 1)
    glMap2f(GL_MAP2_VERTEX_3, 0, 1, 0, 1, points)
    glMapGrid2f(12, 0.0, 1.0, 12, 0.0, 1.0)
    glEvalMesh2(GL_FILL, 0, 12, 0, 12)

    # bottom side
    mp = Point2(x1+hx, y1)
    v1 = Vector2(0, 1) * ((random.random()-.5) * hy/2)
    mp1 = mp + v1

    points = [
       [(p1.x, p1.y, 0), (mp1.x, mp1.y, 0), (mp1.x, mp1.y, 0), (p2.x, p2.y, 0)],
       [(p1.x, p1.y, 0), (p1.x, p1.y, 0), (x1+hx, y1+hy, 0), (x1+hx, y1+hy, 0)],
    ]

    glColor(123/255., 191/255., 49/255., 1)
    glMap2f(GL_MAP2_VERTEX_3, 0, 1, 0, 1, points)
    glMapGrid2f(12, 0.0, 1.0, 12, 0.0, 1.0)
    glEvalMesh2(GL_FILL, 0, 12, 0, 12)

def draw_fluffy(bl, tr):
    '''
        - N points around circle
        - control points at up to 45 degrees from normal of point from circle
        - length of control vector between 1/2R to R
    '''
    x1, y1 = bl
    x2, y2 = tr
    hx = (x2-x1)/2.
    hy = (y2-y1)/2.
    draw_trunk((x1 + hx - hx/4, y1), (x1 + hx + hx/4, y1 + hy))

    y1 += hy/2

    # re-calc
    hx = (x2-x1)/2.
    hy = (y2-y1)/2.
    v = Vector2((x2-x1)/2., 0)
    m = Point2(x1 + hx, y1+ hy)

    NUM = random.choice((3, 4, 5))

    angles = []
    points = []
    for i in range(NUM):
        angle = math.pi * 2 * i / NUM
        angle += math.pi * (random.random()-.5) * .1
        angles.append(angle)
        r = Matrix3.new_rotate(angle)
        points.append(m + r * v)

    glColor(123/255., 191/255., 49/255., 1)
    glBegin(GL_POLYGON)
    for i in range(NUM):
        glVertex2f(*points[i])
    glEnd()

    # now figure control points for sides
    for i in range(NUM):
        if i == NUM-1: p1, p2 = points[i], points[0]
        else: p1, p2 = points[i], points[i+1]
        if i == NUM-1: a1, a2 = angles[i], angles[0] + math.pi*2
        else: a1, a2 = angles[i], angles[i+1]
        da = abs(a2-a1) / 2
        a1 += math.pi/(NUM*2) + da * random.random()
        a2 -= math.pi/(NUM*2) + da * random.random()

        l1 = hx + hx * random.random()
        l2 = hx + hx * random.random()

        mp1 = p1 + Matrix3.new_rotate(a1) * Vector2(1, 0) * l1
        mp2 = p2 + Matrix3.new_rotate(a2) * Vector2(1, 0) * l2

        p = [
           [(p1.x, p1.y, 0), (mp1.x, mp1.y, 0), (mp2.x, mp2.y, 0),
                (p2.x, p2.y, 0)],
           [(p1.x, p1.y, 0), (p1.x, p1.y, 0), (p2.x, p2.y, 0), (p2.x, p2.y, 0)],
        ]

        glColor(123/255., 191/255., 49/255., 1)
        glMap2f(GL_MAP2_VERTEX_3, 0, 1, 0, 1, p)
        glMapGrid2f(12, 0.0, 1.0, 12, 0.0, 1.0)
        glEvalMesh2(GL_FILL, 0, 12, 0, 12)

        '''
        glPointSize(5)
        colors = (
            (255, 0, 0),
            (255, 255, 0),
            (255, 0, 255),
            (0, 0, 255),
        )

        glBegin(GL_LINES)
        glColor(*colors[i])
        glVertex2f(*m)
        glVertex2f(*p1)
        glVertex2f(*m)
        glVertex2f(*p2)
        glVertex3f(*p[0][0])
        glVertex3f(*p[0][1])
        glVertex3f(*p[0][2])
        glVertex3f(*p[0][3])
        glEnd()
        '''

if __name__ == '__main__':
    import sys
    import pygame
    from pygame.locals import *

    pygame.init()
    vw, vh = viewport = (1024, 768)
    screen = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)
    clock = pygame.time.Clock()

    # set up 2d mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, 0, vw, vh)
    glOrtho(0, vw, 0, vh, -50, 50)
    glMatrixMode(GL_MODELVIEW)
    glClearColor(.3, .3, .3, 1)
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_MAP2_VERTEX_3)


    while 1:
        ts = clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: sys.exit()
            if e.type == KEYDOWN and e.key == K_ESCAPE: sys.exit()
            if e.type == KEYDOWN and e.key == K_SPACE:
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glBegin(GL_LINES)
                glColor(1, 1, 1, 1)
                glVertex2f(0, 100)
                glVertex2f(1024, 100)
                glEnd()
                glPushMatrix()
                glTranslate(0, 100, 0)
                draw_pointy((0, 0), (256, 512))
                glTranslate(256, 0, 0)
                draw_fluffy((0, 0), (256, 512))
                glPopMatrix()
                pygame.display.flip()

