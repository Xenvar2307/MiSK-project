import pygame


class BasicButton:
    def __init__(self, surface, image, x, y, width, height):
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.surface = surface

    def draw(self):
        # return value, tells us if we should act
        action = False

        # mouse position
        pos = pygame.mouse.get_pos()

        # mouse on button
        if self.rect.collidepoint(pos):
            # check for release of button
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        # reset clicked status
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        self.surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


class ButtonFactory_Standard:
    def __init__(self) -> None:
        self.back_image = pygame.image.load("img/empty_grey_background.png")

    def factory(self, surface, text, font, x, y, width, height):
        # copy background
        background = self.back_image.copy()
        # resize to desired size
        background = pygame.transform.scale(background, (width, height))
        # draw around
        pygame.draw.rect(
            background,
            (65, 65, 65),
            (
                0,
                0,
                width,
                height,
            ),
            width=int(height / 16),
        )
        # create text image to size
        text_image = font.render(text, True, (255, 255, 255))

        # focus on height if text fits
        if text_image.get_width() * height / text_image.get_height() < width - 4 * int(
            height / 16
        ):
            text_image = pygame.transform.scale(
                text_image,
                (text_image.get_width() * height / text_image.get_height(), height),
            )
        else:
            text_image = pygame.transform.scale(
                text_image,
                (
                    width - 4 * int(height / 16),
                    text_image.get_height()
                    * (width - 4 * int(height / 16))
                    / text_image.get_width(),
                ),
            )

        # throw text on image
        background.blit(
            text_image,
            (
                width / 2 - text_image.get_width() / 2,
                height / 2 - text_image.get_height() / 2,
            ),
        )

        # correct
        background = background.convert_alpha()

        return BasicButton(surface, background, x, y, width, height)
