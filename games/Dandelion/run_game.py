# Author: Alexander Malmberg <alexander@malmberg.org>

import pygame
import sys
import OpenGL
#OpenGL.ERROR_CHECKING = True
#OpenGL.ERROR_LOGGING = True
from OpenGL import GL

import game_loop


def main():
  pygame.init()

  # TODO(alex): Options for this. Default to full-screen, desktop res?
  flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
  if len(sys.argv) > 1 and sys.argv[1] == '--fullscreen':
    width, height = 0, 0
    flags |= pygame.FULLSCREEN
  else:
    width, height = 960, 600
  # TODO(alex): Options for this, too, but our life will be way easier
  # if we can rely on anti-aliasing.
  pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
  pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

  pygame.display.set_caption('Dandelion')
  pygame.display.set_icon(pygame.image.load('icon.png'))
  screen = pygame.display.set_mode((width, height), flags)

  # Get the actual size of our window.
  width = screen.get_width()
  height = screen.get_height()
  aspect_ratio = float(width) / height
  GL.glViewport(0, 0, width, height)
  GL.glMatrixMode(GL.GL_PROJECTION)
  GL.glOrtho(-aspect_ratio, aspect_ratio, -1, 1, -1, 1)
  GL.glMatrixMode(GL.GL_MODELVIEW)

  game = game_loop.Game(aspect_ratio)
  game.StartTitleScreen()
  game.Run()


main()
