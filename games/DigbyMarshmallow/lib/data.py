"""Data loaders.

Add functions here to load specific types of resources.

"""

import os
import textwrap

from pyglet import media
from pyglet import font

import squirtle

import config
from common import *
from constants import *


font.add_directory(os.path.join(DATA_DIR, "fonts"))
if not os.path.exists("profiles"):
    os.mkdir("profiles")


def file_path(path):
    return os.path.join(DATA_DIR, path)


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


def load_scene(path):
    scene_path = os.path.join(DATA_DIR, "scenes", path)
    lines = [line.strip().decode('ascii') for line in open(scene_path)]
    flags = {}
    frames = []
    text = ''
    image = None
    for line in lines:
        if line.startswith('--'):
            frames.append((text.strip(), image, flags))
            text = ''
            image = None
            flags = {}
            continue
            
        if line.startswith('IMAGE:'):
            image = line[6:].strip()
        elif line.startswith('CENTER'):
            flags['center'] = True
        elif line:
            text += line + '\n'
    if text or image: frames.append((text.strip(), image, flags))
    return frames

def load_profile(path):
    imports = ''
    scope = {}
    profile_path = os.path.join("profiles", path)
    exec imports in scope
    exec open(profile_path, "rb") in scope
    return scope

def save_profile(path, state):
    profile_path = os.path.join("profiles", path)
    open(profile_path, "wb").write(repr(state))
        
def load_stage(path):
    """Load a stage file from the stages directory.

    :Parameters:
        `path` : str
            The relative path from the stages directory to the file.

    """
    imports = textwrap.dedent("""\
        from vector import Vector
        from world import StaticObject
        from squirtle import SVG
        import swag, enemy, oxygen, door, signpost
    """)
    scope = {}
    stage_path = os.path.join(DATA_DIR, "stages", path)
    exec imports in scope
    exec open(stage_path, "rb") in scope
    return scope


def save_stage(path, world):
    """Save a stage to the stages directory.

    :Parameters:
        `path` : str
            The relative path from the stages directory to the file.

    """
    stage_path = os.path.join(DATA_DIR, "stages", path)
    backup_path = os.path.join(DATA_DIR, "stages", path + ".backup")
    if os.path.exists(stage_path):
        import shutil
        shutil.copyfile(stage_path, backup_path)
    open(stage_path, "wb").write(repr(world))


def load_image(path, **kwds):
    """Load an image file from the images directory.

    Additional arguments are passed to squirtle.SVG.

    :Parameters:
        `path` : str
            The relative path from the images directory to the file.

    """
    if isinstance(path, basestring):
        image_path = os.path.join(DATA_DIR, "images", path)
    else:
        image_path = os.path.join(DATA_DIR, "images", *path)
    return squirtle.SVG(image_path, **kwds)


def load_styles():
    """Load the list of world styles represented by the data.

    """
    styles = []
    backgrounds_path = os.path.join(DATA_DIR, "images", "background")
    for filename in os.listdir(backgrounds_path):
        name, ext = os.path.splitext(filename)
        if ext in (".svg", ".svgz"):
            styles.append(name)
    return styles


def load_palette(name, **kwds):
    """Load the list of images in a particular style.

    Additional arguments are passed to squirtle.SVG.

    :Parameters:
        `name` : str
            The name of the style to load.

    """
    svg_list = []
    style_path = os.path.join(DATA_DIR, "images", name)
    generic_path = os.path.join(DATA_DIR, "images", 'generic')
    
    for filename in os.listdir(style_path):
        filepath = os.path.join(name, filename)
        base, ext = os.path.splitext(filename)
        if ext in (".svg", ".svgz"):
            svg = load_image(filepath, **kwds)
            svg_list.append(svg)
    
    for filename in os.listdir(generic_path):
        filepath = os.path.join('generic', filename)
        base, ext = os.path.splitext(filename)
        if ext in (".svg", ".svgz"):
            svg = load_image(filepath, **kwds)
            svg_list.append(svg)
    
    return svg_list
