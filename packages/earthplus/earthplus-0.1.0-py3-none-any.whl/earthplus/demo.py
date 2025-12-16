import sys
import pygame
from pygame.locals import QUIT
from .window import Window
from .objects import Cube
from .renderer import render_scene

def run_demo():
    win = Window(900, 600, "Earth+ Demo")
    cube = Cube()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        win.clear()
        render_scene([cube])
        win.update()
        clock.tick(60)

if __name__ == "__main__":
    run_demo()
