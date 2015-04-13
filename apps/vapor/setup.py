#!/usr/bin/env python
# coding:utf-8

from distutils.core import setup

setup(name='Vapor',
      version='0.1',
      description='Python Gaming Interface',
      author='Italo Maia',
      author_email='italo.maia@gmail.com',
      url='https://github.com/italomaia/turtle-linux',
      scripts=['scripts/run_vapor.py'],
      packages=['vapor'],
      data_files=[('vapor/glade', ['vapor/main.glade'])]
)