"""Interface components based on Pyglet objects.

"""

from __future__ import division

from pyglet import image
from pyglet import graphics
from pyglet import text
from pyglet.window import key
from pyglet.window import mouse
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED
from pyglet.gl import *

import data

import config
from common import *
from constants import *

__all__ = [

    # Style management
    "Style", "get_default_style", "set_default_style",

    # Abstract base classes
    "InterfaceComponent", "MenuOption", "Menu",

    # Text based components
    "TextBox", "TextEntry", "TextMenuOption", "TextMenu",

    # Image based components
    "ImageBox", "ImageButton"

]




## Helper functions
###################

_vdata = ('v2f', [0, 0, 1, 0, 1, 1, 0, 1])

def draw_rect(pos, size, outline, background):
    """Draw a straightforward rectangle.

    :Parameters:
        `pos` : (float, float)
            The coordinates of the lower left corner.
        `size` : (float, float)
            The dimensions of the rectangle.
        `outline` : (float, float, float, [float])
            The GL color in which to draw the outline.
        `background` : (float, float, float, [float])
            The GL color in which to shade the interior.

    """
    (x, y), (w, h) = pos, size
    def color(color):
        return glColor4f(*color)
    glPushMatrix()
    glTranslatef(x, y, 0.0)
    glScalef(w, h, 1.0)
    if background is not None:
        color(background)
        graphics.draw(4, GL_QUADS, _vdata)
    if outline is not None:
        color(outline)
        graphics.draw(4, GL_LINE_LOOP, _vdata)
    glPopMatrix()




## Style objects
################

class Style(object):
    """Style objects are used to customise global interface.

    """

    def __init__(self, **kwds):
        """Create a Style object.

        All arguments are stored as instance attributes.

        """
        for name in kwds:
            setattr(self, name, kwds[name])


default_style = None

def get_default_style():
    """Retrieve the default style.

    """
    return default_style


def set_default_style(style):
    """Set a default style.

    :Parameters:
        `style` : Style
            The style object to set.

    """
    global default_style
    default_style = style




## Interface components
#######################

class InterfaceComponentMeta(type):
    """Metaclass for interface components.

    """

    def __init__(self, name, bases, dict):
        """Create an InterfaceComponentMeta object.

        """
        name_trees = ("keyword_names", "dependent_names", "cache_names")
        for name in name_trees:
            own = dict.get(name, frozenset())
            for b in bases:
                base = getattr(b, name, frozenset())
                own = base | own
            setattr(self, name, own)


