import os
import glob

import pygame
import pygame.gfxdraw

from spacewar.config.constants import GRID_ROWS, max_col


class GameRenderer:
    def __init__(self, settings, hex_grid):
        self._settings = settings
        self._hex_grid = hex_grid

    def render_battle(self, screen, background, display, battle, settings,
                      hex_grid, text_manager, small_font, infofont,
                      info_target, infobox,
                      selection_list, text_entry, message_box, command_entry,
                      command_box, draw_phasers=None,
                      show_invalid_destinations=False):
        if draw_phasers is None:
            draw_phasers = []

        b = battle
        if not b:
            return

        if b.player and not draw_phasers:
            screen.blit(background, (0, 0))
        elif draw_phasers:
            screen.blit(background, (0, 0))
        else:
            screen.fill(settings.background)

        if show_invalid_destinations and b.player:
            for row in range(1, GRID_ROWS + 1):
                for column in range(1, max_col(row) + 1):
                    if not b.player.get_valid_destination(
                            row, column, bool(b.player.action)):
                        x, y = hex_grid.hex_to_coords(row, column)
                        screen.blit(hex_grid.invalid_surface, (x - 1, y - 1))

        if b.selected:
            screen.blit(hex_grid.select_surface,
                        (int(b.selected.pos[0]) - 1, int(b.selected.pos[1]) - 1))

        for torp in b.torpedoes:
            torp.render(screen)

        for phaser in draw_phasers:
            pygame.draw.line(screen, *phaser)

        for ship in b.ships:
            if ship == b.player:
                continue
            visible = (not ship.cloaked or ship.shot_recently or
                       ship.explode or not b.player or
                       (b.team_game and ship.type == b.player.type))
            if visible:
                ship.render(screen)

        if b.player:
            b.player.render(screen)

        for ship in b.ships:
            if ship.teleport_target:
                move_time = self._get_move_time_for_teleport(ship)
                if move_time is not None:
                    pygame.gfxdraw.filled_circle(
                        screen, int(ship.pos[0]) + 4, int(ship.pos[1]) + 4,
                        abs(move_time), (0, 255, 0))

        if b.player:
            titlebar = text_manager.load("titlebar").format(
                shields=b.player.shields, speed=b.player.speed)
        else:
            titlebar = text_manager.load("titlebar-no-player")
        screen.blit(small_font.render(
            titlebar, True, settings.foreground, settings.background), (0, 0))

        pygame.transform.scale(screen, settings.window_size, display)

        if info_target and infobox:
            infobox.update()
            infobox.rect.left = int(infobox.rect.left) * settings.window_multiplier
            infobox.rect.top = int(infobox.rect.top) * settings.window_multiplier
            if infobox.rect.right > settings.window_size[0]:
                infobox.rect.right = (int(info_target.pos[0]) - 1) * settings.window_multiplier
            if infobox.rect.bottom > settings.window_size[1]:
                infobox.rect.bottom = settings.window_size[1]
            infobox.render(display)

        if selection_list:
            selection_list.render(display)
        if text_entry:
            text_entry.update(display.get_width(), display.get_height())
            text_entry.render(display)
        if message_box:
            message_box.render(display)

    def _get_move_time_for_teleport(self, ship):
        return None

    @staticmethod
    def take_screenshot(display):
        scrnames = glob.glob(os.path.join("screenshots", "screenshot*.png"))
        names = []
        max_num = 0
        for name in scrnames:
            n = os.path.splitext(os.path.basename(name))[0][10:]
            names.append(n)
        for name in names:
            if not set(name).difference(set("0123456789")) and int(name) > max_num:
                max_num = int(name)
        if "screenshots" not in os.listdir("."):
            os.mkdir("screenshots")
        pygame.image.save(
            display,
            os.path.join("screenshots", "screenshot%04d.png" % (max_num + 1)))
