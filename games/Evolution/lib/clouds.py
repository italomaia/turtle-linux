import random
from OpenGL.GL import *
from euclid import *

def draw_cloud(bl, tr):
    '''
    - two base points, line between
    - another 4 points on semi-circle above
    - length of control vectors = 1/4 -> 1/2 R
    - angle of control vectors up to 45 degrees from angle to center
    '''
    x1, y1 = bl
    x2, y2 = tr

    l = bl
    t = (x2, y1)
    hx = (x2-x1)/2.
    hy = (y2-y1)/2.
    v = Vector2((x2-x1)/2., 0)
    m = Point2(x1 + hx, y1+ hy)

    angles = []
    points = []
    cps = []
    for i in range(6):
        angle = math.pi * i / 5.
        if i not in (0, 5):
            angle += (random.random()-.5) * (math.pi / 10.)
        angles.append(angle)
        r = Matrix3.new_rotate(angle)
        p = m + r * v
        points.append(p)
        r = Matrix3.new_rotate(angle + random.random() * math.pi / 5.)
        v1 = r * v * .5
        r = Matrix3.new_rotate(angle - random.random() * math.pi / 5.)
        v2 = r * v * .5
        cps.append((p + v1, p + v2))

    glColor(.8, .8, .8, 1)
    glBegin(GL_POLYGON)
    for i in range(6):
        glVertex2f(*points[i])
    glEnd()

    for i in range(5):
        p1 = tuple(points[i]) + (0,)
        p2 = tuple(points[i + 1]) + (0,)
        cp1 = tuple(cps[i][0]) + (0,)
        cp2 = tuple(cps[i+1][1]) + (0,)
        p = [
           [p1, cp1, cp2, p2],
           [p1, p1, p2, p2],
        ]

        glMap2f(GL_MAP2_VERTEX_3, 0, 1, 0, 1, p)
        glMapGrid2f(12, 0.0, 1.0, 12, 0.0, 1.0)
        glEvalMesh2(GL_FILL, 0, 12, 0, 12)

    '''
    colors = (
        (255, 0, 0),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 0),
        (0, 255, 255),
        (0, 0, 255),
    )
    glBegin(GL_LINES)
    for i in range(6):
        glColor(*colors[i])
        glVertex2f(*m)
        glVertex2f(*points[i])
        glVertex2f(*points[i])
        glVertex2f(*cps[i][0])
        glVertex2f(*points[i])
        glVertex2f(*cps[i][1])
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

    def draw():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glTranslate(100, 100, 0)
        draw_cloud((0, 0), (256, 128))
        glPopMatrix()
        pygame.display.flip()

    draw()

    while 1:
        ts = clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: sys.exit()
            if e.type == KEYDOWN and e.key == K_ESCAPE: sys.exit()
            if e.type == KEYDOWN and e.key == K_SPACE:
                draw()
