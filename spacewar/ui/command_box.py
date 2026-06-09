import pygame

from spacewar.ui.text_rendering import render_button


class CommandBox:
    def __init__(self, screen, font, foreground, background, text_manager):
        self.screen = screen
        self.font = font
        self.foreground = foreground
        self.background = background
        self.text_manager = text_manager

        self.movement_info = self.font.render(
            text_manager.load("move to") + "(XX, XX)", True, foreground)
        longest = 0, None
        for tag in ("do nothing", "fire-phaser", "fire-torpedo", "self-destruct"):
            if len(text_manager.load(tag)) > longest[0]:
                longest = len(text_manager.load(tag)), tag
        self.action_info = self.font.render(
            text_manager.load("action-prefix") + text_manager.load(longest[1]) + "(XX, XX)",
            True, foreground)
        self.action_info_rect = self.action_info.get_rect()

        self.okay_button, self.okay_button_rect = render_button(
            text_manager.load("button-okay"), self.font, foreground, background)
        self.cancel_button, self.cancel_button_rect = render_button(
            text_manager.load("button-cancel"), self.font, foreground, background)
        self.move_button, self.move_button_rect = render_button(
            text_manager.load("button-destination"), self.font, foreground, background)
        self.act_button, self.act_button_rect = render_button(
            text_manager.load("button-target"), self.font, foreground, background)

        frame_width = max(
            self.movement_info.get_width() + self.move_button.get_width() + 4,
            self.action_info.get_width() + self.act_button.get_width() + 4,
            self.screen.get_width() // 2,
        )
        frame_height = (
            self.movement_info.get_height() +
            self.action_info.get_height() +
            max(self.okay_button_rect.height, self.cancel_button_rect.height) + 16
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
        self.action_info_rect.topleft = (
            self.rect.left + 2,
            self.rect.top + 10 + self.movement_info.get_height(),
        )
        self.move_button_rect.centery = (
            self.rect.top + 4 + self.movement_info.get_height() // 2
        )
        self.move_button_rect.right = self.rect.right - 3
        self.act_button_rect.centery = self.action_info_rect.centery
        self.act_button_rect.right = self.rect.right - 3

    def update(self, player):
        tm = self.text_manager
        self.movement_info = self.font.render(
            tm.load("move to") + (repr(player.movement) if player.movement else "..."),
            True, self.foreground)
        text = tm.load("action-prefix")
        if not player.action:
            text += tm.load("do nothing")
        elif player.action in ("phaser", "torpedo"):
            text += tm.load("fire-" + player.action) + (
                repr(player.target) if player.target else "...")
        elif player.action in ("weapon_1", "weapon_2"):
            slot = 1 if player.action == "weapon_1" else 2
            comp = player.loadout.get_weapon(slot)
            wname = comp.get("weapon_type", "weapon").replace("_", " ").title() if comp else "Weapon"
            target_str = repr(player.target) if player.target else "..."
            text += f"Fire {wname} {target_str}"
        elif player.action == "regen_shields":
            text += "Regen Shields"
        elif player.action == "self-destruct":
            text += tm.load("self-destruct")
        self.action_info = self.font.render(text, True, self.foreground)
        self.action_info_rect = self.action_info.get_rect()
        self.action_info_rect.topleft = (
            self.rect.left + 2,
            self.rect.top + 10 + self.movement_info.get_height(),
        )

    def render(self, player_action):
        self.screen.blit(self.frame, self.rect)
        self.screen.blit(self.movement_info, (self.rect.left + 2, self.rect.top + 2))
        self.screen.blit(self.move_button, self.move_button_rect)
        self.screen.blit(self.action_info, self.action_info_rect)
        if player_action in ("phaser", "torpedo", "weapon_1", "weapon_2"):
            self.screen.blit(self.act_button, self.act_button_rect)
        self.screen.blit(self.okay_button, self.okay_button_rect)
        self.screen.blit(self.cancel_button, self.cancel_button_rect)
