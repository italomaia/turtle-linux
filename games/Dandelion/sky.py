# Author: Alexander Malmberg <alexander@malmberg.org>

import ctypes
import math
import OpenGL
from OpenGL.GL import *

import drawable
import shaders


sky_vshader = """\
#version 120

varying vec2 position;

void main() {
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  position = gl_Vertex.xy;
}
"""
sky_fshader = """\
#version 120

uniform vec3 color1, color2;
uniform vec2 center;
varying vec2 position;

void main() {
  float a = distance(position, center) * 0.5;
  gl_FragColor.rgb = mix(color1, color2, a);
}
"""


class Sky(drawable.Drawable):
  # TODO(alex): state on position, be able to move it up and down
  def __init__(self, game, width):
    self.width = width
    self.c1 = list(game.transition['sky'][0])
    self.c2 = list(game.transition['sky'][1])
    self.center = (0, 0.7)

    self.program = shaders.CompileProgram(
      'sky', sky_vshader, sky_fshader)

    self.c1_loc = glGetUniformLocation(self.program, 'color1')
    self.c2_loc = glGetUniformLocation(self.program, 'color2')
    self.center_loc = glGetUniformLocation(self.program, 'center')

  def Draw(self):
    glPushMatrix()
    glLoadIdentity()  # Ignore camera position.
    glUseProgram(self.program)
    glUniform3f(self.c1_loc, *self.c2)
    glUniform3f(self.c2_loc, *self.c1)
    glUniform2f(self.center_loc, *self.center)

    glBegin(GL_TRIANGLE_STRIP)
    glVertex(-self.width, -1)
    glVertex(-self.width,  1)
    glVertex( self.width, -1)
    glVertex( self.width,  1)
    glEnd()

    glUseProgram(0)
    glPopMatrix()
