import qgl
from OpenGL.GL import *
from OpenGL.GLU import *

class AlignedQuad(qgl.scene.Leaf):
    def __init__(self, (w, h), alignx=0.5, aligny=1.0):
        x1,y1 = -w*(1.0-alignx),-h*(1.0-aligny)
        x2,y2 = x1+w, y1+h
        self.vertices = (x1, y1, 0.0), (x1, y2, 0.0), (x2, y2, 0.0), (x2, y1, 0.0)
        self.texture_coords = ((0.0,0.0),(0.0,1.0),(1.0,1.0),(1.0,0.0))

    def compile(self):
        lst = qgl.render.GLDisplayList()
        glNewList(lst.id, GL_COMPILE)
        v = self.vertices
        t = self.texture_coords
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
        self.list = lst

    def execute(self):
        glCallList(self.list.id)

class Triangle(qgl.scene.Leaf):
    def __init__(self, v):
        self.vertices = v

    def compile(self):
        lst = qgl.render.GLDisplayList()
        glNewList(lst.id, GL_COMPILE)

        v = self.vertices
        glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
        glEnable ( GL_COLOR_MATERIAL )
        glBegin(GL_TRIANGLES)
        glColor4f(1.0, 0.6, 0.0, 0.2)
        glVertex2f(v[0][0],v[0][1])
        glVertex2f(v[1][0],v[1][1])
        glVertex2f(v[2][0],v[2][1])
        glEnd()
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glDisable ( GL_COLOR_MATERIAL )

        glEndList()
        self.list = lst

    def execute(self):
        glCallList(self.list.id)

class PorcionMuzza(qgl.scene.Leaf):
    def __init__(self, v):
        self.vertices = v

    def compile(self):
        lst = qgl.render.GLDisplayList()
        glNewList(lst.id, GL_COMPILE)

        v = self.vertices
        glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
        glEnable ( GL_COLOR_MATERIAL )
        glBegin(GL_TRIANGLE_STRIP)
        glColor4f(1.0, 0.6, 0.0, 0.2)
        glVertex2f(v[0][0],v[0][1])
        glColor4f(1.0, 0.6, 0.0, 0.6)
        glVertex2f(v[1][0],v[1][1])
        glVertex2f(v[2][0],v[2][1])
        glVertex2f(v[3][0],v[3][1])
        glVertex2f(v[4][0],v[4][1])
        glEnd()
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glDisable ( GL_COLOR_MATERIAL )

        glEndList()
        self.list = lst

    def execute(self):
        glCallList(self.list.id)

class TextoAlineado(qgl.scene.Leaf):
    def __init__(self, text, font, foreground=(1,1,1), background=None, size=32, alignx=0.5, aligny=1.0):
        self._text = text 
        self.foreground = foreground
        self.background = background
        self.size = size
        self.font = font
        self.alignx = alignx
        self.aligny = aligny

    def set_text(self, text):
        self._text = text
        self.parent.accept(self.parent.compiler)
    def get_text(self):
        return self._text
    text = property(fset=set_text, fget=get_text)


    def compile(self):
        key = self.font, self.foreground, self.background
        if key in qgl.render.qgl_cache:
            self.font_object = qgl.render.qgl_cache[key]
        else:
            font = qgl.render.FontTexture(*key)
            qgl.render.qgl_cache[key] = font
            self.font_object = font

        lst = qgl.render.GLDisplayList()
        glNewList(lst.id, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.font_object.texture.id)
        glBegin(GL_QUADS)
        ox,oy = 0.0,0.0

        for c in self._text:
            tex = self.font_object.alphabet[c]
            h = tex[2][1] - tex[0][1]
            w = tex[2][0] - tex[0][0]
            h *= self.size
            w *= self.size
            ox += w
        ox = - ox * (self.alignx)
        oy = - h * self.aligny
            
        for c in self._text:
            tex = self.font_object.alphabet[c]
            h = tex[2][1] - tex[0][1]
            w = tex[2][0] - tex[0][0]
            h *= self.size
            w *= self.size
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
        self.list = lst

    def execute(self):
        glCallList(self.list.id)
