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

This module contains functions for loading mesh data from files.

"""
        
def load_obj(filename, swapyz=False):
    """
    Load a wavefront OBJ file, and return vertices, texcoords, normals, 
    and faces.
    """
    vertices = []
    normals = []
    texcoords = []
    faces = []
    
    for line in open(filename, "r"):
        values = line.split()
        if len(values) < 1:
            continue
        if values[0] == 'v':
            v = [float(i) for i in values[1:4]]
            if swapyz:
                v = v[0],v[2],v[1]
            vertices.append(v)
        elif values[0] == 'vn':
            v = [float(i) for i in values[1:4]]
            if swapyz:
                v = v[0],v[2],v[1]
            normals.append(v)
        elif values[0] == 'vt':
            texcoords.append([float(i) for i in values[1:3]])
        elif values[0] == 'f':
            face = []
            local_texcoords = []
            norms = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 2 and len(w[1]) > 0:
                    local_texcoords.append(int(w[1]))
                else:
                    local_texcoords.append(0)
                if len(w) >= 3 and len(w[2]) > 0:
                    norms.append(int(w[2]))
                else:
                    norms.append(0)
            faces.append((face,norms,local_texcoords))
    return vertices, texcoords, normals, faces
    
def load(filename):
    if filename[-3:] == 'obj':
        return load_obj(filename)
    else:
        raise IOError("Unknown filetype")
    





