import pygame
from enum import Enum

pygame.init()

# display
screen_width = 1600
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("MiSK - project")

# frames
fps = 60
clock = pygame.time.Clock()
# colors
black = (0, 0, 0)
white = (255, 255, 255)

meters_to_pixel_ratio = 100


def reset_screen():
    screen.fill(black)


class Trebuchet:
    def __init__(self) -> None:
        pass


class main_module:
    def run(self):
        # event control
        run = True
        Next_module = Module_names.Exit_app

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    Next_module = Module_names.Exit_app
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked = True
                else:
                    clicked = False

            # updating display
            pygame.display.update()

        return Next_module


class Exit_app_module:
    def run(self):
        pygame.quit()
        return Module_names.Exit_app


# module control


class Module_names(Enum):
    Main_module = main_module()
    Exit_app = Exit_app_module()


# main

current_module = Module_names.Main_module

while current_module != Module_names.Exit_app:
    reset_screen()
    current_module = current_module.value.run()

pygame.quit()