class InterfaceComponent(object):
    """Base class for interface components.

    """

    ## Metaclass
    ############

    __metaclass__ = InterfaceComponentMeta

    ## Name trees
    #############

    keyword_names = frozenset([
        "xpos", "ypos", "width", "height", "halign", "valign", "padding",
        "margin", "outline", "background", "expand", "direction", "scrolling",
        "sensitivity", "visible", "window", "proxy", "parent",
    ])

    dependent_names = frozenset([
        "xpos", "ypos", "width", "height", "halign", "valign", "padding",
        "margin", "expand", "direction", "window", "proxy",
    ])

    cache_names = frozenset([
        "scaling_factors", "box_shape", "content_shape", "scroll_max",
        "scroll_length", "scroll_offset",
    ])

    ## Default values
    #################

    xpos = 0.0
    ypos = 0.0
    width = 0.0
    height = 0.0
    halign = "center"
    valign = "center"
    padding = 0.0
    margin = 0.0
    outline = None
    background = None
    expand = None
    direction = "vertical"
    scrolling = False
    sensitivity = 0.1
    visible = True
    window = None
    proxy = None
    parent = None

    ## Constructor
    ##############

    def __init__(self, **kwds):
        """Create an InterfaceComponent object.

        :Parameters:
            `xpos` : float
                The x coordinate of the bounding box's bottom left corner.
            `ypos` : float
                The y coordinate of the bounding box's bottom left corner.
            `width` : float
                The width of the bounding box.
            `height` : float
                The height of the bounding box.
            `halign` : str [left, center, right]
                The horizontal alignment of the content.
            `valign` : str [bottom, center, top]
                The vertical alignment of the content.
            `padding` : float
                The distance between the content box and the content.
            `margin` : float
                The distance between the bounding box and the content box.
            `outline` : (float, float, float, [float])
                The GL color in which to outline the content box.
            `background` : (float, float, float, [float])
                The GL color in which to shade the content box.
            `expand` : str [horizontal, vertical, both]
                Whether to expand the content box to fill one or both dimensions
                of the bounding box. If not set content box wraps tightly.
            `direction` : str [horizontal, vertical]
                The direction in which the component scans and scrolls.
            `scrolling` : bool
                Whether or not the component is allowed to scroll.
            `sensitivity` : float
                The scroll sensitivity in proportion to the size of the
                bounding box.
            `visible` : bool
                Whether or not the component is inactive.
            `window` : pyglet.window.Window
                The pyglet Window object on which we are drawing. If not set
                then we interpret the measurements as absolute.
            `parent` : InterfaceComponent
                The interface component which is scrolling this one.
            `style` : Style
                The style object from which to acquire default values. If not
                set then the default style is used.

        """
        # Choose the appropriate style object.
        style = kwds.pop("style", default_style)
        for name in self.keyword_names:
            # Acquire the default value.
            value = getattr(self, name)
            # Override with the style value.
            value = getattr(style, name, value)
            # Set the instance attribute.
            setattr(self, name, value)
        for name in kwds.keys():
            assert name in self.keyword_names, "invalid argument %r" % name
            # Override with the keyword argument.
            setattr(self, name, kwds.pop(name))

        # Add as a child of the parent object.
        if self.parent is not None:
            self.parent.children.append(self)

        #: Current scroll value.
        self.scroll = 0.0

        #: Child components.
        self.children = []

    def __setattr__(self, name, value):
        """Clear cached attributes if a dependent attribute changes.

        """
        super(InterfaceComponent, self).__setattr__(name, value)
        if name in self.dependent_names:
            self.clear_cache()

    def __contains__(self, pos):
        """Check if the specified coordinates are inside the component.

        :Parameters:
            `pos` : tuple
                The x and y coordinates to test.

        """
        x, y = pos
        bx, by, bw, bh = self.box_shape
        in_x = bx <= x < bx + bw
        in_y = by <= y < by + bh
        return in_x and in_y

    ## Utility
    ##########

    def clear_cache(self):
        """Clear cached attributes.

        """
        for name in self.cache_names:
            delattr(self, name)

    @cached
    def scaling_factors(self):
        """The appropriate directional scalings.

        """
        sx, sy = 1.0, 1.0
        if self.window is not None:
            sx, sy = self.window.get_size()
        elif self.proxy is not None:
            sx, sy = self.proxy.get_shape()[2:]
        return sx, sy

    def scroll_coordinates(self, x, y):
        """Adjust the coordinates for the parents scroll amount.

        """
        if self.parent is not None:
            tx, ty = self.parent.scroll_vector
            return x - tx, y - ty
        return x, y

    def proxy_coordinates(self, x, y):
        if self.proxy is not None:
            sx, sy = self.proxy.get_shape()[:2]
            return x - sx, y - sy
        return x, y

    ## Scrolling
    ############

    @cached
    def scroll_max(self):
        """The maximum scroll value.

        """
        sx, sy = self.scaling_factors
        cx, cy, cw, ch = self.content_shape
        bx, by, bw, bh = self.box_shape
        padding = self.padding * sy
        if self.direction == "vertical":
            self.scroll_length = bh - 2 * padding
            scroll_max = ch - self.scroll_length
        elif self.direction == "horizontal":
            self.scroll_length = bw - 2 * padding
            scroll_max = cw - self.scroll_length
        return scroll_max

    @cached
    def scroll_length(self):
        """The length of the scrolling window.

        """
        sx, sy = self.scaling_factors
        cx, cy, cw, ch = self.content_shape
        bx, by, bw, bh = self.box_shape
        padding = self.padding * sy
        if self.direction == "vertical":
            scroll_length = bh - 2 * padding
            self.scroll_max = ch - scroll_length
        elif self.direction == "horizontal":
            scroll_length = bw - 2 * padding
            self.scroll_max = cw - scroll_length
        return scroll_length

    @cached
    def scroll_offset(self):
        """The display offset to the scroll value accounting for alignment.

        """
        if self.scroll_max > 0.0:
            if self.direction == "vertical":
                if self.valign == "center":
                    return -self.scroll_max / 2
                elif self.valign == "bottom":
                    return -self.scroll_max
            if self.direction == "horizontal":
                if self.halign == "center":
                    return -self.scroll_max / 2
                elif self.halign == "right":
                    return -self.scroll_max
        return 0.0

    @property
    def scroll_vector(self):
        """The scroll offset vector in the form (x, y).

        """
        scroll = self.scroll + self.scroll_offset
        if self.direction == "vertical":
            return (0.0, scroll)
        elif self.direction == "horizontal":
            return (-scroll, 0.0)
        return (0.0, 0.0)

    def scroll_relative(self, steps):
        """Scroll forwards a number of (possibly negative) relative steps.

        :Parameters:
            `steps` : int
                The number of steps (size relative to length) to scroll.

        """
        delta = steps * self.scroll_length * self.sensitivity
        self.scroll = max(0.0, min(self.scroll_max, self.scroll + delta))

    ## Event handlers
    #################

    def set_mouse(self, x, y):
        """Process the position of the mouse.

        """
        pass

    def on_mouse_press(self, x, y, btn, mods):
        """Process an 'on_mouse_press' event.

        """
        if not self.visible:
            return EVENT_UNHANDLED
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_release(self, x, y, btn, mods):
        """Process an 'on_mouse_release' event.

        """
        if not self.visible:
            return EVENT_UNHANDLED
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        """Process an 'on_mouse_motion' event.

        """
        if not self.visible:
            return EVENT_UNHANDLED
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_drag(self, x, y, dx, dy, btns, mods):
        """Process an 'on_mouse_drag' event.

        """
        if not self.visible:
            return EVENT_UNHANDLED
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_scroll(self, x, y, sx, sy):
        """Process an 'on_mouse_scroll' event.

        """
        if not self.visible:
            return EVENT_UNHANDLED
        self.set_mouse(x, y)
        if self.scrolling:
            self.scroll_relative(-sy)
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_mouse_enter(self, x, y):
        """Process an 'on_mouse_enter' event.

        """
        if not self.visible:
            return EVENT_UNHANDLED
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_leave(self, x, y):
        """Process an 'on_mouse_leave' event.

        """
        if not self.visible:
            return EVENT_UNHANDLED
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    ## Content shape
    ################

    @cached
    def content_shape(self):
        """The shape of the content in the format (x, y, w, h).

        """
        raise NotImplementedError("InterfaceComponent.content_shape")

    @property
    def content_pos(self):
        """The lower left corner of the content in the format (x, y).

        """
        return self.content_shape[0:2]

    @property
    def content_size(self):
        """The dimensions of the content in the format (w, h).

        """
        return self.content_shape[2:4]

    ## Box shape
    ############

    @cached
    def box_shape(self):
        """The shape of the content box in the format (x, y, w, h).

        """
        # Compute the absolute measurements.
        sx, sy = self.scaling_factors
        xpos, ypos = self.xpos * sx, self.ypos * sy
        width, height = self.width * sx, self.height * sy
        margin, padding = self.margin * sy, self.padding * sy
        content_x, content_y, content_w, content_h = self.content_shape

        # Compute the horizontal dimensions.
        if self.expand in ("horizontal", "both"):
            box_x = xpos + margin
            box_w = width - 2 * margin
        else:
            box_x = content_x - padding
            box_w = content_w + 2 * padding
        box_x = max(box_x, xpos + margin)
        box_w = min(box_w, width - 2 * margin)

        # Compute the vertical dimensions.
        if self.expand in ("vertical", "both"):
            box_y = ypos + margin
            box_h = height - 2 * margin
        else:
            box_y = content_y - padding
            box_h = content_h + 2 * padding
        box_y = max(box_y, ypos + margin)
        box_h = min(box_h, height - 2 * margin)

        return (box_x, box_y, box_w, box_h)

    @property
    def box_pos(self):
        """The lower left corner of the content box in the format (x, y).

        """
        return self.box_shape[0:2]

    @property
    def box_size(self):
        """The dimensions of the content box in the format (w, h).

        """
        return self.box_shape[2:4]

    @property
    def scissor_shape(self):
        """The dimensions of the scissor box in the format (x, y, w, h).

        """
        bx, by, bw, bh = map(int, self.box_shape)
        if self.proxy is not None:
            sx, sy, sw, sh = map(int, self.proxy.get_shape())
            mbx, mby = bx + sx + bw, by + sy + bh
            bx, by = max(sx, bx + sx), max(sy, by + sy)
            bw = min(mbx, sx + sw) - bx
            bh = min(mby, sy + sh) - by
        return bx + 1, by + 1, max(0, bw - 1), max(0, bh - 1)

    ## Drawing
    ##########

    def draw_box(self):
        """Draw the content box.

        """
        bx, by, bw, bh = self.box_shape
        draw_rect((bx, by), (bw, bh), self.outline, self.background)

    def draw_content(self):
        """Draw the content.

        """
        raise NotImplementedError("InterfaceComponent.draw_content")

    def draw(self):
        """Draw the component.

        """
        self.content_shape
        self.draw_box()
        glPushMatrix()
        if self.scrolling:
            glPushAttrib(GL_SCISSOR_BIT)
            glEnable(GL_SCISSOR_TEST)
            glScissor(*self.scissor_shape)
            tx, ty = self.scroll_vector
            glTranslatef(tx, ty, 0.0)
        self.draw_content()
        if self.scrolling:
            glDisable(GL_SCISSOR_TEST)
            glPopAttrib()
        glPopMatrix()




