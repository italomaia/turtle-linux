from config import *
from body import Body

class Mold(Body):

    def __init__(self, x, y, shape_index):
        Body.__init__(self, MOLD1)
        self.shape_index = shape_index
        self.set_position(x, y)

    def move(self):
        # we don't use self.left() here because that method
        # limits the movement to the level bounds
        self.set_position(self.x-1, self.y)
