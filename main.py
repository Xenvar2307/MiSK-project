import pygame
import math
import numpy
from values import *
from enum import Enum
from buttons import *
from input_fields import *

pygame.init()

# setup display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("MiSK - project")

# fonts
scale_font = pygame.font.SysFont("Arial", 20)
time_info_font = pygame.font.SysFont("Arial", 27)
button_font = pygame.font.SysFont("Arial", 30)

label_font = pygame.font.SysFont("Arial", 33)
alert_font = pygame.font.SysFont("Arial", 20)
print(label_font.size("Counterweight(kg) ="))

# frames
fps = 60
clock = pygame.time.Clock()

ButtonFactory = ButtonFactory_Standard()

# global variables
# scale
meters_to_pixel_ratio = 40
# trebuchet control
release_angle = math.pi / 4  # 45 degrees
# trebuchet style MOVE TO CLASS

# simulation data
simulation_time = 0.0
simulation_running = False

simulation_speed = 1.0
simulation_speed_upper_limit = 5.0
simulation_speed_lower_limit = 0.5  # 0.1 exception

# display variables
alert_list = []


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


def draw_raw_text(surface, text, font, text_col, x, y, tempwidth, tempheight):
    text_image = font.render(text, True, text_col)
    # print(text_image.get_width())
    surface.blit(text_image, (x, y))