## Text box
###########

class TextBox(InterfaceComponent):
    """Component that displays multiline text.

    """

    ## Name trees
    #############

    keyword_names = frozenset([
        "font_name", "font_size", "color",
    ])

    dependent_names = frozenset([
        "font_name", "font_size", "color",
    ])

    ## Default values
    #################

    font_name = None
    font_size = 0.0
    color = (1.0,)*4
    text = u""

    ## Constructor
    ##############

    def __init__(self, **kwds):
        """Create a TextBox object.

        Additional arguments are handled by `InterfaceComponent`.

        :Parameters:
            `font_name` : str
                The name of the font family to use.
            `font_size` : float
                The size at which to draw the font.
            `color` : (float, float, float, [float])
                The color in which to draw the text.
            `text` : unicode
                The text to display.

        """
        _text = kwds.pop("text", u"")
        _html = kwds.pop("html", False)
        super(TextBox, self).__init__(**kwds)
        if _html:
            self.label = text.HTMLLabel(_text)
        else:
            self.label = text.Label(_text)

    def get_text(self):
        return self.label.text
    def set_text(self, value):
        if value != self.label.text:
            self.label.text = value
            self.clear_cache()
    text = property(get_text, set_text)

    ## Content shape
    ################

    @cached
    def content_shape(self):
        """The shape of the content in the format (x, y, w, h).

        """
        # Compute the absolute measurements.
        sx, sy = self.scaling_factors
        xpos, ypos = self.xpos * sx, self.ypos * sy
        width, height = self.width * sx, self.height * sy
        margin, padding = self.margin * sy, self.padding * sy
        label_margin = padding + margin

        # Configure the label properties.
        self.label.font_name = self.font_name
        self.label.font_size = self.font_size * sy
        self.label.width = width - 2 * label_margin
        self.label.anchor_x = "left"
        self.label.anchor_y = "bottom"
        self.label.color = tuple(map(lambda x: int(255 * x), self.color))
        self.label.multiline = True
        self.label.set_style("align", self.halign)

        # Compute the horizontal dimensions.
        content_w = self.label.content_width
        if self.halign == "left":
            content_x = xpos + label_margin
        elif self.halign == "center":
            content_x = xpos + (width - content_w) / 2
        elif self.halign == "right":
            content_x = xpos + width - content_w - label_margin
        self.label.x = xpos + label_margin

        # Compute the vertical dimensions.
        content_h = self.label.content_height
        if self.valign == "bottom":
            content_y = ypos + label_margin
        elif self.valign == "center":
            content_y = ypos + (height - content_h) / 2
        elif self.valign == "top":
            content_y = ypos + height - content_h - label_margin
        self.label.y = content_y

        return (content_x, content_y, content_w, content_h)

    ## Drawing
    ##########

    def draw_content(self):
        """Draw the content.

        """
        self.label.draw()




## Text entry
#############

class TextEntry(TextBox):
    """TextBox that receives and displays character data.

    """

    keyword_names = frozenset([
        "max_length", "callback", "default",
    ])

    max_length = 100
    callback = None
    default = ""

    def __init__(self, **kwds):
        """Create a TextEntry object.

        Additional arguments are handled by `TextBox`.

        :Parameters:
            `max_length` : int
                The maximum number of characters to display.
            `callback` : function
                The callback function to call when enter is pressed.
            `default` : unicode
                The default text to display.

        """
        super(TextEntry, self).__init__(**kwds)
        self.show_entry = False
        self.as_default = False

    def show(self, window):
        window.push_handlers(self)
        self.show_entry = True
        self.text = self.default
        self.as_default = True

    def hide(self):
        self.as_default = False
        self.show_entry = False
        self.window.remove_handlers(self)
        self.window = None

    def on_key_press(self, sym, mods):
        if self.show_entry:
            if sym == key.ENTER:
                self.hide()
                self.callback(self.text)
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_key_release(self, sym, mods):
        if self.show_entry:
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_text(self, text):
        if self.show_entry and text not in u"\r\n":
            old_text = "" if self.as_default else self.text
            new_text = old_text + text
            self.text = new_text[:self.max_length]
            self.as_default = False
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_text_motion(self, motion):
        if self.show_entry:
            if motion == key.MOTION_BACKSPACE:
                old_text = "" if self.as_default else self.text
                self.text = old_text[:-1]
                self.as_default = False
                return EVENT_HANDLED
        return EVENT_UNHANDLED

    def draw(self):
        if self.show_entry:
            super(TextEntry, self).draw()




