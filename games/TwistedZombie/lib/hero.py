from config import *
from body import Body

class Hero(Body):

    def __init__(self):
        Body.__init__(self, BODY1)
        self.set_position(LEVEL_LEFT, \
                          LEVEL_TOP+LEVEL_HEIGHT/2-BODY_HEIGHT/2)
