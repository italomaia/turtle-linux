"""
Script for building the example.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import os


NAME = 'Typus Pocus'
VERSION = '0.01'

plist = dict(
    CFBundleIconFile=NAME,
    CFBundleName=NAME,
    CFBundleShortVersionString=VERSION,
    CFBundleGetInfoString=' '.join([NAME, VERSION]),
    CFBundleExecutable=NAME,
    CFBundleIdentifier='org.pyar.pocus',
)


try:
    import py2app
    setup(
        data_files=[ 'data', "intro.py"],
        app=[
        dict(script="game.py", plist=plist ),
        ],
    )
except ImportError:
    pass

try:
    import py2exe

    data_files = [ (x, [os.path.join(x, e) for e in z]) for d in ("audiencia", "escenario", "sounds", "music") for x,y,z in os.walk(d) if not ".svn" in x ] + [ "readme.txt"]
    setup(console=["game.py"], data_files = data_files)

except ImportError:
    pass