## Generic menus
################

class MenuOption(object):
    """Base menu option implementation.

    """

    def __init__(self, menu, activate):
        """Create a MenuOption object.

        :Parameters:
            `menu` : Menu
                The Menu object of which the option is to compose a part.
            `activate` : function, tuple or None
                Either the function to call when activated, a tuple of the same
                function with arguments or None to indicate a non-activatable
                option.

        """
        self.menu = menu
        self.activate_func = activate
        self.selectable = (activate is not None)

    def __contains__(self, pos):
        """Check if the specified coordinates are inside the option.

        :Parameters:
            `pos` : tuple
                The x and y coordinates to test.

        """
        x, y = pos
        ox, oy, ow, oh = self.shape
        in_x = ox <= x < ox + ow
        in_y = oy <= y < oy + oh
        return in_x and in_y

    def activate(self):
        """Call the (possibly curried) function the option is bound to.

        """
        if self.activate_func is not None:
            if isinstance(self.activate_func, tuple):
                func = self.activate_func[0]
                args = self.activate_func[1:]
                func(*args)
            else:
                self.activate_func()

    @cached
    def shape(self):
        """The shape of the option in the format (x, y, w, h).

        """
        raise NotImplementedError("MenuOption.shape")

    @property
    def pos(self):
        """The bottom left corner of the option in the format (x, y).

        """
        return self.shape[0:2]

    @property
    def size(self):
        """The dimensions of the option in the format (w, h).

        """
        return self.shape[2:4]

    def position(self, x, y):
        """Set the position of the option.

        :Parameters:
            `x` : float
                The x coordinate to set.
            `y` : float
                The y coordinate to set.

        """
        raise NotImplementedError("MenuOption.position")

    def select(self):
        """Select the option.

        """
        raise NotImplementedError("MenuOption.select")

    def deselect(self):
        """Deselect the option.

        """
        raise NotImplementedError("MenuOption.deselect")

    def draw(self):
        """Draw the option.

        """
        raise NotImplementedError("MenuOption.draw")


