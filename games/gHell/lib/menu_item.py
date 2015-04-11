import qgl
import leafs
from data import filepath

class MenuItem:
    
    def __init__(self, caption, callback, x, y):
        font = filepath('You Are Loved.ttf')
        figure = leafs.TextoAlineado(caption, font, size=1000, alignx=0.5, aligny=0.5)
        self.group = qgl.scene.Group()
        self.group.add(figure)
        self.group.translate = (x, y, 0.0)
        self.group.selectable = True
        self.final_zoom = 4
        self.zoom = 4
        self.x, self.y = x, y
        self.callback = callback
        
    def enter(self):
        self.final_zoom = 6.0

    def leave(self):
        self.final_zoom = 4.0

    def update(self):
        dz = (self.final_zoom - self.zoom)
        self.zoom = dz / 4.0
        self.group.scale = (self.zoom, self.zoom, 1)
        w, h, _ = self.group.scale
        #self.group.translate = (self.x, self.y, 1)

    def on_select(self):
        self.callback()
