import pygame


class BattleHUD:
    def __init__(self, font, small_font, foreground, background):
        self.font = font
        self.small_font = small_font
        self.fg = foreground
        self.bg = background
        self.bar_height = 6
        self.padding = 2

    def render(self, display, player, window_multiplier):
        if not player:
            return

        m = window_multiplier
        panel_w = 180 * m
        panel_h = 70 * m
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        pygame.draw.rect(panel, self.fg, (0, 0, panel_w, panel_h), 1)

        y = 3 * m
        x = 4 * m

        hull_pct = max(0, player.hull / player.max_hull) if player.max_hull > 0 else 0
        shield_pct = max(0, player.shields / player.max_shields) if player.max_shields > 0 else 0

        hull_text = self.small_font.render(
            f"Hull: {player.hull}/{player.max_hull}", True, self.fg)
        panel.blit(hull_text, (x, y))
        y += hull_text.get_height() + 1

        bar_w = panel_w - 8 * m
        self._draw_bar(panel, x, y, bar_w, 4 * m, hull_pct,
                       (200, 60, 60), (60, 20, 20))
        y += 5 * m

        shield_text = self.small_font.render(
            f"Shields: {player.shields}/{player.max_shields}", True, self.fg)
        panel.blit(shield_text, (x, y))
        y += shield_text.get_height() + 1

        self._draw_bar(panel, x, y, bar_w, 4 * m, shield_pct,
                       (60, 120, 255), (20, 40, 80))
        y += 6 * m

        info_parts = [f"Spd:{player.speed}"]
        if player.cloaked:
            info_parts.append("CLOAKED")
        if player.action == "power_shields":
            info_parts.append(f"DR:{player.active_dr}%")
        if player.phasing_active:
            info_parts.append("PHASING")
        if player.teleport_cooldown > 0:
            info_parts.append(f"TP:{player.teleport_cooldown}t")

        info_line = self.small_font.render("  ".join(info_parts), True, self.fg)
        panel.blit(info_line, (x, y))
        y += info_line.get_height() + 2 * m

        w1 = player.loadout.get_weapon(1)
        w2 = player.loadout.get_weapon(2)
        if w1:
            w1_name = w1.get("weapon_type", "?").replace("_", " ").title()
            w1_range = w1.get("weapon_range", 0)
            w1_text = self.small_font.render(
                f"W1: {w1_name} r{w1_range}", True,
                (255, 255, 100) if player.action == "weapon_1" else (160, 160, 160))
            panel.blit(w1_text, (x, y))
            y += w1_text.get_height() + 1
        if w2:
            w2_name = w2.get("weapon_type", "?").replace("_", " ").title()
            w2_range = w2.get("weapon_range", 0)
            w2_text = self.small_font.render(
                f"W2: {w2_name} r{w2_range}", True,
                (255, 255, 100) if player.action == "weapon_2" else (160, 160, 160))
            panel.blit(w2_text, (x, y))

        display.blit(panel, (2, 2))

    def _draw_bar(self, surface, x, y, width, height, pct, fill_color, empty_color):
        pygame.draw.rect(surface, empty_color, (x, y, width, height))
        fill_w = int(width * max(0, min(1, pct)))
        if fill_w > 0:
            if pct < 0.25:
                fill_color = (255, 60, 60)
            pygame.draw.rect(surface, fill_color, (x, y, fill_w, height))
        pygame.draw.rect(surface, self.fg, (x, y, width, height), 1)

    def render_action_panel(self, display, player, window_multiplier):
        if not player:
            return

        m = window_multiplier
        panel_w = 140 * m
        actions = self._get_actions(player)
        line_h = self.small_font.get_height() + 2
        panel_h = len(actions) * line_h * m + 6 * m

        panel_x = 2
        panel_y = 74 * m
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        pygame.draw.rect(panel, self.fg, (0, 0, panel_w, panel_h), 1)

        y = 3 * m
        for action_id, label, active in actions:
            color = (255, 255, 100) if active else (160, 160, 160)
            marker = "> " if active else "  "
            text = self.small_font.render(f"{marker}{label}", True, color)
            panel.blit(text, (4 * m, y))
            y += line_h * m

        display.blit(panel, (panel_x, panel_y))

    def _get_actions(self, player):
        actions = []
        w1 = player.loadout.get_weapon(1)
        w2 = player.loadout.get_weapon(2)

        actions.append((None, "Do Nothing", player.action is None))
        if w1:
            name = w1.get("weapon_type", "?").replace("_", " ").title()
            actions.append(("weapon_1", name, player.action == "weapon_1"))
        if w2:
            name = w2.get("weapon_type", "?").replace("_", " ").title()
            actions.append(("weapon_2", name, player.action == "weapon_2"))
        actions.append(("regen_shields", "Regen Shields", player.action == "regen_shields"))
        if player.active_dr > 0:
            actions.append(("power_shields", "Power to Shields", player.action == "power_shields"))

        return actions
