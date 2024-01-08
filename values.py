import pygame

# phisical constants
g = 9.81

# display
screen_width = 1600
screen_height = 900
screen_height_middle = screen_height / 2
screen_width_middle = screen_width / 2
side_padding = 100
ground_level = screen_height - side_padding

# label sizes
label_input_x = screen_width - 450
label_input_y = 150
label_width = 300
label_height = 40
label_y_padding = 10
label_y_skip = label_height + 2 * label_y_padding
label_x_end = label_input_x + label_width

input_field_width = 125
input_field_height = 40

min_weight_radius = 3
weight_density = 2200
# ((4/3)*PI * R**3) * d = Mass
# R**3 = 3*Mass / (4 * d * Pi)
min_trebuchet_thickness = 2
meters_trebuchet_thickness = 0.2

min_projectile_radius = 2
projectile_density = 2800  # stone 2200 - 2800

# allowed keys, do wpisywania danych
allowed_keys = {
    pygame.K_0,
    pygame.K_KP0,
    pygame.K_1,
    pygame.K_KP1,
    pygame.K_2,
    pygame.K_KP2,
    pygame.K_3,
    pygame.K_KP3,
    pygame.K_4,
    pygame.K_KP4,
    pygame.K_5,
    pygame.K_KP5,
    pygame.K_6,
    pygame.K_KP6,
    pygame.K_7,
    pygame.K_KP7,
    pygame.K_8,
    pygame.K_KP8,
    pygame.K_9,
    pygame.K_KP9,
}

period_keys = {
    pygame.K_PERIOD,
    pygame.K_KP_PERIOD,
}

# colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
brown = (205, 133, 63)
light_grey = (220, 220, 220)
grey = (169, 169, 169)
dark_grey = (112, 128, 144)
red = (255, 0, 0)

"""
sizes on laptop 
262
225
231
266
294
316
304
"""
