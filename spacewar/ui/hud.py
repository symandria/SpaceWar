import pygame


class BattleHUD:
    """Compact status panel (top-left, ~20% of screen width) with
    clickable weapon/power rows. Click or press the listed hotkey to
    select an action; rows highlight when active."""

    def __init__(self, font, small_font, foreground, background):
        self.font = font
        self.small_font = small_font
        self.fg = foreground
        self.bg = background
        # (rect in display coords, action id) built each render
        self.hotspots = []

    def hit_test(self, pos):
        for rect, action_id in self.hotspots:
            if rect.collidepoint(pos):
                return action_id
        return None

    def _action_rows(self, player):
        rows = []
        w1 = player.loadout.get_weapon(1)
        w2 = player.loadout.get_weapon(2)
        if w1:
            name = w1.get("weapon_type", "?").replace("_", " ").title()
            rows.append(("weapon_1",
                         f"[1] {name} r{w1.get('weapon_range', 0)}",
                         player.action == "weapon_1"))
        if w2:
            name = w2.get("weapon_type", "?").replace("_", " ").title()
            rows.append(("weapon_2",
                         f"[2] {name} r{w2.get('weapon_range', 0)}",
                         player.action == "weapon_2"))
        if player.active_cloak:
            state = "ON" if player.cloaked else "off"
            rows.append(("cloak", f"[C] Cloak: {state}",
                         player.action == "cloak"))
        if player.loadout.has_tractor():
            rows.append(("tractor_beam", "[T] Tractor Beam",
                         player.action == "tractor_beam"))
        rows.append(("regen_shields", "[R] Regen Shields",
                     player.action == "regen_shields"))
        if player.active_dr > 0:
            rows.append(("power_shields", f"[P] Shields DR {player.active_dr}%",
                         player.action == "power_shields"))
        return rows

    def render(self, display, player, window_multiplier):
        self.hotspots = []
        if not player:
            return

        pad = 4
        panel_w = max(120, int(display.get_width() * 0.20))
        line_h = self.small_font.get_height() + 2
        rows = self._action_rows(player)
        bar_h = 5
        panel_h = (pad * 2 + line_h * 2 + bar_h * 2 + 6 +
                   line_h + len(rows) * line_h)

        panel_x, panel_y = 2, 2
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        pygame.draw.rect(panel, self.fg, (0, 0, panel_w, panel_h), 1)

        x = pad
        y = pad
        bar_w = panel_w - pad * 2

        hull_pct = max(0, player.hull / player.max_hull) if player.max_hull > 0 else 0
        shield_pct = max(0, player.shields / player.max_shields) \
            if player.max_shields > 0 else 0

        text = self.small_font.render(
            f"Hull {player.hull}/{player.max_hull}", True, self.fg)
        panel.blit(text, (x, y))
        y += line_h
        self._draw_bar(panel, x, y, bar_w, bar_h, hull_pct,
                       (200, 60, 60), (60, 20, 20))
        y += bar_h + 3

        text = self.small_font.render(
            f"Shld {player.shields}/{player.max_shields}", True, self.fg)
        panel.blit(text, (x, y))
        y += line_h
        self._draw_bar(panel, x, y, bar_w, bar_h, shield_pct,
                       (60, 120, 255), (20, 40, 80))
        y += bar_h + 3

        info_parts = [f"Spd:{player.speed}"]
        if player.cloaked:
            info_parts.append("CLOAKED")
        if player.phasing_active:
            info_parts.append("PHASING")
        if player.teleport_cooldown > 0:
            info_parts.append(f"TP:{player.teleport_cooldown}t")
        info = self.small_font.render("  ".join(info_parts), True, self.fg)
        panel.blit(info, (x, y))
        y += line_h

        for action_id, label, active in rows:
            color = (255, 255, 100) if active else (170, 170, 170)
            text = self.small_font.render(label, True, color)
            panel.blit(text, (x, y))
            self.hotspots.append((
                pygame.Rect(panel_x + x, panel_y + y, bar_w, line_h),
                action_id))
            y += line_h

        display.blit(panel, (panel_x, panel_y))

    def _draw_bar(self, surface, x, y, width, height, pct, fill_color, empty_color):
        pygame.draw.rect(surface, empty_color, (x, y, width, height))
        fill_w = int(width * max(0, min(1, pct)))
        if fill_w > 0:
            if pct < 0.25:
                fill_color = (255, 60, 60)
            pygame.draw.rect(surface, fill_color, (x, y, fill_w, height))
        pygame.draw.rect(surface, self.fg, (x, y, width, height), 1)
