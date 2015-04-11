"""Data loaders.

Add functions here to load specific types of resources.

"""

from __future__ import division

import os

from pyglet import font
from pyglet import image
from pyglet import media
from pyglet import resource
from pyglet.gl import *
import squirtle

import config
from common import *
from constants import *

resource.path.append(DATA_DIR + "/images")
font.add_directory(os.path.join(DATA_DIR, "fonts"))
resource.reindex()

def load_file(path, mode="rb"):
    """Open a file.

    :Parameters:
        `path` : str
            The relative path from the data directory to the file.
        `mode` : str
            The mode to use when opening the file (default: "rb").

    """
    file_path = os.path.join(DATA_DIR, path)
    return open(file_path, mode)

def round_up2(x):
    n = 1
    while n < x: n *= 2
    return n
    
def load_image(name, centered=False):
    if name in resource.get_cached_texture_names():
        img = resource.texture(name)
    else:
        img = resource.texture(name)
        assert img.width in [1,2,4,8,16,32,64,128,256,512], "Carrie! Resize %s" % name
        assert img.height in [1,2,4,8,16,32,64,128,256,512], "Carrie! Resize %s" % name    
        glBindTexture(img.texture.target, img.texture.id)
        glTexParameteri(img.texture.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        data = img.texture.image_data.get_data('RGBA', img.texture.width * 4)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, img.texture.width, img.texture.height, GL_RGBA, GL_UNSIGNED_BYTE, data)
        img.texture.tex_coords = (0,0,0,1,0,0,1,1,0,0,1,0)
    if centered:
        img.texture.anchor_x = img.texture.width // 2
        img.texture.anchor_y = img.texture.height // 2
    return img.texture

def load_svg(path, **kwds):
    """Load a scalable vector graphic from the images directory.

    :Parameters:
        `path` : str
            The relative path from the images directory to the file.

    """
    svg_path = os.path.join(DATA_DIR, "images", path)
    svg = squirtle.SVG(svg_path, **kwds)
    return svg

def load_song(path):
    """Load a music stream from the music directory.

    :Parameters:
        `path` : str
            The relative path from the music directory to the file.

    """
    song_path = os.path.join(DATA_DIR, "music", path)
    return media.load(song_path)


def load_sound(path):
    """Load a static sound source from the sounds directory.

    :Parameters:
        `path` : str
            The relative path from the sounds directory to the file.

    """
    sound_path = os.path.join(DATA_DIR, "sounds", path)
    return media.load(sound_path, streaming=False)

def load_scene(name):
    file = load_file(os.path.join("scenes", name))
    pages = []
    text = ''
    for line in file:
        line = line.strip()
        if line.startswith('--'):
            pages.append(text)
            text = ''
        elif line:
            text += line
    if text: pages.append(text)
    return pages
