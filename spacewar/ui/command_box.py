import pygame

from spacewar.ui.text_rendering import render_button


class CommandBox:
    def __init__(self, screen, font, foreground, background, text_manager):
        self.screen = screen
        self.font = font
        self.foreground = foreground
        self.background = background
        self.text_manager = text_manager

        self.okay_button, self.okay_button_rect = render_button(
            text_manager.load("button-okay"), self.font, foreground, background)
        self.cancel_button, self.cancel_button_rect = render_button(
            text_manager.load("button-cancel"), self.font, foreground, background)
        self.move_button, self.move_button_rect = render_button(
            "Move [M]", self.font, foreground, background)
        self.act_button, self.act_button_rect = render_button(
            "Target [W]", self.font, foreground, background)

        sample_text = self.font.render("Move to: (XX, XX)  Action: XXXXXXXXXX", True, foreground)
        frame_width = max(
            sample_text.get_width() + 4,
            self.screen.get_width() * 2 // 3,
        )
        frame_height = (
            sample_text.get_height() * 2 +
            max(self.okay_button_rect.height, self.cancel_button_rect.height) + 14
        )
        self.frame = pygame.Surface((frame_width, frame_height))
        self.frame.fill(background)
        self.rect = pygame.Rect(0, 0, frame_width, frame_height)
        pygame.draw.rect(self.frame, foreground, self.rect, 1)
        self.rect.bottom = (self.screen.get_height() * 3) // 4
        self.rect.centerx = self.screen.get_width() // 2

        self.okay_button_rect.bottom = self.rect.bottom - 2
        self.cancel_button_rect.right = self.rect.right - 3
        self.cancel_button_rect.bottom = self.okay_button_rect.bottom
        self.okay_button_rect.right = self.cancel_button_rect.left - 3

        self.movement_info = None
        self.action_info = None
        self.action_info_rect = pygame.Rect(0, 0, 0, 0)
        self.move_button_rect.top = self.rect.top + 2
        self.move_button_rect.right = self.rect.right - 3
        self.act_button_rect.top = self.rect.top + sample_text.get_height() + 6
        self.act_button_rect.right = self.rect.right - 3

    def update(self, player):
        move_str = repr(player.movement) if player.movement else "..."
        self.movement_info = self.font.render(
            f"Move: {move_str}", True, self.foreground)

        action_str = self._format_action(player)
        self.action_info = self.font.render(action_str, True, self.foreground)
        self.action_info_rect = self.action_info.get_rect()
        self.action_info_rect.topleft = (
            self.rect.left + 2,
            self.rect.top + self.movement_info.get_height() + 6,
        )

    def _format_action(self, player):
        action = player.action
        if not action:
            return "Action: None"
        if action in ("weapon_1", "weapon_2"):
            slot = 1 if action == "weapon_1" else 2
            comp = player.loadout.get_weapon(slot)
            if comp:
                wname = comp.get("weapon_type", "?").replace("_", " ").title()
                wrange = comp.get("weapon_range", 0)
                target_str = repr(player.target) if player.target else "..."
                return f"Fire: {wname} r{wrange} -> {target_str}"
            return f"Fire: Weapon {slot} -> ..."
        if action in ("phaser", "torpedo"):
            target_str = repr(player.target) if player.target else "..."
            return f"Fire: {action.title()} -> {target_str}"
        if action == "regen_shields":
            amt = int(player.weapon_power * player.active_regen_mult)
            return f"Regen Shields (+{amt})"
        if action == "power_shields":
            return f"Power to Shields (DR {player.active_dr}%)"
        if action == "self-destruct":
            return "Self-Destruct!"
        return f"Action: {action}"

    def render(self, player_action):
        self.screen.blit(self.frame, self.rect)
        self.screen.blit(self.movement_info, (self.rect.left + 2, self.rect.top + 2))
        self.screen.blit(self.move_button, self.move_button_rect)
        self.screen.blit(self.action_info, self.action_info_rect)
        if player_action in ("phaser", "torpedo", "weapon_1", "weapon_2"):
            self.screen.blit(self.act_button, self.act_button_rect)
        self.screen.blit(self.okay_button, self.okay_button_rect)
        self.screen.blit(self.cancel_button, self.cancel_button_rect)
