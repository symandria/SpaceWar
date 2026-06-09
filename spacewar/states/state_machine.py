from abc import ABC, abstractmethod
from enum import Enum, auto


class StateID(Enum):
    MAIN_MENU = auto()
    CAMPAIGN_MENU = auto()
    BATTLE_IDLE = auto()
    COMMAND_ENTRY = auto()
    DESTINATION_SELECT = auto()
    TARGET_SELECT = auto()
    TURN_RESOLUTION = auto()
    SPECTATING = auto()
    GAME_OVER = auto()


class GameState(ABC):
    def __init__(self, game):
        self.game = game

    def enter(self):
        pass

    def exit(self):
        pass

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass


class StateMachine:
    def __init__(self):
        self._states = {}
        self._current = None
        self._current_id = None

    def register(self, state_id, state):
        self._states[state_id] = state

    @property
    def current_id(self):
        return self._current_id

    def transition_to(self, state_id):
        if self._current:
            self._current.exit()
        self._current = self._states[state_id]
        self._current_id = state_id
        self._current.enter()

    def handle_event(self, event):
        if self._current:
            next_state = self._current.handle_event(event)
            if next_state is not None:
                self.transition_to(next_state)

    def update(self):
        if self._current:
            next_state = self._current.update()
            if next_state is not None:
                self.transition_to(next_state)

    def render(self):
        if self._current:
            self._current.render()