def print_alerts():
    for i, alert in enumerate(alert_list):
        for j, text in enumerate(alert):
            draw_raw_text(
                screen,
                text,
                alert_font,
                red,
                label_input_x,
                label_input_y + 7 * label_y_skip + i * 50 + j * 25,
                0,
                0,
            )


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
        # assigning input values
        self.long_arm_length = long_arm_length
        self.short_arm_length = short_arm_length
        self.sling_length = sling_length
        self.pivot_height = pivot_height
        self.weight_length = weight_length
        self.projectile_mass = projectile_mass
        self.weight_mass = weight_mass
        # setting starter variables
        self.holding_projectile = True
        self.release_time = 0.0

        # update part

        # initial state variables -> angles
        self.pivot_arm_angle = (
            math.asin(self.pivot_height / self.long_arm_length) + math.pi / 2
        )
        self.arm_sling_angle = math.asin(self.pivot_height / self.long_arm_length)
        self.arm_weight_angle = math.pi / 2 - math.asin(
            self.pivot_height / self.long_arm_length
        )
        self.pivot_arm_angle_change = 0
        self.arm_weight_angle_change = 0
        self.arm_sling_angle_change = 0

        # initial state variables -> points, change only on trebuchet move
        self.base_point = (screen_width_middle, ground_level)
        self.pivot_point = add_points(
            self.base_point, (0, -meters_to_pixel_ratio * self.pivot_height)
        )
        # initial state variables -> points, change constantly
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
        self.projectile_pos = self.end_sling

    def update_points_based_on_angles_and_basepoint(self):
        # ustawianie punktów do pozycji trebusza, zawsze bo skala sie moze zmienic
        global meters_to_pixel_ratio
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

    def update_projectile_position(self, time_passed):
        global meters_to_pixel_ratio
        if self.holding_projectile:
            self.projectile_pos = self.end_sling
        else:
            i = 1 / (fps * 10)
            temp = 0
            while temp < time_passed:
                temp += i
                self.projectile_pos = add_points(
                    self.projectile_pos,
                    (
                        meters_to_pixel_ratio * i * self.Beta,
                        -meters_to_pixel_ratio
                        * i
                        * (-g * (simulation_time - self.release_time) + self.Gamma),
                    ),
                )
            # update to change position when shooting

    def update_state_angles(self, time_passed):
        global meters_to_pixel_ratio
        i = 1 / (fps * 10)
        temp = 0
        while temp < time_passed:
            temp += i
            c11 = (
                -(self.short_arm_length**2) * self.weight_mass
                + 2
                * self.short_arm_length
                * self.weight_length
                * self.weight_mass
                * math.cos(self.arm_weight_angle)
                - (self.weight_length**2) * self.weight_mass
                - (self.long_arm_length**2) * self.projectile_mass
                + 2
                * self.long_arm_length
                * self.sling_length
                * self.projectile_mass
                * math.cos(self.arm_sling_angle)
                - (self.sling_length**2) * self.projectile_mass
            )

            c12 = (
                self.weight_length
                * self.weight_mass
                * (
                    self.short_arm_length * math.cos(self.arm_weight_angle)
                    - self.weight_length
                )
            )

            c13 = (
                -self.sling_length
                * self.projectile_mass
                * (
                    self.long_arm_length * math.cos(self.arm_sling_angle)
                    - self.arm_sling_angle
                )
            )
            c22 = -(self.weight_length**2) * self.weight_mass

            c33 = -(self.sling_length**2) * self.projectile_mass

            C = numpy.array([[c11, c12, c13], [c12, c22, 0], [c13, 0, c33]])
            C_inv = numpy.linalg.inv(C)

            w1 = (
                g
                * (
                    self.weight_mass
                    * (
                        self.short_arm_length * math.sin(self.pivot_arm_angle)
                        - self.weight_length
                        * math.sin(self.arm_weight_angle + self.pivot_arm_angle)
                    )
                    - self.projectile_mass
                    * (
                        self.long_arm_length * math.sin(self.pivot_arm_angle)
                        + self.sling_length
                        * math.sin(self.arm_sling_angle - self.pivot_arm_angle)
                    )
                )
                + self.short_arm_length
                * self.weight_length
                * self.weight_mass
                * (self.arm_weight_angle_change + 2 * self.pivot_arm_angle_change)
                * math.sin(self.arm_weight_angle)
                * self.arm_weight_angle_change
                + self.long_arm_length
                * self.sling_length
                * self.projectile_mass
                * (-self.arm_sling_angle_change + 2 * self.pivot_arm_angle_change)
                * math.sin(self.arm_sling_angle)
                * self.arm_sling_angle_change
            )
            w2 = (
                self.weight_length
                * self.weight_mass
                * (
                    g * math.sin(self.arm_weight_angle - self.pivot_arm_angle)
                    - self.short_arm_length
                    * math.sin(self.arm_sling_angle)
                    * (self.pivot_arm_angle_change**2)
                )
            )
            w3 = (
                self.sling_length
                * self.projectile_mass
                * (
                    g * math.sin(self.arm_sling_angle - self.pivot_arm_angle)
                    - self.long_arm_length
                    * math.sin(self.arm_sling_angle)
                    * (self.pivot_arm_angle_change**2)
                )
            )

            W = numpy.array([[w1], [w2], [w3]])

            result = numpy.dot(C_inv, W)

            self.pivot_arm_angle_change += result[0][0] * i
            self.arm_weight_angle_change += result[1][0] * i
            self.arm_sling_angle_change += result[2][0] * i

            self.pivot_arm_angle += self.pivot_arm_angle_change * i
            self.arm_weight_angle += self.arm_weight_angle_change * i
            self.arm_sling_angle += self.arm_sling_angle_change * i

    def calculate_shot_info(self):
        global meters_to_pixel_ratio
        self.release_time = simulation_time
        self.Beta = -self.long_arm_length * math.cos(
            self.pivot_arm_angle
        ) * self.pivot_arm_angle_change - self.sling_length * math.cos(
            self.arm_sling_angle - self.pivot_arm_angle
        ) * (
            self.arm_sling_angle_change - self.pivot_arm_angle_change
        )

        self.Gamma = -self.long_arm_length * math.sin(
            self.pivot_arm_angle
        ) * self.pivot_arm_angle_change + self.sling_length * math.sin(
            self.arm_sling_angle - self.pivot_arm_angle
        ) * (
            self.arm_sling_angle_change - self.pivot_arm_angle_change
        )
        self.Delta = -self.long_arm_length * math.sin(
            self.pivot_arm_angle
        ) - self.sling_length * math.sin(self.arm_sling_angle - self.pivot_arm_angle)
        self.Epsylon = (
            self.long_arm_length * math.cos(self.pivot_arm_angle)
            + self.pivot_height
            - self.sling_length * math.cos(self.arm_sling_angle - self.pivot_arm_angle)
        )
        self.hit_ground_time = (
            self.Gamma + math.sqrt(self.Gamma**2 + 2 * g * self.Epsylon)
        ) / g + self.release_time

        self.range = self.Beta * (self.hit_ground_time - self.release_time)
        self.peak_time = self.Gamma / g + self.release_time
        self.peak = (
            -g / 2 * (self.peak_time - self.release_time) ** 2
            + self.Gamma * (self.peak_time - self.release_time)
            + self.Epsylon
        )
        self.impact = (self.projectile_mass / 2) * (
            self.Beta**2 + (-g * self.hit_ground_time * self.Gamma) ** 2
        )

    def go_to_projectile_phase(self):
        global meters_to_pixel_ratio
        self.calculate_shot_info()
        self.move_base_point((side_padding, screen_height - side_padding))
        update_ratio(False)
        self.update_points_based_on_angles_and_basepoint()
        self.update_projectile_position(0)

        self.holding_projectile = False

    def update(self, time_passed):
        # release control
        global meters_to_pixel_ratio
        if self.pivot_arm_angle < release_angle and self.holding_projectile:
            self.go_to_projectile_phase()

        # jezeli przed strzalem, rusz trebusz
        if self.holding_projectile:
            self.update_state_angles(time_passed)

        self.update_points_based_on_angles_and_basepoint()
        self.update_projectile_position(time_passed)

    def calculate_weight_R(self):
        return max(
            min_weight_radius,
            meters_to_pixel_ratio
            * round(
                (3 * self.weight_mass / (4 * weight_density * math.pi)) ** (1.0 / 3.0)
            ),
        )

    def calculate_projectile_R(self):
        return max(
            min_projectile_radius,
            meters_to_pixel_ratio
            * round(
                (3 * self.projectile_mass / (4 * projectile_density * math.pi))
                ** (1.0 / 3.0)
            ),
        )

    def calculate_trebuchet_thickness(self):
        return max(
            min_trebuchet_thickness,
            round(meters_to_pixel_ratio * meters_trebuchet_thickness),
        )

    def draw(self, subtitles):
        # drawing lines between points
        pygame.draw.line(
            screen,
            brown,
            to_int(self.base_point),
            to_int(self.pivot_point),
            width=int(self.calculate_trebuchet_thickness()),
        )

        pygame.draw.line(
            screen,
            brown,
            to_int(self.end_short_arm),
            to_int(self.end_long_arm),
            width=int(self.calculate_trebuchet_thickness()),
        )

        pygame.draw.line(
            screen,
            brown,
            to_int(self.end_short_arm),
            to_int(self.weight_point),
            width=int(self.calculate_trebuchet_thickness()),
        )

        pygame.draw.line(
            screen,
            brown,
            to_int(self.end_long_arm),
            to_int(self.end_sling),
            width=int(self.calculate_trebuchet_thickness()),
        )

        # projectile
        pygame.draw.circle(
            screen, grey, self.projectile_pos, self.calculate_projectile_R()
        )
        pygame.draw.circle(
            screen,
            light_grey,
            self.projectile_pos,
            self.calculate_projectile_R(),
            width=1,
        )

        # weight
        pygame.draw.circle(
            screen, dark_grey, self.weight_point, self.calculate_weight_R()
        )

    def move_base_point(self, tuple):
        self.base_point = tuple

    def reset(self):
        # update part
        self.arm_sling_angle_change = 0
        self.pivot_arm_angle_change = 0
        self.arm_weight_angle_change = 0

        self.holding_projectile = True

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
        self.update_points_based_on_angles_and_basepoint()

        # only before launch
        self.projectile_pos = self.end_sling


