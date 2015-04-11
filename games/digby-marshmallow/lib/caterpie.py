"""Interface components based on Pyglet objects.

"""
from __future__ import division

from pyglet import text
from pyglet.window import key
from pyglet.window import mouse
from pyglet.event import EVENT_HANDLED
from pyglet.event import EVENT_UNHANDLED
from pyglet.gl import *

import data
from common import *

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


#############
## HELPERS ##
#############

def draw_rect(pos, size, outline, shade):
    """Draw a straightforward rectangle.

    :Parameters:
        `pos` : (float, float)
            The coordinates of the lower left corner.
        `size` : (float, float)
            The dimensions of the rectangle.
        `outline` : (float, float, float, [float])
            The GL color in which to draw the outline.
        `shade` : (float, float, float, [float])
            The GL color in whic to shade the interior.

    """
    x, y = pos
    w, h = size

    def set_color(color):
        if len(color) == 3:
            glColor3f(*color)
            return
        glColor4f(*color)

    if shade is not None:
        set_color(shade)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

    if outline is not None:
        set_color(outline)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()


###########
## STYLE ##
###########

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
    return default_style
def set_default_style(style):
    global default_style
    default_style = style




#########################
## INTERFACE COMPONENT ##
#########################

class InterfaceComponentMeta(type):
    """Metaclass for interface components.

    """

    def __init__(self, name, bases, dict):
        name_trees = ("keyword_names", "dependent_names", "cache_names")
        for name in name_trees:
            own = dict.get(name, frozenset())
            for b in bases:
                base = getattr(b, name, frozenset())
                own = base | own
            setattr(self, name, own)


class InterfaceComponent(object):
    """Baseclass for interface components.

    """

    __metaclass__ = InterfaceComponentMeta

    keyword_names = frozenset([
        "xpos", "ypos", "width", "height", "halign", "valign", "padding",
        "margin", "outline", "background", "expand", "square", "window",
    ])

    dependent_names = frozenset([
        "xpos", "ypos", "width", "height", "halign", "valign", "padding",
        "margin", "expand", "window",
    ])

    cache_names = frozenset([
        "scaling_factors", "box_shape", "content_shape",
    ])

    xpos = 0.0
    ypos = 0.0
    width = 0.0
    height = 0.0
    halign = "center"
    valign = "center"
    padding = 0.0
    margin = 0.0
    outline = (1.0,)*4
    background = (0.0,)*4
    expand = None
    square = None
    window = None

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
            `halign` : str
                The horizontal alignment of the content. Can be either "left",
                "center" or "right".
            `valign` : str
                The vertical alignment of the content. Can be either "bottom",
                "center" or "top".
            `padding` : float
                The distance between the content box and the content.
            `margin` : float
                The distance between the bounding box and the content box.
            `outline` : (float, float, float, [float])
                The GL color in which to outline the content box.
            `background` : (float, float, float, [float])
                The GL color in which to shade the content box.
            `expand` : str
                Whether to expand the content box to fill one or both dimensions
                of the bounding box. Can be either "horizontal", "vertical" or
                "both".
            `square` : str
                Whether to treat proportional measurements as relative to the
                appropriate dimension or always relative to a particular
                dimension.
            `window` : pyglet.window.Window or None
                The pyglet Window object on which we are drawing. If None, then
                we interpret the measurements as absolute rather than relative
                to window size.
            `style` : Style
                The style object from which to acquire default values. If None,
                then the default style is used.

        """
        style = kwds.pop("style", None) or default_style
        for name in self.keyword_names:
            value = getattr(self, name)
            setattr(self, name, value)
            try: setattr(self, name, getattr(style, name))
            except AttributeError: pass
        for name in kwds.keys():
            assert name in self.keyword_names, "invalid argument %r" % name
            setattr(self, name, kwds.pop(name))

    def __setattr__(self, name, value):
        """Clear cached attributes if a dependent attribute changes.

        """
        super(InterfaceComponent, self).__setattr__(name, value)
        if name in self.dependent_names:
            self.clear_cache()

    ## Utility
    ##########

    def clear_cache(self):
        """Clear cached attributes.

        """
        for name in self.cache_names:
            delattr(self, name)

    @cached
    def scaling_factors(self):
        sx, sy = 1.0, 1.0
        if self.window is not None:
            sx, sy = self.window.get_size()
        if self.square == "width":
            sy = sx
        elif self.square == "height":
            sx = sy
        return sx, sy


    ## Event Handlers
    #################

    def set_mouse(self, x, y):
        """Process the position of the mouse.

        """
        pass

    def on_mouse_press(self, x, y, btn, mods):
        """Process an 'on_mouse_press' event.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_release(self, x, y, btn, mods):
        """Process an 'on_mouse_release' event.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        """Process an 'on_mouse_motion' event.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_drag(self, x, y, dx, dy, btns, mods):
        """Process an 'on_mouse_drag' event.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_scroll(self, x, y, sx, sy):
        """Process an 'on_mouse_scroll' event.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_enter(self, x, y):
        """Process an 'on_mouse_enter' event.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_leave(self, x, y):
        """Process an 'on_mouse_leave' event.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    ## Content Shape
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

    ## Box Shape
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
        self.draw_box()
        glEnable(GL_SCISSOR_TEST)
        glScissor(*self.scissor_shape)
        self.draw_content()
        glDisable(GL_SCISSOR_TEST)


