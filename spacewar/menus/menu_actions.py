from abc import ABC, abstractmethod


class MenuAction(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def __call__(self):
        pass

    def _make_list(self, title, *buttons):
        return self.game.make_selection_list(title, *buttons)

    def _text(self, tag):
        return self.game.text_manager.load(tag)