class Menu(InterfaceComponent):
    """Base menu implementation

    """

    keyword_names = frozenset([
        "spacing",
    ])

    dependent_names = frozenset([
        "spacing",
    ])

    spacing = 0.0

    def __init__(self, **kwds):
        """Create a Menu object.

        Additional arguments are handled by `InterfaceComponent`.

        :Parameters:
            `spacing` : float
                The spacing between menu options.

        """
        super(Menu, self).__init__(**kwds)
        self.current = None
        self.options = []
        self.clear_options()

    def clear_cache(self):
        super(Menu, self).clear_cache()
        for opt in getattr(self, "options", ()):
            del opt.shape

    ## Options
    ##########

    def set_current(self, option):
        """Set the currently selected option to a given option.

        :Parameters:
            `option` : MenuOption
                The option to select.

        """
        if self.current is not None:
            self.current.deselect()
        self.current = None
        if option is not None:
            option.select()
            self.current = option

    def change_current_up(self):
        """Set the currently selected option to the previous selectable option.

        """
        selectable = []
        for opt in self.options:
            if opt.selectable:
                selectable.append(opt)
        if selectable:
            if self.current is None:
                new_opt = selectable[-1]
            else:
                cur_idx = selectable.index(self.current)
                new_opt = selectable[(cur_idx - 1) % len(selectable)]
            self.set_current(new_opt)
            self.scroll_option(new_opt)

    def change_current_down(self):
        """Set the currently selected option to the next selectable option.

        """
        selectable = []
        for opt in self.options:
            if opt.selectable:
                selectable.append(opt)
        if selectable:
            if self.current is None:
                new_opt = selectable[0]
            else:
                cur_idx = selectable.index(self.current)
                new_opt = selectable[(cur_idx + 1) % len(selectable)]
            self.set_current(new_opt)
            self.scroll_option(new_opt)

    def clear_options(self):
        """Clear all options from the menu.

        """
        self.current = None
        self.options = []
        self.clear_cache()

    ## Scrolling
    ############

    def scroll_option(self, option):
        """Scroll to position the given option in the viewable area.

        :Parameters:
            `option` : MenuOption
                The option to scroll to.

        """
        cx, cy, cw, ch = self.content_shape
        ox, oy, ow, oh = option.shape
        if self.direction == "vertical":
            min_offset = max(0.0, ch - (oy - cy) - self.scroll_length)
            max_offset = min(self.scroll_max, ch - (oy - cy) - oh)
        elif self.direction == "horizontal":
            min_offset = max(0.0, (ox - cx) + ow - self.scroll_length)
            max_offset = min(self.scroll_max, (ox - cx))
        self.scroll = max(min_offset, min(max_offset, self.scroll))

    ## Event handling
    #################

    def set_mouse(self, x, y):
        """Process the position of the mouse.

        """
        x, y = self.proxy_coordinates(x, y)
        if (x, y) not in self:
            self.set_current(None)
            return
        if self.scrolling:
            if self.direction == "vertical":
                y -= self.scroll + self.scroll_offset
            elif self.direction == "horizontal":
                x += self.scroll + self.scroll_offset
        for opt in self.options:
            if (x, y) in opt and opt.selectable:
                self.set_current(opt)
                break
        else:
            self.set_current(None)

    def on_mouse_release(self, x, y, btn, mods):
        """Activate option under cursor if any.

        """
        self.set_mouse(x, y)
        x, y = self.proxy_coordinates(x, y)
        if btn != mouse.LEFT:
            return EVENT_UNHANDLED
        if self.current is not None:
            self.current.activate()
            self.set_mouse(x, y)
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_key_press(self, sym, mods):
        """Keys can be used to operate the menu.

        """
        up_key = {"vertical" : key.UP, "horizontal" : key.RIGHT}
        down_key = {"vertical" : key.DOWN, "horizontal" : key.LEFT}
        if sym == up_key[self.direction]:
            self.change_current_up()
        elif sym == down_key[self.direction]:
            self.change_current_down()
        elif sym == key.ENTER:
            if self.current is not None:
                self.current.activate()
        else:
            return EVENT_UNHANDLED
        return EVENT_HANDLED

    ## Content shape
    ################

    @cached
    def content_shape(self):
        """The shape of the content in the format (x, y, w, h).

        """
        if self.direction == "vertical":
            return self.compute_shape_vertical()
        elif self.direction == "horizontal":
            return self.compute_shape_horizontal()

    def compute_shape_vertical(self):
        """Compute the content shape for vertical positioning.

        """
        # Compute the absolute measurements.
        sx, sy = self.scaling_factors
        xpos, ypos = self.xpos * sx, self.ypos * sy
        width, height = self.width * sx, self.height * sy
        margin, padding = self.margin * sy, self.padding * sy
        option_margin = padding + margin
        spacing = self.spacing * sy

        # Default values.
        options_x, options_y = 0.0, 0.0
        options_w, options_h = 0.0, 0.0

        # Compute the width and height of the content box.
        for option in self.options:
            opt_w, opt_h = option.size
            options_h += opt_h + spacing
            options_w = max(options_w, opt_w)
        if self.options:
            options_h -= spacing

        # Determine the top of the first option.
        if self.valign == "bottom":
            opt_y = ypos + options_h + option_margin
        elif self.valign == "center":
            opt_y = ypos + (height + options_h) / 2
        elif self.valign == "top":
            opt_y = ypos + height - option_margin

        # Determine the left of each option and position it.
        opt_xs, opt_ys = [], []
        for option in self.options:
            opt_w, opt_h = option.size
            if self.halign == "left":
                opt_x = xpos + option_margin
            elif self.halign == "center":
                opt_x = xpos + (width - opt_w) / 2
            elif self.halign == "right":
                opt_x = xpos + (width - option_margin - opt_w)
            opt_y -= opt_h
            opt_xs.append(opt_x)
            opt_ys.append(opt_y)
            option.position(opt_x, opt_y)
            opt_y -= spacing

        # Compute the bottom left corner of the content box.
        if self.options:
            options_x = min(opt_xs)
            options_y = min(opt_ys)

        return options_x, options_y, options_w, options_h

    def content_shape_horizontal(self):
        """Compute the content shape for horizontal positioning.

        """
        # Compute the absolute measurements.
        sx, sy = self.scaling_factors
        xpos, ypos = self.xpos * sx, self.ypos * sy
        width, height = self.width * sx, self.height * sy
        margin, padding = self.margin * sy, self.padding * sy
        option_margin = padding + margin
        spacing = self.spacing * sy

        # Default values.
        options_x, options_y = 0.0, 0.0
        options_w, options_h = 0.0, 0.0

        # Compute the width and height of the content box.
        for option in self.options:
            opt_w, opt_h = option.size
            options_w += opt_w + spacing
            options_h = max(options_h, opt_h)
        if self.options:
            options_w -= spacing

        # Determine the left of the first option.
        if self.halign == "left":
            opt_x = xpos + option_margin
        elif self.halign == "center":
            opt_x = xpos + (width - options_w) / 2
        elif self.halign == "right":
            opt_x = xpos + width - option_margin - options_w

        # Determine the bottom of each option and position it.
        opt_xs, opt_ys = [], []
        for option in self.options:
            opt_w, opt_h = option.size
            if self.valign == "bottom":
                opt_y = ypos + option_margin
            elif self.valign == "center":
                opt_y = ypos + (height - opt_h) / 1
            elif self.valign == "top":
                opt_y = ypos + height - option_margin - opt_h
            opt_xs.append(opt_x)
            opt_ys.append(opt_y)
            option.position(opt_x, opt_y)
            opt_x += opt_w
            opt_x += spacing

        # Compute the bottom left corner of the content box.
        if self.options:
            options_x = min(opt_xs)
            options_y = min(opt_ys)

        return options_x, options_y, options_w, options_h

    ## Drawing
    ##########

    def draw_content(self):
        """Draw the content.

        """
        for option in self.options:
            option.draw()




## Text menu
############

class TextMenuOption(MenuOption):
    """Text based menu option.

    """

    def __init__(self, menu, activate, label):
        super(TextMenuOption, self).__init__(menu, activate)
        self.label = label
        self.deselect()

    @cached
    def shape(self):
        bx = self.label.x
        by = self.label.y
        bw = self.label.content_width
        bh = self.label.content_height
        return bx, by, bw, bh

    def position(self, x, y):
        self.label.x = x
        self.label.y = y
        del self.shape

    def select(self):
        if self.selectable: color = self.menu.selected_color
        else: color = self.menu.text_color
        self.label.color = tuple(map(lambda x: int(255 * x), color))

    def deselect(self):
        if self.selectable: color = self.menu.unselected_color
        else: color = self.menu.text_color
        self.label.color = tuple(map(lambda x: int(255 * x), color))

    def draw(self):
        self.label.draw()