##############
## TEXT BOX ##
##############

class TextBox(InterfaceComponent):
    """Component that displays multiline text.

    """

    keyword_names = frozenset([
        "font_name", "font_size", "color",
    ])

    dependent_names = frozenset([
        "font_name", "font_size", "color"
    ])

    font_name = None
    font_size = 0.0
    color = (255,)*4

    def __init__(self, **kwds):
        """Create a TextBox object.

        Additional arguments are handled by `InterfaceComponent`.

        :Parameters:
            `font_name` : str
                The name of the font family to use.
            `font_size` : float
                The size at which to draw the font.
            `color` : (int, int, int, [int])
                The color in which to draw the text.
            `text` : unicode
                The text to display.

        """
        self._text = kwds.pop("text", u"")
        super(TextBox, self).__init__(**kwds)
        self.label = text.Label("")

    @property
    def text(self):
        return self._text
    
    @propset(text)
    def text(self, value):
        if value != self._text:
            self._text = value
            self.clear_cache()

    ## Content Shape
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
        self.label.text = self.text
        self.label.font_name = self.font_name
        self.label.font_size = self.font_size * sy
        self.label.width = width - 2 * label_margin
        self.label.anchor_x = "left"
        self.label.anchor_y = "bottom"
        self.label.color = self.color
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


