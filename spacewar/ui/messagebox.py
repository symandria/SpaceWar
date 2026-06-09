import pygame

from spacewar.ui.text_rendering import wordwrap_render


class Messagebox:
    def __init__(self, text, font, display_width, foreground, background):
        self.font = font
        self.text = wordwrap_render(text, self.font, display_width - 4, foreground, background)
        self.image = pygame.Surface((self.text.get_width() + 4, self.text.get_height() + 4))
        self.image.fill(background)
        pygame.draw.rect(self.image, foreground,
                         (0, 0, self.image.get_width(), self.image.get_height()), 1)

    def render(self, screen):
        rect = self.image.get_rect()
        rect.centery = screen.get_height() // 2
        rect.centerx = screen.get_width() // 2
        screen.blit(self.image, rect)
        screen.blit(self.text, (rect.left + 2, rect.top + 2))
