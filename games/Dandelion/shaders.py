# Author: Alexander Malmberg <alexander@malmberg.org>

import math
import random
import sys
import OpenGL
from OpenGL.GL import *


def Lerp(f, a1, a2):
  """Linear interpolate between a1 and a2.

  Works for iterables and simple values.
  """
  try:
    return [v2 * f + (1 - f) * v1 for v1, v2 in zip(a1, a2)]
  except:
    return a2 * f + (1 -f) * a1


def SmoothStep(f):
  return f * f * (3 - 2 * f)


def CompileProgram(name, vshader_src=None, fshader_src=None,
                   bound_attribs=None):
  program = glCreateProgram()

  for kind, src, text in ((GL_VERTEX_SHADER, vshader_src, 'vertex'),
                          (GL_FRAGMENT_SHADER, fshader_src, 'fragment')):
    if src:
      shader = glCreateShader(kind)
      glShaderSource(shader, [src])
      glCompileShader(shader)
      result = glGetShaderiv(shader, GL_COMPILE_STATUS)
      if not result:
        print ('%s shader %s compilation failed: %s'
               % (name, text, glGetShaderInfoLog(shader)))
        sys.exit(1)
      glAttachShader(program, shader)
      glDeleteShader(shader)

  for i, b in enumerate(bound_attribs or []):
    glBindAttribLocation(program, i + 1, b)

  glLinkProgram(program)
  glValidateProgram(program)
  #print (glGetProgramInfoLog(program))

  return program


