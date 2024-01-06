import pygame
import math
from enum import Enum
from buttons import *
from input_fields import *

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
# input fields

lable_input_x = screen_width - 450
lable_input_y = 150
lable_width = 300
lable_height = 40
lable_y_padding = 10
lable_y_skip = lable_height + 2 * lable_y_padding
lable_x_end = lable_input_x + lable_width

input_field_width = 125
input_field_height = 40


# font
scale_font = pygame.font.SysFont("Arial", 20)
time_info_font = pygame.font.SysFont("Arial", 25)
button_font = pygame.font.SysFont("Arial", 200)

# frames
fps = 60
clock = pygame.time.Clock()
# colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
brown = (205, 133, 63)
light_grey = (220, 220, 220)
grey = (169, 169, 169)
dark_grey = (112, 128, 144)

ButtonFactory = ButtonFactory_Standard()

meters_to_pixel_ratio = 40
g = 9.81
release_angle = math.pi / 4  # 45 degrees
trebuchet_thickness = 5

simulation_time = 0.0
simulation_running = False

simulation_speed = 1.0
simulation_speed_upper_limit = 5.0
simulation_speed_lower_limit = 0.5  # 0.1 exception


def draw_text(surface, text, font, text_col, x, y, width, height):
    text_image = font.render(text, True, text_col)

    # focus on height if text fits
    if text_image.get_width() * height / text_image.get_height() < width:
        text_image = pygame.transform.scale(
            text_image,
            (text_image.get_width() * height / text_image.get_height(), height),
        )
    else:
        text_image = pygame.transform.scale(
            text_image,
            (
                width,
                text_image.get_height() * width / text_image.get_width(),
            ),
        )

    surface.blit(text_image, (x, y))


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

        # state variables, angles
        self.pivot_arm_angle = (
            math.asin(self.pivot_height / self.long_arm_length) + math.pi / 2
        )
        self.arm_sling_angle = math.asin(self.pivot_height / self.long_arm_length)
        self.arm_weight_angle = math.pi / 2 - math.asin(
            self.pivot_height / self.long_arm_length
        )

        # base points, manually changed only
        self.base_point = (screen_width_middle, ground_level)
        self.pivot_point = add_points(
            self.base_point, (0, -meters_to_pixel_ratio * self.pivot_height)
        )
        # state points, changed depending on state
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

        self.end_sling = add_points(
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

        # only before launch
        self.projectile_pos = self.end_sling

    def update(self, time_passed):
        # TO DO aktualizacja kątów
        self.pivot_arm_angle += 0.5 * time_passed
        #
        #
        # ustawianie punktów do pozycji trebusza
        self.pivot_point = add_points(
            self.base_point, (0, -meters_to_pixel_ratio * self.pivot_height)
        )
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

        self.end_sling = add_points(
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

        # TO DO change to track after release
        self.projectile_pos = self.end_sling

    def draw(self, subtitles):
        pygame.draw.line(
            screen,
            brown,
            to_int(self.base_point),
            to_int(self.pivot_point),
            width=int(trebuchet_thickness),
        )

        pygame.draw.line(
            screen,
            brown,
            to_int(self.end_short_arm),
            to_int(self.end_long_arm),
            width=int(trebuchet_thickness),
        )

        pygame.draw.line(
            screen,
            brown,
            to_int(self.end_short_arm),
            to_int(self.weight_point),
            width=int(trebuchet_thickness),
        )

        pygame.draw.line(
            screen,
            brown,
            to_int(self.end_long_arm),
            to_int(self.end_sling),
            width=int(trebuchet_thickness),
        )

        # projectile
        pygame.draw.circle(
            screen, grey, self.projectile_pos, int(0.2 * meters_to_pixel_ratio)
        )
        pygame.draw.circle(
            screen,
            light_grey,
            self.projectile_pos,
            int(0.2 * meters_to_pixel_ratio),
            width=2,
        )

        # weight
        pygame.draw.circle(
            screen, dark_grey, self.weight_point, int(0.5 * meters_to_pixel_ratio)
        )

    def change_base_point(self, tuple):
        self.base_point = tuple

    def reset(self):
        # update part

        # state variables, angles
        self.pivot_arm_angle = (
            math.asin(self.pivot_height / self.long_arm_length) + math.pi / 2
        )
        self.arm_sling_angle = math.asin(self.pivot_height / self.long_arm_length)
        self.arm_weight_angle = math.pi / 2 - math.asin(
            self.pivot_height / self.long_arm_length
        )

        # base points, manually changed only
        self.base_point = (screen_width_middle, ground_level)
        self.pivot_point = add_points(
            self.base_point, (0, -meters_to_pixel_ratio * self.pivot_height)
        )
        # state points, changed depending on state
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

        self.end_sling = add_points(
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

        # only before launch
        self.projectile_pos = self.end_sling


def reset_simulation(trebuchet: Trebuchet):
    global simulation_time
    global simulation_running
    simulation_running = False
    simulation_time = 0.0
    trebuchet.reset()


class main_module:
    def run(self, dev_mode: bool, trebuchet: Trebuchet):
        # event control
        run = True
        global simulation_running
        simulation_running = False
        Next_module = Module_names.Exit_app

        global meters_to_pixel_ratio
        meters_to_pixel_ratio = 40

        # create menu buttons
        Run_button = ButtonFactory.factory(
            screen, "Run/Stop Simulation", button_font, screen_width - 200, 0, 200, 50
        )

        Reset_button = ButtonFactory.factory(
            screen, "Reset Simulation", button_font, screen_width - 200, 50, 200, 50
        )

        DownX_button = ButtonFactory.factory(
            screen, "-0.5X", button_font, screen_width - 350, 0, 75, 50
        )
        UpX_button = ButtonFactory.factory(
            screen, "+0.5X", button_font, screen_width - 275, 0, 75, 50
        )

        # create input fields
        Pivot_height_field = BasicInputField(
            screen,
            button_font,
            lable_input_x + lable_width,
            lable_input_y,
            input_field_width,
            input_field_height,
        )
        Pivot_height_field.text = str(trebuchet.pivot_height)

        Long_arm_field = BasicInputField(
            screen,
            button_font,
            lable_input_x + lable_width,
            lable_input_y + lable_y_skip,
            input_field_width,
            input_field_height,
        )
        Long_arm_field.text = str(trebuchet.long_arm_length)

        Short_arm_field = BasicInputField(
            screen,
            button_font,
            lable_input_x + lable_width,
            lable_input_y + 2 * lable_y_skip,
            input_field_width,
            input_field_height,
        )
        Short_arm_field.text = str(trebuchet.short_arm_length)

        Sling_length_field = BasicInputField(
            screen,
            button_font,
            lable_input_x + lable_width,
            lable_input_y + 3 * lable_y_skip,
            input_field_width,
            input_field_height,
        )
        Sling_length_field.text = str(trebuchet.sling_length)

        Weight_length_field = BasicInputField(
            screen,
            button_font,
            lable_input_x + lable_width,
            lable_input_y + 4 * lable_y_skip,
            input_field_width,
            input_field_height,
        )
        Weight_length_field.text = str(trebuchet.weight_length)

        Projectile_mass_field = BasicInputField(
            screen,
            button_font,
            lable_input_x + lable_width,
            lable_input_y + 5 * lable_y_skip,
            input_field_width,
            input_field_height,
        )
        Projectile_mass_field.text = str(trebuchet.projectile_mass)

        Weight_mass_field = BasicInputField(
            screen,
            button_font,
            lable_input_x + lable_width,
            lable_input_y + 6 * lable_y_skip,
            input_field_width,
            input_field_height,
        )
        Weight_mass_field.text = str(trebuchet.weight_mass)

        # global changeable
        active_input_field = None

        global simulation_time
        # simulation_time = 0.0
        global simulation_speed
        # simulation_speed = 1.0

        while run:
            # fps control
            clock.tick(fps)
            # check if we need to update state of trebuchet
            if simulation_running:
                trebuchet.update(simulation_speed * 1 / fps)
                simulation_time += simulation_speed * 1 / fps
            # check for new input values for dimentions of trebuchet
            # TO DO buttons and changing
            #
            # set scale so that it is visible

            meters_to_pixel_ratio = int(
                (screen_height - 2 * side_padding)
                / (
                    trebuchet.pivot_height
                    + trebuchet.long_arm_length
                    + trebuchet.sling_length
                )
            )

            # stable or changed images
            reset_screen()
            draw_scale()

            # draw the trebuchet itself with current scale
            trebuchet.update(0)
            trebuchet.draw(dev_mode)

            # buttons for running and speed control

            if Run_button.draw():
                simulation_running = (
                    not simulation_running
                )  # change state to negation of current state

            if simulation_time > 0.0:
                if Reset_button.draw():
                    reset_simulation(trebuchet)

            if UpX_button.draw():
                if simulation_speed == 0.1:
                    simulation_speed = 0.5
                elif simulation_speed < simulation_speed_upper_limit:
                    simulation_speed += 0.5
            if DownX_button.draw():
                if simulation_speed == 0.5:
                    simulation_speed = 0.1
                elif simulation_speed > simulation_speed_lower_limit:
                    simulation_speed -= 0.5

            # input fields
            if simulation_time == 0.0:
                draw_text(
                    screen,
                    "Pivot Height (m) = ",
                    button_font,
                    white,
                    lable_input_x,
                    lable_input_y,
                    lable_width,
                    lable_height,
                )
                if Pivot_height_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Pivot_height_field
                    Pivot_height_field.active = True
                draw_text(
                    screen,
                    "Long Arm (m) = ",
                    button_font,
                    white,
                    lable_input_x,
                    lable_input_y + 1 * lable_y_skip,
                    lable_width,
                    lable_height,
                )
                if Long_arm_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Long_arm_field
                    Long_arm_field.active = True

                draw_text(
                    screen,
                    "Short Arm (m) = ",
                    button_font,
                    white,
                    lable_input_x,
                    lable_input_y + 2 * lable_y_skip,
                    lable_width,
                    lable_height,
                )
                if Short_arm_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Short_arm_field
                    Short_arm_field.active = True

                draw_text(
                    screen,
                    "Sling Length (m) = ",
                    button_font,
                    white,
                    lable_input_x,
                    lable_input_y + 3 * lable_y_skip,
                    lable_width,
                    lable_height,
                )
                if Sling_length_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Sling_length_field
                    Sling_length_field.active = True

                draw_text(
                    screen,
                    "Weight Lenght (m) = ",
                    button_font,
                    white,
                    lable_input_x,
                    lable_input_y + 4 * lable_y_skip,
                    lable_width,
                    lable_height,
                )
                if Weight_length_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Weight_length_field
                    Weight_length_field.active = True

                draw_text(
                    screen,
                    "Projectile Mass (kg) = ",
                    button_font,
                    white,
                    lable_input_x,
                    lable_input_y + 5 * lable_y_skip,
                    lable_width,
                    lable_height,
                )
                if Projectile_mass_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Projectile_mass_field
                    Projectile_mass_field.active = True

                draw_text(
                    screen,
                    "Counterweight (kg) = ",
                    button_font,
                    white,
                    lable_input_x,
                    lable_input_y + 6 * lable_y_skip,
                    lable_width,
                    lable_height,
                )
                if Weight_mass_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Weight_mass_field
                    Weight_mass_field.active = True

                # mark down active field
                if active_input_field != None:
                    pygame.draw.rect(
                        screen, (247, 0, 255), active_input_field.rect, width=4
                    )

            # check for invalid values TO DO

            # running info
            temp_cute_time = round(simulation_time, 2)
            Run_info_image = time_info_font.render(
                f"Speed: {simulation_speed}  Time: {temp_cute_time}", True, white
            )

            Run_info_image.convert_alpha()
            screen.blit(Run_info_image, (10, 10))

            # event control
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    Next_module = Module_names.Exit_app
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked = True
                    # deactivate input field
                    if active_input_field != None:
                        active_input_field.active = False
                        active_input_field = None
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
trebuchet = Trebuchet(12, 3, 12, 9, 3, 50, 500)
dev_mode = True


while current_module != Module_names.Exit_app:
    reset_screen()
    current_module = current_module.value.run(dev_mode, trebuchet)

pygame.quit()
