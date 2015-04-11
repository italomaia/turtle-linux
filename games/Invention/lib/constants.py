class Constants:
    """ All of the in-game constants are declared here. This is a hell of a lot
    easier than magic values stored in random files! """
    # Maximum rate for objects to fall
    GRAVITY = 7

    # Speed that certain objects travel at
    SPEED = 5

    # Speed that the girl character travels at
    GIRL_SPEED = 2

    # Seconds until the girl begins moving
    GIRL_WAIT = 50

    # Number of building blocks the game starts off with
    START_BLOCKS = 50

    # Maximum FPS for the game
    MAX_FPS = 30

    # Screen width/height
    SCREEN_WIDTH = 600
    SCREEN_HEIGHT = 600

    # Bitmask flags
    ANTIGRAVITY = 1
    ICE = 2
    FIRE = 4
