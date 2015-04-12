from setuptools import setup
from distutils.core import Extension
import py2exe
import glob

setup(
  name='Dandelion',
  data_files=[('music', glob.glob('music/*'))],

  windows=[dict(
    script='bundle_win.py',
    icon_resources=[(0, 'Dandelion.ico')],
    )],
)
