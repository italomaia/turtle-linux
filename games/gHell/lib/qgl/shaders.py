import qgl.scene
from ctypes import *
import sys
 
try:
    # For OpenGL-ctypes
    from OpenGL import platform
    gl = platform.OpenGL
except ImportError:
    # For PyOpenGL
    gl = cdll.LoadLibrary('libGL.so')
 
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

GL_FRAGMENT_SHADER_ARB = 0x8B30
GL_VERTEX_SHADER_ARB = 0x8B31
GL_OBJECT_COMPILE_STATUS_ARB= 0x8B81
GL_OBJECT_LINK_STATUS_ARB = 0x8B82
GL_INFO_LOG_LENGTH_ARB = 0x8B84

glCreateShaderObjectARB = gl.glCreateShaderObjectARB
glShaderSourceARB = gl.glShaderSourceARB
glShaderSourceARB.argtypes = [c_int, c_int, POINTER(c_char_p), POINTER(c_int)]
glCompileShaderARB = gl.glCompileShaderARB
glGetObjectParameterivARB = gl.glGetObjectParameterivARB
glGetObjectParameterivARB.argtypes = [c_int, c_int, POINTER(c_int)]
glCreateProgramObjectARB = gl.glCreateProgramObjectARB
glGetInfoLogARB = gl.glGetShaderInfoLog
glGetInfoLogARB.argtypes = [c_int, c_int, POINTER(c_int), c_char_p]
glAttachObjectARB = gl.glAttachObjectARB
glLinkProgramARB = gl.glLinkProgramARB
glDeleteObjectARB = gl.glDeleteObjectARB
glGetError = gl.glGetError
glUseProgramObjectARB = gl.glUseProgramObjectARB
glGetUniformLocationARB = gl.glGetUniformLocationARB
glUniform1fARB = gl.glUniform1fARB
glUniform1fARB.argtypes = [c_int, c_float]

def check_for_opengl_error(s):
    e = glGetError()
    if (e != GL_NO_ERROR):
        print 'GLERROR: ', s, gluErrorString(e)
        raise SystemExit


class Program(qgl.scene.Leaf):
    def __init__(self, vertex_source, fragment_source):
        self.glDeleteObjectARB = glDeleteObjectARB
        self.updates = {}
        self.vertex_source = vertex_source
        self.fragment_source = fragment_source
        self.program = None
        self.vertex_shader = None
        self.fragment_shader = None
    
    
    def compile(self):
        self.create_program(self.vertex_source, self.fragment_source)
        check_for_opengl_error('CreateProgram')
    
    def create_program(self, vertex_source, fragment_source):
        vertex_shader = None
        fragment_shader = None
        program = glCreateProgramObjectARB()
     
        if vertex_source:
            self.vertex_shader = self.compile_shader(vertex_source, GL_VERTEX_SHADER_ARB)
            check_for_opengl_error('CompileVertexShader')
            glAttachObjectARB(program, self.vertex_shader)
            check_for_opengl_error('AttachVertexShader')
        if fragment_source:
            self.fragment_shader = self.compile_shader(fragment_source, GL_FRAGMENT_SHADER_ARB)
            check_for_opengl_error('CompileFragmentShader')
            glAttachObjectARB(program, self.fragment_shader)
            check_for_opengl_error('AttachFragmentShader')
            
     
        glLinkProgramARB(program)
        self.program = program
        
    def print_log(self, shader):
        length = c_int()
        glGetObjectParameterivARB(shader, GL_INFO_LOG_LENGTH_ARB, byref(length))
     
        if length.value > 0:
            log = create_string_buffer(length.value)
            glGetInfoLogARB(shader, length, byref(length), log)
            print >> sys.stderr, log.value

    def compile_shader(self, source, shader_type):
        shader = glCreateShaderObjectARB(shader_type)
        check_for_opengl_error('CreateShader')
        source = c_char_p(source)
        length = c_int(-1)
        glShaderSourceARB(shader, 1, byref(source), byref(length))
        check_for_opengl_error('ShaderSource')
        glCompileShaderARB(shader)
        check_for_opengl_error('CompileShader')
        status = c_int()
        glGetObjectParameterivARB(shader, GL_OBJECT_COMPILE_STATUS_ARB, byref(status))
        check_for_opengl_error('CheckShader')
        if (not status.value):
            self.print_log(shader)
            raise SystemExit
        return shader
        
    def update(self, **kw):
        self.updates.update(kw)

    def execute(self):
        glUseProgramObjectARB(self.program)
        check_for_opengl_error('UseProgramObject')
        for key in self.updates:
            ptr = glGetUniformLocationARB(self.program, key)
            
            glUniform1fARB(ptr, self.updates[key])
        check_for_opengl_error('Execute')
            
    def __del__(self):
        if self.program:
            self.glDeleteObjectARB(self.program)
        if self.vertex_shader:
            self.glDeleteObjectARB(self.vertex_shader)
        if self.fragment_shader:
            self.glDeleteObjectARB(self.fragment_shader)

