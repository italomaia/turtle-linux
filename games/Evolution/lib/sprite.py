
class Sprite(object):
    def __init__(self, image):
        self.x, self.y = (0, 0)
        self.width, self.height = image.width, image.height
        self.image = image

    def contains(self, x, y):
        if x < self.x: return False
        if y < self.y: return False
        if x >= self.x + self.width: return False
        if y >= self.y + self.height: return False
        return True

    def overlaps(self, rect):
        if self.x > (rect.x + rect.width): return False
        if (self.x + self.width) < rect.x: return False
        if self.y > (rect.y + rect.height): return False
        if (self.y + self.height) < rect.y: return False
        return True

    def get_top(self): return self.y + self.height
    def set_top(self, y): self.y = y - self.height
    top = property(get_top, set_top)

    def get_bottom(self): return self.y
    def set_bottom(self, y): self.y = y
    bottom = property(get_bottom, set_bottom)

    def get_left(self): return self.x
    def set_left(self, x): self.x = x
    left = property(get_left, set_left)

    def get_right(self): return self.x + self.width
    def set_right(self, x): self.x = x - self.width
    right = property(get_right, set_right)

    def get_center(self):
        return (self.x + self.width/2, self.y + self.height/2)
    def set_center(self, center):
        x, y = center
        self.x = x - self.width/2
        self.y = y - self.height/2
    center = property(get_center, set_center)

    def get_midtop(self):
        return (self.x + self.width/2, self.y + self.height)
    def set_midtop(self, midtop):
        x, y = midtop
        self.x = x - self.width/2
        self.y = y - self.height
    midtop = property(get_midtop, set_midtop)

    def get_midbottom(self):
        return (self.x + self.width/2, self.y)
    def set_midbottom(self, midbottom):
        x, y = midbottom
        self.x = x - self.width/2
        self.y = y
    midbottom = property(get_midbottom, set_midbottom)

    def get_midleft(self):
        return (self.x, self.y + self.height/2)
    def set_midleft(self, midleft):
        x, y = midleft
        self.x = x
        self.y = y - self.height/2
    midleft = property(get_midleft, set_midleft)

    def get_midright(self):
        return (self.x + self.width, self.y + self.height/2)
    def set_midright(self, midright):
        x, y = midright
        self.x = x - self.width
        self.y = y - self.height/2
    midright = property(get_midright, set_midright)
 
    def get_topleft(self):
        return (self.x, self.y + self.height)
    def set_topleft(self, pos):
        x, y = pos
        self.x = x
        self.y = y - self.height
    topleft = property(get_topleft, set_topleft)
 
    def get_topright(self):
        return (self.x + self.width, self.y + self.height)
    def set_topright(self, pos):
        x, y = pos
        self.x = x - self.width
        self.y = y - self.height
    topright = property(get_topright, set_topright)
 
    def get_bottomright(self):
        return (self.x + self.width, self.y)
    def set_bottomright(self, pos):
        x, y = pos
        self.x = x - self.width
        self.y = y
    bottomright = property(get_bottomright, set_bottomright)
 
    def get_bottomleft(self):
        return (self.x, self.y)
    def set_bottomleft(self, pos):
        self.x, self.y = pos
    bottomleft = property(get_bottomleft, set_bottomleft)

