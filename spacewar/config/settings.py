import configparser
import os
from collections import OrderedDict

from spacewar.config.constants import INI_DEFAULTS, SCREEN_SIZE


class GameSettings:
    def __init__(self, ini_file='spacewar.ini'):
        pygame_info = _get_display_info()
        default_fullscreen = (pygame_info == (800, 480))
        default_multiplier = min(
            (pygame_info[0] - (0 if default_fullscreen else 20)) // SCREEN_SIZE[0],
            (pygame_info[1] - (0 if default_fullscreen else 20)) // SCREEN_SIZE[1],
        )

        self._ini = configparser.ConfigParser(dict_type=OrderedDict)
        self._ini.read_dict(INI_DEFAULTS)
        if os.path.exists(ini_file):
            self._ini.read(ini_file)
        else:
            with open(ini_file, "w") as f:
                self._ini.write(f)

        self.window_caption = self._ini.get('Window', 'Caption')
        self.icon_file = self._ini.get('Window', 'Icon')
        self.sound_folder = self._ini.get('Data Files', 'Sound folder')
        self.theme_folder = self._ini.get('Data Files', 'Theme folder')
        self.save_folder = self._ini.get('Data Files', 'Character folder')
        self.text_file = self._ini.get('Data Files', 'Localization file')
        self.settings_file = self._ini.get('Data Files', 'Settings file')

        settings_defaults = OrderedDict((
            ('Window', OrderedDict((
                ('Scaling multiplier', repr(default_multiplier)),
                ('Fullscreen', repr(default_fullscreen)),
                ('Font size', '16' if default_multiplier > 4 else '12'),
            ))),
            ('Audio', OrderedDict((
                ('Sound enabled', 'True'),
                ('Sound volume', '100'),
            ))),
            ('Gameplay', OrderedDict((
                ('Classic collisions', 'True'),
                ('White-on-black', 'True'),
                ('Strict character stats', 'False'),
            ))),
        ))

        self._settings = configparser.ConfigParser(dict_type=OrderedDict)
        self._settings.read_dict(settings_defaults)
        if os.path.exists(self.settings_file):
            self._settings.read(self.settings_file)
        else:
            with open(self.settings_file, "w") as f:
                self._settings.write(f)

        self.window_multiplier = self._settings.getint('Window', 'Scaling multiplier')
        self.fullscreen = self._settings.getboolean('Window', 'Fullscreen')
        self.font_size = self._settings.getint('Window', 'Font size')
        self.sound_enabled = self._settings.getboolean('Audio', 'Sound enabled')
        self.sound_volume = self._settings.getint('Audio', 'Sound volume')
        self.pixel_perfect = self._settings.getboolean('Gameplay', 'Classic collisions')
        self.strict_stats = self._settings.getboolean('Gameplay', 'Strict character stats')

        if self._settings.getboolean('Gameplay', 'White-on-black'):
            self.foreground = (255, 255, 255)
            self.background = (0, 0, 0)
        else:
            self.foreground = (0, 0, 0)
            self.background = (255, 255, 255)

        self.window_size = (
            SCREEN_SIZE[0] * self.window_multiplier,
            SCREEN_SIZE[1] * self.window_multiplier,
        )


def _get_display_info():
    import pygame
    if not pygame.display.get_init():
        pygame.display.init()
    info = pygame.display.Info()
    return info.current_w, info.current_h
