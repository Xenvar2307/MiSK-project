import pygame
import math
from enum import Enum

pygame.init()

# display
screen_width = 1600
screen_height = 900
screen_height_middle = screen_height / 2
screen_width_middle = screen_width / 2
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
green = (0, 255, 0)

meters_to_pixel_ratio = 100


def add_points(x, y):
    temp = []
    temp.append(x[0] + y[0])
    temp.append(x[1] + y[1])
    return tuple(temp)


def to_int(tuple):
    temp = (int(tuple[0]), int(tuple[1]))
    return temp


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
    def __init__(
        self,
        long_arm_length,
        short_arm_length,
        sling_length,
        pivot_height,
        weight_length,
        projectile_mass,
        weight_mass,
    ) -> None:
        self.long_arm_length = long_arm_length
        self.short_arm_length = short_arm_length
        self.sling_length = sling_length
        self.pivot_height = pivot_height
        self.weight_length = weight_length
        self.projectile_mass = projectile_mass
        self.weight_mass = weight_mass

        # update part

        # state
        self.pivot_arm_angle = (
            math.asin(self.pivot_height / self.long_arm_length) + math.pi / 2
        )
        self.arm_sling_angle = math.asin(self.pivot_height / self.long_arm_length)
        self.arm_weight_angle = math.pi / 2 - math.asin(
            self.pivot_height / self.long_arm_length
        )
        print(math.degrees(self.pivot_arm_angle))
        print(math.degrees(self.arm_sling_angle))
        print(math.degrees(self.arm_weight_angle))

        # surowe liczenie na pałe
        # stałe
        self.base_point = (screen_width_middle, ground_level)
        self.pivot_point = add_points(
            self.base_point, (0, -meters_to_pixel_ratio * self.pivot_height)
        )
        # zmienne TO DO ALL
        self.end_long_arm = add_points(
            self.base_point,
            (
                -self.long_arm_length
                * math.sin(self.pivot_arm_angle)
                * meters_to_pixel_ratio,
                -meters_to_pixel_ratio
                * (
                    self.long_arm_length * math.cos(self.pivot_arm_angle)
                    + self.pivot_height
                ),
            ),
        )
        self.end_short_arm = add_points(
            self.base_point,
            (
                meters_to_pixel_ratio
                * (self.short_arm_length * math.sin(self.pivot_arm_angle)),
                -meters_to_pixel_ratio
                * (
                    -self.short_arm_length * math.cos(self.pivot_arm_angle)
                    + self.pivot_height
                ),
            ),
        )

        self.projectile_point = add_points(
            self.base_point,
            (
                meters_to_pixel_ratio
                * (
                    -self.long_arm_length * math.sin(self.pivot_arm_angle)
                    - self.sling_length
                    * math.sin(self.arm_sling_angle - self.pivot_arm_angle)
                ),
                -meters_to_pixel_ratio
                * (
                    self.long_arm_length * math.cos(self.pivot_arm_angle)
                    + self.pivot_height
                    - self.sling_length
                    * math.cos(self.arm_sling_angle - self.pivot_arm_angle)
                ),
            ),
        )
        self.weight_point = add_points(
            self.base_point,
            (
                meters_to_pixel_ratio
                * (
                    self.short_arm_length * math.sin(self.pivot_arm_angle)
                    - self.weight_length
                    * math.sin(self.pivot_arm_angle + self.arm_weight_angle)
                ),
                -meters_to_pixel_ratio
                * (
                    -self.short_arm_length * math.cos(self.pivot_arm_angle)
                    + self.pivot_height
                    + self.weight_length
                    * math.cos(self.pivot_arm_angle + self.arm_weight_angle)
                ),
            ),
        )

    def update(self):
        # TO DO aktualizacja kątów
        #
        #
        #
        # ustawianie punktów do pozycji trebusza
        self.end_long_arm = add_points(
            self.base_point,
            (
                -self.long_arm_length
                * math.sin(self.pivot_arm_angle)
                * meters_to_pixel_ratio,
                -meters_to_pixel_ratio
                * (
                    self.long_arm_length * math.cos(self.pivot_arm_angle)
                    + self.pivot_height
                ),
            ),
        )
        self.end_short_arm = add_points(
            self.base_point,
            (
                meters_to_pixel_ratio
                * (self.short_arm_length * math.sin(self.pivot_arm_angle)),
                -meters_to_pixel_ratio
                * (
                    -self.short_arm_length * math.cos(self.pivot_arm_angle)
                    + self.pivot_height
                ),
            ),
        )

        self.projectile_point = add_points(
            self.base_point,
            (
                meters_to_pixel_ratio
                * (
                    -self.long_arm_length * math.sin(self.pivot_arm_angle)
                    - self.sling_length
                    * math.sin(self.arm_sling_angle - self.pivot_arm_angle)
                ),
                -meters_to_pixel_ratio
                * (
                    self.long_arm_length * math.cos(self.pivot_arm_angle)
                    + self.pivot_height
                    - self.sling_length
                    * math.cos(self.arm_sling_angle - self.pivot_arm_angle)
                ),
            ),
        )
        self.weight_point = add_points(
            self.base_point,
            (
                meters_to_pixel_ratio
                * (
                    self.short_arm_length * math.sin(self.pivot_arm_angle)
                    - self.weight_length
                    * math.sin(self.pivot_arm_angle + self.arm_weight_angle)
                ),
                -meters_to_pixel_ratio
                * (
                    -self.short_arm_length * math.cos(self.pivot_arm_angle)
                    + self.pivot_height
                    + self.weight_length
                    * math.cos(self.pivot_arm_angle + self.arm_weight_angle)
                ),
            ),
        )

    def draw(self, subtitles):
        pygame.draw.line(
            screen,
            white,
            to_int(self.base_point),
            to_int(self.pivot_point),
            width=4,
        )

        pygame.draw.line(
            screen,
            green,
            to_int(self.end_short_arm),
            to_int(self.end_long_arm),
            width=4,
        )

        pygame.draw.line(
            screen,
            green,
            to_int(self.end_short_arm),
            to_int(self.weight_point),
            width=4,
        )

        pygame.draw.line(
            screen,
            green,
            to_int(self.end_long_arm),
            to_int(self.projectile_point),
            width=4,
        )


class main_module:
    def run(self, dev_mode: bool, trebuchet: Trebuchet):
        # event control
        run = True
        Next_module = Module_names.Exit_app

        global meters_to_pixel_ratio
        meters_to_pixel_ratio = 100

        while run:
            draw_scale()
            trebuchet.update()
            trebuchet.draw(dev_mode)

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
    def run(self, dev_mode, trebuchet):
        pygame.quit()
        return Module_names.Exit_app


# module control


class Module_names(Enum):
    Main_module = main_module()
    Exit_app = Exit_app_module()


# main

current_module = Module_names.Main_module
trebuchet = Trebuchet(4, 1, 4, 3, 1, 50, 500)
dev_mode = True


while current_module != Module_names.Exit_app:
    reset_screen()
    current_module = current_module.value.run(dev_mode, trebuchet)

pygame.quit()