class TextMenu(Menu):
    """Text based menu.

    """

    keyword_names = frozenset([
        "font_name", "font_size", "text_color", "unselected_color",
        "selected_color",
    ])

    dependent_names = frozenset([
        "font_name", "font_size",
    ])

    font_name = None
    font_size = 0.0

    text_color       = (1.0, 1.0, 1.0, 1.0)
    unselected_color = (0.5, 0.5, 0.0, 1.0)
    selected_color   = (1.0, 1.0, 0.0, 1.0)

    def __init__(self, **kwds):
        """Create a TextMenu object.

        Additional arguments are handled by `Menu`.

        :Parameters:
            `font_name` : str
                The name of the font family to use.
            `font_size` : float
                The size at which to draw the font.

        """
        super(TextMenu, self).__init__(**kwds)
        self.labels = []

    def clear_options(self):
        """Clear all options from the menu.

        """
        for option in self.options:
            self.labels.append(option.label)
        super(TextMenu, self).clear_options()

    @cached
    def content_shape(self):
        """The shape of the content in the format (x, y, w, h).

        """
        # Compute the absolute measurements.
        sx, sy = self.scaling_factors
        xpos, ypos = self.xpos * sx, self.ypos * sy
        width, height = self.width * sx, self.height * sy
        margin, padding = self.margin * sy, self.padding * sy
        label_margin = padding + margin

        # Configure the labels.
        for option in self.options:
            option.label.font_name = self.font_name
            option.label.font_size = self.font_size * sy
            option.label.anchor_x = "left"
            option.label.anchor_y = "bottom"
            option.label.multiline = True
            option.label.set_style("align", self.halign)

        # Compute the shape.
        if self.direction == "vertical":
            return self.compute_shape_vertical()
        elif self.direction == "horizontal":
            return self.compute_shape_horizontal()

    def add_options(self, *option_specs):
        """Add a number of options to the menu.

        :Parameters:
            `option_specs` : str or tuple
                Either plain strings, which becoming non selectable options or
                tuples of a string and a function or curried function. See
                `MenuOption` for details.

        """
        def get_label(string):
            if self.labels:
                label = self.labels.pop()
                label.text = string
                return label
            return text.Label(string)

        for spec in option_specs:
            if isinstance(spec, basestring):
                label = get_label(spec)
                option = TextMenuOption(self, None, label)
            else:
                string, activate = spec
                label = get_label(string)
                option = TextMenuOption(self, activate, label)
            self.options.append(option)

        self.clear_cache()




## Image box
############

class ImageBox(InterfaceComponent):
    """Box containing a scaled image.

    """

    keyword_names = frozenset([
        "graphic", "scale_w", "scale_h",
    ])

    dependent_names = frozenset([
        "graphic", "scale_w", "scale_h",
    ])

    graphic = None
    scale_w = None
    scale_h = None

    def __init__(self, **kwds):
        """Create an ImageBox object.

        Additional arguments are handled by `InterfaceComponent`.

        :Parameters:
            `graphic` : pyglet.image.AbstractImage
            `scale_w` : float
            `scale_h` : float

        """
        super(ImageBox, self).__init__(**kwds)

    @cached
    def content_shape(self):
        """The shape of the content in the format (x, y, w, h).

        """
        # Compute the absolute measurements.
        sx, sy = self.scaling_factors
        xpos, ypos = self.xpos * sx, self.ypos * sy
        width, height = self.width * sx, self.height * sy
        content_margin = (self.margin + self.padding) * sy

        # Determine how to scale the image.
        if self.graphic is not None:
            graphic_w = self.graphic.width
            graphic_h = self.graphic.height
            aspect = graphic_w / graphic_h
            if self.scale_w is not None:
                scale_w = self.scale_w * sx
                scale_h = scale_w / aspect
                if self.scale_h is not None:
                    scale_h = self.scale_h * sy
            elif self.scale_h is not None:
                scale_h = self.scale_h * sy
                scale_w = scale_h * aspect
            else:
                scale_w = width - 2 * content_margin
                scale_h = height - 2 * content_margin
                scale_f = min(scale_w / graphic_w, scale_h / graphic_h)
                scale_w = graphic_w * scale_f
                scale_h = graphic_h * scale_f
        else:
            scale_w = scale_h = 0.0

        # Compute the horizontal dimensions.
        content_w = scale_w
        if self.halign == "left":
            content_x = xpos + content_margin
        elif self.halign == "center":
            content_x = xpos + (width - content_w) / 2
        elif self.halign == "right":
            content_x = xpos + width - content_w - content_margin

        # Compute the vertical dimensions.
        content_h = scale_h
        if self.valign == "bottom":
            content_y = ypos + content_margin
        elif self.valign == "center":
            content_y = ypos + (height - content_h) / 2
        elif self.valign == "top":
            content_y = ypos + height - content_h - content_margin

        return (content_x, content_y, content_w, content_h)

    def draw_content(self):
        """Draw the content.

        """
        if self.graphic is not None:
            cx, cy, cw, ch = self.content_shape
            gw = self.graphic.width
            gh = self.graphic.height
            ax = self.graphic.anchor_x
            ay = self.graphic.anchor_y
            glPushMatrix()
            glTranslatef(cx, cy, 0.0)
            glScalef(cw / gw, ch / gh, 1.0)
            glTranslatef(ax, ay, 0.0)
            glColor3f(1.0, 1.0, 1.0)
            self.graphic.blit(0.0, 0.0)
            glPopMatrix()




## Image button
###############

class ImageButton(ImageBox):
    """ImageBox with a callback when it is clicked.

    """

    keyword_names = frozenset([
        "callback",
    ])

    callback = None

    def __contains__(self, pos):
        """Check if the specified coordinates are inside the button.

        :Parameters:
            `pos` : tuple
                The x and y coordinates to test.

        """
        x, y = pos
        bx, by, bw, bh = self.box_shape
        in_x = bx <= x <= bx + bw
        in_y = by <= y <= by + bh
        return in_x and in_y

    def activate(self):
        """Call the (possibly curried) function the button is bound to.

        """
        if isinstance(self.callback, tuple):
            func = self.callback[0]
            args = self.callback[1:]
            func(*args)
        else:
            self.callback()

    def on_mouse_press(self, x, y, btn, mods):
        """Hide clicks within the box from lower layers.

        """
        self.set_mouse(x, y)
        if self.proxy_coordinates(x, y) in self:
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_mouse_release(self, x, y, btn, mods):
        """Activate the button if under the cursor.

        """
        if btn != mouse.LEFT:
            return EVENT_UNHANDLED
        elif self.proxy_coordinates(x, y) in self:
            self.activate()
            return EVENT_HANDLED
        return EVENT_UNHANDLED




