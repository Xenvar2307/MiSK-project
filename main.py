import pygame
from enum import Enum

pygame.init()

# display
screen_width = 1600
screen_height = 900
side_padding = 100
ground_level = screen_height - side_padding
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("MiSK - project")

# font
scale_font = pygame.font.SysFont("Times New Roman", 20)

# frames
fps = 60
clock = pygame.time.Clock()
# colors
black = (0, 0, 0)
white = (255, 255, 255)

meters_to_pixel_ratio = 100


def get_scale_step(input: int) -> int:  # 0,1,2 -> 1,2,5; 3,4,5 -> 10,20,50
    multiply = 10 ** int(input / 3)
    match input % 3:
        case 0:
            return multiply
        case 1:
            return 2 * multiply
        case 2:
            return 5 * multiply


def meters_to_text(meters: int):
    if meters < 1000:
        return f"{meters}m"
    else:
        return f"{meters/1000}km"


def reset_screen():
    screen.fill(black)


def draw_scale():
    # base lines
    pygame.draw.line(
        screen,
        white,
        (side_padding, ground_level),
        (side_padding, side_padding),
        width=4,
    )

    pygame.draw.line(
        screen,
        white,
        (side_padding, ground_level),
        (screen_width - side_padding, ground_level),
        width=4,
    )

    # get scale step
    temp = 0
    step = get_scale_step(temp)
    while step * meters_to_pixel_ratio < 50:
        temp += 1
        step = get_scale_step(temp)

    # scale x
    meters = 0
    start = side_padding
    count_lines = 1
    lines_to_draw = int(
        (screen_width - 2 * side_padding) / (meters_to_pixel_ratio * step)
    )
    text_step = int(lines_to_draw / 5)
    first = True
    while count_lines <= lines_to_draw:
        meters += step
        start += step * meters_to_pixel_ratio
        pygame.draw.line(
            screen,
            white,
            (start, ground_level),
            (start, ground_level + int(0.25 * side_padding)),
            width=2,
        )

        if count_lines % text_step == 0 or first:
            text_image = scale_font.render(meters_to_text(meters), True, white)
            text_image_rect = text_image.get_rect()
            text_image_rect.center = (start, ground_level + int(0.5 * side_padding))
            text_image.convert_alpha()
            screen.blit(text_image, text_image_rect)

        count_lines += 1
        first = False

    # scale y
    meters = 0
    start = ground_level
    count_lines = 1
    lines_to_draw = int(
        (screen_height - 2 * side_padding) / (meters_to_pixel_ratio * step)
    )
    text_step = int(lines_to_draw / 5)
    first = True
    while count_lines <= lines_to_draw:
        meters += step
        start -= step * meters_to_pixel_ratio
        pygame.draw.line(
            screen,
            white,
            (side_padding, start),
            (side_padding - int(0.25 * side_padding), start),
            width=2,
        )

        if count_lines % text_step == 0 or first:
            text_image = scale_font.render(meters_to_text(meters), True, white)
            text_image_rect = text_image.get_rect()
            text_image_rect.center = (side_padding - int(0.6 * side_padding), start)
            text_image.convert_alpha()
            screen.blit(text_image, text_image_rect)

        count_lines += 1
        first = False


class Trebuchet:
    def __init__(self) -> None:
        pass


class main_module:
    def run(self):
        # event control
        run = True
        Next_module = Module_names.Exit_app

        global meters_to_pixel_ratio
        meters_to_pixel_ratio = 25

        while run:
            draw_scale()

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