class Shaders(object):
  @classmethod
  def Init(self):
    self.InitIgnoreZW()
    self.InitWindShader()
    self.InitRock()


  ignore_zw_program = 0
  ignore_zw_vshader_src = """\
#version 120

void main() {
  vec4 v;
  v.xy = gl_Vertex.xy;
  v.z = 0.0;
  v.w = 1.0;
  gl_Position = gl_ModelViewProjectionMatrix * v;
  gl_FrontColor = gl_Color;
}
"""

  @classmethod
  def InitIgnoreZW(self):
    self.ignore_zw_program = CompileProgram(
      'ignore_zw', self.ignore_zw_vshader_src)

  @classmethod
  def UseIgnoreZW(self):
    """Sets Z and W to 0 and 1."""
    glUseProgram(self.ignore_zw_program)


  wind_tex = 0
  wind_program = 0
  screen_space_wind_program = 0
  wind_vshader_src = """\
#version 120

uniform float wind_offset;
uniform sampler1D wind;

void main() {
  float displacement = 0.05 * texture1D(
      wind, (gl_Vertex.w - wind_offset) * 0.01).r;
  vec4 v;
  v.x = gl_Vertex.x + displacement * gl_Vertex.z;
  v.y = gl_Vertex.y;
  v.z = 0.0;
  v.w = 1.0;
  gl_Position = gl_ModelViewProjectionMatrix * v;
  gl_FrontColor = gl_Color;
}
"""
  wind_color_mix_vshader_src = """\
#version 120

uniform float wind_offset;
uniform sampler1D wind;
uniform vec4 color1, color2;
attribute float color;

void main() {
  float displacement = 0.05 * texture1D(
      wind, (gl_Vertex.w - wind_offset) * 0.01).r;
  vec4 v;
  v.x = gl_Vertex.x + displacement * gl_Vertex.z;
  v.y = gl_Vertex.y;
  v.z = 0.0;
  v.w = 1.0;
  gl_Position = gl_ModelViewProjectionMatrix * v;
  gl_FrontColor = mix(color1, color2, color);
}
"""
  screen_space_wind_vshader_src = """\
#version 120

uniform float wind_offset;
uniform float strength;
uniform float screen_width;
uniform sampler1D wind;

void main() {
  vec4 v = gl_ModelViewProjectionMatrix * gl_Vertex;
  float displacement = 0.05 * texture1D(
      wind, (v.x * screen_width - wind_offset) * 0.01).r;
  v.x = v.x + displacement * strength;
  gl_Position = v;
  gl_FrontColor = gl_Color;
}
"""

  @classmethod
  def InitWindShader(self):
    w = 2048
    nsmooth = 128
    smooth = [random.uniform(0.2, 0.9) for _ in xrange(nsmooth)]

    wind_tex = (ctypes.c_ubyte * w)()
    for i in xrange(w):
      f, o = math.modf(i / float(w) * nsmooth)
      o = int(o)
      a = smooth[o]
      if o + 1 == nsmooth:
        b = smooth[0]
      else:
        b = smooth[o + 1]
      v = Lerp(f, a, b)
      v += v * v * random.gauss(0, 0.08)
      v = min(1, max(0, v))
      wind_tex[i] = int(255. * v)

    self.wind_tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_1D, self.wind_tex)
    glTexParameter(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_REPEAT)

    glTexImage1D(GL_TEXTURE_1D, 0, 1, w, 0, GL_RED, GL_UNSIGNED_BYTE, wind_tex)

    self.wind_program = CompileProgram('wind', self.wind_vshader_src)
    self.wind_color_mix_program = CompileProgram(
      'wind_color_mix', self.wind_color_mix_vshader_src,
      bound_attribs=['color'])
    self.screen_space_wind_program = CompileProgram(
      'screen_space_wind', self.screen_space_wind_vshader_src)

  @classmethod
  def UseWind(self, wind_offset):
    """Wind swaying.

    Color passed through. 'w' holds position wrt. wind. 'z' holds wind
    effect multiplier.
    """
    glUseProgram(self.wind_program)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_1D, self.wind_tex)
    glUniform1i(glGetUniformLocation(self.wind_program, 'wind'), 0)
    glUniform1f(glGetUniformLocation(self.wind_program, 'wind_offset'),
                wind_offset)

  @classmethod
  def UseWindColorMix(self, wind_offset, color1, color2):
    """Wind swaying.

    Color passed through. 'w' holds position wrt. wind. 'z' holds wind
    effect multiplier. Vertex attribute 1 holds color mix fraction.
    """
    glUseProgram(self.wind_color_mix_program)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_1D, self.wind_tex)
    glUniform1i(
      glGetUniformLocation(self.wind_color_mix_program, 'wind'), 1)
    glUniform1f(
      glGetUniformLocation(self.wind_color_mix_program, 'wind_offset'),
      wind_offset)
    glUniform4f(
      glGetUniformLocation(self.wind_color_mix_program, 'color1'), *color1)
    glUniform4f(
      glGetUniformLocation(self.wind_color_mix_program, 'color2'), *color2)

  @classmethod
  def UseScreenSpaceWind(self, wind_offset, strength, screen_width):
    """Wind swaying.

    Doesn't need special z/w coordinates. Color passed
    through. Strength taken from uniform. Position wrt. wind
    calculated from screen space coordinates. This means that the
    wind_offset has to be adjusted for camera position to match
    UseWind.
    """
    # TODO(alex): this is suboptimal. ideas:
    # - have w and z coordinates on seeds but apply displacement in
    #   screen space
    # - separate model and view matrix so wind can be applied in
    #   'view' space, but not 'model' space
    glUseProgram(self.screen_space_wind_program)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_1D, self.wind_tex)
    # Pre-divide it out here to save a per-vertex division in the shader.
    strength /= screen_width
    glUniform1i(
      glGetUniformLocation(self.screen_space_wind_program, 'wind'),
      0)
    glUniform1f(
      glGetUniformLocation(self.screen_space_wind_program, 'wind_offset'),
      wind_offset)
    glUniform1f(
      glGetUniformLocation(self.screen_space_wind_program, 'strength'),
      strength)
    glUniform1f(
      glGetUniformLocation(self.screen_space_wind_program, 'screen_width'),
      screen_width)


  rock_program = 0
  rock_vshader_src = """\
#version 120

varying vec2 position;

void main() {
  vec4 v;
  v.xy = gl_Vertex.xy;
  v.z = 0.0;
  v.w = 1.0;
  position = gl_Vertex.zw;
  gl_Position = gl_ModelViewProjectionMatrix * v;
}
"""
  rock_fshader_src = """\
#version 120

varying vec2 position;
uniform vec4 background, light_rock, dark_rock;

void main() {
  float a = min(min(min(position.x * 24, position.y * 15),
                    (1 - position.x) * 24),
                (1 - position.y) * 15);
  a = min(1, a);
  float f = position.y * 0.6 + position.x * 0.4;
  vec4 c = mix(light_rock, dark_rock, f);
  gl_FragColor = mix(background, c, a);
}
"""

  @classmethod
  def InitRock(self):
    self.rock_program = CompileProgram(
      'rock', self.rock_vshader_src, self.rock_fshader_src)

  @classmethod
  def UseRock(self, background, light_rock, dark_rock):
    """Rock shader."""
    glUseProgram(self.rock_program)
    glUniform4f(
      glGetUniformLocation(self.rock_program, 'background'), *background)
    glUniform4f(
      glGetUniformLocation(self.rock_program, 'light_rock'), *light_rock)
    glUniform4f(
      glGetUniformLocation(self.rock_program, 'dark_rock'), *dark_rock)
