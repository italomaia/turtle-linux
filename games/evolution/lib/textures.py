import pygame
from OpenGL.GL import *

class Texture:
    texture_id = None
    def __init__(self, image, internal_format=GL_RGBA):
        if isinstance(image, str):
            self.filename = image
            image = pygame.image.load(image)
        else:
            self.filename = repr(image)
        w, h = image.get_width(), image.get_height()
        self.width = w
        self.height = h
        data = pygame.image.tostring(image, 'RGBA', 1)
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glPixelStorei(GL_UNPACK_ROW_LENGTH, 0)
        glTexImage2D(GL_TEXTURE_2D, 0, internal_format, w, h,
             0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def __repr__(self):
        return '<Texture %rx%r %r>'%(self.width, self.height,
            self.filename)

    def __del__(self):
        if self.texture_id is None: return
        try:
            glDeleteTextures(self.texture_id)
            self.texture_id = None
        except NameError:
            # glDeleteTextures has been gobbled
            pass

    def render(self, mode=GL_MODULATE):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, mode)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(0, 0)
        glTexCoord2f(1, 0)
        glVertex2f(self.width, 0)
        glTexCoord2f(1, 1)
        glVertex2f(self.width, self.height)
        glTexCoord2f(0, 1)
        glVertex2f(0, self.height)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def sub(self, x, y, w, h):
        return SubTexture(self, x, y, w, h)


class SubTexture(Texture):
    def __init__(self, texture, x, y, w, h):
        self.__texture = texture            # don't collect the parent!
        self.filename = texture.filename
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.texture_id = texture.texture_id

    def render(self, frame=0):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBindTexture(GL_TEXTURE_2D, self.__texture.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glBegin(GL_QUADS)
        w, h = float(self.__texture.width), float(self.__texture.height)
        su, sv = self.x/w, self.y/h
        eu, ev = su + self.w/w, sv + self.h/h
        glTexCoord2f(su, sv)
        glVertex2f(0, 0)
        glTexCoord2f(eu, sv)
        glVertex2f(self.w, 0)
        glTexCoord2f(eu, ev)
        glVertex2f(self.w, self.h)
        glTexCoord2f(su, ev)
        glVertex2f(0, self.h)
        glEnd()
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)

    def __del__(self):
        pass



class TextureGrid(Texture):
    def __init__(self, filename, width, height):
        Texture.__init__(self, filename)
        self.frames = []
        self.frame_width = width
        self.frame_height = height

        for x in range(0, self.width, width):
            for y in range(0, self.height, height):
                x = float(x); y = float(y)
                uvs = [
                    (x / self.width, y / self.height),
                    ((x+width) / self.width, y / self.height),
                    ((x+width) / self.width, (y+height) / self.height),
                    (x / self.width, (y+height) / self.height),
                ]
                self.frames.append(uvs)

    def row(self, n):
        y = float(n * self.frame_height)
        frames = []
        for x in range(0, self.width, self.frame_width):
            x = float(x)
            uvs = [
                (x / self.width, y / self.height),
                ((x+self.frame_width) / self.width, y / self.height),
                ((x+self.frame_width) / self.width,
                    (y+self.frame_height) / self.height),
                (x / self.width, (y+self.frame_height) / self.height),
            ]
            frames.append(uvs)
        return TextureGridRow(self, frames, self.frame_width,
            self.frame_height)

class TextureGridRow(Texture):
    def __init__(self, texture, frames, frame_width, frame_height):
        self.__texture = texture            # don't collect the parent!
        self.filename = texture.filename
        self.width = texture.width
        self.height = texture.height
        self.texture_id = texture.texture_id
        self.frames = frames
        self.frame_width = frame_width
        self.frame_height = frame_height

    def render(self, frame=0):
        uvs = self.frames[frame]
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBindTexture(GL_TEXTURE_2D, self.__texture.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glBegin(GL_QUADS)
        glTexCoord2f(*uvs[0])
        glVertex2f(0, 0)
        glTexCoord2f(*uvs[1])
        glVertex2f(self.frame_width, 0)
        glTexCoord2f(*uvs[2])
        glVertex2f(self.frame_width, self.frame_height)
        glTexCoord2f(*uvs[3])
        glVertex2f(0, self.frame_height)
        glEnd()
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)

    def __del__(self):
        pass


