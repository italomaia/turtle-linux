from setuptools import setup
from distutils.core import Extension
import glob

setup(
  name='Dandelion',
  data_files=[('music', glob.glob('music/*')), ('', ['icon.png'])],

  app=['bundle_mac.py'],
  setup_requires=['py2app'],
  options={'py2app': {'iconfile': 'icon.icns'}},
)
