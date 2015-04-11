import pygame
from pygame import Rect
from pygame.locals import *
import sys
from config import *
from sprites import BodyPart
import utils

class Body(object):

    collision_matrix = (((1,0,1,0,1),  \
                         (1,1,1,1,1),  \
                         (0,0,1,0,0),  \
                         (0,0,1,0,0)), \
                        ((1,0,1,0,1),  \
                         (1,1,1,1,1),  \
                         (0,0,1,1,0),  \
                         (0,0,0,0,0)), \
                        ((1,0,1,0,0),  \
                         (1,1,1,1,1),  \
                         (0,0,1,1,1),  \
                         (0,0,0,0,0)), \
                        ((0,0,1,0,0),  \
                         (1,1,1,1,1),  \
                         (1,0,1,1,1),  \
                         (0,0,0,0,0)), \
                        ((0,0,1,0,1),  \
                         (1,1,1,1,1),  \
                         (1,1,1,0,0),  \
                         (0,0,0,0,0)), \
                        ((0,0,1,0,1),  \
                         (1,1,1,1,1),  \
                         (1,0,1,0,0),  \
                         (0,0,1,0,0)))

    def __init__(self, body):
        self.body_image = utils.load_image(os.path.join(body), (255, 0, 255))
        self.parts = dict(head      =BodyPart(self.body_image, Rect(2*SIDE, 0*SIDE, 1*SIDE, 2*SIDE), (2, 0)), \
                          rhand_up  =BodyPart(self.body_image, Rect(0*SIDE, 0*SIDE, 2*SIDE, 2*SIDE), (0, 0)), \
                          rhand_down=BodyPart(self.body_image, Rect(0*SIDE, 3*SIDE, 2*SIDE, 2*SIDE), (0, 1)), \
                          lhand_up  =BodyPart(self.body_image, Rect(3*SIDE, 0*SIDE, 2*SIDE, 2*SIDE), (3, 0)), \
                          lhand_down=BodyPart(self.body_image, Rect(3*SIDE, 3*SIDE, 2*SIDE, 2*SIDE), (3, 1)), \
                          legs      =BodyPart(self.body_image, Rect(2*SIDE, 2*SIDE, 1*SIDE, 2*SIDE), (2, 2)), \
                          legs2left =BodyPart(self.body_image, Rect(3*SIDE, 2*SIDE, 2*SIDE, 1*SIDE), (2, 2)), \
                          legs2right=BodyPart(self.body_image, Rect(0*SIDE, 2*SIDE, 2*SIDE, 1*SIDE), (1, 2)))

        self.x = 0
        self.y = 0
        self.shape_index = 0
        self.group = pygame.sprite.Group()

    def draw(self, screen):
        self.group.draw(screen)

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self._setup_parts()

    def up(self):
        if self.y > LEVEL_TOP:
            self.y -= 1
            self._setup_parts()

    def down(self):
        if self.y < LEVEL_TOP+LEVEL_HEIGHT-BODY_HEIGHT:
            self.y += 1
            self._setup_parts()

    def left(self):
        if self.x > LEVEL_LEFT:
            self.x -= 1
            self._setup_parts()

    def right(self):
        if self.x < LEVEL_LEFT+LEVEL_WIDTH-BODY_WIDTH:
            self.x += 1
            self._setup_parts()

    def twist_right(self):
        self.shape_index = (self.shape_index + 1) % 6
        self._setup_parts()

    def twist_left(self):
        if self.shape_index == 0:
            self.shape_index = 5
        else:
            self.shape_index -= 1
        self._setup_parts()

    def get_center(self):
        return (self.x*SIDE+SIDE*BODY_WIDTH/2, \
                self.y*SIDE+SIDE*BODY_HEIGHT/3)

    def _setup_parts(self):
        self.group.empty()
        self.group.add(self.parts['head'])

        if self.shape_index == 0:
            self.group.add(self.parts['rhand_up'])
            self.group.add(self.parts['lhand_up'])
            self.group.add(self.parts['legs'])
        elif self.shape_index == 1:
            self.group.add(self.parts['rhand_up'])
            self.group.add(self.parts['lhand_up'])
            self.group.add(self.parts['legs2left'])
        elif self.shape_index == 2:
            self.group.add(self.parts['rhand_up'])
            self.group.add(self.parts['lhand_down'])
            self.group.add(self.parts['legs2left'])
        elif self.shape_index == 3:
            self.group.add(self.parts['rhand_down'])
            self.group.add(self.parts['lhand_down'])
            self.group.add(self.parts['legs2left'])
        elif self.shape_index == 4:
            self.group.add(self.parts['rhand_down'])
            self.group.add(self.parts['lhand_up'])
            self.group.add(self.parts['legs2right'])
        elif self.shape_index == 5:
            self.group.add(self.parts['rhand_down'])
            self.group.add(self.parts['lhand_up'])
            self.group.add(self.parts['legs'])

        for part in self.group:
            part.setup_rect(self.x*SIDE, self.y*SIDE)

    def is_collision(self, body):
        # Basic cases
        if (self.x+BODY_WIDTH < body.x or \
            self.y+BODY_HEIGHT < body.y or \
            self.x > body.x+BODY_WIDTH or \
            self.y > body.y+BODY_HEIGHT):
            return False

        # Compare block by block
        m_self = Body.collision_matrix[self.shape_index]
        m_body = Body.collision_matrix[body.shape_index]

        x1 = max(self.x, body.x)
        y1 = max(self.y, body.y)
        x2 = min(self.x, body.x)+BODY_WIDTH
        y2 = min(self.y, body.y)+BODY_HEIGHT

        for y in range(y1, y2):
            for x in range(x1, x2):
                if (m_self[y-self.y][x-self.x] == 1 and \
                    m_body[y-body.y][x-body.x] == 1):
                    return True

        return False

    def is_fitting(self, body):
        if self.x != body.x or \
           self.y != body.y:
            return False

        return self.shape_index == body.shape_index

######################################################################
# Test
def main():
    #Initialize 
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    body1 = Body(BODY1)
    body2 = Body(MOLD1)
    body1.set_position(10,5)
    body2.set_position(10,5)
    font1 = pygame.font.Font(FONT1, 10)
    while True:
        screen.fill((0,0,0))

        txt = "use LEFT, RIGHT, UP, DOWN, A and S keys"
        screen.blit(font1.render(txt, True, WHITE), (500,0))

        txt = "COLLISION = " + str(body1.is_collision(body2))
        screen.blit(font1.render(txt, True, WHITE), (0,0))

        txt = "FITTING = " + str(body1.is_fitting(body2))
        screen.blit(font1.render(txt, True, WHITE), (0,16))

        body1.draw(screen)
        body2.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)
                if event.key == K_DOWN:
                    body1.down()
                if event.key == K_UP:
                    body1.up()
                if event.key == K_RIGHT:
                    body1.right()
                if event.key == K_LEFT:
                    body1.left()
                if event.key == K_a:
                    body1.twist_left()
                if event.key == K_s:
                    body2.twist_left()
    

if __name__ == "__main__":
    main()
