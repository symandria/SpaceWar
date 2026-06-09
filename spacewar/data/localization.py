import os
import glob


class TextFileError(Exception):
    pass


class TextManager:
    def __init__(self, settings):
        self._settings = settings
        self._cache = {}
        self._active_theme = None

    @property
    def active_theme(self):
        return self._active_theme

    @active_theme.setter
    def active_theme(self, theme):
        self._active_theme = theme

    def load(self, tag):
        alternate = None
        if self._active_theme:
            alternate = os.path.join(
                self._settings.theme_folder, self._active_theme,
                os.path.basename(self._settings.text_file),
            )
            if alternate in self._cache and tag in self._cache[alternate]:
                return self._load_from(tag, alternate)
        for file in self._cache:
            if tag in self._cache[file]:
                return self._load_from(tag, file)
        try:
            return self._load_from(tag)
        except TextFileError as orig:
            if self._active_theme:
                if os.path.exists(alternate):
                    try:
                        return self._load_from(tag, alternate)
                    except TextFileError:
                        pass
            for name in glob.glob(os.path.join(
                self._settings.theme_folder, "*",
                os.path.basename(self._settings.text_file),
            )):
                if name == alternate:
                    pass
                elif os.path.exists(name):
                    try:
                        return self._load_from(tag, name)
                    except TextFileError:
                        pass
            raise orig

    def _load_from(self, tag, file=None):
        if file is None:
            file = self._settings.text_file
        tag = tag.lower()
        if file in self._cache and tag in self._cache[file]:
            text = self._cache[file][tag]
        else:
            if file not in self._cache:
                self._cache[file] = {}
            with open(file, "r", encoding="utf8") as f:
                result = ""
                found = None
                for line in f:
                    line = line.strip("\r\n")
                    if line.startswith("<"):
                        temp = line[1:line.index(">")]
                        if found:
                            self._cache[file][found] = result[1:]
                        found = temp.lower()
                        result = ""
                    elif found:
                        result += "\n" + line
                else:
                    if found:
                        self._cache[file][found] = result[1:]
            if tag not in self._cache[file]:
                raise TextFileError(
                    "Text tag {0!r} not found in text file {1!r}.".format(tag, file))
            text = self._cache[file][tag]
        final = ""
        checks = text.split(">")
        final += checks[0]
        for segment in checks[1:]:
            if "<" not in segment:
                final += ">"
            else:
                inner_tag, segment = segment.split("<", 1)
                final += self.load(inner_tag)
            final += segment
        return final