def reset_simulation(trebuchet: Trebuchet):
    global simulation_time
    global simulation_running
    simulation_running = False
    simulation_time = 0.0
    trebuchet.reset()


def update_ratio(stage_1):
    global meters_to_pixel_ratio
    if stage_1:
        meters_to_pixel_ratio = (screen_height - 2 * side_padding) / (
            trebuchet.pivot_height + trebuchet.long_arm_length + trebuchet.sling_length
        )
    else:
        meters_to_pixel_ratio = min(
            ((screen_height - 2 * side_padding) / trebuchet.peak),
            ((screen_width - 2 * side_padding) / trebuchet.range),
        )


class main_module:
    def run(self, dev_mode: bool, trebuchet: Trebuchet):
        # event control
        run = True
        global meters_to_pixel_ratio
        global simulation_time
        global simulation_speed
        global simulation_running
        simulation_running = False
        Next_module = Module_names.Exit_app

        # create menu buttons
        Run_button = ButtonFactory.factory(
            screen, "", button_font, screen_width - 200, 0, 200, 50
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
        Input_Fields = []

        # create input fields
        Pivot_height_field = BasicInputField(
            screen,
            label_font,
            label_input_x + label_width,
            label_input_y,
            input_field_width,
            input_field_height,
        )
        Pivot_height_field.text = str(trebuchet.pivot_height)
        Input_Fields.append(Pivot_height_field)

        Long_arm_field = BasicInputField(
            screen,
            label_font,
            label_input_x + label_width,
            label_input_y + label_y_skip,
            input_field_width,
            input_field_height,
        )
        Long_arm_field.text = str(trebuchet.long_arm_length)
        Input_Fields.append(Long_arm_field)

        Short_arm_field = BasicInputField(
            screen,
            label_font,
            label_input_x + label_width,
            label_input_y + 2 * label_y_skip,
            input_field_width,
            input_field_height,
        )
        Short_arm_field.text = str(trebuchet.short_arm_length)
        Input_Fields.append(Short_arm_field)

        Sling_length_field = BasicInputField(
            screen,
            label_font,
            label_input_x + label_width,
            label_input_y + 3 * label_y_skip,
            input_field_width,
            input_field_height,
        )
        Sling_length_field.text = str(trebuchet.sling_length)
        Input_Fields.append(Sling_length_field)

        Weight_length_field = BasicInputField(
            screen,
            label_font,
            label_input_x + label_width,
            label_input_y + 4 * label_y_skip,
            input_field_width,
            input_field_height,
        )
        Weight_length_field.text = str(trebuchet.weight_length)
        Input_Fields.append(Weight_length_field)

        Projectile_mass_field = BasicInputField(
            screen,
            label_font,
            label_input_x + label_width,
            label_input_y + 5 * label_y_skip,
            input_field_width,
            input_field_height,
        )
        Projectile_mass_field.text = str(trebuchet.projectile_mass)
        Input_Fields.append(Projectile_mass_field)

        Weight_mass_field = BasicInputField(
            screen,
            label_font,
            label_input_x + label_width,
            label_input_y + 6 * label_y_skip,
            input_field_width,
            input_field_height,
        )
        Weight_mass_field.text = str(trebuchet.weight_mass)
        Input_Fields.append(Weight_mass_field)

        # global changeable
        active_input_field = None

        while run:
            # fps control
            clock.tick(fps)
            # check if we need to update state of trebuchet
            if simulation_running:
                trebuchet.update(simulation_speed * 1 / fps)
                simulation_time += simulation_speed * 1 / fps

            # draw the trebuchet itself with current scale
            valid = True
            global alert_list
            alert_list = []
            # check for conflicts
            if not simulation_running:
                # check if they are empty
                # clear invalid checks
                for inputfield in Input_Fields:
                    inputfield.invalid = False

                for inputfield in Input_Fields:
                    if inputfield.text == "" or float(inputfield.text) == 0.0:
                        inputfield.invalid = True
                        valid = False
                # check values
                if valid:
                    if not (
                        float(Short_arm_field.text) + float(Weight_length_field.text)
                        < float(Pivot_height_field.text)
                    ):
                        alert_list.append(
                            [
                                "Conflict: Short Arm + Weight Lenght needs to be shorter",
                                "than Pivot Height",
                            ]
                        )
                        Short_arm_field.invalid = True
                        Weight_length_field.invalid = True
                        Pivot_height_field.invalid = True
                        valid = False
                    if not (
                        float(Long_arm_field.text) > float(Pivot_height_field.text)
                    ):
                        alert_list.append(
                            [
                                "Conflict: Longer Arm needs to be longer than Pivot Height"
                            ]
                        )
                        Long_arm_field.invalid = True
                        Pivot_height_field.invalid = True
                        valid = False
                else:
                    alert_list.append(["Error: Please, fill all the values"])

            # check for new input values for dimentions of trebuchet
            if not simulation_running and valid and simulation_time == 0.0:
                trebuchet.pivot_height = float(Pivot_height_field.text)
                trebuchet.long_arm_length = float(Long_arm_field.text)
                trebuchet.short_arm_length = float(Short_arm_field.text)
                trebuchet.sling_length = float(Sling_length_field.text)
                trebuchet.weight_length = float(Weight_length_field.text)
                trebuchet.projectile_mass = float(Projectile_mass_field.text)
                trebuchet.weight_mass = float(Weight_mass_field.text)

            if not simulation_running and simulation_time == 0.0:
                trebuchet.reset()

            # buttons for running and speed control
            if simulation_running:
                Run_button_text = button_font.render("Stop Simulation", True, white)
            else:
                Run_button_text = button_font.render("Run Simulation", True, white)

            update_ratio(trebuchet.holding_projectile)
            # drawing
            # stable or changed images
            reset_screen()
            print_alerts()
            draw_scale()

            trebuchet.draw(dev_mode)

            # Run button
            if Run_button.draw() and valid:
                simulation_running = not simulation_running
            temp_rect = Run_button_text.get_rect()
            temp_rect.center = Run_button.rect.center

            screen.blit(Run_button_text, temp_rect)

            # Reset Button
            if simulation_time > 0.0:
                if Reset_button.draw():
                    reset_simulation(trebuchet)

            # Time Buttons
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
                draw_raw_text(
                    screen,
                    "Pivot Height (m) =",
                    label_font,
                    white,
                    label_input_x,
                    label_input_y,
                    label_width,
                    label_height,
                )
                if Pivot_height_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Pivot_height_field
                    Pivot_height_field.active = True
                draw_raw_text(
                    screen,
                    "Long Arm (m) =",
                    label_font,
                    white,
                    label_input_x,
                    label_input_y + 1 * label_y_skip,
                    label_width,
                    label_height,
                )
                if Long_arm_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Long_arm_field
                    Long_arm_field.active = True

                draw_raw_text(
                    screen,
                    "Short Arm (m) =",
                    label_font,
                    white,
                    label_input_x,
                    label_input_y + 2 * label_y_skip,
                    label_width,
                    label_height,
                )
                if Short_arm_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Short_arm_field
                    Short_arm_field.active = True

                draw_raw_text(
                    screen,
                    "Sling Length (m) =",
                    label_font,
                    white,
                    label_input_x,
                    label_input_y + 3 * label_y_skip,
                    label_width,
                    label_height,
                )
                if Sling_length_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Sling_length_field
                    Sling_length_field.active = True

                draw_raw_text(
                    screen,
                    "Weight Lenght (m) =",
                    label_font,
                    white,
                    label_input_x,
                    label_input_y + 4 * label_y_skip,
                    label_width,
                    label_height,
                )
                if Weight_length_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Weight_length_field
                    Weight_length_field.active = True

                draw_raw_text(
                    screen,
                    "Projectile Mass (kg) =",
                    label_font,
                    white,
                    label_input_x,
                    label_input_y + 5 * label_y_skip,
                    label_width,
                    label_height,
                )
                if Projectile_mass_field.draw():
                    if active_input_field != None:
                        active_input_field.active = False
                    active_input_field = Projectile_mass_field
                    Projectile_mass_field.active = True

                draw_raw_text(
                    screen,
                    "Counterweight (kg) =",
                    label_font,
                    white,
                    label_input_x,
                    label_input_y + 6 * label_y_skip,
                    label_width,
                    label_height,
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

            # running info
            temp_cute_time = round(simulation_time, 2)
            Run_info_image = time_info_font.render(
                f"Speed: {simulation_speed}  Time(s): {temp_cute_time}", True, white
            )

            Run_info_image.convert_alpha()
            screen.blit(Run_info_image, (screen_width - 375 - 250, 10))

            # Event control
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

                if event.type == pygame.KEYDOWN:
                    # deactivate field on "enter"
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if active_input_field != None:
                            active_input_field.active = False
                            active_input_field = None
                    # input values to active field
                    if event.key in allowed_keys:
                        if active_input_field != None:
                            active_input_field.text += event.unicode
                    elif event.key in period_keys and event.unicode == ".":
                        if active_input_field != None:
                            if (
                                "." not in active_input_field.text
                                and active_input_field.text != ""
                            ):
                                active_input_field.text += event.unicode
                    # delete values from field
                    if event.key == pygame.K_BACKSPACE:
                        if active_input_field != None:
                            active_input_field.text = active_input_field.text[:-1]

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
trebuchet = Trebuchet(5.7, 1.2, 5, 3.2, 1.4, 15, 2000)
dev_mode = True


while current_module != Module_names.Exit_app:
    reset_screen()
    current_module = current_module.value.run(dev_mode, trebuchet)

pygame.quit()
