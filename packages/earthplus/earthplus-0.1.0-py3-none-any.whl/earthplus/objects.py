from OpenGL.GL import *

class Cube:
    def __init__(self, x=0, y=0, z=-5, size=1):
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.rotation = 0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 1, 1, 1)

        half = self.size / 2

        glBegin(GL_TRIANGLES)
        # Front face (red)
        glColor3ub(255, 0, 0)
        glVertex3f(-half, -half, half)
        glVertex3f(half, -half, half)
        glVertex3f(half, half, half)

        glVertex3f(-half, -half, half)
        glVertex3f(half, half, half)
        glVertex3f(-half, half, half)

        # Back face (green)
        glColor3ub(0, 255, 0)
        glVertex3f(-half, -half, -half)
        glVertex3f(half, -half, -half)
        glVertex3f(half, half, -half)

        glVertex3f(-half, -half, -half)
        glVertex3f(half, half, -half)
        glVertex3f(-half, half, -half)

        # Left face (blue)
        glColor3ub(0, 0, 255)
        glVertex3f(-half, -half, -half)
        glVertex3f(-half, -half, half)
        glVertex3f(-half, half, half)

        glVertex3f(-half, -half, -half)
        glVertex3f(-half, half, half)
        glVertex3f(-half, half, -half)

        # Right face (yellow)
        glColor3ub(255, 255, 0)
        glVertex3f(half, -half, -half)
        glVertex3f(half, -half, half)
        glVertex3f(half, half, half)

        glVertex3f(half, -half, -half)
        glVertex3f(half, half, half)
        glVertex3f(half, half, -half)

        # Top face (cyan)
        glColor3ub(0, 255, 255)
        glVertex3f(-half, half, -half)
        glVertex3f(half, half, -half)
        glVertex3f(half, half, half)

        glVertex3f(-half, half, -half)
        glVertex3f(half, half, half)
        glVertex3f(-half, half, half)

        # Bottom face (magenta)
        glColor3ub(255, 0, 255)
        glVertex3f(-half, -half, -half)
        glVertex3f(half, -half, -half)
        glVertex3f(half, -half, half)

        glVertex3f(-half, -half, -half)
        glVertex3f(half, -half, half)
        glVertex3f(-half, -half, half)
        glEnd()

        glPopMatrix()
        self.rotation += 1