################
## TEXT ENTRY ##
################

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
        """Construct a TextEntry object.

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
        self.window = window
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
        if sym == key.ENTER:
            self.hide()
            self.callback(self.text)
            return EVENT_HANDLED
        elif self.show_entry:
            return EVENT_HANDLED
        return EVENT_UNHANDLED
    
    def on_key_release(self, sym, mods):
        if self.show_entry:
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_text(self, text):
        if self.show_entry and text not in u"\r\n":
            old_text = "" if self.as_default else self.text
            new_text = old_text + text.replace("\r", "\n")
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


###################
## GENERIC MENUS ##
###################

class MenuOption(object):
    """Base menu option implementation.

    """

    def __init__(self, menu, activate):
        """Create an option.

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
        "spacing", "direction", "scrolling", "sensitivity",
    ])

    cache_names = frozenset([
        "scroll_max", "scroll_length", "scroll_offset",
    ])

    dependent_names = frozenset([
        "spacing", "direction",
    ])

    spacing = 0.0
    direction = "vertical"
    scrolling = False
    sensitivity = 0.1

    def __init__(self, **kwds):
        """Create a Menu object.

        Additional arguments are handled by `InterfaceComponent`.

        :Parameters:
            `spacing` : float
                The spacing between menu options.
            `direction` : str
                The direction in which the menu scans.
            `scrolling` : bool
                Whether or not to let me menu scroll.
            `sensitivity` : float
                The scroll sensitivity in proportion to length.

        """

        super(Menu, self).__init__(**kwds)
        self.scroll = 0.0
        self.current = None
        self.options = []
        self.clear_options()

    def __contains__(self, pos):
        """Check if the specified coordinates are inside the menu.

        :Parameters:
            `pos` : tuple
                The x and y coordinates to test.

        """
        x, y = pos
        bx, by, bw, bh = self.box_shape
        in_x = bx <= x < bx + bw
        in_y = by <= y < by + bh
        return in_x and in_y

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

    def scroll_relative(self, steps):
        """Scroll forwards a number of (possibly negative) relative steps.

        :Parameters:
            `steps` : int
                The number of steps (size relative to length) to scroll.

        """
        delta = steps * self.scroll_length * self.sensitivity
        self.scroll = max(0.0, min(self.scroll_max, self.scroll + delta))

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

    ## Event Handling
    #################

    def set_mouse(self, x, y):
        """Process the position of the mouse.

        """
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

    def on_mouse_press(self, x, y, btn, mods):
        """Activate option under cursor if any.

        """
        self.set_mouse(x, y)
        if btn != mouse.LEFT:
            return EVENT_UNHANDLED
        if self.current is not None:
            self.current.activate()
            self.set_mouse(x, y)
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_mouse_scroll(self, x, y, sx, sy):
        """Scroll the menu if we scroll.

        """
        self.set_mouse(x, y)
        if self.scrolling:
            self.scroll_relative(-sy)
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_mouse_drag(self, x, y, dx, dy, btns, mods):
        """Update the mouse position.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_enter(self, x, y):
        """Update the mouse position.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_leave(self, x, y):
        """Update the mouse position.

        """
        self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        """Update the mouse position.

        """
        if not (dx == dy == 0):
            self.set_mouse(x, y)
        return EVENT_UNHANDLED

    def on_mouse_release(self, x, y, btn, mods):
        """Update the mouse position.

        """
        self.set_mouse(x, y)
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

    ## Content Shape
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
                opt_y = ypos + (height - opt_h) / 2
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
        glPushMatrix()
        if self.scrolling:
            scroll = self.scroll + self.scroll_offset
            if self.direction == "vertical":
                glTranslatef(0.0, scroll, 0.0)
            elif self.direction == "horizontal":
                glTranslatef(-scroll, 0.0, 0.0)
        for option in self.options:
            option.draw()
        glPopMatrix()


###############
## TEXT MENU ##
###############

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
        if self.selectable:
            self.label.color = self.menu.selected_color
        else:
            self.label.color = self.menu.text_color

    def deselect(self):
        if self.selectable:
            self.label.color = self.menu.unselected_color
        else:
            self.label.color = self.menu.text_color

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

    text_color       = (255, 255, 255, 255)
    unselected_color = (127, 127,   0, 255)
    selected_color   = (255, 255,   0, 255)

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


###############
## IMAGE BOX ##
###############

class ImageBox(InterfaceComponent):
    """Box containing a scaled image.

    """

    keyword_names = frozenset([
        "graphic"
    ])

    graphic = None

    @cached
    def content_shape(self):
        """The shape of the content in the format (x, y, w, h).

        """
        sx, sy = self.scaling_factors
        xpos, ypos = self.xpos * sx, self.ypos * sy
        width, height = self.width * sx, self.height * sy
        content_margin = (self.margin + self.padding) * sy

        content_w = width - 2 * content_margin
        content_h = height - 2 * content_margin
        content_x = xpos + content_margin
        content_y = ypos + content_margin

        return content_x, content_y, content_w, content_h

    def draw_content(self):
        """Draw the content.

        """
        if self.graphic is not None:
            cx, cy, cw, ch = self.content_shape
            self.graphic.draw(cx, cy, width=cw, height=ch)


##################
## IMAGE BUTTON ##
##################

class ImageButton(ImageBox):
    """ImageBox with a callback when it is clicked.

    """
    
    keyword_names = frozenset([
        "callback"
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
        """Activate the button if under the cursor.

        """
        if btn == mouse.LEFT and (x, y) in self:
            self.activate()
            return EVENT_HANDLED
        return EVENT_UNHANDLED

class BitmapButton(ImageButton):
    def draw_content(self):
        if self.graphic is not None:
            cx, cy, cw, ch = self.content_shape
            glPushMatrix()
            glTranslatef(cx, cy, 0)
            glScalef(cw / self.graphic.width, ch / self.graphic.height, 1) 
            glColor3f(1,1,1)   
            self.graphic.blit(0,0)
            glPopMatrix()