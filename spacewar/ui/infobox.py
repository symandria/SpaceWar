import pygame


class Infobox:
    def __init__(self, target, font, foreground, background, text_manager,
                 is_ally=False):
        self.target = target
        self.font = font
        self.foreground = foreground
        self.background = background
        self.text_manager = text_manager
        self.is_ally = is_ally
        self.surfaces = []
        self.image = None
        self.rect = None
        self._build()

    def _build(self):
        t = self.target
        fg = self.foreground
        dim = (160, 160, 160) if fg == (255, 255, 255) else (80, 80, 80)

        if t.type == "sentry":
            self.surfaces = [
                self.font.render(t.name, True, fg),
                self.font.render(f"Hull: {t.hull}/{t.max_hull}", True, fg),
                self.font.render(f"Shields: {t.shields}/{t.max_shields}", True, fg),
            ]
        elif self.is_ally:
            self.surfaces = [
                self.font.render(
                    self.text_manager.load("rank-" + t.rank) if t.rank else "", True, fg),
                self.font.render(t.captain, True, fg),
                self.font.render(t.name, True, fg),
                self.font.render(f"Hull: {t.hull}/{t.max_hull}", True, fg),
                self.font.render(f"Shields: {t.shields}/{t.max_shields}", True, fg),
                self.font.render(f"Speed: {t.speed}", True, dim),
            ]
            w1 = t.loadout.get_weapon(1)
            w2 = t.loadout.get_weapon(2)
            if w1:
                wn = w1.get("weapon_type", "?").replace("_", " ").title()
                self.surfaces.append(self.font.render(f"W1: {wn}", True, dim))
            if w2:
                wn = w2.get("weapon_type", "?").replace("_", " ").title()
                self.surfaces.append(self.font.render(f"W2: {wn}", True, dim))
            if t.passive_stealth > 0:
                self.surfaces.append(self.font.render(
                    f"Stealth: {t.passive_stealth}", True, dim))
            if t.active_cloak:
                state = "ON" if t.cloaked else "ready"
                self.surfaces.append(self.font.render(
                    f"Cloak: {state}", True, dim))
        else:
            shield_pct = int(t.shields / t.max_shields * 100) if t.max_shields > 0 else 0
            hull_indicator = "OK" if t.hull > t.max_hull * 0.5 else (
                "LOW" if t.hull > t.max_hull * 0.25 else "CRIT")
            self.surfaces = [
                self.font.render(
                    self.text_manager.load("rank-" + t.rank) if t.rank else "", True, fg),
                self.font.render(t.captain, True, fg),
                self.font.render(t.name, True, fg),
                self.font.render(f"Shields: {shield_pct}%", True, fg),
                self.font.render(f"Hull: {hull_indicator}", True, fg),
                self.font.render(f"Speed: {t.speed}", True, dim),
            ]
            if t.cloaked:
                self.surfaces.append(
                    self.font.render("CLOAKED", True, (200, 100, 255)))
            for special in t.loadout.get_specials():
                self.surfaces.append(
                    self.font.render(f"[{special.name}]", True, dim))

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
