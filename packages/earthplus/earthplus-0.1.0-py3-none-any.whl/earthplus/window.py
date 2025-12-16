import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *

class Window:
    def __init__(self, width=800, height=600, title="Earth+ Engine"):
        pygame.init()
        pygame.display.set_caption(title)
        pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL, 24)

        self.width = width
        self.height = height

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, width / height, 0.1, 100)
        glMatrixMode(GL_MODELVIEW)

        # Recommended GL setup for 3D rendering
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def update(self):
        pygame.display.flip()
