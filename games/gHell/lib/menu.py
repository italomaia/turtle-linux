import qgl
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import menu_item

class Menu:
    
    def __init__(self, scene, items, initial_option=0):        
        self.items = items
        self.index = initial_option
        self.menuGroup = qgl.scene.Group()
        self._create_items_text(self.menuGroup, items)
        scene.add_group(self.menuGroup)
        scene.accept()
        self.instances[self.index].enter()
        self.scene = scene

    def update(self, dt=0):
        for x in self.instances:
            x.update()
    
    def update_event(self, event):
        if event.type == MOUSEMOTION:
            print event
            self.on_mouse_motion(event)
        elif event.type == MOUSEBUTTONDOWN:
            self.on_mouse_click(event)
        elif event.type == KEYDOWN:
            if event.key == K_DOWN:
                self.move_down()
            elif event.key == K_UP:
                self.move_up()
            elif event.key in [K_RETURN, K_SPACE]:
                self.select()

    def on_mouse_motion(self, event):
        picker = self.scene.picker
        picker.set_position(event.pos)
        self.scene.root_node.accept (picker)
        if picker.hits:
            for k in picker.hits: #self.moves(picker.hits)
                pass

    def on_mouse_click(self, event):
        picker = self.scene.picker
        picker.set_position(event.pos)
        self.scene.root_node.accept (picker)
        if picker.hits:
            for g in picker.hits: #self.moves(picker.hits)
                entry = self.map[g]
                entry.on_select()
                return

    def move_down(self):
        self._move(1)

    def move_up(self):
        self._move(-1)

    def _move(self, dy):

        self.instances[self.index].leave()
        self.index += dy
        max = len(self.items) - 1

        if self.index < 0:
            self.index = max
        elif self.index > max:
            self.index = 0

        self.instances[self.index].enter()

    def select(self):
        self.instances[self.index].on_select()

    def _create_items_text(self, group, items):
        ITEM_SIZE=35
        self.map = {}
        dy = -(len(items)/2*ITEM_SIZE)
        self.instances = []
        for (text, callback) in items:
            new = menu_item.MenuItem(text, callback, 0.0, -dy)
            group.add(new.group)
            dy += ITEM_SIZE
            self.instances.append(new)
            self.map[new.group]=new
            
    def enable(self):
        self.menuGroup.enable()

    def disable(self):
        self.menuGroup.disable()

if __name__ == '__main__':
    
    m = Menu([('uno', None), ('dos', None)])
    m.move_up()
