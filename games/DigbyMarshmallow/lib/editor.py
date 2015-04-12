from pyglet import app
from pyglet import window
from pyglet.window import key
from pyglet.window import mouse
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED
from pyglet.gl import *

import mode
import squirtle
import caterpie
import world
import data
from vector import Vector
import math
import oxygen

import config
from common import *
from constants import *
import os

import door

from content import swags, enemies, oxygens, switches, signposts

GRID_DEF = 500.0 / 3.0


## TOOLS
########

class Tool(object):
    icon = None
    hotkey = None
    def __init__(self, editor):
        self.editor = editor
        self.world = editor.world
    def select(self):
        pass
    def deselect(self):
        pass
    def press(self, sym, mods):
        pass
    def hold(self, sym, mods):
        pass
    def lclick(self, x, y, mods):
        pass
    def rclick(self, x, y, mods):
        pass
    def ldrag(self, x, y, mods):
        pass
    def rdrag(self, x, y, mods):
        pass
    def release(self):
        pass
    def entry(self, text):
        pass
    def tick(self):
        pass
    def draw(self):
        pass


class PlaceObjects(Tool):
    palette = ()
    def select(self):
        self.selected = self.palette[0]
        self.pos = None
        self.angle = 0.0
        self.scale = 1.0
        if self.editor.world.static:
            self.z = max(obj.z for obj in self.editor.world.static) + 1
        else:
            self.z = 0
    def press(self, sym, mods):
        if sym == key.Z:
            idx = (self.palette.index(self.selected) + 1) % len(self.palette)
            self.selected = self.palette[idx]
        elif sym == key.X:
            idx = (self.palette.index(self.selected) - 1) % len(self.palette)
            self.selected = self.palette[idx]
        elif (sym == key.W or sym == key.E) and mods & key.MOD_SHIFT:
            self.angle = (self.angle // 45 + 1) * 45
        elif (sym == key.R or sym == key.T) and mods & key.MOD_SHIFT:
            self.angle = (self.angle // 45 - 1) * 45
        elif sym == key.D and mods & key.MOD_SHIFT:
            scale = (math.floor(self.scale * 3) + 2) / 3
            self.scale = scale
        elif sym == key.S and mods & key.MOD_SHIFT:
            scale = (math.ceil(self.scale * 3) - 2) / 3
            self.scale = max(1.0 / 3.0, scale)
    def hold(self, sym, mods):
        if sym == key.W and not mods & key.MOD_SHIFT:
            self.angle += 3.0
        elif sym == key.E and not mods & key.MOD_SHIFT:
            self.angle += 0.3
        elif sym == key.R and not mods & key.MOD_SHIFT:
            self.angle -= 0.3
        elif sym == key.T and not mods & key.MOD_SHIFT:
            self.angle -= 3.0
        elif sym == key.D and not mods & key.MOD_SHIFT:
            self.scale *= 1.1
        elif sym == key.S and not mods & key.MOD_SHIFT:
            self.scale /= 1.1
    def lclick(self, x, y, mods):
        if mods &  key.MOD_SHIFT:
            x, y = (Vector((x, y)) // GRID_DEF + (0.5, 0.5)) * GRID_DEF
        obj = world.StaticObject(self.selected, (x, y), self.angle, self.scale, z=self.z)
        self.z += 1
        self.editor.world.static.add(obj)
        self.pos = None
    def draw(self):
        x, y = self.editor.mouse_world_pos
        if self.editor.snap_on:
            x, y = (Vector((x, y)) // GRID_DEF + (0.5, 0.5)) * GRID_DEF
        self.selected.draw(x, y, angle=self.angle, scale=self.scale)


class ModifyObjects(Tool):
    def update_selected(self):
        pass
    def select(self):
        self.selected = None
        self.candidates = None
        self.selected_pos = False
        self.drag_offset = None
        self.hash = None
    def lclick(self, x, y, mods):
        if self.selected is not None and (x, y) not in self.selected.bb:
            self.selected = None
        if self.selected is None:
            self.candidates = []
            for wo in self.hash:
                if (x, y) in wo.bb:
                    self.candidates.append(wo)
            if self.candidates:
                self.selected = self.candidates[0]
                if len(self.candidates) > 1:
                    self.selected_pos = True
    def press(self, sym, mods):
        if self.selected_pos and sym == key.TAB:
            cur_idx = self.candidates.index(self.selected)
            new_idx = (cur_idx + 1) % len(self.candidates)
            self.selected = self.candidates[new_idx]
        elif self.selected is not None:
            self.hash.remove(self.selected)
            if (sym == key.W or sym == key.E) and mods & key.MOD_SHIFT:
                bearing = self.selected.bearing
                self.selected.bearing = (bearing // 45 + 1) * 45
            elif (sym == key.R or sym == key.T) and mods & key.MOD_SHIFT:
                bearing = self.selected.bearing
                self.selected.bearing = (bearing // 45 - 1) * 45
            elif sym == key.D and mods & key.MOD_SHIFT:
                scale = (math.floor(self.selected.scale * 3) + 2) / 3
                self.selected.scale = scale
            elif sym == key.S and mods & key.MOD_SHIFT:
                scale = (math.ceil(self.selected.scale * 3) - 2) / 3
                self.selected.scale = max(1.0 / 3.0, scale)
            elif sym == key.BRACKETLEFT:
                if self.hash:
                    self.selected.z = min(obj.z for obj in self.hash) - 1
            elif sym == key.BRACKETRIGHT:
                if self.hash:
                    self.selected.z = max(obj.z for obj in self.hash) + 1
            elif sym == key.BACKSPACE:
                self.selected = None
                self.candidates = None
            else:
                self.hash.add(self.selected)
                return
            if self.selected is not None:
                self.update_selected()
                self.hash.add(self.selected)
            self.selected_pos = False
    def hold(self, sym, mods):
        if self.selected:
            self.hash.remove(self.selected)
            if sym == key.W and not mods & key.MOD_SHIFT:
                self.selected.bearing += 3.0
            elif sym == key.E and not mods & key.MOD_SHIFT:
                self.selected.bearing += 0.3
            elif sym == key.R and not mods & key.MOD_SHIFT:
                self.selected.bearing -= 0.3
            elif sym == key.T and not mods & key.MOD_SHIFT:
                self.selected.bearing -= 3.0
            elif sym == key.D and not mods & key.MOD_SHIFT:
                self.selected.scale *= 1.1
            elif sym == key.S and not mods & key.MOD_SHIFT:
                self.selected.scale /= 1.1
            else:
                self.hash.add(self.selected)
                return
            self.update_selected()
            self.hash.add(self.selected)
            self.selected_pos = False
    def ldrag(self, x, y, mods):
        if self.selected:
            self.hash.remove(self.selected)
            self.selected_pos = False
            if self.drag_offset is None:
                self.drag_offset = self.selected.pos - (x, y)
            if mods & key.MOD_SHIFT:
                pos = self.drag_offset + (x, y)
                self.selected.pos = (Vector(pos) // GRID_DEF + (0.5, 0.5)) * GRID_DEF
            else:
                self.selected.pos = self.drag_offset + (x, y)
            self.update_selected()
            self.hash.add(self.selected)
    def release(self):
        self.drag_offset = None


class PlaceScenery(PlaceObjects):
    icon = data.load_image("icons/tree.svgz")
    def select(self):
        self.palette = data.load_palette(self.editor.current_style,
                anchor_x="center", anchor_y="center")
        super(PlaceScenery, self).select()


class ModifyScenery(ModifyObjects):
    icon = data.load_image("unneed/block.svgz")
    def update_selected(self):
        self.selected.update()
    def select(self):
        super(ModifyScenery, self).select()
        self.hash = self.editor.world.static
    def draw(self):
        if self.selected is not None:
            glColor3f(0.0, 1.0, 0.0)
            glLineWidth(3.0)
            glBegin(GL_LINE_LOOP)
            for pt in self.selected.points:
                glVertex2f(pt[0], pt[1])
            glEnd()
            glLineWidth(1.0)


class PlaceActorTool(Tool):
    img_svg = None
    def select(self):
        super(PlaceActorTool, self).select()
        self.last_added = None
        self.select_actor(0)
        self.scale = 1.0
        self.angle = 0.0
    def select_actor(self, id):
        id %= len(self.actors)
        id += len(self.actors)
        id %= len(self.actors)
        self.actor_class, self.actor_radius, self.actor_name, self.actor_img = self.actors[id][:4]
        self.actor_img = os.path.join(self.img_path, self.actor_img)
        self.actor_extras = dict(zip(self.actor_class.extra_keys, self.actors[id][4:]))
        for k, v in self.actor_extras.iteritems():
            if isinstance(v, str) and v.endswith('.svgz'):
                self.actor_extras[k] = os.path.join(self.img_path, v)
        self.img_svg = squirtle.SVG(data.file_path(self.actor_img), anchor_x='center', anchor_y='center')
        self.selected_id = id
    def lclick(self, x, y, mods):
        if mods & key.MOD_SHIFT:
            x, y = (Vector((x, y)) // GRID_DEF + (0.5, 0.5)) * GRID_DEF
        self.last_added = self.actor_class(None, pos=(x, y), radius=self.actor_radius, image_file=self.actor_img, name=self.actor_name, bearing=self.angle, **self.actor_extras)
        self.editor.world.actors.add(self.last_added)
    def press(self, sym, mods):
        if sym == key.Z:
            self.select_actor(self.selected_id - 1)
        elif sym == key.X:
            self.select_actor(self.selected_id + 1)
        elif (sym == key.W or sym == key.E) and mods & key.MOD_SHIFT:
            self.angle = (self.angle // 45 + 1) * 45
        elif (sym == key.R or sym == key.T) and mods & key.MOD_SHIFT:
            self.angle = (self.angle // 45 - 1) * 45
    def hold(self, sym, mods):
        if sym == key.W and not mods & key.MOD_SHIFT:
            self.angle += 3.0
        elif sym == key.E and not mods & key.MOD_SHIFT:
            self.angle += 0.3
        elif sym == key.R and not mods & key.MOD_SHIFT:
            self.angle -= 0.3
        elif sym == key.T and not mods & key.MOD_SHIFT:
            self.angle -= 3.0
    def draw(self):
        if self.img_svg:
            x, y = self.editor.mouse_world_pos
            if self.editor.snap_on:
                x, y = (Vector((x, y)) // GRID_DEF + (0.5, 0.5)) * GRID_DEF
            self.img_svg.draw(x, y, radius=self.actor_radius, angle=self.angle)


class ModifyActors(ModifyObjects):
    icon = data.load_image("unneed/block.svgz")
    def select(self):
        super(ModifyActors, self).select()
        self.hash = self.editor.world.actors
    def update_selected(self):
        if isinstance(self.selected, oxygen.Oxygen):
            for obj in self.editor.world.actors:
                if isinstance(obj, oxygen.Oxygen):
                    obj.is_initial = False
                self.selected.is_initial = True
    def draw(self):
        if self.selected is not None:
            glColor3f(0.0, 1.0, 0.0)
            glLineWidth(3.0)
            glBegin(GL_LINE_LOOP)
            r = self.selected.radius
            for i in xrange(16):
                a = 2 * math.pi * i / 16
                x, y = self.selected.pos + (r * math.cos(a), r * math.sin(a))
                glVertex2f(x, y)
            glEnd()
            glLineWidth(1.0)


class PlaceSwagTool(PlaceActorTool):
    icon = squirtle.SVG(data.file_path("images/icons/swag.svgz"))
    actors = swags.swags
    img_path = 'images/swag'


class PlaceEnemyTool(PlaceActorTool):
    icon = squirtle.SVG(data.file_path("images/icons/enemy.svgz"))
    actors = enemies.enemies
    img_path = 'images'

class PlaceOxygenTool(PlaceActorTool):
    icon = squirtle.SVG(data.file_path("images/all/oxygen.svgz"))
    actors = oxygens.oxygens
    img_path = 'images/all'
    def lclick(self, x, y, mods):
        super(PlaceOxygenTool, self).lclick(x, y, mods)
        self.editor.show_entry("Enter oxygen amount (seconds)...")
        self.entry_oxygen = None
        self.entry_pipe = None
        for obj in self.editor.world.actors:
            if isinstance(obj, oxygen.Oxygen):
                obj.is_initial = False
            self.last_added.is_initial = True
    def entry(self, text):
        if self.entry_oxygen is None:
            if not text.isdigit():
                self.editor.show_entry("Enter oxygen amount (seconds)...")
            else:
                self.entry_oxygen = int(text) * 60
                self.editor.show_entry("Enter pipe length (m)...")
        elif self.entry_pipe is None:
            if not text.isdigit():
                self.editor.show_entry("Enter pipe length (m)...")
            else:
                self.entry_pipe = int(text) * 100
                self.last_added.capacity = self.entry_oxygen
                self.last_added.pipe_length = self.entry_pipe

class PlaceSwitchTool(PlaceActorTool):
    icon = data.load_image("switches/switchoff.svgz")
    actors = switches.switches
    img_path = 'images/switches'

class PlaceSignpostTool(PlaceActorTool):
    icon = squirtle.SVG(data.file_path("images/all/signpost.svgz"))
    actors = signposts.signposts
    img_path = 'images/all'
    def lclick(self, x, y, mods):
        super(PlaceSignpostTool, self).lclick(x, y, mods)
        self.editor.show_entry('Enter text key...')
    def entry(self, text):
        self.last_added.text_key = text

class PlaceDoorTool(Tool):
    icon = squirtle.SVG(data.file_path("images/icons/door.svgz"))

    def select(self):
        super(PlaceDoorTool, self).select()
        self.start = None
        
    def lclick(self, x, y, mods):
        if self.start:
            new_id = max(self.editor.world.doors.keys() + [0]) + 1
            self.editor.world.doors[new_id] = door.Door(None, self.start, (x, y))
            self.start = None
        else:
            self.start = (x, y)

    def draw(self):
        if self.start:
            x, y = self.editor.mouse_world_pos
            glLineWidth(3)
            glBegin(GL_LINES)
            glVertex2f(*self.start)
            glVertex2f(x, y)
            glEnd()
            glLineWidth(1)

class LinkDoorTool(Tool):
    icon = squirtle.SVG(data.file_path("images/icons/door.svgz"))
    colors = {'toggle': (1,1,0),
              'open': (0,1,0),
              'close': (1,0,0),
              '': (0,0,1)}
    
    modes = ['toggle', 'open', 'close', '']
    def select(self):
        super(LinkDoorTool, self).select()
        self.switch = None
        self.mode = 'toggle'
    
    def cycle_modes(self):
        n = self.modes.index(self.mode)
        self.mode = self.modes[(n+1) % len(self.modes)]
    def lclick(self, x, y, mods):
        for act in self.editor.world.actors:
            if isinstance(act, door.Switch) and (act.pos - (x, y)).length < act.radius:
                self.switch = act
                return
        if self.switch:
            for id, my_door in self.editor.world.doors.items():
                dist = (my_door.ls.closest_point(Vector((x,y))) - (x, y)).length
                if dist < my_door.thickness:
                    if self.mode:
                        self.switch.doors[id] = self.mode
                    else:
                        del self.switch.doors[id]
    
    def press(self, sym, mods):
        if sym == key.TAB:
            self.cycle_modes()
    def draw(self):
        if self.switch:
            x, y = self.editor.mouse_world_pos
            glLineWidth(3)
            glBegin(GL_LINES)
            glColor3f(*self.colors[self.mode])
            glVertex2f(*self.switch.pos)
            glVertex2f(x, y)
            for id, mode in self.switch.doors.items():
                if mode:
                    glColor3f(*self.colors[mode])
                    glVertex2f(*self.switch.pos)
                    glVertex2f(*self.editor.world.doors[id].pos)
            glEnd()
            glLineWidth(1)

class CycleThemes(Tool):
    icon = data.load_image("background/space.svgz")
    def select(self):
        self.editor.cycle_themes()


class Save(Tool):
    icon = data.load_image("icons/save.svgz")
    def select(self):
        self.editor.show_entry("Enter the filename...")
    def entry(self, text):
        filename = text + ".stage"
        data.save_stage(filename, self.editor.world)


class Load(Tool):
    icon = data.load_image("icons/load.svgz")
    def select(self):
        self.editor.show_entry("Enter the filename...")
    def entry(self, text):
        filename = text + ".stage"
        self.editor.world = world.EditableWorld(data.load_stage(filename))


AVAILABLE_TOOLS = [
    PlaceScenery,
    ModifyScenery,
    CycleThemes,
    PlaceSwagTool,
    PlaceEnemyTool,
    PlaceOxygenTool,
    PlaceSwitchTool,
    PlaceSignpostTool,
    PlaceDoorTool,
    LinkDoorTool,
    ModifyActors,
    Save,
    Load,
]


## EDIT MODE
############

class EditorMode(mode.Mode):
    name = "editor"

    def __init__(self):
        self.world = world.EditableWorld()
        self.mouse_x, self.mouse_y = (0, 0)
        self.toolbox = [t(self) for t in AVAILABLE_TOOLS]
        
        self.current_tool = None
        self.previous_tool = None
        self.prepare_toolicons()

        self.entry = caterpie.TextEntry(
            xpos = 0.2, ypos = 0.2, width = 0.6, height = 0.6,
            padding = TOOL_PADDING, margin = TOOL_MARGIN,
            font_name = "Arial", font_size = 0.04,
            callback = self.entry_callback,
        )
        
        self.camera_pos = Vector((0, 0))
        self.camera_zoom = 1
        self.camera_velocity = Vector((0, 0))
        self.camera_zoom_rate = 1
        
        self.styles = data.load_styles()
        self.current_style = self.styles[0]
        self.cycle_themes()

        self.holding_mods = {}
        self.holding_keys = set()

    @property
    def snap_on(self):
        return key.LSHIFT in self.holding_keys or key.RSHIFT in self.holding_keys
    
    def cycle_themes(self):
        if self.current_style is None:
            self.current_style = self.styles[0]
        else:
            idx = self.styles.index(self.current_style)
            self.current_style = self.styles[(idx + 1) % len(self.styles)]
        background_path = ["background", self.current_style + ".svgz"]
        self.world.background = data.load_image(background_path,
                anchor_x='center', anchor_y='center')
        
    def prepare_toolicons(self):
        tw, tx = min(0.1, 1.0 / len(self.toolbox)), 0.0

        self.toolicons = []
        for t in self.toolbox:
            icon = caterpie.ImageButton(
                xpos = tx, ypos = 0.0, width = tw, height = tw,
                padding = TOOL_PADDING, margin = TOOL_MARGIN,
                outline = TOOL_OUTLINE_NORMAL,
                background = TOOL_BACKGROUND_NORMAL,
                callback = (self.select_tool, t),
                square = "width", graphic = t.icon,
            )
            self.toolicons.append(icon)
            tx += tw

    def select_tool(self, tool):
        if self.current_tool is not None:
            self.current_tool.deselect()
            self.previous_tool = self.current_tool
            idx = self.toolbox.index(self.current_tool)
            self.toolicons[idx].outline = TOOL_OUTLINE_NORMAL
            self.toolicons[idx].background = TOOL_BACKGROUND_NORMAL
            self.current_tool = None
        if tool is not None:
            self.current_tool = tool
            idx = self.toolbox.index(self.current_tool)
            self.toolicons[idx].outline = TOOL_OUTLINE_HIGHLIGHT
            self.toolicons[idx].background = TOOL_BACKGROUND_HIGHLIGHT
            tool.select()

    def show_entry(self, default):
        self.entry.default = default
        self.entry.show(self.window)

    def entry_callback(self, text):
        if self.current_tool is not None:
            self.current_tool.entry(text)

    def connect(self, control):
        self.control = control
        self.window = control.window
        for t in self.toolicons:
            self.window.push_handlers(t)
            t.window = self.window
        self.camera_scale = self.window.height / float(SCREEN_HEIGHT)

    def disconnect(self):
        for ti in self.toolicons:
            ti.window = None
            self.window.remove_handlers(ti)
        self.window = None
        self.control = None

    def set_mouse(self, x, y):
        self.mouse_x, self.mouse_y = x, y
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_drag(self, x, y, dx, dy, btns, mods):
        self.set_mouse(x, y)
        wx, wy = self.mouse_to_world(x, y)
        if self.current_tool is None:
            return EVENT_UNHANDLED

        if btns & mouse.LEFT:
            btn = mouse.LEFT
        elif btns & mouse.RIGHT:
            btn = mouse.RIGHT
        else:
            btn = None
        
        if btn == mouse.RIGHT:
            self.current_tool.rdrag(wx, wy, mods)
        elif btn == mouse.LEFT and mods & key.MOD_CTRL:
            self.current_tool.rdrag(wx, wy, mods)
        elif btn == mouse.LEFT:
            self.current_tool.ldrag(wx, wy, mods)
        else:
            return EVENT_UNHANDLED
        return EVENT_HANDLED
    
    def on_mouse_press(self, x, y, btn, mods):
        self.set_mouse(x, y)
        wx, wy = self.mouse_to_world(x, y)
        if self.current_tool is None:
            return EVENT_UNHANDLED

        if btn == mouse.RIGHT:
            self.current_tool.rclick(wx, wy, mods)
        elif btn == mouse.LEFT and mods & key.MOD_CTRL:
            self.current_tool.rclick(wx, wy, mods)
        elif btn == mouse.LEFT:
            self.current_tool.lclick(wx, wy, mods)
        else:
            return EVENT_UNHANDLED
        return EVENT_HANDLED

    def on_mouse_release(self, x, y, btn, mods):
        self.set_mouse(x, y)
        if self.current_tool is None:
            return EVENT_UNHANDLED
        self.current_tool.release()
        return EVENT_UNHANDLED
        
    def on_key_press(self, sym, mods):
        self.holding_keys.add(sym)
        self.holding_mods[sym] = mods
        if sym == key.ESCAPE:
            self.control.switch_handler("menu")
            return EVENT_HANDLED
        elif sym == key.LEFT:
            self.camera_velocity += (-10, 0)
        elif sym == key.RIGHT:
            self.camera_velocity += (10, 0)
        elif sym == key.UP:
            self.camera_velocity += (0, 10)
        elif sym == key.DOWN:
            self.camera_velocity += (0, -10)
        elif sym == key.Q:
            self.camera_zoom_rate = 1.05
        elif sym == key.A:
            self.camera_zoom_rate = 0.95
        elif self.current_tool is not None:
            self.current_tool.press(sym, mods)
        return EVENT_HANDLED

    def on_key_release(self, sym, mods):
        self.holding_keys.discard(sym)
        self.holding_mods.pop(sym, None)
        if sym == key.LEFT:
            self.camera_velocity -= (-10, 0)
        elif sym == key.RIGHT:
            self.camera_velocity -= (10, 0)
        elif sym == key.UP:
            self.camera_velocity -= (0, 10)
        elif sym == key.DOWN:
            self.camera_velocity -= (0, -10)
        elif sym in (key.Q, key.A):
            self.camera_zoom_rate = 1
    
    def mouse_to_world(self, x, y):
        sw, sh = self.window.get_size()
        rel_pos = Vector((x - sw / 2, y - sh / 2))
        scaled_pos = rel_pos / (self.camera_scale * self.camera_zoom)
        return self.camera_pos + scaled_pos

    @property
    def mouse_world_pos(self):
        return self.mouse_to_world(self.mouse_x, self.mouse_y)

    def draw_world(self):
        self.world.background.draw(self.window.width * 0.3, self.window.height / 2, radius=(.7*self.window.width + .3*self.window.height))
        glPushMatrix()
        glTranslatef(self.window.width/2, self.window.height/2, 0)
        s = self.camera_scale * self.camera_zoom
        glScalef(s, s, s)
        glTranslatef(-self.camera_pos.x, -self.camera_pos.y, 0)

        for obj in sorted(self.world.static, key=lambda x: x.z):
            x, y = obj.pos
            a = obj.bearing
            s = obj.scale
            obj.image.draw(x, y, angle=a, scale=s)
#            glColor3f(0.0, 1.0, 0.0)
#            glBegin(GL_LINE_LOOP)
#            for pt in obj.points:
#                glVertex2f(pt[0], pt[1])
#            glEnd()
        
        for act in self.world.actors:
            act.draw()
        
        for door in self.world.doors.values():
            door.draw()
        if self.current_tool is not None:
            self.current_tool.draw()

        for obj in self.world.actors:
            glLineWidth(2.0)
            if isinstance(obj, oxygen.Oxygen):
                glColor3f(1.0, 0.0, 0.0)
                glBegin(GL_LINE_LOOP)
                r = obj.pipe_length + PLAYER_RADIUS / 2
                for i in xrange(48):
                    a = 2 * math.pi * i / 48
                    delta = (r * math.cos(a), r * math.sin(a))
                    x, y = obj.pos + delta
                    glVertex2f(x, y)
                glEnd()
                glBegin(GL_LINE_LOOP)
                r = obj.pipe_length - PLAYER_RADIUS / 2
                for i in xrange(48):
                    a = 2 * math.pi * i / 48
                    delta = (r * math.cos(a), r * math.sin(a))
                    x, y = obj.pos + delta
                    glVertex2f(x, y)
                glEnd()
            glLineWidth(1.0)
        
        self.draw_grid()
        
        glPopMatrix()

    def draw_grid(self, gridsize=GRID_DEF):
        lo_x, lo_y = self.mouse_to_world(0, 0)
        hi_x, hi_y = self.mouse_to_world(self.window.width, self.window.height)
        lo_x = int(math.floor(lo_x / gridsize) * gridsize)
        lo_y = int(math.floor(lo_y / gridsize) * gridsize)
        hi_x = int(math.ceil(hi_x / gridsize) * gridsize)
        hi_y = int(math.ceil(hi_y / gridsize) * gridsize)
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        x = lo_x
        while x <= hi_x:
            glVertex2f(x, lo_y)
            glVertex2f(x, hi_y)
            x += gridsize
        y = lo_y
        while y <= hi_y:
            glVertex2f(lo_x, y)
            glVertex2f(hi_x, y)
            y += gridsize
        glEnd()

    def draw_hud(self):
        for ti in self.toolicons:
            ti.draw()
        if self.entry.show_entry:
            self.entry.draw()

    def on_draw(self):
        self.window.clear()
        self.draw_world()
        self.draw_hud()

    def tick(self):
        self.camera_pos += self.camera_velocity / self.camera_zoom
        self.camera_zoom *= self.camera_zoom_rate
        if self.current_tool is not None:
            for sym in self.holding_keys:
                self.current_tool.hold(sym, self.holding_mods[sym])
