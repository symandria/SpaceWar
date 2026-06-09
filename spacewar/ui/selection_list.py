import pygame

from spacewar.ui.text_rendering import render_button, wordwrap_render


class SelectionButton:
    def __init__(self, text, callback, font, foreground, background):
        self.image, self.rect = render_button(text, font, foreground, background)
        self.callback = callback

    def render(self, screen):
        screen.blit(self.image, self.rect)


class SelectionList:
    def __init__(self, title, font, foreground, background, display_width, *buttons):
        self.foreground = foreground
        self.background = background
        self.font = font
        self.title = wordwrap_render(title, font, display_width - 4, foreground, background)
        self.title_rect = self.title.get_rect()
        self.buttons = [
            SelectionButton(text, callback, font, foreground, background)
            for text, callback in buttons
        ]
        height = self.title_rect.height
        width = self.title_rect.width
        for button in self:
            height += button.rect.height + 2
            if button.rect.width > width:
                width = button.rect.width
        self.frame = pygame.Surface((width + 4, height + 4))
        self.frame.fill(background)
        self.rect = self.frame.get_rect()
        pygame.draw.rect(self.frame, foreground, self.rect, 1)

    def __iter__(self):
        return iter(self.buttons)

    def render(self, screen):
        self.rect.center = screen.get_width() // 2, screen.get_height() // 2
        self.title_rect.top = self.rect.top + 2
        self.title_rect.centerx = self.rect.centerx
        screen.blit(self.frame, self.rect)
        screen.blit(self.title, self.title_rect)
        y = self.title_rect.bottom + 2
        for button in self:
            button.rect.top = y
            button.rect.centerx = self.rect.centerx
            button.render(screen)
            y += button.rect.height + 2
