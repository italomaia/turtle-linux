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

This module contains everything related to displaying a graph via OpenGL.
- Compiler visitor (changes nodes into OpenGL objects)
- Render visitor (draws stuff)
- Picker visitor (lets you know what was rendered at a certain location)

"""

from weakref import WeakValueDictionary
import zipfile
from StringIO import StringIO

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

try:
    import numpy
except:
    try:
        import Numeric as numpy
    except:
        print 'sin numpy'

from qgl.scene import state
import qgl.texture

import random

#cache for textures and fonts, so that they can be shared among nodes in the tree
qgl_cache = WeakValueDictionary()


class Visitor(object):
    def push_state(self, node): pass
    def pop_state(self, node): pass
    def visit_Node(self, node): pass
    def visit_Root(self, node): pass
    def visit_OrthoViewport(self, node): pass
    def visit_PerspectiveViewport(self, node): pass
    def visit_Transform(self, node): pass
    def visit_Group(self, node): pass
    def visit_Switch(self, node): pass
        
        
class GLTexture(object):
    """
    Takes a pygame surface and converts it into an RGBA OpenGL texture.
    GL Texture cleanup happens when the GLTexture instances is garbage 
    collected.
    """
    @classmethod
    def from_file(cls, filename, mipmap, filter):
        img = pygame.image.load(filename).convert(32, pygame.SRCALPHA)
        img = img.convert_alpha(img)
        return cls(img, mipmap, filter, flip=True)

    def __init__(self, img, mipmap, filter, flip=False):
        img = img.convert(32, pygame.SRCALPHA)
        img = img.convert_alpha(img)
        
        if not mipmap:
            assert img.get_size()[0] in [int(2**i) for i in xrange(100)], "width of image not a power of two."
            assert img.get_size()[1] in [int(2**i) for i in xrange(100)], "height of image not a power of two."

        ptype = GL_RGBA
        channels = 4
        string = pygame.image.tostring(img, 'RGBA', flip)
        size = img.get_size()
        filter_type = GL_NEAREST
        if filter: filter_type = GL_LINEAR
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter_type)
        if mipmap:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
            gluBuild2DMipmaps(GL_TEXTURE_2D, channels, size[0], size[1], ptype, GL_UNSIGNED_BYTE, string)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter_type)
            glTexImage2D(GL_TEXTURE_2D, 0, ptype, size[0], size[1], 0, ptype, GL_UNSIGNED_BYTE, string)
        
        #keep a ref to this, for cleaning up in the destructor.
        self.glDeleteTextures = glDeleteTextures
    
    def __del__(self):
        if hasattr(self, 'id'):
            self.glDeleteTextures(self.id)       


class FontTexture(object):            
    """
    Generates a texture which is used for drawing text using texture mapped 
    quads.
    """
    def __init__(self, font_filename, foreground=(1,1,1), background=None):
        foreground = tuple([int(i*255) for i in foreground])
        if background is not None:
            background = tuple([int(i*255) for i in background])
        
        font = pygame.font.Font(font_filename, 40)
        pack = qgl.texture.Pack(size=(1024,1024))
        
        alphabet = {}

        for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`1234567890-=+_)(*&^%$#@!~[]\\;\',./<>?:"{}| ':
            image = font.render(c, True, foreground).convert(32, pygame.SRCALPHA)
            pygame.draw.rect( image, (255.0,0.0,0.0,0.0), image.get_rect(), 1)
            image = pygame.transform.flip(image, False, True)
            alphabet[c] = pack.pack(image)
            
        self.alphabet = alphabet
        self.texture = GLTexture(pack.image, True,True)
        

class GLDisplayList(object):
    """
    Creates an OpenGL display list, which is referenced using the .id 
    attribute. List cleanup happens when the GLDisplayList instance is 
    garbage collected.
    """
    def __init__(self):
        self.id = glGenLists(1)
        if self.id == 0:
            raise RuntimeError("OpenGL will not allocate display list.")
        self.glDeleteLists = glDeleteLists
    
    def __del__(self):
        self.glDeleteLists(self.id, 1)
        

class GLLight(object):
    """
    Automatically allocates a GL_LIGHT constant. (.id)
    When the instance is garbage collected, the light constant is made 
    available for use again.
    """
    lights = [GL_LIGHT0,GL_LIGHT1,GL_LIGHT2,GL_LIGHT3,GL_LIGHT4,GL_LIGHT5,GL_LIGHT6,GL_LIGHT7]
    def __init__(self):
        try:
            self.id = self.lights.pop(-1)
        except IndexError:
            raise RuntimeError('Too many lights allocated.')
        
    def __del__(self):
        self.lights.append(self.id)
        
        
class GLQuadric(object):
    """
    Creates a GLU Quadric object, which is automatically destroyed when the
    instance is garbage collected.
    """
    def __init__(self):
        self.id = gluNewQuadric()
        if self.id == 0:
            raise RuntimeError("OpenGL will not allocate display quadric.")
        self.gluDeleteQuadric = gluDeleteQuadric
    
    def __del__(self):
        self.gluDeleteQuadric(self.id)
        
        
class Compiler(Visitor):
    """
    Traverse the graph, compiling and leaf nodes so they can be rendered by 
    OpenGL. Sets all nodes to enabled, and all switches to default.
    """
    def __init__(self):
        self.stack = []
        self.static_nodes = set()
        
    def push_state(self, node):
        for child in node.branches:
            child.enable()
        if isinstance(node, qgl.scene.Static):
            node.node_type = 'Group'
        
    def pop_state(self, node):
        if isinstance(node, qgl.scene.Switch):
            node.switch('default')
        elif isinstance(node, qgl.scene.Static):
            self.static_nodes.add(node)
            node.node_type = 'Static'
        elif isinstance(node, qgl.scene.Root):
            self.compile_static_nodes()
            
    def compile_static_nodes(self):
        render = Render()
        for node in self.static_nodes:
            node.node_type = 'Group'
            lst = GLDisplayList()
            glNewList(lst.id, GL_COMPILE)
            node.accept(render)
            glEndList()
            node.list = lst
            node.node_type = 'Static'
    
    def visit_OrthoViewport(self, node):
        node.window_size = pygame.display.get_surface().get_size()

    def visit_PerspectiveViewport(self, node):
        node.window_size = pygame.display.get_surface().get_size()
        
    def visit_Switch(self, node):
        branches = []
        for choice in node.choices.values():
            branches.extend(choice)
        node.branches = branches
    
    def visit_Group(self, node):
        node.compiler = self
        for leaf in node.leaves:
            if isinstance(leaf, state.Texture):
                self.build_texture(leaf)
            if isinstance(leaf, state.Sequence):
                self.build_sequence(leaf)
            elif isinstance(leaf, state.Text):
                self.build_text(leaf)
            elif isinstance(leaf, state.Mesh):
                self.build_mesh(leaf)
            elif isinstance(leaf, state.Sphere):
                self.build_sphere(leaf)
            elif isinstance(leaf, state.Light):
                self.build_light(leaf)
            elif isinstance(leaf, state.Polyline):
                self.build_polyline(leaf)
            elif isinstance(leaf, state.Quad):
                self.build_quad(leaf)
            elif isinstance(leaf, state.ParticleEmitter):
                self.build_particleemitter(leaf)
            elif isinstance(leaf, state.Color):
                pass
            elif isinstance(leaf, state.Material):
                pass
            elif isinstance(leaf, state.Fog):
                pass
            elif isinstance(leaf, state.Texture):
                pass
            elif isinstance(leaf, state.QuadList):
                pass
            elif isinstance(leaf, state.DepthTest):
                pass
            else:
                #default action is to call .compile method. This allows for basic custom leaves.
                #if leaf.key in qgl_cache:
                #    leaf.from_cache(qgl_cache[leaf.key])
                #else:
                stuff = leaf.compile()
                #    qgl_cache[leaf.key] = stuff
                
    
    def build_particleemitter(self, node):
        node.positions = numpy.zeros((node.count, 3), numpy.Float)
        node.velocities = numpy.ones((node.count, 3), numpy.Float)
        node.colors = numpy.ones((node.count, 4), numpy.Float)
        
        for i in xrange(len(node.velocities)):
            angle = random.uniform(node.start_angle, node.stop_angle)
            power = random.uniform(node.min_power, node.max_power)
            node.velocities[i][:] = qgl.qmath.polar_vector(angle, power)
        
            
    def build_quad(self, node):
        lst = GLDisplayList()
        glNewList(lst.id, GL_COMPILE)
        v = node.vertices
        t = node.texture_coords
        glBegin(GL_QUADS)
        glTexCoord2f(t[0][0],t[0][1])
        glVertex2f(v[0][0],v[0][1])
        glTexCoord2f(t[1][0],t[1][1])
        glVertex2f(v[1][0],v[1][1])
        glTexCoord2f(t[2][0],t[2][1])
        glVertex2f(v[2][0],v[2][1])
        glTexCoord2f(t[3][0],t[3][1])
        glVertex2f(v[3][0],v[3][1])
        glEnd()
        glEndList()
        node.list = lst

        
    def build_polyline(self, node):
        pass
        
    def build_light(self, node):
        node.light = GLLight()
    
    def build_texture(self, node):
        key = (node.filename, node.mipmap, node.filter)
        if key in qgl_cache:
            node.texture = qgl_cache[key]
        else:
            texture = GLTexture.from_file(*key)
            qgl_cache[key] = texture
            node.texture = texture
            
    def build_sequence(self, node):
        key = node.filename
        if key in qgl_cache:
            node.texture = qgl_cache[key]
        else:
            f = zipfile.ZipFile(node.filename,"r")
            fo = f.read("texture.rgba")
            size  = eval(f.read("size.repr"))
            image = pygame.image.fromstring(fo, size, "RGBA")
            texture = GLTexture(image, True, True)
            texture.coords = eval(f.read("coords.repr"))
            qgl_cache[key] = texture
            node.texture = texture
            
    def build_text(self, node):
        key = node.font, node.foreground, node.background
        if key in qgl_cache:
            node.font_object = qgl_cache[key]
        else:
            font = FontTexture(*key)
            qgl_cache[key] = font
            node.font_object = font
        
        lst = GLDisplayList()
        glNewList(lst.id, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, node.font_object.texture.id)
        glBegin(GL_QUADS)
        ox,oy = 0.0,0.0
        for c in node._text:
            tex = node.font_object.alphabet[c]
            h = tex[2][1] - tex[0][1]
            w = tex[2][0] - tex[0][0]
            h *= node.size
            w *= node.size
            glTexCoord2f(*tex[0])
            glVertex2f(ox+0, oy+0)
            glTexCoord2f(*tex[1])
            glVertex2f(ox+0, oy+h)
            glTexCoord2f(*tex[2])
            glVertex2f(ox+w, oy+h)
            glTexCoord2f(*tex[3])
            glVertex2f(ox+w, oy)
            ox += w
        glEnd()
        glEndList()
        node.list = lst
            
    def build_mesh(self, node):
        key = (node.filename)
        if key in qgl_cache:
            node.list = qgl_cache[key]
        else:
            mvertices, mtexcoords, mnormals, mfaces = qgl.loaders.load(node.filename)
            gl_list = qgl_cache[key] = GLDisplayList()
            glNewList(gl_list.id, GL_COMPILE)
            glFrontFace(GL_CCW)
            for face in mfaces:
                vertices,normals,texture_coords = face
                glBegin(GL_POLYGON)
                for i in range(0, len(vertices)):
                    if normals[i] > 0:
                        glNormal3fv(mnormals[normals[i] - 1])
                    if texture_coords[i] > 0:
                        glTexCoord2fv(mtexcoords[texture_coords[i] - 1])
                    glVertex3fv(mvertices[vertices[i] - 1])
                glEnd()
            glEndList()
            node.vertices = mvertices
            node.list = gl_list
    
    def build_sphere(self, node):
        key = ('sphere',node.radius,node.x_segments, node.y_segments)
        if key in qgl_cache:
            node.list = qgl_cache[key]
        else:
            gl_list = GLDisplayList()
            q = GLQuadric()
            glNewList(gl_list.id, GL_COMPILE)
            glFrontFace(GL_CCW)
            gluQuadricTexture(q.id, GL_TRUE)
            gluQuadricNormals(q.id, GLU_SMOOTH)
            gluQuadricOrientation(q.id, GLU_OUTSIDE)
            gluSphere(q.id, node.radius, node.x_segments, node.y_segments)
            glEndList()
            node.list = gl_list
            gl_list.quadric = q
            qgl_cache[key] = gl_list
            
        
class Render(Visitor):
    """
    Traverse the graph and render using OpenGL.
    """
    def push_state(self, node):
        glPushMatrix()
        glPushAttrib(GL_CURRENT_BIT|GL_TEXTURE_BIT|GL_ENABLE_BIT|GL_LIGHTING_BIT|GL_POLYGON_BIT)

    def pop_state(self, node):
        glPopAttrib()
        glPopMatrix()
    
    def visit_Root(self, node):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearDepth(1.0)
        glFrontFace(GL_CW)
        glShadeModel(GL_SMOOTH)
        glCullFace(GL_BACK)
        glEnable(GL_CULL_FACE)
        glClearColor(*node.background_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def visit_Transform(self, node):
        glTranslatef(*node.translate)
        glRotatef(node.angle, *node.axis)
        glScalef(*node.scale)
        
    def visit_Static(self, node):
        glTranslatef(*node.translate)
        glRotatef(node.angle, *node.axis)
        glScalef(*node.scale)
        glCallList(node.list.id)
        
    def visit_Group(self, node):
        glTranslatef(*node.translate)
        glRotatef(node.angle, *node.axis)
        glScalef(*node.scale)
        for leaf in node.leaves:
            if leaf.__class__ is state.Quad:
                glCallList(leaf.list.id)
            elif leaf.__class__ is state.Texture:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, leaf.texture.id)
            elif leaf.__class__ is state.Color:
                glColor4f(leaf.rgba[0], leaf.rgba[1], leaf.rgba[2], leaf.rgba[3])
            elif leaf.__class__ is state.Material:
                glMaterial(GL_FRONT, GL_AMBIENT, leaf.ambient)
                glMaterial(GL_FRONT, GL_DIFFUSE, leaf.diffuse)
                glMaterial(GL_FRONT, GL_SPECULAR, leaf.specular)
                glMaterial(GL_FRONT, GL_SHININESS, leaf.shininess)
                glMaterial(GL_FRONT, GL_EMISSION, leaf.emissive)
            elif leaf.__class__ is state.Polyline:
                glBegin(GL_LINE_STRIP)
                for v in leaf.vertices:
                    glVertex2f(v[0],v[1])
                glEnd()
            elif leaf.__class__ is state.Sequence:
                v = leaf.vertices
                t = leaf.texture.coords[leaf.frame]
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, leaf.texture.id)
                glBegin(GL_QUADS)
                glTexCoord2f(t[0][0], t[0][1])
                glVertex2f(v[0][0],v[0][1])
                glTexCoord2f(t[1][0],t[1][1])
                glVertex2f(v[1][0],v[1][1])
                glTexCoord2f(t[2][0],t[2][1])
                glVertex2f(v[2][0],v[2][1])
                glTexCoord2f(t[3][0],t[3][1])
                glVertex2f(v[3][0],v[3][1])
                glEnd()
            elif leaf.__class__ is state.Text:
                glCallList(leaf.list.id)
            elif leaf.__class__ is state.Mesh:
                glCallList(leaf.list.id)
            elif leaf.__class__ is state.Sphere:
                glCallList(leaf.list.id)
            elif leaf.__class__ is state.Light:
                glEnable(GL_LIGHTING)
                glEnable(leaf.light.id)
                glLightfv(leaf.light.id, GL_AMBIENT, leaf.ambient)
                glLightfv(leaf.light.id, GL_DIFFUSE, leaf.diffuse)
                glLightfv(leaf.light.id, GL_SPECULAR, leaf.specular)
                glLightfv(leaf.light.id, GL_POSITION, leaf.position)
            elif leaf.__class__ is state.Fog:
                glEnable(GL_FOG)
                glFogi(GL_FOG_MODE, GL_LINEAR)
                glHint(GL_FOG_HINT, GL_NICEST)
                glFogf(GL_FOG_START, leaf.start)
                glFogf(GL_FOG_END, leaf.end)
                glFogf(GL_FOG_DENSITY, leaf.density)
                glFogfv(GL_FOG_COLOR, leaf.color)
            elif leaf.__class__ is state.QuadList:
                glBegin(GL_QUADS)
                for v in leaf.vertices:
                    glVertex3v(v)   
                glEnd()
            elif leaf.__class__ is state.DepthTest:
                if leaf.enabled:
                    glEnable(GL_DEPTH_TEST)
                else:
                    glDisable(GL_DEPTH_TEST)
            elif leaf.__class__ is state.ParticleEmitter:
                glEnable(GL_VERTEX_ARRAY)
                glEnable(GL_COLOR_ARRAY)
                glVertexPointerf(leaf.positions)
                glColorPointerf(leaf.colors)
                glDrawArrays(GL_POINTS, 0, len(leaf.positions))
            else:
                #default behavior for custom leaves.
                leaf.execute()

    def visit_PerspectiveViewport(self, node):
        glViewport(*node.screen_dimensions)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, node.aspect, 0.1, 512)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def visit_OrthoViewport(self, node):
        glViewport(*node.screen_dimensions)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        w,h = node.size
        w *= 0.5
        h *= 0.5
        glOrtho(-w, w, -h, h, 0, 512)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        

class Picker(Render):
    """
    Traverse the graph and create a list (self.hits) of all items rendered at
    the area defined by self.position and self.area.
    """
    def __init__(self, *args, **kw):
        Render.__init__(self, *args, **kw)
        self.set_position((0,0), area=(1,1))
    
    def set_position(self, pos, area=(3,3)):
        self.position = pos
        self.area = area 
        self.guid = 0
        self.stack = []
        self.hits = []
        self.selectable_nodes = {}
        
    def push_state(self, node):
        self.guid += 1
        Render.push_state(self, node)
        self.stack.append(node)
        if isinstance(node, qgl.scene.Root):
            glInitNames()
            glSelectBuffer(256)
            glRenderMode(GL_SELECT)
        if node.selectable:
            node_id = self.guid
            self.selectable_nodes[node_id] = node
            glPushName(node_id)
        
    def pop_state(self, node):
        Render.pop_state(self, node)
        node = self.stack.pop(-1)
        if isinstance(node, qgl.scene.Root):
            glFlush()
            items = []
            hits = list(glRenderMode(GL_RENDER))
            hits.sort()
            for hit in hits:
                items.extend([self.selectable_nodes[i] for i in hit[2]])
            self.hits = items
        if node.selectable:
            glPopName()
            
    def visit_PerspectiveViewport(self, node):
        glViewport(*node.screen_dimensions)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        viewport = glGetIntegerv(GL_VIEWPORT)
        gluPickMatrix(self.position[0],node.window_size[1]-self.position[1],self.area[0],self.area[1],viewport)
        gluPerspective(45, node.aspect, 0.1, 100)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def visit_OrthoViewport(self, node):
        glViewport(*node.screen_dimensions)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        viewport = glGetIntegerv(GL_VIEWPORT)
        gluPickMatrix(self.position[0],node.window_size[1]-self.position[1],self.area[0],self.area[1],viewport)
        w,h = node.size
        w *= 0.5
        h *= 0.5
        glOrtho(-w, w, -h, h, 0, 512)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
            


    




























#psyco.full()
attributes = GL_CURRENT_BIT|GL_TEXTURE_BIT|GL_ENABLE_BIT|GL_LIGHTING_BIT|GL_POLYGON_BIT

def render(node):
    """
    Traverse the graph and render using OpenGL.
    """
    glPushMatrix()
    glPushAttrib(attributes)

    node__class__ = node.__class__
    if node__class__ is Group:
        glTranslatef(*node.translate)
        glRotatef(node.angle, *node.axis)
        glScalef(*node.scale)
        for leaf in node.leaves:
            leaf__class__ = leaf.__class__
            if leaf__class__ is state.Quad:
                v = leaf.vertices
                t = leaf.texture_coords
                glBegin(GL_QUADS)
                glTexCoord2f(t[0][0],t[0][1])
                glVertex2f(v[0][0],v[0][1])
                glTexCoord2f(t[1][0],t[1][1])
                glVertex2f(v[1][0],v[1][1])
                glTexCoord2f(t[2][0],t[2][1])
                glVertex2f(v[2][0],v[2][1])
                glTexCoord2f(t[3][0],t[3][1])
                glVertex2f(v[3][0],v[3][1])
                glEnd()
            elif leaf__class__ is state.Texture:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, leaf.texture.id)
            elif leaf__class__ is state.Color:
                glColor4f(leaf.rgba[0], leaf.rgba[1], leaf.rgba[2], leaf.rgba[3])
            elif leaf__class__ is state.Polyline:
                glBegin(GL_LINE_STRIP)
                for v in leaf.vertices:
                    glVertex2f(v[0],v[1])
                glEnd()
            elif leaf__class__ is state.Sequence:
                v = leaf.vertices
                t = leaf.texture.coords[leaf.frame]
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, leaf.texture.id)
                glBegin(GL_QUADS)
                glTexCoord2f(t[0][0], t[0][1])
                glVertex2f(v[0][0],v[0][1])
                glTexCoord2f(t[1][0],t[1][1])
                glVertex2f(v[1][0],v[1][1])
                glTexCoord2f(t[2][0],t[2][1])
                glVertex2f(v[2][0],v[2][1])
                glTexCoord2f(t[3][0],t[3][1])
                glVertex2f(v[3][0],v[3][1])
                glEnd()
            elif leaf__class__ is state.Text:
                glCallList(leaf.list.id)
            elif leaf__class__ is state.Mesh:
                glCallList(leaf.list.id)
            elif leaf__class__ is state.Sphere:
                glCallList(leaf.list.id)
            elif leaf__class__ is state.Light:
                glEnable(GL_LIGHTING)
                glEnable(leaf.light.id)
                glLightfv(leaf.light.id, GL_AMBIENT, leaf.ambient)
                glLightfv(leaf.light.id, GL_DIFFUSE, leaf.diffuse)
                glLightfv(leaf.light.id, GL_SPECULAR, leaf.specular)
                glLightfv(leaf.light.id, GL_POSITION, leaf.position)
            elif leaf__class__ is state.Fog:
                glEnable(GL_FOG)
                glFogi(GL_FOG_MODE, GL_LINEAR)
                glHint(GL_FOG_HINT, GL_NICEST)
                glFogf(GL_FOG_START, leaf.start)
                glFogf(GL_FOG_END, leaf.end)
                glFogf(GL_FOG_DENSITY, leaf.density)
                glFogfv(GL_FOG_COLOR, leaf.color)
            elif leaf__class__ is state.QuadList:
                glBegin(GL_QUADS)
                for v in leaf.vertices:
                    glVertex3v(v)   
                glEnd()
    elif node__class__ is Transform:
        glTranslatef(*node.translate)
        glRotatef(node.angle, *node.axis)
        glScalef(*node.scale)
    
    elif node__class__ is PerspectiveViewport:
        glViewport(*node.screen_dimensions)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, node.aspect, 0.1, 512)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    elif node__class__ is OrthoViewport:
        glViewport(*node.screen_dimensions)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, node.size[0], 0, node.size[1], 0.1, 512)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    elif node__class__ is Root:
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearDepth(1.0)
        glFrontFace(GL_CW)
        glShadeModel(GL_SMOOTH)
        glCullFace(GL_BACK)
        glClearColor(*node.background_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    

    for branch in node.branches:
        render(branch)
        
    glPopAttrib()
    glPopMatrix()

#render = rh_opz._make_constants(render, verbose=True)
        
        

    
