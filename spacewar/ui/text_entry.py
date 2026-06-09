import pygame


class TextEntry:
    def __init__(self, prompt, start, callback, font, foreground, background):
        self.font = font
        self.foreground = foreground
        self.background = background
        self.prompt = font.render(prompt, True, foreground)
        self.text = start
        self.start = start
        self.callback = callback
        self.image = None
        self.frame = None
        self.rect = None

    def update(self, display_width, display_height):
        self.image = self.font.render(self.text + "_", True, self.foreground)
        self.frame = pygame.Surface((
            max(self.prompt.get_width(), self.image.get_width()) + 4,
            self.prompt.get_height() + self.image.get_height() + 8,
        ))
        self.rect = self.frame.get_rect()
        self.frame.fill(self.background)
        pygame.draw.rect(self.frame, self.foreground, self.rect, 1)
        self.rect.center = display_width // 2, display_height // 2

    def render(self, display):
        display.blit(self.frame, self.rect)
        rect = self.prompt.get_rect()
        rect.top = self.rect.top + 2
        rect.centerx = self.rect.centerx
        display.blit(self.prompt, rect)
        rect = self.image.get_rect()
        rect.bottom = self.rect.bottom - 2
        rect.centerx = self.rect.centerx
        display.blit(self.image, rect)
