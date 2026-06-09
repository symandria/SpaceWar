import pygame


class Infobox:
    def __init__(self, target, font, foreground, background, text_manager):
        self.target = target
        self.font = font
        self.foreground = foreground
        self.background = background
        self.text_manager = text_manager
        self.surfaces = []
        self.image = None
        self.rect = None
        self._build()

    def _build(self):
        t = self.target
        fg = self.foreground
        if t.type == "sentry":
            self.surfaces = [
                self.font.render(t.name, True, fg),
                self.font.render(
                    self.text_manager.load("shield-prefix") + repr(t.shields), True, fg),
            ]
        else:
            self.surfaces = [
                self.font.render(self.text_manager.load("rank-" + t.rank), True, fg),
                self.font.render(t.captain, True, fg),
                self.font.render(t.name, True, fg),
                self.font.render(
                    self.text_manager.load("shield-prefix") + repr(t.shields), True, fg),
                self.font.render(
                    self.text_manager.load("speed-prefix") + repr(t.speed), True, fg),
            ]
        width = 0
        height = 0
        for surface in self.surfaces:
            if surface.get_width() > width:
                width = surface.get_width()
            height += surface.get_height()
        width += 4
        height += 4
        self.image = pygame.Surface((width, height))
        self.image.fill(self.background)
        pygame.draw.rect(self.image, self.foreground, self.image.get_rect(), 1)
        self.rect = pygame.Rect(int(t.pos[0]) + 10, int(t.pos[1]), width, height)

    def update(self):
        self._build()

    def render(self, screen):
        screen.blit(self.image, self.rect)
        height = 2
        for surface in self.surfaces:
            screen.blit(surface, (self.rect.left + 2, self.rect.top + height))
            height += surface.get_height()
