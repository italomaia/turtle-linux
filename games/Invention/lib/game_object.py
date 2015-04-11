# Python imports
import pygame
import data

# Game-related imports
from constants import Constants

class GameObject(pygame.sprite.Sprite):
    """ To add new objects to the game, they should inherit from this class.
        This class handles a lot of things automatically (gravity, walkable
        masks, animation, etc) """

    def __init__(self):
        # This is a subclass of the PyGame sprite class.
        pygame.sprite.Sprite.__init__(self)
        # Necessary for pygame sprite objects.
        self.image = pygame.surface.Surface((0, 0))
        self.rect = pygame.rect.Rect((0, 0), (0, 0))
        # The animations list stores a group of pygame surfaces which are
        # (obviously) the different frames of animation.
        self.animations = []
        # The current frame of animation we're displaying.
        self.frame = 0
        # The "magic box" is a secondary collision detection rect which gives
        # us cleaner, more accurate collision detection.
        self.magic_box = pygame.rect.Rect((0, 0), (0, 0))
        # The x/y vel specifies the current velocity this object is moving
        # at in the appropriate axis.
        self.xvel = 0
        self.yvel = 0
        # What direction we're travelling in. 0 = Right, 1 = Left (2 = Up, 3 = Down? Maybe)
        self.direction = 0
        # Is this character "alive?" Mostly just necessary for the player sprite currently.
        self.living = True
        # Allow objects to keep track of their falling height if something should happen to
        # them for falling from too high.
        self.fall_height = 0
        # Is the object "done" (currently only used for the player)
        self.done = False
        # Is the object currently being clicked on/dragged
        self.clicked = False

    def load_anims(self, filename, count):
        """ Load a sequence of files with a starting filename and the count of
            them. For example, load_anims('stuff', 5') loads stuff1.png
            through stuff5.png. """
        for i in range(count):
            self.animations.append(pygame.image.load(data.filepath(filename + str(i + 1) + ".png")))
        self.rect = pygame.rect.Rect((0, 0), self.animations[0].get_rect().size)
        # Make sure our initial image is the first frame
        self.image = self.animations[0]

    def load_image(self, filename):
        """ This just loads a single image (don't specify the extension) to
            load as our image. """
        self.animations.append(pygame.image.load(data.filepath(filename + ".png")))
        # Make sure our initial image is the first frame
        self.image = self.animations[0]

    def handle_click(self, pos, dragging):
        """ Handle mouse button input. """
        (x, y) = pos
        # See if the mouse cursor is within our rect
        if x >= self.rect.left and x <= (self.rect.left + self.rect.width):
            if y >= self.rect.top and y <= (self.rect.top + self.rect.height):
                self.clicked = dragging
                if not self.clicked:
                    self.moved = True