## Icon grid
############

class IconGrid(InterfaceComponent):
    """Grid of icons with callbacks for hover and selection.

    """

    keyword_names = frozenset([
        "dimensions", "spacing", "activate", "select", "deselect", "font_name",
        "font_size", "color", "popup",
    ])

    dependent_names = frozenset([
        "dimensions", "spacing", "font_name", "font_size", "color",
    ])

    cache_names = frozenset([
        "icon_size", "icon_stride", "icon_shapes",
    ])

    dimensions = (7, 6)
    spacing = 0.0
    activate = None
    select = None
    deselect = None
    font_size = 0.0
    font_name = None
    color = (1.0, 1.0, 1.0, 1.0)
    popup = 1.5
    row_factor = 1.0

    def __init__(self, **kwds):
        """Create an IconGrid object.

        Additional arguments are handled by `InterfaceComponent`.

        """
        super(IconGrid, self).__init__(**kwds)
        self.clear_images()
        self.current_click = None
        self.current_hover = None

    def do_callback(self, callback, *args):
        if callback is not None:
            if isinstance(callback, tuple):
                func = callback[0]
                args += callback[1:]
                func(*args)
            else:
                callback(*args)

    ## Options
    ##########

    def set_current(self, idx):
        """Set the currently selected image to the given index.

        :Parameters:
            `idx` : int
                The index of the option to select.

        """
        if self.current is not None:
            self.do_callback(self.deselect, self.current)
        self.current = None
        if idx is not None:
            self.do_callback(self.select, idx)
            self.current = idx

    def change_current_direction(self, dx, dy):
        """Change the current option spatially.

        :Parameters:
            `dx` : int
                The change in x coordinate.
            `dy` : int
                The change in y coordinate.

        """
        if self.current is None:
            new_idx = 0
        else:
            y, x = divmod(self.current, self.dimensions[0])
            x = max(0, min(self.dimensions[0] - 1, x + dx))
            y = max(0, min(self.dimensions[1] - 1, y + dy))
            new_idx = x + y * self.dimensions[0]
            new_idx = max(0, min(len(self.images) - 1, new_idx))
        self.set_current(new_idx)
        self.scroll_option(new_idx)

    def add_images(self, *images):
        """Load and add the images.

        """
        for image_name in images:
            if isinstance(image_name, str):
                img = data.load_image(image_name, centered=True)
                self.images.append(img)
            elif isinstance(image_name, unicode):
                lbl = text.Label(x=0, y=0, text=image_name, anchor_x="center",
                        anchor_y="center")
                self.images.append(lbl)
            else:
                self.images.append(image_name)

    def clear_images(self):
        """Clear the image cache.

        """
        self.current = None
        self.images = []
        self.clear_cache()

    ## Scrolling
    ############

    def scroll_option(self, idx):
        """Scroll the view to contain the given option.

        :Parameters:
            `idx` : idx
                The index of the option to which to scroll.

        """
        cx, cy, cw, ch = self.content_shape
        ox, oy, ow, oh = self.icon_shapes[idx]
        if self.direction == "vertical":
            min_offset = max(0.0, ch - (oy - cy) - self.scroll_length)
            max_offset = min(self.scroll_max, ch - (oy - cy) - oh)
        elif self.direction == "horizontal":
            min_offset = max(0.0, (ox - cx) + ow - self.scroll_length)
            max_offset = min(self.scroll_max, (ox - cx))
        self.scroll = max(min_offset, min(max_offset, self.scroll))

    ## Event handlers
    #################

    def set_mouse(self, x, y):
        """Process the position of the mouse.

        """
        x, y = self.proxy_coordinates(x, y)
        if (x, y) not in self:
            self.set_current(None)
            return
        if self.scrolling:
            dx, dy = self.scroll_vector
            x, y = x - dx, y - dy
        for idx, img in enumerate(self.images):
            ix, iy, iw, ih = self.icon_shapes[idx]
            icy = iy + ih / 2
            vh = self.content_size[1] - self.scroll_max
            vy = self.content_pos[1] + self.scroll_max - self.scroll
            if ix < x <= ix + iw and iy < y <= iy + ih:
                if vy <= icy <= vy + vh:
                    self.set_current(idx)
                break
        else:
            self.set_current(None)

    def on_mouse_scroll(self, x, y, sx, sy):
        r = super(IconGrid, self).on_mouse_scroll(x, y, sx, sy)
        self.set_mouse(x, y)
        return r

    def on_mouse_press(self, x, y, btn, mods):
        """Hide clicks within the box from lower layers.

        """
        self.set_mouse(x, y)
        if self.proxy_coordinates(x, y) in self:
            return EVENT_HANDLED
        return EVENT_UNHANDLED


    def on_mouse_release(self, x, y, btn, mods):
        """Activate icons on mouse release.

        """
        self.set_mouse(x, y)
        if btn != mouse.LEFT:
            return EVENT_UNHANDLED
        if self.current is not None:
            self.do_callback(self.activate, self.current)
            return EVENT_HANDLED
        if self.proxy_coordinates(x, y) in self:
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_key_press(self, sym, mods):
        """Process directional keys and enter.

        """
        if sym == key.UP:
            self.change_current_direction(0, -1)
        elif sym == key.DOWN:
            self.change_current_direction(0, 1)
        elif sym == key.LEFT:
            self.change_current_direction(-1, 0)
        elif sym == key.RIGHT:
            self.change_current_direction(1, 0)
        elif sym == key.ENTER:
            if self.current is not None:
                self.do_callback(self.activate, self.current)
        else:
            return EVENT_UNHANDLED
        return EVENT_HANDLED

    ## Icon cache data
    ##################

    @cached
    def icon_size(self):
        """The width and height of the individual icons.

        """
        sx, sy = self.scaling_factors
        cx, cy, cw, ch = self.content_shape
        dim_x, dim_y = self.dimensions
        return (cw - self.spacing * sy * (dim_x - 1)) / dim_x

    @cached
    def icon_stride(self):
        """The distance between corners of adjacent icons.

        """
        sx, sy = self.scaling_factors
        return self.icon_size + self.spacing * sy

    @cached
    def icon_shapes(self):
        """The shapes of the icons in the format (x, y, w, h).

        """
        shapes = []
        cx, cy, cw, ch = self.content_shape
        dim_x, dim_y = self.dimensions
        size = self.icon_size
        spacing = self.spacing * self.scaling_factors[1]
        for idx in range(dim_x * dim_y):
            y, x = divmod(idx, dim_x)
            ry = dim_y - (y + 1)
            px = cx + x * (size + spacing)
            py = cy + ry * (size + spacing * self.row_factor)
            shapes.append((px, py, size, size))
        return shapes

    ## Content shape
    ################

    @cached
    def content_shape(self):
        """The shape of the content in the format (x, y, w, h).

        """
        # Compute the absolute measurements.
        sx, sy = self.scaling_factors
        xpos, ypos = self.xpos * sx, self.ypos * sy
        width, height = self.width * sx, self.height * sy
        margin, padding = self.margin * sy, self.padding * sy
        spacing = self.spacing * sy
        content_margin = padding + margin

        for img in self.images:
            if isinstance(img, text.Label):
                img.font_size = self.font_size * sy
                img.font_name = self.font_name
                img.color = tuple(map(lambda x: int(255 * x), self.color))

        # Compute the horizontal dimensions.
        content_w = width - 2 * content_margin
        if self.halign == "left":
            content_x = xpos + content_margin
        elif self.halign == "center":
            content_x = xpos + (width - content_w) / 2
        elif self.halign == "right":
            content_x = xpos + width - content_w - content_margin

        # Compute the icon size.
        dim_x, dim_y = self.dimensions
        self.icon_size = (content_w - spacing * (dim_x - 1)) / dim_x
        self.icon_stride = self.icon_size + spacing

        # Compute the vertical dimensions.
        content_h = (self.icon_size + spacing * self.row_factor) * dim_y - spacing * self.row_factor
        if self.valign == "bottom":
            content_y = ypos + content_margin
        elif self.valign == "center":
            content_y = ypos + (height - content_h) / 2
        elif self.valign == "top":
            content_y = ypos + height - content_h - content_margin

        return (content_x, content_y, content_w, content_h)

    ## Drawing
    ##########

    def draw_icon(self, idx):
        """Draw an individual icon.

        :Parameters:
            `idx` : int
                The index of the icon to draw.

        """
        glColor3f(1.0, 1.0, 1.0)
        image = self.images[idx]
        image.blit(0.0, 0.0)

    def draw_label(self, idx):
        label = self.images[idx]
        label.draw()

    def draw_content(self):
        """Draw the component.

        """
        cx, cy, cw, ch = self.content_shape
        dim_x, dim_y = self.dimensions
        size = self.icon_size
        stride = self.icon_stride
        def draw(idx):
            img = self.images[idx]
            ix, iy, iw, ih = self.icon_shapes[idx]
            gw, gh = iw, ih
            if isinstance(img, image.AbstractImage):
                gw, gh = img.width, img.height
            glPushMatrix()
            glTranslatef(ix, iy, 0.0)
            if idx == self.current:
                glTranslatef(size / 2, size / 2, 0.0)
                glScalef(self.popup, self.popup, 1.0)
                glTranslatef(-size / 2, -size / 2, 0.0)
                glPushAttrib(GL_SCISSOR_BIT)
                glDisable(GL_SCISSOR_TEST)
            scale = min(iw / gw, ih / gh)
            glTranslatef(size / 2, size / 2, 0.0)
            glScalef(scale, scale, 1.0)
            if isinstance(img, image.AbstractImage):
                self.draw_icon(idx)
            elif isinstance(img, text.Label):
                self.draw_label(idx)
            if idx == self.current:
                glPopAttrib()
            glPopMatrix()
        idxs = range(len(self.images))
        if self.current is not None:
            idxs.remove(self.current)
            idxs.append(self.current)
        map(draw, idxs)

    def draw_box(self):
        super(IconGrid, self).draw_box()
        if hasattr(self, "draw_frame"):
            self.draw_frame()


