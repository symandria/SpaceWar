import pygame

from spacewar.states.state_machine import GameState, StateID


class MenuState(GameState):
    def handle_event(self, event):
        g = self.game
        if event.type == pygame.KEYDOWN:
            if g.text_entry:
                if event.key == pygame.K_BACKSPACE:
                    g.text_entry.text = g.text_entry.text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    g.text_entry.callback()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    g.text_entry.callback(g.text_entry.text)
                elif event.unicode:
                    g.text_entry.text += event.unicode
                return None
        elif event.type == pygame.MOUSEBUTTONUP:
            if g.message_box:
                g.message_box = None
                return None
            if g.text_entry:
                return None
            if g.selection_list:
                for button in g.selection_list:
                    if button.rect.collidepoint(event.pos):
                        result = button.callback()
                        if result is not None:
                            g.selection_list = result
                        elif g.battle and g.battle.player:
                            return StateID.BATTLE_IDLE
                        return None
                return None
        return None

    def update(self):
        if self.game.quit:
            return None
        return None

    def render(self):
        g = self.game
        screen = g.screen
        if g.battle:
            screen.blit(g.background, (0, 0))
            for ship in g.battle.ships:
                ship.render(screen)
            screen.blit(g.small_font.render(
                g.text_manager.load("titlebar-no-player"),
                True, g.settings.foreground, g.settings.background), (0, 0))
        else:
            screen.fill(g.settings.background)
        pygame.transform.scale(screen, g.settings.window_size, g.display)
        if g.selection_list:
            g.selection_list.render(g.display)
        if g.text_entry:
            g.text_entry.update(g.display.get_width(), g.display.get_height())
            g.text_entry.render(g.display)
        if g.message_box:
            g.message_box.render(g.display)
