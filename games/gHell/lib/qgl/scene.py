#Copyright (c) 2006 Simon Wittber
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation files
#(the "Software"), to deal in the Software without restriction,
#including without limitation the rights to use, copy, modify, merge,
#publish, distribute, sublicense, and/or sell copies of the Software,
#and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""

This module contains all possible scene nodes and leaves.

"""

import weakref

#import Numeric
from qgl import texture
import qgl
from copy import copy


class Node(object): 
    def __init__(self, *args):
        self.branches = []
        self.selectable = False
        self._accept = self.accept
        self.node_type = self.__class__.__name__
        self.parent = None
        self.add(*args)
    
    def clone(self):
        return copy(self)
    
    def __getitem__(self, i):
        return self.branches[i]
    
    def disable(self):
        if self.accept != self.disabled_accept:
            self._accept = self.accept
            self.accept = self.disabled_accept
    
    def enable(self):
        if self.accept != self._accept:
            self.accept = self._accept
    
    def disabled_accept(self, visitor):
        pass
        
    def accept(self, visitor):
        visitor.push_state(self)
        getattr(visitor, 'visit_' + self.node_type)(self)
        for node in self.branches:
            node.accept(visitor)
        visitor.pop_state(self)
        
    def add(self, *args):
        for arg in args:
            arg.parent = weakref.proxy(self)
            self.branches.append(arg)
        
    def remove(self, *args):
        for arg in args:
            self.branches.remove(arg)
    
    def update(self, **kw):
        self.__dict__.update(kw)
        return self

class Leaf(object):
    pass

class Root(Node):
    """
    The root node. There must only be one.
    """
    def __init__(self, *args):
        Node.__init__(self, *args)
        self.background_color = (0.0,0.0,0.0,1.0)
    

class PerspectiveViewport(Node):
    """
    The Viewport specifies an area of the screen which all children are 
    rendered to.
    
    .screen_dimensions are the physical screen coordinates which the viewport
    will render to.
    
    .aspect is the aspect ratio of the screen. 
    """
    def __init__(self, *args):
        Node.__init__(self, *args)
        self.screen_dimensions = (0, 0, 800, 600)
        self.aspect = 800.0 / 600.0
        

class OrthoViewport(Node):
    """
    The Viewport specifies an area of the screen which all children are 
    rendered to in an Orthographic projection.
    
    .screen_dimensions are the physical screen coordinates which the viewport
    will render to.
    
    .size is the width and height of the screen coordinate system. This is 
    usually the same as the screen resolution, but does not need to be.
    """
    def __init__(self, *args):
        Node.__init__(self, *args)
        self.screen_dimensions = (0, 0, 800, 600)
        self.size = (800,600)
        

class Transform(Node):
    """
    A Transform node is used to scale, move and rotate its child nodes.
    
    .scale is the x,y,z scaling factor.
    
    .axis is axis which the Node will rotate around
    
    .angle is the rotation around the axis, specified in degrees
    
    .translate is the x,y,z translation (movement or position) of the Node.
    """
    def __init__(self, *args):
        Node.__init__(self, *args)
        self.scale = (1.0,1.0,1.0)
        self.angle = 0.0
        self.axis = (0.0,0.0,1.0)
        self.translate = (0.0,0.0,0.0)

    
class Group(Transform):
    """
    A Group node is the node which contains renderable items.
    It is a subclass of Tranform, and can therefore be moved and scaled in 
    the same way as a Transform Node. Additionally, Leaf nodes can be added
    to a Group, which will allow the leaves to be rendered. Only Group Nodes 
    can contain Leaf Nodes.
    """
    def __init__(self, *args):
        self.leaves = []
        Transform.__init__(self, *args)
        
    def add(self, *args):
        """
        Add a Leaf or Branch to the Node.
        """
        for leaf in args:
            if isinstance(leaf, Node):
                Node.add(self, leaf)
            else:
                leaf.parent = weakref.proxy(self)
                self.leaves.append(leaf)
                
        
    def remove(self, *args):
        """
        Remove a Leaf or Branch from the Node.
        """
        for leaf in args:
            if isinstance(leaf, Leaf):
                self.leaves.remove(leaf)
            else:
                Node.remove(self, leaf)


class Static(Group):
    """
    A Static node is a group which cannot be changed after it has been 
    compiled. Any changes to leaf nodes or children won't work until the node 
    is recompiled. The node however, can still be translated, rotates and 
    scaled (relative to it's orginal values).
    """
    def __init__(self, *args):
        Group.__init__(self, *args)
        self.list = None
    
    
class Switch(Node):
    """
    A Switch node has named groups of children and can change the traversal 
    path depending on the active name. The initial name is 'default'.
    To add children to a node, switch to the name, then add children as 
    normal.
    """
    def __init__(self, *args):
        Node.__init__(self, *args)
        self.choices = dict(default=list(args))
        self.branches = self.choices['default']
    
    def switch(self, name):
        self.branches = self.choices.setdefault(name, [])
        

class World(Node):
    """
    The World node is a helper node which contains pre configured planes for
    sky, ground, background and foreground.
    """
    def __init__(self):
        Node.__init__(self)
        self.node_type = 'Node'
        self.sky = sky = Group()
        sky.update(angle=90.0, axis=(1,0,0), translate=(0.0,2.0,0.0))
        self.ground = ground = Group()
        ground.update(angle=-90.0, axis=(1,0,0), translate=(0.0,-2.0,0.0))
        self.background = background = Group()
        background.update(translate=(0.0,0.0,-40.0))
        self.foreground = foreground = Group()
        foreground.update(translate=(0.0,0.0,-10.0))
        self.camera = Transform(sky, ground, background, foreground)
        self.add(self.camera)

class state:
    
    
    class Texture(Leaf):
        """
        A Texture leaf is added to a group node to change the texture which is 
        used to render subsequent quads.
        
        .filename is the filename to load the texture from
        
        .filter is a bool which controls filtering
        
        .mipmap is a bool which controls mipmapping
        """
        def __init__(self, filename, filter=True, mipmap=True):
            self.filename = filename
            self.filter = filter
            self.mipmap = mipmap


    class Color(Leaf):
        """
        The Color leaf sets the color (including alpha value) for a nodes 
        children and leaves.
        
        .rgba is a 4 tuple sepcifying red, green, blue and alpha values.
        """
        def __init__(self, rgba=(1.0,1.0,1.0,1.0)):
            self.rgba = rgba
            

    class Material(Leaf):
        """
        The Material leaf sets the Material value for a node's children and leaves.
        Materials are important if you are using lights.
        
        Diffuse reflectance plays the most important part in determining what colour
        you perceive the object as and does not vary according to the position of 
        the camera.
        
        Ambient reflection affects the overall colour of the object and is most 
        obvious when it receives no direct illumination.  For real world objects, 
        diffuse and ambient are usually the same.
        
        Specular reflection is the colour produced in hilights, and depends on the
        location of the viewpoint.
        
        Emissive colour implies that the material is a light source, but does not 
        actually emit light on the scene.
        
        Please see Chapter 5 of the Red Book.
        """
        no_mat = (0.0, 0.0, 0.0, 1.0)
        mat_ambient = (0.7, 0.7, 0.7, 1.0)
        mat_diffuse = (0.3, 0.3, 0.3, 1.0)
        mat_specular = (1.0, 1.0, 1.0, 1.0)
        mat_emission = (0.3, 0.2, 0.2, 0.0)

        no_shine = (0.0,)
        low_shine = (5.0,)
        high_shine = (100.0,)

        def __init__(self, ambient=no_mat, diffuse=mat_diffuse, specular=mat_specular, shininess=low_shine, emissive=no_mat):
            self.ambient = ambient
            self.diffuse = diffuse
            self.specular = specular
            self.shininess = shininess
            self.emissive = emissive


    class Quad(Leaf):
        """
        The Quad leaf draws a rectangle using the current texture and color. It 
        is drawn from its centre point.
        
        .vertices are the vertices of the quad (automatically created from the 
        w,h args.
        
        .texture_coords is a 4 tuple of 2 tupels, which specifit the texture 
        coords of the Quad
        """
        def __init__(self, (w, h)):
            x,y = w*0.5,h*0.5
            self.vertices = (-x, -y, 0.0), (-x, y, 0.0), (x, y, 0.0), (x, -y, 0.0)
            self.texture_coords = ((0.0,0.0),(0.0,1.0),(1.0,1.0),(1.0,0.0))


    class Polyline(Leaf):
        """
        The Polyline leaf draws a series of connected lines.
        
        .vertices is a list of 3 tuples which are the points the line will be 
        drawn through.
        """
        def __init__(self, vertices, width=1.0):
            self.width = 1.0
            self.vertices = vertices 
            

    class Sequence(Leaf):
        """
        The sequence leaf draws an image sequence loaded from a file created
        using the make_animation tool.
        
        The (w,h) args specify the width and height of the animation. The 
        filename arg specifies the filename which the sequence is loaded from.
        To create create a sequence, see the qgl.tools module.
        
        .frame is an index into the sequence which controls the currently 
        displayed frame.
        """
        def __init__(self, (w,h), filename):
            x,y = w*0.5,h*0.5
            self.vertices = (-x, -y, 0.0), (-x, y, 0.0), (x, y, 0.0), (x, -y, 0.0)
            self.filename = filename
            self.frame = 0
            
        
    class Text(Leaf):
        """
        The Text leaf draws text using a specified font from the bottom left 
        corner.
        
        .text is the text string to be rendered
        
        .font is the font filename used to render the text
        
        .foreground and .background are rgba tuples which control rendering 
        colors. If background is None, the background is transparent.
        
        .size is the size of the text.
        """
        
        def __init__(self, text, font, foreground=(1,1,1), background=None, size=32):
            self._text = text
            self.foreground = foreground
            self.background = background
            self.size = size
            self.font = font
        
        def set_text(self, text):
            self._text = text
            self.parent.accept(self.parent.compiler)
        def get_text(self):
            return self._text
        text = property(fset=set_text, fget=get_text)
        

    class Mesh(Leaf):
        """
        The Mesh leaf loads 3D model files. Currently, only .obj files are 
        supported.
        
        .filename is the filename of the obj file to load.
        """
        def __init__(self, filename):
            self.filename = filename
            

    class Sphere(Leaf):
        """
        The Sphere leaf draws a texture mapped sphere.
        
        .radius is the radius of the sphere
        
        .x_segments and .y_segments control the number of facets used to
        approximate the sphere
        """
        def __init__(self, radius, x_segments=8, y_segments=8):
            self.radius = radius
            self.x_segments = x_segments
            self.y_segments = y_segments
            

    class Light(Leaf):
        """
        A light leaf will apply lighting parameters to all children rendered after it.
        
        .ambient an rgba tuple which specifies the ambient light color
        
        .diffuse an rgba tuple which specifies the diffuse light color
        
        .specular an rgba tuple which specifies the specular light color
        
        .position is an a x,y,z tuple which specifies the light position
        """
        def __init__(self, ambient=(0.2,0.2,0.2,1.0), diffuse=(1.0,1.0,1.0,1.0), specular=(1.0,1.0,1.0,1.0), position=(0.0,0.0,0.0)):
            self.ambient = ambient
            self.diffuse = diffuse
            self.specular = specular
            self.position = position


    class Fog(Leaf):
        """
        The Fog leaf applies a simple GL fogging effect.
        
        .start is z depth where fogging will start to be applied
        
        .end is the z depth where fogging will end. Everything after this depth 
        will be completely fogged out
        
        .density is the fog density
        
        .color is an rgba tuple which specified the fog color
        """
        def __init__(self, start=10, end=60, density=0.8, color=(0,0,0,1)):
            self.start = start
            self.end = end
            self.density = density
            self.color = color
            

    class DepthTest(Leaf):
        """
        This leaf can disable and enable depth testing.
        """
        def __init__(self, enabled):
            self.enabled = enabled
            

    class ParticleEmitter(Leaf):
        """
        A particle emitter shoots particles.
        """
        def __init__(self, count=100, start_angle=0, stop_angle=360, min_power=0.1, max_power=0.5, life_time=2.0):
            self.count = count
            self.start_angle = start_angle
            self.stop_angle = stop_angle
            self.min_power = min_power
            self.max_power = max_power
            self.life_time = float(life_time)
            self.life = float(life_time)
            
        def tick(self, T):
            self.positions += (self.velocities * T)
            self.life -= T
            alpha = self.life / self.life_time
            self.colors[:,3] = alpha


    class QuadList(Leaf):
        def __init__(self, vertices):
            self.vertices = vertices
            
            

        
        