def make_frame(obj, frame=data.load_image("woodframe.png")):

    def square(x, y, ox, oy):
        return (x, y, x, oy, ox, oy, ox, y)

    bx, by, bw, bh = obj.box_shape
    obx, oby = bx + bw, by + bh
    ww, wh = obj.scaling_factors
    t = wh * 0.02 / 2

    vdata = (
        square(bx-t, by-t, bx+t, by+t) +
        square(bx-t, by+t, bx+t, oby-t) +
        square(bx-t, oby-t, bx+t, oby+t) +
        square(bx+t, oby-t, obx-t, oby+t) +
        square(obx-t, oby-t, obx+t, oby+t) +
        square(obx-t, by+t, obx+t, oby-t) +
        square(obx-t, by-t, obx+t, by+t) +
        square(bx+t, by-t, obx-t, by+t)
    )

    tdata = (
        0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0,
        0.0, 0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5,
        0.0, 0.5, 0.0, 1.0, 0.5, 1.0, 0.5, 0.5,
        0.5, 0.5, 0.5, 1.0, 0.5, 1.0, 0.5, 0.5,
        0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5,
        0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 1.0, 0.5,
        0.5, 0.0, 0.5, 0.5, 1.0, 0.5, 1.0, 0.0,
        0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0,
    )

    b = graphics.Batch()
    b.add(32, GL_QUADS, None, ('v2f', vdata), ('t2f', tdata))

    def draw():
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, frame.id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glColor4f(1, 1, 1, 1)
        b.draw()
        glDisable(GL_TEXTURE_2D)

    return draw
