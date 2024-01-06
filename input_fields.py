import pygame


class BasicInputField:
    def __init__(self, surface, font, x, y, width, height) -> None:
        self.surface = surface
        self.clicked = False
        self.font = font
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect((x, y), (width, height))
        self.text = ""
        self.invalid = False

    def draw(self):
        # draw background
        pygame.draw.rect(self.surface, (255, 255, 255), self.rect)
        # draw if active or invalid
        if self.invalid:
            pygame.draw.rect(self.surface, (255, 0, 0), self.rect, width=4)
        else:
            pygame.draw.rect(self.surface, (153, 153, 0), self.rect, width=3)
        # draw text on TO DO
        text_image = self.font.render(self.text, True, (0, 0, 0))
        if (
            text_image.get_width() * self.height / text_image.get_height()
            < self.width - 4 * int(self.height / 16)
        ):
            text_image = pygame.transform.scale(
                text_image,
                (
                    text_image.get_width() * self.height / text_image.get_height(),
                    self.height,
                ),
            )
        else:
            text_image = pygame.transform.scale(
                text_image,
                (
                    self.width - 4 * int(self.height / 16),
                    text_image.get_height()
                    * (self.width - 4 * int(self.height / 16))
                    / text_image.get_width(),
                ),
            )

        self.surface.blit(
            text_image, (self.x + self.width - text_image.get_width() - 10, self.y)
        )

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

        return action
