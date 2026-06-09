import os

import pygame


class AssetLoader:
    def __init__(self, settings):
        self._settings = settings
        self._images = {}
        self._sounds = {}

    def load_image(self, name, colorkey=None):
        if isinstance(name, pygame.Surface):
            return name
        elif isinstance(name, tuple):
            name, colorkey = name
        if name not in self._images:
            if not os.path.exists(name):
                raise Exception("Image file {0!r} not found.".format(name))
            image = pygame.image.load(name)
            if colorkey or not image.get_flags() & pygame.SRCALPHA:
                image = image.convert()
                if colorkey:
                    image.set_colorkey(colorkey)
            else:
                image = image.convert_alpha()
            self._images[name] = image
        return self._images[name]

    def play_sound(self, sound):
        if not self._settings.sound_enabled:
            return
        if sound not in self._sounds:
            paths = (
                os.path.join(self._settings.sound_folder, sound + '.wav'),
                os.path.join('data', sound + '.wav'),
                sound + '.wav',
            )
            path = None
            for p in paths:
                if os.path.exists(p):
                    path = p
                    break
            else:
                print('Unable to find {0!r}, {1!r}, or {2!r}.'.format(*paths))
            if path:
                self._sounds[sound] = pygame.mixer.Sound(path)
        if sound in self._sounds:
            self._sounds[sound].set_volume(self._settings.sound_volume / 100)
            self._sounds[sound].play()
